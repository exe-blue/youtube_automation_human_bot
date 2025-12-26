"""
API Gateway - 중앙 라우팅 및 인증
포트: 8000

모든 마이크로서비스로의 진입점
- 인증/인가
- 요청 라우팅
- Rate Limiting
- 요청 로깅
"""
from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import uvicorn
from typing import Optional
from datetime import datetime
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from shared.schemas.video import VideoCreate, VideoUpdate, VideoListResponse
from shared.schemas.device import DeviceCreate, DeviceListResponse
from shared.schemas.task import TaskCreate, TaskQueueResponse
from shared.schemas.result import ResultCreate, ResultListResponse, StatsResponse
from shared.schemas.pattern import PatternRequest, PatternResponse

# ==================== 설정 ====================
SERVICES = {
    "video": os.getenv("VIDEO_SERVICE_URL", "http://localhost:8001"),
    "device": os.getenv("DEVICE_SERVICE_URL", "http://localhost:8002"),
    "task": os.getenv("TASK_SERVICE_URL", "http://localhost:8003"),
    "pattern": os.getenv("PATTERN_SERVICE_URL", "http://localhost:8004"),
    "result": os.getenv("RESULT_SERVICE_URL", "http://localhost:8005"),
}

API_KEYS = os.getenv("API_KEYS", "test-key-123,admin-key-456").split(",")

