"""
모니터링 엔드포인트
Monitoring Endpoints

Task 13.1: 모니터링 설정 구현
- 헬스체크 엔드포인트
- 메트릭 엔드포인트
- 상태 대시보드
"""

import json
from typing import Dict, Any
from datetime import datetime
import streamlit as st

from src.utils.health_check import get_health_status, get_metrics
from src.utils.metrics import get_metrics_registry, get_app_metrics
from config.logging_config import get_logger

logger = get_logger(__name__)


class MonitoringEndpoints:
    """모니터링 엔드포인트 클래스"""
    
    def __init__(self):
        """모니터링 엔드포인트 초기화"""
        self.metrics_registry = get_metrics_registry()
        self.app_metrics = get_app_metrics()
    
    def health_endpoint(self) -> Dict[str, Any]:
        """헬스체크 엔드포인트"""
        try:
            health_status = get_health_status()
            
            # 간단한 헬스체크 응답
            if health_status['status'] == 'healthy':
                return {
                    'status': 'UP',
                    'timestamp': health_status['timestamp'],
                    'details': {
                        'uptime': health_status['uptime']['uptime_formatted'],
                        'checks_passed': len([c for c in health_status['checks'] if c['status'] == 'healthy']),
                        'total_checks': len(health_status['checks'])
                    }
                }
            else:
                return {
                    'status': 'DOWN',
                    'timestamp': health_status['timestamp'],
                    'details': health_status
                }
                
        except Exception as e:
            logger.exception("헬스체크 엔드포인트 오류")
            return {
                'status': 'ERROR',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def metrics_endpoint(self, format: str = 'json') -> str:
        """메트릭 엔드포인트"""
        try:
            if format.lower() == 'prometheus':
                return self.metrics_registry.get_prometheus_metrics()
            else:
                metrics_data = {
                    'timestamp': datetime.now().isoformat(),
                    'metrics': self.metrics_registry.get_metrics_dict()
                }
                return json.dumps(metrics_data, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.exception("메트릭 엔드포인트 오류")
            error_response = {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return json.dumps(error_response, indent=2, ensure_ascii=False)
    
    def detailed_health_endpoint(self) -> Dict[str, Any]:
        """상세 헬스체크 엔드포인트"""
        try:
            return get_health_status()
        except Exception as e:
            logger.exception("상세 헬스체크 엔드포인트 오류")
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def system_info_endpoint(self) -> Dict[str, Any]:
        """시스템 정보 엔드포인트"""
        try:
            health_status = get_health_status()
            return {
                'timestamp': datetime.now().isoformat(),
                'system': health_status.get('system', {}),
                'application': health_status.get('application', {}),
                'uptime': health_status.get('uptime', {})
            }
        except Exception as e:
            logger.exception("시스템 정보 엔드포인트 오류")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def render_monitoring_dashboard(self) -> None:
        """모니터링 대시보드 렌더링"""
        st.title("🔍 시스템 모니터링 대시보드")
        
        # 자동 새로고침 설정
        auto_refresh = st.sidebar.checkbox("자동 새로고침 (30초)", value=True)
        if auto_refresh:
            st.rerun()
        
        # 헬스체크 상태
        health_status = get_health_status()
        
        # 상태 표시
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_color = {
                'healthy': '🟢',
                'warning': '🟡',
                'unhealthy': '🔴',
                'error': '⚫'
            }.get(health_status['status'], '⚫')
            
            st.metric(
                label="시스템 상태",
                value=f"{status_color} {health_status['status'].upper()}"
            )
        
        with col2:
            uptime = health_status.get('uptime', {}).get('uptime_formatted', 'N/A')
            st.metric(label="업타임", value=uptime)
        
        with col3:
            checks = health_status.get('checks', [])
            healthy_checks = len([c for c in checks if c['status'] == 'healthy'])
            st.metric(
                label="헬스체크",
                value=f"{healthy_checks}/{len(checks)}"
            )
        
        # 시스템 메트릭
        st.subheader("📊 시스템 메트릭")
        
        system_metrics = health_status.get('system', {})
        if system_metrics and 'error' not in system_metrics:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                cpu_usage = system_metrics.get('cpu', {}).get('usage_percent', 0)
                st.metric(
                    label="CPU 사용률",
                    value=f"{cpu_usage:.1f}%",
                    delta=None
                )
            
            with col2:
                memory_usage = system_metrics.get('memory', {}).get('usage_percent', 0)
                st.metric(
                    label="메모리 사용률",
                    value=f"{memory_usage:.1f}%",
                    delta=None
                )
            
            with col3:
                disk_usage = system_metrics.get('disk', {}).get('usage_percent', 0)
                st.metric(
                    label="디스크 사용률",
                    value=f"{disk_usage:.1f}%",
                    delta=None
                )
        
        # 애플리케이션 메트릭
        st.subheader("🚀 애플리케이션 메트릭")
        
        app_metrics = health_status.get('application', {})
        if app_metrics and 'error' not in app_metrics:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                memory_mb = app_metrics.get('memory_usage', 0) / (1024 * 1024)
                st.metric(
                    label="앱 메모리 사용량",
                    value=f"{memory_mb:.1f} MB"
                )
            
            with col2:
                cpu_percent = app_metrics.get('cpu_usage', 0)
                st.metric(
                    label="앱 CPU 사용률",
                    value=f"{cpu_percent:.1f}%"
                )
            
            with col3:
                threads = app_metrics.get('threads', 0)
                st.metric(
                    label="스레드 수",
                    value=str(threads)
                )
        
        # 스토리지 정보
        st.subheader("💾 스토리지 정보")
        
        storage_metrics = health_status.get('storage', {})
        if storage_metrics and 'error' not in storage_metrics:
            for directory, info in storage_metrics.items():
                if isinstance(info, dict) and 'size_formatted' in info:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**{directory}**")
                    with col2:
                        st.write(f"{info['size_formatted']} ({info['file_count']} 파일)")
        
        # 헬스체크 상세 정보
        st.subheader("🔍 헬스체크 상세")
        
        checks = health_status.get('checks', [])
        for check in checks:
            status_icon = {
                'healthy': '✅',
                'warning': '⚠️',
                'unhealthy': '❌',
                'error': '💥'
            }.get(check['status'], '❓')
            
            with st.expander(f"{status_icon} {check['name']} - {check['status'].upper()}"):
                st.write(check['message'])
                if 'value' in check:
                    st.write(f"값: {check['value']}")
        
        # 메트릭 원시 데이터
        if st.sidebar.checkbox("원시 메트릭 데이터 표시"):
            st.subheader("📈 원시 메트릭 데이터")
            
            metrics_data = self.metrics_registry.get_metrics_dict()
            
            # 카운터
            if metrics_data['counters']:
                st.write("**카운터:**")
                st.json(metrics_data['counters'])
            
            # 게이지
            if metrics_data['gauges']:
                st.write("**게이지:**")
                st.json(metrics_data['gauges'])
            
            # 히스토그램
            if metrics_data['histograms']:
                st.write("**히스토그램:**")
                for name, values in metrics_data['histograms'].items():
                    if values:
                        st.write(f"- {name}: {len(values)} 값, 평균: {sum(values)/len(values):.2f}")
        
        # Prometheus 메트릭
        if st.sidebar.checkbox("Prometheus 메트릭 표시"):
            st.subheader("📊 Prometheus 메트릭")
            prometheus_metrics = self.metrics_registry.get_prometheus_metrics()
            st.code(prometheus_metrics, language='text')
        
        # 새로고침 버튼
        if st.button("🔄 수동 새로고침"):
            st.rerun()
        
        # 마지막 업데이트 시간
        st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# 전역 모니터링 엔드포인트 인스턴스
_monitoring_endpoints = None


def get_monitoring_endpoints() -> MonitoringEndpoints:
    """모니터링 엔드포인트 인스턴스 반환"""
    global _monitoring_endpoints
    if _monitoring_endpoints is None:
        _monitoring_endpoints = MonitoringEndpoints()
    return _monitoring_endpoints


# Streamlit 앱에서 사용할 수 있는 함수들
def render_health_check():
    """헬스체크 페이지 렌더링"""
    endpoints = get_monitoring_endpoints()
    endpoints.render_monitoring_dashboard()


def get_health_json() -> str:
    """JSON 형태의 헬스체크 결과 반환"""
    endpoints = get_monitoring_endpoints()
    return json.dumps(endpoints.health_endpoint(), indent=2, ensure_ascii=False)


def get_metrics_json() -> str:
    """JSON 형태의 메트릭 결과 반환"""
    endpoints = get_monitoring_endpoints()
    return endpoints.metrics_endpoint('json')


def get_metrics_prometheus() -> str:
    """Prometheus 형태의 메트릭 결과 반환"""
    endpoints = get_monitoring_endpoints()
    return endpoints.metrics_endpoint('prometheus')