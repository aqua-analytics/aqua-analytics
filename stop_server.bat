@echo off
echo ====================================
echo  Aqua-Analytics 서버 중지
echo ====================================

echo.
echo Streamlit 프로세스 종료 중...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Streamlit*" 2>nul
taskkill /f /im streamlit.exe 2>nul

echo.
echo 포트 8501 사용 프로세스 확인 중...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501') do (
    echo 프로세스 ID %%a 종료 중...
    taskkill /f /pid %%a 2>nul
)

echo.
echo 서버가 중지되었습니다.
pause