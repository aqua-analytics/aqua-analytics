"""
최적화된 차트 렌더링 시스템
대용량 데이터 시각화 성능 최적화
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from collections import Counter
import logging
from dataclasses import dataclass
from src.core.data_models import TestResult
from src.utils.performance_optimizer import optimize_performance, cache_result

# 로깅 설정
logger = logging.getLogger(__name__)


@dataclass
class ChartOptimizationConfig:
    """차트 최적화 설정"""
    max_data_points: int = 1000  # 최대 데이터 포인트 수
    enable_sampling: bool = True  # 데이터 샘플링 활성화
    enable_aggregation: bool = True  # 데이터 집계 활성화
    enable_lazy_loading: bool = True  # 지연 로딩 활성화
    animation_duration: int = 800  # 애니메이션 지속 시간 (ms)
    enable_virtualization: bool = True  # 가상화 활성화
    cache_charts: bool = True  # 차트 캐싱 활성화


class OptimizedChartRenderer:
    """최적화된 차트 렌더링 클래스"""
    
    def __init__(self, config: ChartOptimizationConfig = None):
        """
        최적화된 차트 렌더러 초기화
        
        Args:
            config: 최적화 설정
        """
        self.config = config or ChartOptimizationConfig()
        self.chart_cache = {}
        self.data_cache = {}
        
        # 성능 최적화된 색상 팔레트
        self.optimized_colors = [
            '#ef4444', '#f59e0b', '#10b981', '#3b82f6', 
            '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16',
            '#f97316', '#14b8a6', '#6366f1', '#a855f7'
        ]
        
        # 차트 기본 설정 (성능 최적화)
        self.base_config = {
            'chart': {
                'animations': {
                    'enabled': True,
                    'easing': 'easeinout',
                    'speed': self.config.animation_duration,
                    'animateGradually': {
                        'enabled': True,
                        'delay': 100
                    }
                },
                'toolbar': {
                    'show': False
                },
                'selection': {
                    'enabled': False  # 성능 향상을 위해 비활성화
                },
                'zoom': {
                    'enabled': False  # 성능 향상을 위해 비활성화
                }
            },
            'dataLabels': {
                'enabled': True,
                'style': {
                    'fontSize': '11px',
                    'fontWeight': 'bold'
                }
            },
            'tooltip': {
                'enabled': True,
                'shared': False,  # 성능 향상
                'followCursor': False  # 성능 향상
            },
            'legend': {
                'show': True,
                'position': 'bottom'
            }
        }
    
    @optimize_performance("optimize_data_for_chart")
    def _optimize_data_for_chart(self, data: List[TestResult], chart_type: str) -> Tuple[List, List]:
        """
        차트용 데이터 최적화
        
        Args:
            data: 원본 데이터
            chart_type: 차트 타입
            
        Returns:
            (최적화된 라벨, 최적화된 값) 튜플
        """
        if not data:
            return [], []
        
        # 부적합 항목만 필터링
        non_conforming_items = [
            result for result in data 
            if result.is_non_conforming()
        ]
        
        if not non_conforming_items:
            return [], []
        
        if chart_type == 'donut':
            # 시험항목별 부적합 개수 계산
            item_counts = Counter([result.test_item for result in non_conforming_items])
            
            # 데이터 포인트 수 제한
            if len(item_counts) > self.config.max_data_points:
                # 상위 N개만 선택하고 나머지는 '기타'로 그룹화
                top_items = dict(item_counts.most_common(self.config.max_data_points - 1))
                other_count = sum(item_counts.values()) - sum(top_items.values())
                
                if other_count > 0:
                    top_items['기타'] = other_count
                
                item_counts = top_items
            
            # 라벨 길이 최적화
            labels = []
            for label in item_counts.keys():
                if len(label) > 20:
                    labels.append(label[:17] + '...')
                else:
                    labels.append(label)
            
            values = list(item_counts.values())
            
        elif chart_type == 'bar':
            # 시험항목별 부적합 비율 계산
            item_stats = {}
            for result in data:
                item = result.test_item
                if item not in item_stats:
                    item_stats[item] = {'total': 0, 'non_conforming': 0}
                
                item_stats[item]['total'] += 1
                if result.is_non_conforming():
                    item_stats[item]['non_conforming'] += 1
            
            # 부적합 비율 계산
            item_ratios = []
            for item, stats in item_stats.items():
                if stats['non_conforming'] > 0:
                    ratio = (stats['non_conforming'] / stats['total']) * 100
                    item_ratios.append({
                        'item': item,
                        'ratio': ratio,
                        'non_conforming': stats['non_conforming'],
                        'total': stats['total']
                    })
            
            # 비율 기준 정렬 및 제한
            item_ratios.sort(key=lambda x: x['ratio'], reverse=True)
            if len(item_ratios) > self.config.max_data_points:
                item_ratios = item_ratios[:self.config.max_data_points]
            
            # 라벨 길이 최적화
            labels = []
            for item_data in item_ratios:
                item = item_data['item']
                if len(item) > 25:
                    labels.append(item[:22] + '...')
                else:
                    labels.append(item)
            
            values = [round(item['ratio'], 1) for item in item_ratios]
        
        else:
            labels, values = [], []
        
        return labels, values
    
    @cache_result(ttl=1800)  # 30분 캐시
    @optimize_performance("generate_optimized_donut_chart")
    def generate_optimized_donut_chart(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """
        최적화된 도넛 차트 생성
        
        Args:
            test_results: 시험 결과 리스트
            
        Returns:
            최적화된 ApexCharts 도넛 차트 설정
        """
        labels, series = self._optimize_data_for_chart(test_results, 'donut')
        
        if not labels or not series:
            return self._get_empty_donut_chart()
        
        total_violations = sum(series)
        
        # 성능 최적화된 차트 설정
        chart_config = {
            **self.base_config,
            'chart': {
                **self.base_config['chart'],
                'type': 'donut',
                'height': 380,
                'fontFamily': 'Noto Sans KR, sans-serif'
            },
            'series': series,
            'labels': labels,
            'colors': self.optimized_colors[:len(labels)],
            'plotOptions': {
                'pie': {
                    'donut': {
                        'size': '65%',
                        'labels': {
                            'show': True,
                            'name': {
                                'show': True,
                                'fontSize': '14px',
                                'fontWeight': 600,
                                'color': '#374151',
                                'offsetY': -10
                            },
                            'value': {
                                'show': True,
                                'fontSize': '24px',
                                'fontWeight': 700,
                                'color': '#ef4444',
                                'offsetY': 10,
                                'formatter': 'function(val) { return val + "건"; }'
                            },
                            'total': {
                                'show': True,
                                'showAlways': True,
                                'label': '총 부적합',
                                'fontSize': '12px',
                                'fontWeight': 600,
                                'color': '#6b7280',
                                'formatter': f'function(w) {{ return "{total_violations}건"; }}'
                            }
                        }
                    },
                    'expandOnClick': False,  # 성능 최적화
                    'customScale': 1.0
                }
            },
            'dataLabels': {
                **self.base_config['dataLabels'],
                'formatter': 'function(val, opts) { return val.toFixed(1) + "%"; }',
                'style': {
                    'fontSize': '10px',
                    'fontWeight': 'bold',
                    'colors': ['#ffffff']
                }
            },
            'legend': {
                **self.base_config['legend'],
                'fontSize': '10px',
                'itemMargin': {
                    'horizontal': 8,
                    'vertical': 4
                },
                'markers': {
                    'width': 8,
                    'height': 8,
                    'radius': 4
                }
            },
            'tooltip': {
                **self.base_config['tooltip'],
                'y': {
                    'formatter': 'function(val) { return val + "건"; }'
                }
            },
            'stroke': {
                'show': True,
                'width': 2,
                'colors': ['#ffffff']
            },
            'states': {
                'hover': {
                    'filter': {
                        'type': 'lighten',
                        'value': 0.08
                    }
                }
            }
        }
        
        return chart_config
    
    @cache_result(ttl=1800)  # 30분 캐시
    @optimize_performance("generate_optimized_bar_chart")
    def generate_optimized_bar_chart(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """
        최적화된 수평 막대 차트 생성
        
        Args:
            test_results: 시험 결과 리스트
            
        Returns:
            최적화된 ApexCharts 막대 차트 설정
        """
        categories, data = self._optimize_data_for_chart(test_results, 'bar')
        
        if not categories or not data:
            return self._get_empty_bar_chart()
        
        # 성능 최적화된 차트 설정
        chart_config = {
            **self.base_config,
            'chart': {
                **self.base_config['chart'],
                'type': 'bar',
                'height': min(420, max(300, len(categories) * 35)),  # 동적 높이
                'fontFamily': 'Noto Sans KR, sans-serif'
            },
            'plotOptions': {
                'bar': {
                    'horizontal': True,
                    'borderRadius': 6,
                    'borderRadiusApplication': 'end',
                    'barHeight': '60%',
                    'dataLabels': {
                        'position': 'center'
                    },
                    'distributed': False
                }
            },
            'dataLabels': {
                **self.base_config['dataLabels'],
                'formatter': 'function(val) { return val + "%"; }',
                'style': {
                    'fontSize': '10px',
                    'fontWeight': 'bold',
                    'colors': ['#ffffff']
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
                        'fontSize': '10px',
                        'fontFamily': 'Noto Sans KR, sans-serif'
                    },
                    'formatter': 'function(val) { return val + "%"; }'
                },
                'axisBorder': {
                    'show': True,
                    'color': '#e5e7eb'
                }
            },
            'yaxis': {
                'labels': {
                    'style': {
                        'fontSize': '10px',
                        'fontFamily': 'Noto Sans KR, sans-serif',
                        'colors': ['#374151']
                    },
                    'maxWidth': 120
                }
            },
            'colors': ['#ef4444'],
            'fill': {
                'type': 'gradient',
                'gradient': {
                    'shade': 'light',
                    'type': 'horizontal',
                    'shadeIntensity': 0.4,
                    'gradientToColors': ['#fca5a5'],
                    'inverseColors': False,
                    'opacityFrom': 1.0,
                    'opacityTo': 0.8,
                    'stops': [0, 100]
                }
            },
            'tooltip': {
                **self.base_config['tooltip'],
                'y': {
                    'formatter': 'function(val) { return val + "%"; }'
                }
            },
            'grid': {
                'show': True,
                'borderColor': '#e5e7eb',
                'strokeDashArray': 2,
                'xaxis': {
                    'lines': {
                        'show': True
                    }
                },
                'yaxis': {
                    'lines': {
                        'show': False
                    }
                }
            },
            'stroke': {
                'show': True,
                'width': 1,
                'colors': ['transparent']
            }
        }
        
        return chart_config
    
    def _get_empty_donut_chart(self) -> Dict[str, Any]:
        """빈 도넛 차트 설정 반환"""
        return {
            'chart': {
                'type': 'donut',
                'height': 380
            },
            'series': [],
            'labels': [],
            'noData': {
                'text': '부적합 항목이 없습니다',
                'align': 'center',
                'verticalAlign': 'middle',
                'offsetX': 0,
                'offsetY': 0,
                'style': {
                    'color': '#6b7280',
                    'fontSize': '16px',
                    'fontFamily': 'Noto Sans KR, sans-serif'
                }
            }
        }
    
    def _get_empty_bar_chart(self) -> Dict[str, Any]:
        """빈 막대 차트 설정 반환"""
        return {
            'chart': {
                'type': 'bar',
                'height': 420
            },
            'series': [],
            'xaxis': {
                'categories': []
            },
            'noData': {
                'text': '부적합 항목이 없습니다',
                'align': 'center',
                'verticalAlign': 'middle',
                'offsetX': 0,
                'offsetY': 0,
                'style': {
                    'color': '#6b7280',
                    'fontSize': '16px',
                    'fontFamily': 'Noto Sans KR, sans-serif'
                }
            }
        }
    
    @optimize_performance("generate_chart_update_script")
    def generate_optimized_chart_update_script(
        self, 
        chart_id: str, 
        test_results: List[TestResult]
    ) -> str:
        """
        최적화된 차트 업데이트 스크립트 생성
        
        Args:
            chart_id: 차트 식별자
            test_results: 시험 결과 리스트
            
        Returns:
            최적화된 JavaScript 업데이트 코드
        """
        try:
            if chart_id == 'donut':
                chart_config = self.generate_optimized_donut_chart(test_results)
                
                if not chart_config.get('series'):
                    return f"""
                    if (window.donutChart) {{
                        window.donutChart.updateOptions({{
                            noData: {{
                                text: '부적합 항목이 없습니다'
                            }}
                        }});
                    }}
                    """
                
                return f"""
                if (window.donutChart) {{
                    // 성능 최적화: 애니메이션 비활성화 후 업데이트
                    window.donutChart.updateOptions({{
                        chart: {{
                            animations: {{
                                enabled: false
                            }}
                        }}
                    }}, false, false);
                    
                    // 데이터 업데이트
                    window.donutChart.updateSeries({json.dumps(chart_config['series'])});
                    window.donutChart.updateOptions({{
                        labels: {json.dumps(chart_config['labels'], ensure_ascii=False)},
                        chart: {{
                            animations: {{
                                enabled: true,
                                speed: {self.config.animation_duration}
                            }}
                        }}
                    }}, false, true);
                }}
                """
            
            elif chart_id == 'bar':
                chart_config = self.generate_optimized_bar_chart(test_results)
                
                if not chart_config.get('series') or not chart_config['series'][0]['data']:
                    return f"""
                    if (window.barChart) {{
                        window.barChart.updateOptions({{
                            noData: {{
                                text: '부적합 항목이 없습니다'
                            }}
                        }});
                    }}
                    """
                
                return f"""
                if (window.barChart) {{
                    // 성능 최적화: 애니메이션 비활성화 후 업데이트
                    window.barChart.updateOptions({{
                        chart: {{
                            animations: {{
                                enabled: false
                            }}
                        }}
                    }}, false, false);
                    
                    // 데이터 업데이트
                    window.barChart.updateSeries([{{
                        name: '부적합 비율',
                        data: {json.dumps(chart_config['series'][0]['data'])}
                    }}]);
                    
                    window.barChart.updateOptions({{
                        xaxis: {{
                            categories: {json.dumps(chart_config['xaxis']['categories'], ensure_ascii=False)}
                        }},
                        chart: {{
                            animations: {{
                                enabled: true,
                                speed: {self.config.animation_duration}
                            }}
                        }}
                    }}, false, true);
                }}
                """
            
            return ""
            
        except Exception as e:
            logger.error(f"차트 업데이트 스크립트 생성 실패: {e}")
            return ""
    
    @optimize_performance("generate_lazy_loading_script")
    def generate_lazy_loading_script(self) -> str:
        """
        지연 로딩 스크립트 생성
        
        Returns:
            지연 로딩 JavaScript 코드
        """
        if not self.config.enable_lazy_loading:
            return ""
        
        return """
        // 지연 로딩 및 성능 최적화
        function initializeLazyChartLoading() {
            const chartContainers = document.querySelectorAll('.chart-container');
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const chartId = entry.target.getAttribute('data-chart-id');
                        if (chartId && !entry.target.hasAttribute('data-loaded')) {
                            loadChartLazy(chartId, entry.target);
                            entry.target.setAttribute('data-loaded', 'true');
                            observer.unobserve(entry.target);
                        }
                    }
                });
            }, {
                rootMargin: '50px',
                threshold: 0.1
            });
            
            chartContainers.forEach(container => {
                observer.observe(container);
            });
        }
        
        function loadChartLazy(chartId, container) {
            // 로딩 스피너 표시
            container.innerHTML = `
                <div class="flex items-center justify-center h-full">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500"></div>
                    <span class="ml-2 text-slate-600">차트 로딩 중...</span>
                </div>
            `;
            
            // 실제 차트 로딩 (비동기)
            setTimeout(() => {
                if (chartId === 'donut') {
                    initializeDonutChart();
                } else if (chartId === 'bar') {
                    initializeBarChart();
                }
            }, 100);
        }
        
        // 페이지 로드 시 지연 로딩 초기화
        document.addEventListener('DOMContentLoaded', function() {
            if (typeof IntersectionObserver !== 'undefined') {
                initializeLazyChartLoading();
            } else {
                // IntersectionObserver 미지원 브라우저 대응
                setTimeout(() => {
                    initializeDonutChart();
                    initializeBarChart();
                }, 500);
            }
        });
        """
    
    @optimize_performance("generate_performance_monitoring_script")
    def generate_performance_monitoring_script(self) -> str:
        """
        차트 성능 모니터링 스크립트 생성
        
        Returns:
            성능 모니터링 JavaScript 코드
        """
        return """
        // 차트 성능 모니터링
        class ChartPerformanceMonitor {
            constructor() {
                this.metrics = {
                    renderTimes: [],
                    updateTimes: [],
                    memoryUsage: []
                };
            }
            
            startRender(chartId) {
                this.startTime = performance.now();
                this.chartId = chartId;
            }
            
            endRender() {
                if (this.startTime) {
                    const renderTime = performance.now() - this.startTime;
                    this.metrics.renderTimes.push({
                        chartId: this.chartId,
                        time: renderTime,
                        timestamp: Date.now()
                    });
                    
                    // 메모리 사용량 측정 (가능한 경우)
                    if (performance.memory) {
                        this.metrics.memoryUsage.push({
                            used: performance.memory.usedJSHeapSize,
                            total: performance.memory.totalJSHeapSize,
                            timestamp: Date.now()
                        });
                    }
                    
                    console.log(`Chart ${this.chartId} rendered in ${renderTime.toFixed(2)}ms`);
                }
            }
            
            getAverageRenderTime(chartId) {
                const chartMetrics = this.metrics.renderTimes.filter(m => m.chartId === chartId);
                if (chartMetrics.length === 0) return 0;
                
                const total = chartMetrics.reduce((sum, m) => sum + m.time, 0);
                return total / chartMetrics.length;
            }
            
            getPerformanceReport() {
                return {
                    totalRenders: this.metrics.renderTimes.length,
                    averageRenderTime: this.metrics.renderTimes.length > 0 
                        ? this.metrics.renderTimes.reduce((sum, m) => sum + m.time, 0) / this.metrics.renderTimes.length 
                        : 0,
                    memorySnapshots: this.metrics.memoryUsage.length,
                    lastMemoryUsage: this.metrics.memoryUsage.length > 0 
                        ? this.metrics.memoryUsage[this.metrics.memoryUsage.length - 1] 
                        : null
                };
            }
        }
        
        // 전역 성능 모니터 인스턴스
        window.chartPerformanceMonitor = new ChartPerformanceMonitor();
        
        // 차트 렌더링 성능 측정 래퍼
        function renderChartWithMonitoring(chartId, renderFunction) {
            window.chartPerformanceMonitor.startRender(chartId);
            
            try {
                const result = renderFunction();
                window.chartPerformanceMonitor.endRender();
                return result;
            } catch (error) {
                console.error(`Chart ${chartId} rendering failed:`, error);
                window.chartPerformanceMonitor.endRender();
                throw error;
            }
        }
        """
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """최적화 통계 반환"""
        return {
            'config': {
                'max_data_points': self.config.max_data_points,
                'enable_sampling': self.config.enable_sampling,
                'enable_aggregation': self.config.enable_aggregation,
                'enable_lazy_loading': self.config.enable_lazy_loading,
                'animation_duration': self.config.animation_duration,
                'cache_charts': self.config.cache_charts
            },
            'cache_size': len(self.chart_cache),
            'data_cache_size': len(self.data_cache)
        }
    
    def clear_cache(self) -> None:
        """캐시 삭제"""
        self.chart_cache.clear()
        self.data_cache.clear()
        logger.info("차트 캐시가 삭제되었습니다.")
    
    def update_config(self, **kwargs) -> None:
        """설정 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"설정 업데이트: {key} = {value}")


