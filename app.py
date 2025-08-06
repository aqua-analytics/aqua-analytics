#!/usr/bin/env python3
"""
Aqua-Analytics Premium: 환경 데이터 인사이트 플랫폼 - GitHub 데모 버전
로컬 버전의 최종 완성된 구성요소들과 완전히 동일한 구현
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import io
import json

st.set_page_config(
    page_title="Aqua-Analytics | 환경 데이터 인사이트 플랫폼",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 테스트 결과 클래스 (로컬 버전과 완전 동일)
class TestResult:
    def __init__(self, data_row):
        self.sample_name = data_row.get('시료명', '')
        self.analysis_number = data_row.get('분석번호', '')
        self.test_item = data_row.get('시험항목', '')
        self.test_unit = data_row.get('시험단위', '')
        self.result_value = data_row.get('결과(성적서)', '')
        self.input_value = data_row.get('시험자입력값', '')
        self.conformity = data_row.get('기준대비 초과여부', '')
        self.tester = data_row.get('시험자', '')
        self.test_standard = data_row.get('시험표준', '')
        
    def is_non_conforming(self):
        return self.conformity == '부적합'# 대시보드 엔
진 클래스 (로컬 버전의 DynamicDashboardEngine 핵심 기능)
class DashboardEngine:
    def create_violation_charts(self, data: List[TestResult]) -> Tuple[go.Figure, go.Figure]:
        """부적합 통계 차트 생성 (로컬 버전과 완전 동일)"""
        violations = [result for result in data if result.is_non_conforming()]
        
        if not violations:
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
        
        return donut_fig, bar_fig# 통
합 분석 엔진 클래스 (로컬 버전의 IntegratedAnalysisEngine 핵심 기능)
class IntegratedAnalysisEngine:
    def create_non_conforming_chart(self, non_conforming_items: Dict[str, int]) -> go.Figure:
        """부적합 항목 도넛 차트 생성 (로컬 버전과 완전 동일)"""
        if not non_conforming_items:
            fig = go.Figure()
            fig.add_annotation(
                text="부적합 항목 없음",
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False
            )
            fig.update_layout(
                height=300,
                showlegend=False,
                margin=dict(t=20, b=20, l=20, r=20)
            )
            return fig
        
        # 상위 10개 항목만 표시
        sorted_items = sorted(non_conforming_items.items(), key=lambda x: x[1], reverse=True)[:10]
        labels = [item[0] for item in sorted_items]
        values = [item[1] for item in sorted_items]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(
                colors=px.colors.qualitative.Set3,
                line=dict(color='white', width=2)
            ),
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>건수: %{value}<br>비율: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            height=300,
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=False,
            font=dict(size=12)
        )
        
        return fig
    
    def create_contamination_level_chart(self, files_data: List[Dict]) -> go.Figure:
        """실험별 오염수준 분포 차트 생성"""
        if not files_data:
            fig = go.Figure()
            fig.add_annotation(
                text="데이터 없음",
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False
            )
            return fig
        
        # 파일별 부적합률 계산
        contamination_levels = []
        file_names = []
        
        for file_data in files_data:
            test_results = file_data.get('test_results', [])
            if test_results:
                violations = [r for r in test_results if r.get('is_non_conforming', False)]
                contamination_rate = len(violations) / len(test_results) * 100
                contamination_levels.append(contamination_rate)
                file_names.append(file_data.get('filename', 'Unknown')[:20])
        
        if contamination_levels:
            fig = px.bar(
                x=file_names,
                y=contamination_levels,
                title="실험별 오염수준 분포",
                labels={'x': '파일명', 'y': '부적합률 (%)'},
                color=contamination_levels,
                color_continuous_scale='Reds'
            )
            
            fig.update_layout(
                height=300,
                margin=dict(t=50, b=20, l=20, r=20),
                xaxis_tickangle=-45
            )
        else:
            fig = go.Figure()
            fig.add_annotation(
                text="오염수준 데이터 없음",
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False
            )
        
        return fig
    
    def create_file_trend_chart(self, files_data: List[Dict]) -> go.Figure:
        """시험/시료별 추이 차트 생성"""
        if not files_data:
            fig = go.Figure()
            fig.add_annotation(
                text="추이 데이터 없음",
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False
            )
            return fig
        
        # 시간별 부적합률 추이
        dates = []
        violation_rates = []
        
        for file_data in files_data:
            upload_time = file_data.get('upload_time')
            if upload_time:
                if isinstance(upload_time, str):
                    upload_time = datetime.fromisoformat(upload_time)
                dates.append(upload_time)
                
                test_results = file_data.get('test_results', [])
                if test_results:
                    violations = [r for r in test_results if r.get('is_non_conforming', False)]
                    violation_rate = len(violations) / len(test_results) * 100
                    violation_rates.append(violation_rate)
                else:
                    violation_rates.append(0)
        
        if dates and violation_rates:
            fig = px.line(
                x=dates,
                y=violation_rates,
                title="시험/시료별 추이",
                labels={'x': '업로드 시간', 'y': '부적합률 (%)'},
                markers=True
            )
            
            fig.update_layout(
                height=300,
                margin=dict(t=50, b=20, l=20, r=20)
            )
        else:
            fig = go.Figure()
            fig.add_annotation(
                text="추이 데이터 없음",
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False
            )
        
        return figcla
ss AquaAnalyticsDemo:
    """Aqua-Analytics Premium 데모 애플리케이션 (로컬 버전의 최종 구성요소 완전 복제)"""
    
    def __init__(self):
        self.apply_premium_theme()
        self.initialize_session_state()
        self.dashboard_engine = DashboardEngine()
        self.integrated_analysis_engine = IntegratedAnalysisEngine()
    
    def apply_premium_theme(self):
        """프리미엄 테마 CSS 적용 (로컬 버전과 완전 동일)"""
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        :root {
            --primary-50: #eff6ff;
            --primary-100: #dbeafe;
            --primary-500: #3b82f6;
            --primary-600: #2563eb;
            --primary-700: #1d4ed8;
            --gray-50: #f8fafc;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-300: #cbd5e1;
            --gray-400: #94a3b8;
            --gray-500: #64748b;
            --gray-600: #475569;
            --gray-700: #334155;
            --gray-800: #1e293b;
            --gray-900: #0f172a;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
        }
        
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--gray-50);
        }
        
        .css-1d391kg, .css-1cypcdb {
            background-color: #ffffff;
            border-right: 1px solid var(--gray-200);
        }
        
        .main .block-container {
            background-color: var(--gray-50);
            padding: 2rem 2rem 4rem 2rem;
            max-width: none;
        }
        
        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1rem 0 1.5rem 0;
            border-bottom: 1px solid var(--gray-200);
            margin-bottom: 1.5rem;
        }
        
        .brand-logo {
            font-size: 2rem;
            line-height: 1;
        }
        
        .brand-title {
            font-size: 1.125rem;
            font-weight: 700;
            color: var(--gray-900);
            line-height: 1.2;
        }
        
        .brand-subtitle {
            font-size: 0.75rem;
            color: var(--gray-500);
            font-weight: 500;
        }
        
        .nav-section-title {
            font-size: 0.6875rem;
            font-weight: 700;
            color: var(--gray-400);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin: 1.5rem 0 0.75rem 0;
            padding: 0 0.5rem;
        }
        
        .kpi-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }
        
        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
            border-color: #cbd5e1;
        }
        
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--gray-200);
        }
        
        .page-title {
            font-size: 1.875rem;
            font-weight: 700;
            color: var(--gray-900);
            margin: 0;
        }
        
        .page-subtitle {
            font-size: 1rem;
            color: var(--gray-600);
            margin: 0.25rem 0 0 0;
        }
        
        .stButton > button {
            width: 100%;
            background: transparent;
            border: none;
            color: var(--gray-700);
            font-weight: 500;
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            text-align: left;
            transition: all 0.2s ease;
            margin-bottom: 0.25rem;
        }
        
        .stButton > button:hover {
            background-color: var(--gray-100);
            color: var(--gray-900);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """세션 상태 초기화 (로컬 버전과 동일한 구조)"""
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
        if 'active_file' not in st.session_state:
            st.session_state.active_file = None
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = {}
        if 'report_history' not in st.session_state:
            st.session_state.report_history = []  
  def render_sidebar(self):
        """프리미엄 사이드바 렌더링 (로컬 버전과 완전 동일)"""
        with st.sidebar:
            # 브랜드 헤더
            st.markdown("""
            <div class="sidebar-brand">
                <div class="brand-logo">💧</div>
                <div>
                    <div class="brand-title">Aqua-Analytics</div>
                    <div class="brand-subtitle">환경 데이터 인사이트</div>
                    <div style="background: #fef3c7; color: #92400e; font-size: 0.7rem; padding: 4px 8px; border-radius: 4px; margin-top: 4px; text-align: center;">
                        🌐 GitHub 데모 버전
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 현재 프로젝트 상태
            if st.session_state.active_file:
                project_name = st.session_state.active_file.replace('.xlsx', '').replace('.xls', '')
                st.markdown(f"""
                <div style="background: var(--primary-50); border: 1px solid var(--primary-200); border-radius: 0.75rem; padding: 1rem; margin-bottom: 1.5rem;">
                    <div style="font-size: 0.75rem; color: var(--primary-600); font-weight: 600; margin-bottom: 0.25rem;">
                        현재 프로젝트
                    </div>
                    <div style="font-size: 0.875rem; color: var(--gray-800); font-weight: 500;">
                        {project_name}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # 네비게이션 메뉴
            st.markdown('<div class="nav-section-title">MENU</div>', unsafe_allow_html=True)
            
            # 통합 분석 메뉴 (최상단)
            if st.button("📈 통합 분석", key="nav_integrated_analysis", use_container_width=True):
                st.session_state.current_page = 'integrated_analysis'
                st.rerun()
            
            # 구분선 추가
            st.markdown("---")
            
            # 기본 메뉴
            main_menu_items = [
                {'id': 'dashboard', 'label': '대시보드', 'icon': '📊'},
                {'id': 'reports', 'label': '보고서 관리', 'icon': '📄'},
                {'id': 'standards', 'label': '시험 규격 관리', 'icon': '🛡️'}
            ]
            
            for item in main_menu_items:
                if st.button(f"{item['icon']} {item['label']}", key=f"nav_{item['id']}", use_container_width=True):
                    st.session_state.current_page = item['id']
                    st.rerun()
            
            # 저장 폴더 바로가기 섹션
            st.markdown("---")
            st.markdown('<div class="nav-section-title">저장 폴더</div>', unsafe_allow_html=True)
            
            folder_buttons = [
                {'key': 'base', 'label': '전체 폴더', 'icon': '📁'},
                {'key': 'uploads', 'label': '업로드 파일', 'icon': '📤'},
                {'key': 'processed', 'label': '처리된 파일', 'icon': '⚙️'},
                {'key': 'dashboard_reports', 'label': '보고서', 'icon': '📄'}
            ]
            
            for folder in folder_buttons:
                file_count = len(st.session_state.uploaded_files) if folder['key'] == 'uploads' else 0
                if folder['key'] == 'processed' and st.session_state.active_file:
                    file_count = 1
                if folder['key'] == 'dashboard_reports' and st.session_state.active_file:
                    file_count = 1
                
                count_text = f"({file_count}개)"
                
                if st.button(f"{folder['icon']} {folder['label']} {count_text}", 
                           key=f"folder_{folder['key']}", use_container_width=True):
                    st.info(f"📁 {folder['label']} 폴더 - 데모 버전에서는 실제 폴더 열기가 제한됩니다.")
    
    def process_uploaded_file(self, uploaded_file, client="미지정", upload_datetime=None):
        """업로드된 파일 처리 (로컬 버전과 동일한 로직)"""
        try:
            if upload_datetime is None:
                upload_datetime = datetime.now()
            
            # 파일 형식에 따른 읽기
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            
            # 테스트 결과 객체 생성
            test_results = []
            for _, row in df.iterrows():
                test_results.append(TestResult(row.to_dict()))
            
            # 세션에 저장 (로컬 버전과 동일한 구조)
            st.session_state.uploaded_files[uploaded_file.name] = {
                'test_results': test_results,
                'processed': True,
                'upload_time': upload_datetime,
                'client': client,
                'file_id': f"demo_{len(st.session_state.uploaded_files)}"
            }
            st.session_state.active_file = uploaded_file.name
            
            # 보고서 이력에 저장
            self.save_to_report_history(uploaded_file.name, test_results, upload_datetime, client)
            
            return True
            
        except Exception as e:
            st.error(f"❌ 파일 처리 오류: {str(e)}")
            return False
    
    def save_to_report_history(self, filename, test_results, upload_time, client, file_id=None):
        """보고서 이력에 저장"""
        violations = [r for r in test_results if r.is_non_conforming()]
        violation_rate = len(violations) / len(test_results) * 100 if test_results else 0
        
        report_item = {
            'filename': filename,
            'project_name': filename.replace('.xlsx', '').replace('.xls', ''),
            'upload_time': upload_time,
            'total_tests': len(test_results),
            'violations': len(violations),
            'violation_rate': violation_rate,
            'test_results': test_results,
            'client': client,
            'file_id': file_id or f"demo_{len(st.session_state.report_history)}"
        }
        
        st.session_state.report_history.append(report_item)
    
    def load_sample_data(self):
        """샘플 데이터 로드 (로컬 버전과 동일한 구조)"""
        sample_data = pd.DataFrame({
            '시료명': [f'시료_{i:03d}' for i in range(1, 101)],
            '분석번호': [f'A{i:04d}' for i in range(1, 101)],
            '시험항목': ['pH', '용존산소', '탁도', 'COD', 'BOD'] * 20,
            '시험단위': ['pH', 'mg/L', 'NTU', 'mg/L', 'mg/L'] * 20,
            '결과(성적서)': [7.2, 8.5, 2.1, 15.3, 12.1] * 20,
            '시험자입력값': [7.1, 8.4, 2.2, 15.1, 12.3] * 20,
            '기준대비 초과여부': ['적합', '적합', '적합', '부적합', '적합'] * 20,
            '시험자': ['김분석', '이실험', '박측정', '최검사', '정품질'] * 20,
            '시험표준': ['KS M 0011', 'KS M 0012', 'KS M 0013', 'KS M 0014', 'KS M 0015'] * 20,
            '분석일자': pd.date_range('2024-01-01', periods=100, freq='D')
        })
        
        # 가상의 업로드 파일 생성
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        mock_file = MockFile("샘플_환경데이터.xlsx")
        self.process_uploaded_file(mock_file, "샘플 데이터", datetime.now())
        
        # 샘플 데이터를 직접 설정
        test_results = []
        for _, row in sample_data.iterrows():
            test_results.append(TestResult(row.to_dict()))
        
        st.session_state.uploaded_files["샘플_환경데이터.xlsx"]['test_results'] = test_results
        
        st.success("✅ 샘플 데이터가 로드되었습니다!")
        st.rerun()    d
ef render_page_header(self, title, subtitle, show_save_button=False):
        """페이지 헤더 렌더링 (로컬 버전과 동일)"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div class="page-header">
                <div>
                    <div class="page-title">{title}</div>
                    <div class="page-subtitle">{subtitle}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if show_save_button:
                if st.button("💾 저장", key="save_button"):
                    st.success("✅ 데모 버전 - 저장 완료 (세션 기반)")
    
    def render_kpi_cards(self, test_results: List[TestResult]):
        """프리미엄 KPI 카드 렌더링 (로컬 버전과 완전 동일)"""
        if not test_results:
            return
        
        # KPI 데이터 계산
        total_tests = len(test_results)
        violations = [r for r in test_results if r.is_non_conforming()]
        violation_rate = len(violations) / total_tests * 100 if total_tests > 0 else 0
        unique_samples = len(set(r.sample_name for r in test_results))
        
        # 4개 컬럼으로 KPI 카드 배치
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div style="background: #dbeafe; color: #2563eb; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 16px;">
                    📊
                </div>
                <div>
                    <div style="font-size: 2.5rem; font-weight: 800; line-height: 1; margin-bottom: 8px; color: #2563eb;">{total_tests:,}</div>
                    <div style="font-size: 0.875rem; color: #64748b; font-weight: 500;">총 시험 건수</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div style="background: #fef2f2; color: #ef4444; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 16px;">
                    ⚠️
                </div>
                <div>
                    <div style="font-size: 2.5rem; font-weight: 800; line-height: 1; margin-bottom: 8px; color: #ef4444;">{len(violations):,}</div>
                    <div style="font-size: 0.875rem; color: #64748b; font-weight: 500;">부적합 건수</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div style="background: #f0fdf4; color: #22c55e; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 16px;">
                    📈
                </div>
                <div>
                    <div style="font-size: 2.5rem; font-weight: 800; line-height: 1; margin-bottom: 8px; color: #22c55e;">{100-violation_rate:.1f}%</div>
                    <div style="font-size: 0.875rem; color: #64748b; font-weight: 500;">적합률</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div style="background: #fef3c7; color: #f59e0b; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 16px;">
                    🧪
                </div>
                <div>
                    <div style="font-size: 2.5rem; font-weight: 800; line-height: 1; margin-bottom: 8px; color: #f59e0b;">{unique_samples:,}</div>
                    <div style="font-size: 0.875rem; color: #64748b; font-weight: 500;">시료 수</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_upload_page(self):
        """프리미엄 업로드 페이지 (로컬 버전과 동일)"""
        self.render_page_header("데이터 업로드", "Excel 파일을 업로드하여 환경 데이터 분석을 시작하세요")
        
        # 업로드 영역
        st.markdown("""
        <div style="background: white; border: 2px dashed #cbd5e1; border-radius: 16px; padding: 3rem 2rem; text-align: center; margin: 2rem 0; transition: all 0.3s ease;">
            <div style="font-size: 4rem; color: #94a3b8; margin-bottom: 1rem;">📁</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin-bottom: 0.5rem;">파일을 업로드하세요</div>
            <div style="font-size: 1rem; color: #64748b; margin-bottom: 2rem;">Excel (.xlsx, .xls) 또는 CSV 파일을 지원합니다</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 샘플 데이터 로드 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📊 샘플 데이터로 시작하기", use_container_width=True, type="primary"):
                self.load_sample_data()
        
        # 지원 형식 안내
        st.markdown("""
        ### 📋 지원 파일 형식
        - **Excel 파일**: `.xlsx`, `.xls`
        - **CSV 파일**: `.csv`
        - **최대 파일 크기**: 200MB
        
        ### 📊 필수 컬럼 구조
        환경 데이터 분석을 위해 다음 컬럼들이 포함되어야 합니다:
        - 시료명, 분석번호, 시험항목, 시험단위
        - 결과(성적서), 시험자입력값
        - 기준대비 초과여부, 시험자, 시험표준
        """)    def r
ender_dashboard_page(self):
        """프리미엄 대시보드 페이지 (로컬 버전과 완전 동일)"""
        # 파일 확인
        if not st.session_state.active_file:
            self.render_upload_page()
            return
        
        file_data = st.session_state.uploaded_files[st.session_state.active_file]
        test_results = file_data['test_results']
        project_name = st.session_state.active_file.replace('.xlsx', '').replace('.xls', '')
        
        # 페이지 헤더 (저장 버튼 포함)
        self.render_page_header("분석 대시보드", f"프로젝트: {project_name}", show_save_button=True)
        
        # KPI 카드
        self.render_kpi_cards(test_results)
        
        # 메인 콘텐츠 영역
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 차트 영역을 좌우로 분할
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.markdown("#### 📊 부적합 항목 분포")
                try:
                    donut_fig, _ = self.dashboard_engine.create_violation_charts(test_results)
                    st.plotly_chart(donut_fig, use_container_width=True, key="premium_donut")
                except Exception as e:
                    st.error(f"도넛 차트 오류: {e}")
            
            with chart_col2:
                st.markdown("#### 📈 부적합 시료별 건수")
                try:
                    _, bar_fig = self.dashboard_engine.create_violation_charts(test_results)
                    st.plotly_chart(bar_fig, use_container_width=True, key="premium_bar")
                except Exception as e:
                    st.error(f"막대 차트 오류: {e}")
        
        with col2:
            # 우측 패널 - 상세 정보
            st.markdown("#### 📋 프로젝트 정보")
            
            # 프로젝트 정보 카드
            st.markdown(f"""
            <div style="background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid #e2e8f0;">
                <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.5rem;">프로젝트명</div>
                <div style="font-size: 1rem; font-weight: 600; color: #1e293b; margin-bottom: 1rem;">{project_name}</div>
                
                <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.5rem;">업로드 시간</div>
                <div style="font-size: 0.875rem; color: #1e293b; margin-bottom: 1rem;">{file_data['upload_time'].strftime('%Y-%m-%d %H:%M:%S')}</div>
                
                <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.5rem;">데이터 상태</div>
                <div style="color: #22c55e; font-weight: 500;">✅ 분석 완료</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 빠른 통계
            st.markdown("#### 📊 빠른 통계")
            
            violations = [r for r in test_results if r.is_non_conforming()]
            unique_items = len(set(r.test_item for r in test_results))
            unique_testers = len(set(r.tester for r in test_results))
            
            st.markdown(f"""
            <div style="background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #e2e8f0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                    <span style="color: #64748b;">시험 항목 수</span>
                    <span style="font-weight: 600;">{unique_items}개</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                    <span style="color: #64748b;">시험자 수</span>
                    <span style="font-weight: 600;">{unique_testers}명</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                    <span style="color: #64748b;">부적합률</span>
                    <span style="font-weight: 600; color: #ef4444;">{len(violations)/len(test_results)*100:.1f}%</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #64748b;">적합률</span>
                    <span style="font-weight: 600; color: #22c55e;">{(1-len(violations)/len(test_results))*100:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 하단 데이터 테이블
        st.markdown("---")
        st.markdown("#### 📋 상세 데이터")
        
        # 데이터프레임 표시 (TestResult 객체를 DataFrame으로 변환)
        df_data = []
        for result in test_results:
            df_data.append({
                '시료명': result.sample_name,
                '분석번호': result.analysis_number,
                '시험항목': result.test_item,
                '시험단위': result.test_unit,
                '결과(성적서)': result.result_value,
                '시험자입력값': result.input_value,
                '기준대비 초과여부': result.conformity,
                '시험자': result.tester,
                '시험표준': result.test_standard
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, height=400)    d
ef render_reports_management_page(self):
        """보고서 관리 페이지 (로컬 버전의 3탭 구조 완전 복제)"""
        self.render_page_header("보고서 관리", "분석된 파일 이력을 관리하고 다시 불러올 수 있습니다")
        
        # 탭으로 구성 (로컬 버전과 완전 동일)
        tab1, tab2, tab3 = st.tabs(["📁 새 파일 분석", "📋 분석 이력", "🗂️ 저장 폴더"])
        
        with tab1:
            # 파일 업로드 영역
            st.markdown("### 📁 새 파일 분석")
            uploaded_file = st.file_uploader("Excel 파일을 업로드하여 새로운 분석을 시작하세요", type=['xlsx', 'xls'])
            
            if uploaded_file:
                # 업로드 일자 설정
                col_date, col_client = st.columns(2)
                with col_date:
                    upload_date = st.date_input(
                        "업로드 일자",
                        value=datetime.now().date(),
                        key="upload_date_input"
                    )
                    upload_time_input = st.time_input(
                        "업로드 시간",
                        value=datetime.now().time(),
                        key="upload_time_input"
                    )
                
                with col_client:
                    client = st.text_input(
                        "의뢰 기관",
                        value="미지정",
                        key="client_input",
                        help="의뢰 기관명을 입력하세요"
                    )
                
                if st.button("📊 파일 분석 시작", type="primary", use_container_width=True):
                    with st.spinner("파일을 처리하고 있습니다..."):
                        # 업로드 시간 조합
                        upload_datetime = datetime.combine(upload_date, upload_time_input)
                        
                        # 파일 처리
                        if self.process_uploaded_file(uploaded_file, client, upload_datetime):
                            st.success(f"✅ 파일 '{uploaded_file.name}' 처리 완료!")
                            
                            # 대시보드로 이동 버튼
                            if st.button("📊 대시보드에서 보기", type="primary"):
                                st.session_state.current_page = 'dashboard'
                                st.rerun()
        
        with tab2:
            # 보고서 이력 표시
            st.markdown("### 📋 분석 이력")
            
            if not st.session_state.report_history:
                st.info("아직 분석된 파일이 없습니다. 새 파일 분석 탭에서 파일을 업로드하여 분석을 시작하세요.")
            else:
                # 이력 카드들
                for i, report in enumerate(st.session_state.report_history):
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 8px;">
                                <div style="font-weight: 600; color: #1e293b; margin-bottom: 4px;">
                                    📄 {report['project_name']}
                                </div>
                                <div style="font-size: 12px; color: #64748b;">
                                    업로드: {report['upload_time'].strftime('%Y-%m-%d %H:%M')}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.metric("총 시험", f"{report['total_tests']}건")
                        
                        with col3:
                            st.metric("부적합", f"{report['violations']}건", f"{report['violation_rate']:.1f}%")
                        
                        with col4:
                            if st.button("📊 보기", key=f"view_report_{i}"):
                                st.session_state.active_file = report['filename']
                                st.session_state.current_page = 'dashboard'
                                st.rerun()
        
        with tab3:
            # 저장 폴더 정보
            st.markdown("### 🗂️ 저장 폴더")
            
            folder_info = [
                {'name': '전체 폴더', 'icon': '📁', 'count': len(st.session_state.uploaded_files), 'description': '모든 분석 파일'},
                {'name': '업로드 파일', 'icon': '📤', 'count': len(st.session_state.uploaded_files), 'description': '원본 업로드 파일'},
                {'name': '처리된 파일', 'icon': '⚙️', 'count': len(st.session_state.uploaded_files), 'description': '분석 처리된 파일'},
                {'name': '보고서', 'icon': '📄', 'count': len(st.session_state.report_history), 'description': '생성된 보고서'}
            ]
            
            for folder in folder_info:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid #e2e8f0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <div style="font-size: 2rem;">{folder['icon']}</div>
                            <div>
                                <div style="font-weight: 600; color: #1e293b;">{folder['name']}</div>
                                <div style="font-size: 0.875rem; color: #64748b;">{folder['description']}</div>
                            </div>
                        </div>
                        <div style="background: #f1f5f9; color: #475569; padding: 0.5rem 1rem; border-radius: 0.5rem; font-weight: 600;">
                            {folder['count']}개
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_integrated_analysis_page(self):
        """통합 분석 페이지 렌더링 (로컬 버전의 차트들 완전 복제)"""
        self.render_page_header("통합 분석", "AI 기반 환경 데이터 통합 분석 및 인사이트")
        
        # 기간 선택
        col1, col2 = st.columns(2)
        with col1:
            period_preset = st.selectbox(
                "분석 기간 선택",
                ["오늘", "최근 7일", "최근 1개월", "최근 3개월", "올해"]
            )
        
        with col2:
            analysis_type = st.selectbox(
                "분석 유형",
                ["전체 분석", "부적합 항목 분석", "시료별 분석", "시험자별 분석"]
            )
        
        # 분석 데이터 준비
        if st.session_state.report_history:
            # 부적합 항목 데이터 준비
            non_conforming_items = {}
            files_data = []
            
            for report in st.session_state.report_history:
                # 부적합 항목 집계
                for result in report.get('test_results', []):
                    if result.is_non_conforming():
                        item = result.test_item
                        non_conforming_items[item] = non_conforming_items.get(item, 0) + 1
                
                # 파일 데이터 준비
                files_data.append({
                    'filename': report['filename'],
                    'test_results': [{'is_non_conforming': r.is_non_conforming()} for r in report.get('test_results', [])],
                    'upload_time': report['upload_time'].isoformat() if hasattr(report['upload_time'], 'isoformat') else str(report['upload_time'])
                })
            
            # 차트 영역
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**❌ 부적합 항목별 분포**")
                non_conforming_fig = self.integrated_analysis_engine.create_non_conforming_chart(non_conforming_items)
                st.plotly_chart(non_conforming_fig, use_container_width=True, key="integrated_non_conforming")
            
            with col2:
                st.markdown("**🧪 실험별 오염수준 분포**")
                contamination_fig = self.integrated_analysis_engine.create_contamination_level_chart(files_data)
                st.plotly_chart(contamination_fig, use_container_width=True, key="integrated_contamination")
            
            # 추이 차트
            st.markdown("#### 📈 시험/시료별 추이")
            file_trend_fig = self.integrated_analysis_engine.create_file_trend_chart(files_data)
            st.plotly_chart(file_trend_fig, use_container_width=True, key="file_trend")
            
            # AI 인사이트
            st.markdown("---")
            st.markdown("#### 🤖 AI 인사이트")
            
            total_files = len(st.session_state.report_history)
            total_violations = sum(report['violations'] for report in st.session_state.report_history)
            avg_violation_rate = sum(report['violation_rate'] for report in st.session_state.report_history) / total_files if total_files > 0 else 0
            
            insights = [
                f"📊 총 {total_files}개 파일에서 {total_violations}건의 부적합 항목이 발견되었습니다.",
                f"📈 평균 부적합률은 {avg_violation_rate:.1f}%로 {'주의가 필요한' if avg_violation_rate > 10 else '양호한'} 수준입니다.",
                "🔍 주요 부적합 항목에 대한 원인 분석이 권장됩니다.",
                "💡 지속적인 모니터링을 통한 품질 개선이 필요합니다.",
                "📋 정기적인 시험 규격 검토를 통한 기준 최적화를 고려해보세요."
            ]
            
            for insight in insights:
                st.info(insight)
        else:
            st.info("👈 먼저 데이터를 업로드해주세요.")
    
    def render_standards_management_page(self):
        """시험 규격 관리 페이지 렌더링"""
        self.render_page_header("시험 규격 관리", "환경 시험 규격 및 기준 관리")
        
        # 현재 적용 규격
        st.markdown("#### 📋 현재 적용 규격")
        
        standards_data = {
            "시험항목": ["pH", "용존산소", "탁도", "COD", "BOD", "총질소", "총인"],
            "기준값": ["6.5-8.5", "≥5.0", "≤4.0", "≤8.0", "≤3.0", "≤0.5", "≤0.02"],
            "단위": ["pH", "mg/L", "NTU", "mg/L", "mg/L", "mg/L", "mg/L"],
            "시험표준": ["KS M 0011", "KS M 0012", "KS M 0013", "KS M 0014", "KS M 0015", "KS M 0016", "KS M 0017"],
            "상태": ["✅ 적용중", "✅ 적용중", "✅ 적용중", "⚠️ 검토필요", "✅ 적용중", "✅ 적용중", "✅ 적용중"]
        }
        
        standards_df = pd.DataFrame(standards_data)
        st.dataframe(standards_df, use_container_width=True, height=300)
        
        # 규격 관리 기능
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📤 규격 문서 업로드")
            uploaded_standard = st.file_uploader(
                "PDF 규격 문서 업로드",
                type=['pdf'],
                help="시험 규격 PDF 문서를 업로드하세요"
            )
            
            if uploaded_standard:
                st.success(f"✅ 규격 문서 업로드 완료: {uploaded_standard.name}")
        
        with col2:
            st.markdown("#### ⚙️ 규격 설정")
            
            # 새 규격 추가 폼
            with st.form("add_standard"):
                new_item = st.text_input("시험항목")
                new_standard = st.text_input("기준값")
                new_unit = st.text_input("단위")
                new_method = st.text_input("시험표준")
                
                if st.form_submit_button("➕ 규격 추가"):
                    st.success("✅ 새 규격이 추가되었습니다 (데모 버전)")
    
    def run(self):
        """애플리케이션 실행 (로컬 버전과 완전 동일한 구조)"""
        self.render_sidebar()
        
        if st.session_state.current_page == 'dashboard':
            self.render_dashboard_page()
        elif st.session_state.current_page == 'reports':
            self.render_reports_management_page()
        elif st.session_state.current_page == 'standards':
            self.render_standards_management_page()
        elif st.session_state.current_page == 'integrated_analysis':
            self.render_integrated_analysis_page()
        else:
            self.render_dashboard_page()

if __name__ == "__main__":
    app = AquaAnalyticsDemo()
    app.run()