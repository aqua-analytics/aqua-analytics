"""
실험실 데이터 처리 엔진
실제 엑셀 파일 구조에 맞춘 데이터 파싱 및 분석
성능 최적화 적용
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
from src.core.data_models import TestResult, Standard, ProjectSummary, parse_datetime, clean_numeric_value
from src.utils.performance_optimizer import optimize_performance, cache_result, global_optimizer

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """실험실 데이터 처리 클래스"""
    
    # 실제 엑셀 컬럼명 매핑 (줄바꿈 포함)
    COLUMN_MAPPING = {
        'No.': 'no',
        '시료명': 'sample_name',
        '분석번호': 'analysis_number',
        '시험항목': 'test_item',
        '시험단위': 'test_unit',
        '결과(성적서)': 'result_report',
        '시험자입력값': 'tester_input_value',
        '기준대비 초과여부 (성적서)': 'standard_excess',
        '기준대비 초과여부\n(성적서)': 'standard_excess',  # 줄바꿈 버전
        '시험자': 'tester',
        '시험표준': 'test_standard',
        '기준': 'standard_criteria',
        '기준 텍스트': 'standard_criteria',  # 실제 컬럼명
        '텍스트 자리수': 'text_digits',
        '자리수\n처리방식': 'text_digits',  # 줄바꿈 버전
        '처리방식': 'processing_method',
        '시험결과 표시자리수': 'result_display_digits',
        '시험결과\n표시자리수': 'result_display_digits',  # 줄바꿈 버전
        '결과유형': 'result_type',
        '시험자그룹': 'tester_group',
        '입력일시': 'input_datetime',
        '승인요청여부': 'approval_request',
        '승인요청일시': 'approval_request_datetime',
        '시험결과 표시한계 (정량한계)(성적서)': 'test_result_display_limit',
        '시험결과 표시한계\n(정량한계)(성적서)': 'test_result_display_limit',  # 줄바꿈 버전
        '정량한계미만처리 (성적서)': 'quantitative_limit_processing',
        '정량한계미만처리\n(성적서)': 'quantitative_limit_processing',  # 줄바꿈 버전
        '시험기기 (RDMS)': 'test_equipment',
        '시험기기\n(RDMS)': 'test_equipment',  # 줄바꿈 버전
        '판정 여부': 'judgment_status',
        '성적서 출력여부': 'report_output',
        '성적서\n출력여부': 'report_output',  # 줄바꿈 버전
        'KOLAS 여부': 'kolas_status',
        '시험소그룹': 'test_lab_group',
        '시험Set': 'test_set'
    }
    
    def __init__(self):
        self.standards_cache = {}  # 기준값 캐시
        self.performance_optimizer = global_optimizer
        
    @optimize_performance("parse_excel_file")
    def parse_excel_file(self, file_path: str) -> List[TestResult]:
        """엑셀 파일을 파싱하여 TestResult 리스트 반환 (성능 최적화 적용)"""
        try:
            logger.info(f"파일 파싱 시작: {file_path}")
            
            # 파일 크기 확인
            file_size = Path(file_path).stat().st_size / 1024 / 1024  # MB
            logger.info(f"파일 크기: {file_size:.1f}MB")
            
            # 대용량 파일인 경우 청크 처리
            if file_size > 10:  # 10MB 이상
                logger.info("대용량 파일 감지 - 청크 처리 모드")
                return self._parse_large_file_chunked(file_path)
            
            # 일반 파일 처리
            df = pd.read_excel(file_path, sheet_name=0)
            
            # 메모리 최적화
            df = self.performance_optimizer.optimize_dataframe_memory(df)
            
            logger.info(f"데이터 행 수: {len(df)}")
            logger.info(f"컬럼 수: {len(df.columns)}")
            logger.info(f"컬럼명: {list(df.columns)}")
            
            # 데이터 검증
            validation_result = self.validate_data_structure(df)
            if not validation_result['is_valid']:
                raise ValueError(f"데이터 구조 검증 실패: {validation_result['errors']}")
            
            # TestResult 객체 리스트 생성 (벡터화 처리)
            test_results = self._convert_dataframe_to_test_results(df)
            
            logger.info(f"파싱 완료: {len(test_results)}개 결과")
            return test_results
            
        except Exception as e:
            logger.error(f"파일 파싱 오류: {e}")
            raise
    
    def _parse_large_file_chunked(self, file_path: str) -> List[TestResult]:
        """대용량 파일 청크 처리"""
        def process_chunk(chunk_df):
            # 메모리 최적화
            chunk_df = self.performance_optimizer.optimize_dataframe_memory(chunk_df)
            return self._convert_dataframe_to_test_results(chunk_df)
        
        def combine_results(results_list):
            combined = []
            for results in results_list:
                combined.extend(results)
            return combined
        
        return self.performance_optimizer.chunked_processor.process_file_chunks(
            file_path, process_chunk, combine_results
        )
    
    @optimize_performance("convert_dataframe_to_test_results")
    def _convert_dataframe_to_test_results(self, df: pd.DataFrame) -> List[TestResult]:
        """DataFrame을 TestResult 리스트로 변환 (벡터화 처리)"""
        test_results = []
        
        # 병렬 처리를 위한 청크 분할
        if len(df) > 1000:
            def process_chunk(chunk_df):
                chunk_results = []
                for _, row in chunk_df.iterrows():
                    try:
                        test_result = self._row_to_test_result(row)
                        if test_result:
                            chunk_results.append(test_result)
                    except Exception as e:
                        logger.warning(f"행 변환 실패: {e}")
                        continue
                return chunk_results
            
            def combine_results(results_list):
                combined = []
                for results in results_list:
                    combined.extend(results)
                return combined
            
            test_results = self.performance_optimizer.chunked_processor.process_dataframe_chunks(
                df, process_chunk, combine_results
            )
        else:
            # 소량 데이터는 순차 처리
            for index, row in df.iterrows():
                try:
                    test_result = self._row_to_test_result(row)
                    if test_result:
                        test_results.append(test_result)
                except Exception as e:
                    logger.warning(f"행 {index} 파싱 실패: {e}")
                    continue
        
        return test_results
    
    def validate_data_structure(self, df: pd.DataFrame) -> Dict:
        """데이터 구조 검증 (유연한 컬럼명 매칭)"""
        errors = []
        warnings = []
        
        # 실제 컬럼명 로깅
        logger.info(f"업로드된 파일의 컬럼명: {list(df.columns)}")
        
        # 필수 컬럼 패턴 정의 (유연한 매칭)
        required_patterns = {
            '시료명': ['시료명', '시료', 'sample', 'Sample Name', '샘플명', '샘플'],
            '시험항목': ['시험항목', '항목', '시험', 'test', 'Test Item', '분석항목', '검사항목'],
            '결과': ['결과(성적서)', '결과', 'result', 'Result', '측정값', '분석결과', '시험결과'],
            '시험자': ['시험자', '분석자', '검사자', 'tester', 'Tester', '담당자', '실험자']
        }
        
        # 컬럼 매칭 결과
        matched_columns = {}
        
        for required_key, patterns in required_patterns.items():
            matched = False
            for pattern in patterns:
                # 대소문자 구분 없이 부분 매칭
                matching_cols = [col for col in df.columns if pattern.lower() in col.lower()]
                if matching_cols:
                    matched_columns[required_key] = matching_cols[0]  # 첫 번째 매칭 컬럼 사용
                    matched = True
                    logger.info(f"'{required_key}' 매칭됨: {matching_cols[0]}")
                    break
            
            if not matched:
                # 정확히 일치하는 컬럼 찾기
                exact_matches = [col for col in df.columns if col in patterns]
                if exact_matches:
                    matched_columns[required_key] = exact_matches[0]
                    matched = True
                    logger.info(f"'{required_key}' 정확 매칭됨: {exact_matches[0]}")
        
        # 누락된 필수 컬럼 확인
        missing_required = [key for key in required_patterns.keys() if key not in matched_columns]
        
        if missing_required:
            # 사용 가능한 컬럼 제안
            available_cols = list(df.columns)[:10]  # 처음 10개 컬럼만 표시
            errors.append(f"필수 컬럼을 찾을 수 없습니다: {missing_required}")
            errors.append(f"사용 가능한 컬럼: {available_cols}")
            
            # 유사한 컬럼명 제안
            suggestions = {}
            for missing in missing_required:
                patterns = required_patterns[missing]
                similar_cols = []
                for col in df.columns:
                    for pattern in patterns:
                        if pattern.lower() in col.lower() or col.lower() in pattern.lower():
                            similar_cols.append(col)
                if similar_cols:
                    suggestions[missing] = similar_cols[:3]  # 최대 3개 제안
            
            if suggestions:
                errors.append(f"유사한 컬럼명 제안: {suggestions}")
        
        # 데이터 행 수 확인
        if len(df) == 0:
            errors.append("데이터가 없습니다")
        
        # 빈 행 확인
        empty_rows = df.isnull().all(axis=1).sum()
        if empty_rows > len(df) * 0.5:  # 50% 이상이 빈 행인 경우
            warnings.append(f"빈 행이 많습니다: {empty_rows}/{len(df)}")
        
        # 데이터 품질 확인
        if len(missing_required) == 0:  # 필수 컬럼이 모두 있는 경우
            for key, col_name in matched_columns.items():
                null_count = df[col_name].isnull().sum()
                if null_count > len(df) * 0.3:  # 30% 이상이 null인 경우
                    warnings.append(f"'{col_name}' 컬럼에 빈 값이 많습니다: {null_count}/{len(df)}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_rows': len(df),
            'empty_rows': empty_rows,
            'matched_columns': matched_columns,
            'available_columns': list(df.columns)
        }
    
    def _row_to_test_result(self, row: pd.Series) -> Optional[TestResult]:
        """DataFrame 행을 TestResult 객체로 변환 (유연한 컬럼명 매칭)"""
        try:
            # 컬럼명 매칭 함수
            def find_column_value(row, *possible_names):
                """여러 가능한 컬럼명 중에서 값을 찾아 반환"""
                for name in possible_names:
                    if name in row.index and not pd.isna(row.get(name)):
                        return row.get(name)
                    # 부분 매칭도 시도
                    for col in row.index:
                        if name.lower() in col.lower():
                            return row.get(col)
                return None
            
            # 필수 필드 확인 (유연한 매칭)
            sample_name = find_column_value(row, '시료명', '시료', 'sample', 'Sample Name', '샘플명', '샘플')
            test_item = find_column_value(row, '시험항목', '항목', '시험', 'test', 'Test Item', '분석항목', '검사항목')
            
            if not sample_name or not test_item:
                return None
            
            return TestResult(
                no=clean_numeric_value(find_column_value(row, 'No.', 'no', '번호', 'number') or 0),
                sample_name=str(sample_name or '').strip(),
                analysis_number=str(find_column_value(row, '분석번호', '분석 번호', 'analysis', 'Analysis Number') or '').strip(),
                test_item=str(test_item or '').strip(),
                test_unit=str(find_column_value(row, '시험단위', '단위', 'unit', 'Unit') or '').strip(),
                result_report=find_column_value(row, '결과(성적서)', '결과', 'result', 'Result', '측정값', '분석결과', '시험결과') or '',
                tester_input_value=clean_numeric_value(find_column_value(row, '시험자입력값', '입력값', 'input', 'Input Value') or 0),
                standard_excess=str(find_column_value(row, '기준대비 초과여부\n(성적서)', '기준대비 초과여부 (성적서)', '기준대비 초과여부', '판정', '적합성', 'judgment') or '-').strip(),
                tester=str(find_column_value(row, '시험자', '분석자', '검사자', 'tester', 'Tester', '담당자', '실험자') or '').strip(),
                test_standard=str(find_column_value(row, '시험표준', '표준', 'standard', 'Standard', '방법') or '').strip(),
                standard_criteria=str(find_column_value(row, '기준 텍스트', '기준', 'criteria', 'Criteria', '허용기준') or '').strip(),
                text_digits=str(find_column_value(row, '자리수\n처리방식', '텍스트 자리수', '자리수', 'digits') or '').strip(),
                processing_method=str(find_column_value(row, '처리방식', '방식', 'method', 'Method') or '').strip(),
                result_display_digits=clean_numeric_value(find_column_value(row, '시험결과\n표시자리수', '시험결과 표시자리수', '표시자리수') or 2),
                result_type=str(find_column_value(row, '결과유형', '유형', 'type', 'Type') or '').strip(),
                tester_group=str(find_column_value(row, '시험자그룹', '그룹', 'group', 'Group') or '').strip(),
                input_datetime=parse_datetime(find_column_value(row, '입력일시', '일시', 'datetime', 'Date Time', '날짜')),
                approval_request=str(find_column_value(row, '승인요청여부', '승인요청', 'approval', 'Approval') or 'N').strip(),
                approval_request_datetime=parse_datetime(find_column_value(row, '승인요청일시', '승인일시')),
                test_result_display_limit=clean_numeric_value(find_column_value(row, '시험결과 표시한계\n(정량한계)(성적서)', '시험결과 표시한계 (정량한계)(성적서)', '표시한계', '정량한계') or 0),
                quantitative_limit_processing=str(find_column_value(row, '정량한계미만처리\n(성적서)', '정량한계미만처리 (성적서)', '정량한계미만처리') or '').strip(),
                test_equipment=str(find_column_value(row, '시험기기\n(RDMS)', '시험기기 (RDMS)', '시험기기', '기기', 'equipment') or '').strip(),
                judgment_status=str(find_column_value(row, '판정 여부', '판정여부', '판정', 'judgment') or 'N').strip(),
                report_output=str(find_column_value(row, '성적서\n출력여부', '성적서 출력여부', '출력여부', 'output') or 'N').strip(),
                kolas_status=str(find_column_value(row, 'KOLAS 여부', 'KOLAS', 'kolas') or 'N').strip(),
                test_lab_group=str(find_column_value(row, '시험소그룹', '시험소', 'lab', 'Lab') or '').strip(),
                test_set=str(find_column_value(row, '시험Set', '시험세트', 'set', 'Set') or '').strip()
            )
        except Exception as e:
            logger.warning(f"행 변환 실패: {e}")
            return None
    
    @cache_result(ttl=1800)  # 30분 캐시
    @optimize_performance("get_project_summary")
    def get_project_summary(self, project_name: str, test_results: List[TestResult]) -> ProjectSummary:
        """프로젝트 요약 통계 생성 (캐시 적용)"""
        return ProjectSummary.from_test_results(project_name, test_results)
    
    def get_standards_info(self, test_results: List[TestResult]) -> Dict[str, Standard]:
        """시험항목별 기준값 정보 추출"""
        standards = {}
        
        for result in test_results:
            if result.test_item not in standards and result.standard_criteria:
                try:
                    standard = Standard.from_test_result(result)
                    standards[result.test_item] = standard
                except Exception as e:
                    logger.warning(f"기준값 추출 실패 ({result.test_item}): {e}")
        
        return standards
    
    def filter_by_test_item(self, test_results: List[TestResult], test_item: str) -> List[TestResult]:
        """시험항목별 필터링"""
        return [result for result in test_results if result.test_item == test_item]
    
    def filter_by_tester(self, test_results: List[TestResult], tester: str) -> List[TestResult]:
        """시험자별 필터링"""
        return [result for result in test_results if result.tester == tester]
    
    def filter_non_conforming(self, test_results: List[TestResult]) -> List[TestResult]:
        """부적합 항목만 필터링"""
        return [result for result in test_results if result.is_non_conforming()]
    
    def get_test_items_list(self, test_results: List[TestResult]) -> List[str]:
        """시험항목 목록 반환"""
        return list(set(result.test_item for result in test_results))
    
    def get_testers_list(self, test_results: List[TestResult]) -> List[str]:
        """시험자 목록 반환"""
        return list(set(result.tester for result in test_results if result.tester))
    
    def process_excel_data(self, df: pd.DataFrame) -> List[TestResult]:
        """DataFrame을 처리하여 TestResult 리스트 반환 (app.py에서 호출되는 메서드)"""
        try:
            logger.info(f"DataFrame 처리 시작: {len(df)}행, {len(df.columns)}컬럼")
            
            # 메모리 최적화
            df = self.performance_optimizer.optimize_dataframe_memory(df)
            
            # 데이터 검증
            validation_result = self.validate_data_structure(df)
            if not validation_result['is_valid']:
                raise ValueError(f"데이터 구조 검증 실패: {validation_result['errors']}")
            
            # TestResult 객체 리스트 생성
            test_results = self._convert_dataframe_to_test_results(df)
            
            logger.info(f"DataFrame 처리 완료: {len(test_results)}개 결과")
            return test_results
            
        except Exception as e:
            logger.error(f"DataFrame 처리 오류: {e}")
            raise

    @optimize_performance("export_to_dataframe")
    def export_to_dataframe(self, test_results: List[TestResult]) -> pd.DataFrame:
        """TestResult 리스트를 DataFrame으로 변환 (성능 최적화)"""
        if not test_results:
            return pd.DataFrame()
        
        # 벡터화된 데이터 변환
        data = {
            '시료명': [result.sample_name for result in test_results],
            '분석번호': [result.analysis_number for result in test_results],
            '시험항목': [result.test_item for result in test_results],
            '시험단위': [result.test_unit for result in test_results],
            '결과': [result.get_display_result() for result in test_results],
            '판정': [result.standard_excess for result in test_results],
            '시험자': [result.tester for result in test_results],
            '입력일시': [
                result.input_datetime.strftime('%Y-%m-%d %H:%M') if result.input_datetime and hasattr(result.input_datetime, 'strftime') else str(result.input_datetime) if result.input_datetime else ''
                for result in test_results
            ],
            '기준': [result.standard_criteria for result in test_results]
        }
        
        df = pd.DataFrame(data)
        
        # 메모리 최적화
        df = self.performance_optimizer.optimize_dataframe_memory(df)
        
        return df

# 사용 예시 및 테스트 함수
def test_data_processor():
    """데이터 프로세서 테스트"""
    processor = DataProcessor()
    
    # 샘플 데이터 생성 (실제 사용 시에는 엑셀 파일 경로 사용)
    sample_data = {
        'No.': [1, 2, 3],
        '시료명': ['냉수탱크', '온수탱크', '유량센서'],
        '분석번호': ['25A00009-001', '25A00009-002', '25A00009-003'],
        '시험항목': ['아크릴로나이트릴', '아크릴로나이트릴', 'N-니트로조다이메틸아민'],
        '시험단위': ['mg/L', 'mg/L', 'ng/L'],
        '결과(성적서)': ['불검출', '0.0007', '2.5'],
        '시험자입력값': [0, 0.0007, 2.5],
        '기준대비 초과여부 (성적서)': ['적합', '부적합', '부적합'],
        '시험자': ['김화빈', '김화빈', '이현풍'],
        '시험표준': ['EPA 524.2', 'EPA 524.2', 'House Method'],
        '기준': ['0.0006 mg/L 이하', '0.0006 mg/L 이하', '2.0 ng/L 이하'],
        '입력일시': ['2025-01-23 09:56', '2025-01-23 09:56', '2025-01-23 09:56']
    }
    
    df = pd.DataFrame(sample_data)
    
    # 검증 테스트
    validation = processor.validate_data_structure(df)
    print(f"검증 결과: {validation}")
    
    # 파싱 테스트
    test_results = []
    for _, row in df.iterrows():
        result = processor._row_to_test_result(row)
        if result:
            test_results.append(result)
    
    print(f"파싱된 결과 수: {len(test_results)}")
    
    # 통계 테스트
    summary = processor.get_project_summary("TEST_PROJECT", test_results)
    print(f"통계: 총 {summary.total_tests}건, 부적합 {summary.violation_tests}건 ({summary.violation_rate:.1f}%)")
    
    return test_results

if __name__ == "__main__":
    test_data_processor()