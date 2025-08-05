"""
인터랙티브 데이터 테이블 구현
HTML 기반 고정 높이 스크롤 테이블과 인터랙션 기능 제공
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional, Callable
from src.core.data_models import TestResult
import json


class InteractiveDataTable:
    """인터랙티브 데이터 테이블 클래스"""
    
    def __init__(self, height: int = 500):
        """
        인터랙티브 데이터 테이블 초기화
        
        Args:
            height: 테이블 고정 높이 (픽셀)
        """
        self.height = height
        self.current_data = []
        self.filtered_data = []
        self.selected_row_index = None
        self.sort_column = None
        self.sort_ascending = True
        self.search_term = ""
        self._initialize_session_state()
    
    def _initialize_session_state(self) -> None:
        """Streamlit 세션 상태 초기화"""
        if 'interactive_table' not in st.session_state:
            st.session_state.interactive_table = {
                'selected_row_index': None,
                'sort_column': '시료명',
                'sort_ascending': True,
                'search_term': '',
                'last_clicked_row': None
            }
    
    def render_table_structure(self, data: List[TestResult], 
                             on_row_select: Optional[Callable] = None) -> None:
        """
        데이터 테이블 기본 구조 구현 (요구사항 3.1, 3.6)
        - HTML 테이블 구조 생성
        - 고정 높이 스크롤 기능 구현  
        - Sticky 헤더 구현
        
        Args:
            data: 시험 결과 데이터 리스트
            on_row_select: 행 선택 시 호출될 콜백 함수
        """
        if not data:
            st.info("표시할 데이터가 없습니다.")
            return
        
        self.current_data = data
        
        # 테이블 데이터 준비
        table_data = self._prepare_table_data(data)
        
        # 검색 및 필터링 적용
        filtered_data = self._apply_search_filter(table_data)
        
        # 정렬 적용
        sorted_data = self._apply_sorting(filtered_data)
        
        self.filtered_data = sorted_data
        
        # HTML 테이블 구조 생성
        table_html = self._generate_table_html(sorted_data)
        
        # 스타일과 함께 테이블 렌더링
        st.markdown(
            f"""
            <div style="height: {self.height}px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 8px;">
                {table_html}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 행 선택 처리
        self._handle_row_selection(sorted_data, on_row_select)
    
    def _prepare_table_data(self, data: List[TestResult]) -> List[Dict[str, Any]]:
        """테이블 표시용 데이터 준비"""
        table_data = []
        for i, result in enumerate(data):
            table_data.append({
                'index': i,
                'id': f"row_{i}",
                '시료명': result.sample_name,
                '시험항목': result.test_item,
                '결과': result.get_display_result(),
                '판정': result.standard_excess,
                '단위': result.test_unit,
                '시험자': result.tester,
                '분석번호': result.analysis_number,
                '입력일시': result.input_datetime.strftime('%Y-%m-%d %H:%M') if result.input_datetime and hasattr(result.input_datetime, 'strftime') else str(result.input_datetime) if result.input_datetime else '',
                'is_violation': result.is_non_conforming(),
                'original_data': result
            })
        return table_data
    
    def _apply_search_filter(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """검색 및 필터 적용 (요구사항 3.2, 3.3)"""
        filtered = data.copy()
        
        # 1. 텍스트 검색 필터
        search_term = st.session_state.interactive_table.get('search_term', '').lower()
        if search_term:
            filtered = [
                row for row in filtered
                if (search_term in row['시료명'].lower() or 
                    search_term in row['시험항목'].lower() or 
                    search_term in row['시험자'].lower() or
                    search_term in row['판정'].lower())
            ]
        
        # 2. 판정 상태 필터
        judgment_filter = st.session_state.interactive_table.get('judgment_filter', '전체')
        if judgment_filter != '전체':
            filtered = [
                row for row in filtered
                if row['판정'] == judgment_filter
            ]
        
        # 3. 부적합만 보기 필터 (요구사항 3.3)
        show_violations_only = st.session_state.interactive_table.get('show_violations_only', False)
        if show_violations_only:
            filtered = [
                row for row in filtered
                if row['is_violation']
            ]
        
        return filtered
    
    def _apply_sorting(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """정렬 적용"""
        sort_column = st.session_state.interactive_table.get('sort_column', '시료명')
        sort_ascending = st.session_state.interactive_table.get('sort_ascending', True)
        
        if sort_column and sort_column in ['시료명', '시험항목', '결과', '판정', '시험자', '입력일시']:
            try:
                return sorted(data, key=lambda x: x[sort_column], reverse=not sort_ascending)
            except (KeyError, TypeError):
                return data
        
        return data
    
    def _generate_table_html(self, data: List[Dict[str, Any]]) -> str:
        """
        HTML 테이블 구조 생성
        고정 높이 스크롤과 Sticky 헤더 포함
        컬럼 헤더 정렬 기능 포함 (요구사항 3.2)
        """
        # 현재 정렬 상태
        sort_column = st.session_state.interactive_table.get('sort_column', '시료명')
        sort_ascending = st.session_state.interactive_table.get('sort_ascending', True)
        
        # 정렬 아이콘
        def get_sort_icon(column_name):
            if column_name == sort_column:
                return "↑" if sort_ascending else "↓"
            return "↕"
        
        # 테이블 헤더 (클릭 가능한 정렬 헤더)
        header_html = f"""
        <div id="table-container" style="height: {self.height}px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 8px; background: white;">
            <table id="interactive-table" style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <thead style="position: sticky; top: 0; background-color: #f1f5f9; z-index: 10; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <tr style="border-bottom: 2px solid #e2e8f0;">
                        <th style="padding: 12px 16px; text-align: left; font-weight: 600; color: #374151; border-right: 1px solid #e2e8f0; cursor: pointer; user-select: none; transition: background-color 0.2s;" 
                            onclick="sortTable('시료명')" title="클릭하여 정렬"
                            onmouseover="this.style.backgroundColor='#e2e8f0'" onmouseout="this.style.backgroundColor='#f1f5f9'">
                            시료명 <span style="color: #6b7280; font-size: 12px;">{get_sort_icon('시료명')}</span>
                        </th>
                        <th style="padding: 12px 16px; text-align: left; font-weight: 600; color: #374151; border-right: 1px solid #e2e8f0; cursor: pointer; user-select: none; transition: background-color 0.2s;" 
                            onclick="sortTable('시험항목')" title="클릭하여 정렬"
                            onmouseover="this.style.backgroundColor='#e2e8f0'" onmouseout="this.style.backgroundColor='#f1f5f9'">
                            시험항목 <span style="color: #6b7280; font-size: 12px;">{get_sort_icon('시험항목')}</span>
                        </th>
                        <th style="padding: 12px 16px; text-align: left; font-weight: 600; color: #374151; border-right: 1px solid #e2e8f0; cursor: pointer; user-select: none; transition: background-color 0.2s;" 
                            onclick="sortTable('결과')" title="클릭하여 정렬"
                            onmouseover="this.style.backgroundColor='#e2e8f0'" onmouseout="this.style.backgroundColor='#f1f5f9'">
                            결과 <span style="color: #6b7280; font-size: 12px;">{get_sort_icon('결과')}</span>
                        </th>
                        <th style="padding: 12px 16px; text-align: left; font-weight: 600; color: #374151; border-right: 1px solid #e2e8f0; cursor: pointer; user-select: none; transition: background-color 0.2s;" 
                            onclick="sortTable('판정')" title="클릭하여 정렬"
                            onmouseover="this.style.backgroundColor='#e2e8f0'" onmouseout="this.style.backgroundColor='#f1f5f9'">
                            판정 <span style="color: #6b7280; font-size: 12px;">{get_sort_icon('판정')}</span>
                        </th>
                        <th style="padding: 12px 16px; text-align: left; font-weight: 600; color: #374151; cursor: pointer; user-select: none; transition: background-color 0.2s;" 
                            onclick="sortTable('시험자')" title="클릭하여 정렬"
                            onmouseover="this.style.backgroundColor='#e2e8f0'" onmouseout="this.style.backgroundColor='#f1f5f9'">
                            시험자 <span style="color: #6b7280; font-size: 12px;">{get_sort_icon('시험자')}</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # 테이블 바디
        body_html = ""
        for i, row in enumerate(data):
            # 부적합 행 스타일링 (요구사항 3.3)
            row_style = "transition: all 0.2s ease;"
            row_class = ""
            if row['is_violation']:
                row_style += " background-color: #fef2f2; border-left: 4px solid #ef4444;"
                row_class = "violation-row"
            
            # 선택된 행 스타일링 (요구사항 3.4, 3.5)
            selected_index = st.session_state.interactive_table.get('selected_row_index')
            if selected_index == row['index']:
                row_style += " background-color: #dbeafe; border: 2px solid #3b82f6; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);"
                row_class += " selected-row"
            
            # 호버 효과
            if row['is_violation']:
                hover_enter = "this.style.backgroundColor='#fef7f7'; this.style.transform='scale(1.01)'"
                hover_leave = "this.style.backgroundColor='#fef2f2'; this.style.transform='scale(1)'"
            else:
                hover_enter = "this.style.backgroundColor='#f8fafc'; this.style.transform='scale(1.01)'"
                hover_leave = "this.style.backgroundColor=''; this.style.transform='scale(1)'"
            
            body_html += f"""
            <tr id="row-{row['index']}" class="{row_class}" 
                style="border-bottom: 1px solid #e2e8f0; cursor: pointer; {row_style}" 
                onmouseover="{hover_enter}" 
                onmouseout="{hover_leave}"
                onclick="selectRow({row['index']})"
                data-row-index="{row['index']}"
                data-sample-name="{row['시료명']}"
                data-test-item="{row['시험항목']}"
                data-is-violation="{str(row['is_violation']).lower()}">
                <td style="padding: 12px 16px; border-right: 1px solid #e2e8f0; font-weight: 500;">{row['시료명']}</td>
                <td style="padding: 12px 16px; border-right: 1px solid #e2e8f0; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{row['시험항목']}">{row['시험항목']}</td>
                <td style="padding: 12px 16px; border-right: 1px solid #e2e8f0; font-weight: 600; {'color: #dc2626;' if row['is_violation'] else 'color: #374151;'}">{row['결과']} {row['단위']}</td>
                <td style="padding: 12px 16px; border-right: 1px solid #e2e8f0;">
                    <span style="padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; {'background-color: #fee2e2; color: #dc2626;' if row['is_violation'] else 'background-color: #dcfce7; color: #16a34a;'}">
                        {row['판정']}
                    </span>
                </td>
                <td style="padding: 12px 16px; color: #6b7280;">{row['시험자']}</td>
            </tr>
            """
        
        # 테이블 닫기
        footer_html = """
                </tbody>
            </table>
        </div>
        """
        
        # 향상된 JavaScript 추가 (요구사항 3.2, 3.3, 3.4, 3.5)
        javascript = f"""
        <script>
        // 전역 변수
        let selectedRowIndex = {st.session_state.interactive_table.get('selected_row_index', 'null')};
        let currentSortColumn = '{sort_column}';
        let currentSortAscending = {str(sort_ascending).lower()};
        let searchTerm = '';
        let filteredRows = [];
        
        // 행 선택 함수 (요구사항 3.4, 3.5)
        function selectRow(index) {{
            // 이전 선택 해제
            const previousSelected = document.querySelector('tr.selected-row');
            if (previousSelected) {{
                previousSelected.classList.remove('selected-row');
                resetRowStyle(previousSelected);
            }}
            
            // 새로운 행 선택
            const targetRow = document.querySelector(`tr[data-row-index="${{index}}"]`);
            if (targetRow) {{
                targetRow.classList.add('selected-row');
                targetRow.style.backgroundColor = '#dbeafe';
                targetRow.style.border = '2px solid #3b82f6';
                targetRow.style.boxShadow = '0 2px 8px rgba(59, 130, 246, 0.3)';
                selectedRowIndex = index;
                
                // 선택된 행으로 스크롤
                targetRow.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                
                // Streamlit에 선택 이벤트 전달
                if (window.parent) {{
                    window.parent.postMessage({{
                        type: 'table_row_selected',
                        index: index,
                        sampleName: targetRow.dataset.sampleName,
                        testItem: targetRow.dataset.testItem,
                        isViolation: targetRow.dataset.isViolation === 'true'
                    }}, '*');
                }}
                
                // 상세 정보 패널 업데이트 트리거
                updateDetailPanel(index);
            }}
        }}
        
        // 행 스타일 초기화
        function resetRowStyle(row) {{
            const isViolation = row.dataset.isViolation === 'true';
            if (isViolation) {{
                row.style.backgroundColor = '#fef2f2';
                row.style.borderLeft = '4px solid #ef4444';
                row.style.border = '';
                row.style.boxShadow = '';
            }} else {{
                row.style.backgroundColor = '';
                row.style.border = '';
                row.style.boxShadow = '';
            }}
        }}
        
        // 테이블 정렬 함수 (요구사항 3.2)
        function sortTable(column) {{
            // 정렬 상태 업데이트
            if (currentSortColumn === column) {{
                currentSortAscending = !currentSortAscending;
            }} else {{
                currentSortColumn = column;
                currentSortAscending = true;
            }}
            
            // 시각적 피드백
            showSortingIndicator(column, currentSortAscending);
            
            // Streamlit에 정렬 이벤트 전달
            if (window.parent) {{
                window.parent.postMessage({{
                    type: 'table_sort_changed',
                    column: column,
                    ascending: currentSortAscending
                }}, '*');
            }}
        }}
        
        // 정렬 인디케이터 표시
        function showSortingIndicator(column, ascending) {{
            const headers = document.querySelectorAll('#interactive-table th');
            headers.forEach(header => {{
                if (header.textContent.includes(column)) {{
                    header.style.backgroundColor = '#e2e8f0';
                    setTimeout(() => {{
                        header.style.backgroundColor = '#f1f5f9';
                    }}, 200);
                }}
            }});
        }}
        
        // 실시간 검색 함수 (요구사항 3.2)
        function filterTable(searchTerm) {{
            const rows = document.querySelectorAll('#interactive-table tbody tr');
            const term = searchTerm.toLowerCase();
            let visibleCount = 0;
            
            filteredRows = [];
            
            rows.forEach((row, index) => {{
                const cells = row.querySelectorAll('td');
                let found = false;
                
                cells.forEach(cell => {{
                    if (cell.textContent.toLowerCase().includes(term)) {{
                        found = true;
                    }}
                }});
                
                if (found || term === '') {{
                    row.style.display = '';
                    row.classList.remove('filtered-out');
                    filteredRows.push(row);
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                    row.classList.add('filtered-out');
                }}
            }});
            
            // 검색 결과 표시
            updateSearchResults(visibleCount, rows.length);
        }}
        
        // 검색 결과 업데이트
        function updateSearchResults(visible, total) {{
            // 검색 결과 정보를 부모 창에 전달
            if (window.parent) {{
                window.parent.postMessage({{
                    type: 'search_results_updated',
                    visible: visible,
                    total: total
                }}, '*');
            }}
        }}
        
        // 부적합 행 강조 함수 (요구사항 3.3)
        function highlightViolations() {{
            const rows = document.querySelectorAll('#interactive-table tbody tr');
            rows.forEach(row => {{
                if (row.dataset.isViolation === 'true') {{
                    row.style.backgroundColor = '#fef2f2';
                    row.style.borderLeft = '4px solid #ef4444';
                    row.classList.add('violation-row');
                    
                    // 부적합 행에 펄스 애니메이션 추가
                    row.style.animation = 'violationPulse 2s ease-in-out infinite';
                }}
            }});
        }}
        
        // 부적합 항목만 필터링
        function filterViolationsOnly(showOnly) {{
            const rows = document.querySelectorAll('#interactive-table tbody tr');
            let visibleCount = 0;
            
            rows.forEach(row => {{
                const isViolation = row.dataset.isViolation === 'true';
                
                if (showOnly) {{
                    if (isViolation) {{
                        row.style.display = '';
                        visibleCount++;
                    }} else {{
                        row.style.display = 'none';
                    }}
                }} else {{
                    row.style.display = '';
                    visibleCount++;
                }}
            }});
            
            updateSearchResults(visibleCount, rows.length);
        }}
        
        // 키보드 네비게이션 (요구사항 3.4, 3.5)
        function initializeKeyboardNavigation() {{
            document.addEventListener('keydown', function(e) {{
                const visibleRows = document.querySelectorAll('#interactive-table tbody tr:not([style*="display: none"])');
                let currentIndex = -1;
                
                // 현재 선택된 행 찾기
                visibleRows.forEach((row, index) => {{
                    if (row.classList.contains('selected-row')) {{
                        currentIndex = index;
                    }}
                }});
                
                // 화살표 키 처리
                if (e.key === 'ArrowDown' && currentIndex < visibleRows.length - 1) {{
                    e.preventDefault();
                    const nextRow = visibleRows[currentIndex + 1];
                    selectRow(parseInt(nextRow.dataset.rowIndex));
                }} else if (e.key === 'ArrowUp' && currentIndex > 0) {{
                    e.preventDefault();
                    const prevRow = visibleRows[currentIndex - 1];
                    selectRow(parseInt(prevRow.dataset.rowIndex));
                }} else if (e.key === 'Enter' && currentIndex >= 0) {{
                    e.preventDefault();
                    const currentRow = visibleRows[currentIndex];
                    // 엔터키로 상세 정보 토글
                    toggleDetailPanel(parseInt(currentRow.dataset.rowIndex));
                }}
            }});
        }}
        
        // 상세 정보 패널 업데이트
        function updateDetailPanel(index) {{
            // 상세 정보 패널 업데이트 로직은 부모 컴포넌트에서 처리
            console.log(`Detail panel updated for row index: ${{index}}`);
        }}
        
        // 상세 정보 패널 토글
        function toggleDetailPanel(index) {{
            if (window.parent) {{
                window.parent.postMessage({{
                    type: 'toggle_detail_panel',
                    index: index
                }}, '*');
            }}
        }}
        
        // CSS 애니메이션 추가
        const style = document.createElement('style');
        style.textContent = `
            @keyframes violationPulse {{
                0%, 100% {{ border-left-color: #ef4444; }}
                50% {{ border-left-color: #fca5a5; }}
            }}
            
            .violation-row {{
                position: relative;
            }}
            
            .violation-row::before {{
                content: '⚠️';
                position: absolute;
                left: -2px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 12px;
                z-index: 1;
            }}
            
            .selected-row {{
                position: relative;
                z-index: 2;
            }}
            
            #interactive-table tbody tr:hover {{
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .filtered-out {{
                opacity: 0.3;
                transition: opacity 0.3s ease;
            }}
        `;
        document.head.appendChild(style);
        
        // 테이블 초기화
        function initializeTable() {{
            highlightViolations();
            initializeKeyboardNavigation();
            
            // 초기 선택된 행이 있다면 스타일 적용
            if (selectedRowIndex !== null) {{
                selectRow(selectedRowIndex);
            }}
            
            console.log('Interactive table initialized successfully');
        }}
        
        // DOM 로드 완료 시 초기화
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initializeTable);
        }} else {{
            initializeTable();
        }}
        </script>
        """
        
        return header_html + body_html + footer_html + javascript
    
    def _handle_row_selection(self, data: List[Dict[str, Any]], 
                            on_row_select: Optional[Callable] = None) -> None:
        """행 선택 처리"""
        # 행 선택을 위한 selectbox (임시 구현)
        if data:
            selected_index = st.selectbox(
                "행 선택 (상세 정보 보기)",
                options=range(len(data)),
                format_func=lambda x: f"{data[x]['시료명']} - {data[x]['시험항목'][:30]}{'...' if len(data[x]['시험항목']) > 30 else ''}",
                key="interactive_table_row_selector",
                index=st.session_state.interactive_table.get('selected_row_index', 0) if st.session_state.interactive_table.get('selected_row_index') is not None else 0
            )
            
            if selected_index is not None:
                # 세션 상태 업데이트
                st.session_state.interactive_table['selected_row_index'] = data[selected_index]['index']
                
                # 콜백 함수 호출
                if on_row_select:
                    original_data = data[selected_index]['original_data']
                    on_row_select(original_data)
    
    def render_search_and_controls(self) -> None:
        """검색 및 제어 UI 렌더링 (요구사항 3.2)"""
        # 검색 및 필터 컨트롤 카드
        with st.container():
            st.markdown("""
            <div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem;">
                <h4 style="margin: 0 0 1rem 0; color: #374151; font-weight: 600;">🔍 테이블 검색 및 필터</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # 첫 번째 행: 실시간 검색
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # 실시간 검색 기능 (요구사항 3.2)
                search_term = st.text_input(
                    "",
                    placeholder="🔍 시료명, 시험항목, 시험자, 판정으로 실시간 검색...",
                    key="table_search_input",
                    value=st.session_state.interactive_table.get('search_term', ''),
                    help="입력하는 즉시 테이블이 필터링됩니다",
                    label_visibility="collapsed"
                )
                
                if search_term != st.session_state.interactive_table.get('search_term', ''):
                    st.session_state.interactive_table['search_term'] = search_term
                    st.rerun()
            
            with col2:
                # 검색 초기화 버튼
                if st.button("🗑️ 검색 초기화", key="clear_search", help="검색어를 초기화합니다"):
                    st.session_state.interactive_table['search_term'] = ''
                    st.rerun()
            
            # 두 번째 행: 필터 및 정렬 옵션
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                # 판정 상태 필터
                judgment_filter = st.selectbox(
                    "📊 판정 필터",
                    options=['전체', '적합', '부적합'],
                    key="judgment_filter",
                    index=0,
                    help="특정 판정 결과만 필터링"
                )
                
                if judgment_filter != st.session_state.interactive_table.get('judgment_filter', '전체'):
                    st.session_state.interactive_table['judgment_filter'] = judgment_filter
                    st.rerun()
            
            with col2:
                # 컬럼 헤더 정렬 기능 (요구사항 3.2)
                sort_column = st.selectbox(
                    "📈 정렬 기준",
                    options=['시료명', '시험항목', '결과', '판정', '시험자', '입력일시'],
                    key="table_sort_column",
                    index=['시료명', '시험항목', '결과', '판정', '시험자', '입력일시'].index(
                        st.session_state.interactive_table.get('sort_column', '시료명')
                    ),
                    help="테이블 정렬 기준 선택"
                )
                
                if sort_column != st.session_state.interactive_table.get('sort_column'):
                    st.session_state.interactive_table['sort_column'] = sort_column
                    st.rerun()
            
            with col3:
                # 정렬 순서 및 부적합 필터
                sort_ascending = st.checkbox(
                    "⬆️ 오름차순",
                    value=st.session_state.interactive_table.get('sort_ascending', True),
                    key="table_sort_order",
                    help="정렬 순서 선택"
                )
                
                if sort_ascending != st.session_state.interactive_table.get('sort_ascending'):
                    st.session_state.interactive_table['sort_ascending'] = sort_ascending
                    st.rerun()
                
                # 부적합 항목만 보기 (요구사항 3.3)
                show_violations_only = st.checkbox(
                    "⚠️ 부적합만 보기",
                    key="show_violations_only",
                    value=st.session_state.interactive_table.get('show_violations_only', False),
                    help="부적합 항목만 필터링하여 표시"
                )
                
                if show_violations_only != st.session_state.interactive_table.get('show_violations_only', False):
                    st.session_state.interactive_table['show_violations_only'] = show_violations_only
                    st.rerun()
            
            with col4:
                # 테이블 새로고침 및 내보내기
                if st.button("🔄", key="table_refresh", help="테이블 새로고침"):
                    st.session_state.interactive_table['search_term'] = ''
                    st.session_state.interactive_table['judgment_filter'] = '전체'
                    st.session_state.interactive_table['selected_row_index'] = None
                    st.session_state.interactive_table['show_violations_only'] = False
                    st.rerun()
                
                if st.button("📥", key="export_table", help="테이블 데이터 내보내기"):
                    st.info("데이터 내보내기 기능은 다음 단계에서 구현됩니다.")
        
        # 필터 상태 표시
        self._render_filter_status()
    
    def render_table_summary(self) -> None:
        """테이블 요약 정보 표시"""
        if not self.filtered_data:
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("표시된 행 수", len(self.filtered_data))
        
        with col2:
            violation_count = sum(1 for row in self.filtered_data if row['is_violation'])
            st.metric("부적합 건수", violation_count)
        
        with col3:
            if len(self.filtered_data) > 0:
                violation_rate = (violation_count / len(self.filtered_data)) * 100
                st.metric("부적합 비율", f"{violation_rate:.1f}%")
        
        with col4:
            total_samples = len(set(row['시료명'] for row in self.filtered_data))
            st.metric("시료 수", total_samples)
    
    def get_selected_row(self) -> Optional[TestResult]:
        """선택된 행의 원본 데이터 반환"""
        selected_index = st.session_state.interactive_table.get('selected_row_index')
        
        if selected_index is not None and self.current_data:
            if 0 <= selected_index < len(self.current_data):
                return self.current_data[selected_index]
        
        return None
    
    def _render_filter_status(self) -> None:
        """필터 상태 표시"""
        search_term = st.session_state.interactive_table.get('search_term', '')
        judgment_filter = st.session_state.interactive_table.get('judgment_filter', '전체')
        show_violations_only = st.session_state.interactive_table.get('show_violations_only', False)
        
        active_filters = []
        
        if search_term:
            active_filters.append(f"🔍 검색: '{search_term}'")
        
        if judgment_filter != '전체':
            active_filters.append(f"📊 판정: {judgment_filter}")
        
        if show_violations_only:
            active_filters.append("⚠️ 부적합만 표시")
        
        if active_filters:
            filter_text = " | ".join(active_filters)
            st.markdown(f"""
            <div style="background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 6px; padding: 8px 12px; margin: 8px 0; font-size: 12px; color: #0c4a6e;">
                <strong>활성 필터:</strong> {filter_text}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px 12px; margin: 8px 0; font-size: 12px; color: #64748b;">
                <strong>필터 없음</strong> - 모든 데이터가 표시됩니다
            </div>
            """, unsafe_allow_html=True)
        
        if judgment_filter != '전체':
            active_filters.append(f"📊 판정: {judgment_filter}")
        
        if show_violations_only:
            active_filters.append("⚠️ 부적합만 표시")
        
        if active_filters:
            st.markdown(f"""
            <div style="background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 6px; padding: 8px 12px; margin-bottom: 1rem;">
                <small style="color: #0369a1;">
                    <strong>활성 필터:</strong> {' | '.join(active_filters)}
                </small>
            </div>
            """, unsafe_allow_html=True)

    def render_enhanced_table_with_interactions(self, data: List[TestResult], 
                                              on_row_select: Optional[Callable] = None) -> None:
        """
        향상된 인터랙티브 테이블 렌더링 (요구사항 3.2, 3.3, 3.4, 3.5, 3.6)
        - 컬럼 헤더 정렬 기능 구현
        - 실시간 검색/필터링 기능 구현
        - 행 선택 및 하이라이트 기능 구현
        - 부적합 행 시각적 강조 구현
        """
        if not data:
            st.info("표시할 데이터가 없습니다.")
            return
        
        self.current_data = data
        
        # 검색 및 제어 UI
        self.render_search_and_controls()
        
        # 테이블 데이터 준비 및 필터링
        table_data = self._prepare_table_data(data)
        filtered_data = self._apply_search_filter(table_data)
        sorted_data = self._apply_sorting(filtered_data)
        
        self.filtered_data = sorted_data
        
        # 테이블 요약 정보
        self.render_table_summary()
        
        # 향상된 HTML 테이블 생성
        enhanced_table_html = self._generate_enhanced_table_html(sorted_data)
        
        # 테이블 컨테이너
        st.markdown(enhanced_table_html, unsafe_allow_html=True)
        
        # JavaScript 이벤트 처리
        self._handle_javascript_events(sorted_data, on_row_select)
    
    def _generate_enhanced_table_html(self, data: List[Dict[str, Any]]) -> str:
        """
        향상된 HTML 테이블 생성 (요구사항 3.2, 3.3, 3.4, 3.5)
        - 클릭 가능한 정렬 헤더
        - 부적합 행 시각적 강조
        - 행 선택 및 하이라이트
        - 키보드 네비게이션 지원
        """
        # 현재 정렬 상태
        sort_column = st.session_state.interactive_table.get('sort_column', '시료명')
        sort_ascending = st.session_state.interactive_table.get('sort_ascending', True)
        selected_index = st.session_state.interactive_table.get('selected_row_index')
        
        # 정렬 아이콘 생성
        def get_sort_icon(column_name):
            if column_name == sort_column:
                return "🔼" if sort_ascending else "🔽"
            return "↕️"
        
        # 테이블 시작
        table_html = f"""
        <div id="enhanced-table-container" style="
            height: {self.height}px; 
            overflow-y: auto; 
            border: 2px solid #e2e8f0; 
            border-radius: 12px; 
            background: white;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
        ">
            <table id="enhanced-interactive-table" style="
                width: 100%; 
                border-collapse: collapse; 
                font-size: 14px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            ">
                <thead style="
                    position: sticky; 
                    top: 0; 
                    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                    z-index: 10; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <tr style="border-bottom: 2px solid #cbd5e1;">
        """
        
        # 헤더 컬럼들 (클릭 가능한 정렬 기능)
        headers = [
            ('시료명', '시료명'),
            ('시험항목', '시험항목'),
            ('결과', '결과'),
            ('판정', '판정'),
            ('시험자', '시험자')
        ]
        
        for header_key, header_display in headers:
            is_current_sort = header_key == sort_column
            header_style = f"""
                padding: 16px 20px; 
                text-align: left; 
                font-weight: 700; 
                color: {'#1e40af' if is_current_sort else '#374151'}; 
                border-right: 1px solid #cbd5e1; 
                cursor: pointer; 
                user-select: none; 
                transition: all 0.2s ease;
                background: {'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)' if is_current_sort else 'transparent'};
                position: relative;
            """
            
            table_html += f"""
                <th style="{header_style}" 
                    onclick="handleSort('{header_key}')" 
                    title="클릭하여 {header_display}(으)로 정렬"
                    onmouseover="this.style.background='linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)'" 
                    onmouseout="this.style.background='{'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)' if is_current_sort else 'transparent'}'"
                    data-column="{header_key}">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <span>{header_display}</span>
                        <span style="font-size: 12px; margin-left: 8px;">{get_sort_icon(header_key)}</span>
                    </div>
                </th>
            """
        
        table_html += """
                    </tr>
                </thead>
                <tbody id="enhanced-table-body">
        """
        
        # 테이블 바디 (데이터 행들)
        for i, row in enumerate(data):
            is_violation = row['is_violation']
            is_selected = selected_index == row['index']
            
            # 행 스타일 결정
            if is_selected:
                row_bg = "linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)"
                row_border = "2px solid #3b82f6"
                row_shadow = "0 4px 12px rgba(59, 130, 246, 0.3)"
            elif is_violation:
                row_bg = "linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)"
                row_border = "2px solid transparent"
                row_shadow = "0 2px 4px rgba(239, 68, 68, 0.2)"
            else:
                row_bg = "white"
                row_border = "2px solid transparent"
                row_shadow = "none"
            
            # 호버 효과 정의
            if is_violation:
                hover_enter = "this.style.background='linear-gradient(135deg, #fef7f7 0%, #fecaca 100%)'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(239, 68, 68, 0.3)'"
                hover_leave = f"this.style.background='{row_bg}'; this.style.transform='translateY(0)'; this.style.boxShadow='{row_shadow}'"
            else:
                hover_enter = "this.style.background='linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(0, 0, 0, 0.1)'"
                hover_leave = f"this.style.background='{row_bg}'; this.style.transform='translateY(0)'; this.style.boxShadow='{row_shadow}'"
            
            # 부적합 표시 아이콘
            violation_indicator = "⚠️" if is_violation else ""
            
            table_html += f"""
            <tr id="enhanced-row-{row['index']}" 
                class="{'violation-row' if is_violation else ''} {'selected-row' if is_selected else ''}"
                style="
                    border-bottom: 1px solid #e2e8f0; 
                    cursor: pointer; 
                    background: {row_bg};
                    border: {row_border};
                    box-shadow: {row_shadow};
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    position: relative;
                " 
                onmouseover="{hover_enter}" 
                onmouseout="{hover_leave}"
                onclick="handleRowSelect({row['index']})"
                data-row-index="{row['index']}"
                data-sample-name="{row['시료명']}"
                data-test-item="{row['시험항목']}"
                data-is-violation="{str(row['is_violation']).lower()}"
                data-judgment="{row['판정']}"
                tabindex="0"
                onkeydown="handleKeyNavigation(event, {row['index']})">
                
                <td style="
                    padding: 16px 20px; 
                    border-right: 1px solid #e2e8f0; 
                    font-weight: 600;
                    position: relative;
                ">
                    <div style="display: flex; align-items: center;">
                        {f'<span style="margin-right: 8px; font-size: 16px;">{violation_indicator}</span>' if violation_indicator else ''}
                        <span>{row['시료명']}</span>
                    </div>
                </td>
                
                <td style="
                    padding: 16px 20px; 
                    border-right: 1px solid #e2e8f0; 
                    max-width: 250px; 
                    overflow: hidden; 
                    text-overflow: ellipsis; 
                    white-space: nowrap;
                " title="{row['시험항목']}">
                    {row['시험항목']}
                </td>
                
                <td style="
                    padding: 16px 20px; 
                    border-right: 1px solid #e2e8f0; 
                    font-weight: 700;
                    color: {'#dc2626' if is_violation else '#374151'};
                ">
                    {row['결과']} {row['단위']}
                </td>
                
                <td style="padding: 16px 20px; border-right: 1px solid #e2e8f0;">
                    <span style="
                        padding: 6px 12px; 
                        border-radius: 20px; 
                        font-size: 12px; 
                        font-weight: 700; 
                        text-transform: uppercase;
                        {'background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); color: #dc2626; border: 1px solid #f87171;' if is_violation else 'background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); color: #16a34a; border: 1px solid #4ade80;'}
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    ">
                        {row['판정']}
                    </span>
                </td>
                
                <td style="
                    padding: 16px 20px; 
                    color: #6b7280;
                    font-style: italic;
                ">
                    {row['시험자']}
                </td>
            </tr>
            """
        
        # 테이블 종료
        table_html += """
                </tbody>
            </table>
        </div>
        """
        
        # 향상된 JavaScript 추가
        enhanced_javascript = f"""
        <script>
        // 전역 상태 관리
        let enhancedTableState = {{
            selectedRowIndex: {selected_index if selected_index is not None else 'null'},
            currentSortColumn: '{sort_column}',
            currentSortAscending: {str(sort_ascending).lower()},
            searchTerm: '',
            filteredRows: [],
            keyboardNavigationEnabled: true
        }};
        
        // 정렬 처리 함수 (요구사항 3.2)
        function handleSort(column) {{
            // 시각적 피드백
            const header = document.querySelector(`th[data-column="${{column}}"]`);
            if (header) {{
                header.style.transform = 'scale(0.95)';
                setTimeout(() => {{
                    header.style.transform = 'scale(1)';
                }}, 150);
            }}
            
            // 정렬 상태 업데이트
            if (enhancedTableState.currentSortColumn === column) {{
                enhancedTableState.currentSortAscending = !enhancedTableState.currentSortAscending;
            }} else {{
                enhancedTableState.currentSortColumn = column;
                enhancedTableState.currentSortAscending = true;
            }}
            
            // Streamlit에 정렬 변경 알림
            notifyStreamlit('sort_changed', {{
                column: column,
                ascending: enhancedTableState.currentSortAscending
            }});
            
            console.log(`Table sorted by ${{column}} (${{enhancedTableState.currentSortAscending ? 'ascending' : 'descending'}})`);
        }}
        
        // 행 선택 처리 함수 (요구사항 3.4, 3.5)
        function handleRowSelect(index) {{
            // 이전 선택 해제
            const previousSelected = document.querySelector('.selected-row');
            if (previousSelected) {{
                previousSelected.classList.remove('selected-row');
                resetRowStyle(previousSelected);
            }}
            
            // 새로운 행 선택
            const targetRow = document.querySelector(`#enhanced-row-${{index}}`);
            if (targetRow) {{
                targetRow.classList.add('selected-row');
                applySelectedStyle(targetRow);
                enhancedTableState.selectedRowIndex = index;
                
                // 선택된 행으로 부드럽게 스크롤
                targetRow.scrollIntoView({{ 
                    behavior: 'smooth', 
                    block: 'center',
                    inline: 'nearest'
                }});
                
                // 선택 효과 애니메이션
                targetRow.style.animation = 'selectedPulse 0.6s ease-in-out';
                setTimeout(() => {{
                    targetRow.style.animation = '';
                }}, 600);
                
                // Streamlit에 선택 이벤트 전달
                notifyStreamlit('row_selected', {{
                    index: index,
                    sampleName: targetRow.dataset.sampleName,
                    testItem: targetRow.dataset.testItem,
                    isViolation: targetRow.dataset.isViolation === 'true',
                    judgment: targetRow.dataset.judgment
                }});
                
                console.log(`Row selected: index ${{index}}, sample: ${{targetRow.dataset.sampleName}}`);
            }}
        }}
        
        // 선택된 행 스타일 적용
        function applySelectedStyle(row) {{
            row.style.background = 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)';
            row.style.border = '2px solid #3b82f6';
            row.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.3)';
            row.style.transform = 'translateY(-1px)';
        }}
        
        // 행 스타일 초기화
        function resetRowStyle(row) {{
            const isViolation = row.dataset.isViolation === 'true';
            
            if (isViolation) {{
                row.style.background = 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)';
                row.style.border = '2px solid transparent';
                row.style.boxShadow = '0 2px 4px rgba(239, 68, 68, 0.2)';
            }} else {{
                row.style.background = 'white';
                row.style.border = '2px solid transparent';
                row.style.boxShadow = 'none';
            }}
            row.style.transform = 'translateY(0)';
        }}
        
        // 키보드 네비게이션 (요구사항 3.4, 3.5)
        function handleKeyNavigation(event, currentIndex) {{
            if (!enhancedTableState.keyboardNavigationEnabled) return;
            
            const visibleRows = Array.from(document.querySelectorAll('#enhanced-table-body tr:not([style*="display: none"])'));
            const currentRowIndex = visibleRows.findIndex(row => 
                parseInt(row.dataset.rowIndex) === currentIndex
            );
            
            let targetRowIndex = currentRowIndex;
            
            switch(event.key) {{
                case 'ArrowDown':
                    event.preventDefault();
                    targetRowIndex = Math.min(currentRowIndex + 1, visibleRows.length - 1);
                    break;
                case 'ArrowUp':
                    event.preventDefault();
                    targetRowIndex = Math.max(currentRowIndex - 1, 0);
                    break;
                case 'Enter':
                case ' ':
                    event.preventDefault();
                    // 엔터나 스페이스로 상세 정보 토글
                    notifyStreamlit('toggle_detail_panel', {{ index: currentIndex }});
                    return;
                case 'Escape':
                    event.preventDefault();
                    // ESC로 선택 해제
                    const selectedRow = document.querySelector('.selected-row');
                    if (selectedRow) {{
                        selectedRow.classList.remove('selected-row');
                        resetRowStyle(selectedRow);
                        enhancedTableState.selectedRowIndex = null;
                    }}
                    return;
                default:
                    return;
            }}
            
            if (targetRowIndex !== currentRowIndex && visibleRows[targetRowIndex]) {{
                const targetRow = visibleRows[targetRowIndex];
                const newIndex = parseInt(targetRow.dataset.rowIndex);
                handleRowSelect(newIndex);
            }}
        }}
        
        // 실시간 검색 필터링 (요구사항 3.2)
        function applySearchFilter(searchTerm) {{
            const rows = document.querySelectorAll('#enhanced-table-body tr');
            const term = searchTerm.toLowerCase();
            let visibleCount = 0;
            
            enhancedTableState.filteredRows = [];
            
            rows.forEach((row, index) => {{
                const sampleName = row.dataset.sampleName.toLowerCase();
                const testItem = row.dataset.testItem.toLowerCase();
                const judgment = row.dataset.judgment.toLowerCase();
                
                const matches = sampleName.includes(term) || 
                              testItem.includes(term) || 
                              judgment.includes(term) ||
                              term === '';
                
                if (matches) {{
                    row.style.display = '';
                    row.classList.remove('filtered-out');
                    enhancedTableState.filteredRows.push(row);
                    visibleCount++;
                    
                    // 검색어 하이라이트
                    if (term && term.length > 0) {{
                        highlightSearchTerm(row, term);
                    }} else {{
                        removeHighlight(row);
                    }}
                }} else {{
                    row.style.display = 'none';
                    row.classList.add('filtered-out');
                    removeHighlight(row);
                }}
            }});
            
            // 검색 결과 통계 업데이트
            notifyStreamlit('search_results_updated', {{
                visible: visibleCount,
                total: rows.length,
                searchTerm: searchTerm
            }});
            
            console.log(`Search applied: "${{searchTerm}}" - ${{visibleCount}}/${{rows.length}} rows visible`);
        }}
        
        // 검색어 하이라이트
        function highlightSearchTerm(row, term) {{
            const cells = row.querySelectorAll('td');
            cells.forEach(cell => {{
                const originalText = cell.textContent;
                if (originalText.toLowerCase().includes(term)) {{
                    const regex = new RegExp(`(${{term}})`, 'gi');
                    const highlightedText = originalText.replace(regex, 
                        '<mark style="background: #fef08a; padding: 2px 4px; border-radius: 3px; font-weight: bold;">$1</mark>'
                    );
                    cell.innerHTML = highlightedText;
                }}
            }});
        }}
        
        // 하이라이트 제거
        function removeHighlight(row) {{
            const marks = row.querySelectorAll('mark');
            marks.forEach(mark => {{
                mark.outerHTML = mark.textContent;
            }});
        }}
        
        // 부적합 항목 강조 (요구사항 3.3)
        function emphasizeViolations() {{
            const violationRows = document.querySelectorAll('.violation-row');
            violationRows.forEach((row, index) => {{
                // 부적합 행에 펄스 애니메이션 적용
                setTimeout(() => {{
                    row.style.animation = 'violationEmphasis 1.5s ease-in-out';
                }}, index * 200);
            }});
        }}
        
        // 부적합 항목만 필터링
        function filterViolationsOnly(showOnly) {{
            const rows = document.querySelectorAll('#enhanced-table-body tr');
            let visibleCount = 0;
            
            rows.forEach(row => {{
                const isViolation = row.dataset.isViolation === 'true';
                
                if (showOnly) {{
                    if (isViolation) {{
                        row.style.display = '';
                        visibleCount++;
                    }} else {{
                        row.style.display = 'none';
                    }}
                }} else {{
                    row.style.display = '';
                    visibleCount++;
                }}
            }});
            
            notifyStreamlit('violation_filter_applied', {{
                showOnly: showOnly,
                visible: visibleCount,
                total: rows.length
            }});
        }}
        
        // Streamlit 통신
        function notifyStreamlit(eventType, data) {{
            if (window.parent) {{
                window.parent.postMessage({{
                    type: `enhanced_table_${{eventType}}`,
                    data: data,
                    timestamp: Date.now()
                }}, '*');
            }}
        }}
        
        // CSS 애니메이션 정의
        const enhancedStyles = document.createElement('style');
        enhancedStyles.textContent = `
            @keyframes selectedPulse {{
                0% {{ transform: translateY(-1px) scale(1); }}
                50% {{ transform: translateY(-2px) scale(1.02); }}
                100% {{ transform: translateY(-1px) scale(1); }}
            }}
            
            @keyframes violationEmphasis {{
                0%, 100% {{ 
                    border-left: 4px solid #ef4444; 
                    box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
                }}
                50% {{ 
                    border-left: 4px solid #f87171; 
                    box-shadow: 0 4px 8px rgba(239, 68, 68, 0.4);
                }}
            }}
            
            .violation-row {{
                position: relative;
            }}
            
            .violation-row::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 4px;
                background: linear-gradient(180deg, #ef4444 0%, #f87171 100%);
                border-radius: 0 2px 2px 0;
            }}
            
            .selected-row {{
                position: relative;
                z-index: 5;
            }}
            
            .filtered-out {{
                opacity: 0.3;
                transition: opacity 0.3s ease;
            }}
            
            #enhanced-table-body tr:focus {{
                outline: 2px solid #3b82f6;
                outline-offset: -2px;
            }}
            
            mark {{
                animation: highlightFade 2s ease-in-out;
            }}
            
            @keyframes highlightFade {{
                0% {{ background-color: #fef08a; }}
                100% {{ background-color: #fef3c7; }}
            }}
        `;
        document.head.appendChild(enhancedStyles);
        
        // 테이블 초기화
        function initializeEnhancedTable() {{
            // 부적합 항목 강조
            emphasizeViolations();
            
            // 초기 선택된 행이 있다면 스타일 적용
            if (enhancedTableState.selectedRowIndex !== null) {{
                const selectedRow = document.querySelector(`#enhanced-row-${{enhancedTableState.selectedRowIndex}}`);
                if (selectedRow) {{
                    selectedRow.classList.add('selected-row');
                    applySelectedStyle(selectedRow);
                }}
            }}
            
            // 키보드 이벤트 리스너 추가
            document.addEventListener('keydown', function(e) {{
                if (e.target.closest('#enhanced-interactive-table')) {{
                    // 테이블 내에서의 키보드 이벤트는 개별 행에서 처리
                    return;
                }}
                
                // 전역 키보드 단축키
                if (e.ctrlKey || e.metaKey) {{
                    switch(e.key) {{
                        case 'f':
                            e.preventDefault();
                            // 검색 입력 필드에 포커스
                            const searchInput = document.querySelector('input[placeholder*="검색"]');
                            if (searchInput) {{
                                searchInput.focus();
                            }}
                            break;
                        case 'v':
                            e.preventDefault();
                            // 부적합 항목만 토글
                            const currentFilter = document.querySelector('input[type="checkbox"][key*="violations"]');
                            if (currentFilter) {{
                                currentFilter.click();
                            }}
                            break;
                    }}
                }}
            }});
            
            console.log('Enhanced interactive table initialized successfully');
            
            // 초기화 완료 알림
            notifyStreamlit('table_initialized', {{
                rowCount: document.querySelectorAll('#enhanced-table-body tr').length,
                violationCount: document.querySelectorAll('.violation-row').length
            }});
        }}
        
        // DOM 로드 완료 시 초기화
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initializeEnhancedTable);
        }} else {{
            initializeEnhancedTable();
        }}
        
        // 외부에서 호출 가능한 함수들 노출
        window.enhancedTableAPI = {{
            selectRow: handleRowSelect,
            sortTable: handleSort,
            filterSearch: applySearchFilter,
            filterViolations: filterViolationsOnly,
            emphasizeViolations: emphasizeViolations,
            getState: () => enhancedTableState
        }};
        </script>
        """
        
        return table_html + enhanced_javascript
    
    def _handle_javascript_events(self, data: List[Dict[str, Any]], 
                                on_row_select: Optional[Callable] = None) -> None:
        """JavaScript 이벤트 처리"""
        # 실제 구현에서는 Streamlit의 components.html과 
        # 메시지 패싱을 통해 JavaScript 이벤트를 처리해야 함
        # 여기서는 기본적인 행 선택 처리만 구현
        
        if data and on_row_select:
            selected_index = st.session_state.interactive_table.get('selected_row_index')
            if selected_index is not None and 0 <= selected_index < len(data):
                original_data = data[selected_index]['original_data']
                on_row_select(original_data)

    def prepare_table_data(self, data: List[TestResult]) -> List[Dict[str, Any]]:
        """테이블 표시용 데이터 준비 (public 메서드)"""
        return self._prepare_table_data(data)
    
    def filter_data(self, data: List[Dict[str, Any]], search_term: str = "") -> List[Dict[str, Any]]:
        """데이터 필터링 (public 메서드)"""
        # 검색어를 세션 상태에 설정
        if search_term:
            st.session_state.interactive_table['search_term'] = search_term
        return self._apply_search_filter(data)

    def render_complete_table(self, data: List[TestResult], 
                            on_row_select: Optional[Callable] = None) -> None:
        """
        완전한 인터랙티브 테이블 렌더링
        검색, 정렬, 선택 기능 모두 포함
        """
        # 향상된 인터랙티브 테이블 렌더링
        self.render_enhanced_table_with_interactions(data, on_row_select)
        
        st.markdown("---")
        
        # 테이블 요약 정보
        self.render_table_summary()


