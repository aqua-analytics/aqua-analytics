#!/usr/bin/env python3
"""
통합 분석 엔진 - 다중 파일 데이터 통합 분석
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import plotly.graph_objects as go
import plotly.express as px

class IntegratedAnalysisEngine:
    """통합 분석 엔진 클래스"""
    
    def __init__(self):
        # 데이터베이스 매니저는 런타임에 주입
        self.db_manager = None
    
    def set_db_manager(self, db_manager):
        """데이터베이스 매니저 설정"""
        self.db_manager = db_manager
    
    def get_period_presets(self) -> Dict[str, Tuple[datetime, datetime]]:
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
    
    def analyze_period(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """기간별 통합 분석 수행"""
        # 데이터베이스 매니저가 없으면 임시로 생성
        if not self.db_manager:
            from database_manager import db_manager
            self.db_manager = db_manager
        
        return self.db_manager.get_integrated_analysis_data(start_date, end_date)
    
    def create_conforming_chart(self, conforming_items: Dict[str, int]) -> go.Figure:
        """적합 항목 도넛 차트 생성"""
        if not conforming_items:
            # 빈 차트
            fig = go.Figure()
            fig.add_annotation(
                text="적합 항목 없음",
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
        sorted_items = sorted(conforming_items.items(), key=lambda x: x[1], reverse=True)[:10]
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
    
    def create_non_conforming_chart(self, non_conforming_items: Dict[str, int]) -> go.Figure:
        """부적합 항목 도넛 차트 생성"""
        if not non_conforming_items:
            # 빈 차트
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
                colors=px.colors.qualitative.Set1,
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
    
    def create_monthly_trend_chart(self, monthly_stats: Dict[str, Dict]) -> go.Figure:
        """월별 트렌드 차트 생성"""
        if not monthly_stats:
            fig = go.Figure()
            fig.add_annotation(
                text="데이터 없음",
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
        
        # 월별 데이터 정렬
        sorted_months = sorted(monthly_stats.keys())
        months = [datetime.strptime(month, "%Y-%m").strftime("%Y년 %m월") for month in sorted_months]
        
        total_tests = [monthly_stats[month]["tests"] for month in sorted_months]
        violations = [monthly_stats[month]["violations"] for month in sorted_months]
        violation_rates = [(v/t*100) if t > 0 else 0 for v, t in zip(violations, total_tests)]
        
        fig = go.Figure()
        
        # 총 시험 건수 막대 차트
        fig.add_trace(go.Bar(
            x=months,
            y=total_tests,
            name='총 시험 건수',
            marker_color='lightblue',
            yaxis='y',
            hovertemplate='<b>%{x}</b><br>총 시험: %{y}건<extra></extra>'
        ))
        
        # 부적합률 라인 차트
        fig.add_trace(go.Scatter(
            x=months,
            y=violation_rates,
            mode='lines+markers',
            name='부적합률 (%)',
            line=dict(color='red', width=3),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate='<b>%{x}</b><br>부적합률: %{y:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title="월별 시험 건수 및 부적합률 추이",
            xaxis_title="월",
            yaxis=dict(
                title="시험 건수",
                side="left"
            ),
            yaxis2=dict(
                title="부적합률 (%)",
                side="right",
                overlaying="y"
            ),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            hovermode='x unified'
        )
        
        return fig
    
    def create_monthly_trend_chart(self, monthly_stats: Dict[str, Dict]) -> go.Figure:
        """월별 트렌드 차트 생성"""
        if not monthly_stats:
            fig = go.Figure()
            fig.add_annotation(
                text="데이터 없음",
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
        
        # 월별 데이터 정렬
        sorted_months = sorted(monthly_stats.keys())
        months = [datetime.strptime(month, "%Y-%m").strftime("%Y년 %m월") for month in sorted_months]
        
        total_tests = [monthly_stats[month]["tests"] for month in sorted_months]
        violations = [monthly_stats[month]["violations"] for month in sorted_months]
        violation_rates = [(v/t*100) if t > 0 else 0 for v, t in zip(violations, total_tests)]
        
        fig = go.Figure()
        
        # 총 시험 건수 막대 차트
        fig.add_trace(go.Bar(
            x=months,
            y=total_tests,
            name='총 시험 건수',
            marker_color='lightblue',
            yaxis='y',
            hovertemplate='<b>%{x}</b><br>총 시험: %{y}건<extra></extra>'
        ))
        
        # 부적합률 라인 차트
        fig.add_trace(go.Scatter(
            x=months,
            y=violation_rates,
            mode='lines+markers',
            name='부적합률 (%)',
            line=dict(color='red', width=3),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate='<b>%{x}</b><br>부적합률: %{y:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title="월별 시험 건수 및 부적합률 추이",
            xaxis_title="월",
            yaxis=dict(
                title="시험 건수",
                side="left"
            ),
            yaxis2=dict(
                title="부적합률 (%)",
                side="right",
                overlaying="y"
            ),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            hovermode='x unified'
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
            fig.update_layout(
                height=300,
                showlegend=False,
                margin=dict(t=20, b=20, l=20, r=20)
            )
            return fig
        
        # 실험별 오염 농도 데이터 수집
        contamination_data = []
        
        for file_record in files_data:
            try:
                if not isinstance(file_record, dict):
                    continue
                    
                test_results = file_record.get("test_results", [])
                if not isinstance(test_results, list):
                    continue
                
                for result in test_results:
                    try:
                        if not isinstance(result, dict):
                            continue
                            
                        # 부적합 항목만 처리
                        is_non_conforming = result.get("is_non_conforming", False)
                        if isinstance(is_non_conforming, str):
                            is_non_conforming = is_non_conforming.lower() in ['true', '1', 'yes', '부적합']
                        elif not isinstance(is_non_conforming, bool):
                            standard_excess = result.get("standard_excess", "적합")
                            is_non_conforming = standard_excess == "부적합"
                        
                        if is_non_conforming:
                            test_item = result.get("test_item", "")
                            test_value = result.get("test_value", "")
                            
                            # 숫자 값 추출 시도
                            try:
                                if isinstance(test_value, (int, float)):
                                    value = float(test_value)
                                elif isinstance(test_value, str):
                                    # 문자열에서 숫자 추출
                                    import re
                                    numbers = re.findall(r'-?\d+\.?\d*', test_value)
                                    if numbers:
                                        value = float(numbers[0])
                                    else:
                                        continue
                                else:
                                    continue
                                
                                contamination_data.append({
                                    'test_item': test_item,
                                    'value': value,
                                    'sample': result.get("sample_name", "")
                                })
                            except (ValueError, TypeError):
                                continue
                                
                    except Exception:
                        continue
            except Exception:
                continue
        
        if not contamination_data:
            fig = go.Figure()
            fig.add_annotation(
                text="부적합 농도 데이터 없음",
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
        
        # 시험 항목별 농도 분포 히스토그램
        fig = go.Figure()
        
        # 시험 항목별로 그룹화
        test_items = {}
        for data in contamination_data:
            item = data['test_item']
            if item not in test_items:
                test_items[item] = []
            test_items[item].append(data['value'])
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
        
        for i, (item, values) in enumerate(test_items.items()):
            if len(values) > 0:
                fig.add_trace(go.Histogram(
                    x=values,
                    name=item,
                    marker_color=colors[i % len(colors)],
                    opacity=0.7,
                    nbinsx=10
                ))
        
        fig.update_layout(
            title="실험별 부적합 농도 분포",
            xaxis_title="농도 값",
            yaxis_title="빈도",
            height=300,
            margin=dict(t=50, b=50, l=50, r=50),
            barmode='overlay',
            showlegend=True
        )
        
        return fig
    
    def create_file_trend_chart(self, files_data: List[Dict]) -> go.Figure:
        """시험/시료별 추이 차트 생성"""
        if not files_data:
            fig = go.Figure()
            fig.add_annotation(
                text="데이터 없음",
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
        
        # 파일별 부적합률과 평균 농도 계산
        file_stats = []
        
        for file_record in files_data:
            try:
                if not isinstance(file_record, dict):
                    continue
                
                filename = file_record.get("filename", "")
                upload_time = file_record.get("upload_time", "")
                test_results = file_record.get("test_results", [])
                
                if not isinstance(test_results, list) or not test_results:
                    continue
                
                total_tests = len(test_results)
                violations = 0
                total_concentration = 0
                concentration_count = 0
                
                for result in test_results:
                    try:
                        if not isinstance(result, dict):
                            continue
                        
                        # 부적합 여부 확인
                        is_non_conforming = result.get("is_non_conforming", False)
                        if isinstance(is_non_conforming, str):
                            is_non_conforming = is_non_conforming.lower() in ['true', '1', 'yes', '부적합']
                        elif not isinstance(is_non_conforming, bool):
                            standard_excess = result.get("standard_excess", "적합")
                            is_non_conforming = standard_excess == "부적합"
                        
                        if is_non_conforming:
                            violations += 1
                            
                            # 농도 값 추출
                            test_value = result.get("test_value", "")
                            try:
                                if isinstance(test_value, (int, float)):
                                    total_concentration += float(test_value)
                                    concentration_count += 1
                                elif isinstance(test_value, str):
                                    import re
                                    numbers = re.findall(r'-?\d+\.?\d*', test_value)
                                    if numbers:
                                        total_concentration += float(numbers[0])
                                        concentration_count += 1
                            except (ValueError, TypeError):
                                pass
                    except Exception:
                        continue
                
                violation_rate = (violations / total_tests * 100) if total_tests > 0 else 0
                avg_concentration = (total_concentration / concentration_count) if concentration_count > 0 else 0
                
                # 파일명에서 날짜 추출 시도
                try:
                    if upload_time:
                        upload_date = datetime.fromisoformat(upload_time)
                        date_str = upload_date.strftime("%m/%d")
                    else:
                        date_str = filename[:10] if len(filename) >= 10 else filename
                except:
                    date_str = filename[:10] if len(filename) >= 10 else filename
                
                file_stats.append({
                    'filename': filename,
                    'date': date_str,
                    'violation_rate': violation_rate,
                    'avg_concentration': avg_concentration,
                    'total_tests': total_tests,
                    'violations': violations
                })
                
            except Exception:
                continue
        
        if not file_stats:
            fig = go.Figure()
            fig.add_annotation(
                text="파일별 통계 데이터 없음",
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
        
        # 날짜순 정렬
        file_stats.sort(key=lambda x: x['date'])
        
        dates = [stat['date'] for stat in file_stats]
        violation_rates = [stat['violation_rate'] for stat in file_stats]
        avg_concentrations = [stat['avg_concentration'] for stat in file_stats]
        
        fig = go.Figure()
        
        # 부적합률 라인 차트
        fig.add_trace(go.Scatter(
            x=dates,
            y=violation_rates,
            mode='lines+markers',
            name='부적합률 (%)',
            line=dict(color='red', width=3),
            marker=dict(size=8),
            yaxis='y',
            hovertemplate='<b>%{x}</b><br>부적합률: %{y:.1f}%<extra></extra>'
        ))
        
        # 평균 농도 막대 차트 (보조 축)
        if any(c > 0 for c in avg_concentrations):
            fig.add_trace(go.Bar(
                x=dates,
                y=avg_concentrations,
                name='평균 농도',
                marker_color='lightblue',
                opacity=0.6,
                yaxis='y2',
                hovertemplate='<b>%{x}</b><br>평균 농도: %{y:.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            title="파일별 부적합률 및 농도 추이",
            xaxis_title="파일/날짜",
            yaxis=dict(title="부적합률 (%)", side="left"),
            yaxis2=dict(title="평균 농도", side="right", overlaying="y"),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            hovermode='x unified'
        )
        
        return fig
    
    def generate_integrated_report_html(self, analysis_data: Dict[str, Any], 
                                      start_date: datetime, end_date: datetime) -> str:
        """통합 분석 보고서 HTML 생성"""
        period_str = f"{start_date.strftime('%Y년 %m월 %d일')} ~ {end_date.strftime('%Y년 %m월 %d일')}"
        
        # 상위 부적합 항목 테이블 생성
        violation_table_rows = ""
        top_violation_items = analysis_data.get("top_violation_items", [])
        total_violations = analysis_data.get("total_violations", 0)
        
        if top_violation_items and isinstance(top_violation_items, list):
            for i, item_data in enumerate(top_violation_items[:10], 1):
                if isinstance(item_data, (list, tuple)) and len(item_data) >= 2:
                    item, count = item_data[0], item_data[1]
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
            for i, client_data in enumerate(top_clients, 1):
                if isinstance(client_data, (list, tuple)) and len(client_data) >= 2:
                    client, count = client_data[0], client_data[1]
                    client_table_rows += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{client}</td>
                        <td>{count}건</td>
                    </tr>
                    """
        
        if not client_table_rows:
            client_table_rows = "<tr><td colspan='3'>의뢰 기관 정보가 없습니다.</td></tr>"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Aqua-Analytics 통합 분석 보고서</title>
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
                .table-container {{
                    overflow-x: auto;
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
                    <p>통합 분석 보고서</p>
                    <p><strong>분석 기간:</strong> {period_str}</p>
                </div>
                
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="kpi-value">{analysis_data.get('total_files', 0)}</div>
                        <div class="kpi-label">총 분석 파일 수</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{analysis_data.get('total_tests', 0)}</div>
                        <div class="kpi-label">총 시험 항목 수</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{analysis_data.get('total_violations', 0)}</div>
                        <div class="kpi-label">부적합 항목 수</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-value">{analysis_data.get('violation_rate', 0)}%</div>
                        <div class="kpi-label">부적합률</div>
                    </div>
                </div>
                
                <div class="summary-box">
                    <h3>📋 분석 요약</h3>
                    <p>{analysis_data.get('summary_text', '분석 요약 정보가 없습니다.')}</p>
                </div>
                
                <div class="section">
                    <h2>🔍 주요 부적합 항목</h2>
                    <div class="table-container">
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
                </div>
                
                <div class="section">
                    <h2>🏢 주요 의뢰 기관</h2>
                    <div class="table-container">
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
                    <p>본 보고서는 Aqua-Analytics 시스템에서 자동 생성되었습니다.</p>
                    <p>생성 일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content

# 전역 인스턴스 생성
integrated_analysis_engine = IntegratedAnalysisEngine()