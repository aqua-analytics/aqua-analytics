"""
시험성적서 미리보기 모달 컴포넌트
모달 UI, PDF 생성, 다운로드, 인쇄 기능 제공
"""

from typing import List, Dict, Any, Optional
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import base64
import json

try:
    from ..core.data_models import TestResult, ProjectSummary
    from ..core.document_generator import DocumentGenerator
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
    from data_models import TestResult, ProjectSummary
    from document_generator import DocumentGenerator


class ReportPreviewModal:
    """시험성적서 미리보기 모달 클래스"""
    
    def __init__(self):
        """ReportPreviewModal 초기화"""
        self.document_generator = DocumentGenerator()
        self.modal_id = "report-preview-modal"
        self.is_open = False
        
    def render_modal_html(
        self, 
        test_results: List[TestResult], 
        project_name: str,
        report_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        미리보기 모달 HTML 생성
        
        Args:
            test_results: 시험 결과 데이터
            project_name: 프로젝트명
            report_metadata: 보고서 메타데이터
            
        Returns:
            모달 HTML 문자열
        """
        # 보고서 HTML 생성
        report_html = self.document_generator.generate_test_report_html(
            test_results=test_results,
            project_name=project_name,
            report_metadata=report_metadata
        )
        
        # 모달 HTML 구성
        modal_html = f"""
        <!-- 시험성적서 미리보기 모달 -->
        <div id="{self.modal_id}" class="fixed inset-0 z-50 items-center justify-center hidden">
            <div class="modal-backdrop fixed inset-0 bg-black bg-opacity-50" onclick="closeReportModal()"></div>
            <div class="bg-white rounded-lg shadow-xl w-11/12 max-w-6xl h-5/6 relative flex flex-col">
                <!-- 모달 헤더 -->
                <div class="p-4 border-b flex justify-between items-center bg-slate-50 rounded-t-lg">
                    <div>
                        <h3 class="text-lg font-bold text-slate-800">시험성적서 미리보기</h3>
                        <p class="text-sm text-slate-600">{project_name}</p>
                    </div>
                    <button 
                        id="close-report-btn" 
                        onclick="closeReportModal()"
                        class="text-slate-500 hover:text-slate-800 text-2xl font-bold w-8 h-8 flex items-center justify-center rounded-full hover:bg-slate-200 transition"
                    >
                        &times;
                    </button>
                </div>
                
                <!-- 모달 콘텐츠 (보고서 미리보기) -->
                <div class="p-4 flex-grow overflow-y-auto bg-slate-100">
                    <div class="bg-white shadow-lg rounded-lg overflow-hidden">
                        <div id="report-preview-content" class="report-preview-container">
                            {report_html}
                        </div>
                    </div>
                </div>
                
                <!-- 모달 푸터 (액션 버튼들) -->
                <div class="p-4 border-t bg-slate-50 rounded-b-lg">
                    <div class="flex justify-between items-center">
                        <div class="text-sm text-slate-600">
                            <span>생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</span>
                        </div>
                        <div class="space-x-2">
                            <button 
                                onclick="printReport()" 
                                class="bg-slate-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-slate-600 transition flex items-center space-x-2"
                            >
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path>
                                </svg>
                                <span>인쇄</span>
                            </button>
                            <button 
                                onclick="downloadPDF()" 
                                class="bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700 transition flex items-center space-x-2"
                            >
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                </svg>
                                <span>PDF로 저장</span>
                            </button>
                            <button 
                                onclick="downloadHTML()" 
                                class="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-blue-700 transition flex items-center space-x-2"
                            >
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                                </svg>
                                <span>HTML 저장</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
        /* 모달 전용 스타일 */
        .report-preview-container {{
            transform: scale(0.8);
            transform-origin: top left;
            width: 125%;
            height: auto;
        }}
        
        .report-preview-container .report-container {{
            margin: 0;
            box-shadow: none;
            border-radius: 0;
        }}
        
        /* 모달 애니메이션 */
        #{self.modal_id} {{
            transition: opacity 0.3s ease-in-out;
        }}
        
        #{self.modal_id}.show {{
            opacity: 1;
        }}
        
        #{self.modal_id} > div:nth-child(2) {{
            transition: transform 0.3s ease-in-out;
            transform: scale(0.9);
        }}
        
        #{self.modal_id}.show > div:nth-child(2) {{
            transform: scale(1);
        }}
        
        /* 스크롤바 스타일링 */
        .overflow-y-auto::-webkit-scrollbar {{
            width: 8px;
        }}
        
        .overflow-y-auto::-webkit-scrollbar-track {{
            background: #f1f5f9;
        }}
        
        .overflow-y-auto::-webkit-scrollbar-thumb {{
            background: #cbd5e1;
            border-radius: 4px;
        }}
        
        .overflow-y-auto::-webkit-scrollbar-thumb:hover {{
            background: #94a3b8;
        }}
        </style>
        
        <script>
        // 모달 관련 JavaScript 함수들
        
        // 모달 열기
        function showReportModal() {{
            const modal = document.getElementById('{self.modal_id}');
            if (modal) {{
                modal.classList.remove('hidden');
                modal.classList.add('flex');
                setTimeout(() => {{
                    modal.classList.add('show');
                }}, 10);
                
                // 바디 스크롤 방지
                document.body.style.overflow = 'hidden';
            }}
        }}
        
        // 모달 닫기
        function closeReportModal() {{
            const modal = document.getElementById('{self.modal_id}');
            if (modal) {{
                modal.classList.remove('show');
                setTimeout(() => {{
                    modal.classList.add('hidden');
                    modal.classList.remove('flex');
                }}, 300);
                
                // 바디 스크롤 복원
                document.body.style.overflow = 'auto';
            }}
        }}
        
        // 인쇄 기능
        function printReport() {{
            const reportContent = document.getElementById('report-preview-content');
            if (reportContent) {{
                const printWindow = window.open('', '_blank');
                printWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>시험성적서 - {project_name}</title>
                        <style>
                            body {{ margin: 0; padding: 20px; font-family: 'Malgun Gothic', sans-serif; }}
                            @media print {{ 
                                body {{ padding: 0; }}
                                .report-container {{ box-shadow: none !important; }}
                            }}
                        </style>
                    </head>
                    <body>
                        ${{reportContent.innerHTML}}
                    </body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.focus();
                setTimeout(() => {{
                    printWindow.print();
                    printWindow.close();
                }}, 500);
            }}
        }}
        
        // PDF 다운로드 (브라우저 인쇄 대화상자 사용)
        function downloadPDF() {{
            // 현재는 브라우저의 인쇄 기능을 사용하여 PDF 저장
            // 사용자가 인쇄 대화상자에서 "PDF로 저장" 선택 가능
            printReport();
            
            // TODO: 향후 서버사이드 PDF 생성 구현
            // fetch('/api/generate-pdf', {{
            //     method: 'POST',
            //     headers: {{ 'Content-Type': 'application/json' }},
            //     body: JSON.stringify({{ reportData: ... }})
            // }}).then(response => response.blob())
            //   .then(blob => {{
            //       const url = window.URL.createObjectURL(blob);
            //       const a = document.createElement('a');
            //       a.href = url;
            //       a.download = 'test_report.pdf';
            //       a.click();
            //   }});
        }}
        
        // HTML 다운로드
        function downloadHTML() {{
            const reportContent = document.getElementById('report-preview-content');
            if (reportContent) {{
                const htmlContent = `
                    <!DOCTYPE html>
                    <html lang="ko">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>시험성적서 - {project_name}</title>
                    </head>
                    <body>
                        ${{reportContent.innerHTML}}
                    </body>
                    </html>
                `;
                
                const blob = new Blob([htmlContent], {{ type: 'text/html;charset=utf-8' }});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `test_report_{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            }}
        }}
        
        // ESC 키로 모달 닫기
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                closeReportModal();
            }}
        }});
        
        // 전역 함수로 등록 (외부에서 호출 가능)
        window.showReportModal = showReportModal;
        window.closeReportModal = closeReportModal;
        window.printReport = printReport;
        window.downloadPDF = downloadPDF;
        window.downloadHTML = downloadHTML;
        </script>
        """
        
        return modal_html
    
    def render_streamlit_modal(
        self, 
        test_results: List[TestResult], 
        project_name: str,
        report_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Streamlit에서 모달 렌더링
        
        Args:
            test_results: 시험 결과 데이터
            project_name: 프로젝트명
            report_metadata: 보고서 메타데이터
        """
        # 모달 HTML 생성
        modal_html = self.render_modal_html(test_results, project_name, report_metadata)
        
        # Streamlit components로 렌더링
        components.html(modal_html, height=0, scrolling=False)
    
    def generate_modal_trigger_button(self, button_text: str = "시험성적서 미리보기") -> str:
        """
        모달을 여는 트리거 버튼 HTML 생성
        
        Args:
            button_text: 버튼 텍스트
            
        Returns:
            버튼 HTML 문자열
        """
        return f"""
        <button 
            onclick="showReportModal()" 
            class="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-blue-700 transition flex items-center space-x-2"
        >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <span>{button_text}</span>
        </button>
        """
    
    def integrate_with_template(
        self, 
        base_template: str, 
        test_results: List[TestResult], 
        project_name: str,
        report_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        기존 HTML 템플릿에 모달 통합
        
        Args:
            base_template: 기존 HTML 템플릿
            test_results: 시험 결과 데이터
            project_name: 프로젝트명
            report_metadata: 보고서 메타데이터
            
        Returns:
            모달이 통합된 HTML 템플릿
        """
        # 모달 HTML 생성
        modal_html = self.render_modal_html(test_results, project_name, report_metadata)
        
        # 기존 템플릿에서 </body> 태그 찾기
        body_end = base_template.rfind('</body>')
        
        if body_end != -1:
            # </body> 태그 앞에 모달 HTML 삽입
            integrated_template = (
                base_template[:body_end] + 
                modal_html + 
                base_template[body_end:]
            )
        else:
            # </body> 태그가 없으면 끝에 추가
            integrated_template = base_template + modal_html
        
        return integrated_template
    
    def create_streamlit_interface(
        self, 
        test_results: List[TestResult], 
        project_name: str,
        report_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Streamlit 인터페이스 생성
        
        Args:
            test_results: 시험 결과 데이터
            project_name: 프로젝트명
            report_metadata: 보고서 메타데이터
        """
        st.subheader("📄 시험성적서 미리보기")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔍 미리보기", use_container_width=True):
                # 보고서 HTML 생성
                report_html = self.document_generator.generate_test_report_html(
                    test_results=test_results,
                    project_name=project_name,
                    report_metadata=report_metadata
                )
                
                # Streamlit에서 HTML 표시
                st.components.v1.html(report_html, height=800, scrolling=True)
        
        with col2:
            if st.button("🖨️ 인쇄용 HTML", use_container_width=True):
                # 인쇄용 HTML 생성 및 다운로드
                report_html = self.document_generator.generate_test_report_html(
                    test_results=test_results,
                    project_name=project_name,
                    report_metadata=report_metadata
                )
                
                st.download_button(
                    label="📥 HTML 다운로드",
                    data=report_html,
                    file_name=f"test_report_{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    use_container_width=True
                )
        
        with col3:
            if st.button("📊 요약 보고서", use_container_width=True):
                # 요약 정보 표시
                summary = ProjectSummary.from_test_results(project_name, test_results)
                
                st.info(f"""
                **프로젝트 요약**
                - 총 시료: {summary.total_samples}개
                - 총 시험: {summary.total_tests}건
                - 부적합: {summary.violation_tests}건 ({summary.violation_rate:.1f}%)
                """)


def test_report_preview_modal():
    """ReportPreviewModal 테스트 함수"""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
    
    from data_models import TestResult
    from data_processor import DataProcessor
    import pandas as pd
    
    print("🖼️ ReportPreviewModal 테스트 시작")
    print("=" * 50)
    
    # 샘플 데이터 생성
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
        '기준': ['0.0006 mg/L 이하', '0.0006 mg/L 이하', '0.1 ng/L 이하', '0.0006 mg/L 이하', '0.0006 mg/L 이하'],
        '입력일시': ['2025-01-23 09:56'] * 5
    }
    
    df = pd.DataFrame(sample_data)
    
    # 데이터 처리
    processor = DataProcessor()
    test_results = []
    for _, row in df.iterrows():
        result = processor._row_to_test_result(row)
        if result:
            test_results.append(result)
    
    # ReportPreviewModal 테스트
    modal = ReportPreviewModal()
    
    print(f"✅ ReportPreviewModal 초기화 완료")
    print(f"   모달 ID: {modal.modal_id}")
    print(f"   테스트 데이터: {len(test_results)}건")
    
    # 1. 모달 HTML 생성 테스트
    modal_html = modal.render_modal_html(
        test_results=test_results,
        project_name="COWAY_품질관리_테스트",
        report_metadata={
            'client_name': '코웨이 주식회사',
            'tester_name': '김화빈'
        }
    )
    
    print(f"✅ 모달 HTML 생성 완료")
    print(f"   HTML 크기: {len(modal_html):,} 문자")
    
    # 2. 트리거 버튼 생성 테스트
    button_html = modal.generate_modal_trigger_button("성적서 보기")
    
    print(f"✅ 트리거 버튼 생성 완료")
    print(f"   버튼 HTML: {len(button_html)} 문자")
    
    # 3. 템플릿 통합 테스트
    base_template = """
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body>
        <h1>기존 콘텐츠</h1>
    </body>
    </html>
    """
    
    integrated_template = modal.integrate_with_template(
        base_template=base_template,
        test_results=test_results,
        project_name="COWAY_품질관리_테스트"
    )
    
    print(f"✅ 템플릿 통합 완료")
    print(f"   통합 템플릿 크기: {len(integrated_template):,} 문자")
    
    # 4. 파일 저장 테스트
    output_path = f"reports/modal_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    os.makedirs("reports", exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(integrated_template)
    
    print(f"✅ 테스트 파일 저장 완료: {output_path}")
    
    print("\n📊 모달 기능 요약:")
    print(f"   - 미리보기: HTML 렌더링")
    print(f"   - 인쇄: JavaScript window.print()")
    print(f"   - PDF 저장: 브라우저 인쇄 대화상자")
    print(f"   - HTML 다운로드: Blob API 사용")
    
    return modal_html, integrated_template


if __name__ == "__main__":
    test_report_preview_modal()