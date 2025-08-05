"""
상세 정보 패널 시스템 테스트
"""

import pytest
import streamlit as st
from datetime import datetime
from unittest.mock import Mock, patch
from src.components.detail_info_panel import DetailInfoPanel
from src.core.data_models import TestResult, Standard


class TestDetailInfoPanel:
    """상세 정보 패널 테스트 클래스"""
    
    @pytest.fixture
    def sample_test_result(self):
        """테스트용 시험 결과 데이터"""
        return TestResult(
            no=1,
            sample_name="냉수탱크",
            analysis_number="25A00009-001",
            test_item="1-[4-(1-hydroxy-1-methylethyl)phenyl]-ethanone",
            test_unit="μg/L",
            result_report="불검출",
            tester_input_value=0,
            standard_excess="적합",
            tester="김시험",
            test_standard="KS M 3016:2021",
            standard_criteria="2.0 μg/L 이하",
            text_digits="3",
            processing_method="자동",
            result_display_digits=3,
            result_type="정량",
            tester_group="A그룹",
            input_datetime=datetime(2025, 1, 23, 9, 56),
            approval_request="Y",
            approval_request_datetime=datetime(2025, 1, 23, 10, 30),
            test_result_display_limit=0.001,
            quantitative_limit_processing="미만표시",
            test_equipment="LC-MS/MS",
            judgment_status="완료",
            report_output="Y",
            kolas_status="Y",
            test_lab_group="품질관리팀",
            test_set="SET-001"
        )
    
    @pytest.fixture
    def violation_test_result(self):
        """부적합 테스트용 시험 결과 데이터"""
        return TestResult(
            no=2,
            sample_name="온수탱크",
            analysis_number="25A00009-002",
            test_item="아크릴로나이트릴",
            test_unit="mg/L",
            result_report="0.0007",
            tester_input_value=0.0007,
            standard_excess="부적합",
            tester="이시험",
            test_standard="KS M 3018:2021",
            standard_criteria="0.0006 mg/L 이하",
            text_digits="4",
            processing_method="수동",
            result_display_digits=4,
            result_type="정량",
            tester_group="B그룹",
            input_datetime=datetime(2025, 1, 23, 11, 15),
            approval_request="N",
            approval_request_datetime=None,
            test_result_display_limit=0.0001,
            quantitative_limit_processing="미만표시",
            test_equipment="GC-MS",
            judgment_status="대기",
            report_output="N",
            kolas_status="N",
            test_lab_group="분석팀",
            test_set="SET-002"
        )
    
    @pytest.fixture
    def detail_panel(self):
        """상세 정보 패널 인스턴스"""
        return DetailInfoPanel(height=500)
    
    def test_detail_panel_initialization(self, detail_panel):
        """상세 정보 패널 초기화 테스트"""
        assert detail_panel.height == 500
        assert detail_panel.selected_test_result is None
        assert detail_panel.standard_info is None
    
    def test_session_state_initialization(self, detail_panel):
        """세션 상태 초기화 테스트"""
        # Create a mock that behaves like Streamlit's session state
        class MockSessionState:
            def __init__(self):
                self._data = {}
            
            def __contains__(self, key):
                return key in self._data
            
            def __setattr__(self, key, value):
                if key.startswith('_'):
                    super().__setattr__(key, value)
                else:
                    self._data[key] = value
            
            def __getattr__(self, key):
                return self._data.get(key)
        
        mock_session_state = MockSessionState()
        
        with patch('streamlit.session_state', mock_session_state):
            detail_panel._initialize_session_state()
            
            # Verify that detail_panel was set
            assert hasattr(mock_session_state, 'detail_panel')
            assert mock_session_state.detail_panel['selected_test_result'] is None
            assert mock_session_state.detail_panel['show_standard_sheet'] is False
            assert mock_session_state.detail_panel['selected_standard_doc'] is None
            assert mock_session_state.detail_panel['panel_expanded'] is True
    
    @patch('streamlit.markdown')
    def test_render_empty_state(self, mock_markdown, detail_panel):
        """빈 상태 렌더링 테스트"""
        mock_session_state = Mock()
        mock_session_state.detail_panel = {'selected_test_result': None}
        
        with patch('streamlit.session_state', mock_session_state):
            detail_panel.render_detail_panel()
            
            # markdown이 호출되었는지 확인
            assert mock_markdown.called
            
            # 빈 상태 메시지가 포함되었는지 확인
            call_args = mock_markdown.call_args_list
            empty_state_found = any(
                "상세 정보를 보려면 행을 선택하세요" in str(call[0][0])
                for call in call_args
            )
            assert empty_state_found
    
    @patch('streamlit.markdown')
    def test_render_sample_info_section(self, mock_markdown, detail_panel, sample_test_result):
        """시료 정보 섹션 렌더링 테스트 (요구사항 4.1)"""
        # Mock session state properly
        mock_session_state = Mock()
        mock_session_state.detail_panel = {'selected_test_result': None}
        
        with patch('streamlit.session_state', mock_session_state):
            detail_panel.render_detail_panel(sample_test_result)
            
            # markdown이 호출되었는지 확인
            assert mock_markdown.called
            
            # 시료 정보가 포함되었는지 확인
            call_args = mock_markdown.call_args_list
            sample_info_found = any(
                "냉수탱크" in str(call[0][0]) and "25A00009-001" in str(call[0][0])
                for call in call_args
            )
            assert sample_info_found
    
    @patch('streamlit.markdown')
    def test_render_test_standard_section(self, mock_markdown, detail_panel, sample_test_result):
        """시험 규격 정보 섹션 렌더링 테스트 (요구사항 4.2)"""
        mock_session_state = Mock()
        mock_session_state.detail_panel = {'selected_test_result': None}
        
        with patch('streamlit.session_state', mock_session_state):
            detail_panel.render_detail_panel(sample_test_result)
            
            # markdown이 호출되었는지 확인
            assert mock_markdown.called
            
            # 시험 규격 정보가 포함되었는지 확인
            call_args = mock_markdown.call_args_list
            standard_info_found = any(
                "시험 규격 정보" in str(call[0][0]) and "KS M 3016:2021" in str(call[0][0])
                for call in call_args
            )
            assert standard_info_found
    
    @patch('streamlit.markdown')
    def test_violation_result_highlighting(self, mock_markdown, detail_panel, violation_test_result):
        """부적합 결과 강조 표시 테스트"""
        mock_session_state = Mock()
        mock_session_state.detail_panel = {'selected_test_result': None}
        
        with patch('streamlit.session_state', mock_session_state):
            detail_panel.render_detail_panel(violation_test_result)
            
            # markdown이 호출되었는지 확인
            assert mock_markdown.called
            
            # 부적합 스타일링이 적용되었는지 확인
            call_args = mock_markdown.call_args_list
            violation_styling_found = any(
                "#fef2f2" in str(call[0][0]) and "#dc2626" in str(call[0][0])
                for call in call_args
            )
            assert violation_styling_found
    
    def test_get_standard_document_name(self, detail_panel):
        """규격 문서명 생성 테스트"""
        # 알려진 시험 항목
        doc_name = detail_panel._get_standard_document_name("아크릴로나이트릴")
        assert doc_name == "KS_M_3018_2021.pdf"
        
        # 알려지지 않은 시험 항목
        doc_name = detail_panel._get_standard_document_name("알려지지않은항목")
        assert doc_name == "알려지지않은항목_규격.pdf"
    
    @patch('streamlit.markdown')
    def test_render_standard_bottom_sheet(self, mock_markdown, detail_panel):
        """규격 문서 바텀 시트 렌더링 테스트 (요구사항 4.3, 4.4, 4.5)"""
        detail_panel.render_standard_bottom_sheet()
        
        # markdown이 호출되었는지 확인
        assert mock_markdown.called
        
        # 바텀 시트 HTML이 포함되었는지 확인
        call_args = mock_markdown.call_args_list
        bottom_sheet_found = any(
            "standard-bottom-sheet" in str(call[0][0]) and "showStandardDocument" in str(call[0][0])
            for call in call_args
        )
        assert bottom_sheet_found
    
    def test_get_selected_test_result(self, detail_panel, sample_test_result):
        """선택된 시험 결과 반환 테스트"""
        mock_session_state = Mock()
        mock_session_state.detail_panel = {'selected_test_result': None}
        
        with patch('streamlit.session_state', mock_session_state):
            # 초기 상태에서는 None
            result = detail_panel.get_selected_test_result()
            assert result is None
            
            # 세션 상태에 데이터 설정
            mock_session_state.detail_panel = {'selected_test_result': sample_test_result}
            
            # 선택된 결과 반환 확인
            result = detail_panel.get_selected_test_result()
            assert result == sample_test_result
    
    def test_clear_selection(self, detail_panel, sample_test_result):
        """선택 상태 초기화 테스트"""
        mock_session_state = Mock()
        mock_session_state.detail_panel = {'selected_test_result': sample_test_result}
        
        with patch('streamlit.session_state', mock_session_state):
            # 데이터 설정
            detail_panel.selected_test_result = sample_test_result
            detail_panel.standard_info = Standard.from_test_result(sample_test_result)
            
            # 초기화 실행
            detail_panel.clear_selection()
            
            # 초기화 확인
            assert detail_panel.selected_test_result is None
            assert detail_panel.standard_info is None
            assert mock_session_state.detail_panel['selected_test_result'] is None
    
    def test_approval_info_rendering_with_approval(self, detail_panel, sample_test_result):
        """승인 정보 렌더링 테스트 (승인 요청된 경우)"""
        approval_html = detail_panel._render_approval_info(sample_test_result)
        
        assert "승인 요청됨" in approval_html
        assert "2025-01-23 10:30" in approval_html
        assert "#f59e0b" in approval_html  # 승인 요청 색상
    
    def test_approval_info_rendering_without_approval(self, detail_panel, violation_test_result):
        """승인 정보 렌더링 테스트 (승인 요청되지 않은 경우)"""
        approval_html = detail_panel._render_approval_info(violation_test_result)
        
        assert "승인 대기" in approval_html
        assert "승인 요청 없음" in approval_html
        assert "#64748b" in approval_html  # 대기 상태 색상
    
    @patch('streamlit.markdown')
    def test_standard_link_generation(self, mock_markdown, detail_panel, sample_test_result):
        """규격 링크 생성 테스트 (요구사항 4.2)"""
        mock_session_state = Mock()
        mock_session_state.detail_panel = {'selected_test_result': None}
        
        with patch('streamlit.session_state', mock_session_state):
            detail_panel.render_detail_panel(sample_test_result)
            
            # markdown 호출 확인
            assert mock_markdown.called
            
            # 규격 링크가 생성되었는지 확인
            call_args = mock_markdown.call_args_list
            link_found = any(
                "showStandardDocument" in str(call[0][0]) and "KS_M_3016_2021.pdf" in str(call[0][0])
                for call in call_args
            )
            assert link_found
    
    @patch('streamlit.markdown')
    def test_additional_info_section(self, mock_markdown, detail_panel, sample_test_result):
        """추가 정보 섹션 테스트"""
        mock_session_state = Mock()
        mock_session_state.detail_panel = {'selected_test_result': None}
        
        with patch('streamlit.session_state', mock_session_state):
            detail_panel.render_detail_panel(sample_test_result)
            
            # markdown 호출 확인
            assert mock_markdown.called
            
            # 추가 정보가 포함되었는지 확인
            call_args = mock_markdown.call_args_list
            additional_info_found = any(
                "추가 정보" in str(call[0][0]) and "LC-MS/MS" in str(call[0][0]) and "A그룹" in str(call[0][0])
                for call in call_args
            )
            assert additional_info_found


