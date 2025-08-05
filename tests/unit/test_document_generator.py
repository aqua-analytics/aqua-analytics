#!/usr/bin/env python3
"""
DocumentGenerator 단위 테스트
"""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'core'))

from data_models import TestResult, ProjectSummary
from data_processor import DataProcessor
from document_generator import DocumentGenerator
import pandas as pd
from datetime import datetime


class TestDocumentGenerator(unittest.TestCase):
    """DocumentGenerator 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.generator = DocumentGenerator()
        self.test_results = self._create_test_data()
    
    def _create_test_data(self):
        """테스트용 데이터 생성"""
        sample_data = {
            'No.': [1, 2, 3, 4, 5],
            '시료명': ['냉수탱크', '온수탱크', 'Blank', '제품#1', '제품#2'],
            '분석번호': ['25A00009-001', '25A00009-002', '25A00011-003', '25A00089-002', '25A00089-003'],
            '시험항목': ['아크릴로나이트릴', '아크릴로나이트릴', 'N-니트로조다이메틸아민', '아크릴로나이트릴', '아크릴로나이트릴'],
            '시험단위': ['mg/L', 'mg/L', 'ng/L', 'mg/L', 'mg/L'],
            '결과(성적서)': ['불검출', '불검출', '2.29', '0.0007', '0.0004'],
            '시험자입력값': [0, 0, 2.29, 0.0007, 0.0004],
            '기준대비 초과여부 (성적서)': ['적합', '적합', '부적합', '부적합', '적합'],
            '시험자': ['김화빈', '김화빈', '이현풍', '김화빈', '김화빈'],
            '시험표준': ['EPA 524.2', 'EPA 524.2', 'House Method', 'EPA 524.2', 'EPA 524.2'],
            '기준': ['0.0006 mg/L 이하', '0.0006 mg/L 이하', '2.0 ng/L 이하', '0.0006 mg/L 이하', '0.0006 mg/L 이하'],
            '입력일시': ['2025-01-23 09:56'] * 5
        }
        
        df = pd.DataFrame(sample_data)
        processor = DataProcessor()
        
        test_results = []
        for _, row in df.iterrows():
            result = processor._row_to_test_result(row)
            if result:
                test_results.append(result)
        
        return test_results
    
    def test_initialization(self):
        """초기화 테스트"""
        self.assertIsInstance(self.generator, DocumentGenerator)
        self.assertIn('name', self.generator.company_info)
        self.assertEqual(self.generator.company_info['name'], 'COWAY')
        self.assertIsNotNone(self.generator.default_styles)
    
    def test_highlight_violations(self):
        """부적합 항목 하이라이트 테스트"""
        highlighted_results = self.generator.highlight_violations(self.test_results)
        
        # 결과 개수 확인
        self.assertEqual(len(highlighted_results), len(self.test_results))
        
        # 부적합 항목 확인
        violations = [r for r in highlighted_results if r['is_violation']]
        self.assertEqual(len(violations), 2)  # 샘플 데이터에서 2개가 부적합
        
        # 하이라이트 클래스 확인
        for result in highlighted_results:
            if result['is_violation']:
                self.assertEqual(result['highlight_class'], 'violation-highlight')
                self.assertEqual(result['status_class'], 'status-fail')
            else:
                self.assertEqual(result['highlight_class'], 'normal-result')
                self.assertEqual(result['status_class'], 'status-pass')
    
    def test_generate_test_report_html(self):
        """HTML 보고서 생성 테스트"""
        html_content = self.generator.generate_test_report_html(
            test_results=self.test_results,
            project_name="TEST_PROJECT",
            report_metadata={'client_name': '테스트 클라이언트'}
        )
        
        # HTML 기본 구조 확인
        self.assertIn('<!DOCTYPE html>', html_content)
        self.assertIn('<html lang="ko">', html_content)
        self.assertIn('TEST_PROJECT 시험성적서', html_content)
        self.assertIn('테스트 클라이언트', html_content)
        
        # 부적합 항목 하이라이트 확인
        self.assertIn('violation-highlight', html_content)
        self.assertIn('status-fail', html_content)
        
        # 회사 정보 확인
        self.assertIn('COWAY', html_content)
    
    def test_apply_data_binding(self):
        """데이터 바인딩 테스트"""
        template = "안녕하세요 ${client_name}님, 총 ${total_tests}건의 시험이 완료되었습니다."
        
        bound_content = self.generator.apply_data_binding(template, {
            'client_name': '코웨이',
            'total_tests': 5
        })
        
        expected = "안녕하세요 코웨이님, 총 5건의 시험이 완료되었습니다."
        self.assertEqual(bound_content, expected)
        
        # 이중 중괄호 테스트
        template2 = "프로젝트: {{project_name}}, 결과: {{result}}"
        bound_content2 = self.generator.apply_data_binding(template2, {
            'project_name': 'TEST',
            'result': 'SUCCESS'
        })
        
        expected2 = "프로젝트: TEST, 결과: SUCCESS"
        self.assertEqual(bound_content2, expected2)
    
    def test_save_report_file(self):
        """파일 저장 테스트"""
        test_content = "<html><body>Test Report</body></html>"
        filename = "test_report_unit_test"
        
        saved_path = self.generator.save_report_file(
            content=test_content,
            filename=filename,
            output_dir="test_reports"
        )
        
        # 파일 경로 확인
        self.assertTrue(saved_path.endswith('.html'))
        self.assertIn(filename, saved_path)
        
        # 파일 존재 확인
        self.assertTrue(os.path.exists(saved_path))
        
        # 파일 내용 확인
        with open(saved_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertEqual(content, test_content)
        
        # 테스트 파일 정리
        os.remove(saved_path)
        if os.path.exists("test_reports") and not os.listdir("test_reports"):
            os.rmdir("test_reports")
    
    def test_calculate_excess_ratio(self):
        """초과 배수 계산 테스트"""
        # 부적합 항목 찾기
        violation_result = None
        for result in self.test_results:
            if result.is_non_conforming():
                violation_result = result
                break
        
        self.assertIsNotNone(violation_result)
        
        # 초과 배수 계산
        excess_ratio = self.generator._calculate_excess_ratio(violation_result)
        self.assertIsInstance(excess_ratio, float)
        self.assertGreater(excess_ratio, 1.0)  # 부적합이므로 1보다 커야 함
    
    def test_determine_risk_level(self):
        """위험도 결정 테스트"""
        # 다양한 초과 배수에 대한 위험도 테스트
        self.assertEqual(self.generator._determine_risk_level(0.5), 'SAFE')
        self.assertEqual(self.generator._determine_risk_level(1.5), 'LOW')
        self.assertEqual(self.generator._determine_risk_level(3.0), 'MEDIUM')
        self.assertEqual(self.generator._determine_risk_level(6.0), 'HIGH')
    
    def test_normalize_status(self):
        """상태값 정규화 테스트"""
        self.assertEqual(self.generator._normalize_status('부적합'), '부적합')
        self.assertEqual(self.generator._normalize_status('적합'), '적합')
        self.assertEqual(self.generator._normalize_status('FAIL'), '부적합')
        self.assertEqual(self.generator._normalize_status('PASS'), '적합')
        self.assertEqual(self.generator._normalize_status(''), '적합')  # 기본값
    
    def test_empty_test_results(self):
        """빈 테스트 결과 처리 테스트"""
        with self.assertRaises(ValueError):
            self.generator.generate_test_report_html(
                test_results=[],
                project_name="EMPTY_TEST"
            )
    
    def test_metadata_preparation(self):
        """메타데이터 준비 테스트"""
        metadata = self.generator._prepare_metadata(
            metadata={'custom_field': 'custom_value'},
            test_results=self.test_results,
            project_name="TEST_PROJECT"
        )
        
        # 기본 필드 확인
        self.assertIn('report_title', metadata)
        self.assertIn('report_number', metadata)
        self.assertIn('total_samples', metadata)
        self.assertIn('total_tests', metadata)
        
        # 커스텀 필드 확인
        self.assertEqual(metadata['custom_field'], 'custom_value')
        
        # 계산된 값 확인
        self.assertEqual(metadata['total_tests'], len(self.test_results))


class TestReportPreviewModal(unittest.TestCase):
    """ReportPreviewModal 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'components'))
        from report_preview_modal import ReportPreviewModal
        
        self.modal = ReportPreviewModal()
        self.test_results = self._create_test_data()
    
    def _create_test_data(self):
        """테스트용 데이터 생성"""
        sample_data = {
            'No.': [1, 2, 3],
            '시료명': ['냉수탱크', '온수탱크', 'Blank'],
            '분석번호': ['25A00009-001', '25A00009-002', '25A00011-003'],
            '시험항목': ['아크릴로나이트릴', '아크릴로나이트릴', 'N-니트로조다이메틸아민'],
            '시험단위': ['mg/L', 'mg/L', 'ng/L'],
            '결과(성적서)': ['불검출', '0.0007', '2.29'],
            '시험자입력값': [0, 0.0007, 2.29],
            '기준대비 초과여부 (성적서)': ['적합', '부적합', '부적합'],
            '시험자': ['김화빈', '김화빈', '이현풍'],
            '시험표준': ['EPA 524.2', 'EPA 524.2', 'House Method'],
            '기준': ['0.0006 mg/L 이하', '0.0006 mg/L 이하', '2.0 ng/L 이하'],
            '입력일시': ['2025-01-23 09:56'] * 3
        }
        
        df = pd.DataFrame(sample_data)
        processor = DataProcessor()
        
        test_results = []
        for _, row in df.iterrows():
            result = processor._row_to_test_result(row)
            if result:
                test_results.append(result)
        
        return test_results
    
    def test_modal_initialization(self):
        """모달 초기화 테스트"""
        self.assertIsNotNone(self.modal.modal_id)
        self.assertEqual(self.modal.modal_id, "report-preview-modal")
        self.assertFalse(self.modal.is_open)
    
    def test_render_modal_html(self):
        """모달 HTML 렌더링 테스트"""
        modal_html = self.modal.render_modal_html(
            test_results=self.test_results,
            project_name="TEST_MODAL_PROJECT"
        )
        
        # 모달 기본 구조 확인
        self.assertIn('report-preview-modal', modal_html)
        self.assertIn('시험성적서 미리보기', modal_html)
        self.assertIn('TEST_MODAL_PROJECT', modal_html)
        
        # 버튼 확인
        self.assertIn('printReport()', modal_html)
        self.assertIn('downloadPDF()', modal_html)
        self.assertIn('downloadHTML()', modal_html)
        
        # JavaScript 함수 확인
        self.assertIn('showReportModal', modal_html)
        self.assertIn('closeReportModal', modal_html)
    
    def test_generate_trigger_button(self):
        """트리거 버튼 생성 테스트"""
        button_html = self.modal.generate_modal_trigger_button("테스트 버튼")
        
        self.assertIn('showReportModal()', button_html)
        self.assertIn('테스트 버튼', button_html)
        self.assertIn('bg-blue-600', button_html)
    
    def test_integrate_with_template(self):
        """템플릿 통합 테스트"""
        base_template = """
        <!DOCTYPE html>
        <html>
        <head><title>Base Template</title></head>
        <body>
            <h1>기존 콘텐츠</h1>
        </body>
        </html>
        """
        
        integrated = self.modal.integrate_with_template(
            base_template=base_template,
            test_results=self.test_results,
            project_name="INTEGRATION_TEST"
        )
        
        # 기존 콘텐츠 유지 확인
        self.assertIn('기존 콘텐츠', integrated)
        
        # 모달 추가 확인
        self.assertIn('report-preview-modal', integrated)
        self.assertIn('INTEGRATION_TEST', integrated)


if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)