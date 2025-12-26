"""
Task Service - 작업 스케줄링 마이크로서비스
포트: 8003

- 작업 생성/분배
- 작업 큐 관리
- 기기 할당
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import uvicorn
import httpx
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from shared.schemas.task import (
    TaskCreate,
    TaskInDB,
    TaskResponse,
    TaskQueueResponse,
    TaskAssign,
    TaskStatus,
    TaskMessage
)
from shared.schemas.pattern import HumanPatternConfig

# ==================== FastAPI 앱 ====================
app = FastAPI(
    title="Task Service",
    description="작업 스케줄링 마이크로서비스",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 설정 ====================
PATTERN_SERVICE_URL = os.getenv("PATTERN_SERVICE_URL", "http://localhost:8004")
DEVICE_SERVICE_URL = os.getenv("DEVICE_SERVICE_URL", "http://localhost:8002")
VIDEO_SERVICE_URL = os.getenv("VIDEO_SERVICE_URL", "http://localhost:8001")

# ==================== 임시 인메모리 저장소 ====================
tasks_db: dict[str, TaskInDB] = {}

# HTTP 클라이언트
http_client = httpx.AsyncClient(timeout=30.0)


# ==================== 헬퍼 함수 ====================

async def get_video_info(video_id: str) -> dict:
    """영상 정보 조회"""
    try:
        response = await http_client.get(f"{VIDEO_SERVICE_URL}/videos/{video_id}")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {}


async def generate_pattern(video_duration: int, config_override: Optional[dict] = None) -> dict:
    """휴먼 패턴 생성 요청"""
    try:
        payload = {"video_duration": video_duration}
        if config_override:
            payload["config_override"] = config_override
        
        response = await http_client.post(
            f"{PATTERN_SERVICE_URL}/patterns/generate",
            json=payload
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"패턴 생성 오류: {e}")
    
    # 기본 패턴 반환
    return {
        "pattern": {
            "watch": {"watch_time": int(video_duration * 0.7), "watch_percent": 70},
            "interaction": {"should_like": False, "should_comment": False}
        }
    }


async def update_device_status(device_id: str, status: str):
    """기기 상태 업데이트"""
    try:
        await http_client.put(
            f"{DEVICE_SERVICE_URL}/devices/{device_id}/status",
            params={"status": status}
        )
    except:
        pass


# ==================== API 엔드포인트 ====================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "task-service"}


@app.get("/tasks", response_model=TaskQueueResponse)
async def list_tasks(
    status: Optional[str] = None,
    video_id: Optional[str] = None,
    device_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """작업 목록 조회"""
    tasks = list(tasks_db.values())
    
    # 필터링
    if status:
        tasks = [t for t in tasks if t.status.value == status]
    if video_id:
        tasks = [t for t in tasks if t.video_id == video_id]
    if device_id:
        tasks = [t for t in tasks if t.device_id == device_id]
    
    # 정렬 (우선순위 높은 것 먼저, 오래된 것 먼저)
    tasks.sort(key=lambda t: (-t.priority, t.queued_at))
    
    # 상태별 집계
    all_tasks = list(tasks_db.values())
    status_counts = {
        "queued": len([t for t in all_tasks if t.status == TaskStatus.QUEUED]),
        "assigned": len([t for t in all_tasks if t.status == TaskStatus.ASSIGNED]),
        "running": len([t for t in all_tasks if t.status == TaskStatus.RUNNING]),
        "completed": len([t for t in all_tasks if t.status == TaskStatus.COMPLETED]),
        "failed": len([t for t in all_tasks if t.status == TaskStatus.FAILED]),
    }
    
    # 페이지네이션
    paginated = tasks[offset:offset + limit]
    
    # TaskResponse로 변환
    task_responses = []
    for t in paginated:
        resp = TaskResponse(**t.model_dump())
        task_responses.append(resp)
    
    return TaskQueueResponse(
        total=len(tasks),
        queued=status_counts["queued"],
        assigned=status_counts["assigned"],
        running=status_counts["running"],
        completed=status_counts["completed"],
        failed=status_counts["failed"],
        tasks=task_responses
    )


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """작업 상세 조회"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(**tasks_db[task_id].model_dump())


@app.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    """작업 생성"""
    # 영상 정보 조회
    video_info = await get_video_info(task.video_id)
    video_duration = video_info.get("duration", 300)  # 기본 5분
    
    # 휴먼 패턴 생성
    pattern_result = await generate_pattern(
        video_duration, 
        task.pattern_config
    )
    
    # 작업 생성
    new_task = TaskInDB(
        video_id=task.video_id,
        device_id=task.device_id,
        priority=task.priority,
        pattern_config=pattern_result.get("pattern", {}),
        status=TaskStatus.QUEUED
    )
    
    tasks_db[new_task.id] = new_task
    
    return TaskResponse(**new_task.model_dump())


