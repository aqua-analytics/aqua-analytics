"""
실험실 분석 데이터 모델 정의
실제 엑셀 데이터 구조에 맞춘 데이터 클래스들
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union
import pandas as pd
import numpy as np

@dataclass
class TestResult:
    """시험 결과 데이터 모델"""
    no: int                                    # No.
    sample_name: str                          # 시료명
    analysis_number: str                      # 분석번호
    test_item: str                           # 시험항목
    test_unit: str                           # 시험단위
    result_report: Union[str, float]         # 결과(성적서) - "불검출" 또는 수치값
    tester_input_value: Union[float, int]    # 시험자입력값
    standard_excess: str                     # 기준대비 초과여부 (-, 적합, 부적합)
    tester: str                              # 시험자
    test_standard: str                       # 시험표준
    standard_criteria: str                   # 기준
    text_digits: str                         # 텍스트 자리수
    processing_method: str                   # 처리방식
    result_display_digits: int               # 시험결과 표시자리수
    result_type: str                         # 결과유형
    tester_group: str                        # 시험자그룹
    input_datetime: datetime                 # 입력일시
    approval_request: str                    # 승인요청여부
    approval_request_datetime: Optional[datetime]  # 승인요청일시
    test_result_display_limit: Union[float, int]   # 시험결과 표시한계
    quantitative_limit_processing: str       # 정량한계미만처리
    test_equipment: str                      # 시험기기
    judgment_status: str                     # 판정 여부
    report_output: str                       # 성적서 출력여부
    kolas_status: str                        # KOLAS 여부
    test_lab_group: str                      # 시험소그룹
    test_set: str                           # 시험Set

    def is_non_conforming(self) -> bool:
        """부적합 여부 판단"""
        return self.standard_excess == "부적합"
    
    def get_numeric_result(self) -> Optional[float]:
        """수치 결과값 반환 (불검출인 경우 None)"""
        if isinstance(self.result_report, str) and "불검출" in self.result_report:
            return None
        try:
            return float(self.result_report)
        except (ValueError, TypeError):
            return None
    
    def get_display_result(self) -> str:
        """화면 표시용 결과값"""
        if isinstance(self.result_report, str) and "불검출" in self.result_report:
            return "불검출"
        return str(self.result_report)

@dataclass
class Standard:
    """시험 기준값 정보"""
    test_item: str           # 시험항목명
    unit: str                # 단위
    limit_value: float       # 기준값
    limit_text: str          # 기준 텍스트 (예: "0.0006 mg/L 이하")
    regulation: str          # 관련 규정
    test_method: str         # 시험방법
    
    @classmethod
    def from_test_result(cls, test_result: TestResult) -> 'Standard':
        """TestResult에서 Standard 정보 추출"""
        # 기준 텍스트에서 수치값 추출
        limit_value = cls._extract_limit_value(test_result.standard_criteria)
        
        return cls(
            test_item=test_result.test_item,
            unit=test_result.test_unit,
            limit_value=limit_value,
            limit_text=test_result.standard_criteria,
            regulation=test_result.test_standard,
            test_method=test_result.test_standard
        )
    
    @staticmethod
    def _extract_limit_value(criteria_text: str) -> float:
        """기준 텍스트에서 수치값 추출"""
        if not criteria_text or criteria_text.strip() == "":
            return 0.0
        
        # "0.0006 mg/L 이하" 형태에서 숫자 추출
        import re
        numbers = re.findall(r'\d+\.?\d*', criteria_text)
        if numbers:
            return float(numbers[0])
        return 0.0

@dataclass
class ProjectSummary:
    """프로젝트 품질관리 요약"""
    project_name: str                   # 프로젝트명
    analysis_period: str                # 분석 기간
    total_samples: int                  # 총 시료 개수
    total_tests: int                    # 총 시험 건수
    violation_tests: int                # 부적합 건수
    violation_samples: int              # 부적합 시료 개수
    violation_rate: float               # 부적합 비율(%)
    test_items_summary: dict            # 시험항목별 요약
    sample_summary: dict                # 시료별 요약
    
    @classmethod
    def from_test_results(cls, project_name: str, test_results: list[TestResult]) -> 'ProjectSummary':
        """TestResult 리스트에서 프로젝트 요약 정보 생성"""
        total_tests = len(test_results)
        violation_tests = sum(1 for result in test_results if result.is_non_conforming())
        violation_rate = (violation_tests / total_tests * 100) if total_tests > 0 else 0.0
        
        # 고유 시료 개수 계산
        unique_samples = set(result.sample_name for result in test_results)
        total_samples = len(unique_samples)
        
        # 부적합 시료 개수 계산
        violation_sample_names = set(result.sample_name for result in test_results if result.is_non_conforming())
        violation_samples = len(violation_sample_names)
        
        # 분석 기간 계산
        dates = [result.input_datetime for result in test_results if result.input_datetime and hasattr(result.input_datetime, 'strftime')]
        if dates:
            min_date = min(dates).strftime('%Y.%m.%d')
            max_date = max(dates).strftime('%Y.%m.%d')
            analysis_period = f"{min_date} – {max_date} 분석"
        else:
            analysis_period = "분석 기간 정보 없음"
        
        # 시험항목별 요약
        test_items_summary = {}
        for result in test_results:
            item = result.test_item
            if item not in test_items_summary:
                test_items_summary[item] = {
                    'total': 0,
                    'violation': 0,
                    'rate': 0.0
                }
            test_items_summary[item]['total'] += 1
            if result.is_non_conforming():
                test_items_summary[item]['violation'] += 1
        
        # 비율 계산
        for item_data in test_items_summary.values():
            if item_data['total'] > 0:
                item_data['rate'] = (item_data['violation'] / item_data['total']) * 100
        
        # 시료별 요약
        sample_summary = {}
        for result in test_results:
            sample = result.sample_name
            if sample not in sample_summary:
                sample_summary[sample] = {
                    'total': 0,
                    'violation': 0,
                    'rate': 0.0
                }
            sample_summary[sample]['total'] += 1
            if result.is_non_conforming():
                sample_summary[sample]['violation'] += 1
        
        # 비율 계산
        for sample_data in sample_summary.values():
            if sample_data['total'] > 0:
                sample_data['rate'] = (sample_data['violation'] / sample_data['total']) * 100
        
        return cls(
            project_name=project_name,
            analysis_period=analysis_period,
            total_samples=total_samples,
            total_tests=total_tests,
            violation_tests=violation_tests,
            violation_samples=violation_samples,
            violation_rate=violation_rate,
            test_items_summary=test_items_summary,
            sample_summary=sample_summary
        )

def parse_datetime(date_str) -> Optional[datetime]:
    """날짜 문자열을 datetime 객체로 변환"""
    if not date_str or pd.isna(date_str) or str(date_str).strip() == '':
        return None
    
    # 이미 datetime 객체인 경우
    if isinstance(date_str, datetime):
        return date_str
    
    # 문자열로 변환
    date_str = str(date_str).strip()
    
    try:
        # "2025-01-23 09:56" 형태
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            # "2025-01-23" 형태
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                # "2025/01/23 09:56" 형태
                return datetime.strptime(date_str, "%Y/%m/%d %H:%M")
            except ValueError:
                try:
                    # "2025/01/23" 형태
                    return datetime.strptime(date_str, "%Y/%m/%d")
                except ValueError:
                    return None

def clean_numeric_value(value) -> Union[float, int, None]:
    """수치값 정리 (NaN, 빈 문자열 등 처리)"""
    if pd.isna(value) or value == "" or value == "NaN":
        return 0
    try:
        return float(value) if '.' in str(value) else int(value)
    except (ValueError, TypeError):
        return 0