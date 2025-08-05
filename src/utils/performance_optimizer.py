"""
성능 최적화 시스템
대용량 파일 처리, 데이터 캐싱, 메모리 최적화 구현
"""

import pandas as pd
import numpy as np
import time
import gc
import psutil
import os
import hashlib
import pickle
import logging
from typing import List, Dict, Any, Optional, Tuple, Iterator, Callable
from pathlib import Path
from functools import wraps, lru_cache
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
import weakref

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """성능 메트릭 데이터 클래스"""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    memory_before: float
    memory_after: float
    memory_peak: float
    cpu_usage: float
    data_size: int
    success: bool
    error_message: Optional[str] = None


class MemoryMonitor:
    """메모리 사용량 모니터링 클래스"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.peak_memory = 0
        self.monitoring = False
        self._monitor_thread = None
    
    def start_monitoring(self):
        """메모리 모니터링 시작"""
        self.monitoring = True
        self.peak_memory = self.get_current_memory()
        self._monitor_thread = threading.Thread(target=self._monitor_memory)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
    
    def stop_monitoring(self) -> float:
        """메모리 모니터링 중지 및 피크 메모리 반환"""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        return self.peak_memory
    
    def _monitor_memory(self):
        """메모리 모니터링 스레드"""
        while self.monitoring:
            current_memory = self.get_current_memory()
            if current_memory > self.peak_memory:
                self.peak_memory = current_memory
            time.sleep(0.1)  # 100ms 간격으로 모니터링
    
    def get_current_memory(self) -> float:
        """현재 메모리 사용량 반환 (MB)"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_memory_percent(self) -> float:
        """메모리 사용률 반환 (%)"""
        return self.process.memory_percent()