# ==================== FastAPI 앱 ====================
app = FastAPI(
    title="YouTube Automation API Gateway",
    description="마이크로서비스 중앙 게이트웨이",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP 클라이언트
http_client = httpx.AsyncClient(timeout=30.0)


# ==================== 인증 미들웨어 ====================

async def verify_api_key(authorization: Optional[str] = Header(None)):
    """API 키 검증"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Bearer 토큰 추출
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization
    
    if token not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return token


# ==================== 헬스 체크 ====================

@app.get("/health")
async def health_check():
    """게이트웨이 및 서비스 헬스 체크"""
    service_status = {}
    
    for name, url in SERVICES.items():
        try:
            response = await http_client.get(f"{url}/health", timeout=5.0)
            service_status[name] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            service_status[name] = "unreachable"
    
    return {
        "gateway": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": service_status
    }


# ==================== 영상 API 프록시 ====================

@app.get("/videos", response_model=VideoListResponse)
async def list_videos(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    api_key: str = Depends(verify_api_key)
):
    """영상 목록 조회"""
    params = {"limit": limit, "offset": offset}
    if status:
        params["status"] = status
    
    response = await http_client.get(
        f"{SERVICES['video']}/videos",
        params=params
    )
    return response.json()


@app.post("/videos")
async def create_video(
    video: VideoCreate,
    api_key: str = Depends(verify_api_key)
):
    """영상 등록"""
    response = await http_client.post(
        f"{SERVICES['video']}/videos",
        json=video.model_dump()
    )
    return response.json()


@app.put("/videos/{video_id}")
async def update_video(
    video_id: str,
    video: VideoUpdate,
    api_key: str = Depends(verify_api_key)
):
    """영상 업데이트"""
    response = await http_client.put(
        f"{SERVICES['video']}/videos/{video_id}",
        json=video.model_dump(exclude_unset=True)
    )
    return response.json()


@app.delete("/videos/{video_id}")
async def delete_video(
    video_id: str,
    api_key: str = Depends(verify_api_key)
):
    """영상 삭제"""
    response = await http_client.delete(
        f"{SERVICES['video']}/videos/{video_id}"
    )
    return response.json()


# ==================== 기기 API 프록시 ====================

@app.get("/devices", response_model=DeviceListResponse)
async def list_devices(
    status: Optional[str] = None,
    pc_id: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """기기 목록 조회"""
    params = {}
    if status:
        params["status"] = status
    if pc_id:
        params["pc_id"] = pc_id
    
    response = await http_client.get(
        f"{SERVICES['device']}/devices",
        params=params
    )
    return response.json()


@app.post("/devices")
async def register_device(
    device: DeviceCreate,
    api_key: str = Depends(verify_api_key)
):
    """기기 등록"""
    response = await http_client.post(
        f"{SERVICES['device']}/devices",
        json=device.model_dump()
    )
    return response.json()


@app.post("/devices/{device_id}/heartbeat")
async def device_heartbeat(
    device_id: str,
    health: dict,
    api_key: str = Depends(verify_api_key)
):
    """기기 하트비트"""
    response = await http_client.post(
        f"{SERVICES['device']}/devices/{device_id}/heartbeat",
        json=health
    )
    return response.json()


# ==================== 작업 API 프록시 ====================

@app.get("/tasks", response_model=TaskQueueResponse)
async def list_tasks(
    status: Optional[str] = None,
    video_id: Optional[str] = None,
    device_id: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """작업 목록 조회"""
    params = {}
    if status:
        params["status"] = status
    if video_id:
        params["video_id"] = video_id
    if device_id:
        params["device_id"] = device_id
    
    response = await http_client.get(
        f"{SERVICES['task']}/tasks",
        params=params
    )
    return response.json()


@app.post("/tasks")
async def create_task(
    task: TaskCreate,
    api_key: str = Depends(verify_api_key)
):
    """작업 생성"""
    response = await http_client.post(
        f"{SERVICES['task']}/tasks",
        json=task.model_dump()
    )
    return response.json()


@app.post("/tasks/{task_id}/assign")
async def assign_task(
    task_id: str,
    device_id: str,
    api_key: str = Depends(verify_api_key)
):
    """작업 할당"""
    response = await http_client.post(
        f"{SERVICES['task']}/tasks/{task_id}/assign",
        json={"device_id": device_id}
    )
    return response.json()


@app.get("/tasks/next")
async def get_next_task(
    device_id: str,
    api_key: str = Depends(verify_api_key)
):
    """다음 작업 요청 (기기에서 호출)"""
    response = await http_client.get(
        f"{SERVICES['task']}/tasks/next",
        params={"device_id": device_id}
    )
    return response.json()


# ==================== 패턴 API 프록시 ====================

@app.post("/patterns/generate", response_model=PatternResponse)
async def generate_pattern(
    request: PatternRequest,
    api_key: str = Depends(verify_api_key)
):
    """휴먼 패턴 생성"""
    response = await http_client.post(
        f"{SERVICES['pattern']}/patterns/generate",
        json=request.model_dump()
    )
    return response.json()


@app.post("/patterns/watch")
async def generate_watch_pattern(
    video_duration: int,
    api_key: str = Depends(verify_api_key)
):
    """시청 패턴 생성"""
    response = await http_client.post(
        f"{SERVICES['pattern']}/patterns/watch",
        params={"video_duration": video_duration}
    )
    return response.json()


@app.get("/patterns/stats/watch-distribution")
async def get_watch_distribution(
    video_duration: int = 300,
    samples: int = 1000,
    api_key: str = Depends(verify_api_key)
):
    """시청 시간 분포 시뮬레이션"""
    response = await http_client.get(
        f"{SERVICES['pattern']}/stats/watch-distribution",
        params={"video_duration": video_duration, "samples": samples}
    )
    return response.json()


# ==================== 결과 API 프록시 ====================

@app.post("/results")
async def submit_result(
    result: ResultCreate,
    api_key: str = Depends(verify_api_key)
):
    """결과 제출"""
    response = await http_client.post(
        f"{SERVICES['result']}/results",
        json=result.model_dump()
    )
    return response.json()


@app.get("/results", response_model=ResultListResponse)
async def list_results(
    video_id: Optional[str] = None,
    device_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    api_key: str = Depends(verify_api_key)
):
    """결과 목록 조회"""
    params = {"limit": limit, "offset": offset}
    if video_id:
        params["video_id"] = video_id
    if device_id:
        params["device_id"] = device_id
    
    response = await http_client.get(
        f"{SERVICES['result']}/results",
        params=params
    )
    return response.json()


@app.get("/stats", response_model=StatsResponse)
async def get_stats(api_key: str = Depends(verify_api_key)):
    """전체 통계 조회"""
    response = await http_client.get(f"{SERVICES['result']}/stats")
    return response.json()


@app.get("/stats/daily")
async def get_daily_stats(
    days: int = 7,
    api_key: str = Depends(verify_api_key)
):
    """일별 통계 조회"""
    response = await http_client.get(
        f"{SERVICES['result']}/stats/daily",
        params={"days": days}
    )
    return response.json()


# ==================== 대시보드 데이터 ====================

@app.get("/dashboard")
async def get_dashboard_data(api_key: str = Depends(verify_api_key)):
    """대시보드용 통합 데이터"""
    try:
        # 병렬로 여러 서비스 데이터 수집
        videos_resp = await http_client.get(f"{SERVICES['video']}/videos", params={"limit": 10})
        devices_resp = await http_client.get(f"{SERVICES['device']}/devices")
        tasks_resp = await http_client.get(f"{SERVICES['task']}/tasks", params={"limit": 10})
        stats_resp = await http_client.get(f"{SERVICES['result']}/stats")
        
        return {
            "videos": videos_resp.json() if videos_resp.status_code == 200 else {},
            "devices": devices_resp.json() if devices_resp.status_code == 200 else {},
            "tasks": tasks_resp.json() if tasks_resp.status_code == 200 else {},
            "stats": stats_resp.json() if stats_resp.status_code == 200 else {},
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


# ==================== 에러 핸들러 ====================

@app.exception_handler(httpx.RequestError)
async def service_unavailable_handler(request: Request, exc: httpx.RequestError):
    return JSONResponse(
        status_code=503,
        content={"detail": f"Service unavailable: {str(exc)}"}
    )


# ==================== 실행 ====================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

