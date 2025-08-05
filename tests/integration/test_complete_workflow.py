"""
전체 워크플로우 통합 테스트
파일 업로드부터 보고서 생성까지 전체 프로세스 테스트
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 테스트 대상 모듈 import
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.core.data_processor import DataProcessor
    from src.core.dynamic_dashboard_engine import DynamicDashboardEngine
    from src.core.data_models import TestResult, ProjectSummary, Standard
    from src.components.optimized_chart_renderer import OptimizedChartRenderer
    from src.utils.performance_optimizer import PerformanceOptimizer
    from src.utils.error_handler import ErrorHandler
    from src.utils.file_validator import FileValidator
except ImportError:
    # 대체 import 경로
    sys.path.append('src')
    from core.data_processor import DataProcessor
    from core.dynamic_dashboard_engine import DynamicDashboardEngine
    from core.data_models import TestResult, ProjectSummary, Standard
    from components.optimized_chart_renderer import OptimizedChartRenderer
    from utils.performance_optimizer import PerformanceOptimizer
    from utils.error_handler import ErrorHandler
    from utils.file_validator import FileValidator


class TestCompleteWorkflow:
    """전체 워크플로우 통합 테스트 클래스"""
    
    @pytest.fixture
    def sample_excel_data(self):
        """테스트용 엑셀 데이터 생성"""
        data = {
            'No.': list(range(1, 101)),
            '시료명': [f'시료_{i % 10 + 1}' for i in range(100)],
            '분석번호': [f'25A{i:05d}' for i in range(100)],
            '시험항목': np.random.choice([
                '아크릴로나이트릴', 'N-니트로조다이메틸아민', '벤젠', 
                '톨루엔', '크실렌'
            ], 100),
            '시험단위': ['mg/L'] * 100,
            '결과(성적서)': [
                '불검출' if np.random.random() < 0.3 
                else f'{np.random.uniform(0, 0.01):.6f}' 
                for _ in range(100)
            ],
            '시험자입력값': np.random.uniform(0, 0.01, 100),
            '기준대비 초과여부 (성적서)': np.random.choice(['적합', '부적합'], 100, p=[0.7, 0.3]),
            '시험자': np.random.choice(['김화빈', '이현풍', '박민수'], 100),
            '시험표준': ['EPA 524.2'] * 100,
            '기준': ['0.0006 mg/L 이하'] * 100,
            '입력일시': [
                (datetime.now() - timedelta(days=np.random.randint(0, 30))).strftime('%Y-%m-%d %H:%M')
                for _ in range(100)
            ]
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def temp_excel_file(self, sample_excel_data):
        """임시 엑셀 파일 생성"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            sample_excel_data.to_excel(tmp_file.name, index=False)
            yield tmp_file.name
        
        # 정리
        if os.path.exists(tmp_file.name):
            os.unlink(tmp_file.name)
    
    @pytest.fixture
    def large_excel_data(self):
        """대용량 테스트 데이터 생성 (5000행)"""
        size = 5000
        data = {
            'No.': list(range(1, size + 1)),
            '시료명': [f'시료_{i % 100 + 1}' for i in range(size)],
            '분석번호': [f'25A{i:05d}' for i in range(size)],
            '시험항목': np.random.choice([
                '아크릴로나이트릴', 'N-니트로조다이메틸아민', '벤젠', 
                '톨루엔', '크실렌', '에틸벤젠', '스티렌', '클로로포름'
            ], size),
            '시험단위': ['mg/L'] * size,
            '결과(성적서)': [
                '불검출' if np.random.random() < 0.2 
                else f'{np.random.uniform(0, 0.02):.6f}' 
                for _ in range(size)
            ],
            '시험자입력값': np.random.uniform(0, 0.02, size),
            '기준대비 초과여부 (성적서)': np.random.choice(['적합', '부적합'], size, p=[0.6, 0.4]),
            '시험자': np.random.choice(['김화빈', '이현풍', '박민수', '최영희', '정수진'], size),
            '시험표준': np.random.choice(['EPA 524.2', 'EPA 525.2', 'House Method'], size),
            '기준': ['0.0006 mg/L 이하'] * size,
            '입력일시': [
                (datetime.now() - timedelta(days=np.random.randint(0, 90))).strftime('%Y-%m-%d %H:%M')
                for _ in range(size)
            ]
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def temp_large_excel_file(self, large_excel_data):
        """대용량 임시 엑셀 파일 생성"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            large_excel_data.to_excel(tmp_file.name, index=False)
            yield tmp_file.name
        
        # 정리
        if os.path.exists(tmp_file.name):
            os.unlink(tmp_file.name)
    
    def test_complete_workflow_small_file(self, temp_excel_file):
        """소규모 파일 전체 워크플로우 테스트"""
        # 1. 파일 검증
        validator = FileValidator()
        validation_result = validator.validate_file(temp_excel_file)
        assert validation_result['is_valid'], f"파일 검증 실패: {validation_result['errors']}"
        
        # 2. 데이터 처리
        processor = DataProcessor()
        start_time = time.time()
        test_results = processor.parse_excel_file(temp_excel_file)
        parse_time = time.time() - start_time
        
        assert len(test_results) > 0, "파싱된 결과가 없습니다"
        assert parse_time < 5.0, f"파싱 시간이 너무 깁니다: {parse_time:.2f}초"
        
        # 3. 프로젝트 요약 생성
        project_name = "TEST_PROJECT"
        summary = processor.get_project_summary(project_name, test_results)
        
        assert summary.project_name == project_name
        assert summary.total_tests == len(test_results)
        assert 0 <= summary.violation_rate <= 100
        
        # 4. 대시보드 엔진 초기화 및 업데이트
        dashboard_engine = DynamicDashboardEngine(processor)
        dashboard_engine.update_dashboard(test_results, "test_file.xlsx")
        
        assert dashboard_engine.is_dashboard_initialized()
        assert dashboard_engine.get_current_file() == "test_file.xlsx"
        
        # 5. KPI 데이터 검증
        kpi_data = dashboard_engine.get_kpi_data()
        assert kpi_data is not None
        assert kpi_data['total_tests'] == len(test_results)
        assert kpi_data['non_conforming_tests'] >= 0
        assert 0 <= kpi_data['non_conforming_rate'] <= 100
        
        # 6. 차트 렌더링 테스트
        chart_renderer = OptimizedChartRenderer()
        
        start_time = time.time()
        donut_config = chart_renderer.generate_optimized_donut_chart(test_results)
        donut_time = time.time() - start_time
        
        start_time = time.time()
        bar_config = chart_renderer.generate_optimized_bar_chart(test_results)
        bar_time = time.time() - start_time
        
        assert donut_time < 1.0, f"도넛 차트 생성 시간이 너무 깁니다: {donut_time:.2f}초"
        assert bar_time < 1.0, f"막대 차트 생성 시간이 너무 깁니다: {bar_time:.2f}초"
        
        # 7. DataFrame 내보내기 테스트
        start_time = time.time()
        df = processor.export_to_dataframe(test_results)
        export_time = time.time() - start_time
        
        assert len(df) == len(test_results)
        assert export_time < 2.0, f"DataFrame 내보내기 시간이 너무 깁니다: {export_time:.2f}초"
        
        print(f"✅ 소규모 파일 워크플로우 테스트 완료")
        print(f"   - 파싱 시간: {parse_time:.3f}초")
        print(f"   - 도넛 차트: {donut_time:.3f}초")
        print(f"   - 막대 차트: {bar_time:.3f}초")
        print(f"   - 내보내기: {export_time:.3f}초")
    
    def test_complete_workflow_large_file(self, temp_large_excel_file):
        """대용량 파일 전체 워크플로우 테스트"""
        # 1. 파일 검증
        validator = FileValidator()
        validation_result = validator.validate_file(temp_large_excel_file)
        assert validation_result['is_valid'], f"파일 검증 실패: {validation_result['errors']}"
        
        # 2. 성능 최적화기 초기화
        optimizer = PerformanceOptimizer()
        
        # 3. 대용량 데이터 처리
        processor = DataProcessor()
        start_time = time.time()
        test_results = processor.parse_excel_file(temp_large_excel_file)
        parse_time = time.time() - start_time
        
        assert len(test_results) > 4000, "대용량 데이터 파싱 결과가 부족합니다"
        assert parse_time < 30.0, f"대용량 파일 파싱 시간이 너무 깁니다: {parse_time:.2f}초"
        
        # 4. 메모리 사용량 확인
        memory_usage = optimizer.memory_monitor.get_current_memory()
        assert memory_usage < 500, f"메모리 사용량이 너무 높습니다: {memory_usage:.1f}MB"
        
        # 5. 대시보드 업데이트 (대용량 데이터)
        dashboard_engine = DynamicDashboardEngine(processor)
        start_time = time.time()
        dashboard_engine.update_dashboard(test_results, "large_test_file.xlsx")
        dashboard_time = time.time() - start_time
        
        assert dashboard_time < 10.0, f"대시보드 업데이트 시간이 너무 깁니다: {dashboard_time:.2f}초"
        
        # 6. 최적화된 차트 렌더링 (대용량 데이터)
        chart_renderer = OptimizedChartRenderer()
        
        start_time = time.time()
        donut_config = chart_renderer.generate_optimized_donut_chart(test_results)
        donut_time = time.time() - start_time
        
        start_time = time.time()
        bar_config = chart_renderer.generate_optimized_bar_chart(test_results)
        bar_time = time.time() - start_time
        
        # 대용량 데이터에서도 합리적인 시간 내에 완료되어야 함
        assert donut_time < 3.0, f"대용량 도넛 차트 생성 시간이 너무 깁니다: {donut_time:.2f}초"
        assert bar_time < 3.0, f"대용량 막대 차트 생성 시간이 너무 깁니다: {bar_time:.2f}초"
        
        # 7. 데이터 포인트 수 제한 확인 (최적화 검증)
        donut_series = donut_config.get('series', [])
        bar_data = bar_config.get('series', [{}])[0].get('data', [])
        
        assert len(donut_series) <= 1000, f"도넛 차트 데이터 포인트가 너무 많습니다: {len(donut_series)}"
        assert len(bar_data) <= 1000, f"막대 차트 데이터 포인트가 너무 많습니다: {len(bar_data)}"
        
        # 8. 성능 보고서 확인
        performance_report = optimizer.get_performance_report()
        assert performance_report['total_operations'] > 0
        assert performance_report['success_rate'] > 90  # 90% 이상 성공률
        
        print(f"✅ 대용량 파일 워크플로우 테스트 완료")
        print(f"   - 데이터 크기: {len(test_results)}행")
        print(f"   - 파싱 시간: {parse_time:.3f}초")
        print(f"   - 대시보드 업데이트: {dashboard_time:.3f}초")
        print(f"   - 도넛 차트: {donut_time:.3f}초")
        print(f"   - 막대 차트: {bar_time:.3f}초")
        print(f"   - 메모리 사용량: {memory_usage:.1f}MB")
        print(f"   - 성공률: {performance_report['success_rate']:.1f}%")
    
    def test_error_handling_workflow(self):
        """에러 처리 워크플로우 테스트"""
        processor = DataProcessor()
        error_handler = ErrorHandler()
        
        # 1. 존재하지 않는 파일 테스트
        with pytest.raises(Exception):
            processor.parse_excel_file("nonexistent_file.xlsx")
        
        # 2. 잘못된 형식 파일 테스트
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b"This is not an Excel file")
            tmp_file.flush()
            
            try:
                with pytest.raises(Exception):
                    processor.parse_excel_file(tmp_file.name)
            finally:
                os.unlink(tmp_file.name)
        
        # 3. 빈 데이터 처리 테스트
        empty_data = pd.DataFrame()
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            empty_data.to_excel(tmp_file.name, index=False)
            
            try:
                validation_result = processor.validate_data_structure(empty_data)
                assert not validation_result['is_valid']
                assert '데이터가 없습니다' in str(validation_result['errors'])
            finally:
                os.unlink(tmp_file.name)
        
        # 4. 필수 컬럼 누락 테스트
        incomplete_data = pd.DataFrame({
            'No.': [1, 2, 3],
            '시료명': ['A', 'B', 'C']
            # 필수 컬럼들이 누락됨
        })
        
        validation_result = processor.validate_data_structure(incomplete_data)
        assert not validation_result['is_valid']
        assert '필수 컬럼 누락' in str(validation_result['errors'])
        
        print("✅ 에러 처리 워크플로우 테스트 완료")
    
    def test_caching_performance(self, temp_excel_file):
        """캐싱 성능 테스트"""
        processor = DataProcessor()
        optimizer = PerformanceOptimizer()
        
        # 첫 번째 호출 (캐시 미스)
        start_time = time.time()
        test_results1 = processor.parse_excel_file(temp_excel_file)
        first_call_time = time.time() - start_time
        
        # 프로젝트 요약 첫 번째 호출
        start_time = time.time()
        summary1 = processor.get_project_summary("TEST_PROJECT", test_results1)
        first_summary_time = time.time() - start_time
        
        # 두 번째 호출 (캐시 히트 - 같은 데이터)
        start_time = time.time()
        summary2 = processor.get_project_summary("TEST_PROJECT", test_results1)
        second_summary_time = time.time() - start_time
        
        # 캐시 효과 검증
        assert second_summary_time < first_summary_time, "캐시 효과가 없습니다"
        
        # 캐시된 결과가 동일한지 확인
        assert summary1.project_name == summary2.project_name
        assert summary1.total_tests == summary2.total_tests
        assert summary1.violation_rate == summary2.violation_rate
        
        # 캐시 통계 확인
        cache_stats = optimizer.cache.get_stats()
        assert cache_stats['size'] > 0, "캐시에 데이터가 저장되지 않았습니다"
        
        print(f"✅ 캐싱 성능 테스트 완료")
        print(f"   - 첫 번째 요약 생성: {first_summary_time:.3f}초")
        print(f"   - 두 번째 요약 생성: {second_summary_time:.3f}초")
        print(f"   - 캐시 효과: {first_summary_time / max(second_summary_time, 0.001):.1f}배 빠름")
        print(f"   - 캐시 크기: {cache_stats['size']}")
    
    def test_memory_optimization(self, temp_large_excel_file):
        """메모리 최적화 테스트"""
        processor = DataProcessor()
        optimizer = PerformanceOptimizer()
        
        # 메모리 모니터링 시작
        initial_memory = optimizer.memory_monitor.get_current_memory()
        
        # 대용량 데이터 처리
        test_results = processor.parse_excel_file(temp_large_excel_file)
        
        # DataFrame 변환 및 최적화
        df = processor.export_to_dataframe(test_results)
        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        optimized_df = optimizer.optimize_dataframe_memory(df)
        optimized_memory = optimized_df.memory_usage(deep=True).sum() / 1024 / 1024
        
        # 메모리 최적화 효과 검증
        memory_reduction = (original_memory - optimized_memory) / original_memory * 100
        assert memory_reduction > 0, "메모리 최적화 효과가 없습니다"
        
        # 최종 메모리 사용량 확인
        final_memory = optimizer.memory_monitor.get_current_memory()
        memory_increase = final_memory - initial_memory
        
        # 메모리 증가량이 합리적인 범위 내인지 확인
        assert memory_increase < 200, f"메모리 사용량이 너무 많이 증가했습니다: {memory_increase:.1f}MB"
        
        print(f"✅ 메모리 최적화 테스트 완료")
        print(f"   - 원본 DataFrame: {original_memory:.1f}MB")
        print(f"   - 최적화된 DataFrame: {optimized_memory:.1f}MB")
        print(f"   - 메모리 절약: {memory_reduction:.1f}%")
        print(f"   - 총 메모리 증가: {memory_increase:.1f}MB")
    
    def test_concurrent_processing(self, temp_excel_file):
        """동시 처리 테스트"""
        import threading
        import queue
        
        processor = DataProcessor()
        results_queue = queue.Queue()
        errors_queue = queue.Queue()
        
        def process_file(file_path, thread_id):
            try:
                start_time = time.time()
                test_results = processor.parse_excel_file(file_path)
                processing_time = time.time() - start_time
                
                results_queue.put({
                    'thread_id': thread_id,
                    'results_count': len(test_results),
                    'processing_time': processing_time
                })
            except Exception as e:
                errors_queue.put({
                    'thread_id': thread_id,
                    'error': str(e)
                })
        
        # 5개 스레드로 동시 처리
        threads = []
        for i in range(5):
            thread = threading.Thread(target=process_file, args=(temp_excel_file, i))
            threads.append(thread)
            thread.start()
        
        # 모든 스레드 완료 대기
        for thread in threads:
            thread.join(timeout=30)  # 30초 타임아웃
        
        # 결과 검증
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        errors = []
        while not errors_queue.empty():
            errors.append(errors_queue.get())
        
        assert len(results) == 5, f"일부 스레드가 완료되지 않았습니다: {len(results)}/5"
        assert len(errors) == 0, f"처리 중 오류 발생: {errors}"
        
        # 모든 스레드가 동일한 결과를 반환하는지 확인
        first_result_count = results[0]['results_count']
        for result in results:
            assert result['results_count'] == first_result_count, "스레드별 결과가 다릅니다"
        
        avg_processing_time = sum(r['processing_time'] for r in results) / len(results)
        
        print(f"✅ 동시 처리 테스트 완료")
        print(f"   - 성공한 스레드: {len(results)}/5")
        print(f"   - 평균 처리 시간: {avg_processing_time:.3f}초")
        print(f"   - 결과 일관성: ✓")


if __name__ == "__main__":
    # 테스트 실행
    test_class = TestCompleteWorkflow()
    
    # 샘플 데이터로 테스트 실행
    sample_data = test_class.sample_excel_data()
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        sample_data.to_excel(tmp_file.name, index=False)
        
        try:
            print("🧪 전체 워크플로우 통합 테스트 시작")
            test_class.test_complete_workflow_small_file(tmp_file.name)
            test_class.test_error_handling_workflow()
            test_class.test_caching_performance(tmp_file.name)
            test_class.test_concurrent_processing(tmp_file.name)
            print("🎉 모든 통합 테스트 완료!")
            
        finally:
            if os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)