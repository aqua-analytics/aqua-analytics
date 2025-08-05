# Aqua-Analytics 통합 분석 대시보드 기능 명세서

## 1. 개요
'Aqua-Analytics' 대시보드의 '통합 분석' 기능을 고도화하여, 누적된 데이터를 기반으로 시계열 분석 및 다차원 인사이트를 제공하는 것을 목표로 한다. 사용자는 직관적인 인터페이스를 통해 기간을 설정하고, 해당 기간의 품질 동향을 한눈에 파악할 수 있어야 한다.

## 2. 데이터 처리 및 영속성

### 2.1. 데이터 저장
**요구사항**: 파일 업로드 후 분석이 완료된 데이터는 애플리케이션이 종료되어도 유지되어야 한다.

**구현 명세**:
- 분석 완료 시, 원본 파일명, 등록 시점(Timestamp), 의뢰 기관, 분석 결과 요약 등의 메타데이터를 database.json 또는 로컬 DB(e.g., SQLite)에 저장한다.
- 데이터 스키마 예시:
```json
{
  "file_id": "unique_id_123",
  "file_name": "Project_A_240726.xlsx",
  "client": "A환경연구소",
  "processed_at": "2024-07-26T10:30:00Z",
  "report_path": "/reports/Project_A_240726.html",
  "summary": {
    "total_items": 15,
    "fail_items": 5,
    "failure_rate": 33.3
  }
}
```

### 2.2. 저장 폴더 관리
**요구사항**: 사용자가 저장된 파일(리포트 등)의 실제 위치를 확인할 수 있어야 한다.

**구현 명세**:
- '통합 분석' 화면 또는 '설정' 메뉴에 [저장 폴더 바로가기] 버튼을 추가한다.
- 클릭 시, 운영체제의 파일 탐색기(Windows Explorer, macOS Finder)에서 해당 데이터가 저장된 폴더를 연다.

## 3. UI/UX 및 기능 명세

### 3.1. 기간 설정 컨트롤러 (통합형)
**요구사항**: 분리된 기간 설정을 하나로 통합하고, 연도에 고정되지 않는 일반적인 기준으로 개선한다.

**구현 명세**:
- 하나의 '기간 설정' 카드 내에 모든 컨트롤을 배치한다.
- 사전 정의된 기간 (Preset-based):
  - 오늘, 최근 7일, 최근 1개월, 최근 3개월, 올해 등 현재 시점을 기준으로 동적으로 계산되는 버튼을 제공한다.
- 사용자 지정 기간 (Custom Range):
  - 시작일과 종료일을 선택할 수 있는 Date-picker를 제공한다.
- 기간 선택 시, 해당 기간(시작일 ~ 종료일)이 명확하게 표시되어야 한다. (e.g., "기간: 2024-05-01 ~ 2024-07-31")

### 3.2. 통합 분석 결과 표시
**요구사항**: 선택된 기간 내 processed_at 타임스탬프를 가진 모든 데이터를 집계하여 분석 결과를 표시해야 한다.

**구현 명세**:
- KPI 카드 항목 추가:
  - 총 시험 수: 선택된 기간 내 분석된 파일의 총개수.
  - 주요 의뢰 기관: 기간 내 시험을 가장 많이 의뢰한 기관 Top 3를 순서대로 나열.
- 항목 분포 차트:
  - '적합/부적합 항목 분포' 라는 제목 아래, 두 개의 도넛 차트를 나란히 배치한다.
  - 왼쪽 차트: 기간 내 모든 '적합' 판정 항목들의 분포 (e.g., 'pH', '온도' 등).
  - 오른쪽 차트: 기간 내 모든 '부적합' 판정 항목들의 분포 (e.g., 'T-N', 'T-P' 등).
- 리포트 요약 및 미리보기:
  - 품질 분석 리포트 요약: 선택된 기간 전체의 데이터 동향을 요약한 텍스트를 동적으로 생성한다.
  - 리포트 미리보기: 클릭 시, 기간 전체에 대한 통합 분석 보고서가 모달 창으로 표시된다.

## 4. 시스템 흐름
1. 사용자가 '통합 분석' 메뉴 진입.
2. 시스템은 저장된 모든 데이터(database.json)를 로드.
3. 기간 설정 컨트롤러에서 기본값(e.g., 최근 1개월)으로 기간 설정.
4. 해당 기간에 포함되는 데이터를 필터링하여 KPI, 차트, 요약 리포트를 화면에 렌더링.
5. 사용자가 기간을 변경하면, 4번 과정을 반복하여 화면을 동적으로 업데이트.

