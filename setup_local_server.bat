@echo off
echo ====================================
echo  Aqua-Analytics 로컬 서버 설치
echo ====================================

echo.
echo [1/5] Python 설치 확인 중...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python이 설치되지 않았습니다.
    echo https://python.org 에서 Python 3.9 이상을 설치하세요.
    pause
    exit /b 1
)

echo.
echo [2/5] 가상환경 생성 중...
python -m venv aqua_env
call aqua_env\Scripts\activate.bat

echo.
echo [3/5] 필요한 패키지 설치 중...
pip install -r requirements.txt

echo.
echo [4/5] 폴더 구조 생성 중...
mkdir aqua_analytics_data\uploads 2>nul
mkdir aqua_analytics_data\processed 2>nul
mkdir aqua_analytics_data\database 2>nul
mkdir aqua_analytics_data\reports\dashboard 2>nul
mkdir aqua_analytics_data\reports\integrated 2>nul
mkdir aqua_analytics_data\standards 2>nul
mkdir aqua_analytics_data\templates 2>nul

echo.
echo [5/5] 설치 완료!
echo.
echo ====================================
echo  설치가 완료되었습니다!
echo ====================================
echo.
echo 서버 시작: start_server.bat 실행
echo 서버 중지: Ctrl+C
echo.
pause