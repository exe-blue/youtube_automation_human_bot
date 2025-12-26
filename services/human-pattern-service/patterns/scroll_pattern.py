"""
스크롤/스와이프 패턴 생성 모듈
- PDF 문서 기반 자연스러운 스와이프
- Ease-in-out 커브 적용
- 속도 변화 및 노이즈 추가
"""
import numpy as np
from typing import List, Tuple, Optional
import sys
sys.path.append("../../..")

from shared.schemas.pattern import (
    ScrollPatternConfig,
    ScrollPatternResult,
    SwipePoint,
    SwipeEasing
)


class ScrollPatternGenerator:
    """스크롤/스와이프 패턴 생성기"""
    
    # TikTok/Shorts 스크롤 패턴 분포 (PDF 문서 기반)
    SCROLL_TIMING_DISTRIBUTION = {
        "instant_skip": 0.25,    # 즉시 스킵 (1초 이내)
        "short_view": 0.30,      # 짧게 시청 (1-3초)
        "medium_view": 0.28,     # 중간 시청 (3-10초)
        "full_view": 0.17        # 완전 시청 (10초+)
    }
    
    def __init__(self, config: Optional[ScrollPatternConfig] = None):
        self.config = config or ScrollPatternConfig()
    
    def generate_swipe(self,
                       start_x: int,
                       start_y: int,
                       end_x: int,
                       end_y: int,
                       duration: Optional[int] = None) -> ScrollPatternResult:
        """
        자연스러운 스와이프 경로 생성
        
        Args:
            start_x, start_y: 시작 좌표
            end_x, end_y: 종료 좌표
            duration: 스와이프 지속 시간 (ms), None이면 자동 계산
        
        Returns:
            ScrollPatternResult: 생성된 스와이프 패턴
        """
        # 지속 시간 결정
        if duration is None:
            duration = np.random.randint(
                self.config.duration_min,
                self.config.duration_max + 1
            )
        
        # 경로 포인트 수 (10ms 간격)
        steps = max(duration // 10, 5)
        
        # 경로 생성
        path = self._generate_path(
            start_x, start_y, end_x, end_y, 
            steps, duration
        )
        
        # 스와이프 후 대기 시간
        pause_after = np.random.randint(
            self.config.pause_after_min,
            self.config.pause_after_max + 1
        )
        
        return ScrollPatternResult(
            path=path,
            total_duration=duration,
            pause_after=pause_after,
            easing_applied=self.config.easing
        )
    
    def _generate_path(self,
                       start_x: int,
                       start_y: int,
                       end_x: int,
                       end_y: int,
                       steps: int,
                       duration: int) -> List[SwipePoint]:
        """
        이징 함수가 적용된 스와이프 경로 생성
        """
        path = []
        
        for i in range(steps + 1):
            t = i / steps  # 0.0 ~ 1.0
            
            # 이징 함수 적용
            ease_t = self._apply_easing(t)
            
            # 기본 좌표 계산
            x = start_x + (end_x - start_x) * ease_t
            y = start_y + (end_y - start_y) * ease_t
            
            # 노이즈 추가 (시작점과 끝점 제외)
            if self.config.noise_enabled and 0 < i < steps:
                noise_x = np.random.normal(0, self.config.noise_std)
                noise_y = np.random.normal(0, self.config.noise_std)
                x += noise_x
                y += noise_y
            
            # 타임스탬프 계산
            timestamp = int((duration * i) / steps)
            
            path.append(SwipePoint(
                x=int(x),
                y=int(y),
                timestamp=timestamp
            ))
        
        return path
    
    def _apply_easing(self, t: float) -> float:
        """
        이징 함수 적용
        
        Args:
            t: 0.0 ~ 1.0 정규화된 시간
        
        Returns:
            이징이 적용된 0.0 ~ 1.0 값
        """
        if self.config.easing == SwipeEasing.LINEAR:
            return t
        
        elif self.config.easing == SwipeEasing.EASE_IN:
            # 천천히 시작
            return t * t
        
        elif self.config.easing == SwipeEasing.EASE_OUT:
            # 천천히 끝남
            return 1 - (1 - t) ** 2
        
        elif self.config.easing == SwipeEasing.EASE_IN_OUT:
            # Smoothstep: 천천히 시작하고 끝남 (기본)
            return t * t * (3 - 2 * t)
        
        elif self.config.easing == SwipeEasing.BEZIER:
            # 3차 베지어 근사
            return t * t * t * (t * (6 * t - 15) + 10)
        
        return t
    
    def generate_scroll_down(self,
                             screen_width: int,
                             screen_height: int) -> ScrollPatternResult:
        """
        아래로 스크롤 (위로 스와이프) 패턴 생성
        """
        # 화면 중앙 기준
        center_x = screen_width // 2
        
        # 시작점: 화면 하단 70%
        start_y = int(screen_height * 0.7)
        
        # 종료점: 화면 상단 30%
        end_y = int(screen_height * 0.3)
        
        # X 좌표에 약간의 변화
        x_variation = int(screen_width * 0.1)
        start_x = center_x + np.random.randint(-x_variation, x_variation)
        end_x = center_x + np.random.randint(-x_variation, x_variation)
        
        return self.generate_swipe(start_x, start_y, end_x, end_y)
    
    def generate_scroll_up(self,
                           screen_width: int,
                           screen_height: int) -> ScrollPatternResult:
        """
        위로 스크롤 (아래로 스와이프) 패턴 생성
        """
        center_x = screen_width // 2
        
        start_y = int(screen_height * 0.3)
        end_y = int(screen_height * 0.7)
        
        x_variation = int(screen_width * 0.1)
        start_x = center_x + np.random.randint(-x_variation, x_variation)
        end_x = center_x + np.random.randint(-x_variation, x_variation)
        
        return self.generate_swipe(start_x, start_y, end_x, end_y)
    
    def generate_shorts_scroll_timing(self) -> float:
        """
        Shorts/TikTok 스크롤 타이밍 생성 (초)
        PDF 문서 분포 기반
        """
        rand = np.random.random()
        
        if rand < self.config.instant_skip_probability:
            # 즉시 스킵 (0.5-1.5초)
            return np.random.uniform(0.5, 1.5)
        
        elif rand < (self.config.instant_skip_probability + 
                     self.config.short_view_probability):
            # 짧게 시청 (1.5-3.5초)
            return np.random.uniform(1.5, 3.5)
        
        elif rand < 0.83:
            # 중간 시청 (3.5-10초)
            return np.random.uniform(3.5, 10)
        
        else:
            # 완전 시청 (10-30초)
            return np.random.uniform(10, 30)
    
    def generate_seek_swipe(self,
                            screen_width: int,
                            screen_height: int,
                            direction: str = "forward") -> ScrollPatternResult:
        """
        Seek (앞으로/뒤로 가기) 스와이프 생성
        YouTube 더블 탭 영역 기준
        
        Args:
            direction: "forward" (오른쪽 더블탭) or "backward" (왼쪽 더블탭)
        """
        # 비디오 영역 높이 (화면 상단 40%)
        video_y = int(screen_height * 0.2)
        video_height = int(screen_height * 0.4)
        
        if direction == "forward":
            # 오른쪽 영역 (화면 우측 1/3)
            tap_x = int(screen_width * 0.75)
        else:
            # 왼쪽 영역 (화면 좌측 1/3)
            tap_x = int(screen_width * 0.25)
        
        tap_y = video_y + video_height // 2
        
        # 더블 탭은 짧은 스와이프로 시뮬레이션 (같은 위치 두 번)
        return self.generate_swipe(tap_x, tap_y, tap_x, tap_y, duration=50)


if __name__ == "__main__":
    # 테스트
    generator = ScrollPatternGenerator()
    
    print("=== 스와이프 경로 테스트 ===")
    result = generator.generate_swipe(500, 1800, 520, 500)
    print(f"총 시간: {result.total_duration}ms")
    print(f"포인트 수: {len(result.path)}")
    print(f"대기 시간: {result.pause_after}ms")
    print(f"첫 3개 포인트:")
    for p in result.path[:3]:
        print(f"  ({p.x}, {p.y}) @ {p.timestamp}ms")
    print(f"마지막 3개 포인트:")
    for p in result.path[-3:]:
        print(f"  ({p.x}, {p.y}) @ {p.timestamp}ms")
    
    print("\n=== Shorts 스크롤 타이밍 분포 ===")
    timings = [generator.generate_shorts_scroll_timing() for _ in range(1000)]
    instant = len([t for t in timings if t < 1.5])
    short = len([t for t in timings if 1.5 <= t < 3.5])
    medium = len([t for t in timings if 3.5 <= t < 10])
    full = len([t for t in timings if t >= 10])
    print(f"즉시 스킵 (<1.5초): {instant/10}%")
    print(f"짧은 시청 (1.5-3.5초): {short/10}%")
    print(f"중간 시청 (3.5-10초): {medium/10}%")
    print(f"완전 시청 (10초+): {full/10}%")

