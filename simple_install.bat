@echo off
chcp 65001 >nul
echo.
echo ████████████████████████████████████████████████████████████████
echo ██        🧪 Aqua-Analytics Premium 간단 설치                 ██
echo ████████████████████████████████████████████████████████████████
echo.

:: 필수 파일 확인
if not exist "aqua_analytics_premium.py" (
    echo ❌ aqua_analytics_premium.py 파일이 없습니다.
    echo GitHub에서 전체 프로젝트를 다운로드했는지 확인해주세요.
    pause
    exit /b 1
)

:: Python 확인
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다.
    echo.
    echo Python 설치 방법:
    echo 1. https://python.org 접속
    echo 2. Python 3.11.7 다운로드
    echo 3. 설치 시 "Add Python to PATH" 반드시 체크
    echo 4. 설치 완료 후 컴퓨터 재부팅
    echo 5. 이 스크립트 다시 실행
    echo.
    pause
    exit /b 1
)

echo ✅ Python 확인 완료

:: 가상환경 생성
echo.
echo 가상환경 생성 중...
python -m venv aqua_env
call aqua_env\Scripts\activate.bat

:: 패키지 설치
echo.
echo 패키지 설치 중... (인터넷 연결 필요)
pip install --upgrade pip
pip install streamlit pandas plotly openpyxl python-dateutil psutil

:: 폴더 생성
echo.
echo 폴더 구조 생성 중...
mkdir aqua_analytics_data\uploads 2>nul
mkdir aqua_analytics_data\processed 2>nul
mkdir aqua_analytics_data\database 2>nul
mkdir aqua_analytics_data\reports\dashboard 2>nul
mkdir aqua_analytics_data\reports\integrated 2>nul

echo.
echo ✅ 설치 완료!
echo.
echo 🚀 서버 시작 중...
echo 브라우저에서 http://localhost:8501 접속하세요.
echo.

start http://localhost:8501
streamlit run aqua_analytics_premium.py --server.address 0.0.0.0 --server.port 8501

pause