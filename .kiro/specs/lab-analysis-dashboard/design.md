# 시험 분석 보고서 대시보드 설계

## 개요

파일 중심의 워크플로우와 인터랙티브 사용자 인터페이스를 제공하는 시험 분석 보고서 대시보드 시스템의 상세 설계 문서입니다. 사이드바 탐색과 동적 메인 콘텐츠를 통해 통합된 분석 환경을 제공합니다.

## 시스템 아키텍처

### 전체 구조
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit)                    │
├─────────────────┬───────────────────────────────────────────┤
│   A. 사이드바    │           B. 메인 콘텐츠                   │
│   (탐색 패널)    │           (분석 대시보드)                  │
│                │                                           │
│ • 현재 조회     │ • B-1: 동적 헤더 + 성적서 미리보기 버튼     │
│   파일 목록     │ • B-2: 핵심 요약 (KPI 카드)               │
│ • 메인 메뉴     │ • B-3: 부적합 통계 (시각화 차트)           │
│   - 처리 대기   │ • B-4: 데이터 목록 (인터랙티브 테이블)      │
│   - 성적서 목록 │ • B-5: 상세 정보 패널                     │
│   - 규격 목록   │                                           │
└─────────────────┴───────────────────────────────────────────┤
│                    Backend (Python)                        │
├─────────────────────────────────────────────────────────────┤
│ • 파일 자동화 엔진 • 데이터 처리 엔진 • 문서 생성 엔진        │
│ • 규격 문서 관리  • PDF 생성      • 바텀 시트 처리          │
└─────────────────────────────────────────────────────────────┘
│                    Storage (File System)                   │
├─────────────────────────────────────────────────────────────┤
│ • 처리 대기 폴더  • 시험 규격 폴더  • 생성된 성적서          │
│ • 업로드 파일    • 템플릿 파일    • 설정 파일              │
└─────────────────────────────────────────────────────────────┘
```

### 화면 레이아웃 구조
```
┌─ 사이드바 (264px) ─┬─ 메인 콘텐츠 (나머지 전체) ─────────────┐
│                   │                                        │
│ 📊 분석 시스템     │ [파일명] 분석 보고서 대시보드    [미리보기] │
│                   │                                        │
│ 현재 조회 파일     │ ┌─ KPI 카드 (4개) ─────────────────────┐ │
│ • File1.xlsx ✓    │ │ 총시험 부적합 부적합비율 처리대기    │ │
│ • File2.xlsx      │ └─────────────────────────────────────┘ │
│                   │                                        │
│ 메뉴              │ ┌─ 차트 (2개) ─────────────────────────┐ │
│ 📊 처리 대기 파일  │ │ 도넛차트    │    수평막대차트        │ │
│ 📄 시험성적서 목록 │ └─────────────────────────────────────┘ │
│ 📋 규격 목록      │                                        │
│                   │ ┌─ 테이블 ─────┬─ 상세정보 ─────────┐ │
│                   │ │ 시료명 항목   │ 시험 규격 정보     │ │
│                   │ │ 결과   판정   │ 선택 시료 상세정보  │ │
│                   │ └─────────────┴──────────────────┘ │
└───────────────────┴────────────────────────────────────────┘
```

## 주요 컴포넌트

### 1. 사이드바 탐색 시스템 (SidebarNavigationSystem)

**역할**: 파일 중심의 탐색 인터페이스 제공

**주요 기능**:
- 현재 조회 파일 목록 관리 (채팅 목록 형태)
- 활성 파일 시각적 강조 표시
- 메인 메뉴 네비게이션 (처리 대기, 성적서, 규격)
- 파일 선택 시 메인 콘텐츠 동적 전환

**클래스 구조**:
```python
class SidebarNavigationSystem:
    def __init__(self):
        self.current_files = []
        self.active_file = None
        self.menu_items = ['처리 대기 파일', '시험성적서 목록', '규격 목록']
    
    def render_file_list(self) -> None
    def set_active_file(self, file_name: str) -> None
    def handle_file_selection(self, file_name: str) -> None
    def render_menu_navigation(self) -> None
    def get_active_file_data(self) -> Dict
