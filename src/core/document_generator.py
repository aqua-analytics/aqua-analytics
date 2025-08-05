"""
시험성적서 생성 시스템 (DocumentGenerator)
HTML 템플릿 기반 성적서 생성, 데이터 바인딩, 기준 초과 항목 하이라이트
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import re
from pathlib import Path
import base64
from io import BytesIO

try:
    from .data_models import TestResult, ProjectSummary, Standard
except ImportError:
    from data_models import TestResult, ProjectSummary, Standard


class DocumentGenerator:
    """시험성적서 생성 클래스"""
    
    def __init__(self, template_path: Optional[str] = None):
        """
        DocumentGenerator 초기화
        
        Args:
            template_path: HTML 템플릿 파일 경로 (선택사항)
        """
        self.template_path = template_path
        self.company_info = {
            'name': 'COWAY',
            'address': '서울특별시 중구 서소문로 40',
            'phone': '02-1588-5200',
            'email': 'quality@coway.co.kr',
            'website': 'www.coway.co.kr',
            'logo_url': 'https://www.coway.co.kr/images/common/logo.png'
        }
        
        # 기본 템플릿 스타일
        self.default_styles = self._get_default_styles()
    
    def generate_test_report_html(
        self, 
        test_results: List[TestResult], 
        project_name: str,
        report_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        시험성적서 HTML 생성
        
        Args:
            test_results: 시험 결과 데이터 리스트
            project_name: 프로젝트명
            report_metadata: 추가 메타데이터 (접수번호, 의뢰자 정보 등)
            
        Returns:
            생성된 HTML 문자열
        """
        if not test_results:
            raise ValueError("시험 결과 데이터가 없습니다.")
        
        # 메타데이터 기본값 설정
        metadata = self._prepare_metadata(report_metadata, test_results, project_name)
        
        # 프로젝트 요약 생성
        summary = ProjectSummary.from_test_results(project_name, test_results)
        
        # 부적합 항목 추출 및 하이라이트 준비
        violations = [result for result in test_results if result.is_non_conforming()]
        highlighted_results = self._prepare_highlighted_results(test_results)
        
        # HTML 템플릿 생성
        html_content = self._build_report_template(
            metadata=metadata,
            summary=summary,
            test_results=highlighted_results,
            violations=violations
        )
        
        return html_content
    
    def apply_data_binding(
        self, 
        template_content: str, 
        data_context: Dict[str, Any]
    ) -> str:
        """
        템플릿에 데이터 바인딩 적용
        
        Args:
            template_content: HTML 템플릿 내용
            data_context: 바인딩할 데이터 컨텍스트
            
        Returns:
            데이터가 바인딩된 HTML 문자열
        """
        bound_content = template_content
        
        # ${variable} 형태의 플레이스홀더 치환
        for key, value in data_context.items():
            placeholder = f"${{{key}}}"
            if placeholder in bound_content:
                bound_content = bound_content.replace(placeholder, str(value))
        
        # {{variable}} 형태의 플레이스홀더 치환 (이중 중괄호)
        for key, value in data_context.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in bound_content:
                bound_content = bound_content.replace(placeholder, str(value))
        
        return bound_content
    
    def highlight_violations(
        self, 
        test_results: List[TestResult]
    ) -> List[Dict[str, Any]]:
        """
        기준 초과 항목 자동 하이라이트 처리
        
        Args:
            test_results: 시험 결과 데이터 리스트
            
        Returns:
            하이라이트 정보가 포함된 결과 리스트
        """
        highlighted_results = []
        
        for result in test_results:
            result_data = {
                'original': result,
                'sample_name': result.sample_name,
                'analysis_number': result.analysis_number,
                'test_item': result.test_item,
                'result_display': result.get_display_result(),
                'unit': result.test_unit,
                'criteria': result.standard_criteria,
                'status': self._normalize_status(result.standard_excess),
                'is_violation': result.is_non_conforming(),
                'highlight_class': 'violation-highlight' if result.is_non_conforming() else 'normal-result',
                'status_class': 'status-fail' if result.is_non_conforming() else 'status-pass',
                'tester': result.tester,
                'input_datetime': result.input_datetime.strftime('%Y-%m-%d %H:%M') if result.input_datetime and hasattr(result.input_datetime, 'strftime') else str(result.input_datetime) if result.input_datetime else '',
                'test_standard': result.test_standard
            }
            
            # 초과 배수 계산 (부적합인 경우)
            if result.is_non_conforming():
                excess_ratio = self._calculate_excess_ratio(result)
                result_data['excess_ratio'] = excess_ratio
                result_data['risk_level'] = self._determine_risk_level(excess_ratio)
            else:
                result_data['excess_ratio'] = 0.0
                result_data['risk_level'] = 'SAFE'
            
            highlighted_results.append(result_data)
        
        return highlighted_results
    
    def generate_pdf_bytes(self, html_content: str) -> bytes:
        """
        HTML을 PDF로 변환 (향후 구현)
        
        Args:
            html_content: 변환할 HTML 내용
            
        Returns:
            PDF 바이트 데이터
        """
        # TODO: WeasyPrint 또는 Playwright를 사용한 PDF 생성
        # 현재는 HTML을 바이트로 반환 (임시)
        return html_content.encode('utf-8')
    
    def save_report_file(
        self, 
        content: str, 
        filename: str, 
        output_dir: str = "reports"
    ) -> str:
        """
        보고서 파일 저장
        
        Args:
            content: 저장할 내용
            filename: 파일명 (확장자 제외)
            output_dir: 출력 디렉토리
            
        Returns:
            저장된 파일 경로
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        file_path = output_path / f"{filename}.html"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def _prepare_metadata(
        self, 
        metadata: Optional[Dict[str, Any]], 
        test_results: List[TestResult], 
        project_name: str
    ) -> Dict[str, Any]:
        """메타데이터 준비"""
        default_metadata = {
            'report_title': f'{project_name} 시험성적서',
            'report_number': f'RPT-{datetime.now().strftime("%Y%m%d")}-{len(test_results):03d}',
            'client_name': '코웨이 주식회사',
            'client_address': '서울특별시 중구 서소문로 40',
            'request_date': datetime.now().strftime('%Y년 %m월 %d일'),
            'report_date': datetime.now().strftime('%Y년 %m월 %d일'),
            'test_period': self._extract_test_period(test_results),
            'total_samples': len(set(r.sample_name for r in test_results)),
            'total_tests': len(test_results),
            'tester_name': test_results[0].tester if test_results else '시험자',
            'approver_name': '품질관리책임자',
            'lab_name': 'COWAY 품질관리센터'
        }
        
        if metadata:
            default_metadata.update(metadata)
        
        return default_metadata
    
    def _prepare_highlighted_results(self, test_results: List[TestResult]) -> List[Dict[str, Any]]:
        """하이라이트된 결과 데이터 준비"""
        return self.highlight_violations(test_results)
    
    def _build_report_template(
        self,
        metadata: Dict[str, Any],
        summary: ProjectSummary,
        test_results: List[Dict[str, Any]],
        violations: List[TestResult]
    ) -> str:
        """보고서 HTML 템플릿 구성"""
        
        # 헤더 섹션
        header_html = self._build_header_section(metadata)
        
        # 요약 정보 섹션
        summary_html = self._build_summary_section(summary, metadata)
        
        # 시험 결과 테이블 섹션
        results_table_html = self._build_results_table(test_results)
        
        # 부적합 항목 상세 섹션
        violations_html = self._build_violations_section(violations)
        
        # 기준값 정보 섹션
        standards_html = self._build_standards_section(test_results)
        
        # 푸터 섹션
        footer_html = self._build_footer_section(metadata)
        
        # 전체 HTML 조합
        full_html = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{metadata['report_title']}</title>
            <style>{self.default_styles}</style>
        </head>
        <body>
            <div class="report-container">
                {header_html}
                {summary_html}
                {results_table_html}
                {violations_html}
                {standards_html}
                {footer_html}
            </div>
            
            <script>
                // 인쇄 기능
                function printReport() {{
                    window.print();
                }}
                
                // PDF 저장 기능 (브라우저 인쇄 대화상자 사용)
                function saveAsPDF() {{
                    window.print();
                }}
            </script>
        </body>
        </html>
        """
        
        return full_html
    
    def _build_header_section(self, metadata: Dict[str, Any]) -> str:
        """헤더 섹션 HTML 생성"""
        return f"""
        <header class="report-header">
            <div class="header-content">
                <div class="company-info">
                    <h1 class="company-name">{self.company_info['name']}</h1>
                    <p class="company-address">{self.company_info['address']}</p>
                    <p class="company-contact">Tel: {self.company_info['phone']} | Email: {self.company_info['email']}</p>
                </div>
                <div class="report-info">
                    <h2 class="report-title">{metadata['report_title']}</h2>
                    <p class="report-number">보고서 번호: {metadata['report_number']}</p>
                    <p class="report-date">발행일: {metadata['report_date']}</p>
                </div>
            </div>
        </header>
        """
    
    def _build_summary_section(self, summary: ProjectSummary, metadata: Dict[str, Any]) -> str:
        """요약 정보 섹션 HTML 생성"""
        return f"""
        <section class="summary-section">
            <h3 class="section-title">시험 개요</h3>
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="label">의뢰자:</span>
                    <span class="value">{metadata['client_name']}</span>
                </div>
                <div class="summary-item">
                    <span class="label">시험 기간:</span>
                    <span class="value">{metadata['test_period']}</span>
                </div>
                <div class="summary-item">
                    <span class="label">총 시료 수:</span>
                    <span class="value">{summary.total_samples}개</span>
                </div>
                <div class="summary-item">
                    <span class="label">총 시험 건수:</span>
                    <span class="value">{summary.total_tests}건</span>
                </div>
                <div class="summary-item">
                    <span class="label">부적합 건수:</span>
                    <span class="value violation-text">{summary.violation_tests}건</span>
                </div>
                <div class="summary-item">
                    <span class="label">부적합 비율:</span>
                    <span class="value violation-text">{summary.violation_rate:.1f}%</span>
                </div>
            </div>
        </section>
        """
    
    def _build_results_table(self, test_results: List[Dict[str, Any]]) -> str:
        """시험 결과 테이블 HTML 생성"""
        table_rows = []
        
        for i, result in enumerate(test_results, 1):
            row_class = result['highlight_class']
            status_class = result['status_class']
            
            table_rows.append(f"""
            <tr class="{row_class}">
                <td class="text-center">{i}</td>
                <td>{result['sample_name']}</td>
                <td>{result['analysis_number']}</td>
                <td>{result['test_item']}</td>
                <td class="text-right font-bold">{result['result_display']} {result['unit']}</td>
                <td>{result['criteria']}</td>
                <td class="text-center">
                    <span class="status-badge {status_class}">{result['status']}</span>
                </td>
                <td>{result['tester']}</td>
            </tr>
            """)
        
        return f"""
        <section class="results-section">
            <h3 class="section-title">시험 결과</h3>
            <div class="table-container">
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>No.</th>
                            <th>시료명</th>
                            <th>접수번호</th>
                            <th>시험항목</th>
                            <th>결과</th>
                            <th>기준값</th>
                            <th>판정</th>
                            <th>시험자</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(table_rows)}
                    </tbody>
                </table>
            </div>
        </section>
        """
    
    def _build_violations_section(self, violations: List[TestResult]) -> str:
        """부적합 항목 상세 섹션 HTML 생성"""
        if not violations:
            return f"""
            <section class="violations-section">
                <h3 class="section-title">부적합 항목</h3>
                <div class="no-violations">
                    <p class="success-message">🎉 모든 시험 항목이 기준에 적합합니다.</p>
                </div>
            </section>
            """
        
        violation_rows = []
        for i, violation in enumerate(violations, 1):
            excess_ratio = self._calculate_excess_ratio(violation)
            risk_level = self._determine_risk_level(excess_ratio)
            
            violation_rows.append(f"""
            <tr class="violation-row">
                <td class="text-center">{i}</td>
                <td>{violation.sample_name}</td>
                <td>{violation.test_item}</td>
                <td class="text-right font-bold violation-value">
                    {violation.get_display_result()} {violation.test_unit}
                </td>
                <td>{violation.standard_criteria}</td>
                <td class="text-right">{excess_ratio:.2f}배</td>
                <td class="text-center">
                    <span class="risk-badge risk-{risk_level.lower()}">{risk_level}</span>
                </td>
            </tr>
            """)
        
        return f"""
        <section class="violations-section">
            <h3 class="section-title">⚠️ 부적합 항목 상세</h3>
            <div class="table-container">
                <table class="violations-table">
                    <thead>
                        <tr>
                            <th>No.</th>
                            <th>시료명</th>
                            <th>시험항목</th>
                            <th>초과 결과</th>
                            <th>기준값</th>
                            <th>초과 배수</th>
                            <th>위험도</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(violation_rows)}
                    </tbody>
                </table>
            </div>
            <div class="violation-summary">
                <p><strong>총 {len(violations)}건의 부적합 항목이 발견되었습니다.</strong></p>
            </div>
        </section>
        """
    
    def _build_standards_section(self, test_results: List[Dict[str, Any]]) -> str:
        """기준값 정보 섹션 HTML 생성"""
        # 고유한 시험항목별 기준값 정보 추출
        standards_info = {}
        for result in test_results:
            item = result['test_item']
            if item not in standards_info:
                standards_info[item] = {
                    'unit': result['unit'],
                    'criteria': result['criteria'],
                    'test_standard': result.get('test_standard', 'N/A')
                }
        
        standards_rows = []
        for i, (item, info) in enumerate(standards_info.items(), 1):
            standards_rows.append(f"""
            <tr>
                <td class="text-center">{i}</td>
                <td>{item}</td>
                <td class="text-center">{info['unit']}</td>
                <td>{info['criteria']}</td>
                <td>{info['test_standard']}</td>
            </tr>
            """)
        
        return f"""
        <section class="standards-section">
            <h3 class="section-title">시험 기준값 정보</h3>
            <div class="table-container">
                <table class="standards-table">
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
                        {''.join(standards_rows)}
                    </tbody>
                </table>
            </div>
        </section>
        """
    
    def _build_footer_section(self, metadata: Dict[str, Any]) -> str:
        """푸터 섹션 HTML 생성"""
        return f"""
        <footer class="report-footer">
            <div class="footer-content">
                <div class="signatures">
                    <div class="signature-block">
                        <p class="signature-label">시험자</p>
                        <p class="signature-name">{metadata['tester_name']}</p>
                        <div class="signature-line"></div>
                    </div>
                    <div class="signature-block">
                        <p class="signature-label">승인자</p>
                        <p class="signature-name">{metadata['approver_name']}</p>
                        <div class="signature-line"></div>
                    </div>
                </div>
                <div class="footer-info">
                    <p class="lab-name">{metadata['lab_name']}</p>
                    <p class="generation-date">보고서 생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
                </div>
                <div class="footer-notes">
                    <h4>주의사항</h4>
                    <ul>
                        <li>본 성적서는 시험 의뢰된 시료에 한하여 유효합니다.</li>
                        <li>시험 결과는 시험 당시의 시료 상태를 나타냅니다.</li>
                        <li>부적합 항목에 대해서는 즉시 개선 조치를 취하시기 바랍니다.</li>
                        <li>본 성적서의 일부 발췌나 복사는 당사의 승인 없이 불가합니다.</li>
                    </ul>
                </div>
            </div>
        </footer>
        """
    
    def _extract_test_period(self, test_results: List[TestResult]) -> str:
        """시험 기간 추출"""
        dates = [r.input_datetime for r in test_results if r.input_datetime]
        if not dates:
            return "시험 기간 정보 없음"
        
        min_date = min(dates).strftime('%Y.%m.%d') if hasattr(min(dates), 'strftime') else str(min(dates))
        max_date = max(dates).strftime('%Y.%m.%d') if hasattr(max(dates), 'strftime') else str(max(dates))
        
        if min_date == max_date:
            return f"{min_date}"
        else:
            return f"{min_date} ~ {max_date}"
    
    def _normalize_status(self, status: str) -> str:
        """상태값 정규화"""
        if status in ['부적합', '초과', 'FAIL']:
            return '부적합'
        elif status in ['적합', '합격', 'PASS']:
            return '적합'
        else:
            return '적합'  # 기본값
    
    def _calculate_excess_ratio(self, result: TestResult) -> float:
        """초과 배수 계산"""
        try:
            numeric_result = result.get_numeric_result()
            if numeric_result is None:
                return 0.0
            
            # 기준값 추출
            standard = Standard.from_test_result(result)
            if standard.limit_value <= 0:
                return 0.0
            
            return numeric_result / standard.limit_value
        except (ValueError, ZeroDivisionError):
            return 0.0
    
    def _determine_risk_level(self, excess_ratio: float) -> str:
        """위험도 결정"""
        if excess_ratio >= 5.0:
            return 'HIGH'
        elif excess_ratio >= 2.0:
            return 'MEDIUM'
        elif excess_ratio > 1.0:
            return 'LOW'
        else:
            return 'SAFE'
    
    def _get_default_styles(self) -> str:
        """기본 CSS 스타일 반환"""
        return """
        /* 시험성적서 기본 스타일 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        
        .report-container {
            max-width: 1200px;
            margin: 20px auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* 헤더 스타일 */
        .report-header {
            background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            color: white;
            padding: 30px;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        
        .company-name {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .company-address, .company-contact {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .report-title {
            font-size: 24px;
            font-weight: bold;
            text-align: right;
            margin-bottom: 10px;
        }
        
        .report-number, .report-date {
            font-size: 14px;
            text-align: right;
            opacity: 0.9;
        }
        
        /* 섹션 공통 스타일 */
        .summary-section, .results-section, .violations-section, .standards-section {
            padding: 30px;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .section-title {
            font-size: 20px;
            font-weight: bold;
            color: #1f2937;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #2563eb;
        }
        
        /* 요약 정보 스타일 */
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }
        
        .summary-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 15px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #2563eb;
        }
        
        .summary-item .label {
            font-weight: 600;
            color: #4b5563;
        }
        
        .summary-item .value {
            font-weight: bold;
            color: #1f2937;
        }
        
        .violation-text {
            color: #dc2626 !important;
        }
        
        /* 테이블 공통 스타일 */
        .table-container {
            overflow-x: auto;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }
        
        .results-table, .violations-table, .standards-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        
        .results-table th, .violations-table th, .standards-table th {
            background: #f3f4f6;
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #d1d5db;
        }
        
        .results-table td, .violations-table td, .standards-table td {
            padding: 10px 8px;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .results-table tr:hover, .violations-table tr:hover, .standards-table tr:hover {
            background: #f9fafb;
        }
        
        /* 하이라이트 스타일 */
        .violation-highlight {
            background-color: #fef2f2 !important;
        }
        
        .violation-highlight:hover {
            background-color: #fee2e2 !important;
        }
        
        .normal-result {
            background-color: white;
        }
        
        .violation-value {
            color: #dc2626;
        }
        
        /* 상태 배지 스타일 */
        .status-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-pass {
            background: #d1fae5;
            color: #065f46;
        }
        
        .status-fail {
            background: #fee2e2;
            color: #991b1b;
        }
        
        /* 위험도 배지 스타일 */
        .risk-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
        }
        
        .risk-high {
            background: #fecaca;
            color: #991b1b;
        }
        
        .risk-medium {
            background: #fed7aa;
            color: #9a3412;
        }
        
        .risk-low {
            background: #fef3c7;
            color: #92400e;
        }
        
        .risk-safe {
            background: #d1fae5;
            color: #065f46;
        }
        
        /* 부적합 섹션 스타일 */
        .no-violations {
            text-align: center;
            padding: 40px;
        }
        
        .success-message {
            font-size: 18px;
            color: #059669;
            font-weight: 600;
        }
        
        .violation-summary {
            margin-top: 15px;
            padding: 15px;
            background: #fef2f2;
            border-left: 4px solid #dc2626;
            border-radius: 4px;
        }
        
        /* 푸터 스타일 */
        .report-footer {
            background: #f8f9fa;
            padding: 30px;
        }
        
        .signatures {
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
        }
        
        .signature-block {
            text-align: center;
        }
        
        .signature-label {
            font-weight: 600;
            margin-bottom: 10px;
            color: #4b5563;
        }
        
        .signature-name {
            font-weight: bold;
            margin-bottom: 20px;
        }
        
        .signature-line {
            width: 150px;
            height: 1px;
            background: #9ca3af;
            margin: 0 auto;
        }
        
        .footer-info {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .lab-name {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .generation-date {
            font-size: 14px;
            color: #6b7280;
        }
        
        .footer-notes h4 {
            font-size: 16px;
            margin-bottom: 10px;
            color: #374151;
        }
        
        .footer-notes ul {
            list-style-type: disc;
            padding-left: 20px;
        }
        
        .footer-notes li {
            margin-bottom: 5px;
            font-size: 14px;
            color: #4b5563;
        }
        
        /* 유틸리티 클래스 */
        .text-center { text-align: center; }
        .text-right { text-align: right; }
        .font-bold { font-weight: bold; }
        
        /* 인쇄 스타일 */
        @media print {
            body {
                background: white;
            }
            
            .report-container {
                box-shadow: none;
                margin: 0;
            }
            
            .report-header {
                background: #2563eb !important;
                -webkit-print-color-adjust: exact;
            }
            
            .violation-highlight {
                background-color: #fef2f2 !important;
                -webkit-print-color-adjust: exact;
            }
        }
        """


