"""
Device Service - 기기 관리 마이크로서비스
포트: 8002

- 기기 등록/상태 관리
- 하트비트 처리
- 헬스 모니터링
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uvicorn
import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from shared.schemas.device import (
    DeviceCreate,
    DeviceInDB,
    DeviceResponse,
    DeviceListResponse,
    DeviceHealthUpdate,
    DeviceHeartbeat,
    DeviceStatus
)

# ==================== FastAPI 앱 ====================
app = FastAPI(
    title="Device Service",
    description="기기 관리 마이크로서비스",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 임시 인메모리 저장소 ====================
# 실제 구현 시 PostgreSQL 연결
devices_db: dict[str, DeviceInDB] = {}

# 헬스체크 설정
HEARTBEAT_TIMEOUT_SECONDS = 60  # 60초 이상 하트비트 없으면 오프라인
OVERHEAT_TEMP_THRESHOLD = 70.0  # 70°C 이상 과열

# ==================== 헬퍼 함수 ====================

def check_device_health(device: DeviceInDB) -> DeviceStatus:
    """기기 상태 자동 판정"""
    # 과열 체크
    if device.battery_temp and device.battery_temp >= OVERHEAT_TEMP_THRESHOLD:
        return DeviceStatus.OVERHEAT
    
    # 하트비트 타임아웃 체크
    if device.last_heartbeat:
        timeout = datetime.utcnow() - timedelta(seconds=HEARTBEAT_TIMEOUT_SECONDS)
        if device.last_heartbeat < timeout:
            return DeviceStatus.OFFLINE
    else:
        return DeviceStatus.OFFLINE
    
    return device.status


# ==================== API 엔드포인트 ====================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "device-service"}


@app.get("/devices", response_model=DeviceListResponse)
async def list_devices(
    status: Optional[str] = None,
    pc_id: Optional[str] = None
):
    """기기 목록 조회"""
    devices = list(devices_db.values())
    
    # 상태 자동 업데이트
    for device in devices:
        device.status = check_device_health(device)
    
    # 필터링
    if status:
        devices = [d for d in devices if d.status.value == status]
    if pc_id:
        devices = [d for d in devices if d.pc_id == pc_id]
    
    # 상태별 집계
    status_counts = {
        "idle": len([d for d in devices if d.status == DeviceStatus.IDLE]),
        "busy": len([d for d in devices if d.status == DeviceStatus.BUSY]),
        "offline": len([d for d in devices if d.status == DeviceStatus.OFFLINE]),
        "error": len([d for d in devices if d.status in [DeviceStatus.ERROR, DeviceStatus.OVERHEAT]]),
    }
    
    # DeviceResponse로 변환
    device_responses = []
    for d in devices:
        resp = DeviceResponse(**d.model_dump())
        device_responses.append(resp)
    
    return DeviceListResponse(
        total=len(devices),
        idle=status_counts["idle"],
        busy=status_counts["busy"],
        offline=status_counts["offline"],
        error=status_counts["error"],
        devices=device_responses
    )


@app.get("/devices/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str):
    """기기 상세 조회"""
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device = devices_db[device_id]
    device.status = check_device_health(device)
    
    return DeviceResponse(**device.model_dump())


@app.post("/devices", response_model=DeviceResponse)
async def register_device(device: DeviceCreate):
    """기기 등록"""
    # 시리얼 번호로 중복 체크
    existing = next(
        (d for d in devices_db.values() if d.serial_number == device.serial_number),
        None
    )
    
    if existing:
        # 이미 등록된 기기 → 상태 업데이트
        existing.pc_id = device.pc_id
        existing.model = device.model
        existing.last_heartbeat = datetime.utcnow()
        existing.status = DeviceStatus.IDLE
        existing.updated_at = datetime.utcnow()
        return DeviceResponse(**existing.model_dump())
    
    # 새 기기 등록
    new_device = DeviceInDB(
        serial_number=device.serial_number,
        pc_id=device.pc_id,
        model=device.model,
        status=DeviceStatus.IDLE,
        last_heartbeat=datetime.utcnow()
    )
    
    devices_db[new_device.id] = new_device
    
    return DeviceResponse(**new_device.model_dump())


@app.post("/devices/{device_id}/heartbeat")
async def device_heartbeat(device_id: str, health: DeviceHealthUpdate):
    """기기 하트비트 수신"""
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device = devices_db[device_id]
    
    # 헬스 정보 업데이트
    device.last_heartbeat = datetime.utcnow()
    device.battery_temp = health.battery_temp
    device.cpu_usage = health.cpu_usage
    device.memory_usage = health.memory_usage
    device.battery_level = health.battery_level
    device.updated_at = datetime.utcnow()
    
    # 상태 자동 판정
    device.status = check_device_health(device)
    
    # 과열 시 경고
    warning = None
    if device.status == DeviceStatus.OVERHEAT:
        warning = f"Device overheating: {device.battery_temp}°C"
    
    return {
        "status": device.status.value,
        "warning": warning,
        "received_at": datetime.utcnow().isoformat()
    }


@app.put("/devices/{device_id}/status")
async def update_device_status(device_id: str, status: str):
    """기기 상태 수동 업데이트"""
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    try:
        new_status = DeviceStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    device = devices_db[device_id]
    device.status = new_status
    device.updated_at = datetime.utcnow()
    
    return {"device_id": device_id, "status": new_status.value}


@app.post("/devices/{device_id}/task-complete")
async def record_task_complete(device_id: str, success: bool):
    """작업 완료 기록"""
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device = devices_db[device_id]
    device.total_tasks += 1
    
    if success:
        device.success_tasks += 1
    else:
        device.error_tasks += 1
    
    # 작업 완료 후 idle 상태로
    device.status = DeviceStatus.IDLE
    device.updated_at = datetime.utcnow()
    
    return {
        "total_tasks": device.total_tasks,
        "success_tasks": device.success_tasks,
        "error_tasks": device.error_tasks
    }


@app.delete("/devices/{device_id}")
async def delete_device(device_id: str):
    """기기 삭제"""
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    del devices_db[device_id]
    
    return {"message": "Device deleted", "device_id": device_id}


@app.get("/devices/idle/count")
async def get_idle_devices_count():
    """대기 중인 기기 수 조회"""
    # 상태 자동 업데이트
    for device in devices_db.values():
        device.status = check_device_health(device)
    
    idle_count = len([d for d in devices_db.values() if d.status == DeviceStatus.IDLE])
    
    return {"idle_count": idle_count}


@app.get("/devices/pc/{pc_id}")
async def get_devices_by_pc(pc_id: str):
    """PC별 기기 조회"""
    devices = [d for d in devices_db.values() if d.pc_id == pc_id]
    
    for device in devices:
        device.status = check_device_health(device)
    
    return {
        "pc_id": pc_id,
        "device_count": len(devices),
        "devices": [DeviceResponse(**d.model_dump()) for d in devices]
    }


# ==================== 실행 ====================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )

