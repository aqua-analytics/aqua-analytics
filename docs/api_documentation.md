# 🔧 API 문서

> 실험실 품질관리 대시보드의 내부 API 및 개발자 가이드

## 📋 목차

1. [개요](#개요)
2. [핵심 클래스](#핵심-클래스)
3. [데이터 모델](#데이터-모델)
4. [API 엔드포인트](#api-엔드포인트)
5. [확장 가이드](#확장-가이드)
6. [개발 환경 설정](#개발-환경-설정)

## 🎯 개요

### 아키텍처 구조

```
┌─ Presentation Layer ─────────────────────────────────┐
│  Streamlit App (app.py)                              │
│  ├─ StreamlitApp                                     │
│  ├─ HTML Templates                                   │
│  └─ Static Assets                                    │
└─────────────────────────────────────────────────────┘
┌─ Business Logic Layer ───────────────────────────────┐
│  Components & Core                                   │
│  ├─ DynamicDashboardEngine                          │
│  ├─ DataProcessor                                    │
│  ├─ TemplateIntegrator                              │
│  └─ ReportGenerator                                  │
└─────────────────────────────────────────────────────┘
┌─ Data Layer ─────────────────────────────────────────┐
│  Models & Storage                                    │
│  ├─ TestResult                                       │
│  ├─ ProjectSummary                                   │
│  ├─ Standard                                         │
│  └─ File System                                      │
└─────────────────────────────────────────────────────┘
```

### 기술 스택

- **Frontend**: Streamlit, HTML/CSS/JavaScript, TailwindCSS, ApexCharts
- **Backend**: Python 3.9+, Pandas, NumPy
- **Storage**: File System (향후 Database 확장 가능)
- **Deployment**: Docker, Docker Compose

## 🏗️ 핵심 클래스

### 1. StreamlitApp

**위치**: `app.py`  
**역할**: 메인 애플리케이션 클래스

```python
class StreamlitApp:
    """메인 Streamlit 애플리케이션 클래스"""
    
    def __init__(self):
        """애플리케이션 초기화"""
        
    def initialize_session_state(self) -> None:
        """세션 상태 초기화"""
        
    def handle_page_routing(self) -> str:
        """페이지 라우팅 시스템"""
        
    def render_main_content(self, current_page: str) -> None:
        """메인 콘텐츠 렌더링"""
```

**주요 메서드**:

#### `initialize_session_state()`
```python
def initialize_session_state(self) -> None:
    """세션 상태 초기화 (요구사항 1.1, 2.1)"""
    default_states = {
        'uploaded_files': {},
        'active_file': None,
        'current_page': '📊 처리 대기 파일',
        'dashboard_initialized': False,
        # ... 기타 상태들
    }
```

#### `process_uploaded_file()`
```python
def process_uploaded_file(self, upload_result: Dict[str, Any]) -> None:
    """업로드된 파일 처리"""
    # 1. 파일 데이터 읽기
    # 2. 데이터 처리 및 검증
    # 3. TestResult 객체로 변환
    # 4. 세션 상태에 저장
```

### 2. DataProcessor

**위치**: `src/core/data_processor.py`  
**역할**: 엑셀 데이터 처리 및 분석

```python
class DataProcessor:
    """데이터 처리 엔진"""
    
    def __init__(self):
        """데이터 처리기 초기화"""
        
    def process_excel_data(self, df: pd.DataFrame) -> List[TestResult]:
        """엑셀 데이터를 TestResult 객체로 변환"""
        
    def calculate_project_summary(self, test_results: List[TestResult]) -> ProjectSummary:
        """프로젝트 요약 정보 계산"""
        
    def get_violation_statistics(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """부적합 통계 계산"""
```

**사용 예시**:
```python
# 데이터 처리기 초기화
processor = DataProcessor()

# 엑셀 데이터 처리
df = pd.read_excel('sample.xlsx')
test_results = processor.process_excel_data(df)

# 프로젝트 요약 생성
summary = processor.calculate_project_summary(test_results)
```

### 3. DynamicDashboardEngine

**위치**: `src/core/dynamic_dashboard_engine.py`  
**역할**: 동적 대시보드 생성 및 관리

```python
class DynamicDashboardEngine:
    """동적 대시보드 엔진"""
    
    def __init__(self, data_processor: DataProcessor):
        """대시보드 엔진 초기화"""
        
    def update_dashboard(self, test_results: List[TestResult], filename: str) -> None:
        """대시보드 업데이트"""
        
    def generate_kpi_cards(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """KPI 카드 데이터 생성"""
        
    def create_violation_charts(self, test_results: List[TestResult]) -> Tuple[Figure, Figure]:
        """부적합 통계 차트 생성"""
```

**KPI 데이터 구조**:
```python
{
    'total_tests': 1234,
    'non_conforming_tests': 56,
    'non_conforming_rate': 4.5,
    'total_samples': 89,
    'unique_test_items': 15
}
```

### 4. TemplateIntegrator

**위치**: `src/core/template_integration.py`  
**역할**: HTML 템플릿과 데이터 통합

```python
class TemplateIntegrator:
    """템플릿 통합 클래스"""
    
    def inject_data_into_template(self, 
                                html_template: str, 
                                test_results: List[TestResult], 
                                project_name: str) -> str:
        """템플릿에 데이터 주입"""
        
    def generate_javascript_data(self, 
                               test_results: List[TestResult], 
                               project_name: str) -> str:
        """JavaScript 데이터 생성"""
```

**JavaScript 데이터 형식**:
```javascript
window.actualProjects = {
    "프로젝트명_PJT": {
        "projectName": "프로젝트명_PJT",
        "analysisDate": "2024-01-15",
        "data": [
            {
                "sampleName": "샘플A",
                "analysisNumber": "2024-001-001",
                "testItem": "대장균",
                "result": "15",
                "unit": "CFU/g",
                "status": "부적합"
            }
            // ... 더 많은 데이터
        ]
    }
};
```

## 📊 데이터 모델

### 1. TestResult

**위치**: `src/core/data_models.py`

```python
@dataclass
class TestResult:
    """시험 결과 데이터 모델"""
    sample_name: str              # 시료명
    analysis_number: str          # 분석번호
    test_item: str               # 시험항목
    unit: str                    # 단위
    result_value: Optional[float] # 결과값
    tester: str                  # 시험자
    input_datetime: datetime     # 입력일시
    approval_datetime: Optional[datetime] # 승인일시
    
    def is_non_conforming(self) -> bool:
        """부적합 여부 판정"""
        
    def get_formatted_result(self) -> str:
        """포맷된 결과값 반환"""
        
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
```

### 2. ProjectSummary

```python
@dataclass
class ProjectSummary:
    """프로젝트 요약 정보"""
    project_name: str            # 프로젝트명
    analysis_period: str         # 분석 기간
    total_samples: int           # 총 시료 수
    total_tests: int            # 총 시험 수
    non_conforming_tests: int   # 부적합 시험 수
    non_conforming_rate: float  # 부적합 비율
    test_items: List[str]       # 시험 항목 목록
    
    def get_status_summary(self) -> str:
        """상태 요약 반환"""
        
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
```

### 3. Standard

```python
@dataclass
class Standard:
    """시험 규격 정보"""
    test_item: str              # 시험항목명
    unit: str                   # 단위
    limit_value: float          # 기준값
    limit_type: str            # 기준 타입 (≤, ≥, =)
    regulation: str            # 관련 규정
    document_path: Optional[str] # 규격 문서 경로
    
    def check_conformity(self, result_value: float) -> bool:
        """적합성 판정"""
        
    def get_formatted_limit(self) -> str:
        """포맷된 기준값 반환"""
```

## 🌐 API 엔드포인트

### Streamlit 내부 엔드포인트

#### 1. 헬스체크
```
GET /_stcore/health
```
**응답**:
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "uptime": 3600,
    "version": "1.0.0"
}
```

#### 2. 메트릭
```
GET /_stcore/metrics
```
**응답**:
```json
{
    "system": {
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "disk_usage": 23.1
    },
    "application": {
        "active_sessions": 5,
        "processed_files": 123,
        "total_requests": 4567
    }
}
```

### 커스텀 API 함수

#### 1. 파일 처리 API

```python
def process_file_api(file_data: bytes, filename: str) -> Dict[str, Any]:
    """파일 처리 API"""
    try:
        # 파일 검증
        validation_result = validate_file(file_data, filename)
        if not validation_result['valid']:
            return {'success': False, 'error': validation_result['error']}
        
        # 데이터 처리
        df = pd.read_excel(io.BytesIO(file_data))
        processor = DataProcessor()
        test_results = processor.process_excel_data(df)
        
        return {
            'success': True,
            'data': {
                'test_results': [result.to_dict() for result in test_results],
                'summary': processor.calculate_project_summary(test_results).to_dict()
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

#### 2. 보고서 생성 API

```python
def generate_report_api(test_results: List[TestResult], 
                       format: str = 'html') -> Dict[str, Any]:
    """보고서 생성 API"""
    try:
        generator = ReportGenerator()
        
        if format == 'html':
            report_content = generator.generate_html_report(test_results)
        elif format == 'pdf':
            report_content = generator.generate_pdf_report(test_results)
        else:
            return {'success': False, 'error': 'Unsupported format'}
        
        return {
            'success': True,
            'data': {
                'content': report_content,
                'format': format,
                'generated_at': datetime.now().isoformat()
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

## 🔧 확장 가이드

### 새로운 컴포넌트 추가

#### 1. 컴포넌트 클래스 생성

```python
# src/components/new_component.py
class NewComponent:
    """새로운 컴포넌트"""
    
    def __init__(self, config: Dict[str, Any]):
        """컴포넌트 초기화"""
        self.config = config
    
    def render(self, data: Any) -> None:
        """컴포넌트 렌더링"""
        pass
    
    def handle_interaction(self, event: Dict[str, Any]) -> None:
        """사용자 인터랙션 처리"""
        pass
```

#### 2. 메인 앱에 통합

```python
# app.py
from src.components.new_component import NewComponent

class StreamlitApp:
    def initialize_components(self):
        # 기존 컴포넌트들...
        self.new_component = NewComponent(config)
    
    def render_new_feature(self):
        """새 기능 렌더링"""
        self.new_component.render(data)
```

### 새로운 데이터 모델 추가

#### 1. 데이터 클래스 정의

```python
# src/core/data_models.py
@dataclass
class NewDataModel:
    """새로운 데이터 모델"""
    field1: str
    field2: int
    field3: Optional[datetime] = None
    
    def validate(self) -> bool:
        """데이터 검증"""
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return asdict(self)
```

#### 2. 데이터 처리기에 통합

```python
# src/core/data_processor.py
class DataProcessor:
    def process_new_data(self, raw_data: Any) -> List[NewDataModel]:
        """새로운 데이터 처리"""
        processed_data = []
        # 처리 로직...
        return processed_data
```

### 새로운 차트 타입 추가

#### 1. 차트 생성 함수

```python
# src/components/chart_system.py
def create_new_chart(data: List[Dict[str, Any]]) -> Figure:
    """새로운 차트 생성"""
    fig = go.Figure()
    
    # 차트 구성...
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode='lines+markers',
        name='New Chart'
    ))
    
    fig.update_layout(
        title="새로운 차트",
        xaxis_title="X축",
        yaxis_title="Y축"
    )
    
    return fig
```

#### 2. 대시보드 엔진에 통합

```python
# src/core/dynamic_dashboard_engine.py
class DynamicDashboardEngine:
    def create_new_visualization(self, test_results: List[TestResult]) -> Figure:
        """새로운 시각화 생성"""
        chart_data = self._prepare_chart_data(test_results)
        return create_new_chart(chart_data)
```

## 🛠️ 개발 환경 설정

### 로컬 개발 환경

#### 1. 저장소 클론 및 설정

```bash
# 저장소 클론
git clone https://github.com/your-repo/lab-analysis-dashboard.git
cd lab-analysis-dashboard

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 의존성 설치 (선택사항)
pip install -r requirements-dev.txt
```

#### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# 개발 환경 설정
echo "APP_DEBUG=true" >> .env
echo "LOG_LEVEL=DEBUG" >> .env
```

#### 3. 개발 서버 실행

```bash
# Streamlit 개발 서버
streamlit run app.py --server.runOnSave=true

# 또는 특정 포트로 실행
streamlit run app.py --server.port=8502
```

### 테스트 환경

#### 1. 단위 테스트

```bash
# 전체 테스트 실행
pytest tests/unit/ -v

# 커버리지 포함
pytest tests/unit/ --cov=src --cov-report=html

# 특정 테스트 파일
pytest tests/unit/test_data_processor.py -v
```

#### 2. 통합 테스트

```bash
# 통합 테스트 실행
pytest tests/integration/ -v

# 성능 테스트
python tests/integration/test_performance_benchmarks.py
```

### 코드 품질 도구

#### 1. 린팅 및 포맷팅

```bash
# Black 포맷팅
black src/ tests/

# isort 임포트 정렬
isort src/ tests/

# Flake8 린팅
flake8 src/ tests/

# mypy 타입 체크
mypy src/
```

#### 2. 사전 커밋 훅 설정

```bash
# pre-commit 설치
pip install pre-commit

# 훅 설정
pre-commit install

# 수동 실행
pre-commit run --all-files
```

### Docker 개발 환경

#### 1. 개발용 Docker 이미지

```dockerfile
# Dockerfile.dev
FROM python:3.9-slim

WORKDIR /app

# 개발 의존성 포함
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements-dev.txt

# 소스 코드 마운트 (볼륨 사용)
VOLUME ["/app"]

# 개발 서버 실행
CMD ["streamlit", "run", "app.py", "--server.runOnSave=true"]
```

#### 2. 개발용 Docker Compose

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  lab-dashboard-dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8501:8501"
    volumes:
      - .:/app
    environment:
      - APP_DEBUG=true
      - LOG_LEVEL=DEBUG
```

### 디버깅 가이드

#### 1. Streamlit 디버깅

```python
# 디버그 정보 표시
if st.session_state.get('show_debug_info', False):
    st.write("Debug Info:", st.session_state)

# 예외 처리 및 로깅
try:
    result = process_data(data)
except Exception as e:
    st.error(f"오류 발생: {e}")
    logger.exception("데이터 처리 오류")
```

#### 2. 성능 프로파일링

```python
import cProfile
import pstats

# 프로파일링 실행
profiler = cProfile.Profile()
profiler.enable()

# 측정할 코드
result = expensive_function()

profiler.disable()

# 결과 분석
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

---

**📚 관련 문서**
- [사용자 가이드](user_guide.md) - 최종 사용자를 위한 가이드
- [배포 가이드](deployment_guide.md) - 프로덕션 배포 방법
- [아키텍처 문서](architecture.md) - 시스템 아키텍처 상세 설명