"""
Aqua-Analytics KPI 카드 시스템
호버 효과와 툴팁이 포함된 인터랙티브 KPI 카드
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from src.core.data_models import TestResult
import json

class AquaKPICards:
    """Aqua-Analytics KPI 카드 컴포넌트"""
    
    def __init__(self):
        self.apply_kpi_css()
    
    def apply_kpi_css(self):
        """KPI 카드 전용 CSS 스타일"""
        st.markdown("""
        <style>
        /* KPI 카드 컨테이너 */
        .kpi-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        /* KPI 카드 기본 스타일 */
        .kpi-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 0.75rem;
            padding: 1.5rem;
            position: relative;
            transition: all 0.3s ease;
            cursor: pointer;
            overflow: hidden;
        }
        
        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            border-color: #cbd5e1;
        }
        
        /* KPI 카드 헤더 */
        .kpi-header {
            display: flex;
            justify-content: between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }
        
        .kpi-title {
            font-size: 0.875rem;
            font-weight: 600;
            color: #64748b;
            margin: 0;
            flex: 1;
        }
        
        .kpi-icon {
            font-size: 1.25rem;
            opacity: 0.7;
        }
        
        /* KPI 값 */
        .kpi-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0.5rem 0;
            line-height: 1;
        }
        
        .kpi-value.primary {
            color: #1e293b;
        }
        
        .kpi-value.danger {
            color: #ef4444;
        }
        
        .kpi-value.warning {
            color: #f59e0b;
        }
        
        .kpi-value.success {
            color: #10b981;
        }
        
        /* KPI 부가 정보 */
        .kpi-subtitle {
            font-size: 0.875rem;
            color: #64748b;
            margin: 0;
            font-weight: 500;
        }
        
        .kpi-highlight {
            font-size: 0.75rem;
            color: #1e293b;
            font-weight: 600;
            margin-top: 0.5rem;
            padding: 0.25rem 0.5rem;
            background: #f1f5f9;
            border-radius: 0.375rem;
            display: inline-block;
        }
        
        /* 툴팁 스타일 */
        .kpi-tooltip {
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #1e293b;
            color: white;
            padding: 0.75rem;
            border-radius: 0.5rem;
            font-size: 0.75rem;
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 1000;
            margin-bottom: 0.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .kpi-tooltip::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 6px solid transparent;
            border-top-color: #1e293b;
        }
        
        .kpi-card:hover .kpi-tooltip {
            opacity: 1;
            visibility: visible;
        }
        
        /* 툴팁 리스트 스타일 */
        .tooltip-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .tooltip-list li {
            padding: 0.125rem 0;
            font-size: 0.75rem;
        }
        
        .tooltip-title {
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #ffffff;
        }
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            .kpi-container {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
            }
            
            .kpi-card {
                padding: 1rem;
            }
            
            .kpi-value {
                font-size: 2rem;
            }
            
            .kpi-tooltip {
                position: fixed;
                bottom: auto;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                white-space: normal;
                max-width: 280px;
            }
        }
        
        /* 로딩 애니메이션 */
        .kpi-loading {
            background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }
        
        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def generate_kpi_data(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """KPI 데이터 생성 (기존 로직 확장)"""
        if not test_results:
            return {
                'total_tests': 0,
                'non_conforming_tests': 0,
                'non_conforming_rate': 0.0,
                'total_samples': 0,
                'top_violation_item': None,
                'violation_details': []
            }
        
        total_tests = len(test_results)
        violations = [r for r in test_results if r.is_non_conforming()]
        non_conforming_tests = len(violations)
        non_conforming_rate = (non_conforming_tests / total_tests * 100) if total_tests > 0 else 0.0
        
        # 시료 개수 계산
        unique_samples = set(r.sample_name for r in test_results)
        total_samples = len(unique_samples)
        
        # 부적합 항목별 통계
        violation_by_item = {}
        for violation in violations:
            item = violation.test_item
            if item not in violation_by_item:
                violation_by_item[item] = {
                    'count': 0,
                    'samples': set(),
                    'max_excess': 0
                }
            violation_by_item[item]['count'] += 1
            violation_by_item[item]['samples'].add(violation.sample_name)
        
        # 가장 많은 부적합이 발생한 항목
        top_violation_item = None
        if violation_by_item:
            top_violation_item = max(violation_by_item.items(), key=lambda x: x[1]['count'])
        
        # 부적합 상세 정보 (Top 5)
        violation_details = sorted(
            [(item, data['count']) for item, data in violation_by_item.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_tests': total_tests,
            'non_conforming_tests': non_conforming_tests,
            'non_conforming_rate': round(non_conforming_rate, 1),
            'total_samples': total_samples,
            'top_violation_item': top_violation_item,
            'violation_details': violation_details,
            'unique_samples': len(unique_samples),
            'violation_by_item': violation_by_item
        }
    
    def render_kpi_card(self, title: str, value: str, icon: str, color: str = "primary", 
                       subtitle: str = None, highlight: str = None, tooltip_content: str = None):
        """개별 KPI 카드 렌더링"""
        tooltip_html = ""
        if tooltip_content:
            tooltip_html = f'<div class="kpi-tooltip">{tooltip_content}</div>'
        
        subtitle_html = ""
        if subtitle:
            subtitle_html = f'<p class="kpi-subtitle">{subtitle}</p>'
        
        highlight_html = ""
        if highlight:
            highlight_html = f'<div class="kpi-highlight">{highlight}</div>'
        
        card_html = f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <h3 class="kpi-title">{title}</h3>
                <div class="kpi-icon">{icon}</div>
            </div>
            <p class="kpi-value {color}">{value}</p>
            {subtitle_html}
            {highlight_html}
            {tooltip_html}
        </div>
        """
        
        return card_html
    
    def render_kpi_cards(self, test_results: List[TestResult]):
        """전체 KPI 카드 시스템 렌더링"""
        if not test_results:
            st.info("데이터를 업로드하면 KPI 지표가 표시됩니다.")
            return
        
        # KPI 데이터 생성
        kpi_data = self.generate_kpi_data(test_results)
        
        # 툴팁 내용 생성
        samples_tooltip = f"총 {kpi_data['unique_samples']}개 시료, {len(set(r.test_item for r in test_results))}개 항목"
        
        violations_tooltip_content = ""
        if kpi_data['violation_details']:
            violations_list = "<ul class='tooltip-list'>"
            for item, count in kpi_data['violation_details']:
                violations_list += f"<li>• {item}: {count}건</li>"
            violations_list += "</ul>"
            violations_tooltip_content = f"<div class='tooltip-title'>Top 5 부적합 항목</div>{violations_list}"
        
        rate_tooltip = f"{kpi_data['total_tests']}개 항목 중 {kpi_data['non_conforming_tests']}개 부적합"
        
        top_item_name = "해당 없음"
        top_item_tooltip = "부적합 항목이 없습니다"
        if kpi_data['top_violation_item']:
            item_name, item_data = kpi_data['top_violation_item']
            top_item_name = item_name[:15] + "..." if len(item_name) > 15 else item_name
            top_item_tooltip = f"가장 많은 부적합이 발생한 시험 항목입니다.<br>부적합 건수: {item_data['count']}건"
        
        # KPI 카드들 생성
        cards_html = f"""
        <div class="kpi-container">
            {self.render_kpi_card(
                title="총 시험 항목",
                value=f"{kpi_data['total_tests']}건",
                icon="📋",
                color="primary",
                tooltip_content=samples_tooltip
            )}
            {self.render_kpi_card(
                title="부적합 항목 수",
                value=f"{kpi_data['non_conforming_tests']}건",
                icon="⚠️",
                color="danger",
                tooltip_content=violations_tooltip_content
            )}
            {self.render_kpi_card(
                title="부적합률",
                value=f"{kpi_data['non_conforming_rate']}%",
                icon="📊",
                color="warning" if kpi_data['non_conforming_rate'] > 20 else "success",
                tooltip_content=rate_tooltip
            )}
            {self.render_kpi_card(
                title="주요 부적합 시험",
                value=top_item_name,
                icon="🔬",
                color="primary",
                tooltip_content=top_item_tooltip
            )}
        </div>
        """
        
        st.markdown(cards_html, unsafe_allow_html=True)
        
        return kpi_data

# 전역 인스턴스
aqua_kpi_cards = AquaKPICards()