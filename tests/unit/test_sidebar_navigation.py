"""
사이드바 탐색 시스템 테스트
"""

from sidebar_navigation import SidebarNavigationSystem, PageManager
from data_models import TestResult
from datetime import datetime


def test_sidebar_navigation_system():
    """SidebarNavigationSystem 기본 기능 테스트"""
    print("=== SidebarNavigationSystem 테스트 ===")
    
    # 인스턴스 생성
    sidebar_nav = SidebarNavigationSystem()
    print("✅ SidebarNavigationSystem 인스턴스 생성 성공")
    
    # 초기 상태 확인
    assert sidebar_nav.get_file_count() == 0
    assert sidebar_nav.get_file_list() == []
    print("✅ 초기 상태 확인 완료")
    
    # 샘플 테스트 결과 생성
    sample_test_result = TestResult(
        no=1, sample_name='테스트 시료', analysis_number='TEST-001',
        test_item='테스트 항목', test_unit='mg/L', result_report='1.5',
        tester_input_value=1.5, standard_excess='적합', tester='테스터',
        test_standard='Test Method', standard_criteria='2.0 mg/L 이하',
        text_digits='', processing_method='반올림', result_display_digits=2,
        result_type='수치형', tester_group='테스트그룹',
        input_datetime=datetime.now(), approval_request='Y',
        approval_request_datetime=datetime.now(),
        test_result_display_limit=0.1, quantitative_limit_processing='불검출',
        test_equipment='', judgment_status='N', report_output='Y',
        kolas_status='N', test_lab_group='테스트랩', test_set='Set 1'
    )
    
    # 파일 추가 테스트
    sidebar_nav.add_file("test_file.xlsx", b"test_content", [sample_test_result])
    assert sidebar_nav.get_file_count() == 1
    assert "test_file.xlsx" in sidebar_nav.get_file_list()
    print("✅ 파일 추가 기능 테스트 완료")
    
    # 파일 처리 상태 확인
    assert sidebar_nav.is_file_processed("test_file.xlsx") == True
    print("✅ 파일 처리 상태 확인 완료")
    
    # 테스트 결과 가져오기
    test_results = sidebar_nav.get_file_test_results("test_file.xlsx")
    assert len(test_results) == 1
    assert test_results[0].sample_name == '테스트 시료'
    print("✅ 테스트 결과 가져오기 완료")
    
    # 파일 제거 테스트
    sidebar_nav.remove_file("test_file.xlsx")
    assert sidebar_nav.get_file_count() == 0
    print("✅ 파일 제거 기능 테스트 완료")
    
    print("🎉 모든 테스트 통과!")


def test_page_manager():
    """PageManager 기본 기능 테스트"""
    print("\n=== PageManager 테스트 ===")
    
    sidebar_nav = SidebarNavigationSystem()
    page_manager = PageManager(sidebar_nav)
    print("✅ PageManager 인스턴스 생성 성공")
    
    # 메서드 존재 확인
    assert hasattr(page_manager, 'render_pending_files_page')
    assert hasattr(page_manager, 'render_reports_page')
    assert hasattr(page_manager, 'render_standards_page')
    print("✅ 필수 메서드 존재 확인 완료")
    
    print("🎉 PageManager 테스트 통과!")


if __name__ == "__main__":
    test_sidebar_navigation_system()
    test_page_manager()
    print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")