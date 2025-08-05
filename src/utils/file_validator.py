"""
파일 업로드 검증 시스템
File Upload Validation System

Task 11.1: 파일 업로드 검증 구현
- 파일 형식 검증 로직 구현
- 파일 크기 제한 검증 구현
- 파일 손상 검사 기능 구현
- 에러 메시지 표시 시스템 구현
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import zipfile
import logging
from dataclasses import dataclass
from enum import Enum

# 로깅 설정
logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """검증 수준"""
    BASIC = "basic"      # 기본 검증 (확장자, 크기)
    STANDARD = "standard"  # 표준 검증 (기본 + MIME 타입)
    STRICT = "strict"    # 엄격한 검증 (표준 + 내용 검사)


@dataclass
class ValidationResult:
    """검증 결과"""
    is_valid: bool
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    errors: List[str] = None
    warnings: List[str] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}


class FileValidator:
    """파일 업로드 검증 클래스"""
    
    # 지원되는 파일 형식 (요구사항: 기술적 제약사항 1)
    SUPPORTED_EXTENSIONS = {
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xls': 'application/vnd.ms-excel',
        '.csv': 'text/csv',
        '.txt': 'text/plain'
    }
    
    # 파일 크기 제한 (요구사항: 기술적 제약사항 3)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MIN_FILE_SIZE = 1024  # 1KB
    
    # 위험한 파일 확장자
    DANGEROUS_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
        '.jar', '.app', '.deb', '.pkg', '.dmg', '.iso', '.msi'
    }
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        """
        파일 검증기 초기화
        
        Args:
            validation_level: 검증 수준
        """
        self.validation_level = validation_level
        self.custom_validators = []
        
    def validate_file(self, file_path: Union[str, Path], 
                     uploaded_file=None) -> ValidationResult:
        """
        파일 검증 메인 함수
        
        Args:
            file_path: 파일 경로
            uploaded_file: Streamlit 업로드 파일 객체 (선택사항)
            
        Returns:
            ValidationResult: 검증 결과
        """
        result = ValidationResult(is_valid=True, file_path=str(file_path))
        
        try:
            # 1. 기본 검증
            self._validate_basic(file_path, result, uploaded_file)
            
            # 2. 표준 검증 (MIME 타입)
            if self.validation_level in [ValidationLevel.STANDARD, ValidationLevel.STRICT]:
                self._validate_mime_type(file_path, result, uploaded_file)
            
            # 3. 엄격한 검증 (파일 내용)
            if self.validation_level == ValidationLevel.STRICT:
                self._validate_content(file_path, result, uploaded_file)
            
            # 4. 커스텀 검증
            self._run_custom_validators(file_path, result, uploaded_file)
            
            # 최종 검증 상태 결정
            result.is_valid = len(result.errors) == 0
            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"검증 중 예상치 못한 오류 발생: {str(e)}")
            logger.error(f"파일 검증 오류: {e}", exc_info=True)
        
        return result
    
    def _validate_basic(self, file_path: Union[str, Path], 
                       result: ValidationResult, uploaded_file=None) -> None:
        """기본 검증 (확장자, 크기, 보안)"""
        file_path = Path(file_path)
        
        # 1. 파일 확장자 검증
        extension = file_path.suffix.lower()
        
        if not extension:
            result.errors.append("파일 확장자가 없습니다.")
            return
        
        if extension in self.DANGEROUS_EXTENSIONS:
            result.errors.append(f"보안상 위험한 파일 형식입니다: {extension}")
            return
        
        if extension not in self.SUPPORTED_EXTENSIONS:
            supported_list = ', '.join(self.SUPPORTED_EXTENSIONS.keys())
            result.errors.append(
                f"지원되지 않는 파일 형식입니다. "
                f"지원 형식: {supported_list}"
            )
            return
        
        # 2. 파일 크기 검증
        file_size = None
        
        if uploaded_file:
            # Streamlit 업로드 파일인 경우
            file_size = len(uploaded_file.getvalue()) if hasattr(uploaded_file, 'getvalue') else None
        elif file_path.exists():
            # 로컬 파일인 경우
            file_size = file_path.stat().st_size
        
        if file_size is not None:
            result.file_size = file_size
            
            if file_size < self.MIN_FILE_SIZE:
                result.errors.append(
                    f"파일이 너무 작습니다. "
                    f"최소 크기: {self._format_file_size(self.MIN_FILE_SIZE)}"
                )
            
            if file_size > self.MAX_FILE_SIZE:
                result.errors.append(
                    f"파일이 너무 큽니다. "
                    f"최대 크기: {self._format_file_size(self.MAX_FILE_SIZE)}, "
                    f"현재 크기: {self._format_file_size(file_size)}"
                )
        
        # 3. 파일명 검증
        self._validate_filename(file_path.name, result)
        
        # 메타데이터 저장
        result.metadata.update({
            'extension': extension,
            'filename': file_path.name,
            'expected_mime_type': self.SUPPORTED_EXTENSIONS.get(extension)
        })
    
    def _validate_mime_type(self, file_path: Union[str, Path], 
                           result: ValidationResult, uploaded_file=None) -> None:
        """MIME 타입 검증"""
        try:
            extension = Path(file_path).suffix.lower()
            expected_mime = self.SUPPORTED_EXTENSIONS.get(extension)
            
            if not expected_mime:
                return  # 기본 검증에서 이미 처리됨
            
            # MIME 타입 감지
            detected_mime = None
            
            if uploaded_file and hasattr(uploaded_file, 'type'):
                # Streamlit 업로드 파일의 MIME 타입
                detected_mime = uploaded_file.type
            else:
                # 파일 경로에서 MIME 타입 추정
                detected_mime, _ = mimetypes.guess_type(str(file_path))
            
            result.mime_type = detected_mime
            
            # MIME 타입 검증
            if detected_mime:
                # 일반적인 MIME 타입 변형 허용
                allowed_mimes = [expected_mime]
                
                # Excel 파일의 경우 추가 MIME 타입 허용
                if extension == '.xlsx':
                    allowed_mimes.extend([
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        'application/zip'  # xlsx는 실제로 zip 파일
                    ])
                elif extension == '.xls':
                    allowed_mimes.extend([
                        'application/vnd.ms-excel',
                        'application/msexcel',
                        'application/x-msexcel'
                    ])
                elif extension == '.csv':
                    allowed_mimes.extend([
                        'text/csv',
                        'text/plain',
                        'application/csv'
                    ])
                
                if detected_mime not in allowed_mimes:
                    result.warnings.append(
                        f"파일 형식이 예상과 다릅니다. "
                        f"예상: {expected_mime}, 감지: {detected_mime}"
                    )
            else:
                result.warnings.append("MIME 타입을 감지할 수 없습니다.")
                
        except Exception as e:
            result.warnings.append(f"MIME 타입 검증 중 오류: {str(e)}")
    
    def _validate_content(self, file_path: Union[str, Path], 
                         result: ValidationResult, uploaded_file=None) -> None:
        """파일 내용 검증 (파일 손상 검사)"""
        try:
            extension = Path(file_path).suffix.lower()
            
            if extension in ['.xlsx', '.xls']:
                self._validate_excel_content(file_path, result, uploaded_file)
            elif extension == '.csv':
                self._validate_csv_content(file_path, result, uploaded_file)
                
        except Exception as e:
            result.errors.append(f"파일 내용 검증 실패: {str(e)}")
    
    def _validate_excel_content(self, file_path: Union[str, Path], 
                               result: ValidationResult, uploaded_file=None) -> None:
        """Excel 파일 내용 검증"""
        try:
            # pandas로 파일 읽기 시도
            if uploaded_file:
                # Streamlit 업로드 파일인 경우
                df = pd.read_excel(uploaded_file, nrows=5)  # 처음 5행만 읽어서 테스트
            else:
                # 로컬 파일인 경우
                df = pd.read_excel(file_path, nrows=5)
            
            # 기본 구조 검증
            if df.empty:
                result.warnings.append("Excel 파일이 비어있습니다.")
            else:
                result.metadata.update({
                    'preview_rows': len(df),
                    'preview_columns': len(df.columns),
                    'column_names': list(df.columns)[:10]  # 처음 10개 컬럼명만
                })
                
                # 필수 컬럼 존재 여부 확인 (선택사항)
                expected_columns = ['시료명', '시험항목', '결과(성적서)']
                missing_columns = [col for col in expected_columns if col not in df.columns]
                
                if missing_columns:
                    result.warnings.append(
                        f"권장 컬럼이 누락되었을 수 있습니다: {', '.join(missing_columns)}"
                    )
                
        except zipfile.BadZipFile:
            result.errors.append("Excel 파일이 손상되었습니다 (압축 파일 오류).")
        except pd.errors.ExcelFileError as e:
            result.errors.append(f"Excel 파일 형식 오류: {str(e)}")
        except Exception as e:
            result.errors.append(f"Excel 파일 검증 실패: {str(e)}")
    
    def _validate_csv_content(self, file_path: Union[str, Path], 
                             result: ValidationResult, uploaded_file=None) -> None:
        """CSV 파일 내용 검증"""
        try:
            # pandas로 파일 읽기 시도
            if uploaded_file:
                df = pd.read_csv(uploaded_file, nrows=5, encoding='utf-8')
            else:
                # 인코딩 자동 감지 시도
                encodings = ['utf-8', 'cp949', 'euc-kr', 'latin1']
                df = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, nrows=5, encoding=encoding)
                        result.metadata['detected_encoding'] = encoding
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    result.errors.append("CSV 파일의 인코딩을 감지할 수 없습니다.")
                    return
            
            # 기본 구조 검증
            if df.empty:
                result.warnings.append("CSV 파일이 비어있습니다.")
            else:
                result.metadata.update({
                    'preview_rows': len(df),
                    'preview_columns': len(df.columns),
                    'column_names': list(df.columns)[:10]
                })
                
        except pd.errors.EmptyDataError:
            result.errors.append("CSV 파일이 비어있거나 형식이 잘못되었습니다.")
        except pd.errors.ParserError as e:
            result.errors.append(f"CSV 파일 파싱 오류: {str(e)}")
        except Exception as e:
            result.errors.append(f"CSV 파일 검증 실패: {str(e)}")
    
    def _validate_filename(self, filename: str, result: ValidationResult) -> None:
        """파일명 검증"""
        # 파일명 길이 검사
        if len(filename) > 255:
            result.errors.append("파일명이 너무 깁니다 (최대 255자).")
        
        # 위험한 문자 검사
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        found_chars = [char for char in dangerous_chars if char in filename]
        
        if found_chars:
            result.warnings.append(
                f"파일명에 특수문자가 포함되어 있습니다: {', '.join(found_chars)}"
            )
        
        # 한글/영문 파일명 검증
        if not filename.replace('.', '').replace('-', '').replace('_', '').replace(' ', '').isalnum():
            # 한글이 포함된 경우는 허용
            try:
                filename.encode('ascii')
            except UnicodeEncodeError:
                # 한글 등 비ASCII 문자 포함 - 경고만 표시
                result.warnings.append("파일명에 한글이 포함되어 있습니다. 호환성을 위해 영문 사용을 권장합니다.")
    
    def _run_custom_validators(self, file_path: Union[str, Path], 
                              result: ValidationResult, uploaded_file=None) -> None:
        """커스텀 검증 함수 실행"""
        for validator_func in self.custom_validators:
            try:
                validator_func(file_path, result, uploaded_file)
            except Exception as e:
                result.warnings.append(f"커스텀 검증 오류: {str(e)}")
    
    def add_custom_validator(self, validator_func) -> None:
        """커스텀 검증 함수 추가"""
        self.custom_validators.append(validator_func)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """파일 크기를 읽기 쉬운 형태로 변환"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    @classmethod
    def create_lab_validator(cls) -> 'FileValidator':
        """실험실 데이터용 특화 검증기 생성"""
        validator = cls(ValidationLevel.STRICT)
        
        # 실험실 데이터 특화 검증 함수 추가
        def validate_lab_data_structure(file_path, result, uploaded_file):
            """실험실 데이터 구조 검증"""
            try:
                extension = Path(file_path).suffix.lower()
                
                if extension in ['.xlsx', '.xls']:
                    # Excel 파일의 경우 필수 컬럼 검사
                    if uploaded_file:
                        df = pd.read_excel(uploaded_file, nrows=1)
                    else:
                        df = pd.read_excel(file_path, nrows=1)
                    
                    required_columns = ['시료명', '시험항목']
                    missing_required = [col for col in required_columns if col not in df.columns]
                    
                    if missing_required:
                        result.errors.append(
                            f"실험실 데이터 필수 컬럼이 누락되었습니다: {', '.join(missing_required)}"
                        )
                    
                    # 권장 컬럼 검사
                    recommended_columns = ['결과(성적서)', '시험자', '기준대비 초과여부']
                    missing_recommended = [col for col in recommended_columns if col not in df.columns]
                    
                    if missing_recommended:
                        result.warnings.append(
                            f"권장 컬럼이 누락되었습니다: {', '.join(missing_recommended)}"
                        )
                        
            except Exception as e:
                result.warnings.append(f"실험실 데이터 구조 검증 실패: {str(e)}")
        
        validator.add_custom_validator(validate_lab_data_structure)
        return validator


