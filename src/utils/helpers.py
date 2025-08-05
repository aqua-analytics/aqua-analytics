"""
공통 헬퍼 함수들
자주 사용되는 유틸리티 함수들을 제공합니다.
"""

import math
from datetime import datetime, timedelta
from typing import Any, Optional, Union, List, Dict


def safe_divide(numerator: Union[int, float], denominator: Union[int, float], 
                default: float = 0.0) -> float:
    """
    안전한 나눗셈 (0으로 나누기 방지)
    
    Args:
        numerator: 분자
        denominator: 분모
        default: 분모가 0일 때 반환할 기본값
        
    Returns:
        나눗셈 결과 또는 기본값
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def calculate_percentage(part: Union[int, float], total: Union[int, float], 
                        decimal_places: int = 1) -> float:
    """
    백분율 계산
    
    Args:
        part: 부분값
        total: 전체값
        decimal_places: 소수점 자릿수
        
    Returns:
        백분율 (0-100)
    """
    if total == 0:
        return 0.0
    
    percentage = (part / total) * 100
    return round(percentage, decimal_places)


def format_number(value: Union[int, float], decimal_places: int = 2, 
                 use_comma: bool = True) -> str:
    """
    숫자 포맷팅
    
    Args:
        value: 포맷팅할 숫자
        decimal_places: 소수점 자릿수
        use_comma: 천단위 구분자 사용 여부
        
    Returns:
        포맷팅된 숫자 문자열
    """
    try:
        if math.isnan(value) or math.isinf(value):
            return "N/A"
        
        if use_comma:
            return f"{value:,.{decimal_places}f}"
        else:
            return f"{value:.{decimal_places}f}"
    except (TypeError, ValueError):
        return str(value)


def format_date(date_value: Optional[datetime], format_string: str = "%Y-%m-%d %H:%M") -> str:
    """
    날짜 포맷팅
    
    Args:
        date_value: 포맷팅할 날짜
        format_string: 날짜 형식 문자열
        
    Returns:
        포맷팅된 날짜 문자열
    """
    if date_value is None:
        return "N/A"
    
    try:
        return date_value.strftime(format_string)
    except (AttributeError, ValueError):
        return str(date_value)


def format_file_size(size_bytes: int) -> str:
    """
    파일 크기 포맷팅
    
    Args:
        size_bytes: 바이트 단위 파일 크기
        
    Returns:
        읽기 쉬운 파일 크기 문자열
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    텍스트 길이 제한
    
    Args:
        text: 원본 텍스트
        max_length: 최대 길이
        suffix: 생략 표시 문자
        
    Returns:
        제한된 길이의 텍스트
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def get_color_by_status(status: str) -> str:
    """
    상태에 따른 색상 반환
    
    Args:
        status: 상태 문자열
        
    Returns:
        CSS 색상 코드
    """
    color_map = {
        '적합': '#10b981',      # 초록색
        '부적합': '#ef4444',    # 빨간색
        '대기': '#f59e0b',      # 주황색
        '진행중': '#3b82f6',    # 파란색
        '완료': '#10b981',      # 초록색
        '오류': '#ef4444',      # 빨간색
        '-': '#6b7280'          # 회색
    }
    
    return color_map.get(status, '#6b7280')


def get_icon_by_status(status: str) -> str:
    """
    상태에 따른 아이콘 반환
    
    Args:
        status: 상태 문자열
        
    Returns:
        이모지 아이콘
    """
    icon_map = {
        '적합': '✅',
        '부적합': '❌',
        '대기': '⏳',
        '진행중': '🔄',
        '완료': '✅',
        '오류': '⚠️',
        '-': '➖'
    }
    
    return icon_map.get(status, '❓')


def create_summary_stats(data: List[Dict[str, Any]], 
                        group_by: str, 
                        count_field: str = None) -> Dict[str, int]:
    """
    데이터 요약 통계 생성
    
    Args:
        data: 분석할 데이터 리스트
        group_by: 그룹화할 필드명
        count_field: 카운트할 필드명 (None이면 행 개수)
        
    Returns:
        그룹별 통계 딕셔너리
    """
    stats = {}
    
    for item in data:
        if group_by in item:
            key = item[group_by]
            if key not in stats:
                stats[key] = 0
            
            if count_field and count_field in item:
                stats[key] += item[count_field]
            else:
                stats[key] += 1
    
    return stats


def filter_data_by_criteria(data: List[Dict[str, Any]], 
                           criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    조건에 따른 데이터 필터링
    
    Args:
        data: 필터링할 데이터 리스트
        criteria: 필터링 조건 딕셔너리
        
    Returns:
        필터링된 데이터 리스트
    """
    filtered_data = []
    
    for item in data:
        match = True
        
        for key, value in criteria.items():
            if key not in item:
                match = False
                break
            
            if isinstance(value, list):
                if item[key] not in value:
                    match = False
                    break
            else:
                if item[key] != value:
                    match = False
                    break
        
        if match:
            filtered_data.append(item)
    
    return filtered_data


def generate_unique_id(prefix: str = "", length: int = 8) -> str:
    """
    고유 ID 생성
    
    Args:
        prefix: ID 접두사
        length: ID 길이
        
    Returns:
        고유 ID 문자열
    """
    import random
    import string
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    if prefix:
        return f"{prefix}_{timestamp}_{random_chars}"
    else:
        return f"{timestamp}_{random_chars}"


def deep_merge_dict(dict1: Dict, dict2: Dict) -> Dict:
    """
    딕셔너리 깊은 병합
    
    Args:
        dict1: 첫 번째 딕셔너리
        dict2: 두 번째 딕셔너리
        
    Returns:
        병합된 딕셔너리
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dict(result[key], value)
        else:
            result[key] = value
    
    return result


def time_ago(date_time: datetime) -> str:
    """
    상대적 시간 표시 (예: "2시간 전")
    
    Args:
        date_time: 기준 날짜시간
        
    Returns:
        상대적 시간 문자열
    """
    now = datetime.now()
    diff = now - date_time
    
    if diff.days > 0:
        return f"{diff.days}일 전"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}시간 전"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}분 전"
    else:
        return "방금 전"