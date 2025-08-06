#!/usr/bin/env python3
"""
Aqua-Analytics Premium: 환경 데이터 인사이트 플랫폼 - GitHub 데모 버전
로컬 버전과 완전히 동일한 UI/UX 및 기능
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

# 테스트 결과 클래스 (로컬 버전과 동일)
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
        return self.conformity == '부적합'

class AquaAnalyticsDemo:
    """Aqua-Analytics Premium 데모 애플리케이션 (로컬 버전 완전 복제)"""
    
    def __init__(self):
        self.apply_premium_theme()
        self.initialize_session_state()
    
    def apply_premium_theme(self):
        """프리미엄 테마 CSS 적용 (로컬 버전과 완전 동일)"""
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
        
        /* KPI 카드 스타일 */
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
            background: linear-gradient(90deg, var(--primary-500), var(--primary-600));
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
        
        .kpi-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-bottom: 16px;
        }
        
        .kpi-value {
            font-size: 2.5rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 8px;
        }
        
        .kpi-label {
            font-size: 0.875rem;
            color: var(--gray-600);
            font-weight: 500;
        }
        
        /* 페이지 헤더 */
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
        .upload-area {
            background: white;
            border: 2px dashed var(--gray-300);
            border-radius: 16px;
            padding: 3rem 2rem;
            text-align: center;
            margin: 2rem 0;
            transition: all 0.3s ease;
        }
        
        .upload-area:hover {
            border-color: var(--primary-500);
            background: var(--primary-50);
        }
        
        .upload-icon {
            font-size: 4rem;
            color: var(--gray-400);
            margin-bottom: 1rem;
        }
        
        .upload-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 0.5rem;
        }
        
        .upload-subtitle {
            font-size: 1rem;
            color: var(--gray-600);
            margin-bottom: 2rem;
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
        if 'demo_data_loaded' not in st.session_state:
            st.session_state.demo_data_loaded = False
    
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
                file_count = len(st.session_state.uploaded_files) if folder['key'] == 'uploads' else 0
                if folder['key'] == 'processed' and st.session_state.active_file:
                    file_count = 1
                if folder['key'] == 'dashboard_reports' and st.session_state.active_file:
                    file_count = 1
                
                count_text = f"({file_count}개)"
                
                if st.button(f"{folder['icon']} {folder['label']} {count_text}", 
                           key=f"folder_{folder['key']}", use_container_width=True):
                    st.info(f"📁 {folder['label']} 폴더 - 데모 버전에서는 실제 폴더 열기가 제한됩니다.")
    
    def process_uploaded_file(self, uploaded_file):
        """업로드된 파일 처리 (로컬 버전과 동일한 로직)"""
        try:
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
                'raw_data': df,
                'upload_time': datetime.now()
            }
            st.session_state.active_file = uploaded_file.name
            
            st.success(f"✅ 파일 업로드 성공: {uploaded_file.name}")
            st.info(f"📊 데이터 크기: {len(df):,}행 × {len(df.columns)}열")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 파일 처리 오류: {str(e)}")
    
    def load_sample_data(self):
        """샘플 데이터 로드 (로컬 버전과 동일한 구조)"""
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
        
        # 테스트 결과 객체 생성
        test_results = []
        for _, row in sample_data.iterrows():
            test_results.append(TestResult(row.to_dict()))
        
        # 세션에 저장
        filename = "샘플_환경데이터.xlsx"
        st.session_state.uploaded_files[filename] = {
            'test_results': test_results,
            'raw_data': sample_data,
            'upload_time': datetime.now()
        }
        st.session_state.active_file = filename
        st.session_state.demo_data_loaded = True
        
        st.success("✅ 샘플 데이터가 로드되었습니다!")
        st.rerun()
    
    def render_page_header(self, title, subtitle, show_save_button=False):
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
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon" style="background: #dbeafe; color: #2563eb;">
                    📊
                </div>
                <div>
                    <div class="kpi-value" style="color: #2563eb;">{total_tests:,}</div>
                    <div class="kpi-label">총 시험 건수</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon" style="background: #fef2f2; color: #ef4444;">
                    ⚠️
                </div>
                <div>
                    <div class="kpi-value" style="color: #ef4444;">{len(violations):,}</div>
                    <div class="kpi-label">부적합 건수</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon" style="background: #f0fdf4; color: #22c55e;">
                    📈
                </div>
                <div>
                    <div class="kpi-value" style="color: #22c55e;">{100-violation_rate:.1f}%</div>
                    <div class="kpi-label">적합률</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon" style="background: #fef3c7; color: #f59e0b;">
                    🧪
                </div>
                <div>
                    <div class="kpi-value" style="color: #f59e0b;">{unique_samples:,}</div>
                    <div class="kpi-label">시료 수</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_upload_page(self):
        """프리미엄 업로드 페이지 (로컬 버전과 동일)"""
        self.render_page_header("데이터 업로드", "Excel 파일을 업로드하여 환경 데이터 분석을 시작하세요")
        
        # 업로드 영역
        st.markdown("""
        <div class="upload-area">
            <div class="upload-icon">📁</div>
            <div class="upload-title">파일을 업로드하세요</div>
            <div class="upload-subtitle">Excel (.xlsx, .xls) 또는 CSV 파일을 지원합니다</div>
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
        """)
    
    def render_dashboard_page(self):
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
                    violations = [r for r in test_results if r.is_non_conforming()]
                    if violations:
                        # 부적합 항목별 분포
                        violation_by_item = {}
                        for v in violations:
                            violation_by_item[v.test_item] = violation_by_item.get(v.test_item, 0) + 1
                        
                        # 도넛 차트 생성
                        fig = go.Figure(data=[go.Pie(
                            labels=list(violation_by_item.keys()),
                            values=list(violation_by_item.values()),
                            hole=0.4,
                            marker_colors=['#ef4444', '#f97316', '#eab308', '#84cc16', '#22c55e']
                        )])
                        
                        fig.update_layout(
                            title="",
                            height=400,
                            margin=dict(l=20, r=20, t=20, b=20),
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, key="premium_donut")
                    else:
                        st.info("부적합 항목이 없습니다.")
                except Exception as e:
                    st.error(f"도넛 차트 오류: {e}")
            
            with chart_col2:
                st.markdown("#### 📈 부적합 시료별 건수")
                try:
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
        
        # 데이터프레임 표시
        df = file_data['raw_data']
        st.dataframe(df, use_container_width=True, height=400)
    
    def render_integrated_analysis_page(self):
        """통합 분석 페이지 렌더링"""
        self.render_page_header("통합 분석", "AI 기반 환경 데이터 통합 분석 및 인사이트")
        
        if not st.session_state.active_file:
            st.info("👈 먼저 데이터를 업로드해주세요.")
            return
        
        file_data = st.session_state.uploaded_files[st.session_state.active_file]
        test_results = file_data['test_results']
        df = file_data['raw_data']
        
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
        
        # 분석 결과 차트
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 시험항목별 결과 분포")
            if '시험항목' in df.columns and '결과(성적서)' in df.columns:
                fig = px.box(df, x='시험항목', y='결과(성적서)', 
                           title="시험항목별 측정값 분포")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🔍 적합성 분석")
            if '기준대비 초과여부' in df.columns:
                conformity_counts = df['기준대비 초과여부'].value_counts()
                fig = px.pie(values=conformity_counts.values, names=conformity_counts.index,
                           title="전체 적합성 분포")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # AI 인사이트
        st.markdown("---")
        st.markdown("#### 🤖 AI 인사이트")
        
        violations = [r for r in test_results if r.is_non_conforming()]
        violation_rate = len(violations) / len(test_results) * 100
        
        insights = [
            f"📊 전체 {len(test_results)}건의 시험 중 {len(violations)}건이 부적합으로 판정되었습니다.",
            f"📈 부적합률은 {violation_rate:.1f}%로 {'주의가 필요한' if violation_rate > 10 else '양호한'} 수준입니다.",
            "🔍 주요 부적합 항목에 대한 원인 분석이 권장됩니다.",
            "💡 지속적인 모니터링을 통한 품질 개선이 필요합니다.",
            "📋 정기적인 시험 규격 검토를 통한 기준 최적화를 고려해보세요."
        ]
        
        for insight in insights:
            st.info(insight)
    
    def render_reports_management_page(self):
        """보고서 관리 페이지 렌더링"""
        self.render_page_header("보고서 관리", "분석 보고서 생성 및 관리")
        
        if not st.session_state.active_file:
            st.info("👈 먼저 데이터를 업로드해주세요.")
            return
        
        file_data = st.session_state.uploaded_files[st.session_state.active_file]
        test_results = file_data['test_results']
        df = file_data['raw_data']
        
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
        
        if st.button("📋 보고서 생성", use_container_width=True, type="primary"):
            # 보고서 내용 생성
            violations = [r for r in test_results if r.is_non_conforming()]
            violation_rate = len(violations) / len(test_results) * 100
            
            report_content = f"""
            <div style="font-family: 'Inter', sans-serif; max-width: 800px; margin: 0 auto;">
                <h1 style="color: #2563eb; border-bottom: 2px solid #dbeafe; padding-bottom: 1rem;">
                    🧪 {report_type}
                </h1>
                
                <div style="background: #f8fafc; padding: 1.5rem; border-radius: 0.75rem; margin: 1.5rem 0;">
                    <h3 style="color: #1e293b; margin-bottom: 1rem;">📋 프로젝트 개요</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td style="padding: 0.5rem; border-bottom: 1px solid #e2e8f0;"><strong>프로젝트명:</strong></td><td style="padding: 0.5rem; border-bottom: 1px solid #e2e8f0;">{st.session_state.active_file}</td></tr>
                        <tr><td style="padding: 0.5rem; border-bottom: 1px solid #e2e8f0;"><strong>생성 일시:</strong></td><td style="padding: 0.5rem; border-bottom: 1px solid #e2e8f0;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                        <tr><td style="padding: 0.5rem; border-bottom: 1px solid #e2e8f0;"><strong>총 시험 건수:</strong></td><td style="padding: 0.5rem; border-bottom: 1px solid #e2e8f0;">{len(test_results):,}건</td></tr>
                        <tr><td style="padding: 0.5rem;"><strong>부적합 건수:</strong></td><td style="padding: 0.5rem; color: #ef4444; font-weight: 600;">{len(violations)}건 ({violation_rate:.1f}%)</td></tr>
                    </table>
                </div>
                
                <div style="background: white; padding: 1.5rem; border-radius: 0.75rem; margin: 1.5rem 0; border: 1px solid #e2e8f0;">
                    <h3 style="color: #1e293b; margin-bottom: 1rem;">📊 주요 지표</h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                        <div style="text-align: center; padding: 1rem; background: #f0fdf4; border-radius: 0.5rem;">
                            <div style="font-size: 2rem; font-weight: 700; color: #22c55e;">{100-violation_rate:.1f}%</div>
                            <div style="color: #166534;">적합률</div>
                        </div>
                        <div style="text-align: center; padding: 1rem; background: #fef2f2; border-radius: 0.5rem;">
                            <div style="font-size: 2rem; font-weight: 700; color: #ef4444;">{violation_rate:.1f}%</div>
                            <div style="color: #991b1b;">부적합률</div>
                        </div>
                    </div>
                </div>
                
                <div style="background: white; padding: 1.5rem; border-radius: 0.75rem; margin: 1.5rem 0; border: 1px solid #e2e8f0;">
                    <h3 style="color: #1e293b; margin-bottom: 1rem;">💡 분석 결과 및 권장사항</h3>
                    <ul style="line-height: 1.6;">
                        <li>전체 시험 결과의 품질 수준은 {'우수' if violation_rate < 5 else '보통' if violation_rate < 15 else '개선 필요'}합니다.</li>
                        <li>부적합 항목에 대한 원인 분석 및 개선 조치가 필요합니다.</li>
                        <li>정기적인 품질 모니터링을 통한 지속적 개선을 권장합니다.</li>
                        <li>시험 규격 및 절차의 정기적 검토가 필요합니다.</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; color: #64748b;">
                    <p><em>Aqua-Analytics Premium에서 생성된 보고서입니다.</em></p>
                </div>
            </div>
            """
            
            st.markdown(report_content, unsafe_allow_html=True)
            
            # 다운로드 버튼
            st.download_button(
                label=f"📄 {report_type} 다운로드 ({export_format})",
                data=report_content,
                file_name=f"aqua_analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
    
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