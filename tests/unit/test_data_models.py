#!/usr/bin/env python3
"""
데이터 모델 및 프로세서 종합 테스트
"""

import unittest
from datetime import datetime
from data_models import TestResult, Standard, ProjectSummary, parse_datetime, clean_numeric_value
from data_processor import DataProcessor
import pandas as pd
import numpy as np

class TestDataModels(unittest.TestCase):
    """데이터 모델 테스트"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.test_result = TestResult(
            no=1,
            sample_name='냉수탱크',
            analysis_number='25A00009-001',
            test_item='아크릴로나이트릴',
            test_unit='mg/L',
            result_report='불검출',
            tester_input_value=0,
            standard_excess='적합',
            tester='김화빈',
            test_standard='EPA 524.2',
            standard_criteria='0.0006 mg/L 이하',
            text_digits='',
            processing_method='',
            result_display_digits=2,
            result_type='',
            tester_group='',
            input_datetime=datetime.now(),
            approval_request='N',
            approval_request_datetime=None,
            test_result_display_limit=0,
            quantitative_limit_processing='',
            test_equipment='',
            judgment_status='N',
            report_output='N',
            kolas_status='N',
            test_lab_group='',
            test_set=''
        )
    
    def test_test_result_creation(self):
        """TestResult 생성 테스트"""
        self.assertEqual(self.test_result.sample_name, '냉수탱크')
        self.assertEqual(self.test_result.test_item, '아크릴로나이트릴')
        self.assertFalse(self.test_result.is_non_conforming())
        self.assertEqual(self.test_result.get_display_result(), '불검출')
        self.assertIsNone(self.test_result.get_numeric_result())
    
    def test_non_conforming_result(self):
        """부적합 결과 테스트"""
        non_conforming_result = TestResult(
            no=2,
            sample_name='온수탱크',
            analysis_number='25A00009-002',
            test_item='아크릴로나이트릴',
            test_unit='mg/L',
            result_report=0.0007,
            tester_input_value=0.0007,
            standard_excess='부적합',
            tester='김화빈',
            test_standard='EPA 524.2',
            standard_criteria='0.0006 mg/L 이하',
            text_digits='',
            processing_method='',
            result_display_digits=4,
            result_type='',
            tester_group='',
            input_datetime=datetime.now(),
            approval_request='N',
            approval_request_datetime=None,
            test_result_display_limit=0,
            quantitative_limit_processing='',
            test_equipment='',
            judgment_status='N',
            report_output='N',
            kolas_status='N',
            test_lab_group='',
            test_set=''
        )
        
        self.assertTrue(non_conforming_result.is_non_conforming())
        self.assertEqual(non_conforming_result.get_numeric_result(), 0.0007)
        self.assertEqual(non_conforming_result.get_display_result(), '0.0007')
    
    def test_standard_creation(self):
        """Standard 생성 테스트"""
        standard = Standard.from_test_result(self.test_result)
        self.assertEqual(standard.test_item, '아크릴로나이트릴')
        self.assertEqual(standard.unit, 'mg/L')
        self.assertEqual(standard.limit_value, 0.0006)
        self.assertEqual(standard.limit_text, '0.0006 mg/L 이하')
    
    def test_project_summary(self):
        """ProjectSummary 생성 테스트"""
        # 테스트 데이터 생성
        test_results = [
            self.test_result,  # 적합
            TestResult(
                no=2, sample_name='온수탱크', analysis_number='25A00009-002',
                test_item='아크릴로나이트릴', test_unit='mg/L', result_report=0.0007,
                tester_input_value=0.0007, standard_excess='부적합', tester='김화빈',
                test_standard='EPA 524.2', standard_criteria='0.0006 mg/L 이하',
                text_digits='', processing_method='', result_display_digits=4,
                result_type='', tester_group='', input_datetime=datetime.now(),
                approval_request='N', approval_request_datetime=None,
                test_result_display_limit=0, quantitative_limit_processing='',
                test_equipment='', judgment_status='N', report_output='N',
                kolas_status='N', test_lab_group='', test_set=''
            )  # 부적합
        ]
        
        summary = ProjectSummary.from_test_results('TEST_PROJECT', test_results)
        
        self.assertEqual(summary.project_name, 'TEST_PROJECT')
        self.assertEqual(summary.total_samples, 2)
        self.assertEqual(summary.total_tests, 2)
        self.assertEqual(summary.violation_tests, 1)
        self.assertEqual(summary.violation_samples, 1)
        self.assertEqual(summary.violation_rate, 50.0)
        self.assertIn('아크릴로나이트릴', summary.test_items_summary)
    
    def test_utility_functions(self):
        """유틸리티 함수 테스트"""
        # parse_datetime 테스트
        dt = parse_datetime('2025-01-23 09:56')
        self.assertIsInstance(dt, datetime)
        self.assertEqual(dt.year, 2025)
        
        # clean_numeric_value 테스트
        self.assertEqual(clean_numeric_value('123'), 123)
        self.assertEqual(clean_numeric_value('123.45'), 123.45)
        self.assertEqual(clean_numeric_value(''), 0)
        self.assertEqual(clean_numeric_value(np.nan), 0)

class TestDataProcessor(unittest.TestCase):
    """데이터 프로세서 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.processor = DataProcessor()
        
        # 샘플 데이터 생성
        self.sample_data = {
            'No.': [1, 2, 3],
            '시료명': ['냉수탱크', '온수탱크', '유량센서'],
            '분석번호': ['25A00009-001', '25A00009-002', '25A00009-003'],
            '시험항목': ['아크릴로나이트릴', '아크릴로나이트릴', 'N-니트로조다이메틸아민'],
            '시험단위': ['mg/L', 'mg/L', 'ng/L'],
            '결과(성적서)': ['불검출', '0.0007', '2.5'],
            '시험자입력값': [0, 0.0007, 2.5],
            '기준대비 초과여부\n(성적서)': ['적합', '부적합', '부적합'],
            '시험자': ['김화빈', '김화빈', '이현풍'],
            '시험표준': ['EPA 524.2', 'EPA 524.2', 'House Method'],
            '기준 텍스트': ['0.0006 mg/L 이하', '0.0006 mg/L 이하', '2.0 ng/L 이하'],
            '입력일시': ['2025-01-23 09:56', '2025-01-23 09:56', '2025-01-23 09:56']
        }
        
        self.df = pd.DataFrame(self.sample_data)
    
    def test_data_validation(self):
        """데이터 검증 테스트"""
        validation = self.processor.validate_data_structure(self.df)
        self.assertTrue(validation['is_valid'])
        self.assertEqual(len(validation['errors']), 0)
        self.assertEqual(validation['total_rows'], 3)
    
    def test_row_conversion(self):
        """행 변환 테스트"""
        test_results = []
        for _, row in self.df.iterrows():
            result = self.processor._row_to_test_result(row)
            if result:
                test_results.append(result)
        
        self.assertEqual(len(test_results), 3)
        self.assertEqual(test_results[0].sample_name, '냉수탱크')
        self.assertEqual(test_results[1].standard_excess, '부적합')
        self.assertTrue(test_results[1].is_non_conforming())
    
    def test_filtering_functions(self):
        """필터링 함수 테스트"""
        test_results = []
        for _, row in self.df.iterrows():
            result = self.processor._row_to_test_result(row)
            if result:
                test_results.append(result)
        
        # 부적합 필터링
        non_conforming = self.processor.filter_non_conforming(test_results)
        self.assertEqual(len(non_conforming), 2)
        
        # 시험항목별 필터링
        acrylonitrile_results = self.processor.filter_by_test_item(test_results, '아크릴로나이트릴')
        self.assertEqual(len(acrylonitrile_results), 2)
        
        # 시험자별 필터링
        kim_results = self.processor.filter_by_tester(test_results, '김화빈')
        self.assertEqual(len(kim_results), 2)
    
    def test_summary_functions(self):
        """요약 함수 테스트"""
        test_results = []
        for _, row in self.df.iterrows():
            result = self.processor._row_to_test_result(row)
            if result:
                test_results.append(result)
        
        # 프로젝트 요약
        summary = self.processor.get_project_summary('TEST_PROJECT', test_results)
        self.assertEqual(summary.total_tests, 3)
        self.assertEqual(summary.violation_tests, 2)
        self.assertAlmostEqual(summary.violation_rate, 66.7, places=1)
        
        # 기준값 정보
        standards = self.processor.get_standards_info(test_results)
        self.assertGreater(len(standards), 0)
        
        # 목록 함수
        test_items = self.processor.get_test_items_list(test_results)
        testers = self.processor.get_testers_list(test_results)
        self.assertEqual(len(test_items), 2)  # 아크릴로나이트릴, N-니트로조다이메틸아민
        self.assertEqual(len(testers), 2)     # 김화빈, 이현풍
    
    def test_export_to_dataframe(self):
        """DataFrame 내보내기 테스트"""
        test_results = []
        for _, row in self.df.iterrows():
            result = self.processor._row_to_test_result(row)
            if result:
                test_results.append(result)
        
        exported_df = self.processor.export_to_dataframe(test_results)
        self.assertEqual(len(exported_df), 3)
        self.assertIn('시료명', exported_df.columns)
        self.assertIn('시험항목', exported_df.columns)
        self.assertIn('판정', exported_df.columns)

if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)