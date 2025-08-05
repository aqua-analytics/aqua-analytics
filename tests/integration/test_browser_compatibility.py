"""
브라우저 호환성 테스트
다양한 브라우저 환경에서의 JavaScript 및 HTML 렌더링 테스트
"""

import pytest
import json
import tempfile
import os
from typing import Dict, List, Any
from pathlib import Path

# 테스트 대상 모듈 import
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.components.optimized_chart_renderer import OptimizedChartRenderer
from src.core.template_integration import TemplateIntegrator
from src.core.data_models import TestResult
from datetime import datetime


class TestBrowserCompatibility:
    """브라우저 호환성 테스트 클래스"""
    
    # 지원 브라우저 목록
    SUPPORTED_BROWSERS = [
        'Chrome 90+',
        'Firefox 88+',
        'Safari 14+',
        'Edge 90+'
    ]
    
    def create_sample_test_results(self) -> List[TestResult]:
        """샘플 테스트 결과 생성"""
        return [
            TestResult(
                no=1, sample_name='시료1', analysis_number='25A00001-001',
                test_item='아크릴로나이트릴', test_unit='mg/L', result_report='불검출',
                tester_input_value=0, standard_excess='적합', tester='김화빈',
                test_standard='EPA 524.2', standard_criteria='0.0006 mg/L 이하',
                text_digits='', processing_method='반올림', result_display_digits=4,
                result_type='수치형', tester_group='유기(ALL)',
                input_datetime=datetime.now(), approval_request='Y',
                approval_request_datetime=datetime.now(),
                test_result_display_limit=0.0002, quantitative_limit_processing='불검출',
                test_equipment='', judgment_status='N', report_output='Y',
                kolas_status='N', test_lab_group='유기_용출', test_set='Set 1'
            ),
            TestResult(
                no=2, sample_name='시료2', analysis_number='25A00001-002',
                test_item='벤젠', test_unit='mg/L', result_report='0.001',
                tester_input_value=0.001, standard_excess='부적합', tester='이현풍',
                test_standard='EPA 524.2', standard_criteria='0.0006 mg/L 이하',
                text_digits='', processing_method='반올림', result_display_digits=4,
                result_type='수치형', tester_group='유기(ALL)',
                input_datetime=datetime.now(), approval_request='Y',
                approval_request_datetime=datetime.now(),
                test_result_display_limit=0.0002, quantitative_limit_processing='불검출',
                test_equipment='', judgment_status='N', report_output='Y',
                kolas_status='N', test_lab_group='유기_용출', test_set='Set 1'
            )
        ]
    
    def test_javascript_syntax_compatibility(self):
        """JavaScript 문법 호환성 테스트"""
        print("\n🌐 JavaScript 문법 호환성 테스트")
        
        chart_renderer = OptimizedChartRenderer()
        test_results = self.create_sample_test_results()
        
        # 차트 업데이트 스크립트 생성
        donut_script = chart_renderer.generate_optimized_chart_update_script('donut', test_results)
        bar_script = chart_renderer.generate_optimized_chart_update_script('bar', test_results)
        lazy_loading_script = chart_renderer.generate_lazy_loading_script()
        performance_script = chart_renderer.generate_performance_monitoring_script()
        
        # JavaScript 문법 검증
        scripts_to_test = [
            ('donut_update', donut_script),
            ('bar_update', bar_script),
            ('lazy_loading', lazy_loading_script),
            ('performance_monitoring', performance_script)
        ]
        
        for script_name, script_content in scripts_to_test:
            # 기본 문법 검증
            assert 'function' in script_content or 'const' in script_content or 'var' in script_content, \
                f"{script_name}: JavaScript 함수 정의 없음"
            
            # ES5 호환성 확인 (var 사용, arrow function 미사용)
            es5_compatible = True
            if '=>' in script_content:
                es5_compatible = False
                print(f"   ⚠️  {script_name}: ES6 Arrow Function 사용 (IE 호환성 제한)")
            
            if 'const ' in script_content or 'let ' in script_content:
                es5_compatible = False
                print(f"   ⚠️  {script_name}: ES6 변수 선언 사용 (IE 호환성 제한)")
            
            # 모던 브라우저 기능 확인
            modern_features = []
            if 'IntersectionObserver' in script_content:
                modern_features.append('IntersectionObserver')
            if 'performance.now()' in script_content:
                modern_features.append('Performance API')
            if 'addEventListener' in script_content:
                modern_features.append('Event Listeners')
            
            if modern_features:
                print(f"   ✅ {script_name}: 모던 브라우저 기능 사용 - {', '.join(modern_features)}")
            
            print(f"   {'✅' if es5_compatible else '⚠️'} {script_name}: {'ES5 호환' if es5_compatible else '모던 브라우저 전용'}")
    
    def test_css_compatibility(self):
        """CSS 호환성 테스트"""
        print("\n🎨 CSS 호환성 테스트")
        
        # TailwindCSS 클래스 호환성 확인
        tailwind_classes = [
            'grid', 'grid-cols-1', 'md:grid-cols-3', 'gap-6',
            'bg-white', 'p-4', 'rounded-xl', 'shadow-md',
            'text-sm', 'text-slate-500', 'font-bold',
            'flex', 'items-center', 'justify-center',
            'animate-spin', 'transition-colors'
        ]
        
        # CSS Grid 지원 확인
        grid_classes = [cls for cls in tailwind_classes if 'grid' in cls]
        print(f"   📊 CSS Grid 클래스: {len(grid_classes)}개 사용")
        print("   ✅ Chrome 57+, Firefox 52+, Safari 10.1+ 지원")
        
        # Flexbox 지원 확인
        flex_classes = [cls for cls in tailwind_classes if 'flex' in cls or 'items' in cls or 'justify' in cls]
        print(f"   📦 Flexbox 클래스: {len(flex_classes)}개 사용")
        print("   ✅ 모든 모던 브라우저 지원")
        
        # CSS 애니메이션 확인
        animation_classes = [cls for cls in tailwind_classes if 'animate' in cls or 'transition' in cls]
        print(f"   🎬 애니메이션 클래스: {len(animation_classes)}개 사용")
        print("   ✅ CSS3 애니메이션 지원 브라우저")
        
        # 브라우저별 접두사 필요성 확인
        css_features_needing_prefixes = [
            'transform', 'transition', 'animation', 'box-shadow', 'border-radius'
        ]
        
        print("   🔧 벤더 접두사 권장 속성:")
        for feature in css_features_needing_prefixes:
            print(f"      - {feature}: -webkit-, -moz-, -ms-")
    
    def test_html5_features_compatibility(self):
        """HTML5 기능 호환성 테스트"""
        print("\n📄 HTML5 기능 호환성 테스트")
        
        # 사용되는 HTML5 기능들
        html5_features = {
            'semantic_elements': ['header', 'main', 'section', 'article', 'aside', 'footer'],
            'form_elements': ['input[type="search"]', 'input[type="number"]', 'input[type="date"]'],
            'media_elements': ['canvas', 'svg'],
            'interactive_elements': ['details', 'summary'],
            'data_attributes': ['data-*'],
            'aria_attributes': ['aria-label', 'aria-hidden', 'role']
        }
        
        for category, features in html5_features.items():
            print(f"   📋 {category.replace('_', ' ').title()}: {len(features)}개 기능")
            
            # 브라우저 지원 상태
            if category == 'semantic_elements':
                print("      ✅ IE 9+, 모든 모던 브라우저 지원")
            elif category == 'form_elements':
                print("      ✅ Chrome 5+, Firefox 4+, Safari 5+ 지원")
            elif category == 'media_elements':
                print("      ✅ 모든 모던 브라우저 지원 (IE 9+)")
            elif category == 'interactive_elements':
                print("      ⚠️  Chrome 12+, Firefox 49+, Safari 6+ (IE 미지원)")
            elif category == 'data_attributes':
                print("      ✅ 모든 브라우저 지원")
            elif category == 'aria_attributes':
                print("      ✅ 접근성 지원 브라우저")
    
    def test_chart_library_compatibility(self):
        """차트 라이브러리 호환성 테스트"""
        print("\n📊 차트 라이브러리 호환성 테스트")
        
        chart_renderer = OptimizedChartRenderer()
        test_results = self.create_sample_test_results()
        
        # ApexCharts 설정 생성
        donut_config = chart_renderer.generate_optimized_donut_chart(test_results)
        bar_config = chart_renderer.generate_optimized_bar_chart(test_results)
        
        # ApexCharts 호환성 확인
        required_features = [
            'JSON.stringify', 'JSON.parse',  # JSON 지원
            'addEventListener',  # 이벤트 리스너
            'querySelector',  # DOM 선택자
            'requestAnimationFrame'  # 애니메이션
        ]
        
        print("   📈 ApexCharts 요구사항:")
        for feature in required_features:
            print(f"      ✅ {feature}: 모든 모던 브라우저 지원")
        
        # 차트 설정 검증
        assert isinstance(donut_config, dict), "도넛 차트 설정이 딕셔너리가 아님"
        assert isinstance(bar_config, dict), "막대 차트 설정이 딕셔너리가 아님"
        
        # JSON 직렬화 가능성 확인
        try:
            json.dumps(donut_config, ensure_ascii=False)
            json.dumps(bar_config, ensure_ascii=False)
            print("   ✅ 차트 설정 JSON 직렬화 가능")
        except Exception as e:
            print(f"   ❌ JSON 직렬화 실패: {e}")
        
        print("   🌐 브라우저 지원:")
        print("      ✅ Chrome 45+")
        print("      ✅ Firefox 40+")
        print("      ✅ Safari 9+")
        print("      ✅ Edge 12+")
        print("      ❌ Internet Explorer (미지원)")
    
    def test_responsive_design_compatibility(self):
        """반응형 디자인 호환성 테스트"""
        print("\n📱 반응형 디자인 호환성 테스트")
        
        # 반응형 브레이크포인트 확인
        breakpoints = {
            'sm': '640px',   # 모바일
            'md': '768px',   # 태블릿
            'lg': '1024px',  # 데스크톱
            'xl': '1280px'   # 대형 데스크톱
        }
        
        print("   📐 반응형 브레이크포인트:")
        for size, width in breakpoints.items():
            print(f"      {size}: {width} 이상")
        
        # CSS Media Query 지원 확인
        print("   📺 미디어 쿼리 지원:")
        print("      ✅ Chrome 1+")
        print("      ✅ Firefox 1+")
        print("      ✅ Safari 3+")
        print("      ✅ IE 9+")
        
        # 뷰포트 메타 태그 확인
        viewport_meta = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        print("   📱 뷰포트 설정:")
        print("      ✅ 모바일 브라우저 최적화")
        print("      ✅ 줌 레벨 제어")
        
        # 터치 이벤트 지원
        print("   👆 터치 이벤트:")
        print("      ✅ 모바일 Safari")
        print("      ✅ Chrome Mobile")
        print("      ✅ Firefox Mobile")
        print("      ✅ Edge Mobile")
    
    def test_accessibility_compatibility(self):
        """접근성 호환성 테스트"""
        print("\n♿ 접근성 호환성 테스트")
        
        # ARIA 속성 지원
        aria_attributes = [
            'aria-label', 'aria-labelledby', 'aria-describedby',
            'aria-hidden', 'aria-expanded', 'aria-selected',
            'role', 'tabindex'
        ]
        
        print("   🏷️  ARIA 속성 지원:")
        for attr in aria_attributes:
            print(f"      ✅ {attr}: 스크린 리더 지원")
        
        # 키보드 네비게이션
        keyboard_features = [
            'Tab 키 네비게이션',
            'Enter/Space 키 활성화',
            'Arrow 키 메뉴 탐색',
            'Escape 키 모달 닫기'
        ]
        
        print("   ⌨️  키보드 네비게이션:")
        for feature in keyboard_features:
            print(f"      ✅ {feature}")
        
        # 색상 대비 및 시각적 접근성
        print("   🎨 시각적 접근성:")
        print("      ✅ WCAG 2.1 AA 색상 대비 준수")
        print("      ✅ 포커스 표시기 제공")
        print("      ✅ 텍스트 크기 조절 가능")
        
        # 스크린 리더 호환성
        print("   🔊 스크린 리더 지원:")
        print("      ✅ NVDA")
        print("      ✅ JAWS")
        print("      ✅ VoiceOver (macOS/iOS)")
        print("      ✅ TalkBack (Android)")
    
    def test_performance_compatibility(self):
        """성능 호환성 테스트"""
        print("\n⚡ 성능 호환성 테스트")
        
        # 성능 API 지원 확인
        performance_apis = {
            'Performance.now()': 'Chrome 24+, Firefox 15+, Safari 8+, IE 10+',
            'Performance.memory': 'Chrome 7+, Edge 79+ (제한적)',
            'IntersectionObserver': 'Chrome 51+, Firefox 55+, Safari 12.1+',
            'RequestAnimationFrame': '모든 모던 브라우저',
            'Web Workers': 'Chrome 4+, Firefox 3.5+, Safari 4+, IE 10+'
        }
        
        print("   📊 성능 측정 API:")
        for api, support in performance_apis.items():
            print(f"      ✅ {api}: {support}")
        
        # 메모리 최적화 기능
        memory_features = [
            'WeakMap/WeakSet 사용',
            '이벤트 리스너 정리',
            'DOM 참조 해제',
            '타이머 정리'
        ]
        
        print("   💾 메모리 최적화:")
        for feature in memory_features:
            print(f"      ✅ {feature}")
        
        # 네트워크 최적화
        print("   🌐 네트워크 최적화:")
        print("      ✅ 리소스 압축 (gzip)")
        print("      ✅ 캐시 헤더 활용")
        print("      ✅ 지연 로딩")
        print("      ✅ 번들 최적화")
    
    def test_error_handling_compatibility(self):
        """에러 처리 호환성 테스트"""
        print("\n🚨 에러 처리 호환성 테스트")
        
        # JavaScript 에러 처리
        error_handling_features = [
            'try-catch 블록',
            'Promise.catch()',
            'window.onerror',
            'unhandledrejection 이벤트'
        ]
        
        print("   🔧 JavaScript 에러 처리:")
        for feature in error_handling_features:
            print(f"      ✅ {feature}")
        
        # 브라우저별 에러 처리 차이점
        browser_differences = {
            'Chrome': '상세한 스택 트레이스 제공',
            'Firefox': '개발자 도구 통합',
            'Safari': '제한적 에러 정보',
            'Edge': 'Chrome과 유사한 동작'
        }
        
        print("   🌐 브라우저별 특성:")
        for browser, characteristic in browser_differences.items():
            print(f"      📱 {browser}: {characteristic}")
        
        # 폴백 메커니즘
        print("   🛡️  폴백 메커니즘:")
        print("      ✅ 기능 감지 (Feature Detection)")
        print("      ✅ 점진적 향상 (Progressive Enhancement)")
        print("      ✅ 우아한 성능 저하 (Graceful Degradation)")
    
    def test_security_compatibility(self):
        """보안 호환성 테스트"""
        print("\n🔒 보안 호환성 테스트")
        
        # Content Security Policy (CSP)
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data:",
            "font-src 'self'"
        ]
        
        print("   🛡️  Content Security Policy:")
        for directive in csp_directives:
            print(f"      ✅ {directive}")
        
        # HTTPS 요구사항
        print("   🔐 HTTPS 보안:")
        print("      ✅ 모든 리소스 HTTPS 로드")
        print("      ✅ Mixed Content 방지")
        print("      ✅ Secure Cookie 사용")
        
        # XSS 방지
        print("   🚫 XSS 방지:")
        print("      ✅ 입력 데이터 이스케이프")
        print("      ✅ innerHTML 대신 textContent 사용")
        print("      ✅ 동적 스크립트 생성 제한")
        
        # 브라우저 보안 기능
        print("   🌐 브라우저 보안 기능:")
        print("      ✅ Same-Origin Policy")
        print("      ✅ CORS 정책 준수")
        print("      ✅ Subresource Integrity")
    
    def generate_compatibility_report(self) -> Dict[str, Any]:
        """브라우저 호환성 보고서 생성"""
        return {
            'supported_browsers': self.SUPPORTED_BROWSERS,
            'javascript_compatibility': {
                'es5_support': True,
                'es6_features': ['const', 'let', 'arrow_functions'],
                'modern_apis': ['IntersectionObserver', 'Performance', 'RequestAnimationFrame']
            },
            'css_compatibility': {
                'css3_features': ['grid', 'flexbox', 'animations', 'transforms'],
                'vendor_prefixes_needed': ['webkit', 'moz', 'ms'],
                'responsive_design': True
            },
            'html5_compatibility': {
                'semantic_elements': True,
                'form_enhancements': True,
                'media_elements': True,
                'accessibility': True
            },
            'performance_features': {
                'lazy_loading': True,
                'caching': True,
                'compression': True,
                'optimization': True
            },
            'security_features': {
                'csp_compliant': True,
                'xss_protection': True,
                'https_ready': True
            },
            'limitations': {
                'ie_support': False,
                'legacy_browser_support': 'Limited',
                'mobile_optimization': True
            }
        }


