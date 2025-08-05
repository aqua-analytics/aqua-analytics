"""
시험성적서 생성 시스템
실제 데이터를 기반으로 한 품질관리 보고서 생성
"""

from typing import List, Dict, Any
from data_models import TestResult, ProjectSummary
from datetime import datetime
import base64
from io import BytesIO
import pandas as pd

class ReportGenerator:
    """품질관리 보고서 생성 클래스"""
    
    def __init__(self):
        self.company_info = {
            'name': 'COWAY',
            'address': '서울특별시 중구 서소문로 40',
            'phone': '02-1588-5200',
            'email': 'quality@coway.co.kr'
        }
    
    def generate_quality_report_html(self, test_results: List[TestResult], project_name: str) -> str:
        """품질관리 보고서 HTML 생성"""
        
        # 프로젝트 요약 생성
        summary = ProjectSummary.from_test_results(project_name, test_results)
        
        # 부적합 항목만 추출
        violations = [result for result in test_results if result.is_non_conforming()]
        
        # HTML 템플릿 생성
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{project_name} 품질관리 보고서</title>
            <style>
                body {{
                    font-family: 'Malgun Gothic', sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .report-container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    border-radius: 8px;
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: bold;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 16px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 30px;
                }}
                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .summary-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    border-left: 4px solid #667eea;
                }}
                .summary-card.danger {{
                    border-left-color: #dc3545;
                    background: #fff5f5;
                }}
                .summary-card h3 {{
                    margin: 0 0 10px 0;
                    color: #495057;
                    font-size: 14px;
                }}
                .summary-card .value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #212529;
                }}
                .summary-card.danger .value {{
                    color: #dc3545;
                }}
                .section {{
                    margin-bottom: 30px;
                }}
                .section h2 {{
                    color: #495057;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                .table th,
                .table td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #dee2e6;
                }}
                .table th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                    color: #495057;
                }}
                .table tr:hover {{
                    background-color: #f8f9fa;
                }}
                .violation-row {{
                    background-color: #fff5f5 !important;
                }}
                .violation-row:hover {{
                    background-color: #ffe6e6 !important;
                }}
                .status-badge {{
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .status-pass {{
                    background-color: #d4edda;
                    color: #155724;
                }}
                .status-fail {{
                    background-color: #f8d7da;
                    color: #721c24;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px 30px;
                    border-top: 1px solid #dee2e6;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
                @media print {{
                    body {{ background-color: white; }}
                    .report-container {{ box-shadow: none; }}
                }}
            </style>
        </head>
        <body>
            <div class="report-container">
                <div class="header">
                    <h1>{project_name}</h1>
                    <p>품질관리 보고서</p>
                    <p>{summary.analysis_period}</p>
                </div>
                
                <div class="content">
                    <!-- 요약 정보 -->
                    <div class="summary-grid">
                        <div class="summary-card">
                            <h3>총 시료 개수</h3>
                            <div class="value">{summary.total_samples}개</div>
                        </div>
                        <div class="summary-card">
                            <h3>총 시험 건수</h3>
                            <div class="value">{summary.total_tests}건</div>
                        </div>
                        <div class="summary-card danger">
                            <h3>부적합 시료</h3>
                            <div class="value">{summary.violation_samples}개</div>
                        </div>
                        <div class="summary-card danger">
                            <h3>부적합 비율</h3>
                            <div class="value">{summary.violation_rate:.1f}%</div>
                        </div>
                    </div>
                    
                    <!-- 부적합 항목 상세 -->
                    <div class="section">
                        <h2>🚨 부적합 항목 상세</h2>
                        {self._generate_violation_table_html(violations)}
                    </div>
                    
                    <!-- 시험항목별 통계 -->
                    <div class="section">
                        <h2>📊 시험항목별 통계</h2>
                        {self._generate_item_statistics_html(summary.test_items_summary)}
                    </div>
                    
                    <!-- 전체 시험 결과 -->
                    <div class="section">
                        <h2>📋 전체 시험 결과</h2>
                        {self._generate_all_results_table_html(test_results)}
                    </div>
                    
                    <!-- 기준값 정보 -->
                    <div class="section">
                        <h2>📏 시험 기준값 정보</h2>
                        {self._generate_standards_table_html(test_results)}
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>{self.company_info['name']}</strong> | {self.company_info['address']}</p>
                    <p>Tel: {self.company_info['phone']} | Email: {self.company_info['email']}</p>
                    <p>보고서 생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_violation_table_html(self, violations: List[TestResult]) -> str:
        """부적합 항목 테이블 HTML 생성"""
        if not violations:
            return "<p>🎉 부적합 항목이 없습니다!</p>"
        
        rows = []
        for i, violation in enumerate(violations, 1):
            rows.append(f"""
                <tr class="violation-row">
                    <td>{i}</td>
                    <td>{violation.analysis_number}</td>
                    <td><strong>{violation.sample_name}</strong></td>
                    <td>{violation.test_item}</td>
                    <td><strong>{violation.get_display_result()} {violation.test_unit}</strong></td>
                    <td>{violation.standard_criteria}</td>
                    <td><span class="status-badge status-fail">부적합</span></td>
                </tr>
            """)
        
        return f"""
        <table class="table">
            <thead>
                <tr>
                    <th>No.</th>
                    <th>접수번호</th>
                    <th>시료명</th>
                    <th>시험항목</th>
                    <th>초과결과</th>
                    <th>기준값</th>
                    <th>판정</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        <p><strong>총 {len(violations)}건의 부적합 항목이 발견되었습니다.</strong></p>
        """
    
    def _generate_item_statistics_html(self, test_items_summary: Dict[str, Dict]) -> str:
        """시험항목별 통계 HTML 생성"""
        rows = []
        for item, data in test_items_summary.items():
            status_class = "status-fail" if data['violation'] > 0 else "status-pass"
            status_text = f"{data['violation']}/{data['total']}건 부적합" if data['violation'] > 0 else "모두 적합"
            
            rows.append(f"""
                <tr>
                    <td>{item}</td>
                    <td>{data['total']}건</td>
                    <td>{data['violation']}건</td>
                    <td>{data['rate']:.1f}%</td>
                    <td><span class="status-badge {status_class}">{status_text}</span></td>
                </tr>
            """)
        
        return f"""
        <table class="table">
            <thead>
                <tr>
                    <th>시험항목</th>
                    <th>총 시험건수</th>
                    <th>부적합건수</th>
                    <th>부적합비율</th>
                    <th>상태</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
    
    def _generate_all_results_table_html(self, test_results: List[TestResult]) -> str:
        """전체 결과 테이블 HTML 생성 (최대 50개만 표시)"""
        display_results = test_results[:50]  # 너무 많으면 50개만 표시
        
        rows = []
        for i, result in enumerate(display_results, 1):
            row_class = "violation-row" if result.is_non_conforming() else ""
            status_class = "status-fail" if result.is_non_conforming() else "status-pass"
            status_text = result.standard_excess if result.standard_excess in ['적합', '부적합'] else '적합'
            
            rows.append(f"""
                <tr class="{row_class}">
                    <td>{i}</td>
                    <td>{result.sample_name}</td>
                    <td>{result.analysis_number}</td>
                    <td>{result.test_item}</td>
                    <td>{result.get_display_result()} {result.test_unit}</td>
                    <td>{result.standard_criteria}</td>
                    <td><span class="status-badge {status_class}">{status_text}</span></td>
                </tr>
            """)
        
        note = f"<p><em>* 총 {len(test_results)}건 중 {len(display_results)}건을 표시합니다.</em></p>" if len(test_results) > 50 else ""
        
        return f"""
        <table class="table">
            <thead>
                <tr>
                    <th>No.</th>
                    <th>시료명</th>
                    <th>접수번호</th>
                    <th>시험항목</th>
                    <th>결과</th>
                    <th>기준값</th>
                    <th>판정</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        {note}
        """
    
    def _generate_standards_table_html(self, test_results: List[TestResult]) -> str:
        """기준값 정보 테이블 HTML 생성"""
        standards = {}
        for result in test_results:
            if result.test_item not in standards and result.standard_criteria:
                standards[result.test_item] = {
                    'unit': result.test_unit,
                    'criteria': result.standard_criteria,
                    'method': result.test_standard
                }
        
        rows = []
        for i, (item, info) in enumerate(standards.items(), 1):
            rows.append(f"""
                <tr>
                    <td>{i}</td>
                    <td>{item}</td>
                    <td>{info['unit']}</td>
                    <td>{info['criteria']}</td>
                    <td>{info['method']}</td>
                </tr>
            """)
        
        return f"""
        <table class="table">
            <thead>
                <tr>
                    <th>No.</th>
                    <th>시험항목</th>
                    <th>단위</th>
                    <th>기준값</th>
                    <th>시험방법</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
    
    def save_report_html(self, html_content: str, filename: str) -> str:
        """HTML 보고서 파일 저장"""
        filepath = f"{filename}.html"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return filepath
    
    def generate_summary_report(self, test_results: List[TestResult], project_name: str) -> Dict[str, Any]:
        """요약 보고서 데이터 생성"""
        summary = ProjectSummary.from_test_results(project_name, test_results)
        violations = [result for result in test_results if result.is_non_conforming()]
        
        # 위험도별 분류
        high_risk_items = []
        medium_risk_items = []
        low_risk_items = []
        
        for item, data in summary.test_items_summary.items():
            if data['rate'] >= 50:
                high_risk_items.append(item)
            elif data['rate'] >= 20:
                medium_risk_items.append(item)
            else:
                low_risk_items.append(item)
        
        return {
            'project_name': project_name,
            'analysis_period': summary.analysis_period,
            'total_samples': summary.total_samples,
            'total_tests': summary.total_tests,
            'violation_samples': summary.violation_samples,
            'violation_tests': summary.violation_tests,
            'violation_rate': summary.violation_rate,
            'violations': [
                {
                    'sample_name': v.sample_name,
                    'analysis_number': v.analysis_number,
                    'test_item': v.test_item,
                    'result': v.get_display_result(),
                    'unit': v.test_unit,
                    'criteria': v.standard_criteria
                } for v in violations
            ],
            'risk_analysis': {
                'high_risk': high_risk_items,
                'medium_risk': medium_risk_items,
                'low_risk': low_risk_items
            },
            'recommendations': self._generate_recommendations(summary, violations)
        }
    
    def _generate_recommendations(self, summary: ProjectSummary, violations: List[TestResult]) -> List[str]:
        """개선 권고사항 생성"""
        recommendations = []
        
        if summary.violation_rate > 30:
            recommendations.append("전체 부적합 비율이 30%를 초과합니다. 품질관리 프로세스 전반에 대한 검토가 필요합니다.")
        
        if summary.violation_rate > 50:
            recommendations.append("부적합 비율이 매우 높습니다. 긴급한 품질개선 조치가 필요합니다.")
        
        # 항목별 권고사항
        for item, data in summary.test_items_summary.items():
            if data['rate'] == 100:
                recommendations.append(f"{item} 항목에서 모든 시료가 부적합입니다. 해당 항목에 대한 즉시 조치가 필요합니다.")
            elif data['rate'] >= 50:
                recommendations.append(f"{item} 항목의 부적합 비율이 {data['rate']:.1f}%입니다. 해당 항목에 대한 집중 관리가 필요합니다.")
        
        if not recommendations:
            recommendations.append("전반적으로 양호한 품질 수준을 유지하고 있습니다. 현재 수준을 지속 유지하시기 바랍니다.")
        
        return recommendations

def test_report_generator():
    """보고서 생성기 테스트"""
    from data_processor import DataProcessor
    import pandas as pd
    
    # 샘플 데이터 생성
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
    
    # 데이터 처리
    processor = DataProcessor()
    test_results = []
    for _, row in df.iterrows():
        result = processor._row_to_test_result(row)
        if result:
            test_results.append(result)
    
    # 보고서 생성
    generator = ReportGenerator()
    
    print("📋 품질관리 보고서 생성 테스트")
    print("=" * 40)
    
    # HTML 보고서 생성
    html_content = generator.generate_quality_report_html(test_results, "COWAY_품질관리_PJT")
    filepath = generator.save_report_html(html_content, "quality_report_test")
    
    print(f"✅ HTML 보고서 생성 완료: {filepath}")
    print(f"   파일 크기: {len(html_content):,} 문자")
    
    # 요약 보고서 생성
    summary_report = generator.generate_summary_report(test_results, "COWAY_품질관리_PJT")
    
    print(f"✅ 요약 보고서 생성 완료")
    print(f"   프로젝트: {summary_report['project_name']}")
    print(f"   부적합 비율: {summary_report['violation_rate']:.1f}%")
    print(f"   부적합 항목: {len(summary_report['violations'])}건")
    print(f"   권고사항: {len(summary_report['recommendations'])}개")
    
    # 권고사항 출력
    print("\n📋 개선 권고사항:")
    for i, rec in enumerate(summary_report['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    return html_content, summary_report

if __name__ == "__main__":
    test_report_generator()