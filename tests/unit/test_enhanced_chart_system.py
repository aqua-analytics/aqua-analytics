"""
향상된 차트 시스템 테스트
부적합 통계 차트 구현 검증
"""

import unittest
import json
from unittest.mock import Mock, patch
from src.components.chart_system import ChartSystem
from src.core.data_models import TestResult
from datetime import datetime


class TestEnhancedChartSystem(unittest.TestCase):
    """향상된 차트 시스템 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.chart_system = ChartSystem()
        
        # 테스트용 샘플 데이터
        self.sample_test_results = [
            TestResult(
                no=1,
                sample_name="냉수탱크",
                analysis_number="25A00009-001",
                test_item="pH",
                test_unit="",
                result_report="7.2",
                tester_input_value=7.2,
                standard_excess="부적합",
                tester="김화빈",
                test_standard="EPA 524.2",
                standard_criteria="6.5-8.5",
                text_digits="",
                processing_method="",
                result_display_digits=1,
                result_type="",
                tester_group="",
                input_datetime=datetime(2025, 1, 23, 9, 56),
                approval_request="",
                approval_request_datetime=None,
                test_result_display_limit=0,
                quantitative_limit_processing="",
                test_equipment="",
                judgment_status="",
                report_output="",
                kolas_status="",
                test_lab_group="",
                test_set=""
            ),
            TestResult(
                no=2,
                sample_name="온수탱크",
                analysis_number="25A00009-002",
                test_item="대장균",
                test_unit="CFU/mL",
                result_report="5",
                tester_input_value=5,
                standard_excess="부적합",
                tester="이현풍",
                test_standard="Standard Methods",
                standard_criteria="0 CFU/mL",
                text_digits="",
                processing_method="",
                result_display_digits=0,
                result_type="",
                tester_group="",
                input_datetime=datetime(2025, 1, 23, 10, 30),
                approval_request="",
                approval_request_datetime=None,
                test_result_display_limit=0,
                quantitative_limit_processing="",
                test_equipment="",
                judgment_status="",
                report_output="",
                kolas_status="",
                test_lab_group="",
                test_set=""
            ),
            TestResult(
                no=3,
                sample_name="제품#1",
                analysis_number="25A00089-002",
                test_item="탁도",
                test_unit="NTU",
                result_report="0.8",
                tester_input_value=0.8,
                standard_excess="적합",
                tester="김화빈",
                test_standard="EPA 180.1",
                standard_criteria="1.0 NTU 이하",
                text_digits="",
                processing_method="",
                result_display_digits=1,
                result_type="",
                tester_group="",
                input_datetime=datetime(2025, 1, 23, 11, 15),
                approval_request="",
                approval_request_datetime=None,
                test_result_display_limit=0,
                quantitative_limit_processing="",
                test_equipment="",
                judgment_status="",
                report_output="",
                kolas_status="",
                test_lab_group="",
                test_set=""
            )
        ]
    
    def test_enhanced_donut_chart_generation(self):
        """향상된 도넛 차트 생성 테스트"""
        chart_config = self.chart_system.generate_non_conforming_donut_chart(self.sample_test_results)
        
        # 기본 구조 검증
        self.assertIn('chart', chart_config)
        self.assertIn('series', chart_config)
        self.assertIn('labels', chart_config)
        self.assertIn('colors', chart_config)
        
        # 차트 타입 검증
        self.assertEqual(chart_config['chart']['type'], 'donut')
        self.assertEqual(chart_config['chart']['height'], 380)
        
        # 애니메이션 설정 검증
        animations = chart_config['chart']['animations']
        self.assertTrue(animations['enabled'])
        self.assertEqual(animations['speed'], 1500)
        self.assertEqual(animations['animateGradually']['delay'], 300)
        self.assertEqual(animations['dynamicAnimation']['speed'], 800)
        
        # 데이터 검증 (부적합 항목만)
        expected_series = [1, 1]  # pH, 대장균 각각 1건
        expected_labels = ["pH", "대장균"]
        self.assertEqual(chart_config['series'], expected_series)
        self.assertEqual(chart_config['labels'], expected_labels)
        
        # 도넛 설정 검증
        donut_config = chart_config['plotOptions']['pie']['donut']
        self.assertEqual(donut_config['size'], '68%')
        self.assertTrue(donut_config['labels']['show'])
        self.assertEqual(donut_config['customScale'], 1.15)
        
        # 드롭 섀도우 검증
        shadow = chart_config['chart']['dropShadow']
        self.assertTrue(shadow['enabled'])
        self.assertEqual(shadow['blur'], 6)
        self.assertEqual(shadow['opacity'], 0.15)
    
    def test_enhanced_bar_chart_generation(self):
        """향상된 수평 막대 차트 생성 테스트"""
        chart_config = self.chart_system.generate_non_conforming_bar_chart(self.sample_test_results)
        
        # 기본 구조 검증
        self.assertIn('chart', chart_config)
        self.assertIn('series', chart_config)
        self.assertIn('plotOptions', chart_config)
        
        # 차트 타입 검증
        self.assertEqual(chart_config['chart']['type'], 'bar')
        self.assertEqual(chart_config['chart']['height'], 420)
        
        # 애니메이션 설정 검증
        animations = chart_config['chart']['animations']
        self.assertTrue(animations['enabled'])
        self.assertEqual(animations['speed'], 1800)
        self.assertEqual(animations['animateGradually']['delay'], 400)
        self.assertEqual(animations['dynamicAnimation']['speed'], 1000)
        
        # 막대 차트 설정 검증
        bar_config = chart_config['plotOptions']['bar']
        self.assertTrue(bar_config['horizontal'])
        self.assertEqual(bar_config['borderRadius'], 8)
        self.assertEqual(bar_config['barHeight'], '65%')
        
        # 그라데이션 설정 검증
        gradient = chart_config['fill']['gradient']
        self.assertEqual(gradient['type'], 'horizontal')
        self.assertEqual(gradient['shadeIntensity'], 0.5)
        self.assertEqual(len(gradient['colorStops']), 4)
        
        # 색상 정지점 검증
        color_stops = gradient['colorStops']
        self.assertEqual(color_stops[0]['color'], '#dc2626')
        self.assertEqual(color_stops[0]['opacity'], 1)
        self.assertEqual(color_stops[-1]['color'], '#fca5a5')
        self.assertEqual(color_stops[-1]['opacity'], 0.85)
    
    def test_chart_data_dynamic_update(self):
        """차트 데이터 동적 업데이트 테스트"""
        # 도넛 차트 업데이트
        donut_config = self.chart_system.update_chart_data('donut', self.sample_test_results)
        self.assertIn('series', donut_config)
        self.assertIn('labels', donut_config)
        
        # 막대 차트 업데이트
        bar_config = self.chart_system.update_chart_data('bar', self.sample_test_results)
        self.assertIn('series', bar_config)
        self.assertIn('xaxis', bar_config)
        
        # 잘못된 차트 ID 테스트
        with self.assertRaises(ValueError):
            self.chart_system.update_chart_data('invalid', self.sample_test_results)
    
    def test_chart_update_script_generation(self):
        """차트 업데이트 스크립트 생성 테스트"""
        # 도넛 차트 업데이트 스크립트
        donut_script = self.chart_system.get_chart_update_script('donut', self.sample_test_results)
        self.assertIn('window.donutChart', donut_script)
        self.assertIn('updateOptions', donut_script)
        
        # 막대 차트 업데이트 스크립트
        bar_script = self.chart_system.get_chart_update_script('bar', self.sample_test_results)
        self.assertIn('window.barChart', bar_script)
        self.assertIn('updateOptions', bar_script)
        
        # 잘못된 차트 ID
        invalid_script = self.chart_system.get_chart_update_script('invalid', self.sample_test_results)
        self.assertEqual(invalid_script, "")
    
    def test_animation_update_script(self):
        """애니메이션 업데이트 스크립트 테스트"""
        animation_script = self.chart_system.update_charts_with_animation(self.sample_test_results)
        
        # 필수 함수들 포함 확인
        self.assertIn('updateChartsWithAnimation', animation_script)
        self.assertIn('fadeOutCharts', animation_script)
        self.assertIn('fadeInCharts', animation_script)
        self.assertIn('showChartLoading', animation_script)
        self.assertIn('hideChartLoading', animation_script)
        self.assertIn('showUpdateSuccess', animation_script)
        
        # 애니메이션 타이밍 확인
        self.assertIn('setTimeout', animation_script)
        self.assertIn('transition', animation_script)
        
        # 로딩 오버레이 스타일 확인
        self.assertIn('chart-loading-overlay', animation_script)
        self.assertIn('animate-spin', animation_script)
    
    def test_enhanced_chart_interactions(self):
        """향상된 차트 인터랙션 테스트"""
        interaction_script = self.chart_system.generate_enhanced_chart_interactions()
        
        # 필수 인터랙션 함수들 확인
        self.assertIn('initializeEnhancedChartInteractions', interaction_script)
        self.assertIn('showChartDetailModal', interaction_script)
        self.assertIn('closeChartDetailModal', interaction_script)
        self.assertIn('enhanceChartHoverEffects', interaction_script)
        self.assertIn('exportChart', interaction_script)
        
        # 이벤트 리스너 확인
        self.assertIn('dataPointSelection', interaction_script)
        self.assertIn('addEventListener', interaction_script)
        
        # 모달 구조 확인
        self.assertIn('chart-detail-modal', interaction_script)
        self.assertIn('상세 정보', interaction_script)
        self.assertIn('개선 권고사항', interaction_script)
    
    def test_empty_data_handling(self):
        """빈 데이터 처리 테스트"""
        empty_results = []
        
        # 빈 도넛 차트
        empty_donut = self.chart_system.generate_non_conforming_donut_chart(empty_results)
        self.assertIn('series', empty_donut)
        self.assertEqual(empty_donut['series'], [1])
        self.assertEqual(empty_donut['labels'], ['데이터 없음'])
        
        # 빈 막대 차트
        empty_bar = self.chart_system.generate_non_conforming_bar_chart(empty_results)
        self.assertIn('series', empty_bar)
        self.assertEqual(empty_bar['series'][0]['data'], [])
    
    def test_chart_configuration_consistency(self):
        """차트 설정 일관성 테스트"""
        donut_config = self.chart_system.generate_non_conforming_donut_chart(self.sample_test_results)
        bar_config = self.chart_system.generate_non_conforming_bar_chart(self.sample_test_results)
        
        # 공통 설정 확인
        self.assertEqual(donut_config['chart']['fontFamily'], bar_config['chart']['fontFamily'])
        self.assertTrue(donut_config['chart']['animations']['enabled'])
        self.assertTrue(bar_config['chart']['animations']['enabled'])
        
        # 드롭 섀도우 설정 일관성
        donut_shadow = donut_config['chart']['dropShadow']
        bar_shadow = bar_config['chart']['dropShadow']
        self.assertEqual(donut_shadow['blur'], bar_shadow['blur'])
        self.assertEqual(donut_shadow['opacity'], bar_shadow['opacity'])
    
    def test_responsive_configuration(self):
        """반응형 설정 테스트"""
        chart_config = self.chart_system.generate_non_conforming_donut_chart(self.sample_test_results)
        
        # 반응형 브레이크포인트 확인
        self.assertIn('responsive', chart_config)
        responsive_config = chart_config['responsive']
        
        # 브레이크포인트 개수 확인
        self.assertGreater(len(responsive_config), 0)
        
        # 각 브레이크포인트 구조 확인
        for breakpoint in responsive_config:
            self.assertIn('breakpoint', breakpoint)
            self.assertIn('options', breakpoint)
    
    def test_color_palette_application(self):
        """색상 팔레트 적용 테스트"""
        chart_config = self.chart_system.generate_non_conforming_donut_chart(self.sample_test_results)
        
        # 색상 배열 확인
        self.assertIn('colors', chart_config)
        colors = chart_config['colors']
        
        # 기본 색상 팔레트 확인
        expected_colors = ['#ef4444', '#f59e0b', '#10b981']
        for i, color in enumerate(colors):
            if i < len(expected_colors):
                self.assertEqual(color, expected_colors[i])
    
    def test_performance_optimization(self):
        """성능 최적화 테스트"""
        # 대량 데이터 시뮬레이션
        large_dataset = []
        for i in range(100):
            result = TestResult(
                no=i,
                sample_name=f"샘플_{i}",
                analysis_number=f"25A{i:05d}-001",
                test_item=f"항목_{i % 10}",
                test_unit="mg/L",
                result_report="1.0",
                tester_input_value=1.0,
                standard_excess="부적합" if i % 3 == 0 else "적합",
                tester="테스터",
                test_standard="Standard",
                standard_criteria="0.5 mg/L 이하",
                text_digits="",
                processing_method="",
                result_display_digits=1,
                result_type="",
                tester_group="",
                input_datetime=datetime.now(),
                approval_request="",
                approval_request_datetime=None,
                test_result_display_limit=0,
                quantitative_limit_processing="",
                test_equipment="",
                judgment_status="",
                report_output="",
                kolas_status="",
                test_lab_group="",
                test_set=""
            )
            large_dataset.append(result)
        
        # 대량 데이터 처리 시간 측정
        import time
        start_time = time.time()
        
        donut_config = self.chart_system.generate_non_conforming_donut_chart(large_dataset)
        bar_config = self.chart_system.generate_non_conforming_bar_chart(large_dataset)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 처리 시간이 1초 이내인지 확인
        self.assertLess(processing_time, 1.0)
        
        # 결과 데이터 크기 확인 (상위 8개 항목만)
        self.assertLessEqual(len(donut_config['series']), 9)  # 8개 + 기타
        self.assertLessEqual(len(bar_config['series'][0]['data']), 8)


if __name__ == '__main__':
    unittest.main()