ㅌ"""
시각화 차트 시스템 구현
ApexCharts를 사용한 부적합 통계 차트 생성
"""

import json
from typing import Dict, List, Any, Optional
from collections import Counter
from src.core.data_models import TestResult


class ChartSystem:
    """ApexCharts 기반 시각화 차트 시스템"""
    
    def __init__(self):
        # ApexCharts 기본 설정 및 테마 구성
        self.chart_config = {
            'theme': {
                'mode': 'light',
                'palette': 'palette1'
            },
            'colors': [
                '#ef4444',  # red-500 (부적합 주색상)
                '#f59e0b',  # amber-500
                '#10b981',  # emerald-500
                '#3b82f6',  # blue-500
                '#8b5cf6',  # violet-500
                '#ec4899',  # pink-500
                '#06b6d4',  # cyan-500
                '#84cc16'   # lime-500
            ],
            'animations': {
                'enabled': True,
                'easing': 'easeinout',
                'speed': 1200,
                'animateGradually': {
                    'enabled': True,
                    'delay': 200
                },
                'dynamicAnimation': {
                    'enabled': True,
                    'speed': 500
                }
            },
            'responsive_breakpoints': [
                {
                    'breakpoint': 480,
                    'options': {
                        'chart': {
                            'height': 300
                        },
                        'legend': {
                            'position': 'bottom'
                        }
                    }
                },
                {
                    'breakpoint': 768,
                    'options': {
                        'chart': {
                            'height': 350
                        }
                    }
                }
            ],
            'font_family': 'Noto Sans KR, sans-serif'
        }
    
    def generate_non_conforming_donut_chart(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """
        부적합 항목별 분포 도넛 차트 데이터 생성 (향상된 버전)
        
        Args:
            test_results: 시험 결과 리스트
            
        Returns:
            ApexCharts 도넛 차트 설정 딕셔너리
        """
        # 부적합 항목만 필터링
        non_conforming_items = [
            result for result in test_results 
            if result.is_non_conforming()
        ]
        
        if not non_conforming_items:
            return self._get_empty_donut_chart()
        
        # 시험항목별 부적합 개수 계산
        item_counts = Counter([result.test_item for result in non_conforming_items])
        
        # 상위 8개 항목만 표시 (나머지는 '기타'로 그룹화)
        top_items = dict(item_counts.most_common(8))
        other_count = sum(item_counts.values()) - sum(top_items.values())
        
        if other_count > 0:
            top_items['기타'] = other_count
        
        # 라벨 길이 제한 (차트 가독성 향상)
        labels = []
        for label in top_items.keys():
            if len(label) > 18:
                labels.append(label[:15] + '...')
            else:
                labels.append(label)
        
        series = list(top_items.values())
        total_violations = sum(series)
        
        chart_config = {
            'chart': {
                'type': 'donut',
                'height': 380,
                'fontFamily': self.chart_config['font_family'],
                'animations': {
                    'enabled': True,
                    'easing': 'easeinout',
                    'speed': 1500,
                    'animateGradually': {
                        'enabled': True,
                        'delay': 300
                    },
                    'dynamicAnimation': {
                        'enabled': True,
                        'speed': 800
                    }
                },
                'toolbar': {
                    'show': False
                },
                'dropShadow': {
                    'enabled': True,
                    'top': 3,
                    'left': 3,
                    'blur': 6,
                    'opacity': 0.15
                }
            },
            'series': series,
            'labels': labels,
            'colors': self.chart_config['colors'][:len(labels)],
            'plotOptions': {
                'pie': {
                    'donut': {
                        'size': '68%',
                        'labels': {
                            'show': True,
                            'name': {
                                'show': True,
                                'fontSize': '15px',
                                'fontWeight': 600,
                                'color': '#374151',
                                'offsetY': -12
                            },
                            'value': {
                                'show': True,
                                'fontSize': '26px',
                                'fontWeight': 700,
                                'color': '#ef4444',
                                'offsetY': 12,
                                'formatter': 'function(val) { return val + "건"; }'
                            },
                            'total': {
                                'show': True,
                                'showAlways': True,
                                'label': '총 부적합',
                                'fontSize': '13px',
                                'fontWeight': 600,
                                'color': '#6b7280',
                                'formatter': f'function(w) {{ return "{total_violations}건"; }}'
                            }
                        }
                    },
                    'expandOnClick': True,
                    'customScale': 1.15,
                    'offsetX': 0,
                    'offsetY': 0
                }
            },
            'dataLabels': {
                'enabled': True,
                'formatter': 'function(val, opts) { return val.toFixed(1) + "%"; }',
                'style': {
                    'fontSize': '11px',
                    'fontWeight': 'bold',
                    'colors': ['#ffffff']
                },
                'dropShadow': {
                    'enabled': True,
                    'top': 1,
                    'left': 1,
                    'blur': 2,
                    'opacity': 0.9
                }
            },
            'legend': {
                'position': 'bottom',
                'fontSize': '11px',
                'fontFamily': self.chart_config['font_family'],
                'itemMargin': {
                    'horizontal': 10,
                    'vertical': 5
                },
                'markers': {
                    'width': 10,
                    'height': 10,
                    'radius': 5
                }
            },
            'tooltip': {
                'enabled': True,
                'style': {
                    'fontSize': '12px',
                    'fontFamily': self.chart_config['font_family']
                },
                'y': {
                    'formatter': 'function(val) { return val + "건"; }'
                }
            },
            'states': {
                'hover': {
                    'filter': {
                        'type': 'lighten',
                        'value': 0.1
                    }
                },
                'active': {
                    'allowMultipleDataPointsSelection': False,
                    'filter': {
                        'type': 'darken',
                        'value': 0.25
                    }
                }
            },
            'stroke': {
                'show': True,
                'curve': 'smooth',
                'lineCap': 'butt',
                'colors': ['#ffffff'],
                'width': 2,
                'dashArray': 0
            },
            'responsive': self.chart_config['responsive_breakpoints']
        }
        
        return chart_config
    
    def generate_non_conforming_bar_chart(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """
        부적합 항목별 비율 수평 막대 차트 데이터 생성
        
        Args:
            test_results: 시험 결과 리스트
            
        Returns:
            ApexCharts 수평 막대 차트 설정 딕셔너리
        """
        if not test_results:
            return self._get_empty_bar_chart()
        
        # 시험항목별 전체 개수와 부적합 개수 계산
        item_stats = {}
        for result in test_results:
            item = result.test_item
            if item not in item_stats:
                item_stats[item] = {'total': 0, 'non_conforming': 0}
            
            item_stats[item]['total'] += 1
            if result.is_non_conforming():
                item_stats[item]['non_conforming'] += 1
        
        # 부적합 비율 계산 및 정렬
        item_ratios = []
        for item, stats in item_stats.items():
            if stats['non_conforming'] > 0:  # 부적합이 있는 항목만
                ratio = (stats['non_conforming'] / stats['total']) * 100
                item_ratios.append({
                    'item': item,
                    'ratio': ratio,
                    'non_conforming': stats['non_conforming'],
                    'total': stats['total']
                })
        
        # 비율 기준 내림차순 정렬, 상위 8개만
        item_ratios.sort(key=lambda x: x['ratio'], reverse=True)
        item_ratios = item_ratios[:8]
        
        if not item_ratios:
            return self._get_empty_bar_chart()
        
        # 라벨 길이 제한 (차트 가독성 향상)
        categories = []
        for item_data in item_ratios:
            item = item_data['item']
            if len(item) > 25:
                categories.append(item[:22] + '...')
            else:
                categories.append(item)
        
        data = [round(item['ratio'], 1) for item in item_ratios]
        
        chart_config = {
            'chart': {
                'type': 'bar',
                'height': 420,
                'fontFamily': self.chart_config['font_family'],
                'animations': {
                    'enabled': True,
                    'easing': 'easeinout',
                    'speed': 1800,
                    'animateGradually': {
                        'enabled': True,
                        'delay': 400
                    },
                    'dynamicAnimation': {
                        'enabled': True,
                        'speed': 1000
                    }
                },
                'toolbar': {
                    'show': False
                },
                'dropShadow': {
                    'enabled': True,
                    'top': 3,
                    'left': 3,
                    'blur': 6,
                    'opacity': 0.15
                }
            },
            'plotOptions': {
                'bar': {
                    'horizontal': True,
                    'borderRadius': 8,
                    'borderRadiusApplication': 'end',
                    'barHeight': '65%',
                    'dataLabels': {
                        'position': 'center'
                    },
                    'distributed': False,
                    'rangeBarOverlap': True,
                    'rangeBarGroupRows': False
                }
            },
            'dataLabels': {
                'enabled': True,
                'formatter': 'function(val) { return val + "%"; }',
                'offsetX': 0,
                'style': {
                    'fontSize': '11px',
                    'fontWeight': 'bold',
                    'colors': ['#ffffff']
                },
                'dropShadow': {
                    'enabled': True,
                    'top': 1,
                    'left': 1,
                    'blur': 2,
                    'opacity': 0.9
                }
            },
            'series': [{
                'name': '부적합 비율',
                'data': data
            }],
            'xaxis': {
                'categories': categories,
                'labels': {
                    'style': {
                        'fontSize': '11px',
                        'fontFamily': self.chart_config['font_family']
                    },
                    'formatter': 'function(val) { return val + "%"; }'
                },
                'axisBorder': {
                    'show': True,
                    'color': '#e5e7eb'
                },
                'axisTicks': {
                    'show': True,
                    'color': '#e5e7eb'
                }
            },
            'yaxis': {
                'labels': {
                    'style': {
                        'fontSize': '11px',
                        'fontFamily': self.chart_config['font_family'],
                        'colors': ['#374151']
                    },
                    'maxWidth': 150
                }
            },
            'colors': ['#ef4444'],
            'fill': {
                'type': 'gradient',
                'gradient': {
                    'shade': 'light',
                    'type': 'horizontal',
                    'shadeIntensity': 0.5,
                    'gradientToColors': ['#fca5a5'],
                    'inverseColors': False,
                    'opacityFrom': 1.0,
                    'opacityTo': 0.85,
                    'stops': [0, 30, 70, 100],
                    'colorStops': [
                        {
                            'offset': 0,
                            'color': '#dc2626',
                            'opacity': 1
                        },
                        {
                            'offset': 30,
                            'color': '#ef4444',
                            'opacity': 0.95
                        },
                        {
                            'offset': 70,
                            'color': '#f87171',
                            'opacity': 0.9
                        },
                        {
                            'offset': 100,
                            'color': '#fca5a5',
                            'opacity': 0.85
                        }
                    ]
                }
            },
            'tooltip': {
                'enabled': True,
                'style': {
                    'fontSize': '12px',
                    'fontFamily': self.chart_config['font_family']
                },
                'y': {
                    'formatter': 'function(val, opts) { return val + "%"; }'
                }
            },
            'grid': {
                'show': True,
                'borderColor': '#e5e7eb',
                'strokeDashArray': 3,
                'position': 'back',
                'xaxis': {
                    'lines': {
                        'show': True
                    }
                },
                'yaxis': {
                    'lines': {
                        'show': False
                    }
                },
                'row': {
                    'colors': ['transparent', '#f9fafb'],
                    'opacity': 0.5
                },
                'padding': {
                    'top': 0,
                    'right': 0,
                    'bottom': 0,
                    'left': 0
                }
            },
            'states': {
                'hover': {
                    'filter': {
                        'type': 'lighten',
                        'value': 0.08
                    }
                },
                'active': {
                    'allowMultipleDataPointsSelection': False,
                    'filter': {
                        'type': 'darken',
                        'value': 0.15
                    }
                }
            },
            'stroke': {
                'show': True,
                'width': 1,
                'colors': ['transparent']
            },
            'responsive': self.chart_config['responsive_breakpoints']
        }
        
        return chart_config
    
    def update_chart_data(self, chart_id: str, test_results: List[TestResult]) -> Dict[str, Any]:
        """
        차트 데이터 동적 업데이트를 위한 설정 반환
        
        Args:
            chart_id: 차트 식별자 ('donut' 또는 'bar')
            test_results: 시험 결과 리스트
            
        Returns:
            업데이트용 차트 데이터
        """
        if chart_id == 'donut':
            return self.generate_non_conforming_donut_chart(test_results)
        elif chart_id == 'bar':
            return self.generate_non_conforming_bar_chart(test_results)
        else:
            raise ValueError(f"Unknown chart_id: {chart_id}")
    
    def get_chart_update_script(self, chart_id: str, test_results: List[TestResult]) -> str:
        """
        차트 업데이트를 위한 JavaScript 스크립트 생성
        
        Args:
            chart_id: 차트 식별자 ('donut' 또는 'bar')
            test_results: 시험 결과 리스트
            
        Returns:
            차트 업데이트 JavaScript 코드
        """
        try:
            chart_config = self.update_chart_data(chart_id, test_results)
            
            if chart_id == 'donut':
                return f"""
                if (window.donutChart) {{
                    window.donutChart.updateSeries({json.dumps(chart_config['series'])});
                    window.donutChart.updateOptions({{
                        labels: {json.dumps(chart_config['labels'], ensure_ascii=False)},
                        plotOptions: {{
                            pie: {{
                                donut: {{
                                    labels: {{
                                        total: {{
                                            formatter: function(w) {{ 
                                                return "{sum(chart_config['series'])}건"; 
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }});
                }}
                """
            elif chart_id == 'bar':
                return f"""
                if (window.barChart) {{
                    window.barChart.updateSeries([{{
                        name: '부적합 비율',
                        data: {json.dumps(chart_config['series'][0]['data'])}
                    }}]);
                    window.barChart.updateOptions({{
                        xaxis: {{
                            categories: {json.dumps(chart_config['xaxis']['categories'], ensure_ascii=False)}
                        }}
                    }});
                }}
                """
            else:
                return ""
        except Exception:
            return ""
    
    def update_charts_with_animation(self, test_results: List[TestResult]) -> str:
        """
        애니메이션과 함께 차트를 업데이트하는 JavaScript 함수 생성
        
        Args:
            test_results: 시험 결과 리스트
            
        Returns:
            애니메이션 업데이트 JavaScript 코드
        """
        donut_update = self.get_chart_update_script('donut', test_results)
        bar_update = self.get_chart_update_script('bar', test_results)
        
        return f"""
        // 애니메이션과 함께 차트 업데이트
        function updateChartsWithAnimation() {{
            // 로딩 표시
            showChartLoading();
            
            // 차트 페이드 아웃 효과
            fadeOutCharts();
            
            setTimeout(() => {{
                // 차트 데이터 업데이트
                {donut_update}
                {bar_update}
                
                // 차트 페이드 인 효과
                setTimeout(() => {{
                    fadeInCharts();
                    hideChartLoading();
                    showUpdateSuccess();
                }}, 800);
            }}, 300);
        }}

        // 차트 페이드 아웃 효과
        function fadeOutCharts() {{
            const chartContainers = document.querySelectorAll('.chart-container');
            chartContainers.forEach(container => {{
                container.style.transition = 'opacity 0.3s ease-out';
                container.style.opacity = '0.3';
            }});
        }}

        // 차트 페이드 인 효과
        function fadeInCharts() {{
            const chartContainers = document.querySelectorAll('.chart-container');
            chartContainers.forEach(container => {{
                container.style.transition = 'opacity 0.5s ease-in';
                container.style.opacity = '1';
            }});
        }}

        // 로딩 표시 함수
        function showChartLoading() {{
            const chartCards = document.querySelectorAll('.chart-card');
            chartCards.forEach(card => {{
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'chart-loading-overlay';
                loadingDiv.innerHTML = \`
                    <div class="flex items-center justify-center h-full">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500"></div>
                        <span class="ml-2 text-slate-600">업데이트 중...</span>
                    </div>
                \`;
                loadingDiv.style.cssText = \`
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(255, 255, 255, 0.9);
                    z-index: 10;
                    border-radius: 0.75rem;
                \`;
                card.style.position = 'relative';
                card.appendChild(loadingDiv);
            }});
        }}

        // 로딩 숨김 함수
        function hideChartLoading() {{
            const loadingOverlays = document.querySelectorAll('.chart-loading-overlay');
            loadingOverlays.forEach(overlay => {{
                overlay.style.transition = 'opacity 0.3s ease-out';
                overlay.style.opacity = '0';
                setTimeout(() => {{
                    if (overlay.parentNode) {{
                        overlay.parentNode.removeChild(overlay);
                    }}
                }}, 300);
            }});
        }}

        // 업데이트 성공 메시지
        function showUpdateSuccess() {{
            const successDiv = document.createElement('div');
            successDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
            successDiv.innerHTML = '차트가 성공적으로 업데이트되었습니다.';
            document.body.appendChild(successDiv);
            
            setTimeout(() => {{
                successDiv.style.transition = 'opacity 0.3s ease-out';
                successDiv.style.opacity = '0';
                setTimeout(() => {{
                    if (successDiv.parentNode) {{
                        successDiv.parentNode.removeChild(successDiv);
                    }}
                }}, 300);
            }}, 2000);
        }}
        """
    
    def generate_enhanced_chart_interactions(self) -> str:
        """
        향상된 차트 인터랙션 기능 JavaScript 생성
        
        Returns:
            인터랙션 JavaScript 코드
        """
        return """
        // 향상된 차트 인터랙션 초기화
        function initializeEnhancedChartInteractions() {
            // 차트 호버 효과 강화
            enhanceChartHoverEffects();
            
            // 차트 클릭 이벤트 처리
            setupChartClickEvents();
            
            // 차트 내보내기 기능
            setupChartExportFeatures();
        }

        // 차트 호버 효과 강화
        function enhanceChartHoverEffects() {
            const chartCards = document.querySelectorAll('.chart-card');
            chartCards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-4px)';
                    this.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.1)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                    this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
                });
            });
        }

        // 차트 클릭 이벤트 설정
        function setupChartClickEvents() {
            // 도넛 차트 클릭 이벤트
            if (window.donutChart) {
                window.donutChart.addEventListener('dataPointSelection', function(event, chartContext, config) {
                    const selectedIndex = config.dataPointIndex;
                    const selectedLabel = chartContext.w.config.labels[selectedIndex];
                    const selectedValue = chartContext.w.config.series[selectedIndex];
                    
                    showChartDetailModal('donut', selectedLabel, selectedValue);
                });
            }
            
            // 막대 차트 클릭 이벤트
            if (window.barChart) {
                window.barChart.addEventListener('dataPointSelection', function(event, chartContext, config) {
                    const selectedIndex = config.dataPointIndex;
                    const selectedLabel = chartContext.w.config.xaxis.categories[selectedIndex];
                    const selectedValue = chartContext.w.config.series[0].data[selectedIndex];
                    
                    showChartDetailModal('bar', selectedLabel, selectedValue);
                });
            }
        }

        // 차트 상세 정보 모달 표시
        function showChartDetailModal(chartType, label, value) {
            const modal = document.createElement('div');
            modal.id = 'chart-detail-modal';
            modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
            
            const modalContent = \`
                <div class="bg-white rounded-xl p-6 max-w-md w-full mx-4">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold text-slate-800">상세 정보</h3>
                        <button onclick="closeChartDetailModal()" class="text-slate-400 hover:text-slate-600">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    <div class="space-y-4">
                        <div class="bg-slate-50 p-4 rounded-lg">
                            <h4 class="font-medium text-slate-700 mb-2">시험 항목</h4>
                            <p class="text-slate-600">\${label}</p>
                        </div>
                        <div class="bg-slate-50 p-4 rounded-lg">
                            <h4 class="font-medium text-slate-700 mb-2">\${chartType === 'donut' ? '부적합 건수' : '부적합 비율'}</h4>
                            <p class="text-2xl font-bold text-red-500">\${value}\${chartType === 'donut' ? '건' : '%'}</p>
                        </div>
                        <div class="bg-blue-50 p-4 rounded-lg">
                            <h4 class="font-medium text-blue-700 mb-2">개선 권고사항</h4>
                            <p class="text-sm text-blue-600">
                                \${label} 항목의 \${chartType === 'donut' ? '부적합 발생' : '높은 부적합 비율'}에 대한 
                                원인 분석 및 개선 조치가 필요합니다.
                            </p>
                        </div>
                    </div>
                    <div class="mt-6 flex justify-end">
                        <button onclick="closeChartDetailModal()" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                            확인
                        </button>
                    </div>
                </div>
            \`;
            
            modal.innerHTML = modalContent;
            document.body.appendChild(modal);
            
            // 모달 외부 클릭 시 닫기
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeChartDetailModal();
                }
            });
        }

        // 차트 상세 정보 모달 닫기
        function closeChartDetailModal() {
            const modal = document.getElementById('chart-detail-modal');
            if (modal) {
                modal.style.transition = 'opacity 0.3s ease-out';
                modal.style.opacity = '0';
                setTimeout(() => {
                    if (modal.parentNode) {
                        modal.parentNode.removeChild(modal);
                    }
                }, 300);
            }
        }

        // 차트 내보내기 기능 설정
        function setupChartExportFeatures() {
            // 전역 내보내기 함수 정의
            window.exportChart = function(chartType) {
                let chart;
                let filename;
                
                if (chartType === 'donut' && window.donutChart) {
                    chart = window.donutChart;
                    filename = '부적합_분포_차트';
                } else if (chartType === 'bar' && window.barChart) {
                    chart = window.barChart;
                    filename = '부적합_비율_차트';
                } else {
                    console.error('차트를 찾을 수 없습니다:', chartType);
                    return;
                }
                
                // PNG로 내보내기
                chart.dataURI().then(function(uri) {
                    const link = document.createElement('a');
                    link.href = uri.imgURI;
                    link.download = filename + '.png';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    // 성공 메시지 표시
                    showExportSuccess(filename);
                });
            };
        }

        // 내보내기 성공 메시지
        function showExportSuccess(filename) {
            const successDiv = document.createElement('div');
            successDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
            successDiv.innerHTML = \`\${filename}.png 파일이 다운로드되었습니다.\`;
            document.body.appendChild(successDiv);
            
            setTimeout(() => {
                successDiv.style.transition = 'opacity 0.3s ease-out';
                successDiv.style.opacity = '0';
                setTimeout(() => {
                    if (successDiv.parentNode) {
                        successDiv.parentNode.removeChild(successDiv);
                    }
                }, 300);
            }, 3000);
        }

        // 차트 전체화면 토글
        function toggleChartFullscreen(chartId) {
            const chartContainer = document.getElementById(chartId);
            const chartCard = chartContainer.closest('.chart-card');
            
            if (chartCard.classList.contains('fullscreen-chart')) {
                // 전체화면 해제
                chartCard.classList.remove('fullscreen-chart');
                chartCard.style.cssText = '';
                document.body.style.overflow = '';
            } else {
                // 전체화면 적용
                chartCard.classList.add('fullscreen-chart');
                chartCard.style.cssText = \`
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    z-index: 9999;
                    background: white;
                    padding: 2rem;
                \`;
                document.body.style.overflow = 'hidden';
            }
            
            // 차트 크기 재조정
            setTimeout(() => {
                if (window.donutChart && chartId === 'donut-chart') {
                    window.donutChart.resize();
                }
                if (window.barChart && chartId === 'bar-chart') {
                    window.barChart.resize();
                }
            }, 100);
        }
        """
    
    def _get_empty_donut_chart(self) -> Dict[str, Any]:
        """빈 도넛 차트 설정 반환"""
        return {
            'chart': {
                'type': 'donut',
                'height': 350
            },
            'series': [1],
            'labels': ['데이터 없음'],
            'colors': ['#E0E0E0'],
            'plotOptions': {
                'pie': {
                    'donut': {
                        'size': '60%',
                        'labels': {
                            'show': True,
                            'total': {
                                'show': True,
                                'label': '부적합 없음',
                                'fontSize': '14px'
                            }
                        }
                    }
                }
            },
            'legend': {
                'show': False
            }
        }
    
    def create_donut_chart(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """호환성을 위한 도넛 차트 생성 메서드"""
        return self.generate_non_conforming_donut_chart(test_results)
    
    def create_bar_chart(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """호환성을 위한 막대 차트 생성 메서드"""
        return self.generate_non_conforming_bar_chart(test_results)

    def _get_empty_bar_chart(self) -> Dict[str, Any]:
        """빈 막대 차트 설정 반환"""
        return {
            'chart': {
                'type': 'bar',
                'height': 400
            },
            'series': [{
                'name': '부적합 비율',
                'data': []
            }],
            'xaxis': {
                'categories': []
            },
            'noData': {
                'text': '부적합 데이터가 없습니다',
                'align': 'center',
                'verticalAlign': 'middle',
                'style': {
                    'fontSize': '16px'
                }
            }
        }