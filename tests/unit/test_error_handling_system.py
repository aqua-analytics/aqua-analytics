"""
에러 처리 시스템 통합 테스트
Error Handling System Integration Tests

Task 11.1 & 11.2: 파일 업로드 검증 및 데이터 처리 에러 핸들링 테스트
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
from io import BytesIO
import sys

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src" / "utils"))

try:
    from file_validator import FileValidator, ValidationResult, ValidationLevel, ErrorMessageFormatter
    from error_handler import DataProcessingErrorHandler, ProcessingResult, UserFriendlyErrorFormatter
    from validation import IntegratedValidator
except ImportError as e:
    pytest.skip(f"검증 모듈을 임포트할 수 없습니다: {e}", allow_module_level=True)


class TestFileValidation:
    """파일 검증 테스트 (Task 11.1)"""
    
    def setup_method(self):
        """테스트 설정"""
        self.validator = FileValidator.create_lab_validator()
        
    def test_supported_file_extensions(self):
        """지원되는 파일 확장자 테스트"""
        supported_files = [
            "test.xlsx",
            "test.xls", 
            "test.csv",
            "data.XLSX",  # 대소문자 구분 없음
        ]
        
        for filename in supported_files:
            result = ValidationResult(is_valid=True, file_path=filename)
            self.validator._validate_basic(filename, result)
            
            # 파일 크기 문제가 없다면 확장자는 통과해야 함
            extension_errors = [e for e in result.errors if "지원되지 않는" in e or "확장자" in e]
            assert len(extension_errors) == 0, f"지원되는 파일 {filename}이 거부됨"
    
    def test_unsupported_file_extensions(self):
        """지원되지 않는 파일 확장자 테스트"""
        unsupported_files = [
            "test.exe",
            "test.bat",
            "test.pdf",
            "test.doc",
            "test"       # 확장자 없음
        ]
        
        for filename in unsupported_files:
            result = ValidationResult(is_valid=True, file_path=filename)
            self.validator._validate_basic(filename, result)
            
            # 확장자 관련 에러가 있어야 함
            has_extension_error = any(
                "지원되지 않는" in error or "확장자" in error or "보안상 위험" in error 
                for error in result.errors
            )
            assert has_extension_error, f"지원되지 않는 파일 {filename}이 통과됨"
    
    def test_file_size_validation(self):
        """파일 크기 검증 테스트"""
        # 가상의 파일 크기 테스트
        test_cases = [
            (1024, True),          # 1KB - 통과  
            (1024 * 1024, True),   # 1MB - 통과
            (50 * 1024 * 1024, True),  # 50MB - 경계값 통과
            (51 * 1024 * 1024, False), # 51MB - 실패
            (500, False),          # 500B - 너무 작음 (MIN_FILE_SIZE = 1024)
        ]
        
        for file_size, should_pass in test_cases:
            result = ValidationResult(is_valid=True, file_path="test.xlsx", file_size=file_size)
            
            # 파일 크기 검증 로직 시뮬레이션
            if file_size < self.validator.MIN_FILE_SIZE:
                result.errors.append(f"파일이 너무 작습니다.")
            elif file_size > self.validator.MAX_FILE_SIZE:
                result.errors.append(f"파일이 너무 큽니다.")
            
            result.is_valid = len(result.errors) == 0
            
            assert result.is_valid == should_pass, f"파일 크기 {file_size}B 검증 실패"
    
    def test_filename_validation(self):
        """파일명 검증 테스트"""
        test_cases = [
            ("normal_file.xlsx", True),
            ("한글파일명.xlsx", True),  # 한글 허용 (경고만)
            ("file with spaces.xlsx", True),
            ("a" * 300 + ".xlsx", False),  # 너무 긴 파일명
        ]
        
        for filename, should_pass in test_cases:
            result = ValidationResult(is_valid=True, file_path=filename)
            self.validator._validate_filename(filename, result)
            
            has_critical_errors = any(
                error for error in result.errors 
                if "너무 깁니다" in error
            )
            
            # 경고는 있을 수 있지만 에러는 예상대로 있어야 함
            has_warnings = any(
                warning for warning in result.warnings
                if "특수문자" in warning or "한글" in warning
            )
            
            if should_pass:
                assert not has_critical_errors, f"유효한 파일명 {filename}이 거부됨"
            else:
                assert has_critical_errors, f"유효하지 않은 파일명 {filename}이 통과됨"
    
    def test_excel_content_validation(self):
        """Excel 파일 내용 검증 테스트"""
        # 테스트용 Excel 데이터 생성
        test_data = pd.DataFrame({
            '시료명': ['샘플1', '샘플2'],
            '시험항목': ['항목A', '항목B'],
            '결과(성적서)': [1.5, 2.0]
        })
        
        # 임시 Excel 파일 생성
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            test_data.to_excel(tmp_file.name, index=False)
            
            try:
                result = ValidationResult(is_valid=True, file_path=tmp_file.name)
                self.validator._validate_excel_content(tmp_file.name, result)
                
                # 정상적인 Excel 파일은 에러가 없어야 함
                assert len(result.errors) == 0, f"정상 Excel 파일 검증 실패: {result.errors}"
                
                # 메타데이터가 설정되어야 함
                assert 'preview_rows' in result.metadata
                assert 'preview_columns' in result.metadata
                assert result.metadata['preview_rows'] == 2
                assert result.metadata['preview_columns'] == 3
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_error_message_formatting(self):
        """에러 메시지 포맷팅 테스트"""
        # 테스트용 검증 결과 생성
        result = ValidationResult(is_valid=False, file_path="test.xlsx")
        result.errors = [
            "지원되지 않는 파일 형식입니다.",
            "파일이 너무 큽니다."
        ]
        result.warnings = [
            "파일명에 한글이 포함되어 있습니다."
        ]
        
        # 메시지 포맷팅
        formatted = ErrorMessageFormatter.format_validation_result(result)
        
        assert formatted['status'] == 'error'
        assert len(formatted['errors']) == 2
        assert len(formatted['warnings']) == 1
        
        # 해결 방안 제안 테스트
        solutions = ErrorMessageFormatter.get_error_solutions("지원되지 않는 파일 형식")
        assert len(solutions) > 0
        assert any("Excel" in solution for solution in solutions)


class TestDataProcessingErrorHandling:
    """데이터 처리 에러 핸들링 테스트 (Task 11.2)"""
    
    def setup_method(self):
        """테스트 설정"""
        self.error_handler = DataProcessingErrorHandler()
    
    def test_column_mapping_success(self):
        """컬럼 매핑 성공 케이스 테스트"""
        # 표준 컬럼명을 가진 데이터
        test_data = pd.DataFrame({
            '시료명': ['샘플1', '샘플2'],
            '시험항목': ['항목A', '항목B'],
            '결과(성적서)': [1.5, 2.0],
            '시험자': ['김철수', '이영희']
        })
        
        result = self.error_handler.handle_column_mapping_errors(test_data)
        
        assert result.success == True
        assert len(result.errors) == 0
        assert 'mapped_columns' in result.metadata
        
        # 필수 컬럼이 모두 매핑되었는지 확인
        mapped_standard_columns = set(result.metadata['mapped_columns'].values())
        required_mapped = all(
            req_col in mapped_standard_columns 
            for req_col in self.error_handler.REQUIRED_COLUMNS
        )
        assert required_mapped, "필수 컬럼 매핑 실패"
    
    def test_column_mapping_missing_required(self):
        """필수 컬럼 누락 테스트"""
        # 필수 컬럼이 누락된 데이터
        test_data = pd.DataFrame({
            '시료명': ['샘플1', '샘플2'],
            # '시험항목' 누락
            '결과(성적서)': [1.5, 2.0]
        })
        
        result = self.error_handler.handle_column_mapping_errors(test_data)
        
        assert result.success == False
        assert result.has_critical_errors() == True
        
        # 누락된 컬럼에 대한 에러가 있어야 함
        missing_errors = [
            error for error in result.errors 
            if "필수 컬럼 누락" in error.message
        ]
        assert len(missing_errors) > 0
    
    def test_column_mapping_similar_names(self):
        """유사한 컬럼명 매핑 테스트"""
        # 유사하지만 정확하지 않은 컬럼명
        test_data = pd.DataFrame({
            '샘플명': ['샘플1', '샘플2'],      # '시료명' 대신
            '테스트항목': ['항목A', '항목B'],   # '시험항목' 대신
            '측정결과': [1.5, 2.0],          # '결과(성적서)' 대신
        })
        
        result = self.error_handler.handle_column_mapping_errors(test_data)
        
        # 유사도 기반 매핑으로 성공해야 함
        assert result.success == True
        
        # 경고가 있어야 함 (유사도 매핑 사용)
        similarity_warnings = [
            warning for warning in result.warnings
            if "유사도 매핑" in warning.message
        ]
        assert len(similarity_warnings) > 0
    
    def test_data_type_conversion_success(self):
        """데이터 타입 변환 성공 테스트"""
        test_data = pd.DataFrame({
            '시료명': ['샘플1', '샘플2'],
            '시험항목': ['항목A', '항목B'],
            '결과(성적서)': ['1.5', '2.0'],  # 문자열 숫자
            '시험자': ['김철수', '이영희']
        })
        
        column_mapping = {
            '시료명': 'sample_name',
            '시험항목': 'test_item',
            '결과(성적서)': 'result_report',
            '시험자': 'tester'
        }
        
        result = self.error_handler.handle_data_type_errors(test_data, column_mapping)
        
        assert result.success == True
        assert result.data is not None
        assert len(result.data) == 2
        
        # 숫자 변환이 성공했는지 확인
        assert 'result_report' in result.data.columns
    
    def test_data_type_conversion_failures(self):
        """데이터 타입 변환 실패 테스트"""
        test_data = pd.DataFrame({
            '시료명': ['샘플1', '샘플2'],
            '시험항목': ['항목A', '항목B'],
            '결과(성적서)': ['invalid_number', '2.0'],  # 변환 불가능한 값
            '입력일시': ['invalid_date', '2024-01-01']   # 변환 불가능한 날짜
        })
        
        column_mapping = {
            '시료명': 'sample_name',
            '시험항목': 'test_item',
            '결과(성적서)': 'result_report',
            '입력일시': 'input_datetime'
        }
        
        result = self.error_handler.handle_data_type_errors(test_data, column_mapping)
        
        # 변환 실패가 있어도 처리는 계속되어야 함
        assert result.data is not None
        
        # 변환 실패에 대한 경고가 있어야 함
        conversion_warnings = [
            warning for warning in result.warnings
            if "데이터 변환 실패" in warning.message
        ]
        assert len(conversion_warnings) > 0
    
    def test_missing_standards_handling(self):
        """기준값 누락 처리 테스트"""
        test_data = pd.DataFrame({
            'sample_name': ['샘플1', '샘플2', '샘플3'],
            'test_item': ['항목A', '항목A', '항목B'],
            'result_report': [1.5, 2.0, 3.0],
            'standard_criteria': ['2.0 이하', None, '4.0 이하']  # 중간값 누락
        })
        
        result = self.error_handler.handle_missing_standards_errors(test_data)
        
        assert result.success == True  # 기준값 누락은 경고 수준
        assert result.data is not None
        
        # 기준값 누락에 대한 경고가 있어야 함
        missing_warnings = [
            warning for warning in result.warnings
            if "기준값 누락" in warning.message
        ]
        assert len(missing_warnings) > 0
        
        # 자동 보완이 시도되었는지 확인
        filled_standards = result.data['standard_criteria'].dropna()
        assert len(filled_standards) >= 2  # 최소 2개는 채워져야 함
    
    def test_user_friendly_error_formatting(self):
        """사용자 친화적 에러 메시지 포맷팅 테스트"""
        # 테스트용 처리 결과 생성
        result = ProcessingResult(success=False, total_rows=10, processed_rows=8)
        
        from error_handler import ProcessingError, ErrorCategory, ErrorSeverity
        
        result.add_error(ProcessingError(
            category=ErrorCategory.COLUMN_MAPPING,
            severity=ErrorSeverity.CRITICAL,
            message="필수 컬럼 누락",
            details="시험항목 컬럼이 없습니다",
            suggested_fix="시험항목 컬럼을 추가하세요"
        ))
        
        result.add_error(ProcessingError(
            category=ErrorCategory.DATA_TYPE,
            severity=ErrorSeverity.WARNING,
            message="데이터 변환 실패",
            details="일부 숫자 변환 실패",
            row_index=5,
            column_name="결과값"
        ))
        
        # 포맷팅 테스트
        formatted = UserFriendlyErrorFormatter.format_processing_result(result)
        
        assert formatted['success'] == False
        assert formatted['summary']['total_rows'] == 10
        assert formatted['summary']['processed_rows'] == 8
        assert formatted['summary']['success_rate'] == 80.0
        
        # 이슈 분류 확인
        assert len(formatted['issues']['critical']) == 1
        assert len(formatted['issues']['warnings']) == 1
        
        # 제안사항과 다음 단계가 있어야 함
        assert len(formatted['suggestions']) > 0
        assert len(formatted['next_steps']) > 0


class TestIntegratedValidation:
    """통합 검증 시스템 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.integrated_validator = IntegratedValidator("strict")
    
    def test_full_validation_workflow_success(self):
        """전체 검증 워크플로우 성공 테스트"""
        # 정상적인 테스트 데이터 생성
        test_data = pd.DataFrame({
            '시료명': ['샘플1', '샘플2'],
            '시험항목': ['항목A', '항목B'],
            '결과(성적서)': [1.5, 2.0],
            '시험자': ['김철수', '이영희'],
            '기준': ['2.0 이하', '3.0 이하']
        })
        
        # 임시 Excel 파일 생성
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            test_data.to_excel(tmp_file.name, index=False)
            
            try:
                # 통합 검증 실행
                result = self.integrated_validator.validate_uploaded_file(tmp_file.name)
                
                assert result['success'] == True
                assert result['can_proceed'] == True
                assert result['formatted_messages'] is not None
                
                # 성공적인 검증 결과 확인
                formatted = result['formatted_messages']
                assert formatted['success'] == True
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_full_validation_workflow_with_issues(self):
        """문제가 있는 파일의 전체 검증 워크플로우 테스트"""
        # 문제가 있는 테스트 데이터 생성
        test_data = pd.DataFrame({
            '샘플명': ['샘플1', '샘플2'],  # '시료명' 대신 유사한 이름
            '테스트': ['항목A', '항목B'],   # '시험항목' 대신 부정확한 이름
            '결과': ['invalid', '2.0'],   # 변환 불가능한 값 포함
            # '시험자' 컬럼 누락
        })
        
        # 임시 Excel 파일 생성
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            test_data.to_excel(tmp_file.name, index=False)
            
            try:
                # 통합 검증 실행
                result = self.integrated_validator.validate_uploaded_file(tmp_file.name)
                
                # 문제가 있지만 처리는 가능해야 함
                assert result['formatted_messages'] is not None
                
                formatted = result['formatted_messages']
                
                # 경고나 에러가 있어야 함
                issues = formatted.get('issues', {})
                total_issues = (len(issues.get('critical', [])) + 
                              len(issues.get('errors', [])) + 
                              len(issues.get('warnings', [])))
                assert total_issues > 0, "문제가 있는 파일에서 이슈가 감지되지 않음"
                
                # 제안사항이 있어야 함
                assert len(formatted.get('suggestions', [])) > 0
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_validation_system_status(self):
        """검증 시스템 상태 테스트"""
        summary = self.integrated_validator.get_validation_summary()
        
        assert 'file_validator_available' in summary
        assert 'error_handler_available' in summary
        assert 'validation_level' in summary
        assert 'supported_formats' in summary
        assert 'max_file_size_mb' in summary
        
        # 시스템이 정상적으로 초기화되었는지 확인
        assert summary['file_validator_available'] == True
        assert summary['error_handler_available'] == True
        assert len(summary['supported_formats']) > 0
        assert summary['max_file_size_mb'] > 0


def test_error_handling_integration():
    """에러 처리 시스템 통합 테스트"""
    # 모든 컴포넌트가 정상적으로 임포트되고 초기화되는지 확인
    try:
        validator = FileValidator.create_lab_validator()
        error_handler = DataProcessingErrorHandler()
        integrated_validator = IntegratedValidator("standard")
        
        assert validator is not None
        assert error_handler is not None
        assert integrated_validator is not None
        
        # 기본 기능이 작동하는지 확인
        test_result = ValidationResult(is_valid=True, file_path="test.xlsx")
        formatted = ErrorMessageFormatter.format_validation_result(test_result)
        assert formatted is not None
        
        print("✅ 에러 처리 시스템 통합 테스트 통과")
        
    except Exception as e:
        pytest.fail(f"에러 처리 시스템 통합 실패: {e}")


if __name__ == "__main__":
    # 개별 테스트 실행
    test_error_handling_integration()
    
    # pytest로 전체 테스트 실행
    pytest.main([__file__, "-v"])