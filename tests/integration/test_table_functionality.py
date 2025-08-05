#!/usr/bin/env python3
"""
간단한 인터랙티브 테이블 기능 테스트
"""

import sys
import os
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.components.interactive_data_table import InteractiveDataTable
from src.core.data_models import TestResult


def create_sample_data():
    """테스트용 샘플 데이터 생성"""
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


def test_table_data_preparation():
    """테이블 데이터 준비 테스트"""
    print("🧪 테이블 데이터 준비 테스트...")
    
    table = InteractiveDataTable(height=500)
    sample_data = create_sample_data()
    
    table_data = table._prepare_table_data(sample_data)
    
    assert len(table_data) == 3
    assert table_data[0]['시료명'] == "시료A"
    assert table_data[0]['시험항목'] == "대장균"
    assert table_data[0]['판정'] == "부적합"
    assert table_data[0]['is_violation'] == True
    
    assert table_data[1]['is_violation'] == False
    assert table_data[2]['결과'] == "불검출"
    
    print("✅ 테이블 데이터 준비 테스트 통과")


def test_search_filtering():
    """검색 필터링 테스트"""
    print("🔍 검색 필터링 테스트...")
    
    table = InteractiveDataTable(height=500)
    sample_data = create_sample_data()
    
    # 세션 상태 시뮬레이션
    import streamlit as st
    if 'interactive_table' not in st.session_state:
        st.session_state.interactive_table = {}
    
    # 시료A로 검색
    st.session_state.interactive_table.update({
        'search_term': '시료A',
        'judgment_filter': '전체',
        'show_violations_only': False
    })
    
    table_data = table._prepare_table_data(sample_data)
    filtered_data = table._apply_search_filter(table_data)
    
    assert len(filtered_data) == 1
    assert filtered_data[0]['시료명'] == "시료A"
    
    # pH로 검색
    st.session_state.interactive_table['search_term'] = 'pH'
    filtered_data = table._apply_search_filter(table_data)
    
    assert len(filtered_data) == 1
    assert filtered_data[0]['시험항목'] == "pH"
    
    print("✅ 검색 필터링 테스트 통과")


def test_violation_filtering():
    """부적합 필터링 테스트"""
    print("⚠️ 부적합 필터링 테스트...")
    
    table = InteractiveDataTable(height=500)
    sample_data = create_sample_data()
    
    import streamlit as st
    if 'interactive_table' not in st.session_state:
        st.session_state.interactive_table = {}
    
    # 부적합만 보기
    st.session_state.interactive_table.update({
        'search_term': '',
        'judgment_filter': '전체',
        'show_violations_only': True
    })
    
    table_data = table._prepare_table_data(sample_data)
    filtered_data = table._apply_search_filter(table_data)
    
    assert len(filtered_data) == 1
    assert filtered_data[0]['is_violation'] == True
    assert filtered_data[0]['판정'] == "부적합"
    
    print("✅ 부적합 필터링 테스트 통과")


def test_sorting_functionality():
    """정렬 기능 테스트"""
    print("📊 정렬 기능 테스트...")
    
    table = InteractiveDataTable(height=500)
    sample_data = create_sample_data()
    
    import streamlit as st
    if 'interactive_table' not in st.session_state:
        st.session_state.interactive_table = {}
    
    # 시료명 오름차순 정렬
    st.session_state.interactive_table.update({
        'sort_column': '시료명',
        'sort_ascending': True
    })
    
    table_data = table._prepare_table_data(sample_data)
    sorted_data = table._apply_sorting(table_data)
    
    assert sorted_data[0]['시료명'] == "시료A"
    assert sorted_data[1]['시료명'] == "시료B"
    assert sorted_data[2]['시료명'] == "시료C"
    
    # 시료명 내림차순 정렬
    st.session_state.interactive_table['sort_ascending'] = False
    sorted_data = table._apply_sorting(table_data)
    
    assert sorted_data[0]['시료명'] == "시료C"
    assert sorted_data[1]['시료명'] == "시료B"
    assert sorted_data[2]['시료명'] == "시료A"
    
    print("✅ 정렬 기능 테스트 통과")


def test_enhanced_html_generation():
    """향상된 HTML 생성 테스트"""
    print("🎨 향상된 HTML 생성 테스트...")
    
    table = InteractiveDataTable(height=500)
    sample_data = create_sample_data()
    
    import streamlit as st
    if 'interactive_table' not in st.session_state:
        st.session_state.interactive_table = {
            'sort_column': '시료명',
            'sort_ascending': True,
            'selected_row_index': None
        }
    
    table_data = table._prepare_table_data(sample_data)
    html = table._generate_enhanced_table_html(table_data)
    
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
    assert 'handleSort(' in html
    assert '🔼' in html or '🔽' in html or '↕️' in html
    
    # 행 선택 기능 확인
    assert 'handleRowSelect(' in html
    assert 'data-row-index=' in html
    
    # 부적합 행 강조 확인
    assert 'violation-row' in html
    assert '⚠️' in html
    
    # JavaScript 함수 확인
    assert 'handleSort' in html
    assert 'handleRowSelect' in html
    assert 'handleKeyNavigation' in html
    assert 'applySearchFilter' in html
    assert 'emphasizeViolations' in html
    
    print("✅ 향상된 HTML 생성 테스트 통과")


def test_row_selection():
    """행 선택 테스트"""
    print("👆 행 선택 테스트...")
    
    table = InteractiveDataTable(height=500)
    sample_data = create_sample_data()
    
    import streamlit as st
    if 'interactive_table' not in st.session_state:
        st.session_state.interactive_table = {}
    
    # 초기 상태
    st.session_state.interactive_table['selected_row_index'] = None
    selected_row = table.get_selected_row()
    assert selected_row is None
    
    # 행 선택
    st.session_state.interactive_table['selected_row_index'] = 0
    table.current_data = sample_data
    
    selected_row = table.get_selected_row()
    assert selected_row is not None
    assert selected_row.sample_name == "시료A"
    assert selected_row.test_item == "대장균"
    
    print("✅ 행 선택 테스트 통과")


def main():
    """메인 테스트 실행"""
    print("🚀 인터랙티브 데이터 테이블 기능 테스트 시작\n")
    
    try:
        test_table_data_preparation()
        test_search_filtering()
        test_violation_filtering()
        test_sorting_functionality()
        test_enhanced_html_generation()
        test_row_selection()
        
        print("\n🎉 모든 테스트가 성공적으로 통과했습니다!")
        print("\n✅ 구현된 기능:")
        print("   - 컬럼 헤더 정렬 기능 (요구사항 3.2)")
        print("   - 실시간 검색/필터링 기능 (요구사항 3.2)")
        print("   - 행 선택 및 하이라이트 기능 (요구사항 3.4, 3.5)")
        print("   - 부적합 행 시각적 강조 (요구사항 3.3)")
        print("   - 키보드 네비게이션 지원")
        print("   - 검색어 하이라이트")
        print("   - 반응형 디자인")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)