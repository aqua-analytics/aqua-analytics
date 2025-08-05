"""
데이터 검증 유틸리티
데이터 유효성 검사 및 검증 관련 함수들

Task 11.1 & 11.2 통합: 파일 검증 및 데이터 처리 에러 핸들링
"""

import re
from typing import Any, List, Dict, Optional, Tuple
import pandas as pd
from datetime import datetime
from pathlib import Path

# 새로운 에러 핸들링 시스템 임포트
try:
    from .file_validator import FileValidator, ValidationResult as FileValidationResult, ValidationLevel
    from .error_handler import DataProcessingErrorHandler, ProcessingResult, UserFriendlyErrorFormatter
except ImportError:
    # 상대 임포트 실패 시 절대 임포트 시도
    try:
        from file_validator import FileValidator, ValidationResult as FileValidationResult, ValidationLevel
        from error_handler import DataProcessingErrorHandler, ProcessingResult, UserFriendlyErrorFormatter
    except ImportError:
        # 임포트 실패 시 기본 클래스 정의
        FileValidator = None
        DataProcessingErrorHandler = None


def validate_test_result_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    시험 결과 데이터 유효성 검사
    
    Args:
        data: 검증할 데이터 딕셔너리
        
    Returns:
        (is_valid, error_messages): 유효성 여부와 에러 메시지 리스트
    """
    errors = []
    
    # 필수 필드 검사
    required_fields = ['시료명', '시험항목', '결과(성적서)', '기준대비 초과여부']
    for field in required_fields:
        if field not in data or pd.isna(data[field]) or str(data[field]).strip() == '':
            errors.append(f"필수 필드 '{field}'가 누락되었습니다.")
    
    # 시료명 검증
    if '시료명' in data and data['시료명']:
        sample_name = str(data['시료명']).strip()
        if len(sample_name) < 1:
            errors.append("시료명이 너무 짧습니다.")
        elif len(sample_name) > 100:
            errors.append("시료명이 너무 깁니다. (최대 100자)")
    
    # 시험항목 검증
    if '시험항목' in data and data['시험항목']:
        test_item = str(data['시험항목']).strip()
        if len(test_item) < 1:
            errors.append("시험항목이 너무 짧습니다.")
        elif len(test_item) > 200:
            errors.append("시험항목이 너무 깁니다. (최대 200자)")
    
    # 판정 결과 검증
    if '기준대비 초과여부' in data and data['기준대비 초과여부']:
        judgment = str(data['기준대비 초과여부']).strip()
        valid_judgments = ['적합', '부적합', '-']
        if judgment not in valid_judgments:
            errors.append(f"판정 결과는 {valid_judgments} 중 하나여야 합니다.")
    
    # 시험자 정보 검증
    if '시험자' in data and data['시험자']:
        tester = str(data['시험자']).strip()
        if len(tester) > 50:
            errors.append("시험자명이 너무 깁니다. (최대 50자)")
    
    return len(errors) == 0, errors


def validate_numeric_result(result_value: Any) -> Tuple[bool, Optional[float]]:
    """
    수치 결과값 검증 및 변환
    
    Args:
        result_value: 검증할 결과값
        
    Returns:
        (is_valid, converted_value): 유효성 여부와 변환된 값
    """
    if pd.isna(result_value):
        return False, None
    
    # 문자열인 경우 "불검출" 등의 특수값 처리
    if isinstance(result_value, str):
        result_str = result_value.strip().lower()
        if result_str in ['불검출', 'nd', 'not detected', '<']:
            return True, None  # 불검출은 유효하지만 수치값은 None
        
        # 숫자 추출 시도
        try:
            # 숫자가 아닌 문자 제거 후 변환
            numeric_str = re.sub(r'[^\d.-]', '', result_str)
            if numeric_str:
                return True, float(numeric_str)
        except ValueError:
            pass
    
    # 숫자 타입인 경우
    try:
        float_value = float(result_value)
        # 합리적인 범위 검사 (음수 불가, 너무 큰 값 불가)
        if float_value < 0:
            return False, None
        if float_value > 1e10:  # 100억 이상은 비현실적
            return False, None
        return True, float_value
    except (ValueError, TypeError):
        return False, None


def validate_date_format(date_value: Any) -> Tuple[bool, Optional[datetime]]:
    """
    날짜 형식 검증 및 변환
    
    Args:
        date_value: 검증할 날짜값
        
    Returns:
        (is_valid, converted_date): 유효성 여부와 변환된 날짜
    """
    if pd.isna(date_value):
        return False, None
    
    # 이미 datetime 객체인 경우
    if isinstance(date_value, datetime):
        return True, date_value
    
    # 문자열인 경우 파싱 시도
    if isinstance(date_value, str):
        date_str = date_value.strip()
        
        # 다양한 날짜 형식 시도
        date_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M',
            '%Y/%m/%d',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%m/%d/%Y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                # 합리적인 날짜 범위 검사 (1900년 이후, 현재로부터 10년 이내)
                current_year = datetime.now().year
                if 1900 <= parsed_date.year <= current_year + 10:
                    return True, parsed_date
            except ValueError:
                continue
    
    return False, None


def validate_standard_criteria(criteria: str) -> Tuple[bool, str]:
    """
    기준값 형식 검증
    
    Args:
        criteria: 기준값 문자열
        
    Returns:
        (is_valid, error_message): 유효성 여부와 에러 메시지
    """
    if not criteria or pd.isna(criteria):
        return False, "기준값이 비어있습니다."
    
    criteria_str = str(criteria).strip()
    
    if len(criteria_str) < 1:
        return False, "기준값이 너무 짧습니다."
    
    if len(criteria_str) > 200:
        return False, "기준값이 너무 깁니다. (최대 200자)"
    
    # 기본적인 기준값 패턴 검사
    # 예: "1.0 mg/L 이하", "6.5-8.5", "불검출"
    valid_patterns = [
        r'\d+\.?\d*\s*\w+/?\w*\s*(이하|이상|미만|초과)',  # "1.0 mg/L 이하"
        r'\d+\.?\d*\s*-\s*\d+\.?\d*',                    # "6.5-8.5"
        r'불검출|nd|not\s+detected',                      # "불검출"
        r'\d+\.?\d*\s*\w+/?\w*',                         # "1.0 mg/L"
    ]
    
    for pattern in valid_patterns:
        if re.search(pattern, criteria_str, re.IGNORECASE):
            return True, ""
    
    # 패턴에 맞지 않아도 경고만 표시 (너무 엄격하지 않게)
    return True, f"기준값 형식을 확인해주세요: {criteria_str}"


def validate_excel_columns(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
    """
    엑셀 파일의 필수 컬럼 존재 여부 검증
    
    Args:
        df: 검증할 DataFrame
        required_columns: 필수 컬럼 리스트
        
    Returns:
        (is_valid, missing_columns): 유효성 여부와 누락된 컬럼 리스트
    """
    missing_columns = []
    
    for col in required_columns:
        if col not in df.columns:
            missing_columns.append(col)
    
    return len(missing_columns) == 0, missing_columns


def validate_data_completeness(df: pd.DataFrame, critical_columns: List[str]) -> Dict[str, int]:
    """
    데이터 완성도 검증
    
    Args:
        df: 검증할 DataFrame
        critical_columns: 중요 컬럼 리스트
        
    Returns:
        컬럼별 누락 데이터 개수
    """
    missing_data = {}
    
    for col in critical_columns:
        if col in df.columns:
            missing_count = df[col].isna().sum()
            missing_data[col] = missing_count
    
    return missing_data


def sanitize_input(input_value: str, max_length: int = 1000) -> str:
    """
    사용자 입력값 정리 및 보안 처리
    
    Args:
        input_value: 입력값
        max_length: 최대 길이
        
    Returns:
        정리된 입력값
    """
    if not input_value:
        return ""
    
    # 문자열로 변환
    sanitized = str(input_value).strip()
    
    # 길이 제한
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # 위험한 문자 제거 (기본적인 XSS 방지)
    dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'script']
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized


class IntegratedValidator:
    """통합 검증 시스템 (파일 + 데이터 처리)"""
    
    def __init__(self, validation_level: str = "standard"):
        """
        통합 검증기 초기화
        
        Args:
            validation_level: 검증 수준 ("basic", "standard", "strict")
        """
        # 파일 검증기 초기화
        if FileValidator:
            level_mapping = {
                "basic": ValidationLevel.BASIC,
                "standard": ValidationLevel.STANDARD,
                "strict": ValidationLevel.STRICT
            }
            self.file_validator = FileValidator.create_lab_validator()
            self.file_validator.validation_level = level_mapping.get(validation_level, ValidationLevel.STANDARD)
        else:
            self.file_validator = None
        
        # 데이터 처리 에러 핸들러 초기화
        if DataProcessingErrorHandler:
            self.error_handler = DataProcessingErrorHandler()
        else:
            self.error_handler = None
    
    def validate_uploaded_file(self, file_path: str, uploaded_file=None) -> Dict[str, Any]:
        """
        업로드된 파일 전체 검증 (Task 11.1 + 11.2)
        
        Args:
            file_path: 파일 경로
            uploaded_file: Streamlit 업로드 파일 객체
            
        Returns:
            통합 검증 결과
        """
        result = {
            'success': False,
            'file_validation': None,
            'data_processing': None,
            'formatted_messages': None,
            'can_proceed': False
        }
        
        try:
            # 1. 파일 검증
            if self.file_validator:
                file_result = self.file_validator.validate_file(file_path, uploaded_file)
                result['file_validation'] = file_result
                
                if not file_result.is_valid:
                    result['formatted_messages'] = self._format_file_validation_messages(file_result)
                    return result
            
            # 2. 데이터 처리 검증 (파일이 유효한 경우)
            if self.error_handler:
                try:
                    # 파일 읽기
                    if uploaded_file:
                        df = pd.read_excel(uploaded_file)
                    else:
                        df = pd.read_excel(file_path)
                    
                    # 컬럼 매핑 검증
                    mapping_result = self.error_handler.handle_column_mapping_errors(df)
                    
                    if mapping_result.success:
                        # 데이터 타입 변환
                        column_mapping = mapping_result.metadata.get('mapped_columns', {})
                        type_result = self.error_handler.handle_data_type_errors(df, column_mapping)
                        
                        if type_result.success or not type_result.has_critical_errors():
                            # 기준값 누락 처리
                            standards_result = self.error_handler.handle_missing_standards_errors(
                                type_result.data if type_result.data is not None else df
                            )
                            
                            result['data_processing'] = standards_result
                            result['success'] = standards_result.success
                            result['can_proceed'] = not standards_result.has_critical_errors()
                        else:
                            result['data_processing'] = type_result
                            result['success'] = False
                            result['can_proceed'] = False
                    else:
                        result['data_processing'] = mapping_result
                        result['success'] = False
                        result['can_proceed'] = False
                    
                    # 사용자 친화적 메시지 포맷팅
                    if result['data_processing'] and UserFriendlyErrorFormatter:
                        result['formatted_messages'] = UserFriendlyErrorFormatter.format_processing_result(
                            result['data_processing']
                        )
                
                except Exception as e:
                    result['formatted_messages'] = {
                        'success': False,
                        'issues': {
                            'critical': [{
                                'message': f"데이터 처리 중 오류 발생: {str(e)}",
                                'details': "파일 형식이나 내용을 확인해주세요.",
                                'suggested_fix': "Excel 파일을 다시 저장하거나 다른 파일을 시도해보세요."
                            }]
                        }
                    }
            
        except Exception as e:
            result['formatted_messages'] = {
                'success': False,
                'issues': {
                    'critical': [{
                        'message': f"검증 중 시스템 오류: {str(e)}",
                        'details': "예상치 못한 오류가 발생했습니다.",
                        'suggested_fix': "시스템 관리자에게 문의하세요."
                    }]
                }
            }
        
        return result
    
    def _format_file_validation_messages(self, file_result: 'FileValidationResult') -> Dict[str, Any]:
        """파일 검증 결과를 사용자 친화적 메시지로 변환"""
        formatted = {
            'success': file_result.is_valid,
            'summary': {
                'total_rows': 0,
                'processed_rows': 0,
                'success_rate': 0 if not file_result.is_valid else 100
            },
            'issues': {
                'critical': [],
                'errors': [],
                'warnings': [],
                'info': []
            },
            'suggestions': [],
            'next_steps': []
        }
        
        # 에러 메시지 분류
        for error in file_result.errors:
            formatted['issues']['errors'].append({
                'message': error,
                'details': "파일 검증 실패",
                'suggested_fix': self._get_file_error_solution(error)
            })
        
        for warning in file_result.warnings:
            formatted['issues']['warnings'].append({
                'message': warning,
                'details': "파일 검증 경고",
                'suggested_fix': "확인 후 계속 진행할 수 있습니다."
            })
        
        # 파일 정보
        if file_result.file_size:
            size_mb = file_result.file_size / (1024 * 1024)
            formatted['issues']['info'].append({
                'message': f"파일 크기: {size_mb:.1f} MB",
                'details': "파일 크기 정보"
            })
        
        # 제안사항 및 다음 단계
        if not file_result.is_valid:
            formatted['suggestions'] = ["파일 형식과 내용을 확인해주세요."]
            formatted['next_steps'] = [
                "1. 오류를 수정하세요.",
                "2. 파일을 다시 업로드하세요."
            ]
        else:
            formatted['next_steps'] = ["파일 검증이 완료되었습니다. 데이터 분석을 시작합니다."]
        
        return formatted
    
    def _get_file_error_solution(self, error_message: str) -> str:
        """파일 에러에 대한 해결 방안"""
        if "지원되지 않는 파일 형식" in error_message:
            return "Excel 파일(.xlsx, .xls) 또는 CSV 파일(.csv)을 사용해주세요."
        elif "파일이 너무 큽니다" in error_message:
            return "파일 크기를 50MB 이하로 줄여주세요."
        elif "파일이 손상되었습니다" in error_message:
            return "파일을 Excel에서 다시 저장해보세요."
        elif "필수 컬럼이 누락" in error_message:
            return "'시료명', '시험항목' 컬럼이 있는지 확인해주세요."
        else:
            return "파일을 확인하고 다시 시도해주세요."
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """검증 시스템 상태 요약"""
        return {
            'file_validator_available': self.file_validator is not None,
            'error_handler_available': self.error_handler is not None,
            'validation_level': self.file_validator.validation_level.value if self.file_validator else "unavailable",
            'supported_formats': list(FileValidator.SUPPORTED_EXTENSIONS.keys()) if FileValidator else [],
            'max_file_size_mb': FileValidator.MAX_FILE_SIZE / (1024 * 1024) if FileValidator else 0
        }