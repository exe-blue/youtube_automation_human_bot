"""
Result Service - 결과 수집 마이크로서비스
포트: 8005

- 결과 수집
- 통계 집계
- 리포트 생성
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timedelta
from collections import defaultdict
import uvicorn
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from shared.schemas.result import (
    ResultCreate,
    ResultInDB,
    ResultResponse,
    ResultListResponse,
    AggregatedStats,
    DailyStats,
    StatsResponse
)
from shared.schemas.task import SearchType

# ==================== FastAPI 앱 ====================
app = FastAPI(
    title="Result Service",
    description="결과 수집 마이크로서비스",
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
results_db: dict[str, ResultInDB] = {}


# ==================== 헬퍼 함수 ====================

def calculate_aggregated_stats() -> AggregatedStats:
    """전체 통계 계산"""
    results = list(results_db.values())
    
    if not results:
        return AggregatedStats()
    
    total_watch_time = sum(r.watch_time for r in results)
    avg_watch_percent = sum(r.watch_percent for r in results) / len(results) if results else 0
    
    total_likes = len([r for r in results if r.liked])
    total_comments = len([r for r in results if r.commented])
    
    like_rate = (total_likes / len(results)) * 100 if results else 0
    comment_rate = (total_comments / len(results)) * 100 if results else 0
    
    # 검색 타입 분포
    search_dist = defaultdict(int)
    for r in results:
        if r.search_type:
            search_dist[r.search_type] += 1
    
    # 평균 검색 순위
    ranks = [r.search_rank for r in results if r.search_rank > 0]
    avg_rank = sum(ranks) / len(ranks) if ranks else 0
    
    return AggregatedStats(
        total_tasks=len(results),
        completed_tasks=len(results),
        total_watch_time=total_watch_time,
        avg_watch_percent=round(avg_watch_percent, 2),
        total_likes=total_likes,
        like_rate=round(like_rate, 2),
        total_comments=total_comments,
        comment_rate=round(comment_rate, 2),
        search_type_distribution=dict(search_dist),
        avg_search_rank=round(avg_rank, 2)
    )


def calculate_daily_stats(days: int = 7) -> List[DailyStats]:
    """일별 통계 계산"""
    results = list(results_db.values())
    daily = defaultdict(lambda: {"completed": 0, "watch_time": 0, "likes": 0, "comments": 0})
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    for r in results:
        if r.created_at >= cutoff:
            date_str = r.created_at.strftime("%Y-%m-%d")
            daily[date_str]["completed"] += 1
            daily[date_str]["watch_time"] += r.watch_time
            if r.liked:
                daily[date_str]["likes"] += 1
            if r.commented:
                daily[date_str]["comments"] += 1
    
    return [
        DailyStats(
            date=date,
            tasks_completed=data["completed"],
            watch_time=data["watch_time"],
            likes=data["likes"],
            comments=data["comments"]
        )
        for date, data in sorted(daily.items(), reverse=True)
    ]


# ==================== API 엔드포인트 ====================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "result-service"}


@app.get("/results", response_model=ResultListResponse)
async def list_results(
    video_id: Optional[str] = None,
    device_id: Optional[str] = None,
    liked: Optional[bool] = None,
    commented: Optional[bool] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = 0
):
    """결과 목록 조회"""
    results = list(results_db.values())
    
    # 필터링
    if video_id:
        results = [r for r in results if r.video_id == video_id]
    if device_id:
        results = [r for r in results if r.device_id == device_id]
    if liked is not None:
        results = [r for r in results if r.liked == liked]
    if commented is not None:
        results = [r for r in results if r.commented == commented]
    
    # 정렬 (최근 것 먼저)
    results.sort(key=lambda r: r.created_at, reverse=True)
    
    # 페이지네이션
    paginated = results[offset:offset + limit]
    
    return ResultListResponse(
        total=len(results),
        results=[ResultResponse(**r.model_dump()) for r in paginated]
    )


@app.get("/results/{result_id}", response_model=ResultResponse)
async def get_result(result_id: str):
    """결과 상세 조회"""
    if result_id not in results_db:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return ResultResponse(**results_db[result_id].model_dump())


@app.post("/results", response_model=ResultResponse)
async def create_result(result: ResultCreate):
    """결과 제출"""
    # 시청 비율 계산
    watch_percent = 0
    if result.total_duration > 0:
        watch_percent = (result.watch_time / result.total_duration) * 100
    
    new_result = ResultInDB(
        task_id=result.task_id,
        device_id=result.device_id,
        video_id=result.task_id,  # 실제로는 task에서 video_id 조회 필요
        watch_time=result.watch_time,
        total_duration=result.total_duration,
        watch_percent=round(watch_percent, 2),
        liked=result.liked,
        commented=result.commented,
        comment_text=result.comment_text,
        search_type=result.search_type,
        search_rank=result.search_rank
    )
    
    # 스크린샷 처리 (Base64 → 파일 저장)
    if result.screenshot_base64:
        # TODO: 스크린샷 저장 로직
        pass
    
    results_db[new_result.id] = new_result
    
    return ResultResponse(**new_result.model_dump())


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """전체 통계 조회"""
    aggregated = calculate_aggregated_stats()
    daily = calculate_daily_stats(7)
    
    # 영상별 통계
    by_video = defaultdict(lambda: {
        "count": 0, "watch_time": 0, "likes": 0, "comments": 0
    })
    
    for r in results_db.values():
        by_video[r.video_id]["count"] += 1
        by_video[r.video_id]["watch_time"] += r.watch_time
        if r.liked:
            by_video[r.video_id]["likes"] += 1
        if r.commented:
            by_video[r.video_id]["comments"] += 1
    
    return StatsResponse(
        aggregated=aggregated,
        daily=daily,
        by_video=dict(by_video)
    )


@app.get("/stats/daily")
async def get_daily_stats(days: int = 7):
    """일별 통계 조회"""
    return calculate_daily_stats(days)


@app.get("/stats/video/{video_id}")
async def get_video_stats(video_id: str):
    """영상별 통계 조회"""
    video_results = [r for r in results_db.values() if r.video_id == video_id]
    
    if not video_results:
        return {
            "video_id": video_id,
            "total_views": 0,
            "total_watch_time": 0,
            "avg_watch_percent": 0,
            "like_count": 0,
            "comment_count": 0
        }
    
    return {
        "video_id": video_id,
        "total_views": len(video_results),
        "total_watch_time": sum(r.watch_time for r in video_results),
        "avg_watch_percent": round(
            sum(r.watch_percent for r in video_results) / len(video_results), 2
        ),
        "like_count": len([r for r in video_results if r.liked]),
        "comment_count": len([r for r in video_results if r.commented]),
        "search_type_distribution": dict(
            defaultdict(int, {r.search_type: 1 for r in video_results if r.search_type})
        )
    }


@app.get("/stats/device/{device_id}")
async def get_device_stats(device_id: str):
    """기기별 통계 조회"""
    device_results = [r for r in results_db.values() if r.device_id == device_id]
    
    return {
        "device_id": device_id,
        "total_tasks": len(device_results),
        "total_watch_time": sum(r.watch_time for r in device_results),
        "avg_watch_percent": round(
            sum(r.watch_percent for r in device_results) / len(device_results), 2
        ) if device_results else 0,
        "like_count": len([r for r in device_results if r.liked]),
        "comment_count": len([r for r in device_results if r.commented])
    }


@app.get("/stats/search-distribution")
async def get_search_distribution():
    """검색 경로별 분포"""
    dist = defaultdict(int)
    
    for r in results_db.values():
        if r.search_type:
            search_name = {
                1: "keyword",
                2: "recent",
                3: "title",
                4: "direct_url"
            }.get(r.search_type, "unknown")
            dist[search_name] += 1
    
    total = sum(dist.values())
    
    return {
        "distribution": dict(dist),
        "percentages": {
            k: round((v / total) * 100, 2) if total > 0 else 0
            for k, v in dist.items()
        }
    }


@app.delete("/results/{result_id}")
async def delete_result(result_id: str):
    """결과 삭제"""
    if result_id not in results_db:
        raise HTTPException(status_code=404, detail="Result not found")
    
    del results_db[result_id]
    
    return {"message": "Result deleted", "result_id": result_id}


# ==================== 실행 ====================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=True
    )

