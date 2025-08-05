"""
🧪 Aqua-Analytics Premium - GitHub 데모 버전
환경 데이터 인사이트 플랫폼

GitHub 데모용 - 임시 저장, 세션 기반
실제 업무용은 로컬 서버 버전을 사용하세요.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import io
import base64

# 페이지 설정
st.set_page_config(
    page_title="Aqua-Analytics Premium - Demo",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데모 버전 알림
st.info("""
🌐 **GitHub 데모 버전**  
이것은 기능 체험용 데모입니다. 데이터는 세션 종료 시 삭제됩니다.  
실제 업무용은 로컬 서버 버전을 설치하여 사용하세요.
""")

# 메인 타이틀
st.title("🧪 Aqua-Analytics Premium")
st.markdown("### 환경 데이터 인사이트 플랫폼 - 데모 버전")

# 사이드바
with st.sidebar:
    st.header("📋 메뉴")
    menu = st.selectbox(
        "분석 메뉴 선택",
        ["🏠 홈", "📊 데이터 업로드", "📈 대시보드", "🔍 통합 분석", "📋 보고서"]
    )
    
    st.markdown("---")
    st.markdown("### 🌟 주요 기능")
    st.markdown("""
    - 실시간 데이터 분석
    - 인터랙티브 대시보드  
    - AI 기반 인사이트
    - 자동 보고서 생성
    - 기준치 모니터링
    """)
    
    st.markdown("---")
    st.markdown("### 🏢 로컬 서버 버전")
    st.markdown("""
    실제 업무용으로는 로컬 서버 버전을 설치하세요:
    
    1. GitHub에서 코드 다운로드
    2. `install_and_run.bat` 실행
    3. 사내 네트워크에서 접속
    """)

# 홈 화면
if menu == "🏠 홈":
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
        st.plotly_chart(fig, use_container_width=True)

# 데이터 업로드
elif menu == "📊 데이터 업로드":
    st.header("📊 데이터 업로드")
    
    st.markdown("""
    ### 지원 파일 형식
    - Excel (.xlsx, .xls)
    - CSV (.csv)
    - JSON (.json)
    """)
    
    uploaded_file = st.file_uploader(
        "파일을 선택하세요",
        type=['xlsx', 'xls', 'csv', 'json'],
        help="환경 데이터 파일을 업로드하세요"
    )
    
    if uploaded_file is not None:
        try:
            # 파일 형식에 따른 읽기
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                df = pd.read_json(uploaded_file)
            
            st.success(f"✅ 파일 업로드 성공: {uploaded_file.name}")
            
            # 데이터 미리보기
            st.subheader("📋 데이터 미리보기")
            st.dataframe(df.head(10))
            
            # 기본 통계
            st.subheader("📊 기본 통계")
            st.write(df.describe())
            
            # 세션에 저장 (데모용)
            st.session_state['uploaded_data'] = df
            st.session_state['filename'] = uploaded_file.name
            
        except Exception as e:
            st.error(f"❌ 파일 읽기 오류: {str(e)}")

# 대시보드
elif menu == "📈 대시보드":
    st.header("📈 인터랙티브 대시보드")
    
    if 'uploaded_data' in st.session_state:
        df = st.session_state['uploaded_data']
        
        # 컬럼 선택
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_columns:
            col1, col2 = st.columns(2)
            
            with col1:
                x_axis = st.selectbox("X축 선택", df.columns)
                
            with col2:
                y_axis = st.selectbox("Y축 선택", numeric_columns)
            
            # 차트 생성
            if x_axis and y_axis:
                fig = px.scatter(df, x=x_axis, y=y_axis, 
                               title=f"{y_axis} vs {x_axis}")
                st.plotly_chart(fig, use_container_width=True)
                
                # 시계열 차트 (날짜 컬럼이 있는 경우)
                date_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
                if date_columns:
                    fig_line = px.line(df, x=date_columns[0], y=y_axis,
                                     title=f"{y_axis} 시계열 트렌드")
                    st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("숫자형 데이터가 없습니다.")
    else:
        st.warning("먼저 데이터를 업로드해주세요.")

# 통합 분석
elif menu == "🔍 통합 분석":
    st.header("🔍 AI 기반 통합 분석")
    
    if 'uploaded_data' in st.session_state:
        df = st.session_state['uploaded_data']
        
        st.subheader("📊 데이터 품질 분석")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 데이터 수", len(df))
            
        with col2:
            missing_count = df.isnull().sum().sum()
            st.metric("결측값", missing_count)
            
        with col3:
            duplicate_count = df.duplicated().sum()
            st.metric("중복값", duplicate_count)
        
        # 상관관계 분석
        numeric_df = df.select_dtypes(include=['number'])
        if len(numeric_df.columns) > 1:
            st.subheader("🔗 상관관계 분석")
            corr_matrix = numeric_df.corr()
            fig_heatmap = px.imshow(corr_matrix, 
                                  title="변수 간 상관관계",
                                  color_continuous_scale="RdBu")
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # AI 인사이트 (시뮬레이션)
        st.subheader("🤖 AI 인사이트")
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
        st.warning("먼저 데이터를 업로드해주세요.")

# 보고서
elif menu == "📋 보고서":
    st.header("📋 자동 보고서 생성")
    
    if 'uploaded_data' in st.session_state:
        df = st.session_state['uploaded_data']
        filename = st.session_state.get('filename', 'data')
        
        st.subheader("📊 분석 보고서")
        
        # 보고서 내용
        report_content = f"""
        # 환경 데이터 분석 보고서
        
        ## 📋 기본 정보
        - 파일명: {filename}
        - 분석 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        - 데이터 수: {len(df):,}개
        - 변수 수: {len(df.columns)}개
        
        ## 📊 데이터 요약
        {df.describe().to_string()}
        
        ## 🔍 데이터 품질
        - 결측값: {df.isnull().sum().sum()}개
        - 중복값: {df.duplicated().sum()}개
        - 완성도: {((len(df) * len(df.columns) - df.isnull().sum().sum()) / (len(df) * len(df.columns)) * 100):.1f}%
        
        ## 💡 주요 인사이트
        - 데이터 품질이 양호합니다
        - 추가 분석을 통한 심화 인사이트 도출 가능
        - 정기적인 모니터링 권장
        
        ---
        *Aqua-Analytics Premium에서 생성된 보고서입니다.*
        """
        
        st.markdown(report_content)
        
        # 다운로드 버튼
        st.download_button(
            label="📄 보고서 다운로드 (텍스트)",
            data=report_content,
            file_name=f"aqua_analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
        
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
        st.warning("먼저 데이터를 업로드해주세요.")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🧪 Aqua-Analytics Premium - Demo Version<br>
    실제 업무용은 로컬 서버 버전을 설치하세요<br>
    <a href='https://github.com/aqua-analytics/aqua-analytics'>GitHub Repository</a>
</div>
""", unsafe_allow_html=True)