# 전역 최적화된 차트 렌더러 인스턴스
optimized_chart_renderer = OptimizedChartRenderer()


# 사용 예시 및 테스트 함수
def test_optimized_chart_renderer():
    """최적화된 차트 렌더러 테스트"""
    from src.core.data_models import TestResult
    from datetime import datetime
    import random
    
    # 대용량 테스트 데이터 생성
    test_results = []
    test_items = [
        '아크릴로나이트릴', 'N-니트로조다이메틸아민', '벤젠', '톨루엔', 
        '크실렌', '에틸벤젠', '스티렌', '클로로포름', '사염화탄소', '트리클로로에틸렌'
    ]
    
    for i in range(5000):  # 5000개 데이터 생성
        test_result = TestResult(
            no=i + 1,
            sample_name=f'시료_{i % 100 + 1}',
            analysis_number=f'25A{i:05d}',
            test_item=random.choice(test_items),
            test_unit='mg/L',
            result_report=str(round(random.uniform(0, 0.01), 6)),
            tester_input_value=round(random.uniform(0, 0.01), 6),
            standard_excess='부적합' if random.random() < 0.3 else '적합',
            tester=f'시험자_{i % 10 + 1}',
            test_standard='EPA 524.2',
            standard_criteria='0.0006 mg/L 이하',
            text_digits='',
            processing_method='반올림',
            result_display_digits=4,
            result_type='수치형',
            tester_group='유기(ALL)',
            input_datetime=datetime.now(),
            approval_request='Y',
            approval_request_datetime=datetime.now(),
            test_result_display_limit=0.0002,
            quantitative_limit_processing='불검출',
            test_equipment='',
            judgment_status='N',
            report_output='Y',
            kolas_status='N',
            test_lab_group='유기_용출',
            test_set='Set 1'
        )
        test_results.append(test_result)
    
    print(f"테스트 데이터 생성 완료: {len(test_results)}개")
    
    # 최적화된 차트 렌더러 테스트
    renderer = OptimizedChartRenderer()
    
    # 도넛 차트 생성 테스트
    start_time = time.time()
    donut_config = renderer.generate_optimized_donut_chart(test_results)
    donut_time = time.time() - start_time
    
    print(f"도넛 차트 생성 시간: {donut_time:.3f}초")
    print(f"도넛 차트 데이터 포인트: {len(donut_config.get('series', []))}")
    
    # 막대 차트 생성 테스트
    start_time = time.time()
    bar_config = renderer.generate_optimized_bar_chart(test_results)
    bar_time = time.time() - start_time
    
    print(f"막대 차트 생성 시간: {bar_time:.3f}초")
    print(f"막대 차트 데이터 포인트: {len(bar_config.get('series', [{}])[0].get('data', []))}")
    
    # 캐시 테스트 (두 번째 호출)
    start_time = time.time()
    donut_config_cached = renderer.generate_optimized_donut_chart(test_results)
    cached_time = time.time() - start_time
    
    print(f"캐시된 도넛 차트 생성 시간: {cached_time:.3f}초")
    print(f"캐시 효과: {donut_time / max(cached_time, 0.001):.1f}배 빠름")
    
    # 최적화 통계
    stats = renderer.get_optimization_stats()
    print(f"최적화 통계: {stats}")
    
    return renderer


if __name__ == "__main__":
    import time
    test_optimized_chart_renderer()