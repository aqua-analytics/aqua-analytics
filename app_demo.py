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
        """프리미엄 테마 CSS 적용"""
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* 전역 변수 정의 */
        :root {
            --primary-50: #eff6ff;
            --primary-100: #dbeafe;
            --primary-500: #3b82f6;
            --primary-600: #2563eb;
            --primary-700: #1d4ed8;
            --success-50: #f0fdf4;
            --success-500: #22c55e;
            --warning-50: #fffbeb;
            --warning-500: #f59e0b;
            --error-50: #fef2f2;
            --error-500: #ef4444;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-400: #9ca3af;
            --gray-500: #6b7280;
            --gray-600: #4b5563;
            --gray-700: #374151;
            --gray-800: #1f2937;
            --gray-900: #111827;
        }
        
        /* 기본 스타일 */
        .main {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, var(--primary-50) 0%, var(--gray-50) 100%);
        }
        
        /* 헤더 스타일 */
        .main-header {
            background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.15);
        }
        
        .main-header h1 {
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .main-header p {
            font-size: 1.1rem;
            opacity: 0.9;
            margin: 0.5rem 0 0 0;
        }
        
        /* 데모 알림 배너 */
        .demo-banner {
            background: linear-gradient(135deg, var(--warning-50) 0%, #fef3c7 100%);
            border: 1px solid var(--warning-500);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1.5rem;
        }
        
        /* 카드 스타일 */
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--gray-200);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        /* 사이드바 스타일 */
        .css-1d391kg {
            background: white;
            border-right: 1px solid var(--gray-200);
        }
        
        /* 버튼 스타일 */
        .stButton > button {
            background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        
        /* 파일 업로더 스타일 */
        .stFileUploader {
            background: var(--gray-50);
            border: 2px dashed var(--gray-300);
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
        }
        
        /* 데이터프레임 스타일 */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """세션 상태 초기화"""
        if 'uploaded_data' not in st.session_state:
            st.session_state.uploaded_data = None
        if 'processed_data' not in st.session_state:
            st.session_state.processed_data = None
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
    
    def render_header(self):
        """메인 헤더 렌더링"""
        st.markdown("""
        <div class="main-header">
            <h1>💧 Aqua-Analytics Premium</h1>
            <p>환경 데이터 인사이트 플랫폼 - GitHub 데모 버전</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 데모 알림 배너
        st.markdown("""
        <div class="demo-banner">
            <strong>🌐 GitHub 데모 버전</strong><br>
            이것은 기능 체험용 데모입니다. 데이터는 세션 종료 시 삭제됩니다.<br>
            실제 업무용은 로컬 서버 버전을 설치하여 사용하세요.
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """사이드바 렌더링"""
        with st.sidebar:
            st.markdown("### 📋 메뉴")
            
            # 메뉴 선택
            menu_options = [
                "🏠 홈",
                "📊 데이터 업로드", 
                "📈 대시보드",
                "🔍 통합 분석",
                "📋 보고서 생성"
            ]
            
            selected_menu = st.selectbox(
                "분석 메뉴 선택",
                menu_options,
                key="main_menu"
            )
            
            st.markdown("---")
            
            # 파일 업로드 섹션
            st.markdown("### 📁 파일 업로드")
            uploaded_file = st.file_uploader(
                "엑셀 파일 선택",
                type=['xlsx', 'xls', 'csv'],
                help="환경 데이터 파일을 업로드하세요"
            )
            
            if uploaded_file is not None:
                self.process_uploaded_file(uploaded_file)
            
            st.markdown("---")
            
            # 시스템 정보
            st.markdown("### ℹ️ 시스템 정보")
            st.info(f"""
            **버전**: Demo v1.0  
            **업데이트**: {datetime.now().strftime('%Y-%m-%d')}  
            **상태**: 온라인
            """)
            
            st.markdown("---")
            
            # 로컬 서버 안내
            st.markdown("### 🏢 로컬 서버 버전")
            st.markdown("""
            실제 업무용으로는 로컬 서버 버전을 설치하세요:
            
            1. GitHub에서 코드 다운로드
            2. `install_and_run.bat` 실행
            3. 사내 네트워크에서 접속
            """)
            
            return selected_menu
    
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
            st.session_state.filename = uploaded_file.name
            
            # 기본 분석 수행
            self.perform_basic_analysis(df)
            
            st.success(f"✅ 파일 업로드 성공: {uploaded_file.name}")
            st.info(f"📊 데이터 크기: {len(df):,}행 × {len(df.columns)}열")
            
        except Exception as e:
            st.error(f"❌ 파일 처리 오류: {str(e)}")
    
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
        
        st.session_state.analysis_results = analysis
        st.session_state.processed_data = df
    
    def render_home(self):
        """홈 화면 렌더링"""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ## 🌊 환경 데이터 분석의 새로운 기준
            
            Aqua-Analytics Premium은 수질, 대기질, 토양 데이터를 통합 분석하여 
            환경 관리에 필요한 인사이트를 제공합니다.
            
            ### ✨ 핵심 기능
            - **📊 실시간 모니터링**: 환경 데이터 실시간 추적
            - **🎯 기준치 관리**: 환경 기준 초과 시 즉시 알림
            - **📈 트렌드 분석**: 시계열 데이터 패턴 분석
            - **🔍 AI 인사이트**: 머신러닝 기반 예측 분석
            - **📋 자동 보고서**: 전문적인 분석 보고서 자동 생성
            """)
        
        with col2:
            st.markdown("### 📊 샘플 데이터")
            
            # 샘플 차트
            sample_data = pd.DataFrame({
                '날짜': pd.date_range('2024-01-01', periods=30),
                'pH': [7.2 + i*0.1 + (i%3)*0.2 for i in range(30)],
                '용존산소': [8.5 - i*0.05 + (i%4)*0.3 for i in range(30)],
                '탁도': [2.1 + i*0.02 + (i%5)*0.1 for i in range(30)]
            })
            
            fig = px.line(sample_data, x='날짜', y=['pH', '용존산소', '탁도'],
                         title="환경 데이터 트렌드 (샘플)")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    def render_data_upload(self):
        """데이터 업로드 화면 렌더링"""
        st.markdown("## 📊 데이터 업로드")
        
        if st.session_state.uploaded_data is not None:
            df = st.session_state.uploaded_data
            
            # 데이터 미리보기
            st.markdown("### 📋 데이터 미리보기")
            st.dataframe(df.head(10), use_container_width=True)
            
            # 기본 통계
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 데이터 수", f"{len(df):,}")
            with col2:
                st.metric("컬럼 수", len(df.columns))
            with col3:
                st.metric("결측값", st.session_state.analysis_results.get('missing_values', 0))
            with col4:
                st.metric("중복값", st.session_state.analysis_results.get('duplicate_rows', 0))
            
            # 데이터 타입 정보
            st.markdown("### 📈 데이터 타입 분석")
            col1, col2 = st.columns(2)
            
            with col1:
                numeric_cols = st.session_state.analysis_results.get('numeric_columns', [])
                st.info(f"**숫자형 컬럼** ({len(numeric_cols)}개)")
                if numeric_cols:
                    st.write(", ".join(numeric_cols[:5]) + ("..." if len(numeric_cols) > 5 else ""))
            
            with col2:
                categorical_cols = st.session_state.analysis_results.get('categorical_columns', [])
                st.info(f"**범주형 컬럼** ({len(categorical_cols)}개)")
                if categorical_cols:
                    st.write(", ".join(categorical_cols[:5]) + ("..." if len(categorical_cols) > 5 else ""))
        
        else:
            st.info("👈 사이드바에서 파일을 업로드해주세요.")
    
    def render_dashboard(self):
        """대시보드 화면 렌더링"""
        st.markdown("## 📈 인터랙티브 대시보드")
        
        if st.session_state.uploaded_data is not None:
            df = st.session_state.uploaded_data
            numeric_columns = st.session_state.analysis_results.get('numeric_columns', [])
            
            if numeric_columns:
                # 차트 설정
                col1, col2 = st.columns(2)
                
                with col1:
                    x_axis = st.selectbox("X축 선택", df.columns, key="dashboard_x")
                with col2:
                    y_axis = st.selectbox("Y축 선택", numeric_columns, key="dashboard_y")
                
                # 차트 생성
                if x_axis and y_axis:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # 산점도
                        fig_scatter = px.scatter(df, x=x_axis, y=y_axis, 
                                               title=f"{y_axis} vs {x_axis}")
                        st.plotly_chart(fig_scatter, use_container_width=True)
                    
                    with col2:
                        # 히스토그램
                        fig_hist = px.histogram(df, x=y_axis, 
                                              title=f"{y_axis} 분포")
                        st.plotly_chart(fig_hist, use_container_width=True)
                    
                    # 시계열 차트 (날짜 컬럼이 있는 경우)
                    date_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
                    if date_columns:
                        fig_line = px.line(df, x=date_columns[0], y=y_axis,
                                         title=f"{y_axis} 시계열 트렌드")
                        st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.warning("숫자형 데이터가 없습니다.")
        else:
            st.info("👈 먼저 데이터를 업로드해주세요.")
    
    def render_integrated_analysis(self):
        """통합 분석 화면 렌더링"""
        st.markdown("## 🔍 AI 기반 통합 분석")
        
        if st.session_state.uploaded_data is not None:
            df = st.session_state.uploaded_data
            
            # 데이터 품질 분석
            st.markdown("### 📊 데이터 품질 분석")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 데이터 수", f"{len(df):,}")
            with col2:
                missing_count = df.isnull().sum().sum()
                st.metric("결측값", missing_count)
            with col3:
                duplicate_count = df.duplicated().sum()
                st.metric("중복값", duplicate_count)
            with col4:
                completeness = ((len(df) * len(df.columns) - missing_count) / (len(df) * len(df.columns)) * 100)
                st.metric("완성도", f"{completeness:.1f}%")
            
            # 상관관계 분석
            numeric_df = df.select_dtypes(include=['number'])
            if len(numeric_df.columns) > 1:
                st.markdown("### 🔗 상관관계 분석")
                corr_matrix = numeric_df.corr()
                fig_heatmap = px.imshow(corr_matrix, 
                                      title="변수 간 상관관계",
                                      color_continuous_scale="RdBu",
                                      aspect="auto")
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # AI 인사이트 (시뮬레이션)
            st.markdown("### 🤖 AI 인사이트")
            insights = [
                "📈 데이터 트렌드가 상승세를 보이고 있습니다.",
                "⚠️ 일부 측정값이 기준치를 초과했습니다.",
                "🔍 계절적 패턴이 관찰됩니다.",
                "💡 데이터 품질이 양호합니다.",
                "📊 추가 모니터링이 권장됩니다."
            ]
            
            for insight in insights:
                st.info(insight)
        else:
            st.info("👈 먼저 데이터를 업로드해주세요.")
    
    def render_report_generation(self):
        """보고서 생성 화면 렌더링"""
        st.markdown("## 📋 자동 보고서 생성")
        
        if st.session_state.uploaded_data is not None:
            df = st.session_state.uploaded_data
            filename = st.session_state.get('filename', 'data')
            
            st.markdown("### 📊 분석 보고서")
            
            # 보고서 내용
            report_content = f"""
# 환경 데이터 분석 보고서

## 📋 기본 정보
- **파일명**: {filename}
- **분석 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **데이터 수**: {len(df):,}개
- **변수 수**: {len(df.columns)}개

## 📊 데이터 요약
{df.describe().to_string()}

## 🔍 데이터 품질
- **결측값**: {df.isnull().sum().sum()}개
- **중복값**: {df.duplicated().sum()}개
- **완성도**: {((len(df) * len(df.columns) - df.isnull().sum().sum()) / (len(df) * len(df.columns)) * 100):.1f}%

## 💡 주요 인사이트
- 데이터 품질이 양호합니다
- 추가 분석을 통한 심화 인사이트 도출 가능
- 정기적인 모니터링 권장

---
*Aqua-Analytics Premium에서 생성된 보고서입니다.*
            """
            
            st.markdown(report_content)
            
            # 다운로드 버튼
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📄 보고서 다운로드 (텍스트)",
                    data=report_content,
                    file_name=f"aqua_analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            
            with col2:
                # Excel 다운로드
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='원본데이터', index=False)
                    df.describe().to_excel(writer, sheet_name='통계요약')
                
                st.download_button(
                    label="📊 데이터 다운로드 (Excel)",
                    data=output.getvalue(),
                    file_name=f"aqua_analytics_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("👈 먼저 데이터를 업로드해주세요.")
    
    def run(self):
        """애플리케이션 실행"""
        self.render_header()
        selected_menu = self.render_sidebar()
        
        # 메뉴에 따른 화면 렌더링
        if selected_menu == "🏠 홈":
            self.render_home()
        elif selected_menu == "📊 데이터 업로드":
            self.render_data_upload()
        elif selected_menu == "📈 대시보드":
            self.render_dashboard()
        elif selected_menu == "🔍 통합 분석":
            self.render_integrated_analysis()
        elif selected_menu == "📋 보고서 생성":
            self.render_report_generation()
        
        # 푸터
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem;'>
            🧪 <strong>Aqua-Analytics Premium</strong> - Demo Version<br>
            실제 업무용은 로컬 서버 버전을 설치하세요<br>
            <a href='https://github.com/aqua-analytics/aqua-analytics' target='_blank'>GitHub Repository</a>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    app = AquaAnalyticsDemo()
    app.run()