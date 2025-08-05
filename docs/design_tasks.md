# Aqua-Analytics: 환경 데이터 인사이트 플랫폼 - 디자인 개선 태스크

## 프로젝트 개요
**기존**: 실험실 품질관리 대시보드  
**신규**: Aqua-Analytics - 환경 데이터 인사이트 플랫폼  
**목표**: 복잡한 데이터를 한눈에 파악할 수 있는 통합적인 뷰 제공, 미니멀하고 직관적인 UX/UI

## 핵심 개선 방향: 'All-in-One' 통합 대시보드
단일 화면 내에서 ①핵심 지표 확인 → ②시각적 탐색 → ③상세 데이터 분석 → ④보고서 생성의 전 과정을 유기적으로 수행

---

## 🎯 Phase 1: 브랜딩 및 기본 레이아웃 개선

### Task 1.1: 브랜딩 변경
- [ ] 프로젝트명 변경: "실험실 품질관리 대시보드" → "Aqua-Analytics"
- [ ] 로고 및 아이콘 시스템 적용 (Feather Icons/Lucide Icons)
- [ ] 컬러 팔레트 정의 및 적용
  - 기본: White (#ffffff), Light Gray (#f8fafc)
  - 포인트: Blue 계열 (#3b82f6, #1e40af)
  - 경고: Soft Red (#ef4444, #dc2626)
- [ ] 폰트 시스템 적용 (Inter, Pretendard)

### Task 1.2: 사이드바 네비게이션 개선
- [ ] 미니멀한 사이드바 디자인 구현
- [ ] 메뉴 구조 개선:
  - 📊 대시보드 (메인)
  - 📄 보고서 관리
  - 🛡️ 시험 규격 관리 (신규)
  - ☁️ 파일 업로드
- [ ] 사용자 프로필 영역 추가
- [ ] 파일 업로드 CTA 카드 추가

**우선순위**: 🔴 High  
**예상 소요시간**: 4-6시간  
**담당 파일**: `src/components/sidebar_navigation.py`, `app.py`

---

## 🎯 Phase 2: 컴팩트 KPI 카드 시스템

### Task 2.1: KPI 카드 디자인 개선
- [ ] 기존 st.metric을 커스텀 카드 컴포넌트로 교체
- [ ] 카드별 아이콘 및 색상 시스템 적용
- [ ] 호버 효과 구현 (transform, shadow)
- [ ] 툴팁 시스템 구현 (부적합 항목 Top 5 등)

### Task 2.2: KPI 데이터 확장
- [ ] 기존 4개 지표 유지 + 부가 정보 추가
  - 총 시험 항목 + 시료/항목 세부 정보
  - 부적합 항목 수 + Top 부적합 항목명
  - 부적합률 + 상세 비율 정보
  - 주요 부적합 시험 (신규)
- [ ] 실시간 데이터 업데이트 기능

**우선순위**: 🔴 High  
**예상 소요시간**: 6-8시간  
**담당 파일**: `src/components/kpi_cards.py` (신규), `src/core/dynamic_dashboard_engine.py`

---

## 🎯 Phase 3: 통합 대시보드 레이아웃

### Task 3.1: 메인 대시보드 레이아웃 재구성
- [ ] 상단: 컴팩트 KPI 카드 4개 (grid-cols-4)
- [ ] 중단: 좌측 인터랙티브 차트 (2/3) + 우측 리포트 요약 (1/3)
- [ ] 하단: 접을 수 있는 상세 데이터 테이블
- [ ] 반응형 디자인 적용 (모바일/태블릿 대응)

### Task 3.2: 인터랙티브 차트 시스템
- [ ] 차트 클릭 시 Cross-filtering 기능 구현
- [ ] 차트 → KPI 카드 연동
- [ ] 차트 → 리포트 요약 연동  
- [ ] 차트 → 데이터 테이블 필터링 연동
- [ ] 차트 애니메이션 및 인터랙션 개선

**우선순위**: 🟡 Medium  
**예상 소요시간**: 8-10시간  
**담당 파일**: `app.py`, `src/components/chart_system.py`, `src/core/dynamic_dashboard_engine.py`

---

## 🎯 Phase 4: 품질 분석 리포트 요약 시스템

### Task 4.1: 리포트 요약 컴포넌트
- [ ] 기존 리포트 내용을 요약한 텍스트 블록 생성
- [ ] 핵심 인사이트 자동 추출 기능
- [ ] 부적합 항목 하이라이트 표시
- [ ] [미리보기] 버튼 구현

### Task 4.2: 모달 기반 리포트 미리보기
- [ ] 전체 화면 모달 창 구현
- [ ] HTML/PDF 보고서 실시간 렌더링
- [ ] 모달 상단 액션 버튼 (PDF 다운로드, 인쇄)
- [ ] 모달 내 스크롤 및 확대/축소 기능

**우선순위**: 🟡 Medium  
**예상 소요시간**: 6-8시간  
**담당 파일**: `src/components/report_preview_modal.py` (신규), `src/core/report_generator.py`

---

## 🎯 Phase 5: 접을 수 있는 데이터 테이블

### Task 5.1: Collapsible 테이블 구현
- [ ] 기본 상태: 접힌 상태로 요약 정보만 표시
- [ ] 클릭 시 부드러운 애니메이션으로 확장
- [ ] 테이블 헤더 고정 및 가상 스크롤링
- [ ] 행별 규격 아이콘 추가 (규격 파일 연결)

### Task 5.2: 테이블 인터랙션 개선
- [ ] 정렬, 필터링, 검색 기능 강화
- [ ] 부적합 행 시각적 하이라이트
- [ ] 행 선택 시 상세 정보 사이드 패널 표시
- [ ] 테이블 데이터 내보내기 기능

**우선순위**: 🟢 Low  
**예상 소요시간**: 4-6시간  
**담당 파일**: `src/components/interactive_data_table.py`

---

## 🎯 Phase 6: 시험 규격 관리 시스템 (신규)

### Task 6.1: 규격 파일 관리 페이지
- [ ] 사이드바에 "시험 규격 관리" 메뉴 추가
- [ ] 규격 파일 업로드 인터페이스 (PDF, DOCX 지원)
- [ ] 규격 파일 목록 관리 테이블
- [ ] 파일 미리보기 및 다운로드 기능

### Task 6.2: 규격 연결 시스템
- [ ] 시험 항목별 규격 파일 매핑 기능
- [ ] 데이터 테이블 행별 규격 아이콘 표시
- [ ] 규격 아이콘 클릭 시 파일 즉시 열기
- [ ] 규격 파일 버전 관리 기능

**우선순위**: 🟢 Low  
**예상 소요시간**: 8-10시간  
**담당 파일**: `src/components/standards_management.py` (신규), `src/core/standards_processor.py` (신규)

---

## 🎯 Phase 7: 전체 디자인 시스템 통합

### Task 7.1: 디자인 토큰 시스템
- [ ] CSS 변수 기반 디자인 토큰 정의
- [ ] 컴포넌트별 일관된 스타일 가이드 적용
- [ ] 다크 모드 지원 (선택사항)
- [ ] 접근성 (a11y) 개선

### Task 7.2: 성능 최적화
- [ ] 컴포넌트 지연 로딩 (Lazy Loading)
- [ ] 차트 렌더링 최적화
- [ ] 메모리 사용량 최적화
- [ ] 로딩 상태 및 스켈레톤 UI 추가

**우선순위**: 🟡 Medium  
**예상 소요시간**: 6-8시간  
**담당 파일**: 전체 컴포넌트

---

## 📋 구현 우선순위 및 일정

### Week 1: 기본 브랜딩 및 레이아웃
- Phase 1: 브랜딩 및 기본 레이아웃 개선
- Phase 2: 컴팩트 KPI 카드 시스템

### Week 2: 핵심 기능 개선
- Phase 3: 통합 대시보드 레이아웃
- Phase 4: 품질 분석 리포트 요약 시스템

### Week 3: 고급 기능 및 최적화
- Phase 5: 접을 수 있는 데이터 테이블
- Phase 7: 전체 디자인 시스템 통합

### Week 4: 추가 기능 (선택사항)
- Phase 6: 시험 규격 관리 시스템

---

## 🎨 디자인 시스템 가이드

### 컬러 팔레트
```css
:root {
  /* Primary Colors */
  --color-primary-50: #eff6ff;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  
  /* Gray Scale */
  --color-gray-50: #f8fafc;
  --color-gray-100: #f1f5f9;
  --color-gray-500: #64748b;
  --color-gray-800: #1e293b;
  
  /* Status Colors */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
}
```

### 타이포그래피
- **Heading**: Inter, 700 weight
- **Body**: Inter, 400-500 weight
- **Caption**: Inter, 400 weight, 0.875rem

### 간격 시스템
- **xs**: 0.25rem (4px)
- **sm**: 0.5rem (8px)
- **md**: 1rem (16px)
- **lg**: 1.5rem (24px)
- **xl**: 2rem (32px)

---

## 📁 파일 구조 변경사항

```
src/
├── components/
│   ├── aqua_sidebar.py (신규)
│   ├── kpi_cards.py (신규)
│   ├── report_preview_modal.py (신규)
│   ├── standards_management.py (신규)
│   └── collapsible_table.py (신규)
├── core/
│   ├── standards_processor.py (신규)
│   └── ui_theme.py (신규)
├── assets/
│   ├── styles/
│   │   ├── aqua_theme.css (신규)
│   │   └── components.css (신규)
│   └── icons/ (신규)
└── utils/
    └── design_tokens.py (신규)
```

---

## ✅ 완료 체크리스트

각 Phase 완료 시 다음 항목들을 확인:

- [ ] 기능 동작 테스트 완료
- [ ] 반응형 디자인 확인
- [ ] 접근성 테스트 완료
- [ ] 성능 테스트 완료
- [ ] 코드 리뷰 완료
- [ ] 문서 업데이트 완료

---

## 🚀 기대 효과

1. **업무 효율성 증대**: 단일 화면 내에서 대부분의 분석 작업 완료
2. **데이터 접근성 향상**: 인터랙티브 차트와 유기적인 필터링
3. **사용자 만족도 제고**: 세련되고 직관적인 UI
4. **전문성 강화**: Aqua-Analytics 브랜딩으로 신뢰도 향상

---

*이 문서는 프로젝트 진행에 따라 지속적으로 업데이트됩니다.*