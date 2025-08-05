"""
향상된 인터랙티브 데이터 테이블 테스트
요구사항 3.2, 3.3, 3.4, 3.5, 3.6 검증
"""

import pytest
import streamlit as st
from datetime import datetime
from unittest.mock import Mock, patch
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.components.interactive_data_table import InteractiveDataTable
from src.core.data_models import TestResult


class TestEnhancedInteractiveTable:
    """향상된 인터랙티브 테이블 테스트"""
    
    @pytest.fixture
    def sample_test_results(self):
        """테스트용 시험 결과 데이터"""
        return [
            TestResult(
                no=1,
                sample_name="시료A",
                analysis_number="A001",
                test_item="대장균",
                test_unit="CFU/mL",
                result_report=150.0,
                tester_input_value=150,
                standard_excess="부적합",
                tester="김시험",
                test_standard="KS M 0001",
                standard_criteria="100 CFU/mL 이하",
                text_digits="3",
                processing_method="직접",
                result_display_digits=0,
                result_type="수치",
                tester_group="미생물팀",
                input_datetime=datetime(2024, 1, 15, 10, 30),
                approval_request="Y",
                approval_request_datetime=datetime(2024, 1, 15, 11, 0),
                test_result_display_limit=100,
                quantitative_limit_processing="표시",
                test_equipment="배양기A",
                judgment_status="완료",
                report_output="Y",
                kolas_status="Y",
                test_lab_group="품질관리팀",
                test_set="SET001"
            ),
            TestResult(
                no=2,
                sample_name="시료B",
                analysis_number="B001",
                test_item="pH",
                test_unit="",
                result_report=7.2,
                tester_input_value=7.2,
                standard_excess="적합",
                tester="이분석",
                test_standard="KS M 0002",
                standard_criteria="6.5-8.5",
                text_digits="1",
                processing_method="직접",
                result_display_digits=1,
                result_type="수치",
                tester_group="화학팀",
                input_datetime=datetime(2024, 1, 15, 14, 20),
                approval_request="Y",
                approval_request_datetime=datetime(2024, 1, 15, 15, 0),
                test_result_display_limit=0,
                quantitative_limit_processing="표시",
                test_equipment="pH미터",
                judgment_status="완료",
                report_output="Y",
                kolas_status="N",
                test_lab_group="품질관리팀",
                test_set="SET002"
            ),
            TestResult(
                no=3,
                sample_name="시료C",
                analysis_number="C001",
                test_item="탁도",
                test_unit="NTU",
                result_report="불검출",
                tester_input_value=0,
                standard_excess="적합",
                tester="박측정",
                test_standard="KS M 0003",
                standard_criteria="1.0 NTU 이하",
                text_digits="1",
                processing_method="직접",
                result_display_digits=1,
                result_type="텍스트",
                tester_group="화학팀",
                input_datetime=datetime(2024, 1, 15, 16, 45),
                approval_request="Y",
                approval_request_datetime=datetime(2024, 1, 15, 17, 0),
                test_result_display_limit=1.0,
                quantitative_limit_processing="불검출",
                test_equipment="탁도계",
                judgment_status="완료",
                report_output="Y",
                kolas_status="Y",
                test_lab_group="품질관리팀",
                test_set="SET003"
            )
        ]
    
    @pytest.fixture
    def interactive_table(self):
        """인터랙티브 테이블 인스턴스"""
        return InteractiveDataTable(height=500)
    
    def test_table_data_preparation(self, interactive_table, sample_test_results):
        """테이블 데이터 준비 테스트"""
        table_data = interactive_table._prepare_table_data(sample_test_results)
        
        assert len(table_data) == 3
        assert table_data[0]['시료명'] == "시료A"
        assert table_data[0]['시험항목'] == "대장균"
        assert table_data[0]['결과'] == "150.0"
        assert table_data[0]['판정'] == "부적합"
        assert table_data[0]['is_violation'] == True
        
        assert table_data[1]['is_violation'] == False
        assert table_data[2]['결과'] == "불검출"
    
    @patch('streamlit.session_state')
    def test_search_filtering(self, mock_session_state, interactive_table, sample_test_results):
        """실시간 검색 필터링 테스트 (요구사항 3.2)"""
        # 세션 상태 설정
        mock_session_state.interactive_table = {
            'search_term': '시료A',
            'judgment_filter': '전체',
            'show_violations_only': False
        }
        
        table_data = interactive_table._prepare_table_data(sample_test_results)
        filtered_data = interactive_table._apply_search_filter(table_data)
        
        assert len(filtered_data) == 1
        assert filtered_data[0]['시료명'] == "시료A"
        
        # 시험항목으로 검색
        mock_session_state.interactive_table['search_term'] = 'pH'
        filtered_data = interactive_table._apply_search_filter(table_data)
        
        assert len(filtered_data) == 1
        assert filtered_data[0]['시험항목'] == "pH"
        
        # 시험자로 검색
        mock_session_state.interactive_table['search_term'] = '김시험'
        filtered_data = interactive_table._apply_search_filter(table_data)
        
        assert len(filtered_data) == 1
        assert filtered_data[0]['시험자'] == "김시험"
    
    @patch('streamlit.session_state')
    def test_violation_filtering(self, mock_session_state, interactive_table, sample_test_results):
        """부적합 항목 필터링 테스트 (요구사항 3.3)"""
        # 부적합만 보기 설정
        mock_session_state.interactive_table = {
            'search_term': '',
            'judgment_filter': '전체',
            'show_violations_only': True
        }
        
        table_data = interactive_table._prepare_table_data(sample_test_results)
        filtered_data = interactive_table._apply_search_filter(table_data)
        
        assert len(filtered_data) == 1
        assert filtered_data[0]['is_violation'] == True
        assert filtered_data[0]['판정'] == "부적합"
    
    @patch('streamlit.session_state')
    def test_judgment_filtering(self, mock_session_state, interactive_table, sample_test_results):
        """판정 상태 필터링 테스트"""
        # 적합만 보기 설정
        mock_session_state.interactive_table = {
            'search_term': '',
            'judgment_filter': '적합',
            'show_violations_only': False
        }
        
        table_data = interactive_table._prepare_table_data(sample_test_results)
        filtered_data = interactive_table._apply_search_filter(table_data)
        
        assert len(filtered_data) == 2
        for row in filtered_data:
            assert row['판정'] == "적합"
    
    @patch('streamlit.session_state')
    def test_sorting_functionality(self, mock_session_state, interactive_table, sample_test_results):
        """컬럼 헤더 정렬 기능 테스트 (요구사항 3.2)"""
        # 시료명 오름차순 정렬
        mock_session_state.interactive_table = {
            'sort_column': '시료명',
            'sort_ascending': True
        }
        
        table_data = interactive_table._prepare_table_data(sample_test_results)
        sorted_data = interactive_table._apply_sorting(table_data)
        
        assert sorted_data[0]['시료명'] == "시료A"
        assert sorted_data[1]['시료명'] == "시료B"
        assert sorted_data[2]['시료명'] == "시료C"
        
        # 시료명 내림차순 정렬
        mock_session_state.interactive_table['sort_ascending'] = False
        sorted_data = interactive_table._apply_sorting(table_data)
        
        assert sorted_data[0]['시료명'] == "시료C"
        assert sorted_data[1]['시료명'] == "시료B"
        assert sorted_data[2]['시료명'] == "시료A"
        
        # 판정으로 정렬 (사전순)
        mock_session_state.interactive_table['sort_column'] = '판정'
        mock_session_state.interactive_table['sort_ascending'] = True
        sorted_data = interactive_table._apply_sorting(table_data)
        
        # 사전순으로 정렬되므로 "부적합"이 "적합"보다 먼저 옴
        violation_count = sum(1 for row in sorted_data if row['판정'] == "부적합")
        conforming_count = sum(1 for row in sorted_data if row['판정'] == "적합")
        assert violation_count == 1
        assert conforming_count == 2
    
    def test_enhanced_table_html_generation(self, interactive_table, sample_test_results):
        """향상된 HTML 테이블 생성 테스트"""
        table_data = interactive_table._prepare_table_data(sample_test_results)
        html = interactive_table._generate_enhanced_table_html(table_data)
        
        # 기본 구조 확인
        assert 'enhanced-table-container' in html
        assert 'enhanced-interactive-table' in html
        assert 'enhanced-table-body' in html
        
        # 헤더 확인
        assert '시료명' in html
        assert '시험항목' in html
        assert '결과' in html
        assert '판정' in html
        assert '시험자' in html
        
        # 정렬 기능 확인
        assert 'onclick="handleSort(' in html
        assert '🔼' in html or '🔽' in html or '↕️' in html
        
        # 행 선택 기능 확인
        assert 'onclick="handleRowSelect(' in html
        assert 'data-row-index=' in html
        
        # 부적합 행 강조 확인
        assert 'violation-row' in html
        assert '⚠️' in html  # 부적합 표시 아이콘
        
        # JavaScript 함수 확인
        assert 'handleSort' in html
        assert 'handleRowSelect' in html
        assert 'handleKeyNavigation' in html
        assert 'applySearchFilter' in html
        assert 'emphasizeViolations' in html
    
    @patch('streamlit.session_state')
    def test_row_selection_state(self, mock_session_state, interactive_table, sample_test_results):
        """행 선택 상태 관리 테스트 (요구사항 3.4, 3.5)"""
        # 초기 상태
        mock_session_state.interactive_table = {
            'selected_row_index': None
        }
        
        selected_row = interactive_table.get_selected_row()
        assert selected_row is None
        
        # 행 선택
        mock_session_state.interactive_table['selected_row_index'] = 0
        interactive_table.current_data = sample_test_results
        
        selected_row = interactive_table.get_selected_row()
        assert selected_row is not None
        assert selected_row.sample_name == "시료A"
        assert selected_row.test_item == "대장균"
    
    @patch('streamlit.session_state')
    @patch('streamlit.text_input')
    @patch('streamlit.selectbox')
    @patch('streamlit.checkbox')
    @patch('streamlit.button')
    @patch('streamlit.columns')
    @patch('streamlit.container')
    @patch('streamlit.markdown')
    def test_search_and_controls_rendering(self, mock_markdown, mock_container, 
                                         mock_columns, mock_button, mock_checkbox, 
                                         mock_selectbox, mock_text_input, 
                                         mock_session_state, interactive_table):
        """검색 및 제어 UI 렌더링 테스트"""
        # 세션 상태 설정
        mock_session_state.interactive_table = {
            'search_term': '',
            'judgment_filter': '전체',
            'sort_column': '시료명',
            'sort_ascending': True,
            'show_violations_only': False
        }
        
        # Mock 설정
        mock_text_input.return_value = ''
        mock_selectbox.return_value = '전체'
        mock_checkbox.return_value = False
        mock_button.return_value = False
        mock_columns.return_value = [Mock(), Mock(), Mock(), Mock()]
        mock_container.return_value.__enter__ = Mock(return_value=Mock())
        mock_container.return_value.__exit__ = Mock(return_value=None)
        
        # 함수 호출
        interactive_table.render_search_and_controls()
        
        # 호출 확인
        mock_text_input.assert_called()
        mock_selectbox.assert_called()
        mock_checkbox.assert_called()
        mock_button.assert_called()
    
    @patch('streamlit.session_state')
    @patch('streamlit.metric')
    @patch('streamlit.columns')
    def test_table_summary_rendering(self, mock_columns, mock_metric, 
                                   mock_session_state, interactive_table, 
                                   sample_test_results):
        """테이블 요약 정보 렌더링 테스트"""
        # Mock 설정
        mock_columns.return_value = [Mock(), Mock(), Mock(), Mock()]
        
        # 필터링된 데이터 설정
        table_data = interactive_table._prepare_table_data(sample_test_results)
        interactive_table.filtered_data = table_data
        
        # 함수 호출
        interactive_table.render_table_summary()
        
        # 메트릭 호출 확인
        assert mock_metric.call_count == 4  # 4개의 메트릭
    
    def test_violation_emphasis_in_html(self, interactive_table, sample_test_results):
        """부적합 항목 시각적 강조 테스트 (요구사항 3.3)"""
        table_data = interactive_table._prepare_table_data(sample_test_results)
        html = interactive_table._generate_enhanced_table_html(table_data)
        
        # 부적합 행 스타일링 확인
        assert 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)' in html
        assert 'border: 2px solid transparent' in html
        assert 'box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2)' in html
        
        # 부적합 표시 아이콘 확인
        assert '⚠️' in html
        
        # CSS 애니메이션 확인
        assert 'violationEmphasis' in html
        assert '@keyframes violationEmphasis' in html
    
    def test_keyboard_navigation_support(self, interactive_table, sample_test_results):
        """키보드 네비게이션 지원 테스트 (요구사항 3.4, 3.5)"""
        table_data = interactive_table._prepare_table_data(sample_test_results)
        html = interactive_table._generate_enhanced_table_html(table_data)
        
        # 키보드 이벤트 핸들러 확인
        assert 'handleKeyNavigation' in html
        assert 'onkeydown=' in html
        assert 'tabindex="0"' in html
        
        # 키보드 단축키 지원 확인
        assert 'ArrowDown' in html
        assert 'ArrowUp' in html
        assert 'Enter' in html
        assert 'Escape' in html
    
    def test_search_highlighting(self, interactive_table, sample_test_results):
        """검색어 하이라이트 기능 테스트"""
        table_data = interactive_table._prepare_table_data(sample_test_results)
        html = interactive_table._generate_enhanced_table_html(table_data)
        
        # 검색어 하이라이트 함수 확인
        assert 'highlightSearchTerm' in html
        assert 'removeHighlight' in html
        assert '<mark style=' in html
        assert 'background: #fef08a' in html
    
    def test_responsive_design_elements(self, interactive_table, sample_test_results):
        """반응형 디자인 요소 테스트"""
        table_data = interactive_table._prepare_table_data(sample_test_results)
        html = interactive_table._generate_enhanced_table_html(table_data)
        
        # 반응형 스타일 확인
        assert 'overflow-y: auto' in html
        assert 'position: sticky' in html
        assert 'box-shadow:' in html
        assert 'border-radius:' in html
        
        # 호버 효과 확인
        assert 'onmouseover=' in html
        assert 'onmouseout=' in html
        assert 'transition:' in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])