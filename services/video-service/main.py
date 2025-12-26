"""
Video Service - 영상 관리 마이크로서비스
포트: 8001

- 영상 CRUD
- 상태 관리
- 메타데이터 관리
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import uvicorn
import re
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from shared.schemas.video import (
    VideoCreate,
    VideoUpdate,
    VideoInDB,
    VideoResponse,
    VideoListResponse,
    VideoStatus
)

# ==================== FastAPI 앱 ====================
app = FastAPI(
    title="Video Service",
    description="영상 관리 마이크로서비스",
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
videos_db: dict[str, VideoInDB] = {}


# ==================== 헬퍼 함수 ====================

def extract_video_id(url: str) -> Optional[str]:
    """YouTube URL에서 영상 ID 추출"""
    patterns = [
        r'(?:v=|/v/|youtu\.be/|/embed/)([a-zA-Z0-9_-]{11})',
        r'(?:watch\?v=)([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, str(url))
        if match:
            return match.group(1)
    
    return None


def validate_youtube_url(url: str) -> bool:
    """YouTube URL 유효성 검사"""
    if not url:
        return False
    return extract_video_id(url) is not None


# ==================== API 엔드포인트 ====================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "video-service"}


@app.get("/videos", response_model=VideoListResponse)
async def list_videos(
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = 0
):
    """영상 목록 조회"""
    videos = list(videos_db.values())
    
    # 필터링
    if status:
        videos = [v for v in videos if v.status.value == status]
    if keyword:
        videos = [v for v in videos if keyword.lower() in (v.keyword or "").lower()]
    
    # 정렬 (우선순위 높은 것 먼저, 최근 것 먼저)
    videos.sort(key=lambda v: (-v.priority, v.created_at), reverse=True)
    
    # 상태별 집계
    all_videos = list(videos_db.values())
    status_counts = {
        "pending": len([v for v in all_videos if v.status == VideoStatus.PENDING]),
        "processing": len([v for v in all_videos if v.status == VideoStatus.PROCESSING]),
        "completed": len([v for v in all_videos if v.status == VideoStatus.COMPLETED]),
        "error": len([v for v in all_videos if v.status == VideoStatus.ERROR]),
    }
    
    # 페이지네이션
    paginated = videos[offset:offset + limit]
    
    # VideoResponse로 변환
    video_responses = []
    for v in paginated:
        resp = VideoResponse(**v.model_dump())
        video_responses.append(resp)
    
    return VideoListResponse(
        total=len(videos),
        pending=status_counts["pending"],
        processing=status_counts["processing"],
        completed=status_counts["completed"],
        error=status_counts["error"],
        videos=video_responses
    )


@app.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str):
    """영상 상세 조회"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return VideoResponse(**videos_db[video_id].model_dump())


@app.post("/videos", response_model=VideoResponse)
async def create_video(video: VideoCreate):
    """영상 등록"""
    # URL 유효성 검사
    if video.url and not validate_youtube_url(str(video.url)):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    # 중복 체크 (URL 기준)
    if video.url:
        video_id_from_url = extract_video_id(str(video.url))
        existing = next(
            (v for v in videos_db.values() 
             if v.url and extract_video_id(str(v.url)) == video_id_from_url),
            None
        )
        if existing:
            raise HTTPException(status_code=409, detail="Video already exists")
    
    new_video = VideoInDB(
        url=video.url,
        title=video.title,
        keyword=video.keyword,
        duration=video.duration,
        priority=video.priority
    )
    
    videos_db[new_video.id] = new_video
    
    return VideoResponse(**new_video.model_dump())


@app.post("/videos/bulk")
async def create_bulk_videos(videos: List[VideoCreate]):
    """대량 영상 등록"""
    created = []
    errors = []
    
    for i, video in enumerate(videos):
        try:
            if video.url and not validate_youtube_url(str(video.url)):
                errors.append({"index": i, "error": "Invalid YouTube URL"})
                continue
            
            new_video = VideoInDB(
                url=video.url,
                title=video.title,
                keyword=video.keyword,
                duration=video.duration,
                priority=video.priority
            )
            
            videos_db[new_video.id] = new_video
            created.append(new_video.id)
            
        except Exception as e:
            errors.append({"index": i, "error": str(e)})
    
    return {
        "created_count": len(created),
        "error_count": len(errors),
        "created_ids": created,
        "errors": errors
    }


@app.put("/videos/{video_id}", response_model=VideoResponse)
async def update_video(video_id: str, video: VideoUpdate):
    """영상 업데이트"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    existing = videos_db[video_id]
    update_data = video.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    existing.updated_at = datetime.utcnow()
    
    return VideoResponse(**existing.model_dump())


@app.delete("/videos/{video_id}")
async def delete_video(video_id: str):
    """영상 삭제"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    del videos_db[video_id]
    
    return {"message": "Video deleted", "video_id": video_id}


@app.post("/videos/{video_id}/increment-completed")
async def increment_completed_count(video_id: str):
    """완료 횟수 증가"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = videos_db[video_id]
    video.completed_count += 1
    video.updated_at = datetime.utcnow()
    
    return {"video_id": video_id, "completed_count": video.completed_count}


@app.post("/videos/{video_id}/increment-error")
async def increment_error_count(video_id: str):
    """에러 횟수 증가"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = videos_db[video_id]
    video.error_count += 1
    video.updated_at = datetime.utcnow()
    
    return {"video_id": video_id, "error_count": video.error_count}


@app.get("/videos/search/by-keyword")
async def search_by_keyword(keyword: str, limit: int = 50):
    """키워드로 영상 검색"""
    results = [
        VideoResponse(**v.model_dump())
        for v in videos_db.values()
        if keyword.lower() in (v.keyword or "").lower()
    ]
    return {"count": len(results[:limit]), "videos": results[:limit]}


@app.get("/videos/pending/list")
async def get_pending_videos(limit: int = 100):
    """대기 중인 영상만 조회"""
    pending = [
        VideoResponse(**v.model_dump())
        for v in videos_db.values()
        if v.status == VideoStatus.PENDING
    ]
    pending.sort(key=lambda v: (-v.priority, v.created_at))
    return {"count": len(pending[:limit]), "videos": pending[:limit]}


# ==================== 실행 ====================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )

