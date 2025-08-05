"""
대시보드 기능 테스트
"""

from data_processor import DataProcessor
from template_integration import TemplateIntegrator
from pathlib import Path
import pandas as pd

def test_full_workflow():
    """전체 워크플로우 테스트"""
    print("🧪 실험실 품질관리 대시보드 테스트 시작")
    print("=" * 50)
    
    # 1. 샘플 데이터 생성
    print("1. 샘플 데이터 생성 중...")
    sample_data = {
        'No.': list(range(1, 11)),
        '시료명': ['냉수탱크', '온수탱크', 'Blank', '제품#1', '제품#2', '원수', '5700용출', 'P09CL용출', '1300L#2', '1300L#4'],
        '분석번호': [f'25A0000{i}-00{i}' for i in range(1, 11)],
        '시험항목': ['아크릴로나이트릴'] * 5 + ['N-니트로조다이메틸아민'] * 5,
        '시험단위': ['mg/L'] * 5 + ['ng/L'] * 5,
        '결과(성적서)': ['불검출', '불검출', '0.0007', '0.001', '0.0004', '2.29', '1.96', '3.4', '3.37', '2.5'],
        '시험자입력값': [0, 0, 0.0007, 0.001, 0.0004, 2.29, 1.96, 3.4, 3.37, 2.5],
        '기준대비 초과여부 (성적서)': ['적합', '적합', '부적합', '부적합', '적합', '부적합', '부적합', '부적합', '부적합', '부적합'],
        '시험자': ['김화빈'] * 5 + ['이현풍'] * 5,
        '시험표준': ['EPA 524.2'] * 5 + ['House Method'] * 5,
        '기준': ['0.0006 mg/L 이하'] * 5 + ['0.1 ng/L 이하'] * 5,
        '입력일시': ['2025-01-23 09:56'] * 10
    }
    
    df = pd.DataFrame(sample_data)
    print(f"   ✅ {len(df)}개 샘플 데이터 생성 완료")
    
    # 2. 데이터 처리
    print("2. 데이터 처리 중...")
    processor = DataProcessor()
    
    test_results = []
    for _, row in df.iterrows():
        result = processor._row_to_test_result(row)
        if result:
            test_results.append(result)
    
    print(f"   ✅ {len(test_results)}개 테스트 결과 파싱 완료")
    
    # 3. 프로젝트 요약 생성
    print("3. 프로젝트 요약 생성 중...")
    project_name = "COWAY_품질관리_PJT"
    summary = processor.get_project_summary(project_name, test_results)
    
    print(f"   ✅ 프로젝트: {summary.project_name}")
    print(f"   ✅ 분석기간: {summary.analysis_period}")
    print(f"   ✅ 총 시료: {summary.total_samples}개")
    print(f"   ✅ 총 시험: {summary.total_tests}건")
    print(f"   ✅ 부적합 시료: {summary.violation_samples}개")
    print(f"   ✅ 부적합 비율: {summary.violation_rate:.1f}%")
    
    # 4. 템플릿 통합 테스트
    print("4. HTML 템플릿 통합 테스트 중...")
    integrator = TemplateIntegrator()
    
    # JavaScript 데이터 생성
    js_data = integrator.generate_javascript_data(test_results, project_name)
    print(f"   ✅ JavaScript 데이터 생성 완료 ({len(js_data)} 문자)")
    
    # 요약 통계
    stats = integrator.create_summary_stats(test_results)
    print(f"   ✅ 요약 통계: 부적합 {stats['violation_tests']}/{stats['total_tests']}건")
    
    # 5. HTML 템플릿 로드 및 통합 테스트
    print("5. HTML 템플릿 통합 테스트 중...")
    template_path = Path("design_template_v2.html")
    
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()
        
        # 데이터 주입
        modified_html = integrator.inject_data_into_template(html_template, test_results, project_name)
        
        print(f"   ✅ HTML 템플릿 로드 완료 ({len(html_template)} 문자)")
        print(f"   ✅ 데이터 주입 완료 ({len(modified_html)} 문자)")
        
        # 수정된 HTML 저장 (테스트용)
        with open("test_output.html", 'w', encoding='utf-8') as f:
            f.write(modified_html)
        print("   ✅ 테스트 HTML 파일 저장: test_output.html")
        
    else:
        print("   ❌ HTML 템플릿 파일을 찾을 수 없습니다.")
    
    # 6. 부적합 항목 상세 분석
    print("6. 부적합 항목 상세 분석...")
    violations = [r for r in test_results if r.is_non_conforming()]
    
    print(f"   📊 부적합 항목 상세:")
    for violation in violations:
        print(f"      - {violation.sample_name}: {violation.test_item} = {violation.get_display_result()} {violation.test_unit}")
    
    # 7. 항목별 통계
    print("7. 항목별 통계 분석...")
    for item, data in summary.test_items_summary.items():
        print(f"   📈 {item}: {data['violation']}/{data['total']}건 부적합 ({data['rate']:.1f}%)")
    
    print("\n" + "=" * 50)
    print("🎉 모든 테스트 완료!")
    print(f"📊 최종 결과: {summary.violation_samples}/{summary.total_samples}개 시료에서 부적합 발견")
    print(f"⚠️  주의 필요 항목: {list(summary.test_items_summary.keys())}")
    
    return test_results, summary

if __name__ == "__main__":
    test_full_workflow()