# 테스트 함수
def test_interactive_data_table():
    """인터랙티브 데이터 테이블 테스트"""
    from datetime import datetime
    
    # 샘플 데이터 생성
    sample_results = [
        TestResult(
            no=1, sample_name='냉수탱크', analysis_number='25A00009-001',
            test_item='아크릴로나이트릴', test_unit='mg/L', result_report='불검출',
            tester_input_value=0, standard_excess='적합', tester='김화빈',
            test_standard='EPA 524.2', standard_criteria='0.0006 mg/L 이하',
            text_digits='', processing_method='반올림', result_display_digits=4,
            result_type='수치형', tester_group='유기(ALL)',
            input_datetime=datetime(2025, 1, 23, 9, 56), approval_request='Y',
            approval_request_datetime=datetime(2025, 1, 23, 13, 45),
            test_result_display_limit=0.0002, quantitative_limit_processing='불검출',
            test_equipment='', judgment_status='N', report_output='Y',
            kolas_status='N', test_lab_group='유기_용출_Acrylonitrile', test_set='Set 1'
        ),
        TestResult(
            no=2, sample_name='온수탱크', analysis_number='25A00009-002',
            test_item='아크릴로나이트릴', test_unit='mg/L', result_report='0.0007',
            tester_input_value=0.0007, standard_excess='부적합', tester='김화빈',
            test_standard='EPA 524.2', standard_criteria='0.0006 mg/L 이하',
            text_digits='', processing_method='반올림', result_display_digits=4,
            result_type='수치형', tester_group='유기(ALL)',
            input_datetime=datetime(2025, 1, 23, 9, 56), approval_request='Y',
            approval_request_datetime=datetime(2025, 1, 23, 13, 45),
            test_result_display_limit=0.0002, quantitative_limit_processing='불검출',
            test_equipment='', judgment_status='N', report_output='Y',
            kolas_status='N', test_lab_group='유기_용출_Acrylonitrile', test_set='Set 1'
        )
    ]
    
    # 테이블 테스트
    table = InteractiveDataTable(height=400)
    
    def on_row_select(selected_row):
        print(f"선택된 행: {selected_row.sample_name} - {selected_row.test_item}")
    
    # 완전한 테이블 렌더링
    table.render_complete_table(sample_results, on_row_select)
    
    return table


if __name__ == "__main__":
    # Streamlit 앱에서 테스트
    st.title("인터랙티브 데이터 테이블 테스트")
    test_interactive_data_table()