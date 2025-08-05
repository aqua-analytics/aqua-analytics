"""
애플리케이션 메트릭 수집 및 노출
Application Metrics Collection and Exposure

Task 13.1: 모니터링 설정 구현
- Prometheus 메트릭 수집
- 커스텀 메트릭 정의
- 성능 지표 추적
"""

import time
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
import psutil
import os

from config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class MetricValue:
    """메트릭 값"""
    value: float
    timestamp: datetime
    labels: Dict[str, str] = None


class MetricsRegistry:
    """메트릭 레지스트리"""
    
    def __init__(self):
        """메트릭 레지스트리 초기화"""
        self._metrics = {}
        self._counters = defaultdict(float)
        self._gauges = defaultdict(float)
        self._histograms = defaultdict(list)
        self._summaries = defaultdict(deque)
        self._lock = threading.Lock()
        
        # 시스템 메트릭 수집 시작
        self._start_system_metrics_collection()
    
    def counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None) -> None:
        """카운터 메트릭 증가"""
        with self._lock:
            key = self._make_key(name, labels)
            self._counters[key] += value
            logger.debug(f"카운터 증가: {name} = {self._counters[key]}")
    
    def gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """게이지 메트릭 설정"""
        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] = value
            logger.debug(f"게이지 설정: {name} = {value}")
    
    def histogram(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """히스토그램 메트릭 추가"""
        with self._lock:
            key = self._make_key(name, labels)
            self._histograms[key].append(value)
            
            # 최대 1000개 값만 유지
            if len(self._histograms[key]) > 1000:
                self._histograms[key] = self._histograms[key][-1000:]
            
            logger.debug(f"히스토그램 추가: {name} = {value}")
    
    def summary(self, name: str, value: float, labels: Dict[str, str] = None, max_age: int = 600) -> None:
        """서머리 메트릭 추가"""
        with self._lock:
            key = self._make_key(name, labels)
            now = datetime.now()
            
            # 새 값 추가
            self._summaries[key].append(MetricValue(value, now, labels))
            
            # 오래된 값 제거
            cutoff_time = now - timedelta(seconds=max_age)
            while self._summaries[key] and self._summaries[key][0].timestamp < cutoff_time:
                self._summaries[key].popleft()
            
            logger.debug(f"서머리 추가: {name} = {value}")
    
    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """메트릭 키 생성"""
        if not labels:
            return name
        
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def _start_system_metrics_collection(self) -> None:
        """시스템 메트릭 수집 시작"""
        def collect_system_metrics():
            while True:
                try:
                    # CPU 사용률
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.gauge('system_cpu_usage_percent', cpu_percent)
                    
                    # 메모리 사용률
                    memory = psutil.virtual_memory()
                    self.gauge('system_memory_usage_percent', memory.percent)
                    self.gauge('system_memory_used_bytes', memory.used)
                    self.gauge('system_memory_available_bytes', memory.available)
                    
                    # 디스크 사용률
                    disk = psutil.disk_usage('/')
                    disk_percent = (disk.used / disk.total) * 100
                    self.gauge('system_disk_usage_percent', disk_percent)
                    self.gauge('system_disk_used_bytes', disk.used)
                    self.gauge('system_disk_free_bytes', disk.free)
                    
                    # 프로세스 메트릭
                    process = psutil.Process()
                    self.gauge('process_memory_bytes', process.memory_info().rss)
                    self.gauge('process_cpu_percent', process.cpu_percent())
                    self.gauge('process_threads', process.num_threads())
                    
                    # 파일 시스템 메트릭
                    self._collect_filesystem_metrics()
                    
                except Exception as e:
                    logger.error(f"시스템 메트릭 수집 오류: {e}")
                
                time.sleep(30)  # 30초마다 수집
        
        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()
        logger.info("시스템 메트릭 수집 시작")
    
    def _collect_filesystem_metrics(self) -> None:
        """파일 시스템 메트릭 수집"""
        try:
            # 업로드 파일 수
            upload_dir = 'uploads/pending'
            if os.path.exists(upload_dir):
                upload_count = len([f for f in os.listdir(upload_dir) 
                                  if f.endswith(('.xlsx', '.xls'))])
                self.gauge('pending_files_count', upload_count)
            
            # 처리된 파일 수
            processed_dir = 'data/processed'
            if os.path.exists(processed_dir):
                processed_count = len(os.listdir(processed_dir))
                self.gauge('processed_files_count', processed_count)
            
            # 보고서 수
            reports_dir = 'reports'
            if os.path.exists(reports_dir):
                reports_count = len([f for f in os.listdir(reports_dir) 
                                   if f.endswith(('.html', '.pdf'))])
                self.gauge('reports_count', reports_count)
            
            # 로그 파일 크기
            log_file = 'logs/app.log'
            if os.path.exists(log_file):
                log_size = os.path.getsize(log_file)
                self.gauge('log_file_size_bytes', log_size)
                
        except Exception as e:
            logger.error(f"파일 시스템 메트릭 수집 오류: {e}")
    
    def get_prometheus_metrics(self) -> str:
        """Prometheus 형식으로 메트릭 반환"""
        lines = []
        
        with self._lock:
            # 카운터 메트릭
            for key, value in self._counters.items():
                name, labels = self._parse_key(key)
                lines.append(f"# TYPE {name} counter")
                if labels:
                    lines.append(f"{name}{{{labels}}} {value}")
                else:
                    lines.append(f"{name} {value}")
            
            # 게이지 메트릭
            for key, value in self._gauges.items():
                name, labels = self._parse_key(key)
                lines.append(f"# TYPE {name} gauge")
                if labels:
                    lines.append(f"{name}{{{labels}}} {value}")
                else:
                    lines.append(f"{name} {value}")
            
            # 히스토그램 메트릭
            for key, values in self._histograms.items():
                if not values:
                    continue
                
                name, labels = self._parse_key(key)
                lines.append(f"# TYPE {name} histogram")
                
                # 히스토그램 버킷
                buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
                for bucket in buckets:
                    count = sum(1 for v in values if v <= bucket)
                    bucket_labels = f'le="{bucket}"'
                    if labels:
                        bucket_labels = f"{labels},{bucket_labels}"
                    lines.append(f"{name}_bucket{{{bucket_labels}}} {count}")
                
                # 총 개수와 합계
                total_count = len(values)
                total_sum = sum(values)
                if labels:
                    lines.append(f"{name}_count{{{labels}}} {total_count}")
                    lines.append(f"{name}_sum{{{labels}}} {total_sum}")
                else:
                    lines.append(f"{name}_count {total_count}")
                    lines.append(f"{name}_sum {total_sum}")
            
            # 서머리 메트릭
            for key, values in self._summaries.items():
                if not values:
                    continue
                
                name, labels = self._parse_key(key)
                lines.append(f"# TYPE {name} summary")
                
                # 분위수 계산
                sorted_values = sorted([v.value for v in values])
                quantiles = [0.5, 0.9, 0.95, 0.99]
                
                for quantile in quantiles:
                    index = int(len(sorted_values) * quantile)
                    if index >= len(sorted_values):
                        index = len(sorted_values) - 1
                    value = sorted_values[index] if sorted_values else 0
                    
                    quantile_labels = f'quantile="{quantile}"'
                    if labels:
                        quantile_labels = f"{labels},{quantile_labels}"
                    lines.append(f"{name}{{{quantile_labels}}} {value}")
                
                # 총 개수와 합계
                total_count = len(values)
                total_sum = sum(v.value for v in values)
                if labels:
                    lines.append(f"{name}_count{{{labels}}} {total_count}")
                    lines.append(f"{name}_sum{{{labels}}} {total_sum}")
                else:
                    lines.append(f"{name}_count {total_count}")
                    lines.append(f"{name}_sum {total_sum}")
        
        return "\n".join(lines)
    
    def _parse_key(self, key: str) -> tuple:
        """메트릭 키 파싱"""
        if '{' in key:
            name, labels_part = key.split('{', 1)
            labels = labels_part.rstrip('}')
            return name, labels
        return key, None
    
    def get_metrics_dict(self) -> Dict[str, Any]:
        """메트릭을 딕셔너리 형태로 반환"""
        with self._lock:
            return {
                'counters': dict(self._counters),
                'gauges': dict(self._gauges),
                'histograms': {k: list(v) for k, v in self._histograms.items()},
                'summaries': {k: [{'value': v.value, 'timestamp': v.timestamp.isoformat()} 
                                for v in list(v)] for k, v in self._summaries.items()}
            }
    
    def reset_metrics(self) -> None:
        """모든 메트릭 초기화"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._summaries.clear()
            logger.info("모든 메트릭 초기화 완료")


class ApplicationMetrics:
    """애플리케이션 특화 메트릭"""
    
    def __init__(self, registry: MetricsRegistry):
        """애플리케이션 메트릭 초기화"""
        self.registry = registry
        self._request_start_times = {}
        
    def record_file_upload(self, file_size: int, file_type: str, success: bool = True) -> None:
        """파일 업로드 메트릭 기록"""
        labels = {'file_type': file_type, 'status': 'success' if success else 'failure'}
        
        self.registry.counter('file_uploads_total', labels=labels)
        if success:
            self.registry.histogram('file_upload_size_bytes', file_size, labels={'file_type': file_type})
        else:
            self.registry.counter('file_upload_failures_total', labels={'file_type': file_type})
    
    def record_data_processing(self, processing_time: float, row_count: int, success: bool = True) -> None:
        """데이터 처리 메트릭 기록"""
        labels = {'status': 'success' if success else 'failure'}
        
        self.registry.counter('data_processing_total', labels=labels)
        if success:
            self.registry.histogram('data_processing_duration_seconds', processing_time)
            self.registry.histogram('data_processing_rows', row_count)
        else:
            self.registry.counter('data_processing_failures_total')
    
    def record_non_conforming_items(self, total_items: int, non_conforming_items: int) -> None:
        """부적합 항목 메트릭 기록"""
        non_conforming_rate = (non_conforming_items / total_items * 100) if total_items > 0 else 0
        
        self.registry.gauge('total_test_items', total_items)
        self.registry.gauge('non_conforming_items', non_conforming_items)
        self.registry.gauge('non_conforming_rate', non_conforming_rate)
    
    def record_report_generation(self, generation_time: float, report_type: str, success: bool = True) -> None:
        """보고서 생성 메트릭 기록"""
        labels = {'report_type': report_type, 'status': 'success' if success else 'failure'}
        
        self.registry.counter('report_generation_total', labels=labels)
        if success:
            self.registry.histogram('report_generation_duration_seconds', generation_time, 
                                   labels={'report_type': report_type})
        else:
            self.registry.counter('report_generation_failures_total', labels={'report_type': report_type})
    
    def record_user_session(self, session_duration: float, page_views: int) -> None:
        """사용자 세션 메트릭 기록"""
        self.registry.counter('user_sessions_total')
        self.registry.histogram('session_duration_seconds', session_duration)
        self.registry.histogram('session_page_views', page_views)
    
    def record_error(self, error_type: str, component: str) -> None:
        """에러 메트릭 기록"""
        labels = {'error_type': error_type, 'component': component}
        self.registry.counter('application_errors_total', labels=labels)
    
    def start_request_timer(self, request_id: str) -> None:
        """요청 타이머 시작"""
        self._request_start_times[request_id] = time.time()
    
    def end_request_timer(self, request_id: str, endpoint: str, status_code: int) -> None:
        """요청 타이머 종료"""
        if request_id in self._request_start_times:
            duration = time.time() - self._request_start_times[request_id]
            del self._request_start_times[request_id]
            
            labels = {
                'endpoint': endpoint,
                'status': str(status_code),
                'method': 'GET'  # Streamlit은 주로 GET 요청
            }
            
            self.registry.counter('http_requests_total', labels=labels)
            self.registry.histogram('http_request_duration_seconds', duration, labels=labels)
    
    def record_concurrent_users(self, count: int) -> None:
        """동시 사용자 수 기록"""
        self.registry.gauge('concurrent_users', count)
    
    def record_cache_hit_rate(self, hit_rate: float) -> None:
        """캐시 히트율 기록"""
        self.registry.gauge('cache_hit_rate', hit_rate)


# 전역 메트릭 인스턴스
_metrics_registry = None
_app_metrics = None


def get_metrics_registry() -> MetricsRegistry:
    """메트릭 레지스트리 반환"""
    global _metrics_registry
    if _metrics_registry is None:
        _metrics_registry = MetricsRegistry()
    return _metrics_registry


def get_app_metrics() -> ApplicationMetrics:
    """애플리케이션 메트릭 반환"""
    global _app_metrics
    if _app_metrics is None:
        _app_metrics = ApplicationMetrics(get_metrics_registry())
    return _app_metrics


# 데코레이터
def track_execution_time(metric_name: str, labels: Dict[str, str] = None):
    """실행 시간 추적 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                final_labels = labels.copy() if labels else {}
                final_labels['function'] = func.__name__
                final_labels['status'] = 'success' if success else 'failure'
                
                get_metrics_registry().histogram(metric_name, duration, final_labels)
        
        return wrapper
    return decorator


def count_calls(metric_name: str, labels: Dict[str, str] = None):
    """함수 호출 횟수 추적 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            final_labels = labels.copy() if labels else {}
            final_labels['function'] = func.__name__
            
            try:
                result = func(*args, **kwargs)
                final_labels['status'] = 'success'
                return result
            except Exception as e:
                final_labels['status'] = 'failure'
                raise
            finally:
                get_metrics_registry().counter(metric_name, labels=final_labels)
        
        return wrapper
    return decorator