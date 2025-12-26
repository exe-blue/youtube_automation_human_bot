"""
터치 패턴 생성 모듈
- PDF 문서 기반 자연스러운 터치 시뮬레이션
- 정규분포 기반 위치 오프셋
- 터치 지속 시간 변화
"""
import numpy as np
from typing import Tuple, Optional
import sys
sys.path.append("../../..")

from shared.schemas.pattern import (
    TouchPatternConfig,
    TouchPatternResult,
    TouchPoint,
    TouchAccuracy
)


class TouchPatternGenerator:
    """터치 패턴 생성기"""
    
    def __init__(self, config: Optional[TouchPatternConfig] = None):
        self.config = config or TouchPatternConfig()
    
    def generate_tap(self, 
                     element_x: int, 
                     element_y: int, 
                     element_width: int, 
                     element_height: int) -> TouchPatternResult:
        """
        자연스러운 터치 좌표 생성
        
        Args:
            element_x: 요소 좌상단 X
            element_y: 요소 좌상단 Y
            element_width: 요소 너비
            element_height: 요소 높이
        
        Returns:
            TouchPatternResult: 생성된 터치 패턴
        """
        # 요소 중심점
        center_x = element_x + element_width / 2
        center_y = element_y + element_height / 2
        
        if self.config.accuracy == TouchAccuracy.PRECISE:
            # 봇처럼 정확한 중심 터치
            tap_x = int(center_x)
            tap_y = int(center_y)
            is_offset = False
            offset_x = 0
            offset_y = 0
        else:
            # 정규분포로 중심 근처 랜덤 (실제 사용자처럼)
            std_x = element_width * self.config.position_std_ratio
            std_y = element_height * self.config.position_std_ratio
            
            if self.config.accuracy == TouchAccuracy.SLOPPY:
                # 더 부정확하게
                std_x *= 1.5
                std_y *= 1.5
            
            tap_x = np.random.normal(center_x, std_x)
            tap_y = np.random.normal(center_y, std_y)
            
            # 요소 범위 내로 클리핑 (가장자리 5px 마진)
            margin = 5
            tap_x = np.clip(tap_x, element_x + margin, element_x + element_width - margin)
            tap_y = np.clip(tap_y, element_y + margin, element_y + element_height - margin)
            
            tap_x = int(tap_x)
            tap_y = int(tap_y)
            
            is_offset = True
            offset_x = tap_x - int(center_x)
            offset_y = tap_y - int(center_y)
        
        # 터치 지속 시간 (정규분포)
        duration = self._generate_touch_duration()
        
        return TouchPatternResult(
            tap_point=TouchPoint(x=tap_x, y=tap_y, duration=duration),
            is_offset=is_offset,
            offset_x=offset_x,
            offset_y=offset_y
        )
    
    def generate_double_tap(self, 
                            element_x: int, 
                            element_y: int,
                            element_width: int, 
                            element_height: int) -> Tuple[TouchPatternResult, TouchPatternResult, int]:
        """
        더블 탭 패턴 생성
        
        Returns:
            (첫 번째 탭, 두 번째 탭, 간격 ms)
        """
        tap1 = self.generate_tap(element_x, element_y, element_width, element_height)
        tap2 = self.generate_tap(element_x, element_y, element_width, element_height)
        
        # 더블 탭 간격
        interval = np.random.randint(
            self.config.double_tap_interval_min,
            self.config.double_tap_interval_max + 1
        )
        
        return tap1, tap2, interval
    
    def _generate_touch_duration(self) -> int:
        """
        터치 지속 시간 생성 (정규분포)
        실제 터치는 50-200ms
        """
        duration = np.random.normal(
            self.config.duration_mean,
            self.config.duration_std
        )
        
        # 범위 제한
        duration = np.clip(
            duration,
            self.config.duration_min,
            self.config.duration_max
        )
        
        return int(duration)
    
    def generate_long_press(self, 
                           element_x: int, 
                           element_y: int,
                           element_width: int, 
                           element_height: int,
                           duration_ms: int = 500) -> TouchPatternResult:
        """
        롱프레스 패턴 생성
        """
        result = self.generate_tap(element_x, element_y, element_width, element_height)
        result.tap_point.duration = duration_ms + np.random.randint(-50, 50)
        return result


class GesturePatternGenerator:
    """복합 제스처 패턴 생성기"""
    
    def __init__(self, touch_config: Optional[TouchPatternConfig] = None):
        self.touch_generator = TouchPatternGenerator(touch_config)
    
    def generate_tap_sequence(self, 
                              points: list,
                              interval_min: int = 200,
                              interval_max: int = 500) -> list:
        """
        연속 탭 시퀀스 생성
        
        Args:
            points: [(x, y, width, height), ...] 리스트
            interval_min: 탭 간 최소 간격 (ms)
            interval_max: 탭 간 최대 간격 (ms)
        
        Returns:
            [(TouchPatternResult, interval), ...]
        """
        sequence = []
        
        for i, (x, y, w, h) in enumerate(points):
            tap = self.touch_generator.generate_tap(x, y, w, h)
            
            # 마지막이 아니면 간격 추가
            if i < len(points) - 1:
                interval = np.random.randint(interval_min, interval_max + 1)
            else:
                interval = 0
            
            sequence.append((tap, interval))
        
        return sequence


if __name__ == "__main__":
    # 테스트
    generator = TouchPatternGenerator()
    
    # 버튼 영역 (100, 200)에서 (200, 250)
    for i in range(5):
        result = generator.generate_tap(100, 200, 100, 50)
        print(f"[{i+1}] 터치: ({result.tap_point.x}, {result.tap_point.y}), "
              f"지속: {result.tap_point.duration}ms, "
              f"오프셋: ({result.offset_x}, {result.offset_y})")
    
    print("\n=== 더블 탭 테스트 ===")
    tap1, tap2, interval = generator.generate_double_tap(100, 200, 100, 50)
    print(f"첫 번째: ({tap1.tap_point.x}, {tap1.tap_point.y})")
    print(f"두 번째: ({tap2.tap_point.x}, {tap2.tap_point.y})")
    print(f"간격: {interval}ms")

