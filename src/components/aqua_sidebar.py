"""
Aqua-Analytics 사이드바 네비게이션 시스템
미니멀하고 전문적인 디자인 적용
"""

import streamlit as st
from typing import Dict, Any, Optional
from pathlib import Path
import base64

class AquaSidebar:
    """Aqua-Analytics 브랜드 사이드바 컴포넌트"""
    
    def __init__(self):
        self.menu_items = [
            {
                'id': 'dashboard',
                'label': '대시보드',
                'icon': '📊',
                'page': '📊 처리 대기 파일',
                'active': True
            },
            {
                'id': 'reports',
                'label': '보고서 관리',
                'icon': '📄',
                'page': '📄 시험성적서 목록',
                'active': False
            },
            {
                'id': 'standards',
                'label': '시험 규격 관리',
                'icon': '🛡️',
                'page': '📋 규격 목록',
                'active': False
            },
            {
                'id': 'upload',
                'label': '파일 업로드',
                'icon': '☁️',
                'page': '📁 파일 업로드',
                'active': False
            }
        ]
        
        self.apply_custom_css()
    
    def apply_custom_css(self):
        """Aqua-Analytics 테마 CSS 적용"""
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* 전체 앱 폰트 적용 */
        .stApp {
            font-family: 'Inter', sans-serif;
        }
        
        /* 사이드바 스타일링 */
        .css-1d391kg {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        
        /* 메인 컨텐츠 배경 */
        .main .block-container {
            background-color: #f8fafc;
            padding-top: 2rem;
        }
        
        /* 브랜드 헤더 */
        .aqua-brand {
            display: flex;
            align-items: center;
            padding: 1.5rem 1rem;
            margin-bottom: 2rem;
            border-bottom: 1px solid #f1f5f9;
        }
        
        .aqua-logo {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
            border-radius: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 0.75rem;
            font-size: 1.25rem;
        }
        
        .aqua-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #1e293b;
            margin: 0;
        }
        
        /* 네비게이션 메뉴 */
        .nav-section {
            margin-bottom: 1.5rem;
        }
        
        .nav-section-title {
            font-size: 0.75rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.75rem;
            padding: 0 1rem;
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            margin: 0.25rem 0.5rem;
            border-radius: 0.5rem;
            color: #64748b;
            text-decoration: none;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        
        .nav-item:hover {
            background-color: #f1f5f9;
            color: #1e293b;
        }
        
        .nav-item.active {
            background-color: #f1f5f9;
            color: #1e293b;
            font-weight: 600;
        }
        
        .nav-item-icon {
            margin-right: 0.75rem;
            font-size: 1.25rem;
        }
        
        /* CTA 카드 */
        .cta-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 0.75rem;
            padding: 1rem;
            margin: 1rem 0.5rem;
        }
        
        .cta-title {
            font-weight: 600;
            font-size: 0.875rem;
            color: #1e293b;
            margin-bottom: 0.5rem;
        }
        
        .cta-description {
            font-size: 0.75rem;
            color: #64748b;
            margin-bottom: 1rem;
            line-height: 1.4;
        }
        
        .cta-button {
            width: 100%;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border: none;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .cta-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        
        /* 사용자 프로필 */
        .user-profile {
            display: flex;
            align-items: center;
            padding: 1rem;
            margin-top: auto;
            border-top: 1px solid #f1f5f9;
        }
        
        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            margin-right: 0.75rem;
        }
        
        .user-info {
            flex: 1;
        }
        
        .user-name {
            font-size: 0.875rem;
            font-weight: 600;
            color: #1e293b;
            margin: 0;
        }
        
        .user-role {
            font-size: 0.75rem;
            color: #64748b;
            margin: 0;
        }
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            .aqua-brand {
                padding: 1rem;
            }
            
            .nav-item {
                padding: 0.5rem 1rem;
            }
            
            .cta-card {
                margin: 0.5rem;
                padding: 0.75rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_brand_header(self):
        """브랜드 헤더 렌더링"""
        st.markdown("""
        <div class="aqua-brand">
            <div class="aqua-logo">💧</div>
            <h1 class="aqua-title">Aqua-Analytics</h1>
        </div>
        """, unsafe_allow_html=True)
    
    def render_navigation(self) -> str:
        """네비게이션 메뉴 렌더링"""
        st.markdown('<div class="nav-section-title">MENU</div>', unsafe_allow_html=True)
        
        # 현재 페이지 상태 확인
        if 'current_page' not in st.session_state:
            st.session_state.current_page = '📊 처리 대기 파일'
        
        selected_page = st.session_state.current_page
        
        # 메뉴 아이템 렌더링
        for item in self.menu_items:
            is_active = item['page'] == selected_page
            active_class = 'active' if is_active else ''
            
            # 클릭 가능한 메뉴 아이템
            if st.button(
                f"{item['icon']} {item['label']}", 
                key=f"nav_{item['id']}",
                help=f"{item['label']} 페이지로 이동"
            ):
                st.session_state.current_page = item['page']
                st.rerun()
        
        return st.session_state.current_page
    
    def render_cta_card(self):
        """파일 업로드 CTA 카드 렌더링"""
        st.markdown("""
        <div class="cta-card">
            <h3 class="cta-title">데이터 분석 리포트</h3>
            <p class="cta-description">새로운 파일을 업로드하여 분석을 시작하세요.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📁 파일 업로드", key="cta_upload", help="Excel 파일을 업로드하여 분석 시작"):
            st.session_state.current_page = '📁 파일 업로드'
            st.rerun()
    
    def render_user_profile(self):
        """사용자 프로필 영역 렌더링"""
        st.markdown("""
        <div class="user-profile">
            <div class="user-avatar">김</div>
            <div class="user-info">
                <p class="user-name">김민준</p>
                <p class="user-role">환경분석팀</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_project_status(self):
        """현재 프로젝트 상태 표시"""
        if 'active_file' in st.session_state and st.session_state.active_file:
            filename = st.session_state.active_file
            project_name = filename.replace('.xlsx', '').replace('.xls', '')
            
            st.markdown(f"""
            <div style="padding: 1rem; margin: 0.5rem; background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 0.5rem;">
                <div style="font-size: 0.75rem; color: #0369a1; font-weight: 600; margin-bottom: 0.25rem;">
                    현재 프로젝트
                </div>
                <div style="font-size: 0.875rem; color: #1e293b; font-weight: 500;">
                    {project_name}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_sidebar(self) -> str:
        """전체 사이드바 렌더링"""
        with st.sidebar:
            # 브랜드 헤더
            self.render_brand_header()
            
            # 현재 프로젝트 상태
            self.render_project_status()
            
            # 네비게이션 메뉴
            selected_page = self.render_navigation()
            
            # CTA 카드
            self.render_cta_card()
            
            # 사용자 프로필 (하단 고정)
            st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
            self.render_user_profile()
        
        return selected_page

# 전역 인스턴스
aqua_sidebar = AquaSidebar()