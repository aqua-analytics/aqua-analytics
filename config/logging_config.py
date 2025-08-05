"""
로깅 시스템 설정
Logging System Configuration

Task 13.1: 로깅 시스템 구현
- 구조화된 로깅 설정
- 로그 레벨 관리
- 파일 로테이션
- JSON 형식 로깅
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import traceback


class JSONFormatter(logging.Formatter):
    """JSON 형식 로그 포매터"""
    
    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 JSON 형식으로 포맷"""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': os.getpid(),
            'thread_id': record.thread
        }
        
        # 예외 정보 추가
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # 추가 컨텍스트 정보
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        
        if hasattr(record, 'file_name'):
            log_entry['file_name'] = record.file_name
        
        if hasattr(record, 'processing_time'):
            log_entry['processing_time'] = record.processing_time
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """컬러 콘솔 출력용 포매터"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # 청록색
        'INFO': '\033[32m',       # 녹색
        'WARNING': '\033[33m',    # 노란색
        'ERROR': '\033[31m',      # 빨간색
        'CRITICAL': '\033[35m',   # 자주색
        'RESET': '\033[0m'        # 리셋
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """컬러가 적용된 로그 메시지 포맷"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # 기본 포맷 적용
        formatted = super().format(record)
        
        # 컬러 적용
        return f"{color}{formatted}{reset}"


class LoggingConfig:
    """로깅 시스템 설정 클래스"""
    
    def __init__(self):
        """로깅 설정 초기화"""
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.log_format = os.getenv('LOG_FORMAT', 'json').lower()
        self.log_file_path = os.getenv('LOG_FILE_PATH', 'logs/app.log')
        self.log_max_size = self._parse_size(os.getenv('LOG_MAX_SIZE', '10MB'))
        self.log_backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        
        # 로그 디렉토리 생성
        self._ensure_log_directory()
        
        # 로깅 설정 적용
        self._configure_logging()
    
    def _parse_size(self, size_str: str) -> int:
        """크기 문자열을 바이트로 변환"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def _ensure_log_directory(self) -> None:
        """로그 디렉토리 생성"""
        log_dir = Path(self.log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def _configure_logging(self) -> None:
        """로깅 시스템 설정"""
        # 루트 로거 설정
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level))
        
        # 기존 핸들러 제거
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 파일 핸들러 설정
        self._setup_file_handler(root_logger)
        
        # 콘솔 핸들러 설정
        self._setup_console_handler(root_logger)
        
        # 특정 로거 설정
        self._setup_specific_loggers()
    
    def _setup_file_handler(self, logger: logging.Logger) -> None:
        """파일 핸들러 설정"""
        file_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_file_path,
            maxBytes=self.log_max_size,
            backupCount=self.log_backup_count,
            encoding='utf-8'
        )
        
        if self.log_format == 'json':
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
        
        logger.addHandler(file_handler)
    
    def _setup_console_handler(self, logger: logging.Logger) -> None:
        """콘솔 핸들러 설정"""
        console_handler = logging.StreamHandler(sys.stdout)
        
        # 개발 환경에서는 컬러 포매터 사용
        if os.getenv('APP_DEBUG', 'false').lower() == 'true':
            console_handler.setFormatter(ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
        else:
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
        
        logger.addHandler(console_handler)
    
    def _setup_specific_loggers(self) -> None:
        """특정 로거 설정"""
        # Streamlit 로거 설정
        streamlit_logger = logging.getLogger('streamlit')
        streamlit_logger.setLevel(logging.WARNING)
        
        # Pandas 로거 설정
        pandas_logger = logging.getLogger('pandas')
        pandas_logger.setLevel(logging.WARNING)
        
        # Plotly 로거 설정
        plotly_logger = logging.getLogger('plotly')
        plotly_logger.setLevel(logging.WARNING)
        
        # 애플리케이션 로거 설정
        app_logger = logging.getLogger('lab_dashboard')
        app_logger.setLevel(getattr(logging, self.log_level))


class ContextLogger:
    """컨텍스트 정보가 포함된 로거"""
    
    def __init__(self, name: str):
        """컨텍스트 로거 초기화"""
        self.logger = logging.getLogger(name)
        self.context = {}
    
    def set_context(self, **kwargs) -> None:
        """컨텍스트 정보 설정"""
        self.context.update(kwargs)
    
    def clear_context(self) -> None:
        """컨텍스트 정보 초기화"""
        self.context.clear()
    
    def _log_with_context(self, level: int, message: str, *args, **kwargs) -> None:
        """컨텍스트 정보와 함께 로그 기록"""
        # 컨텍스트 정보를 extra로 전달
        extra = kwargs.get('extra', {})
        extra.update(self.context)
        kwargs['extra'] = extra
        
        self.logger.log(level, message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """디버그 로그"""
        self._log_with_context(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """정보 로그"""
        self._log_with_context(logging.INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """경고 로그"""
        self._log_with_context(logging.WARNING, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """에러 로그"""
        self._log_with_context(logging.ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """치명적 에러 로그"""
        self._log_with_context(logging.CRITICAL, message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs) -> None:
        """예외 로그"""
        kwargs['exc_info'] = True
        self._log_with_context(logging.ERROR, message, *args, **kwargs)


class PerformanceLogger:
    """성능 측정 로거"""
    
    def __init__(self, logger: ContextLogger):
        """성능 로거 초기화"""
        self.logger = logger
        self.start_time = None
    
    def start_timer(self, operation: str) -> None:
        """타이머 시작"""
        self.start_time = datetime.now()
        self.logger.info(f"시작: {operation}")
    
    def end_timer(self, operation: str) -> float:
        """타이머 종료 및 소요 시간 반환"""
        if self.start_time is None:
            self.logger.warning(f"타이머가 시작되지 않음: {operation}")
            return 0.0
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.logger.info(
            f"완료: {operation}",
            extra={'processing_time': duration}
        )
        
        self.start_time = None
        return duration
    
    def log_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """성능 메트릭 로그"""
        self.logger.info("성능 메트릭", extra=metrics)


# 전역 로깅 설정 초기화
def initialize_logging() -> None:
    """전역 로깅 시스템 초기화"""
    LoggingConfig()


# 편의 함수들
def get_logger(name: str) -> ContextLogger:
    """컨텍스트 로거 생성"""
    return ContextLogger(name)


def get_performance_logger(name: str) -> PerformanceLogger:
    """성능 로거 생성"""
    context_logger = get_logger(name)
    return PerformanceLogger(context_logger)


# 로깅 데코레이터
def log_function_call(logger: Optional[ContextLogger] = None):
    """함수 호출 로깅 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            logger.info(f"함수 호출: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"함수 완료: {func.__name__}")
                return result
            except Exception as e:
                logger.exception(f"함수 오류: {func.__name__} - {str(e)}")
                raise
        
        return wrapper
    return decorator


def log_performance(logger: Optional[ContextLogger] = None):
    """성능 측정 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            perf_logger = PerformanceLogger(logger)
            perf_logger.start_timer(func.__name__)
            
            try:
                result = func(*args, **kwargs)
                perf_logger.end_timer(func.__name__)
                return result
            except Exception as e:
                perf_logger.end_timer(func.__name__)
                logger.exception(f"성능 측정 중 오류: {func.__name__} - {str(e)}")
                raise
        
        return wrapper
    return decorator


# 모듈 초기화 시 로깅 설정
if __name__ != "__main__":
    initialize_logging()