```

### 2. 동적 대시보드 엔진 (DynamicDashboardEngine)

**역할**: 선택된 파일에 따라 동적으로 변경되는 메인 대시보드 관리

**주요 기능**:
- 동적 헤더 업데이트 ("[파일명] 분석 보고서 대시보드")
- KPI 카드 실시간 계산 및 표시
- 인터랙티브 차트 생성 (도넛차트, 수평막대차트)
- 데이터 테이블과 상세정보 패널 연동

**클래스 구조**:
```python
class DynamicDashboardEngine:
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.current_data = None
        self.selected_row = None
    
    def update_dashboard(self, file_data: pd.DataFrame) -> None
    def generate_kpi_cards(self, data: pd.DataFrame) -> Dict
    def create_violation_charts(self, data: pd.DataFrame) -> Tuple[Figure, Figure]
    def render_interactive_table(self, data: pd.DataFrame) -> None
    def update_detail_panel(self, selected_row: Dict) -> None
```

### 3. 파일 자동화 엔진 (FileAutomationEngine)

**역할**: 폴더 스캔 및 파일 자동 인덱싱 처리

**주요 기능**:
- 처리 대기 폴더 주기적 스캔
- 새 파일 자동 인덱싱 및 분석
- 규격 파일 자동 연결
- 파일 상태 관리

**클래스 구조**:
```python
class FileAutomationEngine:
    def __init__(self, watch_folders: Dict[str, str]):
        self.watch_folders = watch_folders  # {'pending': 'path', 'standards': 'path'}
        self.indexed_files = {}
        self.file_status = {}
    
    def scan_pending_folder(self) -> List[str]
    def auto_index_file(self, file_path: str) -> IndexResult
    def scan_standards_folder(self) -> List[str]
    def link_standard_documents(self, test_item: str) -> Optional[str]
    def get_file_processing_status(self) -> Dict
```

### 4. 데이터 처리 엔진 (DataProcessor)

**역할**: 엑셀 파일 데이터 파싱 및 분석

**주요 기능**:
- 엑셀 파일 읽기 및 검증
- 컬럼 자동 매핑
- 기준값 비교 및 부적합 판정
- 데이터 정제 및 변환

**클래스 구조**:
```python
class DataProcessor:
    def __init__(self, standards_config: Dict):
        self.standards = standards_config
    
    def parse_excel_file(self, file_path: str) -> pd.DataFrame
    def validate_data_structure(self, df: pd.DataFrame) -> ValidationResult
    def calculate_violations(self, df: pd.DataFrame) -> pd.DataFrame
    def clean_and_transform_data(self, df: pd.DataFrame) -> pd.DataFrame
    def get_violation_statistics(self, df: pd.DataFrame) -> Dict
```

### 3. UI 컴포넌트 설계 (HTML 템플릿 기반)

**역할**: 제공된 HTML 템플릿을 기반으로 한 사용자 인터페이스 구성

**핵심 디자인 원칙**:
- **모던 카드 기반 레이아웃**: TailwindCSS 기반 깔끔한 그림자와 둥근 모서리
- **4단계 구성**: KPI 카드 → 차트 → 테이블 → 상세정보
- **인터랙티브 연동**: 테이블 선택 시 상세정보 패널 업데이트
- **직관적 색상**: 부적합(빨강), 적합(초록), 중성(파랑/회색)
- **애니메이션 효과**: 부드러운 전환과 호버 효과

**UI 컴포넌트 구성**:

1. **A. 핵심 지표 카드 (KPI Cards) - 3열 그리드**
   ```html
   <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
     <div class="bg-white p-4 rounded-xl shadow-md">
       <p class="text-sm text-slate-500">총 시험 항목</p>
       <p class="text-2xl font-bold">${totalTests}</p>
     </div>
     <div class="bg-white p-4 rounded-xl shadow-md">
       <p class="text-sm text-slate-500">부적합 항목</p>
       <p class="text-2xl font-bold text-red-500">${nonConformingTests}</p>
     </div>
     <div class="bg-white p-4 rounded-xl shadow-md">
       <p class="text-sm text-slate-500">부적합 비율</p>
       <p class="text-2xl font-bold">${nonConformingRate}%</p>
     </div>
   </div>
   ```
   - TailwindCSS 클래스 사용
   - 반응형 그리드 (모바일 1열, 데스크톱 3열)
   - 동적 데이터 바인딩

2. **B. 부적합 통계 차트 (ApexCharts 기반)**
   ```html
   <div class="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-6">
     <div class="lg:col-span-2 bg-white p-6 rounded-xl shadow-md">
       <h3 class="font-bold text-slate-800">부적합 항목 분포</h3>
       <div id="donut-chart"></div>
     </div>
     <div class="lg:col-span-3 bg-white p-6 rounded-xl shadow-md">
       <h3 class="font-bold text-slate-800">부적합 항목별 비율</h3>
       <div id="bar-chart"></div>
     </div>
   </div>
   ```
   - ApexCharts 라이브러리 사용 (Plotly 대신)
   - 도넛 차트 (2열) + 수평 막대 차트 (3열)
   - 반응형 차트 설정

3. **C. 데이터 테이블 (고정 높이 스크롤)**
   ```html
   <div class="lg:col-span-2 bg-white p-6 rounded-xl shadow-md h-[500px] flex flex-col">
     <h3 class="text-xl font-bold text-slate-800 mb-4">데이터 목록</h3>
     <div class="flex-grow overflow-y-auto">
       <table class="w-full text-sm text-left">
         <thead class="text-xs text-slate-700 uppercase bg-slate-100 sticky top-0">
           <tr>
             <th class="px-6 py-3">시료명</th>
             <th class="px-6 py-3">시험항목</th>
             <th class="px-6 py-3">결과</th>
             <th class="px-6 py-3">판정</th>
           </tr>
         </thead>
         <tbody id="data-table-body">
           <!-- 동적 생성 -->
         </tbody>
       </table>
     </div>
   </div>
   ```
   - 고정 높이 (500px) 스크롤 테이블
   - Sticky 헤더
   - 행 클릭 이벤트 처리

4. **D. 상세 정보 패널 (우측 고정)**
   ```html
   <div id="details-panel" class="bg-white p-6 rounded-xl shadow-md h-[500px]">
     <h3 class="text-xl font-bold text-slate-800 mb-4">상세 정보</h3>
     <div class="space-y-4">
       <div class="bg-slate-50 p-4 rounded-lg">
         <h4 class="font-semibold text-slate-700 mb-2">시료 정보</h4>
         <p class="text-sm">시료명: ${selectedSample.sampleName}</p>
       </div>
       <div class="bg-slate-50 p-4 rounded-lg">
         <h4 class="font-semibold text-slate-700 mb-2">시험 규격 정보</h4>
         <p class="text-sm">시험 항목: ${selectedSample.testItem}</p>
         <p class="text-sm">기준값: ≤ ${standardInfo.value} ${standardInfo.unit}</p>
         <p class="text-sm mt-2">
           관련 규격: <a href="#" class="text-blue-600 hover:underline">${standardInfo.doc}</a>
         </p>
       </div>
     </div>
   </div>
   ```
   - 테이블 선택 시 동적 업데이트
   - 규격 문서 링크 (바텀 시트 트리거)

5. **E. 모달 및 바텀 시트**
   ```html
   <!-- 시험성적서 미리보기 모달 -->
   <div id="report-modal" class="fixed inset-0 z-50 items-center justify-center hidden">
     <div class="modal-backdrop fixed inset-0"></div>
     <div class="bg-white rounded-lg shadow-xl w-11/12 max-w-4xl h-5/6 relative flex flex-col">
       <!-- 모달 내용 -->
     </div>
   </div>

   <!-- 규격 파일 미리보기 바텀 시트 -->
   <div id="standard-bottom-sheet" class="fixed bottom-0 left-0 right-0 h-4/5 bg-white shadow-2xl z-50 bottom-sheet">
     <!-- 바텀 시트 내용 -->
   </div>
   ```
   - CSS 트랜지션 효과
   - 백드롭 클릭으로 닫기

**JavaScript 인터랙션 로직**:
```javascript
// 파일 선택 시 대시보드 업데이트
function renderDashboard(fileName) {
    currentFile = fileName;
    const fileData = files[fileName];
    const processed = processData(fileData);
    
    // 제목 업데이트
    document.getElementById('dashboard-title').textContent = `${fileName} 분석 보고서 대시보드`;
    
    // KPI 업데이트
    updateKPICards(processed);
    
    // 차트 업데이트
    updateCharts(processed);
    
    // 테이블 및 상세정보 업데이트
    renderTableAndDetails(processed);
}

// 테이블 행 선택 시 상세정보 업데이트
function handleRowSelection(item) {
    selectedSample = item;
    updateDetailPanel(item);
    highlightSelectedRow(item.id);
}
```

**색상 팔레트 (TailwindCSS 기반)**:
- **Primary**: blue-600 (#2563eb)
- **Success**: green-600 (#16a34a)
- **Warning**: yellow-500 (#eab308)
- **Danger**: red-500 (#ef4444)
- **Background**: slate-100 (#f1f5f9)
- **Card**: white (#ffffff)
- **Text**: slate-800 (#1e293b)

**클래스 구조**:
```python
class StreamlitDashboard:
    def __init__(self):
        self.current_file = None
        self.selected_sample = None
        
    def render_sidebar(self) -> None
    def render_main_dashboard(self, file_data: pd.DataFrame) -> None
    def render_kpi_cards(self, data: pd.DataFrame) -> None
    def render_charts(self, data: pd.DataFrame) -> None
    def render_data_table(self, data: pd.DataFrame) -> None
    def render_detail_panel(self, selected_item: Dict) -> None
    def show_report_modal(self, data: pd.DataFrame) -> None
    def show_standard_bottom_sheet(self, doc_name: str) -> None