class ErrorMessageFormatter:
    """에러 메시지 표시 시스템"""
    
    @staticmethod
    def format_validation_result(result: ValidationResult) -> Dict[str, str]:
        """검증 결과를 사용자 친화적 메시지로 변환"""
        messages = {
            'status': 'success' if result.is_valid else 'error',
            'title': '파일 검증 완료' if result.is_valid else '파일 검증 실패',
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # 에러 메시지 처리
        for error in result.errors:
            messages['errors'].append({
                'message': error,
                'type': 'error',
                'icon': '❌'
            })
        
        # 경고 메시지 처리
        for warning in result.warnings:
            messages['warnings'].append({
                'message': warning,
                'type': 'warning',
                'icon': '⚠️'
            })
        
        # 정보 메시지 생성
        if result.is_valid:
            info_messages = []
            
            if result.file_size:
                info_messages.append(f"파일 크기: {FileValidator._format_file_size(FileValidator(), result.file_size)}")
            
            if result.mime_type:
                info_messages.append(f"파일 형식: {result.mime_type}")
            
            if 'preview_rows' in result.metadata:
                info_messages.append(f"데이터 행 수: {result.metadata['preview_rows']}행 (미리보기)")
            
            if 'preview_columns' in result.metadata:
                info_messages.append(f"컬럼 수: {result.metadata['preview_columns']}개")
            
            for info in info_messages:
                messages['info'].append({
                    'message': info,
                    'type': 'info',
                    'icon': 'ℹ️'
                })
        
        return messages
    
    @staticmethod
    def get_error_solutions(error_message: str) -> List[str]:
        """에러 메시지에 대한 해결 방안 제시"""
        solutions = []
        
        if "지원되지 않는 파일 형식" in error_message:
            solutions.extend([
                "Excel 파일(.xlsx, .xls) 또는 CSV 파일(.csv)을 사용해주세요.",
                "파일을 Excel에서 다시 저장해보세요.",
                "파일 확장자가 올바른지 확인해주세요."
            ])
        
        elif "파일이 너무 큽니다" in error_message:
            solutions.extend([
                "파일 크기를 50MB 이하로 줄여주세요.",
                "불필요한 시트나 데이터를 제거해보세요.",
                "파일을 여러 개로 분할해서 업로드해보세요."
            ])
        
        elif "파일이 손상되었습니다" in error_message:
            solutions.extend([
                "원본 파일을 다시 확인해주세요.",
                "파일을 Excel에서 다시 열어서 저장해보세요.",
                "다른 컴퓨터에서 파일을 열어보세요."
            ])
        
        elif "필수 컬럼이 누락" in error_message:
            solutions.extend([
                "Excel 파일에 '시료명', '시험항목' 컬럼이 있는지 확인해주세요.",
                "컬럼명의 띄어쓰기나 특수문자를 확인해주세요.",
                "첫 번째 행이 컬럼 헤더인지 확인해주세요."
            ])
        
        elif "인코딩을 감지할 수 없습니다" in error_message:
            solutions.extend([
                "CSV 파일을 UTF-8 인코딩으로 저장해주세요.",
                "Excel에서 CSV로 내보낼 때 'UTF-8 CSV' 형식을 선택해주세요.",
                "메모장에서 파일을 열어 '다른 이름으로 저장' > 인코딩을 UTF-8로 변경해주세요."
            ])
        
        return solutions


# 사용 예시 및 테스트 함수
def test_file_validator():
    """파일 검증기 테스트"""
    validator = FileValidator.create_lab_validator()
    
    # 테스트 케이스들
    test_cases = [
        ("test.xlsx", True),
        ("test.xls", True),
        ("test.csv", True),
        ("test.txt", True),
        ("test.exe", False),
        ("test", False),
        ("a" * 300 + ".xlsx", False),  # 너무 긴 파일명
    ]
    
    for filename, should_pass in test_cases:
        # 가상의 파일 경로로 기본 검증만 테스트
        result = ValidationResult(is_valid=True, file_path=filename)
        
        try:
            validator._validate_filename(filename, result)
            extension = Path(filename).suffix.lower()
            
            if extension in validator.DANGEROUS_EXTENSIONS:
                result.errors.append(f"위험한 파일 형식: {extension}")
            elif extension not in validator.SUPPORTED_EXTENSIONS and extension:
                result.errors.append(f"지원되지 않는 형식: {extension}")
            elif not extension:
                result.errors.append("확장자 없음")
            
            result.is_valid = len(result.errors) == 0
            
            print(f"파일: {filename}")
            print(f"예상 결과: {'통과' if should_pass else '실패'}")
            print(f"실제 결과: {'통과' if result.is_valid else '실패'}")
            print(f"에러: {result.errors}")
            print(f"경고: {result.warnings}")
            print("---")
            
        except Exception as e:
            print(f"테스트 오류 ({filename}): {e}")


if __name__ == "__main__":
    test_file_validator()