-----

#### **2. UI/UX 기획**

##### **2.1. 사이드바 메뉴 추가**

  * 기존 메뉴 목록(`대시보드`, `보고서 관리`, `시험 규격 관리`) 하단에 \*\*구분선(\<hr\>)\*\*을 추가한다.
  * 구분선 아래에 **'통합 분석'** 메뉴 항목을 신설한다. 사용자가 이 메뉴를 클릭하면 통합 분석 대시보드로 진입한다.

##### **2.2. 기간 설정 컨트롤러**

  * 통합 분석 대시보드 최상단에 기간을 설정할 수 있는 인터페이스를 배치한다.
  * **사전 정의된 기간 버튼:** 사용 빈도가 높은 기간을 버튼(Chip) 형태로 제공하여 원클릭으로 조회할 수 있게 한다.
      * `최근 3개월`, `최근 6개월`, `최근 1년`
      * `1분기`, `2분기`, `3분기`, `4분기` (올해 기준)
  * **사용자 지정 기간:** 시작일과 종료일을 직접 선택할 수 있는 Date-picker를 제공한다.

##### **2.3. 데이터 시각화 아이디어**

동일한 형식의 데이터를 기간별로 통합하여 보여주기 위해, 시간의 흐름을 효과적으로 표현하는 시각화 방법을 사용한다.

  * **① 핵심 동향 라인 차트 (Trend Line Chart):**

      * 기간 내 **주요 품질 지표의 변화 추이**를 라인 차트로 시각화한다.
      * **Y축:** 부적합률(%), 특정 시험 항목의 평균값(e.g., T-N 평균 농도) 등
      * **X축:** 시간 (일/주/월 단위)
      * 사용자가 여러 시험 항목을 선택하여 차트에서 동시에 비교하며 볼 수 있는 기능을 제공한다.

  * **② 월별 품질 현황 스택 바 차트 (Stacked Bar Chart):**

      * 월별로 수행된 **총 시험 건수와 그중 정상/부적합 비율**을 한눈에 파악할 수 있다.
      * 각 막대는 월(Month)을 의미하며, 막대 내부는 정상(Pass)과 부적합(Fail) 건수가 색상으로 구분되어 쌓여있는 형태이다.
      * 이를 통해 특정 월에 시험 물량이 많았는지, 혹은 유독 부적합 비율이 높았는지 직관적으로 알 수 있다.

  * **③ 품질 달력 히트맵 (Calendar Heatmap):**

      * 일별 부적합 발생 빈도나 위험도를 색상의 농도로 표현하는 달력 형태의 시각화이다.
      * 사용자는 특정 요일이나 월말/월초 등 주기적으로 발생하는 품질 이슈 패턴을 쉽게 발견할 수 있다.

  * **④ 기간 요약 KPI 카드:**

      * 선택된 기간 전체에 대한 핵심 지표를 요약하여 보여준다.
      * `기간 내 총 시험 건수`, `평균 부적합률`, `최다 부적합 항목` 등

-----

다음은 위 기획안을 바탕으로 제작한 **HTML 디자인 초안**입니다.

-----

