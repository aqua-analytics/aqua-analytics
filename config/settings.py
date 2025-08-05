"""
시스템 설정 파일
System Configuration Settings
"""

import os
from pathlib import Path

# 기본 경로 설정
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
UPLOADS_DIR = BASE_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "reports"

# 폴더 생성
for directory in [DATA_DIR, TEMPLATES_DIR, UPLOADS_DIR, REPORTS_DIR]:
    directory.mkdir(exist_ok=True)

# 파일 설정
MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = ['.xlsx', '.xls']
AUTO_DELETE_HOURS = 24

# 데이터베이스 설정 (향후 확장용)
DATABASE_CONFIG = {
    'type': 'sqlite',
    'path': DATA_DIR / 'lab_analysis.db'
}

# 시각화 설정
CHART_CONFIG = {
    'theme': 'plotly_white',
    'color_palette': {
        'primary': '#2563eb',
        'success': '#16a34a', 
        'warning': '#eab308',
        'danger': '#ef4444',
        'background': '#f1f5f9'
    }
}

# 감시 폴더 설정
WATCH_FOLDERS = {
    'pending': UPLOADS_DIR / 'pending',
    'standards': DATA_DIR / 'standards',
    'processed': DATA_DIR / 'processed'
}

# 감시 폴더 생성
for folder in WATCH_FOLDERS.values():
    folder.mkdir(parents=True, exist_ok=True)

# Streamlit 설정
STREAMLIT_CONFIG = {
    'page_title': '실험실 품질관리 대시보드',
    'page_icon': '🧪',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}