def test_document_generator():
    """DocumentGenerator 테스트 함수"""
    from data_processor import DataProcessor
    import pandas as pd
    
    print("📄 DocumentGenerator 테스트 시작")
    print("=" * 50)
    
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
    
    # DocumentGenerator 테스트
    generator = DocumentGenerator()
    
    print(f"✅ DocumentGenerator 초기화 완료")
    print(f"   회사 정보: {generator.company_info['name']}")
    print(f"   테스트 데이터: {len(test_results)}건")
    
    # 1. 하이라이트 기능 테스트
    highlighted_results = generator.highlight_violations(test_results)
    violations = [r for r in highlighted_results if r['is_violation']]
    
    print(f"✅ 하이라이트 기능 테스트 완료")
    print(f"   전체 결과: {len(highlighted_results)}건")
    print(f"   부적합 항목: {len(violations)}건")
    
    # 2. HTML 보고서 생성 테스트
    html_content = generator.generate_test_report_html(
        test_results=test_results,
        project_name="COWAY_품질관리_테스트",
        report_metadata={
            'client_name': '코웨이 주식회사',
            'tester_name': '김화빈',
            'approver_name': '이현풍'
        }
    )
    
    print(f"✅ HTML 보고서 생성 완료")
    print(f"   HTML 크기: {len(html_content):,} 문자")
    
    # 3. 파일 저장 테스트
    saved_path = generator.save_report_file(
        content=html_content,
        filename=f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        output_dir="reports"
    )
    
    print(f"✅ 파일 저장 완료: {saved_path}")
    
    # 4. 데이터 바인딩 테스트
    template = "안녕하세요 ${client_name}님, 총 ${total_tests}건의 시험이 완료되었습니다."
    bound_content = generator.apply_data_binding(template, {
        'client_name': '코웨이',
        'total_tests': len(test_results)
    })
    
    print(f"✅ 데이터 바인딩 테스트 완료")
    print(f"   결과: {bound_content}")
    
    print("\n📊 생성된 보고서 요약:")
    print(f"   - 전체 시험: {len(test_results)}건")
    print(f"   - 부적합: {len([r for r in test_results if r.is_non_conforming()])}건")
    print(f"   - 부적합 비율: {len([r for r in test_results if r.is_non_conforming()]) / len(test_results) * 100:.1f}%")
    
    return html_content, saved_path


if __name__ == "__main__":
    test_document_generator()