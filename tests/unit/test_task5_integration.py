#!/usr/bin/env python3
"""
Task 5 통합 테스트
DynamicDashboardEngine과 KPICardComponent의 통합 테스트
"""

import sys
from datetime import datetime
from data_models import TestResult
from data_processor import DataProcessor
from dynamic_dashboard_engine import DynamicDashboardEngine
from kpi_cards import KPICardComponent


def create_sample_data():
    """테스트용 샘플 데이터 생성"""
    return [
        TestResult(
            no=1, sample_name='냉수탱크', analysis_number='25A00009-001',
            test_item='아크릴로나이트릴', test_unit='mg/L', result_report='불검출',
            tester_input_value=0, standard_excess='적합', tester='김화빈',
            test_standard='EPA 524.2', standard_criteria='0.0006 mg/L 이하',
            text_digits='', processing_method='반올림', result_display_digits=4,
            result_type='수치형', tester_group='유기(ALL)',
            input_datetime=datetime(2025, 1, 23, 9, 56), approval_request='Y',
            approval_request_datetime=datetime(2025, 1, 23, 13, 45),
            test_result_display_limit=0.0002, quantitative_limit_processing='불검출',
            test_equipment='', judgment_status='N', report_output='Y',
            kolas_status='N', test_lab_group='유기_용출_Acrylonitrile', test_set='Set 1'
        ),
        TestResult(
            no=2, sample_name='온수탱크', analysis_number='25A00009-002',
            test_item='아크릴로나이트릴', test_unit='mg/L', result_report='0.0007',
            tester_input_value=0.0007, standard_excess='부적합', tester='김화빈',
            test_standard='EPA 524.2', standard_criteria='0.0006 mg/L 이하',
            text_digits='', processing_method='반올림', result_display_digits=4,
            result_type='수치형', tester_group='유기(ALL)',
            input_datetime=datetime(2025, 1, 23, 9, 56), approval_request='Y',
            approval_request_datetime=datetime(2025, 1, 23, 13, 45),
            test_result_display_limit=0.0002, quantitative_limit_processing='불검출',
            test_equipment='', judgment_status='N', report_output='Y',
            kolas_status='N', test_lab_group='유기_용출_Acrylonitrile', test_set='Set 1'
        ),
        TestResult(
            no=3, sample_name='유량센서', analysis_number='25A00009-003',
            test_item='N-니트로조다이메틸아민', test_unit='ng/L', result_report='2.5',
            tester_input_value=2.5, standard_excess='부적합', tester='이현풍',
            test_standard='House Method', standard_criteria='2.0 ng/L 이하',
            text_digits='', processing_method='반올림', result_display_digits=1,
            result_type='수치형', tester_group='유기(ALL)',
            input_datetime=datetime(2025, 1, 23, 10, 30), approval_request='Y',
            approval_request_datetime=datetime(2025, 1, 23, 14, 15),
            test_result_display_limit=0.5, quantitative_limit_processing='불검출',
            test_equipment='', judgment_status='N', report_output='Y',
            kolas_status='N', test_lab_group='유기_NDMA', test_set='Set 2'
        )
    ]


def test_dynamic_dashboard_engine():
    """DynamicDashboardEngine 테스트"""
    print("=== DynamicDashboardEngine 테스트 ===")
    
    # 데이터 준비
    processor = DataProcessor()
    engine = DynamicDashboardEngine(processor)
    sample_data = create_sample_data()
    
    # 대시보드 업데이트
    engine.update_dashboard(sample_data, "test_sample.xlsx")
    
    # 상태 확인
    assert engine.is_dashboard_initialized(), "대시보드가 초기화되지 않았습니다"
    assert engine.get_current_file() == "test_sample.xlsx", "파일명이 올바르지 않습니다"
    
    # KPI 데이터 확인
    kpi_data = engine.get_kpi_data()
    assert kpi_data is not None, "KPI 데이터가 없습니다"
    assert kpi_data['total_tests'] == 3, f"총 시험 수가 잘못됨: {kpi_data['total_tests']}"
    assert kpi_data['non_conforming_tests'] == 2, f"부적합 수가 잘못됨: {kpi_data['non_conforming_tests']}"
    assert abs(kpi_data['non_conforming_rate'] - 66.7) < 0.1, f"부적합 비율이 잘못됨: {kpi_data['non_conforming_rate']}"
    
    print("✅ DynamicDashboardEngine 테스트 통과")
    return engine