@app.post("/tasks/bulk")
async def create_bulk_tasks(video_ids: List[str], count_per_video: int = 1):
    """대량 작업 생성"""
    created = []
    
    for video_id in video_ids:
        video_info = await get_video_info(video_id)
        video_duration = video_info.get("duration", 300)
        
        for _ in range(count_per_video):
            pattern_result = await generate_pattern(video_duration)
            
            new_task = TaskInDB(
                video_id=video_id,
                pattern_config=pattern_result.get("pattern", {}),
                status=TaskStatus.QUEUED
            )
            tasks_db[new_task.id] = new_task
            created.append(new_task.id)
    
    return {"created_count": len(created), "task_ids": created}


@app.post("/tasks/{task_id}/assign")
async def assign_task(task_id: str, assign: TaskAssign):
    """작업을 기기에 할당"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    if task.status != TaskStatus.QUEUED:
        raise HTTPException(status_code=400, detail=f"Task status is {task.status.value}, cannot assign")
    
    task.device_id = assign.device_id
    task.status = TaskStatus.ASSIGNED
    task.assigned_at = datetime.utcnow()
    
    # 기기 상태를 busy로 변경
    await update_device_status(assign.device_id, "busy")
    
    return TaskResponse(**task.model_dump())


@app.get("/tasks/next")
async def get_next_task(device_id: str):
    """다음 작업 가져오기 (기기에서 호출)"""
    # 대기 중인 작업 중 우선순위 높은 것 선택
    queued_tasks = [
        t for t in tasks_db.values() 
        if t.status == TaskStatus.QUEUED
    ]
    
    if not queued_tasks:
        return {"task": None, "message": "No tasks available"}
    
    # 우선순위 높은 것, 오래된 것 순
    queued_tasks.sort(key=lambda t: (-t.priority, t.queued_at))
    selected_task = queued_tasks[0]
    
    # 작업 할당
    selected_task.device_id = device_id
    selected_task.status = TaskStatus.ASSIGNED
    selected_task.assigned_at = datetime.utcnow()
    
    # 영상 정보 포함
    video_info = await get_video_info(selected_task.video_id)
    
    return {
        "task": TaskResponse(**selected_task.model_dump()),
        "video": video_info,
        "message": "Task assigned"
    }


@app.post("/tasks/{task_id}/start")
async def start_task(task_id: str):
    """작업 시작"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    if task.status not in [TaskStatus.QUEUED, TaskStatus.ASSIGNED]:
        raise HTTPException(status_code=400, detail=f"Task status is {task.status.value}, cannot start")
    
    task.status = TaskStatus.RUNNING
    task.started_at = datetime.utcnow()
    
    return TaskResponse(**task.model_dump())


@app.post("/tasks/{task_id}/complete")
async def complete_task(task_id: str, success: bool = True, error_message: Optional[str] = None):
    """작업 완료"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    if success:
        task.status = TaskStatus.COMPLETED
    else:
        task.status = TaskStatus.FAILED
        task.error_message = error_message
        task.retry_count += 1
        
        # 재시도 가능 여부 체크
        if task.retry_count < task.max_retries:
            task.status = TaskStatus.QUEUED
            task.device_id = None
    
    task.completed_at = datetime.utcnow()
    
    # 기기 상태를 idle로 변경
    if task.device_id:
        await update_device_status(task.device_id, "idle")
    
    return TaskResponse(**task.model_dump())


@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """작업 취소"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    if task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"Task already {task.status.value}")
    
    task.status = TaskStatus.CANCELLED
    task.completed_at = datetime.utcnow()
    
    # 기기 상태를 idle로 변경
    if task.device_id:
        await update_device_status(task.device_id, "idle")
    
    return TaskResponse(**task.model_dump())


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """작업 삭제"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del tasks_db[task_id]
    
    return {"message": "Task deleted", "task_id": task_id}


@app.get("/tasks/video/{video_id}/progress")
async def get_video_progress(video_id: str):
    """영상별 작업 진행 상황"""
    video_tasks = [t for t in tasks_db.values() if t.video_id == video_id]
    
    return {
        "video_id": video_id,
        "total": len(video_tasks),
        "queued": len([t for t in video_tasks if t.status == TaskStatus.QUEUED]),
        "running": len([t for t in video_tasks if t.status == TaskStatus.RUNNING]),
        "completed": len([t for t in video_tasks if t.status == TaskStatus.COMPLETED]),
        "failed": len([t for t in video_tasks if t.status == TaskStatus.FAILED])
    }


# ==================== 실행 ====================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )

