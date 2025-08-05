"""
동적 대시보드 엔진
선택된 파일에 따라 동적으로 변경되는 메인 대시보드 관리
성능 최적화 적용
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any, Optional, Tuple
from src.core.data_models import TestResult, ProjectSummary, Standard
from src.core.data_processor import DataProcessor
from src.utils.performance_optimizer import optimize_performance, cache_result, global_optimizer
from src.components.optimized_chart_renderer import optimized_chart_renderer
import json


class DynamicDashboardEngine:
    """동적 대시보드 엔진 클래스"""
    
    def __init__(self, data_processor: DataProcessor):
        """
        동적 대시보드 엔진 초기화
        
        Args:
            data_processor: 데이터 처리 엔진 인스턴스
        """
        self.data_processor = data_processor
        self.current_data = None
        self.selected_row = None
        self.performance_optimizer = global_optimizer
        self.chart_renderer = optimized_chart_renderer
        self.dashboard_state = {
            'current_file': None,
            'project_name': None,
            'summary': None,
            'kpi_data': None,
            'chart_data': None,
            'is_initialized': False,
            'last_updated': None
        }
        self._initialize_session_state()
    
    def _initialize_session_state(self) -> None:
        """Streamlit 세션 상태 초기화"""
        if 'dashboard_engine' not in st.session_state:
            st.session_state.dashboard_engine = {
                'current_file': None,
                'selected_row_index': None,
                'kpi_data': None,
                'last_update_time': None
            }
    
    @optimize_performance("update_dashboard")
    def update_dashboard(self, file_data: List[TestResult], filename: str = None) -> None:
        """
        대시보드 데이터 업데이트 (요구사항 2.1, 2.2, 2.4) - 성능 최적화 적용
        
        Args:
            file_data: 시험 결과 데이터 리스트
            filename: 파일명 (선택사항)
        """
        from datetime import datetime
        
        self.current_data = file_data
        
        # 프로젝트명 생성
        if filename:
            project_name = filename.replace('.xlsx', '').replace('.xls', '') + '_PJT'
        else:
            project_name = "UNKNOWN_PROJECT_PJT"
        
        # 프로젝트 요약 생성 (캐시 적용)
        summary = self.data_processor.get_project_summary(project_name, file_data)
        
        # KPI 데이터 실시간 계산
        kpi_data = self.generate_kpi_cards(file_data)
        
        # 차트 데이터 준비 (최적화된 렌더러 사용)
        chart_data = self._prepare_optimized_chart_data(file_data)
        
        # 대시보드 상태 업데이트
        self.dashboard_state.update({
            'current_file': filename,
            'project_name': project_name,
            'summary': summary,
            'kpi_data': kpi_data,
            'chart_data': chart_data,
            'is_initialized': True,
            'last_updated': datetime.now()
        })
        
        # Streamlit 세션 상태 업데이트
        st.session_state.dashboard_engine.update({
            'current_file': filename,
            'kpi_data': kpi_data,
            'last_update_time': datetime.now()
        })
        
        # 선택된 행 초기화 (새 파일 로드 시)
        self.selected_row = None
        st.session_state.dashboard_engine['selected_row_index'] = None
    
    @cache_result(ttl=900)  # 15분 캐시
    @optimize_performance("generate_kpi_cards")
    def generate_kpi_cards(self, data: List[TestResult]) -> Dict[str, Any]:
        """
        KPI 카드 데이터 생성 (성능 최적화 적용)
        
        Args:
            data: 시험 결과 데이터
            
        Returns:
            KPI 카드 데이터 딕셔너리
        """
        if not data:
            return {
                'total_tests': 0,
                'non_conforming_tests': 0,
                'non_conforming_rate': 0.0,
                'total_samples': 0,
                'non_conforming_samples': 0
            }
        
        # 벡터화된 계산으로 성능 최적화
        total_tests = len(data)
        
        # 부적합 여부를 한 번에 계산
        non_conforming_flags = [result.is_non_conforming() for result in data]
        non_conforming_tests = sum(non_conforming_flags)
        non_conforming_rate = (non_conforming_tests / total_tests * 100) if total_tests > 0 else 0.0
        
        # 시료명 집합 계산 (중복 제거)
        sample_names = [result.sample_name for result in data]
        unique_samples = set(sample_names)
        total_samples = len(unique_samples)
        
        # 부적합 시료 집합 계산
        non_conforming_sample_names = set(
            result.sample_name for result, is_non_conforming in zip(data, non_conforming_flags)
            if is_non_conforming
        )
        non_conforming_samples = len(non_conforming_sample_names)
        
        return {
            'total_tests': total_tests,
            'non_conforming_tests': non_conforming_tests,
            'non_conforming_rate': round(non_conforming_rate, 1),
            'total_samples': total_samples,
            'non_conforming_samples': non_conforming_samples
        }
    
    def create_violation_charts(self, data: List[TestResult]) -> Tuple[go.Figure, go.Figure]:
        """
        부적합 통계 차트 생성
        
        Args:
            data: 시험 결과 데이터
            
        Returns:
            (도넛 차트, 수평 막대 차트) 튜플
        """
        # 부적합 데이터 필터링
        violations = [result for result in data if result.is_non_conforming()]
        
        if not violations:
            # 빈 차트 반환
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="부적합 항목이 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
            return empty_fig, empty_fig
        
        # 1. 도넛 차트 - 부적합 항목별 분포
        violation_by_item = {}
        for result in violations:
            item = result.test_item
            violation_by_item[item] = violation_by_item.get(item, 0) + 1
        
        donut_fig = px.pie(
            values=list(violation_by_item.values()),
            names=list(violation_by_item.keys()),
            title="부적합 항목별 분포",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        donut_fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>건수: %{value}<br>비율: %{percent}<extra></extra>'
        )
        
        donut_fig.update_layout(
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.01),
            margin=dict(t=50, b=20, l=20, r=120),
            height=400
        )
        
        # 2. 수평 막대 차트 - 부적합 시료별 비율
        violation_by_sample = {}
        for result in violations:
            sample = result.sample_name
            violation_by_sample[sample] = violation_by_sample.get(sample, 0) + 1
        
        # 상위 10개만 표시
        sorted_samples = sorted(violation_by_sample.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if sorted_samples:
            bar_fig = px.bar(
                x=[count for _, count in sorted_samples],
                y=[sample for sample, _ in sorted_samples],
                orientation='h',
                title="부적합 시료별 건수 (상위 10개)",
                labels={'x': '부적합 건수', 'y': '시료명'},
                color=[count for _, count in sorted_samples],
                color_continuous_scale='Reds'
            )
            
            bar_fig.update_traces(
                hovertemplate='<b>%{y}</b><br>부적합 건수: %{x}<extra></extra>'
            )
            
            bar_fig.update_layout(
                showlegend=False,
                margin=dict(t=50, b=20, l=20, r=20),
                height=400,
                yaxis=dict(autorange="reversed")
            )
        else:
            bar_fig = go.Figure()
            bar_fig.add_annotation(
                text="부적합 시료가 없습니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color="gray")
            )
        
        return donut_fig, bar_fig
    
    @optimize_performance("render_interactive_table")
    def render_interactive_table(self, data: List[TestResult]) -> None:
        """
        인터랙티브 데이터 테이블 렌더링 (성능 최적화 적용)
        
        Args:
            data: 시험 결과 데이터
        """
        if not data:
            st.info("표시할 데이터가 없습니다.")
            return
        
        # 대용량 데이터 처리 최적화
        if len(data) > 5000:
            st.warning(f"대용량 데이터 ({len(data)}행) 감지 - 성능 최적화 모드로 전환")
            # 페이지네이션 적용
            page_size = 1000
            total_pages = (len(data) + page_size - 1) // page_size
            
            page = st.selectbox(
                f"페이지 선택 (총 {total_pages}페이지)",
                options=range(1, total_pages + 1),
                key="table_pagination"
            )
            
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(data))
            data = data[start_idx:end_idx]
            
            st.info(f"페이지 {page}: {start_idx + 1}-{end_idx}행 표시")
        
        # 최적화된 DataFrame 생성
        df = self.data_processor.export_to_dataframe(data)
        df['ID'] = range(len(df))
        
        # 검색 기능 (인덱스 기반 최적화)
        search_term = st.text_input("🔍 검색", placeholder="시료명, 시험항목, 시험자로 검색...")
        
        if search_term:
            # 벡터화된 검색
            mask = (
                df['시료명'].str.contains(search_term, case=False, na=False) |
                df['시험항목'].str.contains(search_term, case=False, na=False) |
                df['시험자'].str.contains(search_term, case=False, na=False)
            )
            df = df[mask]
        
        # 정렬 기능 (최적화된 정렬)
        col1, col2 = st.columns([3, 1])
        with col1:
            sort_column = st.selectbox(
                "정렬 기준",
                options=['시료명', '시험항목', '판정', '시험자', '입력일시'],
                key="table_sort_column"
            )
        with col2:
            sort_ascending = st.checkbox("오름차순", value=True, key="table_sort_order")
        
        if sort_column and len(df) > 0:
            df = df.sort_values(by=sort_column, ascending=sort_ascending)
        
        # 행 선택 (성능 최적화)
        if len(df) > 0:
            # 대용량 데이터의 경우 선택 방식 변경
            if len(df) > 100:
                selected_row_id = st.number_input(
                    "행 번호 입력 (1부터 시작)",
                    min_value=1,
                    max_value=len(df),
                    value=1,
                    key="table_row_number"
                )
                selected_index = selected_row_id - 1
            else:
                selected_index = st.selectbox(
                    "행 선택 (상세 정보 보기)",
                    options=range(len(df)),
                    format_func=lambda x: f"{df.iloc[x]['시료명']} - {df.iloc[x]['시험항목']}",
                    key="table_row_selector"
                )
            
            if selected_index is not None and 0 <= selected_index < len(df):
                original_index = df.iloc[selected_index]['ID']
                if original_index < len(data):
                    self.selected_row = data[original_index]
        
        # 성능 최적화된 스타일링
        display_df = df.drop('ID', axis=1)
        
        # 부적합 행 하이라이트 (조건부 적용)
        if len(display_df) <= 1000:  # 1000행 이하에서만 스타일링 적용
            def highlight_violations(row):
                if row['판정'] == '부적합':
                    return ['background-color: #ffebee; color: #c62828'] * len(row)
                return [''] * len(row)
            
            styled_df = display_df.style.apply(highlight_violations, axis=1)
            st.dataframe(styled_df, use_container_width=True, height=400)
        else:
            # 대용량 데이터는 스타일링 없이 표시
            st.dataframe(display_df, use_container_width=True, height=400)
            st.info("성능 최적화를 위해 대용량 데이터에서는 스타일링이 비활성화됩니다.")
        
        # 테이블 요약 정보 (벡터화된 계산)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("표시된 행 수", len(display_df))
        with col2:
            violation_count = (display_df['판정'] == '부적합').sum()
            st.metric("부적합 건수", violation_count)
        with col3:
            if len(display_df) > 0:
                violation_rate = (violation_count / len(display_df)) * 100
                st.metric("부적합 비율", f"{violation_rate:.1f}%")
    
    def update_detail_panel(self, selected_row: TestResult = None) -> None:
        """
        상세 정보 패널 업데이트
        
        Args:
            selected_row: 선택된 행 데이터
        """
        if selected_row is None:
            selected_row = self.selected_row
        
        if selected_row:
            # 시료 정보 섹션
            st.markdown("#### 📋 시료 정보")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**시료명:** {selected_row.sample_name}")
                st.write(f"**분석번호:** {selected_row.analysis_number}")
                st.write(f"**시험자:** {selected_row.tester}")
            
            with col2:
                if selected_row.input_datetime and hasattr(selected_row.input_datetime, 'strftime'):
                    st.write(f"**입력일시:** {selected_row.input_datetime.strftime('%Y-%m-%d %H:%M')}")
                elif selected_row.input_datetime:
                    st.write(f"**입력일시:** {str(selected_row.input_datetime)}")
                st.write(f"**시험자그룹:** {selected_row.tester_group}")
                st.write(f"**시험Set:** {selected_row.test_set}")
            
            st.divider()
            
            # 시험 규격 정보 섹션
            st.markdown("#### 🔬 시험 규격 정보")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**시험항목:** {selected_row.test_item}")
                st.write(f"**시험단위:** {selected_row.test_unit}")
                st.write(f"**결과값:** {selected_row.get_display_result()}")
            
            with col2:
                st.write(f"**기준값:** {selected_row.standard_criteria}")
                st.write(f"**시험표준:** {selected_row.test_standard}")
                
                # 판정 결과 색상 표시
                if selected_row.standard_excess == '부적합':
                    st.error(f"**판정:** {selected_row.standard_excess}")
                else:
                    st.success(f"**판정:** {selected_row.standard_excess}")
            
            st.divider()
            
            # 추가 정보
            with st.expander("🔧 추가 기술 정보"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**시험기기:** {selected_row.test_equipment}")
                    st.write(f"**처리방식:** {selected_row.processing_method}")
                    st.write(f"**결과유형:** {selected_row.result_type}")
                
                with col2:
                    st.write(f"**표시자리수:** {selected_row.result_display_digits}")
                    st.write(f"**KOLAS 여부:** {selected_row.kolas_status}")
                    st.write(f"**성적서 출력:** {selected_row.report_output}")
            
            # 관련 규격 링크
            if selected_row.test_standard:
                if st.button(f"📋 {selected_row.test_standard} 규격 보기", key="standard_link"):
                    self.show_standard_info(selected_row.test_standard)
        else:
            st.info("테이블에서 행을 선택하면 상세 정보가 표시됩니다.")
    
    def show_standard_info(self, standard_name: str) -> None:
        """
        규격 정보 표시 (바텀 시트 대신 expander 사용)
        
        Args:
            standard_name: 규격명
        """
        with st.expander(f"📋 {standard_name} 규격 정보", expanded=True):
            st.write(f"**규격명:** {standard_name}")
            
            # 현재 데이터에서 해당 규격 관련 정보 찾기
            if self.current_data:
                related_tests = [
                    result for result in self.current_data 
                    if result.test_standard == standard_name
                ]
                
                if related_tests:
                    st.write(f"**관련 시험항목 수:** {len(related_tests)}개")
                    
                    # 관련 시험항목 목록
                    test_items = list(set(result.test_item for result in related_tests))
                    st.write("**시험항목:**")
                    for item in test_items:
                        st.write(f"- {item}")
                    
                    # 기준값 정보
                    st.write("**기준값 정보:**")
                    for result in related_tests[:5]:  # 최대 5개만 표시
                        st.write(f"- {result.test_item}: {result.standard_criteria}")
                else:
                    st.info("관련 시험 정보를 찾을 수 없습니다.")
            
            # 다운로드 버튼 (향후 구현)
            if st.button("📥 규격 파일 다운로드", key=f"download_{standard_name}"):
                st.info("규격 파일 다운로드 기능은 향후 구현 예정입니다.")
    
    def render_dynamic_header(self, filename: str = None) -> None:
        """
        동적 헤더 렌더링 (요구사항 2.1)
        파일이 선택되면 "[파일명] 분석 보고서 대시보드" 형식으로 동적 변경
        
        Args:
            filename: 파일명
        """
        if filename is None:
            filename = self.dashboard_state.get('current_file', 'Unknown File')
        
        # 파일명에서 확장자 제거
        display_filename = filename.replace('.xlsx', '').replace('.xls', '') if filename != 'Unknown File' else filename
        
        # 헤더 섹션 (요구사항 2.1, 2.2)
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 동적 제목 업데이트
            st.title(f"{display_filename} 분석 보고서 대시보드")
            
            # 분석 기간 및 상태 표시
            if self.dashboard_state.get('summary'):
                summary = self.dashboard_state['summary']
                st.caption(f"📅 {summary.analysis_period}")
                
                # 실시간 상태 표시
                if self.dashboard_state.get('last_updated'):
                    last_update = self.dashboard_state['last_updated']
                    st.caption(f"🔄 마지막 업데이트: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        
        with col2:
            # 시험성적서 미리보기 버튼 (요구사항 2.2)
            if st.button("📄 시험성적서 미리보기", use_container_width=True, key="report_preview"):
                self.show_report_preview()
            
            # 대시보드 새로고침 버튼
            if st.button("🔄 새로고침", use_container_width=True, key="refresh_dashboard"):
                self.refresh_dashboard_state()
    
    def show_report_preview(self) -> None:
        """시험성적서 미리보기 모달 (expander로 구현)"""
        with st.expander("📄 시험성적서 미리보기", expanded=True):
            if self.dashboard_state.get('summary'):
                summary = self.dashboard_state['summary']
                
                st.write(f"**프로젝트:** {summary.project_name}")
                st.write(f"**분석 기간:** {summary.analysis_period}")
                st.write(f"**총 시험 건수:** {summary.total_tests}건")
                st.write(f"**부적합 건수:** {summary.violation_tests}건")
                st.write(f"**부적합 비율:** {summary.violation_rate:.1f}%")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 PDF로 저장", key="save_pdf"):
                        st.info("PDF 저장 기능은 향후 구현 예정입니다.")
                
                with col2:
                    if st.button("🖨️ 인쇄", key="print_report"):
                        st.info("인쇄 기능은 향후 구현 예정입니다.")
            else:
                st.info("분석 데이터가 없습니다.")
    
    @optimize_performance("prepare_optimized_chart_data")
    def _prepare_optimized_chart_data(self, data: List[TestResult]) -> Dict[str, Any]:
        """
        최적화된 차트 데이터 준비
        
        Args:
            data: 시험 결과 데이터
            
        Returns:
            최적화된 차트 데이터 딕셔너리
        """
        # 최적화된 차트 렌더러 사용
        donut_config = self.chart_renderer.generate_optimized_donut_chart(data)
        bar_config = self.chart_renderer.generate_optimized_bar_chart(data)
        
        return {
            'donut_chart_config': donut_config,
            'bar_chart_config': bar_config,
            'chart_update_scripts': {
                'donut': self.chart_renderer.generate_optimized_chart_update_script('donut', data),
                'bar': self.chart_renderer.generate_optimized_chart_update_script('bar', data)
            },
            'lazy_loading_script': self.chart_renderer.generate_lazy_loading_script(),
            'performance_monitoring_script': self.chart_renderer.generate_performance_monitoring_script()
        }
    
    def get_dashboard_state(self) -> Dict[str, Any]:
        """
        현재 대시보드 상태 반환
        
        Returns:
            대시보드 상태 딕셔너리
        """
        return self.dashboard_state.copy()
    
    def refresh_dashboard_state(self) -> None:
        """
        대시보드 상태 새로고침 (요구사항 2.4)
        현재 데이터를 기반으로 KPI와 차트 데이터를 다시 계산
        """
        if self.current_data:
            from datetime import datetime
            
            # KPI 데이터 재계산
            kpi_data = self.generate_kpi_cards(self.current_data)
            
            # 차트 데이터 재계산
            chart_data = self._prepare_chart_data(self.current_data)
            
            # 상태 업데이트
            self.dashboard_state.update({
                'kpi_data': kpi_data,
                'chart_data': chart_data,
                'last_updated': datetime.now()
            })
            
            # 세션 상태 업데이트
            st.session_state.dashboard_engine.update({
                'kpi_data': kpi_data,
                'last_update_time': datetime.now()
            })
            
            st.success("대시보드가 새로고침되었습니다!")
        else:
            st.warning("새로고침할 데이터가 없습니다.")
    
    def is_dashboard_initialized(self) -> bool:
        """
        대시보드 초기화 상태 확인
        
        Returns:
            초기화 여부
        """
        return self.dashboard_state.get('is_initialized', False)
    
    def get_current_file(self) -> Optional[str]:
        """
        현재 선택된 파일명 반환
        
        Returns:
            현재 파일명 또는 None
        """
        return self.dashboard_state.get('current_file')
    
    def get_kpi_data(self) -> Optional[Dict[str, Any]]:
        """
        현재 KPI 데이터 반환
        
        Returns:
            KPI 데이터 딕셔너리 또는 None
        """
        return self.dashboard_state.get('kpi_data')
    
    def get_selected_row(self) -> Optional[TestResult]:
        """
        현재 선택된 행 데이터 반환
        
        Returns:
            선택된 TestResult 또는 None
        """
        return self.selected_row
    
    def set_selected_row(self, row_index: int) -> None:
        """
        선택된 행 설정
        
        Args:
            row_index: 선택할 행의 인덱스
        """
        if self.current_data and 0 <= row_index < len(self.current_data):
            self.selected_row = self.current_data[row_index]
            st.session_state.dashboard_engine['selected_row_index'] = row_index
    
    def reset_dashboard(self) -> None:
        """대시보드 상태 초기화"""
        self.current_data = None
        self.selected_row = None
        self.dashboard_state = {
            'current_file': None,
            'project_name': None,
            'summary': None,
            'kpi_data': None,
            'chart_data': None,
            'is_initialized': False,
            'last_updated': None
        }
        
        # 세션 상태도 초기화
        if 'dashboard_engine' in st.session_state:
            st.session_state.dashboard_engine = {
                'current_file': None,
                'selected_row_index': None,
                'kpi_data': None,
                'last_update_time': None
            }


# 테스트 함수
def test_dynamic_dashboard_engine():
    """동적 대시보드 엔진 테스트"""
    from data_processor import DataProcessor
    from datetime import datetime
    
    # 샘플 데이터 생성
    sample_results = [
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
        )
    ]
    
    # 엔진 테스트
    processor = DataProcessor()
    engine = DynamicDashboardEngine(processor)
    
    # 대시보드 업데이트
    engine.update_dashboard(sample_results, "test_file.xlsx")
    
    # KPI 데이터 생성 테스트
    kpi_data = engine.generate_kpi_cards(sample_results)
    print(f"KPI 데이터: {kpi_data}")
    
    # 차트 생성 테스트
    donut_fig, bar_fig = engine.create_violation_charts(sample_results)
    print("차트 생성 완료")
    
    # 상태 확인
    state = engine.get_dashboard_state()
    print(f"대시보드 상태: {state['project_name']}")
    
    return engine


if __name__ == "__main__":
    test_dynamic_dashboard_engine()