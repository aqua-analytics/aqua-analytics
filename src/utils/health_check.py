"""
헬스체크 및 모니터링 유틸리티
Health Check and Monitoring Utilities

Task 13.1: 모니터링 설정 구현
- 애플리케이션 상태 확인
- 시스템 리소스 모니터링
- 성능 메트릭 수집
"""

import os
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

from config.logging_config import get_logger
from src.utils.metrics import get_metrics_registry, get_app_metrics

logger = get_logger(__name__)
metrics_registry = get_metrics_registry()
app_metrics = get_app_metrics()


class HealthChecker:
    """애플리케이션 헬스체크 클래스"""
    
    def __init__(self):
        """헬스체커 초기화"""
        self.start_time = datetime.now()
        self.last_check_time = None
        self.check_history = []
        self.max_history = 100
    
    def get_system_health(self) -> Dict[str, Any]:
        """시스템 전체 상태 확인"""
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'status': 'healthy',
                'uptime': self._get_uptime(),
                'system': self._get_system_metrics(),
                'application': self._get_application_metrics(),
                'storage': self._get_storage_metrics(),
                'checks': self._run_health_checks()
            }
            
            # 전체 상태 결정
            if any(check['status'] == 'unhealthy' for check in health_status['checks']):
                health_status['status'] = 'unhealthy'
                metrics_registry.gauge('health_status', 0)  # 0 = unhealthy
            elif any(check['status'] == 'warning' for check in health_status['checks']):
                health_status['status'] = 'warning'
                metrics_registry.gauge('health_status', 0.5)  # 0.5 = warning
            else:
                metrics_registry.gauge('health_status', 1)  # 1 = healthy
            
            # 헬스체크 메트릭 업데이트
            metrics_registry.counter('health_checks_total')
            
            # 히스토리 업데이트
            self._update_history(health_status)
            
            return health_status
            
        except Exception as e:
            logger.exception("헬스체크 실행 중 오류 발생")
            metrics_registry.counter('health_check_errors_total')
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    def _get_uptime(self) -> Dict[str, Any]:
        """애플리케이션 업타임 정보"""
        uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'start_time': self.start_time.isoformat(),
            'uptime_seconds': uptime_seconds,
            'uptime_formatted': self._format_duration(uptime_seconds)
        }
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """시스템 리소스 메트릭"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'usage_percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'usage_percent': (disk.used / disk.total) * 100
                }
            }
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 오류: {e}")
            return {'error': str(e)}
    
    def _get_application_metrics(self) -> Dict[str, Any]:
        """애플리케이션 메트릭"""
        try:
            process = psutil.Process()
            
            return {
                'process_id': process.pid,
                'memory_usage': process.memory_info().rss,
                'cpu_usage': process.cpu_percent(),
                'threads': process.num_threads(),
                'open_files': len(process.open_files()),
                'connections': len(process.connections())
            }
        except Exception as e:
            logger.error(f"애플리케이션 메트릭 수집 오류: {e}")
            return {'error': str(e)}
    
    def _get_storage_metrics(self) -> Dict[str, Any]:
        """스토리지 메트릭"""
        try:
            storage_info = {}
            
            # 주요 디렉토리 크기 확인
            directories = ['uploads', 'data', 'reports', 'logs']
            
            for directory in directories:
                if Path(directory).exists():
                    size = self._get_directory_size(directory)
                    file_count = self._get_file_count(directory)
                    
                    storage_info[directory] = {
                        'size_bytes': size,
                        'size_formatted': self._format_bytes(size),
                        'file_count': file_count
                    }
            
            return storage_info
            
        except Exception as e:
            logger.error(f"스토리지 메트릭 수집 오류: {e}")
            return {'error': str(e)}
    
    def _run_health_checks(self) -> List[Dict[str, Any]]:
        """개별 헬스체크 실행"""
        checks = []
        
        # 1. 메모리 사용량 체크
        checks.append(self._check_memory_usage())
        
        # 2. 디스크 사용량 체크
        checks.append(self._check_disk_usage())
        
        # 3. 필수 디렉토리 체크
        checks.append(self._check_required_directories())
        
        # 4. 로그 파일 체크
        checks.append(self._check_log_files())
        
        # 5. 환경 변수 체크
        checks.append(self._check_environment_variables())
        
        return checks
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """메모리 사용량 체크"""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            if usage_percent > 90:
                status = 'unhealthy'
                message = f"메모리 사용량이 매우 높습니다: {usage_percent}%"
            elif usage_percent > 80:
                status = 'warning'
                message = f"메모리 사용량이 높습니다: {usage_percent}%"
            else:
                status = 'healthy'
                message = f"메모리 사용량 정상: {usage_percent}%"
            
            return {
                'name': 'memory_usage',
                'status': status,
                'message': message,
                'value': usage_percent
            }
            
        except Exception as e:
            return {
                'name': 'memory_usage',
                'status': 'error',
                'message': f"메모리 체크 오류: {e}"
            }
    
    def _check_disk_usage(self) -> Dict[str, Any]:
        """디스크 사용량 체크"""
        try:
            disk = psutil.disk_usage('/')
            usage_percent = (disk.used / disk.total) * 100
            
            if usage_percent > 95:
                status = 'unhealthy'
                message = f"디스크 사용량이 매우 높습니다: {usage_percent:.1f}%"
            elif usage_percent > 85:
                status = 'warning'
                message = f"디스크 사용량이 높습니다: {usage_percent:.1f}%"
            else:
                status = 'healthy'
                message = f"디스크 사용량 정상: {usage_percent:.1f}%"
            
            return {
                'name': 'disk_usage',
                'status': status,
                'message': message,
                'value': usage_percent
            }
            
        except Exception as e:
            return {
                'name': 'disk_usage',
                'status': 'error',
                'message': f"디스크 체크 오류: {e}"
            }
    
    def _check_required_directories(self) -> Dict[str, Any]:
        """필수 디렉토리 체크"""
        try:
            required_dirs = ['uploads/pending', 'data', 'reports', 'logs']
            missing_dirs = []
            
            for directory in required_dirs:
                if not Path(directory).exists():
                    missing_dirs.append(directory)
            
            if missing_dirs:
                status = 'unhealthy'
                message = f"필수 디렉토리가 없습니다: {', '.join(missing_dirs)}"
            else:
                status = 'healthy'
                message = "모든 필수 디렉토리가 존재합니다"
            
            return {
                'name': 'required_directories',
                'status': status,
                'message': message,
                'missing_directories': missing_dirs
            }
            
        except Exception as e:
            return {
                'name': 'required_directories',
                'status': 'error',
                'message': f"디렉토리 체크 오류: {e}"
            }
    
    def _check_log_files(self) -> Dict[str, Any]:
        """로그 파일 체크"""
        try:
            log_file_path = os.getenv('LOG_FILE_PATH', 'logs/app.log')
            
            if not Path(log_file_path).exists():
                status = 'warning'
                message = f"로그 파일이 없습니다: {log_file_path}"
            else:
                # 로그 파일 크기 체크
                file_size = Path(log_file_path).stat().st_size
                max_size = 100 * 1024 * 1024  # 100MB
                
                if file_size > max_size:
                    status = 'warning'
                    message = f"로그 파일이 큽니다: {self._format_bytes(file_size)}"
                else:
                    status = 'healthy'
                    message = f"로그 파일 정상: {self._format_bytes(file_size)}"
            
            return {
                'name': 'log_files',
                'status': status,
                'message': message
            }
            
        except Exception as e:
            return {
                'name': 'log_files',
                'status': 'error',
                'message': f"로그 파일 체크 오류: {e}"
            }
    
    def _check_environment_variables(self) -> Dict[str, Any]:
        """환경 변수 체크"""
        try:
            required_vars = ['LOG_LEVEL', 'LOG_FORMAT']
            missing_vars = []
            
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                status = 'warning'
                message = f"환경 변수가 설정되지 않음: {', '.join(missing_vars)}"
            else:
                status = 'healthy'
                message = "모든 필수 환경 변수가 설정됨"
            
            return {
                'name': 'environment_variables',
                'status': status,
                'message': message,
                'missing_variables': missing_vars
            }
            
        except Exception as e:
            return {
                'name': 'environment_variables',
                'status': 'error',
                'message': f"환경 변수 체크 오류: {e}"
            }
    
    def _update_history(self, health_status: Dict[str, Any]) -> None:
        """헬스체크 히스토리 업데이트"""
        self.check_history.append({
            'timestamp': health_status['timestamp'],
            'status': health_status['status']
        })
        
        # 히스토리 크기 제한
        if len(self.check_history) > self.max_history:
            self.check_history = self.check_history[-self.max_history:]
        
        self.last_check_time = datetime.now()
    
    def get_health_history(self) -> List[Dict[str, Any]]:
        """헬스체크 히스토리 반환"""
        return self.check_history
    
    def _get_directory_size(self, directory: str) -> int:
        """디렉토리 크기 계산"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    pass
        return total_size
    
    def _get_file_count(self, directory: str) -> int:
        """디렉토리 내 파일 개수 계산"""
        file_count = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            file_count += len(filenames)
        return file_count
    
    def _format_bytes(self, bytes_value: int) -> str:
        """바이트를 읽기 쉬운 형태로 변환"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def _format_duration(self, seconds: float) -> str:
        """초를 읽기 쉬운 형태로 변환"""
        duration = timedelta(seconds=seconds)
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days:
            parts.append(f"{days}일")
        if hours:
            parts.append(f"{hours}시간")
        if minutes:
            parts.append(f"{minutes}분")
        if seconds or not parts:
            parts.append(f"{seconds}초")
        
        return " ".join(parts)


class MetricsCollector:
    """메트릭 수집기"""
    
    def __init__(self):
        """메트릭 수집기 초기화"""
        self.metrics = {}
        self.collection_interval = 60  # 60초
        self.last_collection_time = None
    
    def collect_metrics(self) -> Dict[str, Any]:
        """메트릭 수집"""
        try:
            current_time = datetime.now()
            
            metrics = {
                'timestamp': current_time.isoformat(),
                'system': self._collect_system_metrics(),
                'application': self._collect_application_metrics(),
                'custom': self._collect_custom_metrics()
            }
            
            self.metrics = metrics
            self.last_collection_time = current_time
            
            return metrics
            
        except Exception as e:
            logger.exception("메트릭 수집 중 오류 발생")
            return {'error': str(e)}
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """시스템 메트릭 수집"""
        return {
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
    
    def _collect_application_metrics(self) -> Dict[str, Any]:
        """애플리케이션 메트릭 수집"""
        try:
            process = psutil.Process()
            return {
                'memory_usage': process.memory_info().rss,
                'cpu_usage': process.cpu_percent(),
                'threads': process.num_threads(),
                'open_files': len(process.open_files())
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _collect_custom_metrics(self) -> Dict[str, Any]:
        """커스텀 메트릭 수집"""
        return {
            'uploaded_files_count': self._count_uploaded_files(),
            'processed_files_count': self._count_processed_files(),
            'reports_count': self._count_reports(),
            'log_file_size': self._get_log_file_size()
        }
    
    def _count_uploaded_files(self) -> int:
        """업로드된 파일 개수"""
        try:
            upload_dir = Path('uploads/pending')
            if upload_dir.exists():
                return len(list(upload_dir.glob('*.xlsx'))) + len(list(upload_dir.glob('*.xls')))
            return 0
        except Exception:
            return 0
    
    def _count_processed_files(self) -> int:
        """처리된 파일 개수"""
        try:
            processed_dir = Path('data/processed')
            if processed_dir.exists():
                return len(list(processed_dir.glob('*')))
            return 0
        except Exception:
            return 0
    
    def _count_reports(self) -> int:
        """생성된 보고서 개수"""
        try:
            reports_dir = Path('reports')
            if reports_dir.exists():
                return len(list(reports_dir.glob('*.html'))) + len(list(reports_dir.glob('*.pdf')))
            return 0
        except Exception:
            return 0
    
    def _get_log_file_size(self) -> int:
        """로그 파일 크기"""
        try:
            log_file_path = Path(os.getenv('LOG_FILE_PATH', 'logs/app.log'))
            if log_file_path.exists():
                return log_file_path.stat().st_size
            return 0
        except Exception:
            return 0
    
    def get_latest_metrics(self) -> Dict[str, Any]:
        """최신 메트릭 반환"""
        return self.metrics


# 전역 인스턴스
health_checker = HealthChecker()
metrics_collector = MetricsCollector()


def get_health_status() -> Dict[str, Any]:
    """헬스 상태 반환"""
    return health_checker.get_system_health()


def get_metrics() -> Dict[str, Any]:
    """메트릭 반환"""
    return metrics_collector.collect_metrics()