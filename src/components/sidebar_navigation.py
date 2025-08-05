"""
사이드바 탐색 시스템 구현
SidebarNavigationSystem 클래스 - 파일 중심의 탐색 인터페이스 제공
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from pathlib import Path
import os
import pandas as pd
from data_models import TestResult, ProjectSummary
from data_processor import DataProcessor


class SidebarNavigationSystem:
    """사이드바 탐색 시스템 클래스"""
    
    def __init__(self):
        """초기화"""
        self.current_files = []
        self.active_file = None
        # 기본 메뉴와 통합 분석 메뉴 분리
        self.main_menu_items = ['📊 처리 대기 파일', '📄 시험성적서 목록', '📋 규격 목록']
        self.analysis_menu_items = ['📈 통합 분석']
        self.all_menu_items = self.main_menu_items + self.analysis_menu_items
        
        # 세션 상태 초기화
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = {}
        if 'active_file' not in st.session_state:
            st.session_state.active_file = None
        if 'current_page' not in st.session_state:
            st.session_state.current_page = '📊 처리 대기 파일'
    
    def render_file_list(self) -> None:
        """파일 목록 렌더링 기능 구현"""
        st.sidebar.markdown("### 현재 조회 파일")
        
        # 업로드된 파일 목록 표시
        if st.session_state.uploaded_files:
            for filename, file_data in st.session_state.uploaded_files.items():
                # 활성 파일 시각적 강조
                if filename == st.session_state.active_file:
                    # 활성 파일은 다른 스타일로 표시
                    if st.sidebar.button(
                        f"✓ {filename}", 
                        key=f"file_{filename}",
                        help="현재 활성 파일",
                        use_container_width=True
                    ):
                        self.handle_file_selection(filename)
                else:
                    # 비활성 파일
                    if st.sidebar.button(
                        f"📄 {filename}", 
                        key=f"file_{filename}",
                        use_container_width=True
                    ):
                        self.handle_file_selection(filename)
        else:
            st.sidebar.info("업로드된 파일이 없습니다.")
    
    def set_active_file(self, file_name: str) -> None:
        """활성 파일 상태 관리 구현"""
        if file_name in st.session_state.uploaded_files:
            st.session_state.active_file = file_name
            self.active_file = file_name
            st.sidebar.success(f"활성 파일: {file_name}")
        else:
            st.sidebar.error(f"파일을 찾을 수 없습니다: {file_name}")
    
    def handle_file_selection(self, file_name: str) -> None:
        """파일 선택 이벤트 처리 구현"""
        # 활성 파일 설정
        self.set_active_file(file_name)
        
        # 메인 콘텐츠 영역 업데이트를 위한 상태 변경
        st.session_state.content_update_trigger = True
        
        # 페이지 새로고침을 통한 메인 콘텐츠 업데이트
        st.rerun()
    
    def render_menu_navigation(self) -> None:
        """메인 메뉴 네비게이션 렌더링"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 메뉴")
        
        # 기본 메뉴 렌더링
        for menu_item in self.main_menu_items:
            if st.sidebar.button(
                menu_item,
                key=f"menu_{menu_item}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == menu_item else "secondary"
            ):
                if st.session_state.current_page != menu_item:
                    st.session_state.current_page = menu_item
                    st.rerun()
        
        # 구분선 추가
        st.sidebar.markdown("---")
        
        # 통합 분석 메뉴 렌더링
        for menu_item in self.analysis_menu_items:
            if st.sidebar.button(
                menu_item,
                key=f"menu_{menu_item}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == menu_item else "secondary"
            ):
                if st.session_state.current_page != menu_item:
                    st.session_state.current_page = menu_item
                    st.rerun()
    
    def get_active_file_data(self) -> Optional[Dict]:
        """활성 파일 데이터 반환"""
        if self.active_file and self.active_file in st.session_state.uploaded_files:
            return st.session_state.uploaded_files[self.active_file]
        return None
    
    def add_file(self, filename: str, file_content: bytes, test_results: List[TestResult] = None) -> None:
        """파일 추가"""
        from datetime import datetime
        
        st.session_state.uploaded_files[filename] = {
            'content': file_content,
            'test_results': test_results or [],
            'upload_time': datetime.now(),  # datetime 객체로 저장
            'processed': test_results is not None
        }
        
        # 첫 번째 파일인 경우 자동으로 활성화
        if len(st.session_state.uploaded_files) == 1:
            self.set_active_file(filename)
    
    def remove_file(self, filename: str) -> None:
        """파일 제거"""
        if filename in st.session_state.uploaded_files:
            del st.session_state.uploaded_files[filename]
            
            # 활성 파일이 제거된 경우 다른 파일로 변경
            if st.session_state.active_file == filename:
                if st.session_state.uploaded_files:
                    # 다른 파일이 있으면 첫 번째 파일을 활성화
                    next_file = list(st.session_state.uploaded_files.keys())[0]
                    self.set_active_file(next_file)
                else:
                    # 파일이 없으면 활성 파일 초기화
                    st.session_state.active_file = None
                    self.active_file = None
    
    def get_current_page(self) -> str:
        """현재 페이지 반환"""
        return st.session_state.current_page
    
    def render_sidebar(self) -> str:
        """전체 사이드바 렌더링"""
        # 사이드바 헤더
        st.sidebar.title("🧪 실험실 품질관리 시스템")
        st.sidebar.markdown("---")
        
        # 파일 목록 렌더링
        self.render_file_list()
        
        # 메뉴 네비게이션 렌더링
        self.render_menu_navigation()
        
        # 현재 페이지 반환
        return self.get_current_page()
    
    def get_file_count(self) -> int:
        """업로드된 파일 개수 반환"""
        return len(st.session_state.uploaded_files)
    
    def get_file_list(self) -> List[str]:
        """파일 목록 반환"""
        return list(st.session_state.uploaded_files.keys())
    
    def is_file_processed(self, filename: str) -> bool:
        """파일 처리 상태 확인"""
        if filename in st.session_state.uploaded_files:
            return st.session_state.uploaded_files[filename].get('processed', False)
        return False
    
    def get_file_test_results(self, filename: str) -> List[TestResult]:
        """파일의 테스트 결과 반환"""
        if filename in st.session_state.uploaded_files:
            return st.session_state.uploaded_files[filename].get('test_results', [])
        return []
    
    def add_file_to_list(self, filename: str) -> None:
        """파일을 목록에 추가 (호환성을 위한 메서드)"""
        from datetime import datetime
        
        # 이미 파일이 세션 상태에 있다면 활성화만 수행
        if filename in st.session_state.uploaded_files:
            self.set_active_file(filename)
        else:
            # 파일이 없다면 빈 데이터로 추가
            st.session_state.uploaded_files[filename] = {
                'content': b'',
                'test_results': [],
                'upload_time': datetime.now(),  # datetime 객체로 저장
                'processed': False
            }
            self.set_active_file(filename)


class PageManager:
    """페이지 관리 클래스"""
    
    def __init__(self, sidebar_nav: SidebarNavigationSystem):
        self.sidebar_nav = sidebar_nav
        self.data_processor = DataProcessor()
    
    def render_pending_files_page(self) -> None:
        """처리 대기 파일 페이지 구현"""
        st.header("📊 처리 대기 파일")
        
        # 파일 업로드 섹션
        st.subheader("파일 업로드")
        uploaded_file = st.file_uploader(
            "엑셀 파일 선택",
            type=['xlsx', 'xls'],
            help="최대 50MB까지 업로드 가능합니다.",
            key="file_uploader"
        )
        
        if uploaded_file is not None:
            # 파일 처리
            with st.spinner("파일을 처리 중입니다..."):
                try:
                    # 임시 파일로 저장
                    temp_file = f"temp_{uploaded_file.name}"
                    with open(temp_file, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # 데이터 파싱
                    test_results = self.data_processor.parse_excel_file(temp_file)
                    
                    # 임시 파일 삭제
                    os.remove(temp_file)
                    
                    # 사이드바에 파일 추가
                    self.sidebar_nav.add_file(
                        uploaded_file.name, 
                        uploaded_file.getbuffer(), 
                        test_results
                    )
                    
                    st.success(f"✅ 파일 '{uploaded_file.name}'이 성공적으로 처리되었습니다.")
                    st.info(f"📊 총 {len(test_results)}개의 시험 결과가 파싱되었습니다.")
                    
                except Exception as e:
                    st.error(f"❌ 파일 처리 중 오류가 발생했습니다: {str(e)}")
        
        # 업로드된 파일 목록 표시
        st.subheader("업로드된 파일 목록")
        if self.sidebar_nav.get_file_count() > 0:
            for filename in self.sidebar_nav.get_file_list():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    status = "✅ 처리완료" if self.sidebar_nav.is_file_processed(filename) else "⏳ 처리중"
                    st.write(f"📄 {filename} - {status}")
                
                with col2:
                    if st.button("분석", key=f"analyze_{filename}"):
                        self.sidebar_nav.handle_file_selection(filename)
                
                with col3:
                    if st.button("삭제", key=f"delete_{filename}"):
                        self.sidebar_nav.remove_file(filename)
                        st.rerun()
        else:
            st.info("업로드된 파일이 없습니다.")
    
    def render_reports_page(self) -> None:
        """시험성적서 목록 페이지 구현"""
        st.header("📄 시험성적서 목록")
        
        if self.sidebar_nav.get_file_count() > 0:
            st.subheader("생성 가능한 성적서")
            
            for filename in self.sidebar_nav.get_file_list():
                if self.sidebar_nav.is_file_processed(filename):
                    test_results = self.sidebar_nav.get_file_test_results(filename)
                    project_name = filename.replace('.xlsx', '').replace('.xls', '') + '_PJT'
                    
                    with st.expander(f"📋 {project_name} 성적서"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**파일명:** {filename}")
                            st.write(f"**시험 건수:** {len(test_results)}건")
                            violation_count = sum(1 for r in test_results if r.is_non_conforming())
                            st.write(f"**부적합 건수:** {violation_count}건")
                        
                        with col2:
                            if st.button("📄 성적서 생성", key=f"generate_{filename}"):
                                st.info("성적서 생성 기능은 다음 단계에서 구현됩니다.")
                            
                            if st.button("👁️ 미리보기", key=f"preview_{filename}"):
                                st.info("미리보기 기능은 다음 단계에서 구현됩니다.")
        else:
            st.info("처리된 파일이 없습니다. 먼저 파일을 업로드하고 처리해주세요.")
    
    def render_standards_page(self) -> None:
        """규격 목록 페이지 구현"""
        st.header("📋 규격 목록")
        
        # 규격 파일 업로드
        st.subheader("규격 문서 관리")
        
        uploaded_standard = st.file_uploader(
            "규격 문서 업로드 (PDF)",
            type=['pdf'],
            help="시험 규격 관련 PDF 문서를 업로드하세요.",
            key="standard_uploader"
        )
        
        if uploaded_standard is not None:
            st.success(f"✅ 규격 문서 '{uploaded_standard.name}'이 업로드되었습니다.")
            st.info("규격 문서 관리 기능은 다음 단계에서 구현됩니다.")
        
        # 기존 규격 목록 (샘플)
        st.subheader("등록된 규격 목록")
        
        sample_standards = [
            {"name": "EPA 524.2", "description": "유기화합물 분석 방법", "file": "EPA_524_2.pdf"},
            {"name": "House Method", "description": "자체 시험 방법", "file": "house_method.pdf"},
            {"name": "KS 표준", "description": "한국산업표준", "file": "ks_standard.pdf"}
        ]
        
        for standard in sample_standards:
            with st.expander(f"📋 {standard['name']}"):
                st.write(f"**설명:** {standard['description']}")
                st.write(f"**파일:** {standard['file']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 다운로드", key=f"download_{standard['name']}"):
                        st.info("다운로드 기능은 다음 단계에서 구현됩니다.")
                
                with col2:
                    if st.button("👁️ 미리보기", key=f"view_{standard['name']}"):
                        st.info("미리보기 기능은 다음 단계에서 구현됩니다.")
    
    def render_integrated_analysis_page(self) -> None:
        """통합 분석 페이지 구현"""
        st.header("📈 통합 분석 대시보드")
        st.markdown("기간별 데이터 동향을 통해 품질 관리 인사이트를 확보하세요.")
        
        # PeriodController 사용
        from period_controller import PeriodController
        
        period_controller = PeriodController()
        start_date, end_date = period_controller.render_period_selector()
        
        st.markdown("---")
        
        # 통합 분석 결과 영역
        if self.sidebar_nav.get_file_count() > 0:
            st.subheader("📊 통합 분석 결과")
            
            # IntegratedAnalysisEngine 사용
            from integrated_analysis_engine import IntegratedAnalysisEngine
            
            analysis_engine = IntegratedAnalysisEngine()
            
            # 분석 수행
            with st.spinner("데이터를 분석 중입니다..."):
                analysis_result = analysis_engine.analyze_period(
                    start_date, end_date, st.session_state.uploaded_files
                )
            
            # 분석 요약 정보
            summary = analysis_engine.get_analysis_summary(analysis_result)
            
            # KPI 카드 영역
            st.markdown("#### 핵심 지표")
            kpi_cols = st.columns(4)
            
            with kpi_cols[0]:
                st.metric("기간 내 총 시험 건수", f"{analysis_result.total_tests:,}건")
            
            with kpi_cols[1]:
                st.metric("평균 부적합률", f"{analysis_result.violation_rate:.1f}%")
            
            with kpi_cols[2]:
                st.metric("최다 부적합 항목", summary['top_violation_item'])
            
            with kpi_cols[3]:
                quality_score = 100 - analysis_result.violation_rate
                trend_icon = "📈" if summary['trend_direction'] == 'decreasing' else "📉" if summary['trend_direction'] == 'increasing' else "➡️"
                st.metric("품질 점수", f"{quality_score:.1f}점", delta=f"{trend_icon} {summary['trend_direction']}")
            
            # 추가 통계 정보
            st.markdown("#### 📋 분석 요약")
            info_cols = st.columns(3)
            
            with info_cols[0]:
                st.info(f"**분석 기간:** {summary['period']}")
            
            with info_cols[1]:
                st.info(f"**분석 파일 수:** {analysis_result.total_files}개")
            
            with info_cols[2]:
                st.info(f"**총 시료 수:** {analysis_result.total_samples}개")
            
            # 상위 부적합 항목 표시
            if analysis_result.top_violation_items:
                st.markdown("#### 🔍 상위 부적합 항목")
                
                violation_df_data = []
                for item, count in analysis_result.top_violation_items:
                    violation_df_data.append({
                        '시험 항목': item,
                        '부적합 건수': count,
                        '비율': f"{(count / analysis_result.total_tests * 100):.1f}%"
                    })
                
                violation_df = pd.DataFrame(violation_df_data)
                st.dataframe(violation_df, use_container_width=True)
            
            st.markdown("---")
            
            # 시각화 영역 (임시 구현)
            st.markdown("#### 데이터 시각화")
            
            viz_tabs = st.tabs(["📈 트렌드 분석", "📊 월별 현황", "📅 달력 히트맵"])
            
            with viz_tabs[0]:
                st.info("🚧 핵심 동향 라인 차트는 Task 16.2에서 구현됩니다.")
                st.markdown("- Y축: 부적합률(%), 특정 시험 항목의 평균값")
                st.markdown("- X축: 시간 (일/주/월 단위)")
                st.markdown("- 여러 시험 항목 동시 비교 기능")
            
            with viz_tabs[1]:
                st.info("🚧 월별 품질 현황 스택 바 차트는 Task 17.1에서 구현됩니다.")
                st.markdown("- 월별 총 시험 건수")
                st.markdown("- 정상/부적합 비율을 색상으로 구분")
            
            with viz_tabs[2]:
                st.info("🚧 품질 달력 히트맵은 Task 17.2에서 구현됩니다.")
                st.markdown("- 일별 부적합 발생 빈도를 색상 농도로 표현")
                st.markdown("- 주기적 패턴 발견 지원")
        
        else:
            st.info("통합 분석을 위해서는 먼저 파일을 업로드하고 처리해주세요.")
            
            if st.button("📊 처리 대기 파일로 이동", key="go_to_pending"):
                st.session_state.current_page = '📊 처리 대기 파일'
                st.rerun()