"""
상세 정보 패널 시스템 구현
선택된 시료의 상세 정보와 시험 규격 정보를 표시하는 패널
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from datetime import datetime
from src.core.data_models import TestResult, Standard
import json


class DetailInfoPanel:
    """상세 정보 패널 클래스"""
    
    def __init__(self, height: int = 500):
        """
        상세 정보 패널 초기화
        
        Args:
            height: 패널 고정 높이 (픽셀)
        """
        self.height = height
        self.selected_test_result = None
        self.standard_info = None
        self._initialize_session_state()
    
    def _initialize_session_state(self) -> None:
        """Streamlit 세션 상태 초기화"""
        if 'detail_panel' not in st.session_state:
            st.session_state.detail_panel = {
                'selected_test_result': None,
                'show_standard_sheet': False,
                'selected_standard_doc': None,
                'panel_expanded': True
            }
    
    def render_detail_panel(self, selected_test_result: Optional[TestResult] = None) -> None:
        """
        상세 정보 패널 기본 구조 구현 (요구사항 4.1, 4.2)
        - 상세 정보 패널 레이아웃 구현
        - 시료 정보 섹션 구현
        - 시험 규격 정보 섹션 구현
        
        Args:
            selected_test_result: 선택된 시험 결과 데이터
        """
        if selected_test_result:
            self.selected_test_result = selected_test_result
            self.standard_info = Standard.from_test_result(selected_test_result)
            st.session_state.detail_panel['selected_test_result'] = selected_test_result
        
        # 패널 컨테이너
        with st.container():
            # 패널 헤더
            self._render_panel_header()
            
            # 선택된 데이터가 있는 경우에만 내용 표시
            if self.selected_test_result:
                # 시료 정보 섹션 (요구사항 4.1)
                self._render_sample_info_section()
                
                # 시험 규격 정보 섹션 (요구사항 4.2)
                self._render_test_standard_section()
                
                # 추가 정보 섹션
                self._render_additional_info_section()
            else:
                self._render_empty_state()
    
    def _render_panel_header(self) -> None:
        """패널 헤더 렌더링"""
        st.markdown(f"""
        <div style="background: white; padding: 1rem; border-radius: 8px 8px 0 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-bottom: 2px solid #e2e8f0;">
            <div style="display: flex; justify-content: between; align-items: center;">
                <h3 style="margin: 0; color: #1e293b; font-weight: 600; font-size: 1.25rem;">
                    📋 상세 정보
                </h3>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="background: #dbeafe; color: #1d4ed8; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                        {'선택됨' if self.selected_test_result else '선택 없음'}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_sample_info_section(self) -> None:
        """
        시료 정보 섹션 구현 (요구사항 4.1)
        선택된 시료의 기본 정보 표시
        """
        if not self.selected_test_result:
            return
        
        result = self.selected_test_result
        
        # 시료 정보 HTML 생성
        sample_info_html = f"""
        <div style="background: white; padding: 1.5rem; border-left: 4px solid #3b82f6; margin-bottom: 1rem;">
            <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-weight: 600; font-size: 1rem; display: flex; align-items: center;">
                🧪 시료 정보
            </h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="background: #f8fafc; padding: 0.75rem; border-radius: 6px;">
                    <p style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: #64748b; font-weight: 500;">시료명</p>
                    <p style="margin: 0; font-size: 0.875rem; color: #1e293b; font-weight: 600;">{result.sample_name}</p>
                </div>
                <div style="background: #f8fafc; padding: 0.75rem; border-radius: 6px;">
                    <p style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: #64748b; font-weight: 500;">분석번호</p>
                    <p style="margin: 0; font-size: 0.875rem; color: #1e293b; font-weight: 600; font-family: monospace;">{result.analysis_number}</p>
                </div>
                <div style="background: #f8fafc; padding: 0.75rem; border-radius: 6px;">
                    <p style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: #64748b; font-weight: 500;">시험자</p>
                    <p style="margin: 0; font-size: 0.875rem; color: #1e293b; font-weight: 600;">{result.tester}</p>
                </div>
                <div style="background: #f8fafc; padding: 0.75rem; border-radius: 6px;">
                    <p style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: #64748b; font-weight: 500;">입력일시</p>
                    <p style="margin: 0; font-size: 0.875rem; color: #1e293b; font-weight: 600; font-family: monospace;">
                        {result.input_datetime.strftime('%Y-%m-%d %H:%M') if result.input_datetime and hasattr(result.input_datetime, 'strftime') else str(result.input_datetime) if result.input_datetime else '정보 없음'}
                    </p>
                </div>
            </div>
            
            <!-- 시험 결과 요약 -->
            <div style="margin-top: 1rem; padding: 1rem; background: {'#fef2f2' if result.is_non_conforming() else '#f0fdf4'}; border-radius: 8px; border: 1px solid {'#fecaca' if result.is_non_conforming() else '#bbf7d0'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <p style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: #64748b; font-weight: 500;">시험 결과</p>
                        <p style="margin: 0; font-size: 1.125rem; color: {'#dc2626' if result.is_non_conforming() else '#16a34a'}; font-weight: 700;">
                            {result.get_display_result()} {result.test_unit}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <p style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: #64748b; font-weight: 500;">판정</p>
                        <span style="padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.875rem; font-weight: 600; 
                                     background: {'#fee2e2' if result.is_non_conforming() else '#dcfce7'}; 
                                     color: {'#dc2626' if result.is_non_conforming() else '#16a34a'};">
                            {'⚠️ ' if result.is_non_conforming() else '✅ '}{result.standard_excess}
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """
        
        st.markdown(sample_info_html, unsafe_allow_html=True)
    
    def _render_test_standard_section(self) -> None:
        """
        시험 규격 정보 섹션 구현 (요구사항 4.2)
        시험항목, 기준값, 관련 규격 정보 표시
        """
        if not self.selected_test_result or not self.standard_info:
            return
        
        result = self.selected_test_result
        standard = self.standard_info
        
        # 규격 문서명 생성 (실제로는 데이터베이스에서 조회)
        standard_doc_name = self._get_standard_document_name(result.test_item)
        
        # 시험 규격 정보 HTML 생성
        standard_info_html = f"""
        <div style="background: white; padding: 1.5rem; border-left: 4px solid #10b981; margin-bottom: 1rem;">
            <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-weight: 600; font-size: 1rem; display: flex; align-items: center;">
                📊 시험 규격 정보
            </h4>
            
            <div style="display: grid; gap: 1rem;">
                <!-- 시험 항목 정보 -->
                <div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; border: 1px solid #bbf7d0;">
                    <p style="margin: 0 0 0.5rem 0; font-size: 0.75rem; color: #166534; font-weight: 600;">시험 항목</p>
                    <p style="margin: 0; font-size: 0.875rem; color: #1e293b; font-weight: 600; line-height: 1.4;">
                        {result.test_item}
                    </p>
                </div>
                
                <!-- 기준값 정보 -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div style="background: #eff6ff; padding: 1rem; border-radius: 8px; border: 1px solid #bfdbfe;">
                        <p style="margin: 0 0 0.5rem 0; font-size: 0.75rem; color: #1d4ed8; font-weight: 600;">기준값</p>
                        <p style="margin: 0; font-size: 1rem; color: #1e293b; font-weight: 700; font-family: monospace;">
                            ≤ {standard.limit_value} {standard.unit}
                        </p>
                        <p style="margin: 0.25rem 0 0 0; font-size: 0.75rem; color: #64748b;">
                            {standard.limit_text}
                        </p>
                    </div>
                    
                    <div style="background: #fef3c7; padding: 1rem; border-radius: 8px; border: 1px solid #fcd34d;">
                        <p style="margin: 0 0 0.5rem 0; font-size: 0.75rem; color: #92400e; font-weight: 600;">시험 단위</p>
                        <p style="margin: 0; font-size: 1rem; color: #1e293b; font-weight: 700; font-family: monospace;">
                            {result.test_unit}
                        </p>
                    </div>
                </div>
                
                <!-- 시험 표준 및 규격 문서 -->
                <div style="background: #faf5ff; padding: 1rem; border-radius: 8px; border: 1px solid #d8b4fe;">
                    <p style="margin: 0 0 0.5rem 0; font-size: 0.75rem; color: #7c3aed; font-weight: 600;">시험 표준</p>
                    <p style="margin: 0 0 0.75rem 0; font-size: 0.875rem; color: #1e293b; font-weight: 500; line-height: 1.4;">
                        {result.test_standard}
                    </p>
                    
                    <!-- 규격 문서 링크 (요구사항 4.2) -->
                    <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #e2e8f0;">
                        <p style="margin: 0 0 0.5rem 0; font-size: 0.75rem; color: #64748b; font-weight: 500;">관련 규격 문서</p>
                        <button onclick="showStandardDocument('{standard_doc_name}')" 
                                style="background: none; border: none; color: #2563eb; font-size: 0.875rem; font-weight: 600; 
                                       text-decoration: underline; cursor: pointer; padding: 0; display: flex; align-items: center; gap: 0.5rem;
                                       transition: color 0.2s ease;"
                                onmouseover="this.style.color='#1d4ed8'" 
                                onmouseout="this.style.color='#2563eb'">
                            📄 {standard_doc_name}
                            <span style="font-size: 0.75rem; color: #64748b;">클릭하여 미리보기</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        """
        
        st.markdown(standard_info_html, unsafe_allow_html=True)
    
    def _render_additional_info_section(self) -> None:
        """추가 정보 섹션 렌더링"""
        if not self.selected_test_result:
            return
        
        result = self.selected_test_result
        
        # 추가 정보 HTML 생성
        additional_info_html = f"""
        <div style="background: white; padding: 1.5rem; border-left: 4px solid #8b5cf6;">
            <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-weight: 600; font-size: 1rem; display: flex; align-items: center;">
                ⚙️ 추가 정보
            </h4>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="background: #f8fafc; padding: 0.75rem; border-radius: 6px;">
                    <p style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: #64748b; font-weight: 500;">시험자 그룹</p>
                    <p style="margin: 0; font-size: 0.875rem; color: #1e293b; font-weight: 600;">{result.tester_group}</p>
                </div>
                <div style="background: #f8fafc; padding: 0.75rem; border-radius: 6px;">
                    <p style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: #64748b; font-weight: 500;">시험 기기</p>
                    <p style="margin: 0; font-size: 0.875rem; color: #1e293b; font-weight: 600;">{result.test_equipment}</p>
                </div>
                <div style="background: #f8fafc; padding: 0.75rem; border-radius: 6px;">
                    <p style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: #64748b; font-weight: 500;">처리 방식</p>
                    <p style="margin: 0; font-size: 0.875rem; color: #1e293b; font-weight: 600;">{result.processing_method}</p>
                </div>
                <div style="background: #f8fafc; padding: 0.75rem; border-radius: 6px;">
                    <p style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: #64748b; font-weight: 500;">KOLAS 여부</p>
                    <p style="margin: 0; font-size: 0.875rem; color: #1e293b; font-weight: 600;">
                        {'✅ ' if result.kolas_status == 'Y' else '❌ '}{result.kolas_status}
                    </p>
                </div>
            </div>
            
            <!-- 승인 정보 -->
            {self._render_approval_info(result)}
        </div>
        """
        
        st.markdown(additional_info_html, unsafe_allow_html=True)
    
    def _render_approval_info(self, result: TestResult) -> str:
        """승인 정보 렌더링"""
        if result.approval_request_datetime:
            approval_datetime = result.approval_request_datetime.strftime('%Y-%m-%d %H:%M') if hasattr(result.approval_request_datetime, 'strftime') else str(result.approval_request_datetime)
            approval_status = "승인 요청됨"
            approval_color = "#f59e0b"
            approval_bg = "#fef3c7"
        else:
            approval_datetime = "승인 요청 없음"
            approval_status = "승인 대기"
            approval_color = "#64748b"
            approval_bg = "#f1f5f9"
        
        return f"""
        <div style="margin-top: 1rem; padding: 1rem; background: {approval_bg}; border-radius: 8px; border: 1px solid {approval_color}33;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: #64748b; font-weight: 500;">승인 상태</p>
                    <p style="margin: 0; font-size: 0.875rem; color: {approval_color}; font-weight: 600;">{approval_status}</p>
                </div>
                <div style="text-align: right;">
                    <p style="margin: 0 0 0.25rem 0; font-size: 0.75rem; color: #64748b; font-weight: 500;">승인 요청 일시</p>
                    <p style="margin: 0; font-size: 0.875rem; color: #1e293b; font-weight: 600; font-family: monospace;">{approval_datetime}</p>
                </div>
            </div>
        </div>
        """
    
    def _render_empty_state(self) -> None:
        """빈 상태 렌더링"""
        empty_state_html = f"""
        <div style="background: white; padding: 2rem; border-radius: 0 0 8px 8px; text-align: center; height: {self.height - 100}px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <div style="color: #94a3b8; font-size: 3rem; margin-bottom: 1rem;">📋</div>
            <h4 style="margin: 0 0 0.5rem 0; color: #64748b; font-weight: 600;">상세 정보를 보려면 행을 선택하세요</h4>
            <p style="margin: 0; color: #94a3b8; font-size: 0.875rem;">테이블에서 시료를 클릭하면 상세 정보가 표시됩니다</p>
            
            <!-- 도움말 -->
            <div style="margin-top: 2rem; padding: 1rem; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; max-width: 300px;">
                <h5 style="margin: 0 0 0.5rem 0; color: #475569; font-weight: 600; font-size: 0.875rem;">💡 사용 방법</h5>
                <ul style="margin: 0; padding-left: 1rem; color: #64748b; font-size: 0.75rem; line-height: 1.5;">
                    <li>테이블에서 원하는 시료 행을 클릭</li>
                    <li>시료 정보와 시험 규격 확인</li>
                    <li>규격 문서 링크로 상세 규격 조회</li>
                </ul>
            </div>
        </div>
        """
        
        st.markdown(empty_state_html, unsafe_allow_html=True)
    
    def _get_standard_document_name(self, test_item: str) -> str:
        """
        시험 항목에 따른 규격 문서명 반환
        실제로는 데이터베이스나 설정 파일에서 조회해야 함
        """
        # 시험 항목별 규격 문서 매핑 (예시)
        standard_docs = {
            '1-[4-(1-hydroxy-1-methylethyl)phenyl]-ethanone': 'KS_M_3016_2021.pdf',
            'N-니트로조다이메틸아민': 'KS_M_3017_2021.pdf',
            'N-니트로조다이에틸아민': 'KS_M_3017_2021.pdf',
            '아크릴로나이트릴': 'KS_M_3018_2021.pdf',
            '트리페닐포스핀옥사이드': 'KS_M_3019_2021.pdf',
            '과망간산칼륨소비량': 'KS_M_3020_2021.pdf',
            '시안': 'KS_M_3021_2021.pdf',
            '질산성질소': 'KS_M_3022_2021.pdf'
        }
        
        return standard_docs.get(test_item, f'{test_item}_규격.pdf')
    
    def render_standard_bottom_sheet(self) -> None:
        """
        규격 문서 연동 기능 구현 (요구사항 4.2, 4.3, 4.4, 4.5)
        바텀 시트 슬라이드 애니메이션과 규격 문서 미리보기 기능
        """
        # JavaScript와 CSS를 포함한 바텀 시트 구현
        bottom_sheet_html = """
        <!-- 규격 문서 미리보기 바텀 시트 -->
        <div id="standard-bottom-sheet" class="fixed bottom-0 left-0 right-0 bg-white shadow-2xl z-50 transition-transform duration-300 ease-in-out transform translate-y-full">
            <div class="h-4/5 flex flex-col">
                <!-- 바텀 시트 헤더 -->
                <div class="p-4 border-b flex justify-between items-center bg-slate-50">
                    <div class="flex items-center gap-3">
                        <h3 id="standard-title" class="text-lg font-bold text-slate-800"></h3>
                        <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-semibold">규격 문서</span>
                    </div>
                    <button id="close-standard-btn" class="text-slate-500 hover:text-slate-800 text-2xl font-bold transition-colors duration-200">
                        ×
                    </button>
                </div>
                
                <!-- 바텀 시트 내용 -->
                <div class="flex-1 p-4 overflow-y-auto bg-gray-50">
                    <div id="standard-content" class="bg-white rounded-lg shadow-sm p-6">
                        <!-- 규격 문서 미리보기 내용이 여기에 로드됩니다 -->
                        <div class="text-center py-8">
                            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                            <p class="text-slate-600">규격 문서를 로드하는 중...</p>
                        </div>
                    </div>
                </div>
                
                <!-- 바텀 시트 푸터 -->
                <div class="p-4 border-t bg-slate-50 flex justify-between items-center">
                    <div class="text-sm text-slate-600">
                        <span>📄 규격 문서 미리보기</span>
                    </div>
                    <div class="space-x-2">
                        <button id="download-standard-btn" class="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors duration-200">
                            📥 규격 파일 다운로드
                        </button>
                        <button id="close-standard-footer-btn" class="bg-slate-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-slate-600 transition-colors duration-200">
                            닫기
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 바텀 시트 백드롭 -->
        <div id="standard-backdrop" class="fixed inset-0 bg-black bg-opacity-50 z-40 hidden transition-opacity duration-300"></div>
        
        <style>
        .bottom-sheet {
            transition: transform 0.3s ease-in-out;
        }
        
        .bottom-sheet.show {
            transform: translateY(0);
        }
        
        /* 스크롤바 스타일링 */
        #standard-content::-webkit-scrollbar {
            width: 6px;
        }
        
        #standard-content::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 3px;
        }
        
        #standard-content::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
        }
        
        #standard-content::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
        </style>
        
        <script>
        // 바텀 시트 관련 전역 변수
        let standardBottomSheet = null;
        let standardBackdrop = null;
        let currentStandardDoc = null;
        
        // DOM 로드 완료 시 초기화
        document.addEventListener('DOMContentLoaded', function() {
            initializeStandardBottomSheet();
        });
        
        function initializeStandardBottomSheet() {
            standardBottomSheet = document.getElementById('standard-bottom-sheet');
            standardBackdrop = document.getElementById('standard-backdrop');
            
            if (!standardBottomSheet || !standardBackdrop) {
                console.warn('Standard bottom sheet elements not found');
                return;
            }
            
            // 닫기 버튼 이벤트 리스너
            document.getElementById('close-standard-btn').addEventListener('click', closeStandardSheet);
            document.getElementById('close-standard-footer-btn').addEventListener('click', closeStandardSheet);
            
            // 다운로드 버튼 이벤트 리스너
            document.getElementById('download-standard-btn').addEventListener('click', downloadStandardDocument);
            
            // 백드롭 클릭 시 닫기 (요구사항 4.5)
            standardBackdrop.addEventListener('click', closeStandardSheet);
            
            // ESC 키로 닫기
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && standardBottomSheet.classList.contains('show')) {
                    closeStandardSheet();
                }
            });
        }
        
        // 규격 문서 표시 함수 (요구사항 4.3, 4.4)
        function showStandardDocument(docName) {
            if (!standardBottomSheet || !standardBackdrop) {
                console.error('Standard bottom sheet not initialized');
                return;
            }
            
            currentStandardDoc = docName;
            
            // 제목 설정
            document.getElementById('standard-title').textContent = docName + ' 미리보기';
            
            // 바텀 시트 표시 (요구사항 4.3 - 슬라이드 애니메이션)
            standardBackdrop.classList.remove('hidden');
            standardBottomSheet.style.transform = 'translateY(0)';
            
            // 애니메이션 효과
            setTimeout(() => {
                standardBackdrop.style.opacity = '1';
            }, 10);
            
            // 규격 문서 내용 로드 (요구사항 4.4)
            loadStandardDocumentContent(docName);
            
            // 바디 스크롤 방지
            document.body.style.overflow = 'hidden';
        }
        
        // 규격 문서 내용 로드 함수 (요구사항 4.4)
        function loadStandardDocumentContent(docName) {
            const contentContainer = document.getElementById('standard-content');
            
            // 로딩 상태 표시
            contentContainer.innerHTML = `
                <div class="text-center py-8">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p class="text-slate-600">규격 문서를 로드하는 중...</p>
                </div>
            `;
            
            // 실제로는 서버에서 문서를 로드해야 하지만, 여기서는 모의 데이터 사용
            setTimeout(() => {
                const mockContent = generateMockStandardContent(docName);
                contentContainer.innerHTML = mockContent;
            }, 1000);
        }
        
        // 모의 규격 문서 내용 생성
        function generateMockStandardContent(docName) {
            const testItem = currentStandardDoc.replace('_규격.pdf', '').replace('.pdf', '');
            
            return `
                <div class="space-y-6">
                    <!-- 문서 헤더 -->
                    <div class="border-b pb-4">
                        <h2 class="text-xl font-bold text-slate-800 mb-2">${docName}</h2>
                        <div class="flex items-center gap-4 text-sm text-slate-600">
                            <span>📅 발행일: 2021-12-01</span>
                            <span>🔄 개정일: 2023-06-15</span>
                            <span>📋 버전: v2.1</span>
                        </div>
                    </div>
                    
                    <!-- 규격 개요 -->
                    <div class="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <h3 class="font-semibold text-blue-800 mb-2">📋 규격 개요</h3>
                        <p class="text-sm text-blue-700 leading-relaxed">
                            이 규격은 ${testItem}의 시험 방법 및 기준값을 정의합니다. 
                            수질 안전성 확보를 위한 필수 검사 항목으로, 정확한 시험 절차와 
                            판정 기준을 제시합니다.
                        </p>
                    </div>
                    
                    <!-- 시험 방법 -->
                    <div>
                        <h3 class="font-semibold text-slate-800 mb-3">🔬 시험 방법</h3>
                        <div class="bg-slate-50 p-4 rounded-lg space-y-3">
                            <div class="flex items-start gap-3">
                                <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-semibold">1단계</span>
                                <div>
                                    <p class="font-medium text-slate-800">시료 전처리</p>
                                    <p class="text-sm text-slate-600">시료를 적절한 용매로 희석하고 불순물을 제거합니다.</p>
                                </div>
                            </div>
                            <div class="flex items-start gap-3">
                                <span class="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-semibold">2단계</span>
                                <div>
                                    <p class="font-medium text-slate-800">기기 분석</p>
                                    <p class="text-sm text-slate-600">LC-MS/MS 또는 GC-MS를 사용하여 정량 분석을 수행합니다.</p>
                                </div>
                            </div>
                            <div class="flex items-start gap-3">
                                <span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs font-semibold">3단계</span>
                                <div>
                                    <p class="font-medium text-slate-800">결과 판정</p>
                                    <p class="text-sm text-slate-600">측정값을 기준값과 비교하여 적합/부적합을 판정합니다.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 기준값 정보 -->
                    <div>
                        <h3 class="font-semibold text-slate-800 mb-3">📊 기준값 정보</h3>
                        <div class="overflow-x-auto">
                            <table class="w-full text-sm border border-slate-200 rounded-lg">
                                <thead class="bg-slate-100">
                                    <tr>
                                        <th class="px-4 py-2 text-left font-semibold text-slate-700 border-b">항목</th>
                                        <th class="px-4 py-2 text-left font-semibold text-slate-700 border-b">기준값</th>
                                        <th class="px-4 py-2 text-left font-semibold text-slate-700 border-b">단위</th>
                                        <th class="px-4 py-2 text-left font-semibold text-slate-700 border-b">비고</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr class="border-b">
                                        <td class="px-4 py-2 font-medium">${testItem}</td>
                                        <td class="px-4 py-2 font-mono text-blue-600">≤ 0.001</td>
                                        <td class="px-4 py-2">mg/L</td>
                                        <td class="px-4 py-2 text-slate-600">검출한계 이하</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- 주의사항 -->
                    <div class="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                        <h3 class="font-semibold text-yellow-800 mb-2">⚠️ 주의사항</h3>
                        <ul class="text-sm text-yellow-700 space-y-1 list-disc list-inside">
                            <li>시료 채취 시 오염을 방지하고 적절한 보존 조건을 유지하세요.</li>
                            <li>기기 교정은 정기적으로 수행하고 표준물질을 사용하세요.</li>
                            <li>검출한계 미만인 경우 "불검출"로 표기합니다.</li>
                            <li>결과 해석 시 측정 불확도를 고려하세요.</li>
                        </ul>
                    </div>
                    
                    <!-- 관련 법규 -->
                    <div>
                        <h3 class="font-semibold text-slate-800 mb-3">📜 관련 법규</h3>
                        <div class="bg-slate-50 p-4 rounded-lg">
                            <ul class="text-sm text-slate-700 space-y-2">
                                <li>• 먹는물 수질기준 및 검사 등에 관한 규칙</li>
                                <li>• 수도법 시행규칙</li>
                                <li>• KS M 3016:2021 - 수질 시험 방법</li>
                                <li>• ISO 17025:2017 - 시험소 및 교정기관의 능력에 대한 일반 요구사항</li>
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // 바텀 시트 닫기 함수 (요구사항 4.5)
        function closeStandardSheet() {
            if (!standardBottomSheet || !standardBackdrop) {
                return;
            }
            
            // 슬라이드 다운 애니메이션
            standardBottomSheet.style.transform = 'translateY(100%)';
            standardBackdrop.style.opacity = '0';
            
            // 애니메이션 완료 후 숨기기
            setTimeout(() => {
                standardBackdrop.classList.add('hidden');
                document.body.style.overflow = 'auto';
            }, 300);
        }
        
        // 규격 문서 다운로드 함수
        function downloadStandardDocument() {
            if (!currentStandardDoc) {
                alert('다운로드할 문서가 선택되지 않았습니다.');
                return;
            }
            
            // 실제로는 서버에서 파일을 다운로드해야 함
            alert(`${currentStandardDoc} 다운로드를 시작합니다.\\n\\n실제 구현에서는 서버에서 파일을 제공합니다.`);
        }
        </script>
        """
        
        st.markdown(bottom_sheet_html, unsafe_allow_html=True)
    
    def get_selected_test_result(self) -> Optional[TestResult]:
        """현재 선택된 시험 결과 반환"""
        return st.session_state.detail_panel.get('selected_test_result')
    
    def clear_selection(self) -> None:
        """선택 상태 초기화"""
        self.selected_test_result = None
        self.standard_info = None
        st.session_state.detail_panel['selected_test_result'] = None