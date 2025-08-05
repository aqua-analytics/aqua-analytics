"""
파일 처리 유틸리티
파일 업로드, 검증, 처리 관련 공통 함수들
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple, List
import pandas as pd


def validate_excel_file(file_path: str) -> Tuple[bool, str]:
    """
    엑셀 파일 유효성 검사
    
    Args:
        file_path: 검사할 파일 경로
        
    Returns:
        (is_valid, error_message): 유효성 여부와 에러 메시지
    """
    try:
        # 파일 존재 확인
        if not os.path.exists(file_path):
            return False, "파일이 존재하지 않습니다."
        
        # 파일 확장자 확인
        if not file_path.lower().endswith(('.xlsx', '.xls')):
            return False, "엑셀 파일(.xlsx, .xls)만 지원됩니다."
        
        # 파일 크기 확인 (100MB 제한)
        file_size = os.path.getsize(file_path)
        if file_size > 100 * 1024 * 1024:  # 100MB
            return False, "파일 크기가 100MB를 초과합니다."
        
        # 파일 읽기 테스트
        try:
            pd.read_excel(file_path, nrows=1)
        except Exception as e:
            return False, f"파일을 읽을 수 없습니다: {str(e)}"
        
        return True, ""
        
    except Exception as e:
        return False, f"파일 검증 중 오류 발생: {str(e)}"


def clean_filename(filename: str) -> str:
    """
    파일명에서 특수문자 제거 및 정리
    
    Args:
        filename: 원본 파일명
        
    Returns:
        정리된 파일명
    """
    # 특수문자 제거 (한글, 영문, 숫자, 하이픈, 언더스코어만 허용)
    cleaned = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # 연속된 언더스코어 제거
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # 앞뒤 언더스코어 제거
    cleaned = cleaned.strip('_')
    
    return cleaned


def ensure_directory(directory_path: str) -> None:
    """
    디렉토리가 존재하지 않으면 생성
    
    Args:
        directory_path: 생성할 디렉토리 경로
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def get_file_info(file_path: str) -> dict:
    """
    파일 정보 추출
    
    Args:
        file_path: 파일 경로
        
    Returns:
        파일 정보 딕셔너리
    """
    try:
        stat = os.stat(file_path)
        return {
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified': stat.st_mtime,
            'extension': os.path.splitext(file_path)[1].lower()
        }
    except Exception:
        return {}


def list_excel_files(directory: str) -> List[str]:
    """
    디렉토리에서 엑셀 파일 목록 반환
    
    Args:
        directory: 검색할 디렉토리 경로
        
    Returns:
        엑셀 파일 경로 리스트
    """
    excel_files = []
    
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.lower().endswith(('.xlsx', '.xls')):
                excel_files.append(os.path.join(directory, file))
    
    return sorted(excel_files)


def extract_project_name_from_filename(filename: str) -> Optional[str]:
    """
    파일명에서 프로젝트명 추출
    
    Args:
        filename: 파일명
        
    Returns:
        추출된 프로젝트명 또는 None
    """
    # 파일명에서 확장자 제거
    name_without_ext = os.path.splitext(filename)[0]
    
    # _PJT 패턴으로 프로젝트명 추출
    match = re.search(r'(.+?)_PJT', name_without_ext)
    if match:
        return match.group(1).strip()
    
    # _PJT 패턴이 없으면 전체 파일명을 프로젝트명으로 사용
    return name_without_ext.strip()


def create_backup_filename(original_path: str) -> str:
    """
    백업 파일명 생성
    
    Args:
        original_path: 원본 파일 경로
        
    Returns:
        백업 파일 경로
    """
    from datetime import datetime
    
    directory = os.path.dirname(original_path)
    filename = os.path.basename(original_path)
    name, ext = os.path.splitext(filename)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{name}_backup_{timestamp}{ext}"
    
    return os.path.join(directory, backup_filename)