#!/usr/bin/env python3
"""
Aqua-Analytics Premium: 환경 데이터 인사이트 플랫폼 - GitHub 데모 버전
로컬 버전과 동일한 UI/UX, 세션 기반 임시 저장
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import io
import json
import os
from pathlib import Path

st.set_page_config(
    page_title="Aqua-Analytics | 환경 데이터 인사이트 플랫폼",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AquaAnalyticsDemo:
    """Aqua-Analytics Premium 데모 애플리케이션"""
    
    def __init__(self):
        self.apply_premium_theme()
        self.initialize_session_state()
    
    def apply_premium_theme(self):
        """프리미엄 테마 CSS 적용 (로컬 버전과 동일)"""
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
        
        /* 사이드바 브랜드 */
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
        
        /* 네비게이션 섹션 타이틀 */
        .nav-section-title {
            font-size: 0.6875rem;
            font-weight: 700;
            color: var(--gray-400);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin: 1.5rem 0 0.75rem 0;
            padding: 0 0.5rem;
        }
        
        /* 버튼 스타일 */
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
        
        /* 파일 업로더 스타일 */
        .stFileUploader {
            background: var(--gray-50);
            border: 2px dashed var(--gray-300);
            border-radius: 0.5rem;
            padding: 1.5rem;
            text-align: center;
            margin: 1rem 0;
        }
        
        /* 메트릭 카드 */
        .metric-card {
            background: white;
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--gray-200);
            margin-bottom: 1rem;
        }
        
        /* 데모 배너 */
        .demo-banner {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border: 1px solid #f59e0b;
            border-radius: 0.75rem;
            padding: 1rem;
            margin-bottom: 1.5rem;
            color: #92400e;
        }
        
        /* 차트 컨테이너 */
        .chart-container {
            background: white;
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--gray-200);
            margin-bottom: 1.5rem;
        }
        
        /* 데이터프레임 스타일 */
        .dataframe {
            border-radius: 0.5rem;
            overflow: hidden;
            box-shadow: var(--shadow-sm);
        }
        
        /* 페이지 헤더 */
        .page-header {
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--gray-200);
        }
        
        .page-title {
            font-size: 1.875rem;
            font-weight: 700;
            color: var(--gray-900);
            margin-bottom: 0.5rem;
        }
        
        .page-subtitle {
            font-size: 1rem;
            color: var(--gray-600);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """세션 상태 초기화 (로컬 버전과 동일한 구조)"""
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
        if 'active_file' not in st.session_state:
            st.session_state.active_file = None
        if 'uploaded_data' not in st.session_state:
            st.session_state.uploaded_data = None
        if 'processed_data' not in st.session_state:
            st.session_state.processed_data = None
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'demo_data_loaded' not in st.session_state:
            st.session_state.demo_data_loaded = False
    
    def render_sidebar(self):
        """프리미엄 사이드바 렌더링 (로컬 버전과 동일한 구조)"""
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
            
            # 데모 알림
            st.markdown("""
            <div class="demo-banner">
                <strong>🌐 GitHub 데모 버전</strong><br>
                데이터는 세션 종료 시 삭제됩니다.<br>
                실제 업무용은 로컬 서버 버전을 설치하세요.
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
            
            # 파일 업로드 섹션
            st.markdown("---")
            st.markdown('<div class="nav-section-title">파일 업로드</div>', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "엑셀 파일 선택",
                type=['xlsx', 'xls', 'csv'],
                help="환경 데이터 파일을 업로드하세요",
                key="file_uploader"
            )
            
            if uploaded_file is not None:
                self.process_uploaded_file(uploaded_file)
            
            # 샘플 데이터 로드 버튼
            if st.button("📊 샘플 데이터 로드", use_container_width=True):
                self.load_sample_data()
            
            # 저장 폴더 바로가기 섹션
            st.markdown("---")
            st.markdown('<div class="nav-section-title">저장 폴더 (데모)</div>', unsafe_allow_html=True)
            
            folder_info = [
                {'label': '업로드 파일', 'icon': '📤', 'count': len(st.session_state.get('uploaded_files', []))},
                {'label': '처리된 파일', 'icon': '⚙️', 'count': 1 if st.session_state.processed_data is not None else 0},
                {'label': '보고서', 'icon': '📄', 'count': 1 if st.session_state.active_file else 0}
            ]
            
            for folder in folder_info:
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: var(--gray-50); border-radius: 0.5rem; margin-bottom: 0.5rem;">
                    <span>{folder['icon']} {folder['label']}</span>
                    <span style="background: var(--primary-100); color: var(--primary-700); padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;">
                        {folder['count']}개
                    </span>
                </div>
                """, unsafe_allow_html=True)
    
    def process_uploaded_file(self, uploaded_file):
        """업로드된 파일 처리"""
        try:
            # 파일 형식에 따른 읽기
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            
            # 세션에 저장
            st.session_state.uploaded_data = df
            st.session_state.processed_data = df
            st.session_state.active_file = uploaded_file.name
            
            # 기본 분석 수행
            self.perform_basic_analysis(df)
            
            st.success(f"✅ 파일 업로드 성공: {uploaded_file.name}")
            st.info(f"📊 데이터 크기: {len(df):,}행 × {len(df.columns)}열")
            
        except Exception as e:
            st.error(f"❌ 파일 처리 오류: {str(e)}")
    
    def load_sample_data(self):
        """샘플 데이터 로드"""
        # 샘플 환경 데이터 생성
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
        
        st.session_state.uploaded_data = sample_data
        st.session_state.processed_data = sample_data
        st.session_state.active_file = "샘플_환경데이터.xlsx"
        st.session_state.demo_data_loaded = True
        
        self.perform_basic_analysis(sample_data)
        st.success("✅ 샘플 데이터가 로드되었습니다!")
        st.rerun()
    
    def perform_basic_analysis(self, df):
        """기본 분석 수행"""
        analysis = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum(),
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'data_types': df.dtypes.to_dict()
        }
        
        # 부적합 항목 분석 (환경 데이터 특화)
        if '기준대비 초과여부' in df.columns:
            analysis['non_conforming_count'] = len(df[df['기준대비 초과여부'] == '부적합'])
            analysis['conforming_rate'] = (len(df) - analysis['non_conforming_count']) / len(df) * 100
        
        st.session_state.analysis_results = analysis
    
    def render_dashboard_page(self):
        """대시보드 페이지 렌더링"""
        st.markdown("""
        <div class="page-header">
            <div class="page-title">📊 대시보드</div>
            <div class="page-subtitle">환경 데이터 실시간 모니터링 및 분석</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.processed_data is not None:
            df = st.session_state.processed_data
            
            # KPI 카드
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <div style="font-size: 0.875rem; color: var(--gray-600); margin-bottom: 0.5rem;">총 데이터 수</div>
                    <div style="font-size: 2rem; font-weight: 700; color: var(--gray-900);">{:,}</div>
                </div>
                """.format(len(df)), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <div style="font-size: 0.875rem; color: var(--gray-600); margin-bottom: 0.5rem;">분석 항목</div>
                    <div style="font-size: 2rem; font-weight: 700; color: var(--primary-600);">{}</div>
                </div>
                """.format(len(df.columns)), unsafe_allow_html=True)
            
            with col3:
                non_conforming = st.session_state.analysis_results.get('non_conforming_count', 0)
                st.markdown("""
                <div class="metric-card">
                    <div style="font-size: 0.875rem; color: var(--gray-600); margin-bottom: 0.5rem;">부적합 항목</div>
                    <div style="font-size: 2rem; font-weight: 700; color: var(--error);">{}</div>
                </div>
                """.format(non_conforming), unsafe_allow_html=True)
            
            with col4:
                conforming_rate = st.session_state.analysis_results.get('conforming_rate', 100)
                st.markdown("""
                <div class="metric-card">
                    <div style="font-size: 0.875rem; color: var(--gray-600); margin-bottom: 0.5rem;">적합률</div>
                    <div style="font-size: 2rem; font-weight: 700; color: var(--success);">{:.1f}%</div>
                </div>
                """.format(conforming_rate), unsafe_allow_html=True)
            
            # 차트 섹션
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                if '시험항목' in df.columns and '결과(성적서)' in df.columns:
                    fig = px.box(df, x='시험항목', y='결과(성적서)', 
                                title="시험항목별 결과 분포")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                if '기준대비 초과여부' in df.columns:
                    conformity_counts = df['기준대비 초과여부'].value_counts()
                    fig = px.pie(values=conformity_counts.values, names=conformity_counts.index,
                               title="적합성 분포")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # 데이터 테이블
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📋 데이터 테이블")
            st.dataframe(df.head(20), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.info("👈 사이드바에서 파일을 업로드하거나 샘플 데이터를 로드해주세요.")
    
    def render_integrated_analysis_page(self):
        """통합 분석 페이지 렌더링"""
        st.markdown("""
        <div class="page-header">
            <div class="page-title">📈 통합 분석</div>
            <div class="page-subtitle">AI 기반 환경 데이터 통합 분석 및 인사이트</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.processed_data is not None:
            df = st.session_state.processed_data
            
            # 분석 옵션
            col1, col2 = st.columns(2)
            with col1:
                analysis_type = st.selectbox(
                    "분석 유형 선택",
                    ["전체 분석", "시험항목별 분석", "시간별 분석", "적합성 분석"]
                )
            with col2:
                chart_type = st.selectbox(
                    "차트 유형",
                    ["라인 차트", "바 차트", "히트맵", "산점도"]
                )
            
            # 분석 결과
            if analysis_type == "전체 분석":
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    if '분석일자' in df.columns and '결과(성적서)' in df.columns:
                        fig = px.line(df, x='분석일자', y='결과(성적서)', 
                                     color='시험항목' if '시험항목' in df.columns else None,
                                     title="시간별 측정값 추이")
                        st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 1:
                        corr_matrix = df[numeric_cols].corr()
                        fig = px.imshow(corr_matrix, title="변수 간 상관관계")
                        st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # AI 인사이트
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("🤖 AI 인사이트")
            
            insights = [
                "📈 최근 7일간 pH 수치가 안정적인 범위를 유지하고 있습니다.",
                "⚠️ COD 수치에서 일부 기준 초과 사례가 발견되었습니다.",
                "🔍 용존산소 농도가 계절적 패턴을 보이고 있습니다.",
                "💡 전체적인 수질 상태는 양호한 수준입니다.",
                "📊 지속적인 모니터링을 통한 품질 관리가 권장됩니다."
            ]
            
            for i, insight in enumerate(insights):
                st.info(f"{insight}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.info("👈 먼저 데이터를 업로드해주세요.")
    
    def render_reports_management_page(self):
        """보고서 관리 페이지 렌더링"""
        st.markdown("""
        <div class="page-header">
            <div class="page-title">📄 보고서 관리</div>
            <div class="page-subtitle">분석 보고서 생성 및 관리</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.processed_data is not None:
            df = st.session_state.processed_data
            
            # 보고서 생성 옵션
            col1, col2 = st.columns(2)
            
            with col1:
                report_type = st.selectbox(
                    "보고서 유형",
                    ["종합 분석 보고서", "품질 관리 보고서", "부적합 항목 보고서", "통계 요약 보고서"]
                )
            
            with col2:
                export_format = st.selectbox(
                    "내보내기 형식",
                    ["HTML", "PDF", "Excel", "Word"]
                )
            
            if st.button("📋 보고서 생성", use_container_width=True):
                # 보고서 내용 생성
                report_content = self.generate_report(df, report_type)
                
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown(report_content, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 다운로드 버튼
                st.download_button(
                    label=f"📄 {report_type} 다운로드",
                    data=report_content,
                    file_name=f"aqua_analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
        else:
            st.info("👈 먼저 데이터를 업로드해주세요.")
    
    def render_standards_management_page(self):
        """시험 규격 관리 페이지 렌더링"""
        st.markdown("""
        <div class="page-header">
            <div class="page-title">🛡️ 시험 규격 관리</div>
            <div class="page-subtitle">환경 시험 규격 및 기준 관리</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 데모용 규격 정보
        standards_data = {
            "pH": {"기준값": "6.5-8.5", "단위": "pH", "규격": "KS M 0011"},
            "용존산소": {"기준값": "≥5.0", "단위": "mg/L", "규격": "KS M 0012"},
            "탁도": {"기준값": "≤4.0", "단위": "NTU", "규격": "KS M 0013"},
            "COD": {"기준값": "≤8.0", "단위": "mg/L", "규격": "KS M 0014"},
            "BOD": {"기준값": "≤3.0", "단위": "mg/L", "규격": "KS M 0015"}
        }
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📋 현재 적용 규격")
        
        standards_df = pd.DataFrame(standards_data).T
        standards_df.index.name = "시험항목"
        st.dataframe(standards_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 규격 파일 업로드 (데모)
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📤 규격 문서 업로드")
        
        uploaded_standard = st.file_uploader(
            "PDF 규격 문서 업로드",
            type=['pdf'],
            help="시험 규격 PDF 문서를 업로드하세요"
        )
        
        if uploaded_standard:
            st.success(f"✅ 규격 문서 업로드 완료: {uploaded_standard.name}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def generate_report(self, df, report_type):
        """보고서 생성"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report_html = f"""
        <div style="font-family: 'Inter', sans-serif; max-width: 800px;">
            <h1 style="color: var(--primary-600); border-bottom: 2px solid var(--primary-200); padding-bottom: 1rem;">
                🧪 {report_type}
            </h1>
            
            <div style="background: var(--gray-50); padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                <h3>📋 기본 정보</h3>
                <ul>
                    <li><strong>생성 일시:</strong> {current_time}</li>
                    <li><strong>데이터 파일:</strong> {st.session_state.active_file or '샘플 데이터'}</li>
                    <li><strong>총 데이터 수:</strong> {len(df):,}개</li>
                    <li><strong>분석 항목 수:</strong> {len(df.columns)}개</li>
                </ul>
            </div>
            
            <div style="background: white; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; border: 1px solid var(--gray-200);">
                <h3>📊 데이터 요약</h3>
                <p>업로드된 데이터에 대한 기본 통계 분석 결과입니다.</p>
                
                <h4>🔍 품질 지표</h4>
                <ul>
                    <li><strong>결측값:</strong> {df.isnull().sum().sum()}개</li>
                    <li><strong>중복값:</strong> {df.duplicated().sum()}개</li>
                    <li><strong>데이터 완성도:</strong> {((len(df) * len(df.columns) - df.isnull().sum().sum()) / (len(df) * len(df.columns)) * 100):.1f}%</li>
                </ul>
                
                <h4>💡 주요 인사이트</h4>
                <ul>
                    <li>전체적인 데이터 품질이 양호합니다</li>
                    <li>추가 분석을 통한 심화 인사이트 도출이 가능합니다</li>
                    <li>정기적인 모니터링을 통한 품질 관리가 권장됩니다</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--gray-200); color: var(--gray-500);">
                <p><em>Aqua-Analytics Premium에서 생성된 보고서입니다.</em></p>
            </div>
        </div>
        """
        
        return report_html
    
    def run(self):
        """애플리케이션 실행 (로컬 버전과 동일한 구조)"""
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