class TestDetailPanelIntegration:
    """상세 정보 패널 통합 테스트"""
    
    @pytest.fixture
    def mock_interactive_table(self):
        """모의 인터랙티브 테이블"""
        table = Mock()
        table.get_selected_row.return_value = TestResult(
            no=1,
            sample_name="테스트시료",
            analysis_number="TEST-001",
            test_item="테스트항목",
            test_unit="mg/L",
            result_report="0.001",
            tester_input_value=0.001,
            standard_excess="적합",
            tester="테스트시험자",
            test_standard="TEST STANDARD",
            standard_criteria="0.01 mg/L 이하",
            text_digits="3",
            processing_method="자동",
            result_display_digits=3,
            result_type="정량",
            tester_group="테스트그룹",
            input_datetime=datetime.now(),
            approval_request="N",
            approval_request_datetime=None,
            test_result_display_limit=0.001,
            quantitative_limit_processing="미만표시",
            test_equipment="TEST-EQUIPMENT",
            judgment_status="완료",
            report_output="Y",
            kolas_status="Y",
            test_lab_group="테스트팀",
            test_set="TEST-SET"
        )
        return table
    
    @patch('streamlit.markdown')
    def test_table_row_selection_integration(self, mock_markdown, mock_interactive_table):
        """테이블 행 선택과 상세 패널 연동 테스트"""
        detail_panel = DetailInfoPanel()
        mock_session_state = Mock()
        mock_session_state.detail_panel = {'selected_test_result': None}
        
        with patch('streamlit.session_state', mock_session_state):
            # 테이블에서 선택된 행 가져오기
            selected_row = mock_interactive_table.get_selected_row()
            
            # 상세 패널에 선택된 행 전달
            detail_panel.render_detail_panel(selected_row)
            
            # 상세 정보가 렌더링되었는지 확인
            assert mock_markdown.called
            
            # 선택된 데이터가 패널에 설정되었는지 확인
            assert detail_panel.selected_test_result == selected_row
    
    def test_standard_document_mapping(self):
        """규격 문서 매핑 테스트"""
        detail_panel = DetailInfoPanel()
        
        # 다양한 시험 항목에 대한 규격 문서 매핑 테스트
        test_cases = [
            ("1-[4-(1-hydroxy-1-methylethyl)phenyl]-ethanone", "KS_M_3016_2021.pdf"),
            ("N-니트로조다이메틸아민", "KS_M_3017_2021.pdf"),
            ("아크릴로나이트릴", "KS_M_3018_2021.pdf"),
            ("시안", "KS_M_3021_2021.pdf"),
            ("질산성질소", "KS_M_3022_2021.pdf"),
            ("알려지지않은항목", "알려지지않은항목_규격.pdf")
        ]
        
        for test_item, expected_doc in test_cases:
            result = detail_panel._get_standard_document_name(test_item)
            assert result == expected_doc


if __name__ == "__main__":
    pytest.main([__file__])