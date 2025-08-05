"""
애플리케이션 설정 관리
Application Configuration Management

Task 13.1: 환경 변수 설정 구현
- 환경별 설정 관리
- 설정 검증
- 기본값 설정
"""

import os
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from config.logging_config import get_logger

logger = get_logger(__name__)


class Environment(Enum):
    """환경 타입"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """데이터베이스 설정"""
    type: str = "sqlite"
    path: str = "data/lab_dashboard.db"
    backup_enabled: bool = True
    connection_timeout: int = 30


@dataclass
class SecurityConfig:
    """보안 설정"""
    auto_delete_hours: int = 24
    max_concurrent_users: int = 20
    enable_file_validation: bool = True
    virus_scan_enabled: bool = False
    max_file_size_mb: int = 50
    allowed_extensions: list = field(default_factory=lambda: ['xlsx', 'xls'])


@dataclass
class PerformanceConfig:
    """성능 설정"""
    memory_limit: str = "1g"
    cpu_limit: float = 1.0
    cache_enabled: bool = True
    cache_ttl: int = 3600
    max_data_points: int = 1000
    chunk_size: int = 10000


@dataclass
class LoggingConfig:
    """로깅 설정"""
    level: str = "INFO"
    format: str = "json"
    file_path: str = "logs/app.log"
    max_size: str = "10MB"
    backup_count: int = 5


@dataclass
class MonitoringConfig:
    """모니터링 설정"""
    enabled: bool = False
    metrics_port: int = 9090
    health_check_interval: int = 30
    prometheus_enabled: bool = False


@dataclass
class NotificationConfig:
    """알림 설정"""
    enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    admin_email: str = ""


@dataclass
class FileProcessingConfig:
    """파일 처리 설정"""
    upload_timeout: int = 300
    supported_formats: list = field(default_factory=lambda: ['xlsx', 'xls'])
    upload_path: str = "uploads/pending"
    processed_path: str = "data/processed"
    standards_path: str = "data/standards"
    auto_cleanup_enabled: bool = True


class AppConfig:
    """애플리케이션 설정 관리 클래스"""
    
    def __init__(self, env_file: Optional[str] = None):
        """설정 초기화"""
        self.env_file = env_file or ".env"
        self.environment = self._get_environment()
        
        # 환경 변수 로드
        self._load_env_file()
        
        # 설정 객체 초기화
        self.database = self._init_database_config()
        self.security = self._init_security_config()
        self.performance = self._init_performance_config()
        self.logging = self._init_logging_config()
        self.monitoring = self._init_monitoring_config()
        self.notification = self._init_notification_config()
        self.file_processing = self._init_file_processing_config()
        
        # 설정 검증
        self._validate_config()
        
        logger.info(f"애플리케이션 설정 로드 완료 (환경: {self.environment.value})")
    
    def _get_environment(self) -> Environment:
        """현재 환경 확인"""
        env_str = os.getenv('ENVIRONMENT', 'development').lower()
        try:
            return Environment(env_str)
        except ValueError:
            logger.warning(f"알 수 없는 환경: {env_str}, development로 설정")
            return Environment.DEVELOPMENT
    
    def _load_env_file(self) -> None:
        """환경 변수 파일 로드"""
        if Path(self.env_file).exists():
            try:
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            
                            # 환경 변수가 이미 설정되어 있지 않은 경우에만 설정
                            if key not in os.environ:
                                os.environ[key] = value
                
                logger.info(f"환경 변수 파일 로드 완료: {self.env_file}")
            except Exception as e:
                logger.error(f"환경 변수 파일 로드 실패: {e}")
        else:
            logger.warning(f"환경 변수 파일이 없습니다: {self.env_file}")
    
    def _init_database_config(self) -> DatabaseConfig:
        """데이터베이스 설정 초기화"""
        return DatabaseConfig(
            type=os.getenv('DB_TYPE', 'sqlite'),
            path=os.getenv('DB_PATH', 'data/lab_dashboard.db'),
            backup_enabled=self._get_bool_env('DB_BACKUP_ENABLED', True),
            connection_timeout=int(os.getenv('DB_CONNECTION_TIMEOUT', '30'))
        )
    
    def _init_security_config(self) -> SecurityConfig:
        """보안 설정 초기화"""
        return SecurityConfig(
            auto_delete_hours=int(os.getenv('AUTO_DELETE_HOURS', '24')),
            max_concurrent_users=int(os.getenv('MAX_CONCURRENT_USERS', '20')),
            enable_file_validation=self._get_bool_env('ENABLE_FILE_VALIDATION', True),
            virus_scan_enabled=self._get_bool_env('VIRUS_SCAN_ENABLED', False),
            max_file_size_mb=int(os.getenv('MAX_FILE_SIZE', '50')),
            allowed_extensions=os.getenv('SUPPORTED_FORMATS', 'xlsx,xls').split(',')
        )
    
    def _init_performance_config(self) -> PerformanceConfig:
        """성능 설정 초기화"""
        return PerformanceConfig(
            memory_limit=os.getenv('MEMORY_LIMIT', '1g'),
            cpu_limit=float(os.getenv('CPU_LIMIT', '1.0')),
            cache_enabled=self._get_bool_env('CACHE_ENABLED', True),
            cache_ttl=int(os.getenv('CACHE_TTL', '3600')),
            max_data_points=int(os.getenv('MAX_DATA_POINTS', '1000')),
            chunk_size=int(os.getenv('CHUNK_SIZE', '10000'))
        )
    
    def _init_logging_config(self) -> LoggingConfig:
        """로깅 설정 초기화"""
        return LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            format=os.getenv('LOG_FORMAT', 'json'),
            file_path=os.getenv('LOG_FILE_PATH', 'logs/app.log'),
            max_size=os.getenv('LOG_MAX_SIZE', '10MB'),
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', '5'))
        )
    
    def _init_monitoring_config(self) -> MonitoringConfig:
        """모니터링 설정 초기화"""
        return MonitoringConfig(
            enabled=self._get_bool_env('MONITORING_ENABLED', False),
            metrics_port=int(os.getenv('METRICS_PORT', '9090')),
            health_check_interval=int(os.getenv('HEALTH_CHECK_INTERVAL', '30')),
            prometheus_enabled=self._get_bool_env('PROMETHEUS_ENABLED', False)
        )
    
    def _init_notification_config(self) -> NotificationConfig:
        """알림 설정 초기화"""
        return NotificationConfig(
            enabled=self._get_bool_env('NOTIFICATION_ENABLED', False),
            smtp_host=os.getenv('SMTP_HOST', ''),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            smtp_user=os.getenv('SMTP_USER', ''),
            smtp_password=os.getenv('SMTP_PASSWORD', ''),
            admin_email=os.getenv('ADMIN_EMAIL', '')
        )
    
    def _init_file_processing_config(self) -> FileProcessingConfig:
        """파일 처리 설정 초기화"""
        return FileProcessingConfig(
            upload_timeout=int(os.getenv('UPLOAD_TIMEOUT', '300')),
            supported_formats=os.getenv('SUPPORTED_FORMATS', 'xlsx,xls').split(','),
            upload_path=os.getenv('UPLOAD_PATH', 'uploads/pending'),
            processed_path=os.getenv('PROCESSED_PATH', 'data/processed'),
            standards_path=os.getenv('STANDARDS_PATH', 'data/standards'),
            auto_cleanup_enabled=self._get_bool_env('AUTO_CLEANUP_ENABLED', True)
        )
    
    def _get_bool_env(self, key: str, default: bool = False) -> bool:
        """환경 변수를 불린 값으로 변환"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _validate_config(self) -> None:
        """설정 검증"""
        errors = []
        
        # 필수 디렉토리 확인
        required_dirs = [
            self.file_processing.upload_path,
            self.file_processing.processed_path,
            self.file_processing.standards_path,
            Path(self.logging.file_path).parent
        ]
        
        for directory in required_dirs:
            dir_path = Path(directory)
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"디렉토리 생성: {directory}")
                except Exception as e:
                    errors.append(f"디렉토리 생성 실패: {directory} - {e}")
        
        # 파일 크기 제한 검증
        if self.security.max_file_size_mb <= 0:
            errors.append("최대 파일 크기는 0보다 커야 합니다")
        
        # 동시 사용자 수 검증
        if self.security.max_concurrent_users <= 0:
            errors.append("최대 동시 사용자 수는 0보다 커야 합니다")
        
        # 캐시 TTL 검증
        if self.performance.cache_ttl <= 0:
            errors.append("캐시 TTL은 0보다 커야 합니다")
        
        # 알림 설정 검증
        if self.notification.enabled:
            if not self.notification.smtp_host:
                errors.append("알림이 활성화된 경우 SMTP 호스트가 필요합니다")
            if not self.notification.admin_email:
                errors.append("알림이 활성화된 경우 관리자 이메일이 필요합니다")
        
        if errors:
            error_msg = "설정 검증 실패:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("설정 검증 완료")
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """Streamlit 설정 반환"""
        return {
            'server.port': int(os.getenv('APP_PORT', '8501')),
            'server.address': os.getenv('APP_HOST', '0.0.0.0'),
            'server.headless': True,
            'browser.gatherUsageStats': False,
            'server.enableCORS': False,
            'server.enableXsrfProtection': False,
            'server.maxUploadSize': self.security.max_file_size_mb,
            'server.maxMessageSize': self.security.max_file_size_mb,
            'global.developmentMode': self.environment == Environment.DEVELOPMENT
        }
    
    def get_docker_config(self) -> Dict[str, Any]:
        """Docker 설정 반환"""
        return {
            'image_name': 'lab-dashboard',
            'container_name': 'lab-analysis-dashboard',
            'ports': [f"{os.getenv('APP_PORT', '8501')}:8501"],
            'environment': self._get_docker_env_vars(),
            'volumes': self._get_docker_volumes(),
            'restart_policy': 'unless-stopped',
            'healthcheck': {
                'test': ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8501/_stcore/health', timeout=5)"],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3,
                'start_period': '40s'
            }
        }
    
    def _get_docker_env_vars(self) -> Dict[str, str]:
        """Docker 환경 변수 반환"""
        return {
            'ENVIRONMENT': self.environment.value,
            'LOG_LEVEL': self.logging.level,
            'LOG_FORMAT': self.logging.format,
            'MAX_FILE_SIZE': str(self.security.max_file_size_mb),
            'AUTO_DELETE_HOURS': str(self.security.auto_delete_hours),
            'MAX_CONCURRENT_USERS': str(self.security.max_concurrent_users),
            'MEMORY_LIMIT': self.performance.memory_limit,
            'CPU_LIMIT': str(self.performance.cpu_limit),
            'CACHE_ENABLED': str(self.performance.cache_enabled).lower(),
            'MONITORING_ENABLED': str(self.monitoring.enabled).lower()
        }
    
    def _get_docker_volumes(self) -> List[str]:
        """Docker 볼륨 설정 반환"""
        return [
            './uploads:/app/uploads',
            './data:/app/data',
            './reports:/app/reports',
            './logs:/app/logs',
            './config:/app/config'
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환"""
        return {
            'environment': self.environment.value,
            'database': self.database.__dict__,
            'security': self.security.__dict__,
            'performance': self.performance.__dict__,
            'logging': self.logging.__dict__,
            'monitoring': self.monitoring.__dict__,
            'notification': self.notification.__dict__,
            'file_processing': self.file_processing.__dict__
        }
    
    def save_config(self, file_path: str) -> None:
        """설정을 파일로 저장"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"설정 파일 저장 완료: {file_path}")
        except Exception as e:
            logger.error(f"설정 파일 저장 실패: {e}")
            raise
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """설정 업데이트"""
        for section, values in updates.items():
            if hasattr(self, section):
                config_obj = getattr(self, section)
                for key, value in values.items():
                    if hasattr(config_obj, key):
                        setattr(config_obj, key, value)
                        logger.info(f"설정 업데이트: {section}.{key} = {value}")
                    else:
                        logger.warning(f"알 수 없는 설정 키: {section}.{key}")
            else:
                logger.warning(f"알 수 없는 설정 섹션: {section}")
        
        # 설정 재검증
        self._validate_config()


# 전역 설정 인스턴스
_config_instance = None


def get_config() -> AppConfig:
    """전역 설정 인스턴스 반환"""
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig()
    return _config_instance


def reload_config(env_file: Optional[str] = None) -> AppConfig:
    """설정 재로드"""
    global _config_instance
    _config_instance = AppConfig(env_file)
    return _config_instance


# 편의 함수들
def is_development() -> bool:
    """개발 환경 여부 확인"""
    return get_config().environment == Environment.DEVELOPMENT


def is_production() -> bool:
    """프로덕션 환경 여부 확인"""
    return get_config().environment == Environment.PRODUCTION


def get_upload_path() -> str:
    """업로드 경로 반환"""
    return get_config().file_processing.upload_path


def get_max_file_size() -> int:
    """최대 파일 크기 반환 (MB)"""
    return get_config().security.max_file_size_mb


def is_monitoring_enabled() -> bool:
    """모니터링 활성화 여부 확인"""
    return get_config().monitoring.enabled