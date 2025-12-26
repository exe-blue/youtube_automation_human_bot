"""
Human Pattern Service - 휴먼 패턴 생성 마이크로서비스
포트: 8004

PDF 문서 기반 실제 사용자 행동 패턴 생성
- 시청 패턴 (Beta 분포, Long-tail)
- 터치 패턴 (정규분포 오프셋)
- 스크롤 패턴 (Ease-in-out)
- 인터랙션 패턴 (좋아요/댓글 타이밍)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os

# 상위 디렉토리 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from shared.schemas.pattern import (
    HumanPatternConfig,
    GeneratedPattern,
    PatternRequest,
    PatternResponse,
    WatchPatternConfig,
    WatchPatternResult,
    TouchPatternConfig,
    ScrollPatternConfig,
    InteractionPatternConfig,
    InteractionPatternResult
)

from patterns.watch_pattern import WatchPatternGenerator
from patterns.touch_pattern import TouchPatternGenerator, GesturePatternGenerator
from patterns.scroll_pattern import ScrollPatternGenerator
from patterns.interaction_pattern import InteractionPatternGenerator, TypingPatternGenerator

# ==================== FastAPI 앱 ====================
app = FastAPI(
    title="Human Pattern Service",
    description="휴먼 행동 패턴 생성 마이크로서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 생성기 인스턴스 ====================
watch_generator = WatchPatternGenerator()
touch_generator = TouchPatternGenerator()
gesture_generator = GesturePatternGenerator()
scroll_generator = ScrollPatternGenerator()
interaction_generator = InteractionPatternGenerator()
typing_generator = TypingPatternGenerator()


# ==================== API 엔드포인트 ====================

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "human-pattern-service"}


@app.post("/patterns/generate", response_model=PatternResponse)
async def generate_pattern(request: PatternRequest):
    """
    통합 휴먼 패턴 생성
    
    영상 길이를 기반으로 모든 패턴 생성:
    - 시청 패턴 (시간, Seek)
    - 인터랙션 패턴 (좋아요, 댓글)
    """
    try:
        # 설정 오버라이드 적용
        config = request.config_override or HumanPatternConfig()
        
        # 시청 패턴 생성
        watch_gen = WatchPatternGenerator(config.watch)
        watch_result = watch_gen.generate(request.video_duration)
        
        # 인터랙션 패턴 생성
        interaction_gen = InteractionPatternGenerator(config.interaction)
        interaction_result = interaction_gen.generate(watch_result.watch_time)
        
        # 추천 액션 목록 생성
        recommended_actions = []
        if watch_result.seek_count > 0:
            recommended_actions.append(f"Seek {watch_result.seek_count}회 실행")
        if interaction_result.should_like:
            recommended_actions.append(f"좋아요 @ {interaction_result.like_timing}초")
        if interaction_result.should_comment:
            recommended_actions.append(f"댓글 @ {interaction_result.comment_timing}초")
        
        # 통합 패턴 생성
        pattern = GeneratedPattern(
            config=config,
            watch=watch_result,
            touch=config.touch,
            scroll=config.scroll,
            interaction=interaction_result,
            typing=config.typing
        )
        
        return PatternResponse(
            pattern=pattern,
            recommended_actions=recommended_actions
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/patterns/watch")
async def generate_watch_pattern(
    video_duration: int,
    config: Optional[WatchPatternConfig] = None
):
    """시청 패턴만 생성"""
    gen = WatchPatternGenerator(config)
    return gen.generate(video_duration)


@app.post("/patterns/touch")
async def generate_touch_pattern(
    element_x: int,
    element_y: int,
    element_width: int,
    element_height: int,
    config: Optional[TouchPatternConfig] = None
):
    """터치 패턴 생성"""
    gen = TouchPatternGenerator(config)
    return gen.generate_tap(element_x, element_y, element_width, element_height)


@app.post("/patterns/scroll")
async def generate_scroll_pattern(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration: Optional[int] = None,
    config: Optional[ScrollPatternConfig] = None
):
    """스크롤/스와이프 패턴 생성"""
    gen = ScrollPatternGenerator(config)
    return gen.generate_swipe(start_x, start_y, end_x, end_y, duration)


@app.post("/patterns/interaction")
async def generate_interaction_pattern(
    watch_time: int,
    config: Optional[InteractionPatternConfig] = None
):
    """인터랙션 패턴 생성"""
    gen = InteractionPatternGenerator(config)
    return gen.generate(watch_time)


@app.post("/patterns/typing")
async def generate_typing_pattern(text: str):
    """타이핑 패턴 생성"""
    return typing_generator.generate(text)


class ScrollDownRequest(BaseModel):
    screen_width: int = 1080
    screen_height: int = 2280
    config: Optional[ScrollPatternConfig] = None


@app.post("/patterns/scroll-down")
async def generate_scroll_down(request: ScrollDownRequest):
    """아래로 스크롤 패턴 생성 (Shorts/TikTok용)"""
    gen = ScrollPatternGenerator(request.config)
    return gen.generate_scroll_down(request.screen_width, request.screen_height)


@app.get("/patterns/shorts-timing")
async def generate_shorts_timing():
    """Shorts 스크롤 타이밍 생성"""
    timing = scroll_generator.generate_shorts_scroll_timing()
    return {"timing_seconds": timing}


# ==================== 통계/분석 엔드포인트 ====================

@app.get("/stats/watch-distribution")
async def get_watch_distribution(
    video_duration: int = 300,
    samples: int = 1000
):
    """시청 시간 분포 시뮬레이션"""
    distribution = watch_generator.simulate_watch_time_distribution(
        video_duration, samples
    )
    return {
        "video_duration": video_duration,
        "samples": samples,
        "distribution": distribution
    }


@app.get("/stats/interaction-rates")
async def get_interaction_rates(samples: int = 1000):
    """인터랙션 비율 시뮬레이션"""
    rates = interaction_generator.simulate_interaction_rates(samples)
    return {
        "samples": samples,
        "rates": rates
    }


# ==================== 실행 ====================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True
    )