```

### 3. 문서 생성 엔진 (DocumentGenerator)

**역할**: 시험성적서 자동 생성

**템플릿 구조**:
- **헤더 섹션**: 회사 로고, 연락처, 제목
- **정보 섹션**: 접수번호, 의뢰자 정보, 시험 기간
- **결과 테이블**: 시험항목별 상세 결과
- **푸터 섹션**: 주의사항, 서명, 날짜

**PDF 생성 프로세스**:
1. HTML 템플릿에 데이터 바인딩
2. CSS 스타일링 적용
3. 기준 초과 항목 하이라이트
4. PDF 변환 및 저장

**클래스 구조**:
```python
class DocumentGenerator:
    def __init__(self, template_path):
        self.template = self.load_template(template_path)
    
    def generate_report(self, data, metadata) -> bytes
    def apply_highlighting(self, violations) -> str
    def create_pdf(self, html_content) -> bytes
```

### 4. 통합 분석 엔진 (IntegratedAnalysisEngine)

**역할**: 기간별 데이터 통합 분석 및 시각화

**주요 기능**:
- 다중 파일 데이터 통합 및 정규화
- 기간별 데이터 집계 및 통계 계산
- 시계열 분석 및 트렌드 추출
- 품질 패턴 인식 및 이상 탐지

**클래스 구조**:
```python
class IntegratedAnalysisEngine:
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.cache_manager = CacheManager()
        self.trend_analyzer = TrendAnalyzer()
    
    def integrate_period_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame
    def calculate_period_statistics(self, data: pd.DataFrame) -> Dict
    def generate_trend_analysis(self, data: pd.DataFrame) -> TrendResult
    def create_calendar_heatmap_data(self, data: pd.DataFrame) -> Dict
    def get_quality_score_trend(self, data: pd.DataFrame) -> float
```

### 5. 기간 설정 컨트롤러 (PeriodController)

**역할**: 사용자 기간 선택 및 데이터 필터링 관리

**주요 기능**:
- 사전 정의된 기간 버튼 관리
- 사용자 지정 기간 입력 처리
- 기간 유효성 검증
- 기간 변경 시 데이터 자동 업데이트

**클래스 구조**:
```python
class PeriodController:
    def __init__(self):
        self.predefined_periods = {
            '최근 3개월': timedelta(days=90),
            '최근 6개월': timedelta(days=180),
            '최근 1년': timedelta(days=365),
            '1분기': self._get_quarter_range(1),
            '2분기': self._get_quarter_range(2),
            '3분기': self._get_quarter_range(3),
            '4분기': self._get_quarter_range(4)
        }
    
    def handle_period_selection(self, period_type: str) -> Tuple[datetime, datetime]
    def validate_custom_period(self, start_date: datetime, end_date: datetime) -> bool
    def get_period_data_range(self, period: str) -> Tuple[datetime, datetime]
    def _get_quarter_range(self, quarter: int) -> Tuple[datetime, datetime]
```

### 6. 통합 분석 시각화 시스템 (IntegratedVisualizationSystem)

**역할**: 기간별 데이터의 다양한 시각화 제공

**시각화 컴포넌트**:

1. **핵심 동향 라인 차트 (TrendLineChart)**
   ```python
   class TrendLineChart:
       def create_multi_metric_chart(self, data: pd.DataFrame, metrics: List[str]) -> Figure
       def add_trend_lines(self, chart: Figure, trend_data: Dict) -> Figure
       def configure_time_axis(self, chart: Figure, time_unit: str) -> Figure
   ```

2. **월별 품질 현황 스택 바 차트 (MonthlyQualityChart)**
   ```python
   class MonthlyQualityChart:
       def create_stacked_bar_chart(self, monthly_data: pd.DataFrame) -> Figure
       def apply_pass_fail_colors(self, chart: Figure) -> Figure
       def add_volume_indicators(self, chart: Figure, volume_data: Dict) -> Figure
   ```

3. **품질 달력 히트맵 (QualityCalendarHeatmap)**
   ```python
   class QualityCalendarHeatmap:
       def create_calendar_heatmap(self, daily_data: pd.DataFrame) -> Figure
       def calculate_daily_risk_scores(self, data: pd.DataFrame) -> Dict
       def apply_color_intensity_mapping(self, scores: Dict) -> Dict
   ```

4. **통합 분석 KPI 카드 (IntegratedKPICards)**
   ```python
   class IntegratedKPICards:
       def calculate_period_kpis(self, data: pd.DataFrame) -> Dict
       def get_quality_score_change(self, current: float, previous: float) -> Dict
       def identify_top_violation_item(self, data: pd.DataFrame) -> str
   ```

### 4. 웹 인터페이스 (StreamlitApp)

**페이지 구조**:
```
📊 메인 대시보드
├── 📁 파일 업로드 섹션
├── 📈 실시간 분석 결과
├── 🎯 위험도별 요약
└── 📋 상세 데이터 테이블