class DataCache:
    """데이터 캐싱 시스템"""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        캐시 초기화
        
        Args:
            max_size: 최대 캐시 항목 수
            ttl_seconds: 캐시 유효 시간 (초)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.access_times = {}
        self.creation_times = {}
        self._lock = threading.RLock()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        with self._lock:
            if key not in self.cache:
                return None
            
            # TTL 확인
            if self._is_expired(key):
                self._remove_key(key)
                return None
            
            # 접근 시간 업데이트
            self.access_times[key] = time.time()
            return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """캐시에 데이터 저장"""
        with self._lock:
            # 캐시 크기 제한 확인
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()
            
            self.cache[key] = value
            self.access_times[key] = time.time()
            self.creation_times[key] = time.time()
    
    def _is_expired(self, key: str) -> bool:
        """캐시 항목 만료 확인"""
        if key not in self.creation_times:
            return True
        
        age = time.time() - self.creation_times[key]
        return age > self.ttl_seconds
    
    def _evict_lru(self) -> None:
        """LRU 정책으로 캐시 항목 제거"""
        if not self.access_times:
            return
        
        # 가장 오래된 접근 시간을 가진 키 찾기
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self._remove_key(lru_key)
    
    def _remove_key(self, key: str) -> None:
        """캐시 키 제거"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.creation_times.pop(key, None)
    
    def clear(self) -> None:
        """캐시 전체 삭제"""
        with self._lock:
            self.cache.clear()
            self.access_times.clear()
            self.creation_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        with self._lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hit_rate': getattr(self, '_hit_count', 0) / max(getattr(self, '_total_requests', 1), 1),
                'memory_usage_mb': sum(
                    len(pickle.dumps(value)) for value in self.cache.values()
                ) / 1024 / 1024
            }


class ChunkedDataProcessor:
    """대용량 데이터 청크 처리 클래스"""
    
    def __init__(self, chunk_size: int = 1000, max_workers: int = None):
        """
        청크 처리기 초기화
        
        Args:
            chunk_size: 청크 크기
            max_workers: 최대 워커 수
        """
        self.chunk_size = chunk_size
        self.max_workers = max_workers or min(4, os.cpu_count() or 1)
        self.memory_monitor = MemoryMonitor()
    
    def process_dataframe_chunks(
        self, 
        df: pd.DataFrame, 
        process_func: Callable[[pd.DataFrame], Any],
        combine_func: Callable[[List[Any]], Any] = None
    ) -> Any:
        """
        DataFrame을 청크 단위로 처리
        
        Args:
            df: 처리할 DataFrame
            process_func: 각 청크에 적용할 함수
            combine_func: 결과를 결합하는 함수
            
        Returns:
            처리된 결과
        """
        logger.info(f"청크 처리 시작: {len(df)}행, 청크 크기: {self.chunk_size}")
        
        self.memory_monitor.start_monitoring()
        start_time = time.time()
        
        try:
            # 청크 생성
            chunks = [df[i:i + self.chunk_size] for i in range(0, len(df), self.chunk_size)]
            logger.info(f"총 {len(chunks)}개 청크 생성")
            
            # 병렬 처리
            results = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(process_func, chunk) for chunk in chunks]
                
                for i, future in enumerate(futures):
                    try:
                        result = future.result(timeout=30)  # 30초 타임아웃
                        results.append(result)
                        logger.debug(f"청크 {i+1}/{len(chunks)} 처리 완료")
                    except Exception as e:
                        logger.error(f"청크 {i+1} 처리 실패: {e}")
                        continue
            
            # 결과 결합
            if combine_func and results:
                final_result = combine_func(results)
            elif results:
                final_result = results[0] if len(results) == 1 else results
            else:
                final_result = None
            
            # 메모리 정리
            del chunks, results
            gc.collect()
            
            duration = time.time() - start_time
            peak_memory = self.memory_monitor.stop_monitoring()
            
            logger.info(f"청크 처리 완료: {duration:.2f}초, 피크 메모리: {peak_memory:.1f}MB")
            
            return final_result
            
        except Exception as e:
            self.memory_monitor.stop_monitoring()
            logger.error(f"청크 처리 실패: {e}")
            raise
    
    def process_file_chunks(
        self, 
        file_path: str, 
        process_func: Callable[[pd.DataFrame], Any],
        combine_func: Callable[[List[Any]], Any] = None,
        **read_kwargs
    ) -> Any:
        """
        파일을 청크 단위로 읽어서 처리
        
        Args:
            file_path: 파일 경로
            process_func: 각 청크에 적용할 함수
            combine_func: 결과를 결합하는 함수
            **read_kwargs: pandas.read_excel 추가 인자
            
        Returns:
            처리된 결과
        """
        logger.info(f"파일 청크 처리 시작: {file_path}")
        
        self.memory_monitor.start_monitoring()
        start_time = time.time()
        
        try:
            results = []
            chunk_count = 0
            
            # 파일을 청크 단위로 읽기
            for chunk in pd.read_excel(
                file_path, 
                chunksize=self.chunk_size,
                **read_kwargs
            ):
                chunk_count += 1
                logger.debug(f"청크 {chunk_count} 처리 중 ({len(chunk)}행)")
                
                try:
                    result = process_func(chunk)
                    results.append(result)
                except Exception as e:
                    logger.error(f"청크 {chunk_count} 처리 실패: {e}")
                    continue
                
                # 메모리 사용량 확인
                current_memory = self.memory_monitor.get_current_memory()
                if current_memory > 1000:  # 1GB 초과 시 경고
                    logger.warning(f"높은 메모리 사용량: {current_memory:.1f}MB")
                    gc.collect()  # 가비지 컬렉션 강제 실행
            
            # 결과 결합
            if combine_func and results:
                final_result = combine_func(results)
            elif results:
                final_result = results[0] if len(results) == 1 else results
            else:
                final_result = None
            
            duration = time.time() - start_time
            peak_memory = self.memory_monitor.stop_monitoring()
            
            logger.info(f"파일 청크 처리 완료: {chunk_count}개 청크, {duration:.2f}초, 피크 메모리: {peak_memory:.1f}MB")
            
            return final_result
            
        except Exception as e:
            self.memory_monitor.stop_monitoring()
            logger.error(f"파일 청크 처리 실패: {e}")
            raise


class PerformanceOptimizer:
    """성능 최적화 메인 클래스"""
    
    def __init__(self, cache_size: int = 100, chunk_size: int = 1000):
        """
        성능 최적화기 초기화
        
        Args:
            cache_size: 캐시 크기
            chunk_size: 청크 크기
        """
        self.cache = DataCache(max_size=cache_size)
        self.chunked_processor = ChunkedDataProcessor(chunk_size=chunk_size)
        self.memory_monitor = MemoryMonitor()
        self.metrics_history = []
        self._optimization_enabled = True
    
    def performance_monitor(self, operation_name: str):
        """성능 모니터링 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self._optimization_enabled:
                    return func(*args, **kwargs)
                
                # 성능 측정 시작
                start_time = time.time()
                memory_before = self.memory_monitor.get_current_memory()
                self.memory_monitor.start_monitoring()
                
                success = True
                error_message = None
                result = None
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    error_message = str(e)
                    raise
                finally:
                    # 성능 측정 종료
                    end_time = time.time()
                    duration = end_time - start_time
                    memory_after = self.memory_monitor.get_current_memory()
                    memory_peak = self.memory_monitor.stop_monitoring()
                    cpu_usage = psutil.cpu_percent()
                    
                    # 데이터 크기 추정
                    data_size = 0
                    if hasattr(result, '__len__'):
                        data_size = len(result)
                    elif isinstance(result, pd.DataFrame):
                        data_size = len(result)
                    
                    # 메트릭 기록
                    metric = PerformanceMetrics(
                        operation_name=operation_name,
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        memory_before=memory_before,
                        memory_after=memory_after,
                        memory_peak=memory_peak,
                        cpu_usage=cpu_usage,
                        data_size=data_size,
                        success=success,
                        error_message=error_message
                    )
                    
                    self.metrics_history.append(metric)
                    
                    # 성능 로그
                    if success:
                        logger.info(
                            f"{operation_name} 완료: {duration:.2f}초, "
                            f"메모리: {memory_before:.1f}→{memory_after:.1f}MB "
                            f"(피크: {memory_peak:.1f}MB), CPU: {cpu_usage:.1f}%"
                        )
                    else:
                        logger.error(f"{operation_name} 실패: {error_message}")
            
            return wrapper
        return decorator
    
    def cached_operation(self, cache_key: str = None, ttl: int = 3600):
        """캐시된 연산 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self._optimization_enabled:
                    return func(*args, **kwargs)
                
                # 캐시 키 생성
                if cache_key:
                    key = cache_key
                else:
                    key = f"{func.__name__}_{self.cache._generate_key(*args, **kwargs)}"
                
                # 캐시에서 조회
                cached_result = self.cache.get(key)
                if cached_result is not None:
                    logger.debug(f"캐시 히트: {func.__name__}")
                    return cached_result
                
                # 캐시 미스 - 함수 실행
                logger.debug(f"캐시 미스: {func.__name__}")
                result = func(*args, **kwargs)
                
                # 결과 캐시에 저장
                self.cache.set(key, result)
                
                return result
            
            return wrapper
        return decorator
    
    def optimize_dataframe_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame 메모리 사용량 최적화"""
        logger.info(f"DataFrame 메모리 최적화 시작: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f}MB")
        
        optimized_df = df.copy()
        
        for col in optimized_df.columns:
            col_type = optimized_df[col].dtype
            
            if col_type == 'object':
                # 문자열 컬럼 최적화
                try:
                    # 카테고리로 변환 가능한지 확인
                    unique_ratio = optimized_df[col].nunique() / len(optimized_df)
                    if unique_ratio < 0.5:  # 고유값 비율이 50% 미만이면 카테고리로 변환
                        optimized_df[col] = optimized_df[col].astype('category')
                except:
                    pass
            
            elif col_type in ['int64', 'int32']:
                # 정수 컬럼 최적화
                col_min = optimized_df[col].min()
                col_max = optimized_df[col].max()
                
                if col_min >= 0:
                    if col_max < 255:
                        optimized_df[col] = optimized_df[col].astype('uint8')
                    elif col_max < 65535:
                        optimized_df[col] = optimized_df[col].astype('uint16')
                    elif col_max < 4294967295:
                        optimized_df[col] = optimized_df[col].astype('uint32')
                else:
                    if col_min > -128 and col_max < 127:
                        optimized_df[col] = optimized_df[col].astype('int8')
                    elif col_min > -32768 and col_max < 32767:
                        optimized_df[col] = optimized_df[col].astype('int16')
                    elif col_min > -2147483648 and col_max < 2147483647:
                        optimized_df[col] = optimized_df[col].astype('int32')
            
            elif col_type in ['float64', 'float32']:
                # 실수 컬럼 최적화
                optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')
        
        memory_after = optimized_df.memory_usage(deep=True).sum() / 1024 / 1024
        memory_before = df.memory_usage(deep=True).sum() / 1024 / 1024
        reduction = (memory_before - memory_after) / memory_before * 100
        
        logger.info(f"DataFrame 메모리 최적화 완료: {memory_before:.1f}MB → {memory_after:.1f}MB ({reduction:.1f}% 감소)")
        
        return optimized_df
    
    def get_performance_report(self) -> Dict[str, Any]:
        """성능 보고서 생성"""
        if not self.metrics_history:
            return {'message': '성능 데이터가 없습니다.'}
        
        # 최근 메트릭 분석
        recent_metrics = self.metrics_history[-10:]  # 최근 10개
        
        avg_duration = np.mean([m.duration for m in recent_metrics])
        avg_memory_usage = np.mean([m.memory_peak - m.memory_before for m in recent_metrics])
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics) * 100
        
        # 가장 느린 연산 찾기
        slowest_operation = max(self.metrics_history, key=lambda m: m.duration)
        
        # 메모리 사용량이 가장 높은 연산 찾기
        highest_memory_operation = max(self.metrics_history, key=lambda m: m.memory_peak)
        
        return {
            'total_operations': len(self.metrics_history),
            'avg_duration': round(avg_duration, 2),
            'avg_memory_usage_mb': round(avg_memory_usage, 1),
            'success_rate': round(success_rate, 1),
            'cache_stats': self.cache.get_stats(),
            'slowest_operation': {
                'name': slowest_operation.operation_name,
                'duration': round(slowest_operation.duration, 2),
                'timestamp': datetime.fromtimestamp(slowest_operation.start_time).isoformat()
            },
            'highest_memory_operation': {
                'name': highest_memory_operation.operation_name,
                'memory_peak_mb': round(highest_memory_operation.memory_peak, 1),
                'timestamp': datetime.fromtimestamp(highest_memory_operation.start_time).isoformat()
            },
            'current_memory_mb': round(self.memory_monitor.get_current_memory(), 1),
            'current_memory_percent': round(self.memory_monitor.get_memory_percent(), 1)
        }
    
    def clear_cache(self) -> None:
        """캐시 삭제"""
        self.cache.clear()
        logger.info("캐시가 삭제되었습니다.")
    
    def clear_metrics(self) -> None:
        """성능 메트릭 삭제"""
        self.metrics_history.clear()
        logger.info("성능 메트릭이 삭제되었습니다.")
    
    def enable_optimization(self) -> None:
        """최적화 기능 활성화"""
        self._optimization_enabled = True
        logger.info("성능 최적화가 활성화되었습니다.")
    
    def disable_optimization(self) -> None:
        """최적화 기능 비활성화"""
        self._optimization_enabled = False
        logger.info("성능 최적화가 비활성화되었습니다.")
    
    def is_optimization_enabled(self) -> bool:
        """최적화 활성화 상태 확인"""
        return self._optimization_enabled


