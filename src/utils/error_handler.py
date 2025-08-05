"""
데이터 처리 에러 핸들링 시스템
Data Processing Error Handling System

Task 11.2: 데이터 처리 에러 핸들링 구현
- 컬럼 매핑 실패 처리 구현
- 데이터 타입 오류 처리 구현
- 기준값 누락 처리 구현
- 사용자 친화적 에러 메시지 구현
"""

import logging
import traceback
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
from datetime import datetime
import re

# 로깅 설정
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """에러 심각도"""
    CRITICAL = "critical"    # 처리 중단 필요
    ERROR = "error"         # 심각한 오류
    WARNING = "warning"     # 경고
    INFO = "info"          # 정보


class ErrorCategory(Enum):
    """에러 카테고리"""
    COLUMN_MAPPING = "column_mapping"      # 컬럼 매핑 오류
    DATA_TYPE = "data_type"               # 데이터 타입 오류
    MISSING_STANDARD = "missing_standard"  # 기준값 누락
    DATA_VALIDATION = "data_validation"    # 데이터 검증 오류
    PROCESSING = "processing"             # 처리 오류
    SYSTEM = "system"                     # 시스템 오류


@dataclass
class ProcessingError:
    """처리 에러 정보"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: str = ""
    row_index: Optional[int] = None
    column_name: Optional[str] = None
    original_value: Any = None
    suggested_fix: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'category': self.category.value,
            'severity': self.severity.value,
            'message': self.message,
            'details': self.details,
            'row_index': self.row_index,
            'column_name': self.column_name,
            'original_value': str(self.original_value) if self.original_value is not None else None,
            'suggested_fix': self.suggested_fix,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ProcessingResult:
    """처리 결과"""
    success: bool
    data: Optional[Any] = None
    errors: List[ProcessingError] = field(default_factory=list)
    warnings: List[ProcessingError] = field(default_factory=list)
    processed_rows: int = 0
    total_rows: int = 0
    metadata: Dict = field(default_factory=dict)
    
    def add_error(self, error: ProcessingError) -> None:
        """에러 추가"""
        if error.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.ERROR]:
            self.errors.append(error)
        else:
            self.warnings.append(error)
    
    def has_critical_errors(self) -> bool:
        """치명적 에러 존재 여부"""
        return any(error.severity == ErrorSeverity.CRITICAL for error in self.errors)
    
    def get_error_summary(self) -> Dict[str, int]:
        """에러 요약 통계"""
        summary = {
            'critical': 0,
            'error': 0,
            'warning': 0,
            'info': 0
        }
        
        all_issues = self.errors + self.warnings
        for issue in all_issues:
            summary[issue.severity.value] += 1
        
        return summary


class DataProcessingErrorHandler:
    """데이터 처리 에러 핸들러"""
    
    # 컬럼 매핑 테이블 (실제 컬럼명 -> 표준 컬럼명)
    COLUMN_MAPPING_TABLE = {
        # 기본 매핑
        '시료명': 'sample_name',
        '분석번호': 'analysis_number',
        '시험항목': 'test_item',
        '시험단위': 'test_unit',
        '결과(성적서)': 'result_report',
        '시험자': 'tester',
        '기준': 'standard_criteria',
        '기준 텍스트': 'standard_criteria',
        '입력일시': 'input_datetime',
        
        # 줄바꿈이 포함된 컬럼명 매핑
        '기준대비 초과여부\n(성적서)': 'standard_excess',
        '기준대비 초과여부 (성적서)': 'standard_excess',
        '시험결과\n표시자리수': 'result_display_digits',
        '시험결과 표시자리수': 'result_display_digits',
        '자리수\n처리방식': 'text_digits',
        '텍스트 자리수': 'text_digits',
        '시험기기\n(RDMS)': 'test_equipment',
        '시험기기 (RDMS)': 'test_equipment',
        '성적서\n출력여부': 'report_output',
        '성적서 출력여부': 'report_output',
        
        # 유사한 컬럼명들
        '샘플명': 'sample_name',
        '시료이름': 'sample_name',
        '검체명': 'sample_name',
        '시험결과': 'result_report',
        '측정결과': 'result_report',
        '분석결과': 'result_report',
        '판정': 'standard_excess',
        '판정결과': 'standard_excess',
        '적합성': 'standard_excess',
        '기준값': 'standard_criteria',
        '규격': 'standard_criteria',
        '한계값': 'standard_criteria',
    }
    
    # 필수 컬럼 목록
    REQUIRED_COLUMNS = ['sample_name', 'test_item', 'result_report']
    
    # 권장 컬럼 목록
    RECOMMENDED_COLUMNS = ['tester', 'standard_excess', 'standard_criteria']
    
    def __init__(self):
        """에러 핸들러 초기화"""
        self.error_log = []
        self.column_mapping_cache = {}
        
    def handle_column_mapping_errors(self, df: pd.DataFrame) -> ProcessingResult:
        """컬럼 매핑 에러 처리 (요구사항: 성공 기준 1)"""
        result = ProcessingResult(success=True, total_rows=len(df))
        
        try:
            # 1. 컬럼명 정규화 (공백, 특수문자 제거)
            normalized_columns = {}
            for col in df.columns:
                normalized = self._normalize_column_name(col)
                normalized_columns[col] = normalized
            
            # 2. 컬럼 매핑 시도
            mapped_columns = {}
            unmapped_columns = []
            
            for original_col, normalized_col in normalized_columns.items():
                # 직접 매핑 시도
                if original_col in self.COLUMN_MAPPING_TABLE:
                    mapped_columns[original_col] = self.COLUMN_MAPPING_TABLE[original_col]
                # 정규화된 이름으로 매핑 시도
                elif normalized_col in self.COLUMN_MAPPING_TABLE:
                    mapped_columns[original_col] = self.COLUMN_MAPPING_TABLE[normalized_col]
                # 유사도 기반 매핑 시도
                else:
                    similar_mapping = self._find_similar_column_mapping(original_col)
                    if similar_mapping:
                        mapped_columns[original_col] = similar_mapping
                        result.add_error(ProcessingError(
                            category=ErrorCategory.COLUMN_MAPPING,
                            severity=ErrorSeverity.WARNING,
                            message=f"컬럼명 유사도 매핑: '{original_col}' -> '{similar_mapping}'",
                            details="컬럼명이 정확히 일치하지 않아 유사도 기반으로 매핑했습니다.",
                            column_name=original_col,
                            suggested_fix="컬럼명을 표준 형식으로 수정하는 것을 권장합니다."
                        ))
                    else:
                        unmapped_columns.append(original_col)
            
            # 3. 필수 컬럼 확인
            mapped_standard_columns = set(mapped_columns.values())
            missing_required = [col for col in self.REQUIRED_COLUMNS if col not in mapped_standard_columns]
            
            if missing_required:
                for missing_col in missing_required:
                    # 대체 가능한 컬럼 제안
                    suggestions = self._suggest_column_alternatives(missing_col, unmapped_columns)
                    
                    result.add_error(ProcessingError(
                        category=ErrorCategory.COLUMN_MAPPING,
                        severity=ErrorSeverity.CRITICAL,
                        message=f"필수 컬럼 누락: {missing_col}",
                        details=f"데이터 처리에 필요한 필수 컬럼이 없습니다.",
                        suggested_fix=f"다음 컬럼 중 하나를 추가하거나 매핑하세요: {', '.join(suggestions) if suggestions else '해당 데이터를 포함한 컬럼'}"
                    ))
            
            # 4. 권장 컬럼 확인
            missing_recommended = [col for col in self.RECOMMENDED_COLUMNS if col not in mapped_standard_columns]
            
            for missing_col in missing_recommended:
                suggestions = self._suggest_column_alternatives(missing_col, unmapped_columns)
                
                result.add_error(ProcessingError(
                    category=ErrorCategory.COLUMN_MAPPING,
                    severity=ErrorSeverity.WARNING,
                    message=f"권장 컬럼 누락: {missing_col}",
                    details="이 컬럼이 없으면 일부 기능이 제한될 수 있습니다.",
                    suggested_fix=f"가능하면 다음 컬럼을 추가하세요: {', '.join(suggestions) if suggestions else '해당 데이터를 포함한 컬럼'}"
                ))
            
            # 5. 매핑되지 않은 컬럼 처리
            for unmapped_col in unmapped_columns:
                result.add_error(ProcessingError(
                    category=ErrorCategory.COLUMN_MAPPING,
                    severity=ErrorSeverity.INFO,
                    message=f"매핑되지 않은 컬럼: {unmapped_col}",
                    details="이 컬럼은 분석에 사용되지 않습니다.",
                    column_name=unmapped_col,
                    suggested_fix="필요한 경우 컬럼 매핑 테이블에 추가하세요."
                ))
            
            # 결과 설정
            result.success = not result.has_critical_errors()
            result.metadata['mapped_columns'] = mapped_columns
            result.metadata['unmapped_columns'] = unmapped_columns
            
        except Exception as e:
            result.add_error(ProcessingError(
                category=ErrorCategory.COLUMN_MAPPING,
                severity=ErrorSeverity.CRITICAL,
                message="컬럼 매핑 처리 중 시스템 오류",
                details=str(e),
                suggested_fix="시스템 관리자에게 문의하세요."
            ))
            result.success = False
            logger.error(f"컬럼 매핑 오류: {e}", exc_info=True)
        
        return result
    
    def handle_data_type_errors(self, df: pd.DataFrame, 
                               column_mapping: Dict[str, str]) -> ProcessingResult:
        """데이터 타입 에러 처리 (요구사항: 성공 기준 1)"""
        result = ProcessingResult(success=True, total_rows=len(df))
        
        try:
            # 데이터 타입 변환 규칙
            type_conversion_rules = {
                'result_report': self._convert_numeric_result,
                'input_datetime': self._convert_datetime,
                'analysis_number': self._convert_string,
                'sample_name': self._convert_string,
                'test_item': self._convert_string,
                'tester': self._convert_string,
                'standard_criteria': self._convert_string,
                'standard_excess': self._convert_judgment
            }
            
            converted_data = {}
            
            # 각 컬럼별 데이터 타입 변환
            for original_col, standard_col in column_mapping.items():
                if original_col not in df.columns:
                    continue
                
                series = df[original_col]
                conversion_func = type_conversion_rules.get(standard_col, self._convert_string)
                
                converted_series, conversion_errors = self._convert_series_with_error_handling(
                    series, conversion_func, original_col, standard_col
                )
                
                converted_data[standard_col] = converted_series
                
                # 변환 에러 추가
                for error in conversion_errors:
                    result.add_error(error)
            
            # 변환된 데이터프레임 생성
            if converted_data:
                result.data = pd.DataFrame(converted_data)
                result.processed_rows = len(result.data)
            
            result.success = not result.has_critical_errors()
            
        except Exception as e:
            result.add_error(ProcessingError(
                category=ErrorCategory.DATA_TYPE,
                severity=ErrorSeverity.CRITICAL,
                message="데이터 타입 변환 중 시스템 오류",
                details=str(e),
                suggested_fix="시스템 관리자에게 문의하세요."
            ))
            result.success = False
            logger.error(f"데이터 타입 변환 오류: {e}", exc_info=True)
        
        return result
    
    def handle_missing_standards_errors(self, df: pd.DataFrame) -> ProcessingResult:
        """기준값 누락 에러 처리 (요구사항: 성공 기준 1)"""
        result = ProcessingResult(success=True, total_rows=len(df))
        
        try:
            if 'standard_criteria' not in df.columns:
                result.add_error(ProcessingError(
                    category=ErrorCategory.MISSING_STANDARD,
                    severity=ErrorSeverity.WARNING,
                    message="기준값 컬럼이 없습니다",
                    details="기준값 정보가 없어 부적합 판정을 수행할 수 없습니다.",
                    suggested_fix="'기준' 또는 '기준값' 컬럼을 추가하세요."
                ))
                result.success = True  # 경고이므로 처리는 계속
                return result
            
            # 기준값 누락 행 확인
            missing_standards_mask = df['standard_criteria'].isna() | (df['standard_criteria'].astype(str).str.strip() == '')
            missing_count = missing_standards_mask.sum()
            
            if missing_count > 0:
                missing_rows = df[missing_standards_mask].index.tolist()
                
                # 시험항목별 기준값 누락 통계
                if 'test_item' in df.columns:
                    missing_by_item = df[missing_standards_mask]['test_item'].value_counts()
                    
                    for test_item, count in missing_by_item.items():
                        # 동일 시험항목에서 기준값이 있는 행 찾기
                        same_item_mask = df['test_item'] == test_item
                        same_item_with_standard = df[same_item_mask & ~missing_standards_mask]
                        
                        suggested_standard = None
                        if not same_item_with_standard.empty:
                            # 가장 많이 사용된 기준값 제안
                            standard_counts = same_item_with_standard['standard_criteria'].value_counts()
                            suggested_standard = standard_counts.index[0] if not standard_counts.empty else None
                        
                        result.add_error(ProcessingError(
                            category=ErrorCategory.MISSING_STANDARD,
                            severity=ErrorSeverity.WARNING,
                            message=f"시험항목 '{test_item}'의 기준값 누락 ({count}건)",
                            details=f"해당 시험항목에서 {count}개 행의 기준값이 누락되었습니다.",
                            column_name='standard_criteria',
                            suggested_fix=f"기준값을 입력하세요. 제안값: {suggested_standard}" if suggested_standard else "해당 시험항목의 기준값을 확인하여 입력하세요."
                        ))
                
                # 기준값 자동 보완 시도
                filled_df = self._auto_fill_missing_standards(df)
                filled_count = len(df) - filled_df['standard_criteria'].isna().sum()
                
                if filled_count > len(df) - missing_count:
                    result.add_error(ProcessingError(
                        category=ErrorCategory.MISSING_STANDARD,
                        severity=ErrorSeverity.INFO,
                        message=f"기준값 자동 보완 완료 ({filled_count - (len(df) - missing_count)}건)",
                        details="동일 시험항목의 다른 행에서 기준값을 자동으로 보완했습니다.",
                        suggested_fix="자동 보완된 기준값을 확인하세요."
                    ))
                    
                    result.data = filled_df
                else:
                    result.data = df
            else:
                result.data = df
            
            result.processed_rows = len(result.data) if result.data is not None else 0
            result.success = True  # 기준값 누락은 경고 수준
            
        except Exception as e:
            result.add_error(ProcessingError(
                category=ErrorCategory.MISSING_STANDARD,
                severity=ErrorSeverity.ERROR,
                message="기준값 처리 중 오류",
                details=str(e),
                suggested_fix="데이터를 확인하고 다시 시도하세요."
            ))
            result.success = False
            logger.error(f"기준값 처리 오류: {e}", exc_info=True)
        
        return result
    
    def _normalize_column_name(self, column_name: str) -> str:
        """컬럼명 정규화"""
        if pd.isna(column_name):
            return ""
        
        # 문자열로 변환
        normalized = str(column_name).strip()
        
        # 줄바꿈 문자 제거
        normalized = normalized.replace('\n', ' ').replace('\r', ' ')
        
        # 연속된 공백을 하나로
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # 앞뒤 공백 제거
        normalized = normalized.strip()
        
        return normalized
    
    def _find_similar_column_mapping(self, column_name: str) -> Optional[str]:
        """유사한 컬럼명 매핑 찾기"""
        normalized_name = self._normalize_column_name(column_name).lower()
        
        # 키워드 기반 매핑
        keyword_mappings = {
            'sample_name': ['시료', '샘플', '검체', '시편'],
            'test_item': ['시험', '항목', '검사', '분석'],
            'result_report': ['결과', '성적', '측정', '값'],
            'tester': ['시험자', '분석자', '담당자', '검사자'],
            'standard_criteria': ['기준', '규격', '한계', '제한'],
            'standard_excess': ['판정', '적합', '초과', '여부']
        }
        
        for standard_col, keywords in keyword_mappings.items():
            for keyword in keywords:
                if keyword in normalized_name:
                    return standard_col
        
        return None
    
    def _suggest_column_alternatives(self, missing_column: str, 
                                   available_columns: List[str]) -> List[str]:
        """누락된 컬럼에 대한 대안 제안"""
        suggestions = []
        
        # 컬럼별 대안 키워드
        alternative_keywords = {
            'sample_name': ['시료', '샘플', '검체', '시편', '명', '이름'],
            'test_item': ['시험', '항목', '검사', '분석', '테스트'],
            'result_report': ['결과', '성적', '측정', '값', '데이터'],
            'tester': ['시험자', '분석자', '담당자', '검사자', '작성자'],
            'standard_criteria': ['기준', '규격', '한계', '제한', '표준'],
            'standard_excess': ['판정', '적합', '초과', '여부', '상태']
        }
        
        keywords = alternative_keywords.get(missing_column, [])
        
        for col in available_columns:
            col_lower = col.lower()
            for keyword in keywords:
                if keyword in col_lower:
                    suggestions.append(col)
                    break
        
        return suggestions[:3]  # 최대 3개까지만 제안
    
    def _convert_series_with_error_handling(self, series: pd.Series, 
                                          conversion_func, original_col: str, 
                                          standard_col: str) -> Tuple[pd.Series, List[ProcessingError]]:
        """시리즈 변환 및 에러 처리"""
        errors = []
        converted_values = []
        
        for idx, value in series.items():
            try:
                converted_value = conversion_func(value)
                converted_values.append(converted_value)
            except Exception as e:
                converted_values.append(None)
                
                errors.append(ProcessingError(
                    category=ErrorCategory.DATA_TYPE,
                    severity=ErrorSeverity.WARNING,
                    message=f"데이터 변환 실패: {original_col}",
                    details=f"값 '{value}'을(를) {standard_col} 형식으로 변환할 수 없습니다.",
                    row_index=idx,
                    column_name=original_col,
                    original_value=value,
                    suggested_fix=self._get_conversion_suggestion(standard_col, value)
                ))
        
        converted_series = pd.Series(converted_values, index=series.index, name=standard_col)
        return converted_series, errors
    
    def _convert_numeric_result(self, value) -> Optional[float]:
        """수치 결과값 변환"""
        if pd.isna(value):
            return None
        
        # 문자열 처리
        if isinstance(value, str):
            value_str = value.strip().lower()
            
            # 불검출 처리
            if value_str in ['불검출', 'nd', 'not detected', '<', '< 정량한계']:
                return 0.0
            
            # 숫자 추출
            numeric_match = re.search(r'[\d.]+', value_str)
            if numeric_match:
                return float(numeric_match.group())
        
        # 숫자 타입 처리
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValueError(f"수치로 변환할 수 없는 값: {value}")
    
    def _convert_datetime(self, value) -> Optional[datetime]:
        """날짜시간 변환"""
        if pd.isna(value):
            return None
        
        if isinstance(value, datetime):
            return value
        
        # 문자열 날짜 파싱
        if isinstance(value, str):
            date_formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y-%m-%d',
                '%Y/%m/%d %H:%M:%S',
                '%Y/%m/%d %H:%M',
                '%Y/%m/%d'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(value.strip(), fmt)
                except ValueError:
                    continue
        
        raise ValueError(f"날짜 형식으로 변환할 수 없는 값: {value}")
    
    def _convert_string(self, value) -> str:
        """문자열 변환"""
        if pd.isna(value):
            return ""
        return str(value).strip()
    
    def _convert_judgment(self, value) -> str:
        """판정 결과 변환"""
        if pd.isna(value):
            return "-"
        
        value_str = str(value).strip()
        
        # 표준화된 판정 결과로 변환
        if value_str.lower() in ['적합', 'pass', 'ok', 'good', '합격']:
            return '적합'
        elif value_str.lower() in ['부적합', 'fail', 'ng', 'bad', '불합격', '초과']:
            return '부적합'
        else:
            return value_str
    
    def _get_conversion_suggestion(self, target_type: str, original_value) -> str:
        """변환 실패 시 제안사항"""
        suggestions = {
            'result_report': "숫자 형태로 입력하거나 '불검출'로 표시하세요.",
            'input_datetime': "날짜 형식을 'YYYY-MM-DD HH:MM:SS' 또는 'YYYY-MM-DD'로 입력하세요.",
            'standard_excess': "'적합' 또는 '부적합'으로 입력하세요.",
        }
        
        return suggestions.get(target_type, "올바른 형식으로 데이터를 입력하세요.")
    
    def _auto_fill_missing_standards(self, df: pd.DataFrame) -> pd.DataFrame:
        """기준값 자동 보완"""
        filled_df = df.copy()
        
        if 'test_item' not in df.columns or 'standard_criteria' not in df.columns:
            return filled_df
        
        # 시험항목별로 기준값 보완
        for test_item in df['test_item'].unique():
            if pd.isna(test_item):
                continue
            
            item_mask = df['test_item'] == test_item
            item_data = df[item_mask]
            
            # 해당 시험항목에서 가장 많이 사용된 기준값 찾기
            valid_standards = item_data['standard_criteria'].dropna()
            valid_standards = valid_standards[valid_standards.astype(str).str.strip() != '']
            
            if not valid_standards.empty:
                most_common_standard = valid_standards.mode()
                if not most_common_standard.empty:
                    # 누락된 기준값 보완
                    missing_mask = item_mask & (df['standard_criteria'].isna() | (df['standard_criteria'].astype(str).str.strip() == ''))
                    filled_df.loc[missing_mask, 'standard_criteria'] = most_common_standard.iloc[0]
        
        return filled_df


class UserFriendlyErrorFormatter:
    """사용자 친화적 에러 메시지 포맷터"""
    
    @staticmethod
    def format_processing_result(result: ProcessingResult) -> Dict[str, Any]:
        """처리 결과를 사용자 친화적 형태로 포맷"""
        formatted = {
            'success': result.success,
            'summary': {
                'total_rows': result.total_rows,
                'processed_rows': result.processed_rows,
                'success_rate': (result.processed_rows / result.total_rows * 100) if result.total_rows > 0 else 0
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
        
        # 에러 및 경고 분류
        all_issues = result.errors + result.warnings
        
        for issue in all_issues:
            formatted_issue = {
                'message': issue.message,
                'details': issue.details,
                'location': UserFriendlyErrorFormatter._format_location(issue),
                'suggested_fix': issue.suggested_fix,
                'category': issue.category.value
            }
            
            if issue.severity == ErrorSeverity.CRITICAL:
                formatted['issues']['critical'].append(formatted_issue)
            elif issue.severity == ErrorSeverity.ERROR:
                formatted['issues']['errors'].append(formatted_issue)
            elif issue.severity == ErrorSeverity.WARNING:
                formatted['issues']['warnings'].append(formatted_issue)
            else:
                formatted['issues']['info'].append(formatted_issue)
        
        # 전체적인 제안사항 생성
        formatted['suggestions'] = UserFriendlyErrorFormatter._generate_overall_suggestions(result)
        
        # 다음 단계 제안
        formatted['next_steps'] = UserFriendlyErrorFormatter._generate_next_steps(result)
        
        return formatted
    
    @staticmethod
    def _format_location(error: ProcessingError) -> str:
        """에러 위치 포맷"""
        location_parts = []
        
        if error.row_index is not None:
            location_parts.append(f"행 {error.row_index + 1}")
        
        if error.column_name:
            location_parts.append(f"컬럼 '{error.column_name}'")
        
        return ", ".join(location_parts) if location_parts else "전체"
    
    @staticmethod
    def _generate_overall_suggestions(result: ProcessingResult) -> List[str]:
        """전체적인 제안사항 생성"""
        suggestions = []
        
        # 에러 카테고리별 제안
        error_categories = set(error.category for error in result.errors + result.warnings)
        
        if ErrorCategory.COLUMN_MAPPING in error_categories:
            suggestions.append("컬럼명을 표준 형식으로 수정하면 더 정확한 분석이 가능합니다.")
        
        if ErrorCategory.DATA_TYPE in error_categories:
            suggestions.append("데이터 형식을 통일하면 처리 오류를 줄일 수 있습니다.")
        
        if ErrorCategory.MISSING_STANDARD in error_categories:
            suggestions.append("기준값을 모든 시험항목에 입력하면 정확한 판정이 가능합니다.")
        
        # 성공률 기반 제안
        success_rate = (result.processed_rows / result.total_rows * 100) if result.total_rows > 0 else 0
        
        if success_rate < 50:
            suggestions.append("데이터 품질이 낮습니다. 원본 파일을 검토해주세요.")
        elif success_rate < 80:
            suggestions.append("일부 데이터에 문제가 있습니다. 해당 행들을 수정해주세요.")
        
        return suggestions
    
    @staticmethod
    def _generate_next_steps(result: ProcessingResult) -> List[str]:
        """다음 단계 제안"""
        next_steps = []
        
        if result.has_critical_errors():
            next_steps.extend([
                "1. 치명적 오류를 먼저 해결하세요.",
                "2. 데이터 파일을 수정한 후 다시 업로드하세요."
            ])
        elif result.errors:
            next_steps.extend([
                "1. 오류가 있는 데이터를 확인하고 수정하세요.",
                "2. 수정 후 다시 처리하거나 현재 상태로 계속 진행할 수 있습니다."
            ])
        elif result.warnings:
            next_steps.extend([
                "1. 경고 사항을 검토하세요.",
                "2. 필요시 데이터를 수정하거나 현재 상태로 분석을 계속하세요."
            ])
        else:
            next_steps.append("데이터 처리가 완료되었습니다. 분석을 시작할 수 있습니다.")
        
        return next_steps


# 사용 예시 및 테스트 함수
def test_error_handler():
    """에러 핸들러 테스트"""
    handler = DataProcessingErrorHandler()
    
    # 테스트 데이터 생성
    test_data = pd.DataFrame({
        '시료명': ['샘플1', '샘플2', None, '샘플4'],
        '시험항목': ['항목A', '항목B', '항목A', '항목C'],
        '결과(성적서)': ['1.5', 'not detected', 'invalid', '2.0'],
        '시험자': ['김철수', '이영희', '박민수', None],
        '기준': ['2.0 이하', None, '2.0 이하', '1.0 이하'],
        '판정': ['적합', '적합', 'unknown', '부적합']
    })
    
    print("=== 컬럼 매핑 테스트 ===")
    mapping_result = handler.handle_column_mapping_errors(test_data)
    print(f"성공: {mapping_result.success}")
    print(f"에러 수: {len(mapping_result.errors)}")
    print(f"경고 수: {len(mapping_result.warnings)}")
    
    if mapping_result.success:
        print("\n=== 데이터 타입 변환 테스트 ===")
        column_mapping = mapping_result.metadata.get('mapped_columns', {})
        type_result = handler.handle_data_type_errors(test_data, column_mapping)
        print(f"성공: {type_result.success}")
        print(f"처리된 행 수: {type_result.processed_rows}")
        
        if type_result.data is not None:
            print("\n=== 기준값 누락 처리 테스트 ===")
            standards_result = handler.handle_missing_standards_errors(type_result.data)
            print(f"성공: {standards_result.success}")
            
            # 사용자 친화적 메시지 포맷팅 테스트
            print("\n=== 사용자 친화적 메시지 ===")
            formatted = UserFriendlyErrorFormatter.format_processing_result(standards_result)
            print(f"전체 성공률: {formatted['summary']['success_rate']:.1f}%")
            print(f"제안사항: {formatted['suggestions']}")
            print(f"다음 단계: {formatted['next_steps']}")


if __name__ == "__main__":
    test_error_handler()