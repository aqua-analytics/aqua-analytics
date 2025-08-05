"""
성능 벤치마크 테스트
다양한 데이터 크기와 조건에서의 성능 측정
"""

import pytest
import pandas as pd
import numpy as np
import time
import tempfile
import os
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

# 테스트 대상 모듈 import
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.data_processor import DataProcessor
from src.core.dynamic_dashboard_engine import DynamicDashboardEngine
from src.components.optimized_chart_renderer import OptimizedChartRenderer
from src.utils.performance_optimizer import PerformanceOptimizer


class TestPerformanceBenchmarks:
    """성능 벤치마크 테스트 클래스"""
    
    # 성능 기준 (초)
    PERFORMANCE_THRESHOLDS = {
        'small_file_parse': 2.0,      # 100행 파싱
        'medium_file_parse': 10.0,    # 1000행 파싱
        'large_file_parse': 30.0,     # 5000행 파싱
        'xlarge_file_parse': 60.0,    # 10000행 파싱
        'chart_render_small': 1.0,    # 소규모 차트 렌더링
        'chart_render_large': 3.0,    # 대규모 차트 렌더링
        'dashboard_update': 5.0,      # 대시보드 업데이트
        'memory_limit_mb': 500        # 메모리 사용량 제한 (MB)
    }
    
    def generate_test_data(self, size: int) -> pd.DataFrame:
        """테스트 데이터 생성"""
        test_items = [
            '아크릴로나이트릴', 'N-니트로조다이메틸아민', '벤젠', '톨루엔', 
            '크실렌', '에틸벤젠', '스티렌', '클로로포름', '사염화탄소', 
            '트리클로로에틸렌', '테트라클로로에틸렌', '1,1,1-트리클로로에탄'
        ]
        
        testers = ['김화빈', '이현풍', '박민수', '최영희', '정수진', '이민호', '박지영']
        standards = ['EPA 524.2', 'EPA 525.2', 'House Method', 'KS M 0124']
        
        data = {
            'No.': list(range(1, size + 1)),
            '시료명': [f'시료_{i % 50 + 1}' for i in range(size)],
            '분석번호': [f'25A{i:05d}' for i in range(size)],
            '시험항목': np.random.choice(test_items, size),
            '시험단위': ['mg/L'] * size,
            '결과(성적서)': [
                '불검출' if np.random.random() < 0.25 
                else f'{np.random.uniform(0, 0.02):.6f}' 
                for _ in range(size)
            ],
            '시험자입력값': np.random.uniform(0, 0.02, size),
            '기준대비 초과여부 (성적서)': np.random.choice(['적합', '부적합'], size, p=[0.65, 0.35]),
            '시험자': np.random.choice(testers, size),
            '시험표준': np.random.choice(standards, size),
            '기준': np.random.choice([
                '0.0006 mg/L 이하', '0.001 mg/L 이하', '0.005 mg/L 이하', '0.01 mg/L 이하'
            ], size),
            '입력일시': [
                (datetime.now() - timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d %H:%M')
                for _ in range(size)
            ],
            '처리방식': np.random.choice(['반올림', '절사', '올림'], size),
            '결과유형': np.random.choice(['수치형', '문자형'], size, p=[0.8, 0.2]),
            '시험자그룹': np.random.choice(['유기(ALL)', '무기(ALL)', '미생물'], size),
            '승인요청여부': np.random.choice(['Y', 'N'], size, p=[0.9, 0.1]),
            '성적서 출력여부': np.random.choice(['Y', 'N'], size, p=[0.95, 0.05]),
            'KOLAS 여부': np.random.choice(['Y', 'N'], size, p=[0.3, 0.7])
        }
        
        return pd.DataFrame(data)
    
    def create_temp_excel_file(self, data: pd.DataFrame) -> str:
        """임시 엑셀 파일 생성"""
        tmp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        data.to_excel(tmp_file.name, index=False)
        tmp_file.close()
        return tmp_file.name
    
    def measure_performance(self, func, *args, **kwargs) -> Tuple[Any, Dict[str, float]]:
        """성능 측정 헬퍼 함수"""
        process = psutil.Process()
        
        # 시작 상태 측정
        start_time = time.time()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = process.cpu_percent()
        
        # 함수 실행
        result = func(*args, **kwargs)
        
        # 종료 상태 측정
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        end_cpu = process.cpu_percent()
        
        metrics = {
            'execution_time': end_time - start_time,
            'memory_used': end_memory - start_memory,
            'peak_memory': end_memory,
            'cpu_usage': max(start_cpu, end_cpu)
        }
        
        return result, metrics
    
    @pytest.mark.parametrize("data_size", [100, 1000, 5000, 10000])
    def test_file_parsing_performance(self, data_size):
        """파일 파싱 성능 테스트"""
        print(f"\n📊 파일 파싱 성능 테스트 - {data_size}행")
        
        # 테스트 데이터 생성
        test_data = self.generate_test_data(data_size)
        temp_file = self.create_temp_excel_file(test_data)
        
        try:
            processor = DataProcessor()
            
            # 성능 측정
            test_results, metrics = self.measure_performance(
                processor.parse_excel_file, temp_file
            )
            
            # 결과 검증
            assert len(test_results) > 0, "파싱 결과가 없습니다"
            assert len(test_results) <= data_size, "파싱 결과가 예상보다 많습니다"
            
            # 성능 기준 확인
            size_category = self._get_size_category(data_size)
            threshold_key = f'{size_category}_file_parse'
            threshold = self.PERFORMANCE_THRESHOLDS.get(threshold_key, 60.0)
            
            assert metrics['execution_time'] < threshold, \
                f"파싱 시간 초과: {metrics['execution_time']:.2f}초 > {threshold}초"
            
            assert metrics['peak_memory'] < self.PERFORMANCE_THRESHOLDS['memory_limit_mb'], \
                f"메모리 사용량 초과: {metrics['peak_memory']:.1f}MB"
            
            # 결과 출력
            print(f"   ✅ 파싱 완료: {len(test_results)}행")
            print(f"   ⏱️  실행 시간: {metrics['execution_time']:.3f}초")
            print(f"   💾 메모리 사용: {metrics['memory_used']:.1f}MB (피크: {metrics['peak_memory']:.1f}MB)")
            print(f"   🖥️  CPU 사용률: {metrics['cpu_usage']:.1f}%")
            print(f"   📈 처리 속도: {len(test_results) / metrics['execution_time']:.0f}행/초")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def _get_size_category(self, size: int) -> str:
        """데이터 크기 카테고리 반환"""
        if size <= 100:
            return 'small'
        elif size <= 1000:
            return 'medium'
        elif size <= 5000:
            return 'large'
        else:
            return 'xlarge'
    
    @pytest.mark.parametrize("data_size", [100, 1000, 5000])
    def test_chart_rendering_performance(self, data_size):
        """차트 렌더링 성능 테스트"""
        print(f"\n📈 차트 렌더링 성능 테스트 - {data_size}행")
        
        # 테스트 데이터 생성
        test_data = self.generate_test_data(data_size)
        temp_file = self.create_temp_excel_file(test_data)
        
        try:
            processor = DataProcessor()
            test_results = processor.parse_excel_file(temp_file)
            
            chart_renderer = OptimizedChartRenderer()
            
            # 도넛 차트 성능 측정
            donut_config, donut_metrics = self.measure_performance(
                chart_renderer.generate_optimized_donut_chart, test_results
            )
            
            # 막대 차트 성능 측정
            bar_config, bar_metrics = self.measure_performance(
                chart_renderer.generate_optimized_bar_chart, test_results
            )
            
            # 성능 기준 확인
            size_category = 'small' if data_size <= 1000 else 'large'
            threshold = self.PERFORMANCE_THRESHOLDS[f'chart_render_{size_category}']
            
            assert donut_metrics['execution_time'] < threshold, \
                f"도넛 차트 렌더링 시간 초과: {donut_metrics['execution_time']:.2f}초"
            
            assert bar_metrics['execution_time'] < threshold, \
                f"막대 차트 렌더링 시간 초과: {bar_metrics['execution_time']:.2f}초"
            
            # 데이터 포인트 수 제한 확인
            donut_points = len(donut_config.get('series', []))
            bar_points = len(bar_config.get('series', [{}])[0].get('data', []))
            
            assert donut_points <= 1000, f"도넛 차트 데이터 포인트 초과: {donut_points}"
            assert bar_points <= 1000, f"막대 차트 데이터 포인트 초과: {bar_points}"
            
            # 결과 출력
            print(f"   ✅ 차트 렌더링 완료")
            print(f"   🍩 도넛 차트: {donut_metrics['execution_time']:.3f}초 ({donut_points}개 포인트)")
            print(f"   📊 막대 차트: {bar_metrics['execution_time']:.3f}초 ({bar_points}개 포인트)")
            print(f"   💾 총 메모리: {max(donut_metrics['peak_memory'], bar_metrics['peak_memory']):.1f}MB")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    @pytest.mark.parametrize("data_size", [1000, 5000])
    def test_dashboard_update_performance(self, data_size):
        """대시보드 업데이트 성능 테스트"""
        print(f"\n🎛️ 대시보드 업데이트 성능 테스트 - {data_size}행")
        
        # 테스트 데이터 생성
        test_data = self.generate_test_data(data_size)
        temp_file = self.create_temp_excel_file(test_data)
        
        try:
            processor = DataProcessor()
            test_results = processor.parse_excel_file(temp_file)
            
            dashboard_engine = DynamicDashboardEngine(processor)
            
            # 대시보드 업데이트 성능 측정
            _, metrics = self.measure_performance(
                dashboard_engine.update_dashboard, test_results, "test_file.xlsx"
            )
            
            # 성능 기준 확인
            threshold = self.PERFORMANCE_THRESHOLDS['dashboard_update']
            assert metrics['execution_time'] < threshold, \
                f"대시보드 업데이트 시간 초과: {metrics['execution_time']:.2f}초"
            
            # KPI 데이터 검증
            kpi_data = dashboard_engine.get_kpi_data()
            assert kpi_data is not None, "KPI 데이터가 생성되지 않았습니다"
            assert kpi_data['total_tests'] == len(test_results), "KPI 데이터가 정확하지 않습니다"
            
            # 결과 출력
            print(f"   ✅ 대시보드 업데이트 완료")
            print(f"   ⏱️  실행 시간: {metrics['execution_time']:.3f}초")
            print(f"   💾 메모리 사용: {metrics['peak_memory']:.1f}MB")
            print(f"   📊 KPI 데이터: {kpi_data['total_tests']}건 처리")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_memory_optimization_effectiveness(self):
        """메모리 최적화 효과 테스트"""
        print(f"\n💾 메모리 최적화 효과 테스트")
        
        # 대용량 테스트 데이터 생성
        test_data = self.generate_test_data(5000)
        temp_file = self.create_temp_excel_file(test_data)
        
        try:
            processor = DataProcessor()
            optimizer = PerformanceOptimizer()
            
            # 원본 데이터 처리
            test_results = processor.parse_excel_file(temp_file)
            original_df = processor.export_to_dataframe(test_results)
            
            # 메모리 사용량 측정
            original_memory = original_df.memory_usage(deep=True).sum() / 1024 / 1024
            
            # 최적화 적용
            optimized_df, optimization_metrics = self.measure_performance(
                optimizer.optimize_dataframe_memory, original_df
            )
            
            optimized_memory = optimized_df.memory_usage(deep=True).sum() / 1024 / 1024
            
            # 최적화 효과 검증
            memory_reduction = (original_memory - optimized_memory) / original_memory * 100
            assert memory_reduction > 0, "메모리 최적화 효과가 없습니다"
            
            # 데이터 무결성 확인
            assert len(original_df) == len(optimized_df), "최적화 후 데이터 손실 발생"
            assert list(original_df.columns) == list(optimized_df.columns), "컬럼 구조 변경됨"
            
            # 결과 출력
            print(f"   ✅ 메모리 최적화 완료")
            print(f"   📊 원본 크기: {original_memory:.1f}MB")
            print(f"   📉 최적화 후: {optimized_memory:.1f}MB")
            print(f"   💡 절약률: {memory_reduction:.1f}%")
            print(f"   ⏱️  최적화 시간: {optimization_metrics['execution_time']:.3f}초")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_caching_performance_impact(self):
        """캐싱 성능 영향 테스트"""
        print(f"\n🗄️ 캐싱 성능 영향 테스트")
        
        # 테스트 데이터 생성
        test_data = self.generate_test_data(1000)
        temp_file = self.create_temp_excel_file(test_data)
        
        try:
            processor = DataProcessor()
            test_results = processor.parse_excel_file(temp_file)
            
            # 첫 번째 호출 (캐시 미스)
            _, first_metrics = self.measure_performance(
                processor.get_project_summary, "TEST_PROJECT", test_results
            )
            
            # 두 번째 호출 (캐시 히트)
            _, second_metrics = self.measure_performance(
                processor.get_project_summary, "TEST_PROJECT", test_results
            )
            
            # 캐시 효과 검증
            speedup = first_metrics['execution_time'] / max(second_metrics['execution_time'], 0.001)
            assert speedup > 2, f"캐시 효과가 부족합니다: {speedup:.1f}배"
            
            # 결과 출력
            print(f"   ✅ 캐싱 효과 확인")
            print(f"   🐌 첫 번째 호출: {first_metrics['execution_time']:.3f}초")
            print(f"   🚀 두 번째 호출: {second_metrics['execution_time']:.3f}초")
            print(f"   ⚡ 속도 향상: {speedup:.1f}배")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_concurrent_processing_scalability(self):
        """동시 처리 확장성 테스트"""
        print(f"\n🔄 동시 처리 확장성 테스트")
        
        import threading
        import queue
        
        # 테스트 데이터 생성
        test_data = self.generate_test_data(500)  # 작은 크기로 빠른 테스트
        temp_file = self.create_temp_excel_file(test_data)
        
        try:
            processor = DataProcessor()
            
            def process_file_worker(file_path, results_queue, thread_id):
                start_time = time.time()
                try:
                    test_results = processor.parse_excel_file(file_path)
                    processing_time = time.time() - start_time
                    results_queue.put({
                        'thread_id': thread_id,
                        'success': True,
                        'processing_time': processing_time,
                        'results_count': len(test_results)
                    })
                except Exception as e:
                    results_queue.put({
                        'thread_id': thread_id,
                        'success': False,
                        'error': str(e),
                        'processing_time': time.time() - start_time
                    })
            
            # 다양한 동시성 레벨 테스트
            for thread_count in [1, 2, 4, 8]:
                print(f"   🧵 {thread_count}개 스레드 테스트")
                
                results_queue = queue.Queue()
                threads = []
                
                start_time = time.time()
                
                # 스레드 시작
                for i in range(thread_count):
                    thread = threading.Thread(
                        target=process_file_worker,
                        args=(temp_file, results_queue, i)
                    )
                    threads.append(thread)
                    thread.start()
                
                # 모든 스레드 완료 대기
                for thread in threads:
                    thread.join(timeout=30)
                
                total_time = time.time() - start_time
                
                # 결과 수집
                results = []
                while not results_queue.empty():
                    results.append(results_queue.get())
                
                # 성공률 확인
                successful_results = [r for r in results if r.get('success', False)]
                success_rate = len(successful_results) / thread_count * 100
                
                assert success_rate >= 80, f"성공률이 낮습니다: {success_rate:.1f}%"
                
                # 평균 처리 시간
                avg_processing_time = sum(r['processing_time'] for r in successful_results) / len(successful_results)
                
                print(f"      ✅ 성공률: {success_rate:.1f}%")
                print(f"      ⏱️  총 시간: {total_time:.3f}초")
                print(f"      📊 평균 처리: {avg_processing_time:.3f}초")
                
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_performance_regression(self):
        """성능 회귀 테스트"""
        print(f"\n📉 성능 회귀 테스트")
        
        # 기준 성능 데이터 (예상 성능)
        baseline_performance = {
            'small_parse': 1.0,    # 100행 파싱 (초)
            'medium_parse': 5.0,   # 1000행 파싱 (초)
            'chart_render': 0.5,   # 차트 렌더링 (초)
            'dashboard_update': 2.0 # 대시보드 업데이트 (초)
        }
        
        # 현재 성능 측정
        current_performance = {}
        
        # 소규모 파싱 테스트
        test_data = self.generate_test_data(100)
        temp_file = self.create_temp_excel_file(test_data)
        
        try:
            processor = DataProcessor()
            
            # 파싱 성능
            _, metrics = self.measure_performance(processor.parse_excel_file, temp_file)
            current_performance['small_parse'] = metrics['execution_time']
            
            test_results = processor.parse_excel_file(temp_file)
            
            # 차트 렌더링 성능
            chart_renderer = OptimizedChartRenderer()
            _, metrics = self.measure_performance(
                chart_renderer.generate_optimized_donut_chart, test_results
            )
            current_performance['chart_render'] = metrics['execution_time']
            
            # 대시보드 업데이트 성능
            dashboard_engine = DynamicDashboardEngine(processor)
            _, metrics = self.measure_performance(
                dashboard_engine.update_dashboard, test_results, "test.xlsx"
            )
            current_performance['dashboard_update'] = metrics['execution_time']
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        # 중간 규모 파싱 테스트
        test_data = self.generate_test_data(1000)
        temp_file = self.create_temp_excel_file(test_data)
        
        try:
            _, metrics = self.measure_performance(processor.parse_excel_file, temp_file)
            current_performance['medium_parse'] = metrics['execution_time']
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        # 성능 회귀 검증
        regression_threshold = 1.5  # 50% 이상 느려지면 회귀로 판단
        
        for operation, baseline in baseline_performance.items():
            current = current_performance.get(operation, 0)
            regression_ratio = current / baseline
            
            print(f"   📊 {operation}: {current:.3f}초 (기준: {baseline:.3f}초, 비율: {regression_ratio:.2f}x)")
            
            assert regression_ratio < regression_threshold, \
                f"성능 회귀 감지 - {operation}: {regression_ratio:.2f}배 느려짐"
        
        print(f"   ✅ 성능 회귀 없음 확인")


if __name__ == "__main__":
    # 벤치마크 테스트 실행
    test_class = TestPerformanceBenchmarks()
    
    print("🚀 성능 벤치마크 테스트 시작")
    
    # 개별 테스트 실행
    test_class.test_file_parsing_performance(100)
    test_class.test_file_parsing_performance(1000)
    test_class.test_chart_rendering_performance(1000)
    test_class.test_dashboard_update_performance(1000)
    test_class.test_memory_optimization_effectiveness()
    test_class.test_caching_performance_impact()
    test_class.test_concurrent_processing_scalability()
    test_class.test_performance_regression()
    
    print("🎉 모든 성능 벤치마크 테스트 완료!")