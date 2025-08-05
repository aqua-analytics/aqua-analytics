"""
HTML 템플릿과 실제 데이터 통합 모듈
실제 엑셀 데이터를 HTML 템플릿의 JavaScript로 변환
"""

import json
from typing import List, Dict, Any
from data_models import TestResult, ProjectSummary
from datetime import datetime
import re

class TemplateIntegrator:
    """HTML 템플릿과 데이터 통합 클래스"""
    
    def __init__(self):
        self.standards_cache = {}
    
    def generate_javascript_data(self, test_results: List[TestResult], project_name: str) -> str:
        """실제 데이터를 JavaScript 형태로 변환"""
        
        # 프로젝트 요약 생성
        summary = ProjectSummary.from_test_results(project_name, test_results)
        
        # JavaScript 데이터 구조 생성
        js_data = []
        for i, result in enumerate(test_results, 1):
            js_data.append({
                'id': i,
                'sampleName': result.sample_name,
                'analysisNumber': result.analysis_number,
                'testItem': result.test_item,
                'result': result.get_display_result(),
                'numericResult': result.get_numeric_result() or 0,
                'unit': result.test_unit,
                'status': self._normalize_status(result.standard_excess)
            })
        
        # 기준값 정보 생성
        standards = self._extract_standards(test_results)
        
        # 프로젝트 정보 구성
        project_data = {
            'fileName': f"{project_name.replace('_PJT', '.xlsx')}",
            'period': summary.analysis_period,
            'data': js_data
        }
        
        # JavaScript 코드 생성
        js_code = f"""
        // 실제 데이터로 교체
        const projects = {{
            '{project_name}': {json.dumps(project_data, ensure_ascii=False, indent=2)}
        }};
        
        const standards = {json.dumps(standards, ensure_ascii=False, indent=2)};
        
        // 전역 변수로 설정
        window.actualProjects = projects;
        window.actualStandards = standards;
        
        // 기존 데이터를 실제 데이터로 교체
        if (typeof renderDashboard === 'function') {{
            // 페이지 로드 후 실제 데이터로 대시보드 렌더링
            setTimeout(() => {{
                Object.assign(window.projects || {{}}, projects);
                Object.assign(window.standards || {{}}, standards);
                
                // 첫 번째 프로젝트로 대시보드 렌더링
                const firstProject = Object.keys(projects)[0];
                if (firstProject && typeof renderDashboard === 'function') {{
                    renderDashboard(firstProject);
                }}
            }}, 100);
        }}
        """
        
        return js_code
    
    def _normalize_status(self, status: str) -> str:
        """상태값 정규화"""
        if status in ['부적합', '초과', 'FAIL']:
            return '부적합'
        elif status in ['적합', '합격', 'PASS']:
            return '적합'
        else:
            return '적합'  # 기본값
    
    def _extract_standards(self, test_results: List[TestResult]) -> Dict[str, Dict[str, Any]]:
        """시험 결과에서 기준값 정보 추출"""
        standards = {}
        
        for result in test_results:
            if result.test_item not in standards and result.standard_criteria:
                try:
                    # 기준값 추출
                    limit_value = self._extract_limit_value(result.standard_criteria)
                    
                    standards[result.test_item] = {
                        'value': limit_value,
                        'unit': result.test_unit,
                        'criteria': result.standard_criteria
                    }
                except Exception as e:
                    print(f"기준값 추출 실패 ({result.test_item}): {e}")
                    continue
        
        return standards
    
    def _extract_limit_value(self, criteria_text: str) -> float:
        """기준 텍스트에서 수치값 추출"""
        if not criteria_text or criteria_text.strip() == "":
            return 0.0
        
        # "0.0006 mg/L 이하" 형태에서 숫자 추출
        numbers = re.findall(r'\d+\.?\d*', criteria_text)
        if numbers:
            return float(numbers[0])
        return 0.0
    
    def inject_data_into_template(self, html_template: str, test_results: List[TestResult], project_name: str) -> str:
        """HTML 템플릿에 실제 데이터 주입"""
        
        # JavaScript 데이터 생성
        js_data = self.generate_javascript_data(test_results, project_name)
        
        # HTML 템플릿에서 스크립트 섹션 찾기
        script_start = html_template.find('<script>')
        script_end = html_template.find('</script>') + 9
        
        if script_start != -1 and script_end != -1:
            # 기존 스크립트 내용
            original_script = html_template[script_start:script_end]
            
            # 새로운 스크립트 생성 (데이터 주입 + 기존 로직)
            new_script = f"""<script>
{js_data}

{original_script[8:-9]}  // <script>와 </script> 태그 제거
</script>"""
            
            # HTML 템플릿에서 스크립트 교체
            modified_html = html_template[:script_start] + new_script + html_template[script_end:]
            return modified_html
        
        else:
            # 스크립트 섹션을 찾을 수 없는 경우, body 끝에 추가
            body_end = html_template.rfind('</body>')
            if body_end != -1:
                injection_point = body_end
                modified_html = (html_template[:injection_point] + 
                               f"<script>{js_data}</script>\n" + 
                               html_template[injection_point:])
                return modified_html
        
        return html_template
    
    def create_summary_stats(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """요약 통계 생성"""
        total_tests = len(test_results)
        unique_samples = len(set(result.sample_name for result in test_results))
        violations = [r for r in test_results if r.is_non_conforming()]
        violation_samples = len(set(r.sample_name for r in violations))
        
        # 항목별 부적합 통계
        violation_by_item = {}
        for result in violations:
            item = result.test_item
            violation_by_item[item] = violation_by_item.get(item, 0) + 1
        
        # 시료별 부적합 통계
        violation_by_sample = {}
        for result in violations:
            sample = result.sample_name
            violation_by_sample[sample] = violation_by_sample.get(sample, 0) + 1
        
        return {
            'total_tests': total_tests,
            'total_samples': unique_samples,
            'violation_tests': len(violations),
            'violation_samples': violation_samples,
            'violation_rate': (len(violations) / total_tests * 100) if total_tests > 0 else 0,
            'violation_by_item': violation_by_item,
            'violation_by_sample': violation_by_sample
        }

def test_template_integration():
    """템플릿 통합 테스트"""
    from data_processor import DataProcessor
    
    # 샘플 데이터 생성
    sample_data = {
        'No.': [1, 2, 3, 4, 5],
        '시료명': ['냉수탱크', '온수탱크', 'Blank', '제품#1', '제품#2'],
        '분석번호': ['25A00009-001', '25A00009-002', '25A00011-003', '25A00089-002', '25A00089-003'],
        '시험항목': ['아크릴로나이트릴', '아크릴로나이트릴', 'N-니트로조다이메틸아민', '아크릴로나이트릴', '아크릴로나이트릴'],
        '시험단위': ['mg/L', 'mg/L', 'ng/L', 'mg/L', 'mg/L'],
        '결과(성적서)': ['불검출', '불검출', '2.29', '0.0007', '0.0004'],
        '시험자입력값': [0, 0, 2.29, 0.0007, 0.0004],
        '기준대비 초과여부 (성적서)': ['적합', '적합', '부적합', '부적합', '적합'],
        '시험자': ['김화빈', '김화빈', '이현풍', '김화빈', '김화빈'],
        '시험표준': ['EPA 524.2', 'EPA 524.2', 'House Method', 'EPA 524.2', 'EPA 524.2'],
        '기준': ['0.0006 mg/L 이하', '0.0006 mg/L 이하', '0.1 ng/L 이하', '0.0006 mg/L 이하', '0.0006 mg/L 이하'],
        '입력일시': ['2025-01-23 09:56'] * 5
    }
    
    import pandas as pd
    df = pd.DataFrame(sample_data)
    
    # 데이터 처리
    processor = DataProcessor()
    test_results = []
    for _, row in df.iterrows():
        result = processor._row_to_test_result(row)
        if result:
            test_results.append(result)
    
    # 템플릿 통합 테스트
    integrator = TemplateIntegrator()
    
    # JavaScript 데이터 생성 테스트
    js_data = integrator.generate_javascript_data(test_results, "TEST_PROJECT_PJT")
    print("JavaScript 데이터 생성 완료")
    print(f"데이터 길이: {len(js_data)} 문자")
    
    # 요약 통계 테스트
    stats = integrator.create_summary_stats(test_results)
    print(f"요약 통계: {stats}")
    
    return test_results, js_data

if __name__ == "__main__":
    test_template_integration()