📄 문서 관리
├── 📑 성적서 생성
├── 🔗 관련 문서 링크
└── 📥 다운로드 센터

⚙️ 설정
├── 🎚️ 기준값 관리
├── 🎨 차트 설정
└── 👥 사용자 관리
```

## 데이터 모델

### 1. 원본 데이터 스키마
```python
@dataclass
class TestResult:
    sample_name: str          # 시료명
    analysis_number: str      # 분석번호
    test_item: str           # 시험항목
    unit: str                # 시험단위
    result_value: float      # 결과값
    tester: str              # 시험자
    input_datetime: datetime # 입력일시
    approval_datetime: datetime # 승인일시
```

### 2. 분석 결과 스키마
```python
@dataclass
class ViolationResult:
    test_result: TestResult
    standard_limit: float    # 기준값
    excess_ratio: float      # 초과배수
    risk_level: str          # 위험도 (HIGH/MEDIUM/LOW)
    violation_flag: bool     # 초과 여부
```

### 3. 기준값 설정 스키마
```python
@dataclass
class Standard:
    test_item: str           # 시험항목명
    unit: str                # 단위
    limit_value: float       # 기준값
    regulation: str          # 관련 규정
    update_date: datetime    # 업데이트 일자
```

## 에러 처리 전략

### 1. 파일 업로드 에러
- **파일 형식 오류**: 지원되지 않는 형식 안내
- **파일 크기 초과**: 크기 제한 안내 및 압축 권장
- **파일 손상**: 파일 재업로드 요청

### 2. 데이터 처리 에러
- **컬럼 매핑 실패**: 수동 매핑 인터페이스 제공
- **데이터 타입 오류**: 자동 변환 시도 후 실패 시 사용자 확인
- **기준값 누락**: 기본값 사용 또는 사용자 입력 요청

### 3. 시각화 에러
- **데이터 부족**: 최소 데이터 요구사항 안내
- **메모리 부족**: 데이터 샘플링 또는 분할 처리
- **렌더링 실패**: 대체 차트 제공

## 보안 고려사항

### 1. 파일 업로드 보안
- 파일 확장자 검증
- 바이러스 스캔 (가능한 경우)
- 파일 크기 제한
- 업로드 경로 제한

### 2. 데이터 보안
- 업로드된 파일 24시간 후 자동 삭제
- 임시 파일 안전한 경로에 저장
- 민감 정보 로깅 방지

### 3. 웹 보안
- HTTPS 사용 권장
- XSS 방지를 위한 입력 검증
- CSRF 토큰 사용

## 성능 최적화

### 1. 데이터 처리 최적화
- 대용량 파일 청크 단위 처리
- 메모리 효율적인 pandas 연산
- 캐싱을 통한 중복 계산 방지

### 2. 시각화 최적화
- 데이터 포인트 수 제한 (1000개 이상 시 샘플링)
- 지연 로딩을 통한 초기 로딩 시간 단축
- 차트 캐싱

### 3. 웹 성능 최적화
- Streamlit 세션 상태 관리
- 컴포넌트 재사용
- 불필요한 재렌더링 방지

## 테스트 전략

### 1. 단위 테스트
- 데이터 처리 함수 테스트
- 계산 로직 검증
- 에러 처리 테스트

### 2. 통합 테스트
- 파일 업로드부터 결과 생성까지 전체 플로우
- 다양한 데이터 형식 테스트
- 성능 테스트

### 3. 사용자 테스트
- 실제 실험실 데이터로 테스트
- 사용성 테스트
- 브라우저 호환성 테스트

## 배포 전략

### 1. 개발 환경
- 로컬 개발: `streamlit run app.py`
- 테스트 데이터 사용

### 2. 스테이징 환경
- Streamlit Cloud 또는 Heroku
- 실제 데이터로 테스트

### 3. 프로덕션 환경
- 안정적인 클라우드 플랫폼
- 모니터링 및 로깅 설정
- 백업 및 복구 계획