# 전역 성능 최적화기 인스턴스
global_optimizer = PerformanceOptimizer()


def optimize_performance(operation_name: str):
    """성능 최적화 데코레이터 (전역 최적화기 사용)"""
    return global_optimizer.performance_monitor(operation_name)


def cache_result(cache_key: str = None, ttl: int = 3600):
    """결과 캐싱 데코레이터 (전역 최적화기 사용)"""
    return global_optimizer.cached_operation(cache_key, ttl)


# 사용 예시 및 테스트 함수
def test_performance_optimizer():
    """성능 최적화기 테스트"""
    optimizer = PerformanceOptimizer()
    
    # 테스트 데이터 생성
    test_data = pd.DataFrame({
        'id': range(10000),
        'name': [f'item_{i}' for i in range(10000)],
        'value': np.random.randn(10000),
        'category': np.random.choice(['A', 'B', 'C'], 10000)
    })
    
    print(f"원본 데이터 메모리: {test_data.memory_usage(deep=True).sum() / 1024 / 1024:.1f}MB")
    
    # 메모리 최적화 테스트
    optimized_data = optimizer.optimize_dataframe_memory(test_data)
    print(f"최적화된 데이터 메모리: {optimized_data.memory_usage(deep=True).sum() / 1024 / 1024:.1f}MB")
    
    # 성능 모니터링 테스트
    @optimizer.performance_monitor("test_operation")
    def test_operation(data):
        return data.groupby('category').agg({'value': ['mean', 'std', 'count']})
    
    # 캐시 테스트
    @optimizer.cached_operation("test_cache")
    def cached_operation(data):
        time.sleep(1)  # 시뮬레이션
        return data.describe()
    
    # 테스트 실행
    result1 = test_operation(optimized_data)
    print("그룹화 연산 완료")
    
    # 첫 번째 캐시 호출 (느림)
    start_time = time.time()
    cached_result1 = cached_operation(optimized_data)
    first_call_time = time.time() - start_time
    
    # 두 번째 캐시 호출 (빠름)
    start_time = time.time()
    cached_result2 = cached_operation(optimized_data)
    second_call_time = time.time() - start_time
    
    print(f"첫 번째 호출: {first_call_time:.2f}초")
    print(f"두 번째 호출: {second_call_time:.2f}초")
    print(f"캐시 효과: {first_call_time / second_call_time:.1f}배 빠름")
    
    # 성능 보고서
    report = optimizer.get_performance_report()
    print("\n성능 보고서:")
    for key, value in report.items():
        print(f"  {key}: {value}")
    
    return optimizer


if __name__ == "__main__":
    test_performance_optimizer()