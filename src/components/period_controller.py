#!/usr/bin/env python3
"""
기간 설정 컨트롤러 - 통합 분석용 기간 선택 UI
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple, Optional

class PeriodController:
    """기간 설정 컨트롤러 클래스"""
    
    def __init__(self):
        self.preset_periods = self._get_preset_periods()
    
    def _get_preset_periods(self) -> dict:
        """사전 정의된 기간 반환"""
        now = datetime.now()
        today = now.replace(hour=23, minute=59, second=59)
        
        return {
            "오늘": (now.replace(hour=0, minute=0, second=0), today),
            "최근 7일": (now - timedelta(days=7), today),
            "최근 1개월": (now - timedelta(days=30), today),
            "최근 3개월": (now - timedelta(days=90), today),
            "올해": (datetime(now.year, 1, 1), today)
        }
    
    def render_period_selector(self) -> Tuple[datetime, datetime]:
        """기간 선택 UI 렌더링"""
        
        # 기간 설정 카드 스타일
        st.markdown("""
        <style>
        .period-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .period-header {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .preset-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 16px;
        }
        
        .preset-btn {
            padding: 8px 16px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            background: white;
            color: #374151;
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .preset-btn:hover {
            background: #f3f4f6;
            border-color: #9ca3af;
        }
        
        .preset-btn.active {
            background: #3b82f6;
            color: white;
            border-color: #3b82f6;
        }
        
        .custom-period {
            display: flex;
            align-items: center;
            gap: 12px;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
        }
        
        .period-display {
            background: #f0f9ff;
            border: 1px solid #bae6fd;
            border-radius: 8px;
            padding: 12px 16px;
            margin-top: 16px;
            font-size: 0.875rem;
            color: #0c4a6e;
            font-weight: 500;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 기간 설정 카드
        st.markdown("""
        <div class="period-card">
            <div class="period-header">
                📅 기간 설정
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 세션 상태 초기화
        if 'selected_period' not in st.session_state:
            st.session_state.selected_period = "최근 1개월"
        if 'custom_start_date' not in st.session_state:
            st.session_state.custom_start_date = datetime.now() - timedelta(days=30)
        if 'custom_end_date' not in st.session_state:
            st.session_state.custom_end_date = datetime.now()
        
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
            st.markdown("<br>", unsafe_allow_html=True)  # 버튼 정렬을 위한 공간
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
            start_date, end_date = self.preset_periods[st.session_state.selected_period]
        
        # 현재 선택된 기간 표시
        period_display = f"**선택된 기간:** {start_date.strftime('%Y년 %m월 %d일')} ~ {end_date.strftime('%Y년 %m월 %d일')}"
        
        st.markdown(f"""
        <div class="period-display">
            {period_display}
        </div>
        """, unsafe_allow_html=True)
        
        return start_date, end_date
    
    def get_current_period(self) -> Tuple[datetime, datetime]:
        """현재 선택된 기간 반환"""
        if 'selected_period' not in st.session_state:
            st.session_state.selected_period = "최근 1개월"
        
        if st.session_state.selected_period == "사용자 지정":
            return st.session_state.custom_start_date, st.session_state.custom_end_date
        else:
            return self.preset_periods[st.session_state.selected_period]

# 전역 인스턴스
period_controller = PeriodController()