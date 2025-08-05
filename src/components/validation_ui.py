"""
검증 시스템 UI 컴포넌트
Validation System UI Components

Task 11.1 & 11.2: 파일 업로드 검증 및 데이터 처리 에러 핸들링 UI
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys
import os

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "utils"))

try:
    from validation import IntegratedValidator
    from file_validator import ErrorMessageFormatter
except ImportError as e:
    st.error(f"검증 모듈 임포트 오류: {e}")
    IntegratedValidator = None
    ErrorMessageFormatter = None


class ValidationUI:
    """검증 시스템 UI 클래스"""
    
    def __init__(self):
        """UI 초기화"""
        self.validator = IntegratedValidator("strict") if IntegratedValidator else None
        
    def render_file_upload_with_validation(self, key: str = "file_upload") -> Optional[Dict[str, Any]]:
        """
        검증 기능이 통합된 파일 업로드 UI
        
        Args:
            key: Streamlit 위젯 키
            
        Returns:
            업로드 및 검증 결과
        """
        st.subheader("📁 파일 업로드 및 검증")
        
        # 파일 업로드 위젯
        uploaded_file = st.file_uploader(
            "Excel 파일을 선택하세요",
            type=['xlsx', 'xls', 'csv'],
            help="지원 형식: Excel (.xlsx, .xls), CSV (.csv) | 최대 크기: 50MB",
            key=key
        )
        
        if uploaded_file is None:
            self._render_upload_instructions()
            return None
        
        # 파일 정보 표시
        self._render_file_info(uploaded_file)
        
        # 검증 수행
        if self.validator:
            with st.spinner("파일을 검증하고 있습니다..."):
                validation_result = self.validator.validate_uploaded_file(
                    uploaded_file.name, uploaded_file
                )
            
            # 검증 결과 표시
            self._render_validation_results(validation_result)
            
            return {
                'file': uploaded_file,
                'validation_result': validation_result,
                'can_proceed': validation_result.get('can_proceed', False)
            }
        else:
            st.error("검증 시스템을 사용할 수 없습니다.")
            return {
                'file': uploaded_file,
                'validation_result': None,
                'can_proceed': True  # 검증 시스템이 없으면 일단 진행
            }
    
    def _render_upload_instructions(self) -> None:
        """업로드 안내 표시"""
        st.info("📋 **파일 업로드 안내**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **지원 파일 형식:**
            - Excel 파일 (.xlsx, .xls)
            - CSV 파일 (.csv)
            
            **파일 크기 제한:**
            - 최대 50MB
            """)
        
        with col2:
            st.markdown("""
            **권장 데이터 구조:**
            - 시료명 (필수)
            - 시험항목 (필수)
            - 결과(성적서) (필수)
            - 시험자 (권장)
            - 기준값 (권장)
            """)
        
        # 샘플 데이터 다운로드 링크 (선택사항)
        with st.expander("📥 샘플 데이터 다운로드"):
            st.markdown("""
            샘플 Excel 파일을 다운로드하여 데이터 형식을 확인할 수 있습니다.
            """)
            
            # 샘플 데이터 생성
            sample_data = pd.DataFrame({
                '시료명': ['냉수탱크', '온수탱크', '유량센서'],
                '분석번호': ['25A00009-001', '25A00009-002', '25A00009-003'],
                '시험항목': ['아크릴로나이트릴', '아크릴로나이트릴', 'N-니트로조다이메틸아민'],
                '시험단위': ['mg/L', 'mg/L', 'ng/L'],
                '결과(성적서)': ['불검출', '0.0007', '2.5'],
                '기준대비 초과여부 (성적서)': ['적합', '부적합', '부적합'],
                '시험자': ['김화빈', '김화빈', '이현풍'],
                '기준': ['0.0006 mg/L 이하', '0.0006 mg/L 이하', '2.0 ng/L 이하']
            })
            
            # CSV로 변환하여 다운로드 버튼 제공
            csv_data = sample_data.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 샘플 데이터 다운로드 (CSV)",
                data=csv_data,
                file_name="sample_lab_data.csv",
                mime="text/csv"
            )
    
    def _render_file_info(self, uploaded_file) -> None:
        """업로드된 파일 정보 표시"""
        st.success(f"✅ 파일 업로드 완료: **{uploaded_file.name}**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            file_size = len(uploaded_file.getvalue()) if hasattr(uploaded_file, 'getvalue') else 0
            size_mb = file_size / (1024 * 1024)
            st.metric("파일 크기", f"{size_mb:.2f} MB")
        
        with col2:
            file_type = uploaded_file.type if hasattr(uploaded_file, 'type') else "알 수 없음"
            st.metric("파일 형식", file_type)
        
        with col3:
            extension = Path(uploaded_file.name).suffix.upper()
            st.metric("확장자", extension)
    
    def _render_validation_results(self, validation_result: Dict[str, Any]) -> None:
        """검증 결과 표시"""
        formatted_messages = validation_result.get('formatted_messages')
        
        if not formatted_messages:
            st.warning("검증 결과를 표시할 수 없습니다.")
            return
        
        # 전체 상태 표시
        if formatted_messages['success']:
            st.success("🎉 **파일 검증 완료!** 데이터 분석을 시작할 수 있습니다.")
        else:
            st.error("❌ **파일 검증 실패** - 아래 문제들을 해결해주세요.")
        
        # 요약 정보 표시
        summary = formatted_messages.get('summary', {})
        if summary.get('total_rows', 0) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("전체 행 수", summary['total_rows'])
            
            with col2:
                st.metric("처리된 행 수", summary['processed_rows'])
            
            with col3:
                success_rate = summary.get('success_rate', 0)
                st.metric("성공률", f"{success_rate:.1f}%")
        
        # 문제 사항 표시
        issues = formatted_messages.get('issues', {})
        
        # 치명적 오류
        if issues.get('critical'):
            st.error("🚨 **치명적 오류** - 반드시 해결해야 합니다")
            for issue in issues['critical']:
                self._render_issue_card(issue, "error")
        
        # 일반 오류
        if issues.get('errors'):
            st.error("❌ **오류** - 해결을 권장합니다")
            for issue in issues['errors']:
                self._render_issue_card(issue, "error")
        
        # 경고
        if issues.get('warnings'):
            st.warning("⚠️ **경고** - 확인이 필요합니다")
            for issue in issues['warnings']:
                self._render_issue_card(issue, "warning")
        
        # 정보
        if issues.get('info'):
            with st.expander("ℹ️ 추가 정보"):
                for issue in issues['info']:
                    self._render_issue_card(issue, "info")
        
        # 제안사항 및 다음 단계
        suggestions = formatted_messages.get('suggestions', [])
        next_steps = formatted_messages.get('next_steps', [])
        
        if suggestions or next_steps:
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if suggestions:
                    st.info("💡 **제안사항**")
                    for suggestion in suggestions:
                        st.markdown(f"• {suggestion}")
            
            with col2:
                if next_steps:
                    st.info("🎯 **다음 단계**")
                    for step in next_steps:
                        st.markdown(f"{step}")
    
    def _render_issue_card(self, issue: Dict[str, Any], issue_type: str) -> None:
        """개별 문제 사항 카드 표시"""
        message = issue.get('message', '')
        details = issue.get('details', '')
        suggested_fix = issue.get('suggested_fix', '')
        location = issue.get('location', '')
        
        # 아이콘 선택
        icons = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        icon = icons.get(issue_type, 'ℹ️')
        
        # 카드 내용 구성
        card_content = f"{icon} **{message}**"
        
        if details:
            card_content += f"\n\n*{details}*"
        
        if location:
            card_content += f"\n\n📍 위치: {location}"
        
        if suggested_fix:
            card_content += f"\n\n💡 해결방안: {suggested_fix}"
        
        # 카드 표시
        if issue_type == 'error':
            st.error(card_content)
        elif issue_type == 'warning':
            st.warning(card_content)
        else:
            st.info(card_content)
    
    def render_validation_settings(self) -> None:
        """검증 설정 UI"""
        with st.sidebar.expander("⚙️ 검증 설정"):
            if self.validator:
                # 검증 수준 선택
                validation_levels = {
                    "basic": "기본 (확장자, 크기만 검사)",
                    "standard": "표준 (기본 + MIME 타입 검사)",
                    "strict": "엄격 (표준 + 내용 검사)"
                }
                
                current_level = st.selectbox(
                    "검증 수준",
                    options=list(validation_levels.keys()),
                    format_func=lambda x: validation_levels[x],
                    index=2,  # 기본값: strict
                    help="높은 수준일수록 더 엄격하게 검증합니다."
                )
                
                # 검증 수준 업데이트
                if hasattr(self.validator, 'file_validator') and self.validator.file_validator:
                    from file_validator import ValidationLevel
                    level_mapping = {
                        "basic": ValidationLevel.BASIC,
                        "standard": ValidationLevel.STANDARD,
                        "strict": ValidationLevel.STRICT
                    }
                    self.validator.file_validator.validation_level = level_mapping[current_level]
                
                # 검증 시스템 상태 표시
                summary = self.validator.get_validation_summary()
                
                st.markdown("**시스템 상태:**")
                st.markdown(f"• 파일 검증기: {'✅' if summary['file_validator_available'] else '❌'}")
                st.markdown(f"• 에러 핸들러: {'✅' if summary['error_handler_available'] else '❌'}")
                st.markdown(f"• 최대 파일 크기: {summary['max_file_size_mb']:.0f}MB")
                
                supported_formats = summary.get('supported_formats', [])
                if supported_formats:
                    st.markdown(f"• 지원 형식: {', '.join(supported_formats)}")
            else:
                st.error("검증 시스템을 사용할 수 없습니다.")
    
    def render_error_statistics(self, validation_results: List[Dict[str, Any]]) -> None:
        """에러 통계 표시"""
        if not validation_results:
            return
        
        st.subheader("📊 검증 통계")
        
        # 통계 계산
        total_files = len(validation_results)
        successful_files = sum(1 for result in validation_results if result.get('can_proceed', False))
        
        total_errors = 0
        total_warnings = 0
        
        for result in validation_results:
            formatted_messages = result.get('formatted_messages', {})
            issues = formatted_messages.get('issues', {})
            
            total_errors += len(issues.get('critical', [])) + len(issues.get('errors', []))
            total_warnings += len(issues.get('warnings', []))
        
        # 통계 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 파일 수", total_files)
        
        with col2:
            success_rate = (successful_files / total_files * 100) if total_files > 0 else 0
            st.metric("성공률", f"{success_rate:.1f}%")
        
        with col3:
            st.metric("총 오류 수", total_errors)
        
        with col4:
            st.metric("총 경고 수", total_warnings)
        
        # 오류 유형별 분석 (선택사항)
        if total_errors > 0 or total_warnings > 0:
            with st.expander("📈 상세 통계"):
                error_categories = {}
                
                for result in validation_results:
                    formatted_messages = result.get('formatted_messages', {})
                    issues = formatted_messages.get('issues', {})
                    
                    all_issues = (issues.get('critical', []) + 
                                issues.get('errors', []) + 
                                issues.get('warnings', []))
                    
                    for issue in all_issues:
                        category = issue.get('category', 'unknown')
                        error_categories[category] = error_categories.get(category, 0) + 1
                
                if error_categories:
                    st.bar_chart(error_categories)


# 사용 예시 및 테스트 함수
def test_validation_ui():
    """검증 UI 테스트"""
    st.title("🧪 파일 검증 시스템 테스트")
    
    # 검증 UI 인스턴스 생성
    validation_ui = ValidationUI()
    
    # 검증 설정 표시
    validation_ui.render_validation_settings()
    
    # 파일 업로드 및 검증
    upload_result = validation_ui.render_file_upload_with_validation()
    
    if upload_result:
        st.markdown("---")
        st.subheader("🔍 업로드 결과")
        
        if upload_result['can_proceed']:
            st.success("✅ 파일 처리를 계속할 수 있습니다!")
            
            # 실제 데이터 미리보기 (선택사항)
            if st.checkbox("데이터 미리보기"):
                try:
                    df = pd.read_excel(upload_result['file'], nrows=10)
                    st.dataframe(df)
                except Exception as e:
                    st.error(f"데이터 미리보기 실패: {e}")
        else:
            st.error("❌ 파일에 문제가 있어 처리할 수 없습니다.")
    
    # 세션 상태에 검증 결과 저장 (선택사항)
    if 'validation_history' not in st.session_state:
        st.session_state.validation_history = []
    
    if upload_result and upload_result['validation_result']:
        # 중복 방지를 위해 파일명으로 확인
        existing_files = [r.get('file_name') for r in st.session_state.validation_history]
        if upload_result['file'].name not in existing_files:
            st.session_state.validation_history.append({
                'file_name': upload_result['file'].name,
                'validation_result': upload_result['validation_result'],
                'can_proceed': upload_result['can_proceed']
            })
    
    # 검증 통계 표시
    if st.session_state.validation_history:
        st.markdown("---")
        validation_ui.render_error_statistics(
            [r['validation_result'] for r in st.session_state.validation_history]
        )


if __name__ == "__main__":
    test_validation_ui()