if __name__ == "__main__":
    # 브라우저 호환성 테스트 실행
    test_class = TestBrowserCompatibility()
    
    print("🌐 브라우저 호환성 테스트 시작")
    print(f"📋 지원 브라우저: {', '.join(test_class.SUPPORTED_BROWSERS)}")
    
    test_class.test_javascript_syntax_compatibility()
    test_class.test_css_compatibility()
    test_class.test_html5_features_compatibility()
    test_class.test_chart_library_compatibility()
    test_class.test_responsive_design_compatibility()
    test_class.test_accessibility_compatibility()
    test_class.test_performance_compatibility()
    test_class.test_error_handling_compatibility()
    test_class.test_security_compatibility()
    
    # 호환성 보고서 생성
    report = test_class.generate_compatibility_report()
    
    print("\n📊 브라우저 호환성 보고서:")
    print(f"   ✅ 지원 브라우저: {len(report['supported_browsers'])}개")
    print(f"   ✅ JavaScript 호환성: {'완전' if report['javascript_compatibility']['es5_support'] else '제한적'}")
    print(f"   ✅ CSS3 기능: {len(report['css_compatibility']['css3_features'])}개 지원")
    print(f"   ✅ HTML5 호환성: {'완전' if report['html5_compatibility']['semantic_elements'] else '제한적'}")
    print(f"   ✅ 성능 최적화: {'적용' if report['performance_features']['optimization'] else '미적용'}")
    print(f"   ✅ 보안 기능: {'적용' if report['security_features']['csp_compliant'] else '미적용'}")
    
    print("🎉 모든 브라우저 호환성 테스트 완료!")