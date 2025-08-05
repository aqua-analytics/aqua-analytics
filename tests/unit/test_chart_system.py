"""
차트 시스템 테스트
"""

from datetime import datetime
from chart_system import ChartSystem
from data_models import TestResult


def create_sample_test_results():
    """테스트용 샘플 데이터 생성"""
    return [
        TestResult(
            no=1,
            sample_name="시료A",
            analysis_number="A001",
            test_item="pH",
            test_unit="",
            result_report="8.5",
            tester_input_value=8.5,
            standard_excess="적합",
            tester="김분석",
            test_standard="KS M ISO 10523",
            standard_criteria="6.5-8.5",
            text_digits="1",
            processing_method="일반",
            result_display_digits=1,
            result_type="수치",
            tester_group="화학팀",
            input_datetime=datetime(2024, 1, 15),
            approval_request="Y",
            approval_request_datetime=datetime(2024, 1, 15),
            test_result_display_limit=0.1,
            quantitative_limit_processing="표시",
            test_equipment="pH미터",
            judgment_status="완료",
            report_output="Y",
            kolas_status="N",
            test_lab_group="본소",
            test_set="SET1"
        ),
        TestResult(
            no=2,
            sample_name="시료B",
            analysis_number="A002",
            test_item="pH",
            test_unit="",
            result_report="9.2",
            tester_input_value=9.2,
            standard_excess="부적합",
            tester="김분석",
            test_standard="KS M ISO 10523",
            standard_criteria="6.5-8.5",
            text_digits="1",
            processing_method="일반",
            result_display_digits=1,
            result_type="수치",
            tester_group="화학팀",
            input_datetime=datetime(2024, 1, 15),
            approval_request="Y",
            approval_request_datetime=datetime(2024, 1, 15),
            test_result_display_limit=0.1,
            quantitative_limit_processing="표시",
            test_equipment="pH미터",
            judgment_status="완료",
            report_output="Y",
            kolas_status="N",
            test_lab_group="본소",
            test_set="SET1"
        ),
        TestResult(
            no=3,
            sample_name="시료C",
            analysis_number="A003",
            test_item="탁도",
            test_unit="NTU",
            result_report="15",
            tester_input_value=15,
            standard_excess="부적합",
            tester="이분석",
            test_standard="KS M ISO 7027",
            standard_criteria="10 이하",
            text_digits="0",
            processing_method="일반",
            result_display_digits=0,
            result_type="수치",
            tester_group="화학팀",
            input_datetime=datetime(2024, 1, 16),
            approval_request="Y",
            approval_request_datetime=datetime(2024, 1, 16),
            test_result_display_limit=1,
            quantitative_limit_processing="표시",
            test_equipment="탁도계",
            judgment_status="완료",
            report_output="Y",
            kolas_status="N",
            test_lab_group="본소",
            test_set="SET2"
        ),
        TestResult(
            no=4,
            sample_name="시료D",
            analysis_number="A004",
            test_item="탁도",
            test_unit="NTU",
            result_report="5",
            tester_input_value=5,
            standard_excess="적합",
            tester="이분석",
            test_standard="KS M ISO 7027",
            standard_criteria="10 이하",
            text_digits="0",
            processing_method="일반",
            result_display_digits=0,
            result_type="수치",
            tester_group="화학팀",
            input_datetime=datetime(2024, 1, 16),
            approval_request="Y",
            approval_request_datetime=datetime(2024, 1, 16),
            test_result_display_limit=1,
            quantitative_limit_processing="표시",
            test_equipment="탁도계",
            judgment_status="완료",
            report_output="Y",
            kolas_status="N",
            test_lab_group="본소",
            test_set="SET2"
        ),
        TestResult(
            no=5,
            sample_name="시료E",
            analysis_number="A005",
            test_item="pH",
            test_unit="",
            result_report="9.5",
            tester_input_value=9.5,
            standard_excess="부적합",
            tester="박분석",
            test_standard="KS M ISO 10523",
            standard_criteria="6.5-8.5",
            text_digits="1",
            processing_method="일반",
            result_display_digits=1,
            result_type="수치",
            tester_group="화학팀",
            input_datetime=datetime(2024, 1, 17),
            approval_request="Y",
            approval_request_datetime=datetime(2024, 1, 17),
            test_result_display_limit=0.1,
            quantitative_limit_processing="표시",
            test_equipment="pH미터",
            judgment_status="완료",
            report_output="Y",
            kolas_status="N",
            test_lab_group="본소",
            test_set="SET3"
        )
    ]


def test_chart_system_initialization():
    """차트 시스템 초기화 테스트"""
    chart_system = ChartSystem()
    
    assert chart_system.chart_config['theme']['mode'] == 'light'
    assert len(chart_system.chart_config['colors']) == 8
    assert chart_system.chart_config['animations']['enabled'] is True


