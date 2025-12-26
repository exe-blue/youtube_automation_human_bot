"""
시청 패턴 생성 모듈
- PDF 문서 기반 Long-tail 분포 적용
- Beta 분포로 실제 사용자 시청 패턴 시뮬레이션
"""
import numpy as np
from typing import List, Optional
import sys
sys.path.append("../../..")

from shared.schemas.pattern import (
    WatchPatternConfig,
    WatchPatternResult,
    WatchDistribution
)


class WatchPatternGenerator:
    """시청 패턴 생성기"""
    
    # 실제 사용자 시청 시간 분포 (PDF 문서 기반)
    WATCH_TIME_DISTRIBUTION = {
        "0-10초": 0.35,      # 즉시 이탈
        "10-30초": 0.25,     # 초반 이탈
        "30초-1분": 0.15,    # 짧은 시청
        "1-3분": 0.12,       # 중간 시청
        "3-5분": 0.08,       # 긴 시청
        "5분+": 0.05         # 완전 시청
    }
    
    def __init__(self, config: Optional[WatchPatternConfig] = None):
        self.config = config or WatchPatternConfig()
    
    def generate(self, video_duration: int) -> WatchPatternResult:
        """
        시청 패턴 생성
        
        Args:
            video_duration: 영상 전체 길이 (초)
        
        Returns:
            WatchPatternResult: 생성된 시청 패턴
        """
        # 5% 확률로 완전 시청
        if np.random.random() < self.config.full_watch_probability:
            watch_time = video_duration
            is_full_watch = True
        else:
            watch_time = self._generate_watch_time(video_duration)
            is_full_watch = False
        
        # Seek 횟수 및 타이밍 결정
        seek_count = 0
        seek_timings = []
        
        if self.config.seek_enabled and watch_time > 30:  # 30초 이상 시청 시에만 Seek
            seek_count = np.random.randint(
                self.config.seek_count_min, 
                self.config.seek_count_max + 1
            )
            seek_timings = self._generate_seek_timings(watch_time, seek_count)
        
        watch_percent = (watch_time / video_duration) * 100 if video_duration > 0 else 0
        
        return WatchPatternResult(
            watch_time=int(watch_time),
            watch_percent=round(watch_percent, 2),
            is_full_watch=is_full_watch,
            seek_count=seek_count,
            seek_timings=seek_timings
        )
    
    def _generate_watch_time(self, video_duration: int) -> int:
        """
        Beta 분포 기반 시청 시간 생성
        - alpha=2, beta=5: 초반 이탈이 많은 Long-tail 분포
        """
        if self.config.distribution == WatchDistribution.BETA:
            # Beta 분포 (Long-tail)
            ratio = np.random.beta(self.config.alpha, self.config.beta)
        
        elif self.config.distribution == WatchDistribution.NORMAL:
            # 정규 분포 (평균 50%, 표준편차 20%)
            ratio = np.random.normal(0.5, 0.2)
            ratio = np.clip(ratio, 0, 1)
        
        else:  # UNIFORM
            ratio = np.random.uniform(0, 1)
        
        # 최소 시청 시간 보장
        watch_time = max(self.config.min_watch_seconds, ratio * video_duration)
        
        # 영상 길이 초과 방지
        watch_time = min(watch_time, video_duration)
        
        return int(watch_time)
    
    def _generate_seek_timings(self, watch_time: int, seek_count: int) -> List[int]:
        """
        Seek (앞으로/뒤로 가기) 타이밍 생성
        - 시청 시간 내에서 균등하게 분포 + 약간의 랜덤성
        """
        if seek_count == 0 or watch_time < 10:
            return []
        
        # 기본 간격 계산
        interval = watch_time / (seek_count + 1)
        
        timings = []
        for i in range(1, seek_count + 1):
            base_time = interval * i
            
            # ±20% 랜덤 변동
            variation = interval * 0.2
            actual_time = base_time + np.random.uniform(-variation, variation)
            
            # 범위 제한 (10초 ~ watch_time - 5초)
            actual_time = np.clip(actual_time, 10, watch_time - 5)
            timings.append(int(actual_time))
        
        # 정렬 및 중복 제거
        timings = sorted(list(set(timings)))
        
        return timings
    
    def simulate_watch_time_distribution(self, video_duration: int, 
                                         samples: int = 1000) -> dict:
        """
        시청 시간 분포 시뮬레이션 (테스트/분석용)
        """
        results = {
            "0-10초": 0,
            "10-30초": 0,
            "30초-1분": 0,
            "1-3분": 0,
            "3-5분": 0,
            "5분+": 0
        }
        
        for _ in range(samples):
            pattern = self.generate(video_duration)
            watch_time = pattern.watch_time
            
            if watch_time <= 10:
                results["0-10초"] += 1
            elif watch_time <= 30:
                results["10-30초"] += 1
            elif watch_time <= 60:
                results["30초-1분"] += 1
            elif watch_time <= 180:
                results["1-3분"] += 1
            elif watch_time <= 300:
                results["3-5분"] += 1
            else:
                results["5분+"] += 1
        
        # 비율로 변환
        return {k: v / samples for k, v in results.items()}


# 인터랙션 타이밍 생성 헬퍼 함수
def calculate_like_timing(watch_time: int) -> int:
    """
    자연스러운 좋아요 타이밍 생성 (PDF 문서 기반)
    
    분포:
    - 시청 시작 5초 이내: 2%
    - 시청 중간 지점: 35%
    - 시청 완료 직후: 45%
    - 시청 완료 후 10초+: 18%
    """
    rand = np.random.random()
    
    if rand < 0.02:  # 2% - 즉시 좋아요
        return int(np.random.uniform(3, 5))
    
    elif rand < 0.37:  # 35% - 시청 중간
        return int(watch_time * np.random.uniform(0.4, 0.6))
    
    elif rand < 0.82:  # 45% - 시청 완료 직후
        return int(watch_time + np.random.uniform(1, 3))
    
    else:  # 18% - 10초+ 후
        return int(watch_time + np.random.uniform(10, 30))


if __name__ == "__main__":
    # 테스트
    generator = WatchPatternGenerator()
    
    # 5분 영상에 대한 시청 패턴 생성
    for i in range(5):
        pattern = generator.generate(300)
        print(f"[{i+1}] 시청: {pattern.watch_time}초 ({pattern.watch_percent}%), "
              f"Seek: {pattern.seek_count}회, 완전시청: {pattern.is_full_watch}")
    
    # 분포 시뮬레이션
    print("\n=== 시청 시간 분포 시뮬레이션 ===")
    dist = generator.simulate_watch_time_distribution(300, 10000)
    for k, v in dist.items():
        print(f"{k}: {v*100:.1f}%")