def test_kpi_card_component():
    """KPICardComponent 테스트"""
    print("=== KPICardComponent 테스트 ===")
    
    # 컴포넌트 초기화
    kpi_component = KPICardComponent()
    sample_data = create_sample_data()
    
    # 메트릭 계산
    kpi_data = kpi_component.calculate_kpi_metrics(sample_data)
    
    # 계산 결과 검증
    assert kpi_data['total_tests'] == 3, f"총 시험 수가 잘못됨: {kpi_data['total_tests']}"
    assert kpi_data['non_conforming_tests'] == 2, f"부적합 수가 잘못됨: {kpi_data['non_conforming_tests']}"
    assert kpi_data['total_samples'] == 3, f"총 시료 수가 잘못됨: {kpi_data['total_samples']}"
    assert kpi_data['non_conforming_samples'] == 2, f"부적합 시료 수가 잘못됨: {kpi_data['non_conforming_samples']}"
    
    # HTML 생성 테스트
    html_content = kpi_component.generate_html_kpi_cards(kpi_data)
    assert len(html_content) > 1000, "HTML 콘텐츠가 너무 짧습니다"
    assert "총 시험 항목" in html_content, "HTML에 필수 텍스트가 없습니다"
    assert "부적합 항목" in html_content, "HTML에 필수 텍스트가 없습니다"
    
    # 요약 텍스트 테스트
    summary_text = kpi_component.get_kpi_summary_text(kpi_data)
    assert "품질 상태" in summary_text, "요약 텍스트에 상태 정보가 없습니다"
    
    print("✅ KPICardComponent 테스트 통과")
    return kpi_component, kpi_data


def test_integration():
    """통합 테스트"""
    print("=== 통합 테스트 ===")
    
    # 각 컴포넌트 테스트
    engine = test_dynamic_dashboard_engine()
    kpi_component, kpi_data_from_component = test_kpi_card_component()
    
    # 데이터 일관성 확인
    kpi_data_from_engine = engine.get_kpi_data()
    
    assert kpi_data_from_engine['total_tests'] == kpi_data_from_component['total_tests'], \
        "엔진과 컴포넌트의 총 시험 수가 다릅니다"
    assert kpi_data_from_engine['non_conforming_tests'] == kpi_data_from_component['non_conforming_tests'], \
        "엔진과 컴포넌트의 부적합 수가 다릅니다"
    
    # 상태 관리 테스트
    engine.refresh_dashboard_state()
    assert engine.is_dashboard_initialized(), "새로고침 후 초기화 상태가 유지되지 않았습니다"
    
    # 선택된 행 테스트
    engine.set_selected_row(0)
    selected_row = engine.get_selected_row()
    assert selected_row is not None, "행 선택이 작동하지 않습니다"
    assert selected_row.sample_name == "냉수탱크", f"선택된 행 데이터가 잘못됨: {selected_row.sample_name}"
    
    print("✅ 통합 테스트 통과")


def main():
    """메인 테스트 함수"""
    print("Task 5 구현 검증 테스트 시작")
    print("=" * 50)
    
    try:
        test_integration()
        print("\n" + "=" * 50)
        print("🎉 모든 테스트 통과!")
        print("\nTask 5 구현 완료:")
        print("✅ 5.1 DynamicDashboardEngine 클래스 구현")
        print("✅ 5.2 KPI 카드 컴포넌트 구현")
        print("\n주요 기능:")
        print("- 동적 헤더 업데이트 기능")
        print("- KPI 카드 실시간 계산 로직")
        print("- 대시보드 상태 관리")
        print("- TailwindCSS 스타일링")
        print("- 부적합 비율 계산 및 표시")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        return 1
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())