### **통합 분석 대시보드 디자인 초안 (HTML)**

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aqua-Analytics: 통합 분석 (초안)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/feather-icons/dist/feather.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        .sidebar { background-color: #ffffff; }
        .card {
            background-color: #ffffff;
            border-radius: 0.75rem;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }
        .date-chip {
            transition: all 0.2s ease;
        }
    </style>
</head>
<body class="flex h-screen">

    <aside class="sidebar w-64 flex-shrink-0 p-6 flex flex-col">
        <div class="flex items-center mb-10">
            <div class="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center mr-3">
                <i data-feather="droplet" class="text-white"></i>
            </div>
            <h1 class="text-xl font-bold text-gray-800">Aqua-Analytics</h1>
        </div>
        <nav class="flex-grow">
            <h2 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Menu</h2>
            <ul>
                <li><a href="#" class="flex items-center px-4 py-2.5 text-gray-500 hover:bg-gray-100 rounded-lg"><i data-feather="layout" class="w-5 h-5 mr-3"></i> 대시보드</a></li>
                <li><a href="#" class="flex items-center px-4 py-2.5 text-gray-500 hover:bg-gray-100 rounded-lg"><i data-feather="file-text" class="w-5 h-5 mr-3"></i> 보고서 관리</a></li>
                <li><a href="#" class="flex items-center px-4 py-2.5 text-gray-500 hover:bg-gray-100 rounded-lg"><i data-feather="shield" class="w-5 h-5 mr-3"></i> 시험 규격 관리</a></li>
            </ul>
            <hr class="my-4 border-gray-200">
             <ul>
                <li><a href="#" class="flex items-center px-4 py-2.5 text-gray-700 bg-blue-50 rounded-lg font-semibold border-l-4 border-blue-500"><i data-feather="bar-chart-2" class="w-5 h-5 mr-3 text-blue-500"></i> 통합 분석</a></li>
            </ul>
        </nav>
    </aside>

    <main class="main-content flex-1 p-8 overflow-y-auto">
        <header class="mb-8">
            <h2 class="text-3xl font-bold text-gray-800">통합 분석 대시보드</h2>
            <p class="text-gray-500">기간별 데이터 동향을 통해 품질 관리 인사이트를 확보하세요.</p>
        </header>

        <section class="card p-4 mb-8">
            <div class="flex flex-wrap items-center gap-2">
                <span class="text-sm font-semibold text-gray-700 mr-2">기간 선택:</span>
                <button class="date-chip text-sm font-medium py-1.5 px-3 rounded-full bg-blue-100 text-blue-700">최근 3개월</button>
                <button class="date-chip text-sm font-medium py-1.5 px-3 rounded-full bg-white hover:bg-gray-100 border border-gray-300">최근 1년</button>
                <button class="date-chip text-sm font-medium py-1.5 px-3 rounded-full bg-white hover:bg-gray-100 border border-gray-300">1분기</button>
                <button class="date-chip text-sm font-medium py-1.5 px-3 rounded-full bg-white hover:bg-gray-100 border border-gray-300">2분기</button>
                <div class="flex items-center ml-auto">
                     <input type="date" class="border border-gray-300 rounded-md text-sm p-1.5">
                     <span class="mx-2 text-gray-500">~</span>
                     <input type="date" class="border border-gray-300 rounded-md text-sm p-1.5">
                     <button class="ml-2 p-2 bg-gray-700 text-white rounded-md hover:bg-gray-800"><i data-feather="search" class="w-4 h-4"></i></button>
                </div>
            </div>
        </section>

        <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="card p-5">
                <p class="text-sm font-semibold text-gray-500">기간 내 총 시험 건수</p>
                <p class="text-4xl font-bold text-gray-800 mt-2">1,240 <span class="text-base font-medium text-gray-500">건</span></p>
            </div>
            <div class="card p-5">
                <p class="text-sm font-semibold text-gray-500">평균 부적합률</p>
                <p class="text-4xl font-bold text-red-500 mt-2">12.8 <span class="text-base font-medium text-red-500">%</span></p>
            </div>
             <div class="card p-5">
                <p class="text-sm font-semibold text-gray-500">최다 부적합 항목</p>
                <p class="text-2xl font-bold text-gray-800 mt-3 truncate">총인 (T-P)</p>
            </div>
            <div class="card p-5">
                <p class="text-sm font-semibold text-gray-500">품질 점수 추이</p>
                <div class="flex items-center mt-2">
                    <p class="text-4xl font-bold text-green-500">5.2%</p>
                    <i data-feather="trending-up" class="ml-2 text-green-500"></i>
                    <span class="ml-1 text-sm text-gray-500">(지난 분기 대비)</span>
                </div>
            </div>
        </section>

        <section class="space-y-8">
            <div class="card p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">주요 항목 트렌드 (최근 3개월)</h3>
                <img src="https://i.imgur.com/w4pB4lW.png" alt="Trend Line Chart Placeholder" class="w-full h-auto">
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div class="card p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">월별 품질 현황</h3>
                    <img src="https://i.imgur.com/rN55a6N.png" alt="Stacked Bar Chart Placeholder" class="w-full h-auto">
                </div>
                <div class="card p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">일별 부적합 히트맵</h3>
                     <img src="https://i.imgur.com/HnUjQh5.png" alt="Calendar Heatmap Placeholder" class="w-full h-auto">
                </div>
            </div>
        </section>
    </main>
    <script src="https://cdn.jsdelivr.net/npm/feather-icons/dist/feather.min.js"></script>
    <script>
        feather.replace();
    </script>
</body>
</html>
```