def test_donut_chart_generation():
    """도넛 차트 생성 테스트"""
    chart_system = ChartSystem()
    test_results = create_sample_test_results()
    
    donut_config = chart_system.generate_non_conforming_donut_chart(test_results)
    
    # 기본 구조 확인
    assert 'chart' in donut_config
    assert 'series' in donut_config
    assert 'labels' in donut_config
    assert donut_config['chart']['type'] == 'donut'
    
    # 부적합 항목만 포함되는지 확인 (pH: 2건, 탁도: 1건)
    assert len(donut_config['series']) == 2
    assert sum(donut_config['series']) == 3  # 총 부적합 3건
    
    print("✅ 도넛 차트 생성 테스트 통과")
    print(f"   - 부적합 항목 수: {len(donut_config['labels'])}")
    print(f"   - 총 부적합 건수: {sum(donut_config['series'])}")


def test_bar_chart_generation():
    """막대 차트 생성 테스트"""
    chart_system = ChartSystem()
    test_results = create_sample_test_results()
    
    bar_config = chart_system.generate_non_conforming_bar_chart(test_results)
    
    # 기본 구조 확인
    assert 'chart' in bar_config
    assert 'series' in bar_config
    assert bar_config['chart']['type'] == 'bar'
    assert bar_config['plotOptions']['bar']['horizontal'] is True
    
    # 부적합 비율 계산 확인
    # pH: 2/3 = 66.7%, 탁도: 1/2 = 50.0%
    series_data = bar_config['series'][0]['data']
    categories = bar_config['xaxis']['categories']
    
    assert len(series_data) == 2
    assert len(categories) == 2
    
    # pH가 더 높은 비율이므로 첫 번째여야 함
    assert series_data[0] > series_data[1]
    
    print("✅ 막대 차트 생성 테스트 통과")
    print(f"   - 부적합 항목 수: {len(categories)}")
    print(f"   - 비율 데이터: {series_data}")


def test_empty_data_handling():
    """빈 데이터 처리 테스트"""
    chart_system = ChartSystem()
    
    # 빈 리스트
    empty_donut = chart_system.generate_non_conforming_donut_chart([])
    assert empty_donut['labels'] == ['데이터 없음']
    
    empty_bar = chart_system.generate_non_conforming_bar_chart([])
    assert empty_bar['series'][0]['data'] == []
    
    print("✅ 빈 데이터 처리 테스트 통과")


def test_html_generation():
    """HTML 생성 테스트"""
    chart_system = ChartSystem()
    test_results = create_sample_test_results()
    
    html = chart_system.generate_charts_html(test_results)
    
    # HTML 구조 확인
    assert '<div class="charts-container' in html
    assert 'id="donut-chart"' in html
    assert 'id="bar-chart"' in html
    assert 'ApexCharts' in html
    assert 'donutChart.render()' in html
    assert 'barChart.render()' in html
    
    print("✅ HTML 생성 테스트 통과")
    print(f"   - HTML 길이: {len(html)} 문자")


def test_chart_dependencies():
    """차트 의존성 테스트"""
    chart_system = ChartSystem()
    dependencies = chart_system.get_chart_dependencies()
    
    assert 'apexcharts' in dependencies
    assert 'script' in dependencies
    
    print("✅ 차트 의존성 테스트 통과")


if __name__ == "__main__":
    print("🧪 차트 시스템 테스트 시작\n")
    
    test_chart_system_initialization()
    test_donut_chart_generation()
    test_bar_chart_generation()
    test_empty_data_handling()
    test_html_generation()
    test_chart_dependencies()
    
    print("\n🎉 모든 차트 시스템 테스트 통과!")
    
    # 실제 HTML 출력 테스트
    print("\n📊 실제 차트 HTML 생성 테스트:")
    chart_system = ChartSystem()
    test_results = create_sample_test_results()
    html = chart_system.generate_charts_html(test_results)
    
    # HTML 파일로 저장하여 브라우저에서 확인 가능
    with open("test_charts_output.html", "w", encoding="utf-8") as f:
        full_html = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>차트 시스템 테스트</title>
            <script src="https://cdn.tailwindcss.com"></script>
            {chart_system.get_chart_dependencies()}
        </head>
        <body class="bg-gray-100 p-8">
            <div class="max-w-6xl mx-auto">
                <h1 class="text-3xl font-bold text-gray-800 mb-8">차트 시스템 테스트</h1>
                {html}
            </div>
        </body>
        </html>
        """
        f.write(full_html)
    
    print("   - test_charts_output.html 파일 생성 완료")
    print("   - 브라우저에서 열어서 차트 확인 가능")