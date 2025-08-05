#!/usr/bin/env python3
"""
Aqua-Analytics Premium: 환경 데이터 인사이트 플랫폼
완성도 높은 UX/UI 디자인 적용
"""

import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd
from typing import Dict, Any, Optional, List
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# 프로젝트 루트 경로를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src" / "components"))
sys.path.insert(0, str(project_root / "src" / "core"))
sys.path.insert(0, str(project_root / "src" / "utils"))

st.set_page_config(
    page_title="Aqua-Analytics | 환경 데이터 인사이트 플랫폼",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AquaAnalyticsPremium:
    """Aqua-Analytics Premium 애플리케이션"""
    
    def __init__(self):
        self.apply_premium_theme()
        self.setup_folder_structure()
        self.initialize_components()
        self.initialize_session_state()
    
    def apply_premium_theme(self):
        """프리미엄 테마 CSS 적용"""
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://cdn.jsdelivr.net/npm/feather-icons@4.28.0/dist/feather.min.css');
        
        /* 전역 변수 정의 */
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
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        
        /* 전체 앱 스타일 */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--gray-50);
        }
        
        /* 사이드바 스타일링 */
        .css-1d391kg, .css-1cypcdb {
            background-color: #ffffff;
            border-right: 1px solid var(--gray-200);
        }
        
        /* 메인 컨텐츠 영역 */
        .main .block-container {
            background-color: var(--gray-50);
            padding: 2rem 2rem 4rem 2rem;
            max-width: none;
        }
        
        /* 헤더 스타일 */
        .premium-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding: 1.5rem 0;
            border-bottom: 1px solid var(--gray-200);
        }
        
        .header-title {
            font-size: 2rem;
            font-weight: 700;
            color: var(--gray-800);
            margin: 0;
        }
        
        .header-subtitle {
            color: var(--gray-500);
            font-size: 1rem;
            margin: 0.25rem 0 0 0;
        }
        
        .header-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        .action-btn {
            width: 40px;
            height: 40px;
            border-radius: 0.5rem;
            border: 1px solid var(--gray-300);
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            color: var(--gray-600);
        }
        
        .action-btn:hover {
            background: var(--gray-50);
            border-color: var(--gray-400);
            transform: translateY(-1px);
        }
        
        /* KPI 카드 시스템 */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .kpi-card {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 1rem;
            padding: 1.5rem;
            position: relative;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            overflow: hidden;
        }
        
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-500), var(--primary-600));
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        
        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-xl);
            border-color: var(--gray-300);
        }
        
        .kpi-card:hover::before {
            transform: scaleX(1);
        }
        
        .kpi-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }
        
        .kpi-title {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--gray-500);
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }
        
        .kpi-icon {
            width: 24px;
            height: 24px;
            color: var(--gray-400);
        }
        
        .kpi-value {
            font-size: 2.5rem;
            font-weight: 800;
            line-height: 1;
            margin: 0.5rem 0;
        }
        
        .kpi-value.primary { color: var(--gray-800); }
        .kpi-value.success { color: var(--success); }
        .kpi-value.warning { color: var(--warning); }
        .kpi-value.error { color: var(--error); }
        
        .kpi-subtitle {
            font-size: 0.875rem;
            color: var(--gray-500);
            font-weight: 500;
        }
        
        .kpi-trend {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.5rem;
            border-radius: 0.375rem;
            margin-top: 0.5rem;
        }
        
        .kpi-trend.up {
            background: #dcfce7;
            color: #166534;
        }
        
        .kpi-trend.down {
            background: #fef2f2;
            color: #991b1b;
        }
        
        /* 차트 컨테이너 */
        .chart-container {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow-sm);
        }
        
        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .chart-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--gray-800);
        }
        
        .chart-subtitle {
            font-size: 0.875rem;
            color: var(--gray-500);
            margin-top: 0.25rem;
        }
        
        /* 리포트 요약 카드 */
        .report-summary {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 1rem;
            padding: 1.5rem;
            height: fit-content;
        }
        
        .report-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--gray-800);
            margin-bottom: 1rem;
        }
        
        .report-content {
            font-size: 0.875rem;
            line-height: 1.6;
            color: var(--gray-600);
            margin-bottom: 1.5rem;
        }
        
        .report-highlight {
            background: var(--primary-50);
            border-left: 4px solid var(--primary-500);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0 0.5rem 0.5rem 0;
        }
        
        /* 버튼 스타일 */
        .btn-primary {
            background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
            color: white;
            border: none;
            border-radius: 0.5rem;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-size: 0.875rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-lg);
        }
        
        .btn-secondary {
            background: white;
            color: var(--gray-700);
            border: 1px solid var(--gray-300);
            border-radius: 0.5rem;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-size: 0.875rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .btn-secondary:hover {
            background: var(--gray-50);
            border-color: var(--gray-400);
        }
        
        /* 데이터 테이블 스타일 */
        .data-table-container {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 1rem;
            overflow: hidden;
            margin-top: 1.5rem;
        }
        
        .table-header {
            background: var(--gray-50);
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--gray-200);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .table-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--gray-800);
        }
        
        .table-count {
            font-size: 0.875rem;
            color: var(--gray-500);
            background: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            border: 1px solid var(--gray-200);
        }
        
        /* 사이드바 브랜딩 */
        .sidebar-brand {
            display: flex;
            align-items: center;
            padding: 1.5rem 1rem;
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--gray-100);
        }
        
        .brand-logo {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
            border-radius: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 0.75rem;
            font-size: 1.25rem;
            box-shadow: var(--shadow-md);
        }
        
        .brand-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--gray-800);
        }
        
        .brand-subtitle {
            font-size: 0.75rem;
            color: var(--gray-500);
            margin-top: 0.125rem;
        }
        
        /* 네비게이션 메뉴 */
        .nav-section {
            margin-bottom: 1.5rem;
        }
        
        .nav-section-title {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--gray-400);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.75rem;
            padding: 0 1rem;
        }
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem;
            }
            
            .kpi-grid {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            
            .premium-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }
            
            .header-actions {
                align-self: flex-end;
            }
        }
        
        /* 애니메이션 */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .fade-in-up {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* 로딩 스켈레톤 */
        .skeleton {
            background: linear-gradient(90deg, var(--gray-100) 25%, var(--gray-200) 50%, var(--gray-100) 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }
        
        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def setup_folder_structure(self):
        """체계적인 폴더 구조 설정"""
        self.base_folder = Path("aqua_analytics_data")
        self.folders = {
            'base': self.base_folder,
            'uploads': self.base_folder / "uploads",
            'processed': self.base_folder / "processed", 
            'reports': self.base_folder / "reports",
            'dashboard_reports': self.base_folder / "reports" / "dashboard",
            'integrated_reports': self.base_folder / "reports" / "integrated",
            'database': self.base_folder / "database"
        }
        
        # 모든 폴더 생성
        for folder_name, folder_path in self.folders.items():
            folder_path.mkdir(parents=True, exist_ok=True)
    
    def get_folder_path(self, folder_type: str) -> Path:
        """폴더 경로 반환"""
        return self.folders.get(folder_type, self.base_folder)
    
    def initialize_session_state(self):
        """세션 상태 초기화"""
        default_states = {
            'uploaded_files': {},
            'active_file': None,
            'current_page': 'dashboard',
            'dashboard_initialized': False,
            'report_history': []  # 보고서 이력 저장
        }
        
        for key, value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
        # 저장된 데이터 자동 로드
        self.load_saved_data()
        
        # 데이터베이스에서 기존 데이터 로드
        self.load_existing_data()
    
    def initialize_components(self):
        """컴포넌트 초기화"""
        try:
            from data_processor import DataProcessor
            from dynamic_dashboard_engine import DynamicDashboardEngine
            from report_generator import ReportGenerator
            from standards_manager import standards_manager
            from database_manager import db_manager
            
            self.data_processor = DataProcessor()
            self.dashboard_engine = DynamicDashboardEngine(self.data_processor)
            self.report_generator = ReportGenerator()
            self.standards_manager = standards_manager
            self.db_manager = db_manager
            
            # 데이터베이스 경로를 새로운 구조로 설정
            self.db_manager.db_path = self.get_folder_path('database') / "analysis_database.json"
            self.db_manager.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 통합 분석 엔진과 기간 컨트롤러는 직접 구현
            self.integrated_analysis_engine = self.create_integrated_analysis_engine()
            self.period_controller = self.create_period_controller()
            
            # 통합 분석 엔진에 db_manager 설정
            if hasattr(self.integrated_analysis_engine, 'set_db_manager'):
                self.integrated_analysis_engine.set_db_manager(self.db_manager)
            
        except ImportError as e:
            st.error(f"컴포넌트 로드 실패: {e}")
            st.stop()
    
    def create_integrated_analysis_engine(self):
        """통합 분석 엔진 생성"""
        # 외부 통합 분석 엔진 사용
        try:
            from integrated_analysis_engine import integrated_analysis_engine
            return integrated_analysis_engine
        except ImportError:
            # 임포트 실패 시 내장 클래스 사용
            class IntegratedAnalysisEngine:
                def __init__(self, db_manager):
                    self.db_manager = db_manager
            
                def analyze_period(self, start_date, end_date):
                    return self.db_manager.get_integrated_analysis_data(start_date, end_date)
                
                def create_conforming_chart(self, conforming_items):
                    if not conforming_items:
                        fig = go.Figure()
                        fig.add_annotation(text="적합 항목 없음", x=0.5, y=0.5, font_size=16, showarrow=False)
                        fig.update_layout(height=300, showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
                        return fig
                    
                    sorted_items = sorted(conforming_items.items(), key=lambda x: x[1], reverse=True)[:10]
                    labels = [item[0] for item in sorted_items]
                    values = [item[1] for item in sorted_items]
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=labels, values=values, hole=0.4,
                        marker=dict(colors=px.colors.qualitative.Set3, line=dict(color='white', width=2)),
                        textinfo='label+percent', textposition='outside'
                    )])
                    
                    fig.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20), showlegend=False, font=dict(size=12))
                    return fig
                
                def create_non_conforming_chart(self, non_conforming_items):
                    if not non_conforming_items:
                        fig = go.Figure()
                        fig.add_annotation(text="부적합 항목 없음", x=0.5, y=0.5, font_size=16, showarrow=False)
                        fig.update_layout(height=300, showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
                        return fig
                    
                    sorted_items = sorted(non_conforming_items.items(), key=lambda x: x[1], reverse=True)[:10]
                    labels = [item[0] for item in sorted_items]
                    values = [item[1] for item in sorted_items]
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=labels, values=values, hole=0.4,
                        marker=dict(colors=px.colors.qualitative.Set1, line=dict(color='white', width=2)),
                        textinfo='label+percent', textposition='outside'
                    )])
                    
                    fig.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20), showlegend=False, font=dict(size=12))
                    return fig
                
                def create_monthly_trend_chart(self, monthly_stats):
                    if not monthly_stats:
                        fig = go.Figure()
                        fig.add_annotation(text="데이터 없음", x=0.5, y=0.5, font_size=16, showarrow=False)
                        fig.update_layout(height=300, showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
                        return fig
                
                    sorted_months = sorted(monthly_stats.keys())
                    months = [datetime.strptime(month, "%Y-%m").strftime("%Y년 %m월") for month in sorted_months]
                    
                    total_tests = [monthly_stats[month]["tests"] for month in sorted_months]
                    violations = [monthly_stats[month]["violations"] for month in sorted_months]
                    violation_rates = [(v/t*100) if t > 0 else 0 for v, t in zip(violations, total_tests)]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=months, y=total_tests, name='총 시험 건수', marker_color='lightblue', yaxis='y'))
                    fig.add_trace(go.Scatter(x=months, y=violation_rates, mode='lines+markers', name='부적합률 (%)', 
                                           line=dict(color='red', width=3), marker=dict(size=8), yaxis='y2'))
                    
                    fig.update_layout(
                        title="월별 시험 건수 및 부적합률 추이", xaxis_title="월",
                        yaxis=dict(title="시험 건수", side="left"),
                        yaxis2=dict(title="부적합률 (%)", side="right", overlaying="y"),
                        height=400, margin=dict(t=50, b=50, l=50, r=50), hovermode='x unified'
                    )
                    return fig
                
                def generate_integrated_report_html(self, analysis_data, start_date, end_date):
                    """통합 분석 엔진의 HTML 생성 함수 호출"""
                    return self.integrated_analysis_engine.generate_integrated_report_html(
                        analysis_data, start_date, end_date
                    )
        
            return IntegratedAnalysisEngine(self.db_manager)
    
    def create_period_controller(self):
        """기간 컨트롤러 생성"""
        class PeriodController:
            def get_preset_periods(self):
                now = datetime.now()
                today = now.replace(hour=23, minute=59, second=59)
                return {
                    "오늘": (now.replace(hour=0, minute=0, second=0), today),
                    "최근 7일": (now - timedelta(days=7), today),
                    "최근 1개월": (now - timedelta(days=30), today),
                    "최근 3개월": (now - timedelta(days=90), today),
                    "올해": (datetime(now.year, 1, 1), today)
                }
            
            def render_period_selector(self):
                # 세션 상태 초기화
                if 'selected_period' not in st.session_state:
                    st.session_state.selected_period = "최근 1개월"
                if 'custom_start_date' not in st.session_state:
                    st.session_state.custom_start_date = datetime.now() - timedelta(days=30)
                if 'custom_end_date' not in st.session_state:
                    st.session_state.custom_end_date = datetime.now()
                
                # 기간 설정 카드
                st.markdown("### 📅 기간 설정")
                
                # 사전 정의된 기간 버튼들
                col1, col2, col3, col4, col5 = st.columns(5)
                preset_buttons = ["오늘", "최근 7일", "최근 1개월", "최근 3개월", "올해"]
                columns = [col1, col2, col3, col4, col5]
                
                for i, (period_name, col) in enumerate(zip(preset_buttons, columns)):
                    with col:
                        if st.button(
                            period_name, 
                            key=f"preset_{i}",
                            use_container_width=True,
                            type="primary" if st.session_state.selected_period == period_name else "secondary"
                        ):
                            st.session_state.selected_period = period_name
                            st.rerun()
                
                # 구분선
                st.markdown("---")
                
                # 사용자 지정 기간
                st.markdown("**사용자 지정 기간**")
                
                col_start, col_end, col_apply = st.columns([2, 2, 1])
                
                with col_start:
                    custom_start = st.date_input(
                        "시작일",
                        value=st.session_state.custom_start_date.date(),
                        key="custom_start_input"
                    )
                
                with col_end:
                    custom_end = st.date_input(
                        "종료일",
                        value=st.session_state.custom_end_date.date(),
                        key="custom_end_input"
                    )
                
                with col_apply:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🔍 조회", key="apply_custom_period", use_container_width=True):
                        st.session_state.selected_period = "사용자 지정"
                        st.session_state.custom_start_date = datetime.combine(custom_start, datetime.min.time())
                        st.session_state.custom_end_date = datetime.combine(custom_end, datetime.max.time())
                        st.rerun()
                
                # 선택된 기간 계산
                if st.session_state.selected_period == "사용자 지정":
                    start_date = st.session_state.custom_start_date
                    end_date = st.session_state.custom_end_date
                else:
                    presets = self.get_preset_periods()
                    start_date, end_date = presets[st.session_state.selected_period]
                
                # 현재 선택된 기간 표시
                period_display = f"**선택된 기간:** {start_date.strftime('%Y년 %m월 %d일')} ~ {end_date.strftime('%Y년 %m월 %d일')}"
                st.info(period_display)
                
                return start_date, end_date
        
        return PeriodController()
    
    def render_sidebar(self):
        """프리미엄 사이드바 렌더링"""
        with st.sidebar:
            # 브랜드 헤더
            st.markdown("""
            <div class="sidebar-brand">
                <div class="brand-logo">💧</div>
                <div>
                    <div class="brand-title">Aqua-Analytics</div>
                    <div class="brand-subtitle">환경 데이터 인사이트</div>
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
            
            # 폴더별 바로가기 버튼 (실시간 정보 포함)
            folder_buttons = [
                {'key': 'base', 'label': '전체 폴더', 'icon': '📁'},
                {'key': 'uploads', 'label': '업로드 파일', 'icon': '📤'},
                {'key': 'processed', 'label': '처리된 파일', 'icon': '⚙️'},
                {'key': 'dashboard_reports', 'label': '보고서', 'icon': '📄'}
            ]
            
            # 실시간 폴더 정보 표시
            for folder in folder_buttons:
                # 실시간 파일 개수 조회
                try:
                    folder_path = self.get_folder_path(folder['key'])
                    if folder_path.exists():
                        files = list(folder_path.glob('*'))
                        file_count = len([f for f in files if f.is_file()])
                        dir_count = len([f for f in files if f.is_dir()])
                        count_text = f"({file_count}개)"
                    else:
                        count_text = "(0개)"
                except:
                    count_text = ""
                
                # 버튼 표시 (파일 개수 포함)
                button_label = f"{folder['icon']} {folder['label']} {count_text}"
                
                if st.button(button_label, 
                           key=f"open_{folder['key']}_folder", 
                           use_container_width=True):
                    try:
                        folder_info = self.open_storage_folder(folder['key'])
                        if folder_info:
                            # 세션 상태에 알림 정보 저장 (우측 상단 표시용)
                            st.session_state.folder_notification = {
                                'message': f"📁 {folder_info['name']} 열기 완료!",
                                'details': f"📄 파일 {folder_info['files']}개, 📁 폴더 {folder_info['dirs']}개 ({folder_info['size']})",
                                'type': 'success'
                            }
                            st.rerun()
                    except Exception as e:
                        st.session_state.folder_notification = {
                            'message': f"폴더 열기 실패: {e}",
                            'type': 'error'
                        }
                        st.rerun()
            
            # CTA 카드
            st.markdown("---")
            st.markdown("""
            <div style="background: white; border: 1px solid var(--gray-200); border-radius: 0.75rem; padding: 1rem;">
                <h3 style="font-size: 0.875rem; font-weight: 600; color: var(--gray-800); margin-bottom: 0.5rem;">
                    데이터 분석 시작
                </h3>
                <p style="font-size: 0.75rem; color: var(--gray-500); margin-bottom: 1rem; line-height: 1.4;">
                    새로운 파일을 업로드하여 분석을 시작하세요.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📁 파일 업로드", key="sidebar_upload", use_container_width=True):
                st.session_state.current_page = 'reports'
                st.rerun()
    
    def render_page_header(self, title: str, subtitle: str = None, show_save_button: bool = False):
        """프리미엄 페이지 헤더"""
        # 우측 상단 알림 표시
        self.render_top_notification()
        
        if show_save_button and st.session_state.active_file:
            # 저장 버튼이 있는 헤더
            col_title, col_button = st.columns([3, 1])
            
            with col_title:
                st.markdown(f"""
                <div style="padding: 1.5rem 0; border-bottom: 1px solid var(--gray-200);">
                    <h1 style="font-size: 2rem; font-weight: 700; color: var(--gray-800); margin: 0;">{title}</h1>
                    {f'<p style="color: var(--gray-500); font-size: 1rem; margin: 0.25rem 0 0 0;">{subtitle}</p>' if subtitle else ''}
                </div>
                """, unsafe_allow_html=True)
            
            with col_button:
                st.markdown("<br>", unsafe_allow_html=True)  # 버튼 정렬을 위한 공간
                if st.button("💾 데이터베이스 반영", key="save_to_database", use_container_width=True):
                    self.save_dashboard_to_database()
        else:
            # 기본 헤더
            st.markdown(f"""
            <div class="premium-header fade-in-up">
                <div>
                    <h1 class="header-title">{title}</h1>
                    {f'<p class="header-subtitle">{subtitle}</p>' if subtitle else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_top_notification(self):
        """우측 상단 알림 표시"""
        if hasattr(st.session_state, 'folder_notification'):
            notification = st.session_state.folder_notification
            
            # 알림 스타일 정의
            if notification['type'] == 'success':
                bg_color = "#d4edda"
                border_color = "#c3e6cb"
                text_color = "#155724"
                icon = "✅"
            else:
                bg_color = "#f8d7da"
                border_color = "#f5c6cb"
                text_color = "#721c24"
                icon = "❌"
            
            # 우측 상단에 알림 표시
            st.markdown(f"""
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                background-color: {bg_color};
                border: 1px solid {border_color};
                color: {text_color};
                padding: 12px 16px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                max-width: 300px;
                animation: slideInRight 0.3s ease-out;
            ">
                <div style="font-weight: 600; margin-bottom: 4px;">
                    {icon} {notification['message']}
                </div>
                {f'<div style="font-size: 0.9em; opacity: 0.8;">{notification["details"]}</div>' if 'details' in notification else ''}
            </div>
            
            <style>
            @keyframes slideInRight {{
                from {{ transform: translateX(100%); opacity: 0; }}
                to {{ transform: translateX(0); opacity: 1; }}
            }}
            </style>
            """, unsafe_allow_html=True)
            
            # 3초 후 알림 제거
            import time
            time.sleep(0.1)  # 렌더링 완료 대기
            if 'notification_timer' not in st.session_state:
                st.session_state.notification_timer = time.time()
            
            # 3초 경과 시 알림 제거
            if time.time() - st.session_state.notification_timer > 3:
                del st.session_state.folder_notification
                del st.session_state.notification_timer
                st.rerun()
    
    def render_kpi_cards(self, test_results: List):
        """프리미엄 KPI 카드 렌더링 - 카드 형식"""
        if not test_results:
            return
        
        # KPI 데이터 계산
        total_tests = len(test_results)
        violations = [r for r in test_results if r.is_non_conforming()]
        violation_rate = len(violations) / total_tests * 100 if total_tests > 0 else 0
        unique_samples = len(set(r.sample_name for r in test_results))
        
        # 부적합 시료 개수 (중복 제거)
        violation_samples = len(set(v.sample_name for v in violations))
        
        # 주요 부적합 항목
        violation_by_item = {}
        for v in violations:
            violation_by_item[v.test_item] = violation_by_item.get(v.test_item, 0) + 1
        
        top_item = "해당 없음"
        if violation_by_item:
            top_item = max(violation_by_item.items(), key=lambda x: x[1])[0]
            if len(top_item) > 20:
                top_item = top_item[:17] + "..."
        
        # 4개 컬럼으로 KPI 카드 배치
        col1, col2, col3, col4 = st.columns(4)
        
        # 개선된 카드 스타일 CSS
        card_style = """
        <style>
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
        
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-500, #3b82f6), var(--primary-600, #2563eb));
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        
        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
            border-color: #cbd5e1;
        }
        
        .kpi-card:hover::before {
            transform: scaleX(1);
        }
        
        .kpi-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }
        
        .kpi-title {
            font-size: 13px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            line-height: 1.2;
            flex: 1;
            margin-right: 12px;
        }
        
        .kpi-icon {
            font-size: 28px;
            opacity: 0.8;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            border-radius: 12px;
            background: rgba(59, 130, 246, 0.1);
        }
        
        .kpi-value {
            font-size: 36px;
            font-weight: 800;
            line-height: 1;
            margin: 12px 0 8px 0;
            word-break: break-word;
        }
        
        .kpi-value.primary { color: #1e293b; }
        .kpi-value.error { color: #ef4444; }
        .kpi-value.warning { color: #f59e0b; }
        .kpi-value.success { color: #10b981; }
        
        .kpi-subtitle {
            font-size: 13px;
            color: #64748b;
            font-weight: 500;
            line-height: 1.3;
            margin-bottom: 8px;
        }
        
        .kpi-trend {
            font-size: 11px;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        
        .kpi-trend.up {
            background: #fef2f2;
            color: #991b1b;
        }
        
        .kpi-trend.neutral {
            background: #f0f9ff;
            color: #1e40af;
        }
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            .kpi-card {
                height: 140px;
                padding: 20px;
            }
            
            .kpi-value {
                font-size: 28px;
            }
            
            .kpi-icon {
                font-size: 24px;
                width: 32px;
                height: 32px;
            }
        }
        </style>
        """
        
        st.markdown(card_style, unsafe_allow_html=True)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">총 시험 항목</div>
                    <div class="kpi-icon">📋</div>
                </div>
                <div class="kpi-value primary">{total_tests}건</div>
                <div class="kpi-subtitle">{unique_samples}개 시료 분석</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">부적합 시료</div>
                    <div class="kpi-icon">⚠️</div>
                </div>
                <div class="kpi-value error">{violation_samples}개</div>
                <div class="kpi-subtitle">기준치 초과 시료</div>
                <div class="kpi-trend up">↑ {len(violations)}건 부적합</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            trend_class = "up" if violation_rate > 20 else "neutral"
            value_class = "warning" if violation_rate > 20 else "success"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">부적합률</div>
                    <div class="kpi-icon">📊</div>
                </div>
                <div class="kpi-value {value_class}">{violation_rate:.1f}%</div>
                <div class="kpi-subtitle">전체 대비 비율</div>
                <div class="kpi-trend {trend_class}">{len(violations)}/{total_tests} 항목</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">주요 부적합 테스트</div>
                    <div class="kpi-icon">🔬</div>
                </div>
                <div class="kpi-value primary" style="font-size: 20px; line-height: 1.2;">{top_item}</div>
                <div class="kpi-subtitle">가장 빈번한 항목</div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_dashboard_page(self):
        """프리미엄 대시보드 페이지"""
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
                    violations = [r for r in test_results if r.is_non_conforming()]
                    if len(violations) == 0:
                        st.info("부적합 항목이 없습니다.")
            
            with chart_col2:
                st.markdown("#### 📈 부적합 시료별 건수")
                try:
                    # 개선된 막대 차트 생성
                    violations = [r for r in test_results if r.is_non_conforming()]
                    
                    if violations:
                        # 시료별 부적합 건수 계산
                        violation_by_sample = {}
                        for v in violations:
                            sample = v.sample_name
                            violation_by_sample[sample] = violation_by_sample.get(sample, 0) + 1
                        
                        # 상위 10개 시료만 표시
                        sorted_samples = sorted(violation_by_sample.items(), key=lambda x: x[1], reverse=True)[:10]
                        
                        if sorted_samples:
                            # 전체 부적합 건수 대비 비율 계산
                            total_violations = len(violations)
                            
                            samples = [item[0] for item in sorted_samples]
                            counts = [item[1] for item in sorted_samples]
                            percentages = [(count/total_violations)*100 for count in counts]
                            
                            # 개선된 막대 차트 생성
                            import plotly.express as px
                            import plotly.graph_objects as go
                            
                            fig = go.Figure()
                            
                            # 막대 차트에 건수와 비율 표시
                            hover_text = [f"{sample}<br>{count}건 ({percent:.1f}%)" 
                                        for sample, count, percent in zip(samples, counts, percentages)]
                            
                            fig.add_trace(go.Bar(
                                y=samples,
                                x=counts,
                                orientation='h',
                                text=[f"{count}건 ({percent:.1f}%)" for count, percent in zip(counts, percentages)],
                                textposition='auto',
                                hovertext=hover_text,
                                hoverinfo='text',
                                marker=dict(
                                    color='#ef4444',
                                    opacity=0.8
                                )
                            ))
                            
                            fig.update_layout(
                                title="",
                                xaxis_title="부적합 건수",
                                yaxis_title="",
                                height=400,
                                margin=dict(l=20, r=20, t=20, b=20),
                                yaxis=dict(autorange="reversed"),
                                showlegend=False
                            )
                            
                            st.plotly_chart(fig, use_container_width=True, key="premium_bar")
                        else:
                            st.info("부적합 시료가 없습니다.")
                    else:
                        st.info("부적합 항목이 없습니다.")
                        
                except Exception as e:
                    st.error(f"막대 차트 오류: {e}")
        
        with col2:
            # 리포트 요약
            violations = [r for r in test_results if r.is_non_conforming()]
            violation_rate = len(violations) / len(test_results) * 100 if test_results else 0
            
            st.markdown(f"""
            <div class="report-summary fade-in-up">
                <div class="report-title">품질 분석 리포트 요약</div>
                <div class="report-content">
                    전체 <strong>{len(test_results)}개</strong> 시험 항목 중 
                    <strong>{len(violations)}개</strong> 항목에서 기준치 초과가 발견되어, 
                    <strong>{violation_rate:.1f}%</strong>의 부적합률을 기록했습니다.
                </div>
            """, unsafe_allow_html=True)
            
            if violations:
                violation_by_item = {}
                for v in violations:
                    violation_by_item[v.test_item] = violation_by_item.get(v.test_item, 0) + 1
                
                top_item = max(violation_by_item.items(), key=lambda x: x[1])
                
                st.markdown(f"""
                <div class="report-highlight">
                    <strong>{top_item[0]}</strong> 항목에서 가장 많은 부적합({top_item[1]}건)이 
                    발생하여 관련 공정의 정밀 점검이 필요합니다.
                </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="color: var(--success); font-weight: 600;">
                    ✅ 모든 시험 항목이 기준치를 만족합니다.
                </div>
                </div>
                """, unsafe_allow_html=True)
            
            # 3개 카드 액션 버튼들 (한 줄 배치)
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 리포트 미리보기", key="premium_preview", use_container_width=True):
                    st.session_state.show_preview = True
                    st.session_state.show_summary = False
            
            with col2:
                if st.button("📊 분석 요약", key="premium_summary", use_container_width=True):
                    st.session_state.show_summary = True
                    st.session_state.show_preview = False
            
            with col3:
                if st.button("📥 HTML 다운로드", key="premium_download", use_container_width=True):
                    self.generate_html_report(test_results, project_name)
            
            # 미리보기 또는 요약 표시 영역 (3개 카드 합친 가로 크기)
            if st.session_state.get('show_preview', False):
                st.markdown("### 📄 리포트 미리보기")
                with st.container():
                    st.markdown("""
                    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; 
                               padding: 24px; margin: 16px 0;">
                    """, unsafe_allow_html=True)
                    
                    # 미리보기 내용
                    self.render_report_preview_content(test_results, project_name)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # 닫기 버튼
                    if st.button("❌ 미리보기 닫기", key="close_preview"):
                        st.session_state.show_preview = False
                        st.rerun()
            
            elif st.session_state.get('show_summary', False):
                st.markdown("### 📊 분석 요약")
                with st.container():
                    st.markdown("""
                    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; 
                               padding: 24px; margin: 16px 0;">
                    """, unsafe_allow_html=True)
                    
                    # 요약 내용
                    self.render_summary_content(test_results, project_name)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # 닫기 버튼
                    if st.button("❌ 요약 닫기", key="close_summary"):
                        st.session_state.show_summary = False
                        st.rerun()
        
        # 접을 수 있는 데이터 테이블
        with st.expander(f"📋 상세 데이터 ({len(test_results)}개 항목)", expanded=False):
            self.render_premium_table(test_results)
    
    def render_report_preview_content(self, test_results, project_name):
        """리포트 미리보기 내용 렌더링"""
        violations = [r for r in test_results if r.is_non_conforming()]
        violation_rate = len(violations) / len(test_results) * 100 if test_results else 0
        
        # 기본 통계
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("총 시험 항목", len(test_results))
        with col2:
            st.metric("부적합 항목", len(violations))
        with col3:
            st.metric("부적합률", f"{violation_rate:.1f}%")
        with col4:
            unique_samples = len(set(r.sample_name for r in test_results))
            st.metric("시료 개수", unique_samples)
        
        # 부적합 항목 상세
        if violations:
            st.markdown("#### 🔍 부적합 항목 상세")
            violation_df = pd.DataFrame([
                {
                    '시료명': v.sample_name,
                    '시험항목': v.test_item,
                    '측정값': v.get_display_result(),
                    '기준': v.standard_criteria,
                    '시험자': v.tester
                }
                for v in violations[:10]  # 상위 10개만 표시
            ])
            st.dataframe(violation_df, use_container_width=True)
        else:
            st.success("✅ 모든 시험 항목이 기준을 만족합니다.")
    
    def render_summary_content(self, test_results, project_name):
        """분석 요약 내용 렌더링"""
        violations = [r for r in test_results if r.is_non_conforming()]
        violation_rate = len(violations) / len(test_results) * 100 if test_results else 0
        
        # 요약 텍스트
        st.markdown(f"""
        <div style="background: #f8fafc; border-left: 4px solid #3b82f6; padding: 16px; margin: 16px 0;">
            <h4 style="color: #1e293b; margin-bottom: 12px;">📋 {project_name} 분석 요약</h4>
            <p style="color: #475569; line-height: 1.6; margin: 0;">
                전체 <strong>{len(test_results)}개</strong> 시험 항목 중 
                <strong>{len(violations)}개</strong> 항목에서 기준치 초과가 발견되어, 
                <strong>{violation_rate:.1f}%</strong>의 부적합률을 기록했습니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 부적합 항목별 집계
        if violations:
            violation_by_item = {}
            for v in violations:
                violation_by_item[v.test_item] = violation_by_item.get(v.test_item, 0) + 1
            
            st.markdown("#### 📊 부적합 항목별 집계")
            
            # 차트와 테이블을 나란히 배치
            col_chart, col_table = st.columns([1, 1])
            
            with col_chart:
                # 파이 차트
                import plotly.express as px
                df_chart = pd.DataFrame(list(violation_by_item.items()), columns=['항목', '건수'])
                fig = px.pie(df_chart, values='건수', names='항목', title="부적합 항목 분포")
                st.plotly_chart(fig, use_container_width=True)
            
            with col_table:
                # 집계 테이블
                sorted_items = sorted(violation_by_item.items(), key=lambda x: x[1], reverse=True)
                df_summary = pd.DataFrame(sorted_items, columns=['시험항목', '부적합 건수'])
                df_summary['비율(%)'] = (df_summary['부적합 건수'] / len(violations) * 100).round(1)
                st.dataframe(df_summary, use_container_width=True)
        
        # 권장사항
        if violation_rate > 10:
            st.warning("⚠️ 부적합률이 10%를 초과했습니다. 품질관리 강화가 필요합니다.")
        elif violation_rate > 5:
            st.info("ℹ️ 부적합률이 5%를 초과했습니다. 관련 공정을 점검해보세요.")
        else:
            st.success("✅ 양호한 품질 수준을 유지하고 있습니다.")
    
    def render_premium_table(self, test_results):
        """프리미엄 데이터 테이블"""
        if not test_results:
            return
        
        df = pd.DataFrame([
            {
                '시료명': r.sample_name,
                '시험항목': r.test_item,
                '결과': r.get_display_result(),
                '단위': r.test_unit,
                '기준': r.standard_criteria,
                '판정': r.standard_excess,
                '시험자': r.tester
            }
            for r in test_results
        ])
        
        # 검색
        search = st.text_input("🔍 검색", placeholder="시료명, 시험항목으로 검색...")
        if search:
            mask = (
                df['시료명'].str.contains(search, case=False, na=False) |
                df['시험항목'].str.contains(search, case=False, na=False)
            )
            df = df[mask]
        
        # 규격 연결 정보 추가
        df_with_standards = df.copy()
        standard_links = []
        
        for _, row in df.iterrows():
            standard = self.standards_manager.get_standard_by_test_item(row['시험항목'])
            if standard:
                standard_links.append("📋 규격보기")
            else:
                standard_links.append("-")
        
        df_with_standards['규격'] = standard_links
        
        # 스타일링
        def highlight_violations(row):
            if row['판정'] == '부적합':
                return ['background-color: #fef2f2; color: #991b1b; font-weight: 600'] * len(row)
            return [''] * len(row)
        
        styled_df = df_with_standards.style.apply(highlight_violations, axis=1)
        
        # 데이터프레임 표시
        event = st.dataframe(
            styled_df, 
            use_container_width=True, 
            height=400,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # 행 선택 시 규격 표시
        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            if selected_idx < len(df):
                selected_row = df.iloc[selected_idx]
                test_item = selected_row['시험항목']
                
                standard = self.standards_manager.get_standard_by_test_item(test_item)
                if standard:
                    with st.expander(f"📋 {test_item} 시험규격", expanded=True):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**규격명:** {standard['test_item']}")
                            st.write(f"**파일명:** {standard['filename']}")
                            if standard.get('description'):
                                st.write(f"**설명:** {standard['description']}")
                        
                        with col2:
                            download_link = self.standards_manager.get_download_link(standard['filename'])
                            if download_link:
                                st.markdown(f"""
                                <a href="{download_link}" download="{standard['filename']}" 
                                   style="display: inline-block; padding: 8px 16px; background: #3b82f6; color: white; 
                                          text-decoration: none; border-radius: 6px; font-size: 14px; width: 100%; text-align: center;">
                                    📥 다운로드
                                </a>
                                """, unsafe_allow_html=True)
                        
                        # PDF 미리보기
                        self.standards_manager.render_pdf_viewer(standard['filename'], height=400)
                else:
                    st.info(f"'{test_item}' 항목에 대한 시험규격이 등록되지 않았습니다.")
        
        # 통계
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("표시 행수", len(df))
        with col2:
            violations = (df['판정'] == '부적합').sum()
            st.metric("부적합", violations)
        with col3:
            rate = violations / len(df) * 100 if len(df) > 0 else 0
            st.metric("비율", f"{rate:.1f}%")
    
    def render_upload_page(self):
        """프리미엄 업로드 페이지"""
        self.render_page_header("데이터 업로드", "Excel 파일을 업로드하여 환경 데이터 분석을 시작하세요")
        
        # 업로드 영역
        st.markdown("""
        <div style="background: white; border: 2px dashed var(--gray-300); border-radius: 1rem; padding: 3rem; text-align: center; margin: 2rem 0; transition: all 0.3s ease;">
            <div style="font-size: 4rem; margin-bottom: 1rem; color: var(--gray-400);">📁</div>
            <h3 style="color: var(--gray-800); margin-bottom: 0.5rem; font-weight: 600;">
                파일을 드래그하거나 클릭하여 업로드
            </h3>
            <p style="color: var(--gray-500); font-size: 0.875rem;">
                Excel 파일(.xlsx, .xls)을 지원합니다 • 최대 50MB
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("파일 선택", type=['xlsx', 'xls'], label_visibility="collapsed")
        
        if uploaded_file:
            with st.spinner("파일을 처리하고 있습니다..."):
                try:
                    df = pd.read_excel(uploaded_file)
                    test_results = self.data_processor.process_excel_data(df)
                    
                    from datetime import datetime
                    st.session_state.uploaded_files[uploaded_file.name] = {
                        'test_results': test_results,
                        'processed': True,
                        'upload_time': datetime.now()
                    }
                    st.session_state.active_file = uploaded_file.name
                    
                    # 보고서 이력에 저장
                    self.save_to_report_history(uploaded_file.name, test_results)
                    
                    # 데이터베이스에 영구 저장
                    client_name = st.text_input("의뢰 기관명 (선택사항)", placeholder="예: 한국환경공단, A환경연구소")
                    file_id = self.db_manager.save_analysis_result(uploaded_file.name, test_results, client_name)
                    
                    st.success(f"✅ 파일 '{uploaded_file.name}' 처리 완료!")
                    st.info(f"📊 데이터가 영구 저장되었습니다 (ID: {file_id[:8]}...)")
                    st.session_state.current_page = 'dashboard'
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"파일 처리 오류: {e}")
    
    def show_report_modal(self, test_results, project_name):
        """리포트 미리보기"""
        # 탭으로 구성: 요약 / 미리보기 / 다운로드
        tab1, tab2, tab3 = st.tabs(["📋 요약", "👁️ 미리보기", "📥 다운로드"])
        
        with tab1:
            # 요약 정보 전체화면으로 표시
            st.markdown("### 📊 분석 요약")
            
            # 기본 통계 계산
            total_tests = len(test_results)
            violations = [r for r in test_results if r.is_non_conforming()]
            violation_rate = len(violations) / total_tests * 100 if total_tests > 0 else 0
            unique_samples = len(set(r.sample_name for r in test_results))
            
            # KPI 메트릭
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("총 시험 항목", f"{total_tests}건")
            with col2:
                st.metric("총 시료 수", f"{unique_samples}개")
            with col3:
                st.metric("부적합 항목", f"{len(violations)}건")
            with col4:
                st.metric("부적합률", f"{violation_rate:.1f}%")
            
            # 부적합 항목별 집계
            if violations:
                st.markdown("#### 🔍 주요 부적합 항목")
                violation_by_item = {}
                for v in violations:
                    violation_by_item[v.test_item] = violation_by_item.get(v.test_item, 0) + 1
                
                top_items = sorted(violation_by_item.items(), key=lambda x: x[1], reverse=True)[:5]
                for i, (item, count) in enumerate(top_items, 1):
                    st.write(f"{i}. **{item}**: {count}건")
        
        with tab2:
            # 미리보기 전체화면으로 표시
            st.markdown("### 👁️ 리포트 미리보기")
            
            try:
                html_content = self.report_generator.generate_quality_report_html(test_results, project_name)
                
                # 전체화면 HTML 미리보기 (높이 증가)
                st.components.v1.html(html_content, height=1200, scrolling=True)
                
                # 우측 상단에 닫기 버튼
                col_spacer, col_close = st.columns([4, 1])
                with col_close:
                    if st.button("❌ 닫기", key="close_dashboard_preview"):
                        st.rerun()
                        
            except Exception as e:
                st.error(f"리포트 생성 오류: {e}")
        
        with tab3:
            # 다운로드 옵션
            st.markdown("### 📥 다운로드 옵션")
            
            try:
                html_content = self.report_generator.generate_quality_report_html(test_results, project_name)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📄 HTML 파일 다운로드",
                        data=html_content,
                        file_name=f"{project_name}_분석보고서.html",
                        mime="text/html",
                        use_container_width=True
                    )
                
                with col2:
                    if st.button("💾 서버에 저장", key="save_dashboard_to_server", use_container_width=True):
                        self.save_dashboard_to_database()
                
                st.markdown("---")
                st.info("💡 HTML 파일을 다운로드하여 브라우저에서 열거나 인쇄할 수 있습니다.")
                
            except Exception as e:
                st.error(f"리포트 생성 오류: {e}")
    
    def show_summary_report(self, test_results, project_name):
        """요약 보고서"""
        try:
            summary = self.report_generator.generate_summary_report(test_results, project_name)
            
            with st.expander("📊 요약 보고서", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("총 시험", f"{summary['total_tests']}건")
                    st.metric("부적합", f"{len(summary['violations'])}건")
                with col2:
                    st.metric("부적합률", f"{summary['violation_rate']:.1f}%")
                    st.metric("시료수", f"{summary['total_samples']}개")
                
                if summary['recommendations']:
                    st.subheader("💡 개선 권고사항")
                    for i, rec in enumerate(summary['recommendations'], 1):
                        st.warning(f"{i}. {rec}")
                        
        except Exception as e:
            st.error(f"요약 보고서 오류: {e}")
    
    def generate_html_report(self, test_results, project_name):
        """HTML 보고서 생성"""
        try:
            html_content = self.report_generator.generate_quality_report_html(test_results, project_name)
            
            from datetime import datetime
            filename = f"{project_name}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
            st.download_button("📥 HTML 보고서 다운로드", html_content, filename, "text/html")
            st.success("✅ 보고서 준비 완료!")
            
        except Exception as e:
            st.error(f"보고서 생성 오류: {e}")
    
    def save_to_report_history(self, filename, test_results, upload_time=None, client="미지정", file_id=None):
        """보고서 이력에 저장"""
        if upload_time is None:
            upload_time = datetime.now()
        
        # 이미 존재하는 파일인지 확인
        existing_index = None
        for i, report in enumerate(st.session_state.report_history):
            if report['filename'] == filename:
                existing_index = i
                break
        
        report_data = {
            'filename': filename,
            'project_name': filename.replace('.xlsx', '').replace('.xls', ''),
            'test_results': test_results,
            'upload_time': upload_time,
            'client': client,
            'total_tests': len(test_results),
            'violations': len([r for r in test_results if r.is_non_conforming()]),
            'violation_rate': len([r for r in test_results if r.is_non_conforming()]) / len(test_results) * 100 if test_results else 0,
            'file_id': file_id  # file_id 추가
        }
        
        if existing_index is not None:
            # 기존 항목 업데이트
            st.session_state.report_history[existing_index] = report_data
        else:
            # 새 항목 추가 (최신 순으로 정렬)
            st.session_state.report_history.insert(0, report_data)
        
        # 최대 20개까지만 보관
        if len(st.session_state.report_history) > 20:
            st.session_state.report_history = st.session_state.report_history[:20]
    
    def render_reports_management_page(self):
        """보고서 관리 페이지"""
        self.render_page_header("보고서 관리", "분석된 파일 이력을 관리하고 다시 불러올 수 있습니다")
        
        # 탭으로 구성
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
                        try:
                            # 업로드된 파일을 uploads 폴더에 저장
                            uploads_folder = self.get_folder_path('uploads')
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            saved_filename = f"{timestamp}_{uploaded_file.name}"
                            saved_file_path = uploads_folder / saved_filename
                            
                            with open(saved_file_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # 파일 처리
                            df = pd.read_excel(uploaded_file)
                            test_results = self.data_processor.process_excel_data(df)
                            
                            # 업로드 시간 조합
                            upload_datetime = datetime.combine(upload_date, upload_time_input)
                            
                            # 세션 상태에 저장
                            st.session_state.uploaded_files[uploaded_file.name] = {
                                'test_results': test_results,
                                'processed': True,
                                'upload_time': upload_datetime,
                                'client': client
                            }
                            st.session_state.active_file = uploaded_file.name
                        
                            # processed 폴더에 원본 파일 저장
                            try:
                                processed_folder = self.get_folder_path('processed')
                                
                                # 파일명에 날짜 추가
                                file_stem = Path(uploaded_file.name).stem
                                file_suffix = Path(uploaded_file.name).suffix
                                processed_filename = f"{upload_date.strftime('%Y%m%d')}_{file_stem}{file_suffix}"
                                processed_path = processed_folder / processed_filename
                                
                                # 파일 저장
                                with open(processed_path, 'wb') as f:
                                    f.write(uploaded_file.getvalue())
                                
                                st.success(f"✅ 원본 파일이 processed 폴더에 저장되었습니다: {processed_filename}")
                                
                            except Exception as save_error:
                                st.warning(f"원본 파일 저장 실패: {save_error}")
                            
                            # 데이터베이스 반영
                            try:
                                file_id = self.db_manager.save_analysis_result(
                                    file_name=uploaded_file.name,
                                    test_results=test_results,
                                    client=client,
                                    upload_time=upload_datetime
                                )
                                
                                # 세션 상태에 file_id 추가
                                st.session_state.uploaded_files[uploaded_file.name]['file_id'] = file_id
                                
                                st.success(f"✅ 파일 '{uploaded_file.name}' 처리 완료! (ID: {file_id[:8]}...)")
                                
                            except Exception as db_error:
                                st.warning(f"데이터베이스 저장 실패: {db_error}")
                                st.info("파일 분석은 완료되었지만 영구 저장에 실패했습니다.")
                            
                            # 보고서 이력에 저장 (file_id 포함)
                            self.save_to_report_history(uploaded_file.name, test_results, upload_datetime, client, file_id)
                            
                            # 대시보드로 이동 버튼
                            if st.button("📊 대시보드에서 보기", type="primary"):
                                st.session_state.current_page = 'dashboard'
                                st.rerun()
                                
                        except Exception as e:
                            st.error(f"파일 처리 오류: {e}")
        
        with tab2:
            # 보고서 이력 표시
            st.markdown("### 📋 분석 이력")
            
            # 데이터베이스에서 실제 데이터 로드 (세션 상태와 동기화)
            try:
                db_files = self.db_manager.get_all_files()
                
                # 세션 상태 업데이트 (데이터베이스 기준)
                if db_files:
                    st.session_state.report_history = []
                    for file_data in db_files:
                        # 세션 상태 형식으로 변환
                        report_item = {
                            'filename': file_data.get('filename', ''),
                            'project_name': file_data.get('project_name', ''),
                            'upload_time': datetime.fromisoformat(file_data.get('upload_time', datetime.now().isoformat())),
                            'total_tests': len(file_data.get('test_results', [])),
                            'violations': len([r for r in file_data.get('test_results', []) if r.get('is_non_conforming', False)]),
                            'violation_rate': 0,
                            'test_results': file_data.get('test_results', []),
                            'file_id': file_data.get('file_id', '')
                        }
                        # 부적합률 계산
                        if report_item['total_tests'] > 0:
                            report_item['violation_rate'] = (report_item['violations'] / report_item['total_tests']) * 100
                        
                        st.session_state.report_history.append(report_item)
                
            except Exception as sync_error:
                st.warning(f"데이터베이스 동기화 중 오류: {sync_error}")
            
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
                            st.markdown(f"""
                            <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 8px; text-align: center;">
                                <div style="font-size: 20px; font-weight: 700; color: #1e293b;">
                                    {report['total_tests']}건
                                </div>
                                <div style="font-size: 12px; color: #64748b;">
                                    총 시험 항목
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            violation_color = "#ef4444" if report['violations'] > 0 else "#10b981"
                            st.markdown(f"""
                            <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 8px; text-align: center;">
                                <div style="font-size: 20px; font-weight: 700; color: {violation_color};">
                                    {report['violation_rate']:.1f}%
                                </div>
                                <div style="font-size: 12px; color: #64748b;">
                                    부적합률 ({report['violations']}건)
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col4:
                            if st.button("📊 보기", key=f"view_report_{i}"):
                                # 해당 보고서를 활성화하고 대시보드로 이동
                                st.session_state.uploaded_files[report['filename']] = {
                                    'test_results': report['test_results'],
                                    'processed': True,
                                    'upload_time': report['upload_time']
                                }
                                st.session_state.active_file = report['filename']
                                st.session_state.current_page = 'dashboard'
                                st.rerun()
                            
                            # 삭제 확인 상태 관리
                            delete_key = f"confirm_delete_{i}"
                            
                            if st.button("🗑️", key=f"delete_report_{i}", help="삭제"):
                                st.session_state[delete_key] = True
                            
                            # 삭제 확인 다이얼로그
                            if st.session_state.get(delete_key, False):
                                st.warning(f"⚠️ '{report['project_name']}' 분석 결과를 삭제하시겠습니까?")
                                
                                col_confirm, col_cancel = st.columns(2)
                                with col_confirm:
                                    if st.button("✅ 삭제 확인", key=f"confirm_yes_{i}", type="primary"):
                                        try:
                                            # 삭제 실행
                                            success = self.delete_analysis_report(i, report)
                                            
                                            if success:
                                                # 삭제 성공 시
                                                st.session_state[delete_key] = False
                                                st.success(f"✅ '{report['project_name']}' 분석 결과가 삭제되었습니다.")
                                                
                                                # 세션 상태 강제 동기화
                                                if hasattr(st.session_state, 'report_history'):
                                                    # 데이터베이스에서 다시 로드
                                                    try:
                                                        db_files = self.db_manager.get_all_files()
                                                        st.session_state.report_history = []
                                                        for file_data in db_files:
                                                            report_item = {
                                                                'filename': file_data.get('filename', ''),
                                                                'project_name': file_data.get('project_name', ''),
                                                                'upload_time': datetime.fromisoformat(file_data.get('upload_time', datetime.now().isoformat())),
                                                                'total_tests': len(file_data.get('test_results', [])),
                                                                'violations': len([r for r in file_data.get('test_results', []) if r.get('is_non_conforming', False)]),
                                                                'violation_rate': 0,
                                                                'test_results': file_data.get('test_results', []),
                                                                'file_id': file_data.get('file_id', '')
                                                            }
                                                            if report_item['total_tests'] > 0:
                                                                report_item['violation_rate'] = (report_item['violations'] / report_item['total_tests']) * 100
                                                            st.session_state.report_history.append(report_item)
                                                    except Exception:
                                                        pass
                                                
                                                # 강제 페이지 새로고침
                                                time.sleep(0.3)
                                                st.rerun()
                                            else:
                                                st.error("❌ 삭제에 실패했습니다.")
                                                st.session_state[delete_key] = False
                                                
                                        except Exception as delete_error:
                                            st.error(f"삭제 중 오류: {delete_error}")
                                            st.session_state[delete_key] = False
                                
                                with col_cancel:
                                    if st.button("❌ 취소", key=f"confirm_no_{i}"):
                                        st.session_state[delete_key] = False
                                        st.rerun()
        
        with tab3:
            # 저장 폴더 구조 정보 (실시간 업데이트)
            self.show_folder_structure_info()
            
            # 자동 새로고침 옵션
            st.markdown("---")
            col_auto, col_manual = st.columns(2)
            
            with col_auto:
                auto_refresh = st.checkbox("🔄 자동 새로고침 (10초)", key="auto_refresh_folders")
                if auto_refresh:
                    # 10초마다 자동 새로고침
                    import time
                    time.sleep(0.1)  # 짧은 대기
                    st.rerun()
            
            with col_manual:
                if st.button("🔄 수동 새로고침", key="manual_refresh_folders", use_container_width=True):
                    st.rerun()
    
    def delete_analysis_report(self, index: int, report: dict):
        """분석 보고서 완전 삭제 (개선된 버전)"""
        try:
            file_id = report.get('file_id', '')
            filename = report.get('filename', '')
            
            # 1. 데이터베이스에서 먼저 삭제 (가장 중요)
            if file_id:
                try:
                    success = self.db_manager.delete_analysis_result(file_id)
                    if success:
                        st.success("✅ 데이터베이스에서 삭제되었습니다.")
                    else:
                        st.error("❌ 데이터베이스 삭제에 실패했습니다.")
                        return False
                except Exception as db_error:
                    st.error(f"❌ 데이터베이스 삭제 오류: {db_error}")
                    return False
            
            # 2. 세션 상태에서 제거 (데이터베이스 삭제 성공 후)
            try:
                # 보고서 이력에서 제거
                if 0 <= index < len(st.session_state.report_history):
                    st.session_state.report_history.pop(index)
                
                # 현재 활성 파일이 삭제된 파일이면 초기화
                if hasattr(st.session_state, 'active_file') and st.session_state.active_file == filename:
                    st.session_state.active_file = None
                
                # 업로드된 파일 세션에서 제거
                if hasattr(st.session_state, 'uploaded_files') and filename in st.session_state.uploaded_files:
                    del st.session_state.uploaded_files[filename]
                
            except Exception as session_error:
                st.warning(f"⚠️ 세션 상태 정리 오류: {session_error}")
            
            # 3. 저장된 파일들 삭제 시도 (선택적)
            try:
                self.delete_saved_files(filename)
            except Exception as file_error:
                st.warning(f"⚠️ 저장된 파일 삭제 오류: {file_error}")
            
            return True
            
        except Exception as e:
            st.error(f"삭제 중 오류가 발생했습니다: {e}")
            return False
    
    def sync_report_history_with_database(self):
        """보고서 이력을 데이터베이스와 동기화"""
        try:
            db_files = self.db_manager.get_all_files()
            st.session_state.report_history = []
            
            for file_data in db_files:
                report_item = {
                    'filename': file_data.get('filename', ''),
                    'project_name': file_data.get('project_name', ''),
                    'upload_time': datetime.fromisoformat(file_data.get('upload_time', datetime.now().isoformat())),
                    'total_tests': len(file_data.get('test_results', [])),
                    'violations': len([r for r in file_data.get('test_results', []) if r.get('is_non_conforming', False)]),
                    'violation_rate': 0,
                    'test_results': file_data.get('test_results', []),
                    'file_id': file_data.get('file_id', '')
                }
                
                # 부적합률 계산
                if report_item['total_tests'] > 0:
                    report_item['violation_rate'] = (report_item['violations'] / report_item['total_tests']) * 100
                
                st.session_state.report_history.append(report_item)
                
            return True
            
        except Exception as e:
            print(f"데이터베이스 동기화 오류: {e}")
            return False
    
    def delete_saved_files(self, filename: str):
        """저장된 파일들 삭제 (선택적)"""
        try:
            from pathlib import Path
            
            # processed 폴더에서 파일 찾기 및 삭제
            processed_folder = self.get_folder_path('processed')
            for file_path in processed_folder.glob(f"*{Path(filename).stem}*"):
                try:
                    file_path.unlink()
                    st.info(f"📁 처리된 파일 삭제: {file_path.name}")
                except Exception:
                    pass
            
            # dashboard_reports 폴더에서 HTML 보고서 찾기 및 삭제
            dashboard_reports_folder = self.get_folder_path('dashboard_reports')
            for file_path in dashboard_reports_folder.glob(f"*{Path(filename).stem}*"):
                try:
                    file_path.unlink()
                    st.info(f"📄 대시보드 보고서 삭제: {file_path.name}")
                except Exception:
                    pass
                    
        except Exception as e:
            st.warning(f"파일 삭제 중 일부 오류: {e}")
    
    def render_standards_management_page(self):
        """시험규격 관리 페이지"""
        self.render_page_header("시험 규격 관리", "시험 규격 PDF 파일을 업로드하고 관리할 수 있습니다")
        
        # 탭으로 구분
        tab1, tab2, tab3 = st.tabs(["📁 규격 업로드", "📋 규격 목록", "📊 시험표준 정보"])
        
        with tab1:
            st.markdown("### 📁 새 규격 업로드")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 시험항목 입력
                test_item = st.text_input(
                    "시험항목명",
                    placeholder="예: 총질소(T-N), 아크릴로나이트릴, COD 등",
                    help="이 규격이 적용될 시험항목명을 입력하세요"
                )
                
                # 설명 입력
                description = st.text_area(
                    "규격 설명 (선택사항)",
                    placeholder="규격에 대한 간단한 설명을 입력하세요",
                    height=100
                )
            
            with col2:
                st.markdown("""
                <div style="background: #f0f9ff; padding: 16px; border-radius: 8px; border: 1px solid #bae6fd;">
                    <h4 style="color: #0369a1; margin-bottom: 8px;">📋 업로드 가이드</h4>
                    <ul style="color: #0369a1; font-size: 13px; margin: 0;">
                        <li>PDF 파일만 지원</li>
                        <li>최대 50MB</li>
                        <li>시험항목명 정확히 입력</li>
                        <li>중복 파일명 주의</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # 파일 업로드
            uploaded_file = st.file_uploader(
                "PDF 규격 파일 선택",
                type=['pdf'],
                help="시험 규격 PDF 파일을 업로드하세요"
            )
            
            if uploaded_file and test_item:
                col_a, col_b, col_c = st.columns([1, 1, 2])
                
                with col_b:
                    if st.button("📤 업로드", type="primary", use_container_width=True):
                        with st.spinner("파일을 업로드하고 있습니다..."):
                            success = self.standards_manager.upload_standard(
                                uploaded_file, test_item, description
                            )
                            
                            if success:
                                st.success(f"✅ '{uploaded_file.name}' 업로드 완료!")
                                st.balloons()
                            else:
                                st.error("❌ 업로드 실패")
            
            elif uploaded_file and not test_item:
                st.warning("⚠️ 시험항목명을 입력해주세요.")
        
        with tab2:
            st.markdown("### 📋 등록된 규격 목록")
            
            standards_list = self.standards_manager.get_standards_list()
            
            if not standards_list:
                st.info("등록된 규격이 없습니다. 위 탭에서 규격을 업로드하세요.")
                return
            
            # 검색 기능
            search_term = st.text_input("🔍 규격 검색", placeholder="시험항목명으로 검색...")
            
            if search_term:
                standards_list = [
                    s for s in standards_list 
                    if search_term.lower() in s['test_item'].lower() or 
                       search_term.lower() in s['filename'].lower()
                ]
            
            # 규격 목록 표시
            for i, standard in enumerate(standards_list):
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 8px;">
                            <div style="font-weight: 600; color: #1e293b; margin-bottom: 4px;">
                                📄 {standard['test_item']}
                            </div>
                            <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">
                                파일: {standard['filename']}
                            </div>
                            <div style="font-size: 11px; color: #94a3b8;">
                                {standard.get('description', '설명 없음')[:50]}{'...' if len(standard.get('description', '')) > 50 else ''}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        upload_time = standard['upload_time']
                        if isinstance(upload_time, str):
                            upload_time = datetime.fromisoformat(upload_time.replace('Z', '+00:00'))
                        
                        st.markdown(f"""
                        <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 8px; text-align: center;">
                            <div style="font-size: 12px; color: #64748b;">업로드</div>
                            <div style="font-size: 11px; color: #94a3b8;">
                                {upload_time.strftime('%Y-%m-%d')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        file_size_mb = standard['file_size'] / (1024 * 1024)
                        st.markdown(f"""
                        <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 8px; text-align: center;">
                            <div style="font-size: 12px; color: #64748b;">크기</div>
                            <div style="font-size: 11px; color: #94a3b8;">
                                {file_size_mb:.1f} MB
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        # 미리보기 버튼
                        if st.button("👁️", key=f"preview_std_{i}", help="미리보기"):
                            st.session_state[f"show_preview_{i}"] = True
                        
                        # 다운로드 버튼
                        download_link = self.standards_manager.get_download_link(standard['filename'])
                        if download_link:
                            st.markdown(f"""
                            <a href="{download_link}" download="{standard['filename']}" 
                               style="display: inline-block; padding: 6px 12px; background: #3b82f6; color: white; 
                                      text-decoration: none; border-radius: 6px; font-size: 12px; margin-top: 4px;">
                                📥
                            </a>
                            """, unsafe_allow_html=True)
                        
                        # 삭제 버튼
                        if st.button("🗑️", key=f"delete_std_{i}", help="삭제"):
                            file_id = standard['filename'].replace('.pdf', '').replace(' ', '_')
                            if self.standards_manager.delete_standard(file_id):
                                st.success("삭제 완료!")
                                st.rerun()
                    
                    # 미리보기 모달
                    if st.session_state.get(f"show_preview_{i}", False):
                        with st.expander(f"📄 {standard['test_item']} 규격 미리보기", expanded=True):
                            col_close, col_download = st.columns([3, 1])
                            
                            with col_close:
                                if st.button("❌ 닫기", key=f"close_preview_{i}"):
                                    st.session_state[f"show_preview_{i}"] = False
                                    st.rerun()
                            
                            with col_download:
                                if download_link:
                                    st.markdown(f"""
                                    <a href="{download_link}" download="{standard['filename']}" 
                                       style="display: inline-block; padding: 8px 16px; background: #10b981; color: white; 
                                              text-decoration: none; border-radius: 6px; font-size: 14px;">
                                        📥 다운로드
                                    </a>
                                    """, unsafe_allow_html=True)
                            
                            # PDF 뷰어
                            self.standards_manager.render_pdf_viewer(standard['filename'], height=500)
        
        with tab3:
            # 시험표준 정보 테이블
            st.markdown("### 📊 시험표준 정보")
            st.markdown("업로드된 데이터에서 추출한 시험표준 정보를 확인할 수 있습니다.")
            
            # 데이터베이스에서 시험표준 정보 추출
            try:
                standard_info = self.get_test_standard_info()
                
                if not standard_info:
                    st.info("시험표준 정보가 없습니다. 먼저 데이터를 업로드하고 분석해주세요.")
                    if st.button("📁 보고서 관리로 이동", use_container_width=True):
                        st.session_state.current_page = 'reports'
                        st.rerun()
                    return
                
                # 검색 기능
                search_standard = st.text_input("🔍 시험표준 검색", placeholder="시험항목, 시험단위, 시험표준으로 검색...")
                
                if search_standard:
                    standard_info = [
                        info for info in standard_info
                        if search_standard.lower() in str(info.get('시험항목', '')).lower() or
                           search_standard.lower() in str(info.get('시험단위', '')).lower() or
                           search_standard.lower() in str(info.get('시험표준', '')).lower() or
                           search_standard.lower() in str(info.get('기준 텍스트', '')).lower()
                    ]
                
                # 테이블 표시
                if standard_info:
                    df = pd.DataFrame(standard_info)
                    
                    # 컬럼 순서 정리
                    column_order = ['시험항목', '시험단위', '시험표준', '기준 텍스트', '데이터 건수']
                    df = df.reindex(columns=[col for col in column_order if col in df.columns])
                    
                    st.markdown(f"**총 {len(df)}개의 고유한 시험표준 정보**")
                    
                    # 인터랙티브 테이블
                    st.dataframe(
                        df,
                        use_container_width=True,
                        height=400,
                        column_config={
                            "시험항목": st.column_config.TextColumn("시험항목", width="medium"),
                            "시험단위": st.column_config.TextColumn("시험단위", width="small"),
                            "시험표준": st.column_config.TextColumn("시험표준", width="medium"),
                            "기준 텍스트": st.column_config.TextColumn("기준 텍스트", width="medium"),
                            "데이터 건수": st.column_config.NumberColumn("데이터 건수", width="small")
                        }
                    )
                    
                    # 통계 정보
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        unique_items = df['시험항목'].nunique()
                        st.metric("고유 시험항목", f"{unique_items}개")
                    
                    with col2:
                        unique_standards = df['시험표준'].nunique()
                        st.metric("고유 시험표준", f"{unique_standards}개")
                    
                    with col3:
                        house_method_count = len(df[df['시험표준'].str.contains('House Method', na=False)])
                        st.metric("House Method", f"{house_method_count}개")
                    
                    with col4:
                        total_data_count = df['데이터 건수'].sum()
                        st.metric("총 데이터 건수", f"{total_data_count}건")
                    
                    # CSV 다운로드
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 CSV 다운로드",
                        data=csv,
                        file_name=f"시험표준정보_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                else:
                    st.warning("검색 조건에 맞는 시험표준 정보가 없습니다.")
                    
            except Exception as e:
                st.error(f"시험표준 정보 조회 중 오류가 발생했습니다: {e}")
    
    def get_test_standard_info(self):
        """데이터베이스에서 시험표준 정보 추출"""
        try:
            # 데이터베이스에서 모든 파일 조회
            files = self.db_manager.get_all_files()
            
            standard_info_dict = {}
            
            for file_data in files:
                test_results = file_data.get('test_results', [])
                
                for result in test_results:
                    if not isinstance(result, dict):
                        continue
                    
                    # 시험표준 정보 추출
                    test_item = result.get('test_item', '')
                    test_unit = result.get('test_unit', '')
                    test_standard = result.get('test_standard', '')
                    standard_text = result.get('standard_text', '')
                    
                    # House Method가 아닌 경우만 포함
                    if test_standard and 'House Method' not in str(test_standard):
                        # 고유 키 생성
                        key = f"{test_item}|{test_unit}|{test_standard}|{standard_text}"
                        
                        if key not in standard_info_dict:
                            standard_info_dict[key] = {
                                '시험항목': test_item,
                                '시험단위': test_unit,
                                '시험표준': test_standard,
                                '기준 텍스트': standard_text,
                                '데이터 건수': 0
                            }
                        
                        standard_info_dict[key]['데이터 건수'] += 1
            
            # 리스트로 변환하여 반환
            return list(standard_info_dict.values())
            
        except Exception as e:
            print(f"시험표준 정보 추출 오류: {e}")
            return []
    
    def render_integrated_analysis_page(self):
        """통합 분석 페이지 렌더링"""
        self.render_page_header("통합 분석", "누적 데이터를 기반으로 품질 동향을 파악합니다")
        
        try:
            # 기간 설정 컨트롤러
            start_date, end_date = self.period_controller.render_period_selector()
            
            # 통합 분석 수행 (안전한 처리)
            try:
                analysis_data = self.integrated_analysis_engine.analyze_period(start_date, end_date)
                
                # 데이터 타입 검증
                if not isinstance(analysis_data, dict):
                    st.error("통합 분석 데이터 형식이 올바르지 않습니다.")
                    st.error(f"받은 데이터 타입: {type(analysis_data)}")
                    return
                    
            except Exception as analysis_error:
                st.error("통합 분석 중 오류가 발생했습니다:")
                st.error(str(analysis_error))
                st.error("개발자에게 문의하세요.")
                return
            
            # 필수 키들의 기본값 설정
            analysis_data.setdefault('total_files', 0)
            analysis_data.setdefault('total_tests', 0)
            analysis_data.setdefault('total_violations', 0)
            analysis_data.setdefault('violation_rate', 0)
            analysis_data.setdefault('top_clients', [])
            analysis_data.setdefault('top_violation_items', [])
            analysis_data.setdefault('conforming_items', {})
            analysis_data.setdefault('non_conforming_items', {})
            analysis_data.setdefault('monthly_stats', {})
            analysis_data.setdefault('summary_text', '데이터가 없습니다.')
            
            if analysis_data['total_files'] == 0:
                st.info(f"선택된 기간({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})에 분석된 데이터가 없습니다.")
                st.markdown("### 📁 파일 업로드")
                st.info("통합 분석을 위해서는 먼저 파일을 업로드하고 분석해야 합니다.")
                if st.button("📁 파일 업로드하러 가기", use_container_width=True):
                    st.session_state.current_page = 'reports'
                    st.rerun()
                return
            
            # 통합 분석 KPI 카드
            self.render_integrated_kpi_cards(analysis_data)
            
            # 메인 콘텐츠 영역
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # 부적합 항목 분포 차트
                st.markdown("#### 📊 부적합 항목 분포")
                
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    st.markdown("**❌ 부적합 항목별 분포**")
                    non_conforming_fig = self.integrated_analysis_engine.create_non_conforming_chart(
                        analysis_data['non_conforming_items']
                    )
                    st.plotly_chart(non_conforming_fig, use_container_width=True, key="integrated_non_conforming")
                
                with chart_col2:
                    st.markdown("**🧪 실험별 오염수준 분포**")
                    contamination_fig = self.integrated_analysis_engine.create_contamination_level_chart(
                        analysis_data.get('files', [])
                    )
                    st.plotly_chart(contamination_fig, use_container_width=True, key="contamination_levels")
                
                # 시험/시료별 추이 차트
                files_data = analysis_data.get('files', [])
                if files_data:
                    try:
                        st.markdown("#### 📈 시험/시료별 추이")
                        file_trend_fig = self.integrated_analysis_engine.create_file_trend_chart(files_data)
                        st.plotly_chart(file_trend_fig, use_container_width=True, key="file_trend")
                    except Exception as chart_error:
                        st.error(f"시험/시료별 추이 차트 생성 오류: {str(chart_error)}")
                        st.info("차트를 표시할 수 없습니다.")
            
            with col2:
                # 통합 분석 리포트 요약
                st.markdown("#### 📋 통합 분석 리포트 요약")
                
                st.markdown(f"""
                <div style="background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                    <p style="margin: 0; line-height: 1.6; color: #0c4a6e;">{analysis_data['summary_text']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 주요 의뢰 기관
                top_clients = analysis_data.get('top_clients', [])
                if top_clients and isinstance(top_clients, list):
                    st.markdown("#### 🏢 주요 의뢰 기관")
                    for i, client_data in enumerate(top_clients, 1):
                        if isinstance(client_data, (list, tuple)) and len(client_data) >= 2:
                            client, count = client_data[0], client_data[1]
                            st.markdown(f"{i}. **{client}** - {count}건")
                
                # 상위 부적합 항목
                top_violation_items = analysis_data.get('top_violation_items', [])
                if top_violation_items and isinstance(top_violation_items, list):
                    st.markdown("#### 🔍 상위 부적합 항목")
                    
                    violation_df_data = []
                    total_violations = analysis_data.get('total_violations', 0)
                    
                    for violation_data in top_violation_items:
                        if isinstance(violation_data, (list, tuple)) and len(violation_data) >= 2:
                            item, count = violation_data[0], violation_data[1]
                            if total_violations > 0:
                                ratio = (count / total_violations * 100)
                            else:
                                ratio = 0
                            violation_df_data.append({
                                '시험 항목': item,
                                '부적합 건수': count,
                                '비율': f"{ratio:.1f}%"
                            })
                    
                    if violation_df_data:
                        violation_df = pd.DataFrame(violation_df_data)
                        st.dataframe(violation_df, use_container_width=True, height=200)
                
                # 통합 리포트 미리보기 버튼
                st.markdown("---")
                if st.button("📊 통합리포트 미리보기", use_container_width=True, type="primary"):
                    st.session_state.show_integrated_modal = True
                    st.rerun()
                
                # 모달 표시
                if st.session_state.get('show_integrated_modal', False):
                    self.show_integrated_report_options_modal(analysis_data, start_date, end_date)
            
        except Exception as e:
            st.error(f"통합 분석 중 오류가 발생했습니다: {e}")
            st.info("개발자에게 문의하세요.")
    
    def render_integrated_kpi_cards(self, analysis_data: Dict[str, Any]):
        """통합 분석 KPI 카드 렌더링"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">총 시험 수 (파일 기준)</div>
                    <div class="kpi-icon">📋</div>
                </div>
                <div class="kpi-value primary">{analysis_data['total_files']} <span style="font-size: 16px;">건</span></div>
                <div class="kpi-subtitle">분석된 파일 수</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            value_class = "error" if analysis_data['violation_rate'] > 20 else "warning" if analysis_data['violation_rate'] > 10 else "success"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">평균 부적합률</div>
                    <div class="kpi-icon">⚠️</div>
                </div>
                <div class="kpi-value {value_class}">{analysis_data['violation_rate']} <span style="font-size: 16px;">%</span></div>
                <div class="kpi-subtitle">{analysis_data['total_violations']}/{analysis_data['total_tests']} 항목</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            top_client = "해당 없음"
            top_clients = analysis_data.get('top_clients', [])
            if top_clients and isinstance(top_clients, list) and len(top_clients) > 0:
                first_client = top_clients[0]
                if isinstance(first_client, (list, tuple)) and len(first_client) >= 1:
                    top_client = str(first_client[0])
                    if len(top_client) > 15:
                        top_client = top_client[:12] + "..."
            
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">주요 의뢰 기관</div>
                    <div class="kpi-icon">🏢</div>
                </div>
                <div class="kpi-value primary" style="font-size: 20px; line-height: 1.2;">{top_client}</div>
                <div class="kpi-subtitle">최다 의뢰 기관</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            top_item = "해당 없음"
            top_violation_items = analysis_data.get('top_violation_items', [])
            if top_violation_items and isinstance(top_violation_items, list) and len(top_violation_items) > 0:
                first_item = top_violation_items[0]
                if isinstance(first_item, (list, tuple)) and len(first_item) >= 1:
                    top_item = str(first_item[0])
                    if len(top_item) > 15:
                        top_item = top_item[:12] + "..."
            
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">최다 부적합 항목</div>
                    <div class="kpi-icon">🔬</div>
                </div>
                <div class="kpi-value primary" style="font-size: 20px; line-height: 1.2;">{top_item}</div>
                <div class="kpi-subtitle">가장 빈번한 항목</div>
            </div>
            """, unsafe_allow_html=True)
    
    def show_integrated_report_options_modal(self, analysis_data: Dict[str, Any], start_date: datetime, end_date: datetime):
        """통합 리포트 옵션 모달 (요약/미리보기/다운로드)"""
        # 모달 상태 초기화
        if 'show_integrated_modal' not in st.session_state:
            st.session_state.show_integrated_modal = True
        
        if st.session_state.show_integrated_modal:
            # 모달 다이얼로그
            with st.container():
                st.markdown("### 📊 통합리포트 미리보기")
                st.markdown("원하는 옵션을 선택하세요:")
                
                # 3개 옵션 버튼
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📋 요약", use_container_width=True, key="integrated_summary"):
                        st.session_state.integrated_modal_tab = "summary"
                        st.rerun()
                
                with col2:
                    if st.button("👁️ 미리보기", use_container_width=True, key="integrated_preview"):
                        st.session_state.integrated_modal_tab = "preview"
                        st.rerun()
                
                with col3:
                    if st.button("📥 다운로드", use_container_width=True, key="integrated_download"):
                        st.session_state.integrated_modal_tab = "download"
                        st.rerun()
                
                st.markdown("---")
                
                # 선택된 탭에 따른 내용 표시
                selected_tab = st.session_state.get('integrated_modal_tab', None)
                
                if selected_tab == "summary":
                    self.render_integrated_summary(analysis_data)
                elif selected_tab == "preview":
                    self.render_integrated_preview(analysis_data, start_date, end_date)
                elif selected_tab == "download":
                    self.render_integrated_download(analysis_data, start_date, end_date)
                else:
                    # 기본 안내 메시지
                    st.info("위의 버튼 중 하나를 선택하세요.")
                
                # 닫기 버튼
                if st.button("❌ 닫기", use_container_width=True, key="close_integrated_modal"):
                    st.session_state.show_integrated_modal = False
                    if 'integrated_modal_tab' in st.session_state:
                        del st.session_state.integrated_modal_tab
                    st.rerun()
    
    def render_integrated_summary(self, analysis_data: Dict[str, Any]):
        """통합 분석 요약 렌더링"""
        
        # KPI 메트릭
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("총 파일 수", f"{analysis_data.get('total_files', 0)}건")
        with col2:
            st.metric("총 시험 수", f"{analysis_data.get('total_tests', 0)}건")
        with col3:
            st.metric("부적합 수", f"{analysis_data.get('total_violations', 0)}건")
        with col4:
            st.metric("부적합률", f"{analysis_data.get('violation_rate', 0):.1f}%")
        
        # 요약 텍스트
        st.markdown("#### 📝 분석 요약")
        summary_text = analysis_data.get('summary_text', '분석 요약 정보가 없습니다.')
        st.info(summary_text)
        
        # 주요 부적합 항목
        top_violation_items = analysis_data.get('top_violation_items', [])
        if top_violation_items:
            st.markdown("#### 🔍 주요 부적합 항목")
            for i, violation_data in enumerate(top_violation_items[:5], 1):
                if isinstance(violation_data, (list, tuple)) and len(violation_data) >= 2:
                    item, count = violation_data[0], violation_data[1]
                    st.write(f"{i}. **{item}**: {count}건")
    
    def render_integrated_preview(self, analysis_data: Dict[str, Any], start_date: datetime, end_date: datetime):
        """통합 분석 미리보기 렌더링"""
        
        # 리포트 HTML 생성 (안전한 처리)
        try:
            report_html = self.integrated_analysis_engine.generate_integrated_report_html(
                analysis_data, start_date, end_date
            )
            if not report_html or len(report_html) < 100:
                st.error("HTML 보고서 생성에 실패했습니다.")
                return
                
            # 전체화면 HTML 미리보기 (높이 증가)
            st.components.v1.html(report_html, height=800, scrolling=True)
            
        except Exception as html_error:
            st.error(f"HTML 보고서 생성 중 오류: {str(html_error)}")
            st.error("개발자에게 문의하세요.")
    
    def render_integrated_download(self, analysis_data: Dict[str, Any], start_date: datetime, end_date: datetime):
        """통합 분석 다운로드 렌더링"""
        st.markdown("### 📥 그래프 포함 HTML 다운로드")
        st.info("통합 분석 대시보드와 동일한 그래프가 포함된 완전한 HTML 리포트를 다운로드합니다.")
        
        try:
            with st.spinner("그래프가 포함된 HTML 리포트를 생성하고 있습니다..."):
                # 부적합 항목 차트만 생성 (적합 항목 제외)
                non_conforming_fig = self.integrated_analysis_engine.create_non_conforming_chart(
                    analysis_data.get('non_conforming_items', {})
                )
                
                # 실험별 오염수준 분포 차트
                contamination_fig = self.integrated_analysis_engine.create_contamination_level_chart(
                    analysis_data.get('files', [])
                )
                
                # 시험/시료별 추이 차트
                files_data = analysis_data.get('files', [])
                file_trend_fig = None
                if files_data:
                    file_trend_fig = self.integrated_analysis_engine.create_file_trend_chart(files_data)
                
                # 차트를 HTML로 변환
                non_conforming_html = non_conforming_fig.to_html(include_plotlyjs='inline', div_id="non_conforming_chart")
                contamination_html = contamination_fig.to_html(include_plotlyjs='inline', div_id="contamination_chart")
                file_trend_html = ""
                if file_trend_fig:
                    file_trend_html = file_trend_fig.to_html(include_plotlyjs='inline', div_id="file_trend_chart")
                
                # 완전한 HTML 리포트 생성 (적합 항목 제외)
                html_content = self.generate_integrated_html_report_no_conforming(
                    analysis_data, start_date, end_date,
                    non_conforming_html, contamination_html, file_trend_html
                )
                
                # 파일명 생성
                filename = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_통합분석리포트_그래프포함.html"
                
                # Streamlit 다운로드 버튼으로 제공
                st.download_button(
                    label="📊 그래프 포함 HTML 다운로드",
                    data=html_content,
                    file_name=filename,
                    mime="text/html",
                    use_container_width=True,
                    type="primary"
                )
                
                st.success("✅ 그래프가 포함된 HTML 리포트가 준비되었습니다!")
                st.info("위의 다운로드 버튼을 클릭하여 파일을 저장하세요.")
                
        except Exception as e:
            st.error(f"그래프 포함 HTML 생성 중 오류: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
    
    def save_integrated_report(self, analysis_data: Dict[str, Any], start_date: datetime, end_date: datetime):
        """통합 리포트를 파일로 저장"""
        try:
            # 통합 리포트 폴더 사용
            reports_folder = self.get_folder_path('integrated_reports')
            
            # 폴더 생성 확인
            if not reports_folder.exists():
                st.error("리포트 폴더 생성에 실패했습니다.")
                return
            
            # 리포트 HTML 생성
            try:
                report_html = self.integrated_analysis_engine.generate_integrated_report_html(
                    analysis_data, start_date, end_date
                )
                if not report_html or len(report_html) < 100:
                    st.error("HTML 보고서 생성에 실패했습니다.")
                    return
            except Exception as html_error:
                st.error(f"HTML 보고서 생성 중 오류: {str(html_error)}")
                return
            
            # 파일명 생성: 날짜범위_통합분석리포트.html
            filename = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_통합분석리포트.html"
            file_path = reports_folder / filename
            
            # 파일 저장
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_html)
                
                # 파일 저장 확인
                if file_path.exists() and file_path.stat().st_size > 0:
                    st.success(f"✅ 통합 리포트가 저장되었습니다!")
                    st.info(f"📁 저장 위치: {file_path.absolute()}")
                    st.info(f"📄 파일 크기: {file_path.stat().st_size:,} bytes")
                    
                    # 저장 폴더 열기 버튼
                    if st.button("📂 저장 폴더 열기", key="open_integrated_reports_folder"):
                        self.open_folder(str(reports_folder.absolute()))
                else:
                    st.error("파일이 저장되지 않았습니다.")
                    
            except PermissionError:
                st.error("파일 저장 권한이 없습니다. 관리자 권한으로 실행하거나 다른 위치를 선택하세요.")
            except Exception as write_error:
                st.error(f"파일 쓰기 오류: {write_error}")
                
        except Exception as e:
            st.error(f"리포트 저장 중 오류가 발생했습니다: {e}")
            import traceback
            st.error(traceback.format_exc())
    
    def generate_complete_html_report(self, analysis_data: Dict[str, Any], 
                                    start_date: datetime, end_date: datetime,
                                    conforming_html: str, non_conforming_html: str, 
                                    monthly_html: str) -> str:
        """완전한 HTML 리포트 생성 (그래프 포함)"""
        period_str = f"{start_date.strftime('%Y년 %m월 %d일')} ~ {end_date.strftime('%Y년 %m월 %d일')}"
        
        # 상위 부적합 항목 테이블 생성
        violation_table_rows = ""
        top_violation_items = analysis_data.get("top_violation_items", [])
        total_violations = analysis_data.get("total_violations", 0)
        
        if top_violation_items and isinstance(top_violation_items, list):
            for i, item_data in enumerate(top_violation_items[:10], 1):
                if isinstance(item_data, (list, tuple)) and len(item_data) >= 2:
                    item, count = str(item_data[0]), int(item_data[1])
                    percentage = (count/total_violations*100) if total_violations > 0 else 0
                    violation_table_rows += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{item}</td>
                        <td>{count}건</td>
                        <td>{percentage:.1f}%</td>
                    </tr>
                    """
        
        if not violation_table_rows:
            violation_table_rows = "<tr><td colspan='4'>부적합 항목이 없습니다.</td></tr>"
        
        # 주요 의뢰 기관 테이블 생성
        client_table_rows = ""
        top_clients = analysis_data.get("top_clients", [])
        
        if top_clients and isinstance(top_clients, list):
            for i, client_data in enumerate(top_clients[:5], 1):
                if isinstance(client_data, (list, tuple)) and len(client_data) >= 2:
                    client, count = str(client_data[0]), int(client_data[1])
                    client_table_rows += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{client}</td>
                        <td>{count}건</td>
                    </tr>
                    """
        
        if not client_table_rows:
            client_table_rows = "<tr><td colspan='3'>의뢰 기관 데이터가 없습니다.</td></tr>"
        
        # 월별 차트 섹션 (데이터가 있는 경우만)
        monthly_section = ""
        if monthly_html:
            monthly_section = f"""
            <div class="chart-section">
                <h3>📈 월별 트렌드</h3>
                <div class="chart-container">
                    {monthly_html}
                </div>
            </div>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Aqua-Analytics 통합 분석 보고서 (그래프 포함)</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8fafc;
                    color: #334155;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 700;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 1.2em;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 30px;
                }}
                .kpi-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .kpi-card {{
                    background: #f1f5f9;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                }}
                .kpi-value {{
                    font-size: 2.5em;
                    font-weight: 700;
                    color: #1e293b;
                    margin-bottom: 5px;
                }}
                .kpi-label {{
                    font-size: 0.9em;
                    color: #64748b;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .chart-section {{
                    margin: 30px 0;
                    padding: 20px;
                    background: #fafafa;
                    border-radius: 8px;
                    border: 1px solid #e5e7eb;
                }}
                .chart-section h3 {{
                    margin-top: 0;
                    color: #374151;
                    border-bottom: 2px solid #3b82f6;
                    padding-bottom: 10px;
                }}
                .chart-container {{
                    margin: 20px 0;
                }}
                .charts-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin: 20px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #e5e7eb;
                }}
                th {{
                    background: #f8fafc;
                    font-weight: 600;
                    color: #374151;
                }}
                tr:hover {{
                    background: #f9fafb;
                }}
                .summary-box {{
                    background: #eff6ff;
                    border: 1px solid #bfdbfe;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    background: #f8fafc;
                    color: #64748b;
                    font-size: 0.9em;
                }}
                @media print {{
                    body {{ background: white; }}
                    .container {{ box-shadow: none; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💧 Aqua-Analytics</h1>
                    <p>통합 분석 보고서 (그래프 포함)</p>
                    <p><strong>분석 기간:</strong> {period_str}</p>
                </div>
                
                <div class="content">
                    <!-- KPI 카드 -->
                    <div class="kpi-grid">
                        <div class="kpi-card">
                            <div class="kpi-value">{analysis_data.get('total_files', 0)}</div>
                            <div class="kpi-label">총 분석 파일</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value">{analysis_data.get('total_tests', 0)}</div>
                            <div class="kpi-label">총 시험 항목</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value">{analysis_data.get('total_violations', 0)}</div>
                            <div class="kpi-label">부적합 항목</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value">{analysis_data.get('violation_rate', 0):.1f}%</div>
                            <div class="kpi-label">부적합률</div>
                        </div>
                    </div>
                    
                    <!-- 분석 요약 -->
                    <div class="summary-box">
                        <h3>📋 분석 요약</h3>
                        <p>{analysis_data.get('summary_text', '분석 요약이 없습니다.')}</p>
                    </div>
                    
                    <!-- 차트 섹션 -->
                    <div class="charts-grid">
                        <div class="chart-section">
                            <h3>✅ 적합 항목 분포</h3>
                            <div class="chart-container">
                                {conforming_html}
                            </div>
                        </div>
                        <div class="chart-section">
                            <h3>❌ 부적합 항목 분포</h3>
                            <div class="chart-container">
                                {non_conforming_html}
                            </div>
                        </div>
                    </div>
                    
                    {monthly_section}
                    
                    <!-- 상위 부적합 항목 테이블 -->
                    <div class="chart-section">
                        <h3>🔍 상위 부적합 항목</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>순위</th>
                                    <th>시험 항목</th>
                                    <th>부적합 건수</th>
                                    <th>비율</th>
                                </tr>
                            </thead>
                            <tbody>
                                {violation_table_rows}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- 주요 의뢰 기관 테이블 -->
                    <div class="chart-section">
                        <h3>🏢 주요 의뢰 기관</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>순위</th>
                                    <th>의뢰 기관</th>
                                    <th>시험 건수</th>
                                </tr>
                            </thead>
                            <tbody>
                                {client_table_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="footer">
                    <p>© 2024 Aqua-Analytics | 생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def generate_integrated_html_report_no_conforming(self, analysis_data: Dict[str, Any], 
                                                    start_date: datetime, end_date: datetime,
                                                    non_conforming_html: str, contamination_html: str, 
                                                    file_trend_html: str) -> str:
        """적합 항목을 제외한 통합 분석 HTML 리포트 생성"""
        period_str = f"{start_date.strftime('%Y년 %m월 %d일')} ~ {end_date.strftime('%Y년 %m월 %d일')}"
        
        # 상위 부적합 항목 테이블 생성
        violation_table_rows = ""
        top_violation_items = analysis_data.get("top_violation_items", [])
        total_violations = analysis_data.get("total_violations", 0)
        
        if top_violation_items and isinstance(top_violation_items, list):
            for i, item_data in enumerate(top_violation_items[:10], 1):
                if isinstance(item_data, (list, tuple)) and len(item_data) >= 2:
                    item, count = str(item_data[0]), int(item_data[1])
                    percentage = (count/total_violations*100) if total_violations > 0 else 0
                    violation_table_rows += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{item}</td>
                        <td>{count}건</td>
                        <td>{percentage:.1f}%</td>
                    </tr>
                    """
        
        if not violation_table_rows:
            violation_table_rows = "<tr><td colspan='4'>부적합 항목이 없습니다.</td></tr>"
        
        # 주요 의뢰 기관 테이블 생성
        client_table_rows = ""
        top_clients = analysis_data.get("top_clients", [])
        
        if top_clients and isinstance(top_clients, list):
            for i, client_data in enumerate(top_clients[:5], 1):
                if isinstance(client_data, (list, tuple)) and len(client_data) >= 2:
                    client, count = str(client_data[0]), int(client_data[1])
                    client_table_rows += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{client}</td>
                        <td>{count}건</td>
                    </tr>
                    """
        
        if not client_table_rows:
            client_table_rows = "<tr><td colspan='3'>의뢰 기관 데이터가 없습니다.</td></tr>"
        
        # 시험/시료별 추이 차트 섹션 (데이터가 있는 경우만)
        file_trend_section = ""
        if file_trend_html:
            file_trend_section = f"""
            <div class="chart-section">
                <h3>📈 시험/시료별 추이</h3>
                <div class="chart-container">
                    {file_trend_html}
                </div>
            </div>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Aqua-Analytics 통합 분석 보고서 (부적합 항목 중심)</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8fafc;
                    color: #334155;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 700;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 1.2em;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 30px;
                }}
                .kpi-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .kpi-card {{
                    background: #f1f5f9;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                }}
                .kpi-value {{
                    font-size: 2.5em;
                    font-weight: 700;
                    color: #1e293b;
                    margin-bottom: 5px;
                }}
                .kpi-label {{
                    font-size: 0.9em;
                    color: #64748b;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .chart-section {{
                    margin: 30px 0;
                    padding: 20px;
                    background: #fafafa;
                    border-radius: 8px;
                    border: 1px solid #e5e7eb;
                }}
                .chart-section h3 {{
                    margin-top: 0;
                    color: #374151;
                    border-bottom: 2px solid #3b82f6;
                    padding-bottom: 10px;
                }}
                .chart-container {{
                    margin: 20px 0;
                }}
                .charts-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin: 20px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #e5e7eb;
                }}
                th {{
                    background: #f8fafc;
                    font-weight: 600;
                    color: #374151;
                }}
                tr:hover {{
                    background: #f9fafb;
                }}
                .summary-box {{
                    background: #eff6ff;
                    border: 1px solid #bfdbfe;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    background: #f8fafc;
                    color: #64748b;
                    font-size: 0.9em;
                }}
                @media print {{
                    body {{ background: white; }}
                    .container {{ box-shadow: none; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💧 Aqua-Analytics</h1>
                    <p>통합 분석 보고서 (부적합 항목 중심)</p>
                    <p><strong>분석 기간:</strong> {period_str}</p>
                </div>
                
                <div class="content">
                    <!-- KPI 카드 -->
                    <div class="kpi-grid">
                        <div class="kpi-card">
                            <div class="kpi-value">{analysis_data.get('total_files', 0)}</div>
                            <div class="kpi-label">총 분석 파일</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value">{analysis_data.get('total_tests', 0)}</div>
                            <div class="kpi-label">총 시험 항목</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value">{analysis_data.get('total_violations', 0)}</div>
                            <div class="kpi-label">부적합 항목</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value">{analysis_data.get('violation_rate', 0):.1f}%</div>
                            <div class="kpi-label">부적합률</div>
                        </div>
                    </div>
                    
                    <!-- 분석 요약 -->
                    <div class="summary-box">
                        <h3>📋 분석 요약</h3>
                        <p>{analysis_data.get('summary_text', '분석 요약이 없습니다.')}</p>
                    </div>
                    
                    <!-- 부적합 항목 중심 차트 섹션 -->
                    <div class="charts-grid">
                        <div class="chart-section">
                            <h3>❌ 부적합 항목 분포</h3>
                            <div class="chart-container">
                                {non_conforming_html}
                            </div>
                        </div>
                        <div class="chart-section">
                            <h3>🧪 실험별 오염수준 분포</h3>
                            <div class="chart-container">
                                {contamination_html}
                            </div>
                        </div>
                    </div>
                    
                    {file_trend_section}
                    
                    <!-- 상위 부적합 항목 테이블 -->
                    <div class="chart-section">
                        <h3>🔍 상위 부적합 항목</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>순위</th>
                                    <th>시험 항목</th>
                                    <th>부적합 건수</th>
                                    <th>비율</th>
                                </tr>
                            </thead>
                            <tbody>
                                {violation_table_rows}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- 주요 의뢰 기관 테이블 -->
                    <div class="chart-section">
                        <h3>🏢 주요 의뢰 기관</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>순위</th>
                                    <th>의뢰 기관</th>
                                    <th>시험 건수</th>
                                </tr>
                            </thead>
                            <tbody>
                                {client_table_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="footer">
                    <p>© 2024 Aqua-Analytics | 생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content

    def open_folder(self, folder_path: str):
        """폴더 열기"""
        import subprocess
        import platform
        
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.run(["explorer", folder_path])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            elif system == "Linux":
                subprocess.run(["xdg-open", folder_path])
            else:
                st.warning(f"지원되지 않는 운영체제입니다: {system}")
                
        except Exception as e:
            st.error(f"폴더 열기 실패: {e}")
            st.info(f"수동으로 다음 경로를 확인해주세요: {folder_path}")
    
    def open_storage_folder(self, folder_type='base'):
        """저장 폴더 열기 (실시간 정보 포함)"""
        try:
            folder_path = self.get_folder_path(folder_type)
            
            # 폴더 내용 실시간 확인
            if folder_path.exists():
                # 실시간으로 파일 목록 조회
                files = list(folder_path.glob('*'))
                file_count = len([f for f in files if f.is_file()])
                dir_count = len([f for f in files if f.is_dir()])
                
                # 폴더 크기 계산
                try:
                    total_size = sum(f.stat().st_size for f in files if f.is_file())
                    if total_size > 1024 * 1024:  # MB
                        size_str = f"{total_size / (1024 * 1024):.1f} MB"
                    elif total_size > 1024:  # KB
                        size_str = f"{total_size / 1024:.1f} KB"
                    else:
                        size_str = f"{total_size} B"
                except:
                    size_str = "계산 불가"
                
                folder_names = {
                    'base': '전체 저장 폴더',
                    'uploads': '업로드 파일 폴더',
                    'processed': '처리된 파일 폴더',
                    'reports': '보고서 폴더',
                    'dashboard_reports': '대시보드 보고서 폴더',
                    'integrated_reports': '통합 분석 보고서 폴더'
                }
                
                # 폴더 열기
                self.open_folder(str(folder_path.absolute()))
                
                # 실시간 폴더 정보 반환
                return {
                    'name': folder_names.get(folder_type, '폴더'),
                    'path': str(folder_path.absolute()),
                    'files': file_count,
                    'dirs': dir_count,
                    'size': size_str,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                # 폴더가 없는 경우 생성 시도
                try:
                    folder_path.mkdir(parents=True, exist_ok=True)
                    return {
                        'name': folder_names.get(folder_type, '폴더'),
                        'path': str(folder_path.absolute()),
                        'files': 0,
                        'dirs': 0,
                        'size': '0 B',
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                except Exception as create_error:
                    print(f"폴더 생성 실패: {create_error}")
                    return None
                    
        except Exception as e:
            print(f"폴더 열기 중 오류: {e}")
            return None
    
    def show_folder_structure_info(self):
        """폴더 구조 정보 표시 (실시간 업데이트)"""
        st.markdown("### 📁 저장 폴더 구조")
        
        # 새로고침 버튼
        col_title, col_refresh = st.columns([3, 1])
        with col_title:
            st.markdown("현재 저장된 파일 현황을 확인할 수 있습니다.")
        with col_refresh:
            if st.button("🔄 새로고침", key="refresh_folder_info"):
                st.rerun()
        
        # 실시간 폴더 정보 계산
        folder_info = self.get_realtime_folder_info()
        
        # 테이블로 표시
        if folder_info:
            df_folders = pd.DataFrame(folder_info)
            
            # 컬럼 설정
            st.dataframe(
                df_folders,
                use_container_width=True,
                column_config={
                    "name": st.column_config.TextColumn("폴더명", width="medium"),
                    "files": st.column_config.NumberColumn("파일 수", width="small"),
                    "dirs": st.column_config.NumberColumn("폴더 수", width="small"),
                    "size": st.column_config.TextColumn("크기", width="small"),
                    "path": st.column_config.TextColumn("경로", width="large")
                }
            )
            
            # 요약 정보
            total_files = sum(info['files'] for info in folder_info)
            total_dirs = sum(info['dirs'] for info in folder_info)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 파일 수", f"{total_files}개")
            with col2:
                st.metric("총 폴더 수", f"{total_dirs}개")
            with col3:
                # 데이터베이스 파일 수
                db_files_count = len(self.db_manager.get_all_files())
                st.metric("DB 저장 파일", f"{db_files_count}개")
        
        # 폴더별 바로가기 버튼
        st.markdown("#### 📂 폴더 바로가기")
        
        folder_buttons = [
            {'key': 'base', 'label': '전체 폴더', 'icon': '📁'},
            {'key': 'uploads', 'label': '업로드 파일', 'icon': '📤'},
            {'key': 'processed', 'label': '처리된 파일', 'icon': '⚙️'},
            {'key': 'dashboard_reports', 'label': '대시보드 리포트', 'icon': '📊'},
            {'key': 'integrated_reports', 'label': '통합 분석 리포트', 'icon': '📈'}
        ]
        
        cols = st.columns(len(folder_buttons))
        for i, folder in enumerate(folder_buttons):
            with cols[i]:
                if st.button(f"{folder['icon']}\n{folder['label']}", 
                           key=f"open_{folder['key']}_folder_tab3", 
                           use_container_width=True):
                    try:
                        folder_info = self.open_storage_folder(folder['key'])
                        if folder_info:
                            st.session_state.folder_notification = {
                                'message': f"📁 {folder_info['name']} 열기 완료!",
                                'details': f"📄 파일 {folder_info['files']}개, 📁 폴더 {folder_info['dirs']}개",
                                'type': 'success'
                            }
                            st.rerun()
                    except Exception as e:
                        st.session_state.folder_notification = {
                            'message': f"폴더 열기 실패: {e}",
                            'type': 'error'
                        }
                        st.rerun()
    
    def get_realtime_folder_info(self):
        """실시간 폴더 정보 조회"""
        folder_info = []
        
        folder_descriptions = {
            'base': '전체 데이터 폴더',
            'uploads': '업로드된 원본 파일',
            'processed': '처리 완료된 파일',
            'dashboard_reports': '대시보드 보고서',
            'integrated_reports': '통합 분석 보고서',
            'database': '데이터베이스 파일'
        }
        
        for folder_type, folder_path in self.folders.items():
            try:
                if folder_path.exists():
                    # 실시간으로 파일 목록 조회
                    files = list(folder_path.glob('*'))
                    file_count = len([f for f in files if f.is_file()])
                    dir_count = len([f for f in files if f.is_dir()])
                    
                    # 폴더 크기 계산 (선택적)
                    try:
                        total_size = sum(f.stat().st_size for f in files if f.is_file())
                        if total_size > 1024 * 1024:  # MB
                            size_str = f"{total_size / (1024 * 1024):.1f} MB"
                        elif total_size > 1024:  # KB
                            size_str = f"{total_size / 1024:.1f} KB"
                        else:
                            size_str = f"{total_size} B"
                    except:
                        size_str = "계산 불가"
                    
                    folder_info.append({
                        'name': folder_descriptions.get(folder_type, folder_type),
                        'files': file_count,
                        'dirs': dir_count,
                        'size': size_str,
                        'path': str(folder_path.absolute())
                    })
                else:
                    # 폴더가 존재하지 않는 경우
                    folder_info.append({
                        'name': folder_descriptions.get(folder_type, folder_type),
                        'files': 0,
                        'dirs': 0,
                        'size': '폴더 없음',
                        'path': str(folder_path.absolute())
                    })
            except Exception as e:
                # 오류 발생 시 기본값
                folder_info.append({
                    'name': folder_descriptions.get(folder_type, folder_type),
                    'files': 0,
                    'dirs': 0,
                    'size': f'오류: {str(e)[:20]}...',
                    'path': str(folder_path.absolute())
                })
        
        return folder_info
    
    def save_dashboard_to_database(self):
        """현재 대시보드를 데이터베이스에 반영"""
        if not st.session_state.active_file:
            st.error("활성화된 파일이 없습니다.")
            return
        
        try:
            file_data = st.session_state.uploaded_files[st.session_state.active_file]
            test_results = file_data['test_results']
            client = file_data.get('client', '미지정')
            upload_time = file_data.get('upload_time', datetime.now())
            
            # 이미 데이터베이스에 반영된 파일인지 확인
            file_id = file_data.get('file_id')
            
            if not file_id:
                # 새로 데이터베이스에 반영
                file_id = self.db_manager.save_analysis_result(
                    file_name=st.session_state.active_file,
                    test_results=test_results,
                    client=client,
                    upload_time=upload_time
                )
                
                # 세션 상태에 file_id 저장
                st.session_state.uploaded_files[st.session_state.active_file]['file_id'] = file_id
                
                st.success(f"✅ 데이터베이스에 새로 반영되었습니다! (ID: {file_id[:8]}...)")
            else:
                st.info(f"✅ 이미 데이터베이스에 반영된 파일입니다. (ID: {file_id[:8]}...)")
            
            # HTML 보고서 생성 및 저장
            dashboard_reports_folder = self.get_folder_path('dashboard_reports')
            
            # 폴더 생성 확인
            if not dashboard_reports_folder.exists():
                st.error("보고서 폴더 생성에 실패했습니다.")
                return
            
            # 파일명 생성: 날짜+파일명+분석결과.html
            date_str = upload_time.strftime('%Y%m%d')
            file_stem = Path(st.session_state.active_file).stem
            filename = f"{date_str}_{file_stem}_분석결과.html"
            file_path = dashboard_reports_folder / filename
            
            # 대시보드 HTML 생성
            try:
                dashboard_html = self.generate_dashboard_html(test_results, st.session_state.active_file, client)
                if not dashboard_html or len(dashboard_html) < 100:
                    st.error("HTML 보고서 생성에 실패했습니다.")
                    return
            except Exception as html_error:
                st.error(f"HTML 보고서 생성 중 오류: {str(html_error)}")
                st.error("개발자에게 문의하세요.")
                return
            
            # 파일 저장
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(dashboard_html)
                
                # 파일 저장 확인
                if file_path.exists() and file_path.stat().st_size > 0:
                    st.success(f"📄 대시보드 보고서가 저장되었습니다: {filename}")
                    st.info(f"📁 저장 위치: {file_path.absolute()}")
                    st.info(f"📄 파일 크기: {file_path.stat().st_size:,} bytes")
                    
                    # 저장 폴더 열기 버튼
                    if st.button("📂 보고서 폴더 열기", key="open_dashboard_reports_folder"):
                        self.open_folder(str(dashboard_reports_folder.absolute()))
                else:
                    st.error("파일이 저장되지 않았습니다.")
                    
            except PermissionError:
                st.error("파일 저장 권한이 없습니다. 관리자 권한으로 실행하거나 다른 위치를 선택하세요.")
            except Exception as write_error:
                st.error(f"파일 쓰기 오류: {write_error}")
                st.error(f"HTML 길이: {len(dashboard_html)} 문자")
                
        except Exception as e:
            st.error(f"저장 중 오류가 발생했습니다: {e}")
            import traceback
            st.error(traceback.format_exc())
    
    def _generate_empty_dashboard_html(self, project_name, client):
        """빈 대시보드 HTML 생성"""
        return f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>{project_name} - 분석 결과</title>
            <style>
                body {{ font-family: 'Malgun Gothic', sans-serif; margin: 20px; text-align: center; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 40px; }}
                .header {{ margin-bottom: 40px; }}
                .message {{ font-size: 18px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💧 {project_name}</h1>
                    <p>의뢰 기관: {client}</p>
                </div>
                <div class="message">
                    <p>분석할 데이터가 없습니다.</p>
                    <p>생성 일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def generate_dashboard_html(self, test_results, filename, client):
        """대시보드 HTML 보고서 생성"""
        try:
            project_name = filename.replace('.xlsx', '').replace('.xls', '')
            
            # 기본 통계 계산 (안전한 처리)
            total_tests = len(test_results) if test_results else 0
            if total_tests == 0:
                return self._generate_empty_dashboard_html(project_name, client)
            
            # 안전한 부적합 항목 필터링
            violations = []
            for r in test_results:
                try:
                    if hasattr(r, 'is_non_conforming') and callable(r.is_non_conforming):
                        if r.is_non_conforming():
                            violations.append(r)
                    elif hasattr(r, 'standard_excess') and r.standard_excess == '부적합':
                        violations.append(r)
                except Exception:
                    continue
            
            violation_rate = len(violations) / total_tests * 100 if total_tests > 0 else 0
            
            # 안전한 샘플명 추출
            unique_samples = set()
            violation_sample_names = set()
            
            for r in test_results:
                if hasattr(r, 'sample_name') and r.sample_name:
                    unique_samples.add(r.sample_name)
            
            for v in violations:
                if hasattr(v, 'sample_name') and v.sample_name:
                    violation_sample_names.add(v.sample_name)
            
            violation_samples = len(violation_sample_names)
            
            # 부적합 항목별 집계 (안전한 처리)
            violation_by_item = {}
            for v in violations:
                try:
                    item = getattr(v, 'test_item', '알 수 없음')
                    if item:
                        violation_by_item[item] = violation_by_item.get(item, 0) + 1
                except Exception:
                    continue
            
            top_violation_items = sorted(violation_by_item.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # 부적합 항목 테이블 생성
            violation_table_rows = ""
            for i, (item, count) in enumerate(top_violation_items, 1):
                percentage = (count / len(violations) * 100) if violations else 0
                violation_table_rows += f"""
                <tr>
                    <td>{i}</td>
                    <td>{item}</td>
                    <td>{count}건</td>
                    <td>{percentage:.1f}%</td>
                </tr>
                """
            
            if not violation_table_rows:
                violation_table_rows = "<tr><td colspan='4'>부적합 항목이 없습니다.</td></tr>"
            
            # HTML 생성
            return f"""
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <title>{project_name} - 분석 결과</title>
                <style>
                    body {{ font-family: 'Malgun Gothic', sans-serif; margin: 20px; }}
                    .container {{ max-width: 1200px; margin: 0 auto; padding: 40px; }}
                    .header {{ text-align: center; margin-bottom: 40px; }}
                    .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 40px; }}
                    .kpi-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; text-align: center; }}
                    .kpi-value {{ font-size: 2rem; font-weight: bold; color: #1e293b; }}
                    .kpi-label {{ color: #64748b; font-size: 0.9rem; }}
                    table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                    th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
                    th {{ background-color: #f8fafc; font-weight: 600; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>💧 {project_name}</h1>
                        <p>의뢰 기관: {client}</p>
                        <p>생성 일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
                    </div>
                    
                    <div class="kpi-grid">
                        <div class="kpi-card">
                            <div class="kpi-value">{total_tests}</div>
                            <div class="kpi-label">총 시험 건수</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value">{len(unique_samples)}</div>
                            <div class="kpi-label">총 시료 개수</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value">{len(violations)}</div>
                            <div class="kpi-label">부적합 건수</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value">{violation_rate:.1f}%</div>
                            <div class="kpi-label">부적합률</div>
                        </div>
                    </div>
                    
                    <h2>🔍 주요 부적합 항목</h2>
                    <table>
                        <thead>
                            <tr><th>순위</th><th>시험 항목</th><th>부적합 건수</th><th>비율</th></tr>
                        </thead>
                        <tbody>{violation_table_rows}</tbody>
                    </table>
                </div>
            </body>
            </html>
            """
            
        except Exception as e:
            # 오류 발생 시 기본 HTML 반환
            return self._generate_empty_dashboard_html(filename.replace('.xlsx', '').replace('.xls', ''), client)
        for i, (item, count) in enumerate(top_violation_items, 1):
            violation_table_rows += f"""
            <tr>
                <td>{i}</td>
                <td>{item}</td>
                <td>{count}건</td>
                <td>{(count/len(violations)*100):.1f}%</td>
            </tr>
            """
        
        if not violation_table_rows:
            violation_table_rows = "<tr><td colspan='4'>부적합 항목이 없습니다.</td></tr>"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{project_name} - 분석 결과 보고서</title>
            <style>
                body {{
                    font-family: 'Malgun Gothic', sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8fafc;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                    border-bottom: 3px solid #3b82f6;
                    padding-bottom: 20px;
                }}
                .header h1 {{
                    color: #1e293b;
                    font-size: 2.5rem;
                    margin-bottom: 10px;
                }}
                .header p {{
                    color: #64748b;
                    font-size: 1.2rem;
                }}
                .kpi-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }}
                .kpi-card {{
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                }}
                .kpi-value {{
                    font-size: 2.5rem;
                    font-weight: bold;
                    color: #1e293b;
                    margin-bottom: 5px;
                }}
                .kpi-label {{
                    color: #64748b;
                    font-size: 0.9rem;
                }}
                .section {{
                    margin-bottom: 40px;
                }}
                .section h2 {{
                    color: #1e293b;
                    font-size: 1.5rem;
                    margin-bottom: 20px;
                    border-left: 4px solid #3b82f6;
                    padding-left: 15px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #e2e8f0;
                }}
                th {{
                    background-color: #f8fafc;
                    font-weight: 600;
                    color: #374151;
                }}
                .summary-box {{
                    background: #eff6ff;
                    border: 1px solid #bfdbfe;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e2e8f0;
                    color: #64748b;
                    font-size: 0.9rem;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💧 {project_name}</h1>
                    <p>분석 결과 보고서</p>
                    <p><strong>의뢰 기관:</strong> {client}</p>
                </div>
                
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="kpi-value">{total_tests}</div>
                        <div class="kpi-label">총 시험 항목 수</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{unique_samples}</div>
                        <div class="kpi-label">총 시료 수</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{len(violations)}</div>
                        <div class="kpi-label">부적합 항목 수</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{violation_rate:.1f}%</div>
                        <div class="kpi-label">부적합률</div>
                    </div>
                </div>
                
                <div class="summary-box">
                    <h3>📋 분석 요약</h3>
                    <p>총 {unique_samples}개 시료에서 {total_tests}개 항목을 분석한 결과, {len(violations)}개 항목이 부적합으로 판정되어 {violation_rate:.1f}%의 부적합률을 보였습니다.</p>
                    <p>부적합 시료는 총 {violation_samples}개로 전체 시료의 {(violation_samples/unique_samples*100):.1f}%에 해당합니다.</p>
                </div>
                
                <div class="section">
                    <h2>🔍 주요 부적합 항목</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>순위</th>
                                <th>시험 항목</th>
                                <th>부적합 건수</th>
                                <th>비율</th>
                            </tr>
                        </thead>
                        <tbody>
                            {violation_table_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="footer">
                    <p>본 보고서는 Aqua-Analytics 시스템에서 자동 생성되었습니다.</p>
                    <p>생성 일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def load_saved_data(self):
        """저장된 데이터 자동 로드"""
        try:
            # 데이터베이스에서 모든 파일 조회
            all_files = self.db_manager.get_all_files()
            
            # 세션 상태에 로드
            for file_record in all_files:
                filename = file_record['file_name']
                
                # TestResult 객체 재구성
                test_results = []
                for result_data in file_record.get('test_results', []):
                    # 딕셔너리에서 TestResult 객체로 변환
                    from data_models import TestResult
                    test_result = TestResult(
                        no=result_data.get('no', 0),
                        sample_name=result_data.get('sample_name', ''),
                        analysis_number=result_data.get('analysis_number', ''),
                        test_item=result_data.get('test_item', ''),
                        test_unit=result_data.get('test_unit', ''),
                        result_report=result_data.get('result_report', ''),
                        tester_input_value=result_data.get('tester_input_value', 0),
                        standard_excess=result_data.get('standard_excess', '적합'),
                        tester=result_data.get('tester', ''),
                        test_standard=result_data.get('test_standard', ''),
                        standard_criteria=result_data.get('standard_criteria', ''),
                        text_digits=result_data.get('text_digits', ''),
                        processing_method=result_data.get('processing_method', ''),
                        result_display_digits=result_data.get('result_display_digits', 0),
                        result_type=result_data.get('result_type', ''),
                        tester_group=result_data.get('tester_group', ''),
                        input_datetime=datetime.fromisoformat(result_data['input_datetime']) if result_data.get('input_datetime') else datetime.now(),
                        approval_request=result_data.get('approval_request', ''),
                        approval_request_datetime=None,
                        test_result_display_limit=result_data.get('test_result_display_limit', 0),
                        quantitative_limit_processing=result_data.get('quantitative_limit_processing', ''),
                        test_equipment=result_data.get('test_equipment', ''),
                        judgment_status=result_data.get('judgment_status', ''),
                        report_output=result_data.get('report_output', ''),
                        kolas_status=result_data.get('kolas_status', ''),
                        test_lab_group=result_data.get('test_lab_group', ''),
                        test_set=result_data.get('test_set', '')
                    )
                    test_results.append(test_result)
                
                # 세션 상태에 추가
                st.session_state.uploaded_files[filename] = {
                    'test_results': test_results,
                    'processed': True,
                    'upload_time': datetime.fromisoformat(file_record['processed_at']),
                    'client': file_record.get('client', '미지정'),
                    'file_id': file_record['file_id']
                }
                
                # 보고서 이력에도 추가
                self.save_to_report_history(
                    filename, 
                    test_results, 
                    datetime.fromisoformat(file_record['processed_at']),
                    file_record.get('client', '미지정')
                )
            
            if all_files:
                st.success(f"✅ {len(all_files)}개의 저장된 파일을 불러왔습니다.")
                
        except Exception as e:
            st.warning(f"저장된 데이터 로드 중 오류: {e}")
            # 오류가 발생해도 애플리케이션은 계속 실행
    
    def load_existing_data(self):
        """데이터베이스에서 기존 데이터 로드"""
        try:
            # db_manager가 초기화되었는지 확인
            if not hasattr(self, 'db_manager') or self.db_manager is None:
                return
                
            # 데이터베이스에서 모든 파일 조회
            all_files = self.db_manager.get_all_files()
            
            # 세션 상태에 로드
            for file_record in all_files:
                file_name = file_record['file_name']
                
                # TestResult 객체로 복원 (원본 클래스 사용)
                from data_models import TestResult
                
                test_results = []
                for result_data in file_record['test_results']:
                    # 원본 TestResult 클래스로 완전한 객체 생성
                    test_result = TestResult(
                        no=result_data.get('no', 0),
                        sample_name=result_data.get('sample_name', ''),
                        analysis_number=result_data.get('analysis_number', ''),
                        test_item=result_data.get('test_item', ''),
                        test_unit=result_data.get('test_unit', ''),
                        result_report=result_data.get('result_report', ''),
                        tester_input_value=result_data.get('tester_input_value', 0),
                        standard_excess=result_data.get('standard_excess', '적합'),
                        tester=result_data.get('tester', ''),
                        test_standard=result_data.get('test_standard', ''),
                        standard_criteria=result_data.get('standard_criteria', ''),
                        text_digits=result_data.get('text_digits', ''),
                        processing_method=result_data.get('processing_method', ''),
                        result_display_digits=result_data.get('result_display_digits', 0),
                        result_type=result_data.get('result_type', ''),
                        tester_group=result_data.get('tester_group', ''),
                        input_datetime=datetime.fromisoformat(result_data['input_datetime']) if result_data.get('input_datetime') else datetime.now(),
                        approval_request=result_data.get('approval_request', ''),
                        approval_request_datetime=None,
                        test_result_display_limit=result_data.get('test_result_display_limit', 0),
                        quantitative_limit_processing=result_data.get('quantitative_limit_processing', ''),
                        test_equipment=result_data.get('test_equipment', ''),
                        judgment_status=result_data.get('judgment_status', ''),
                        report_output=result_data.get('report_output', ''),
                        kolas_status=result_data.get('kolas_status', ''),
                        test_lab_group=result_data.get('test_lab_group', ''),
                        test_set=result_data.get('test_set', '')
                    )
                    test_results.append(test_result)
                
                # 세션 상태에 저장
                upload_time = datetime.fromisoformat(file_record['processed_at'])
                st.session_state.uploaded_files[file_name] = {
                    'test_results': test_results,
                    'processed': True,
                    'upload_time': upload_time,
                    'client': file_record.get('client', '미지정'),
                    'file_id': file_record['file_id']
                }
                
                # 보고서 이력에도 추가 (file_id 포함)
                report_data = {
                    'filename': file_name,
                    'project_name': file_record.get('project_name', file_name.replace('.xlsx', '').replace('.xls', '')),
                    'test_results': test_results,
                    'upload_time': upload_time,
                    'client': file_record.get('client', '미지정'),
                    'total_tests': file_record['summary']['total_items'],
                    'violations': file_record['summary']['fail_items'],
                    'violation_rate': file_record['summary']['failure_rate'],
                    'file_id': file_record['file_id']  # file_id 추가
                }
                
                # 중복 확인 후 추가
                existing = False
                for existing_report in st.session_state.report_history:
                    if existing_report['filename'] == file_name:
                        existing = True
                        break
                
                if not existing:
                    st.session_state.report_history.append(report_data)
            
            # 최신 순으로 정렬
            st.session_state.report_history.sort(key=lambda x: x['upload_time'], reverse=True)
            
        except Exception as e:
            # 데이터 로드 실패 시 조용히 넘어감 (첫 실행 시 데이터가 없을 수 있음)
            pass
    

    

    
    def run(self):
        """애플리케이션 실행"""
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

# 애플리케이션 실행
if __name__ == "__main__":
    app = AquaAnalyticsPremium()
    app.run()