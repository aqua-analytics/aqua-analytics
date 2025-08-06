@echo off
echo ====================================
echo  Aqua-Analytics 로컬 서버 시작
echo ====================================

echo.
echo 가상환경 활성화 중...
call aqua_env\Scripts\activate.bat

echo.
echo 서버 시작 중...
echo.
echo ====================================
echo  서버 접속 정보
echo ====================================
echo  로컬 접속: http://localhost:8501
echo  사내 접속: http://%COMPUTERNAME%:8501
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        echo  IP 접속: http://%%b:8501
    )
)
echo ====================================
echo.
echo 서버를 중지하려면 Ctrl+C를 누르세요.
echo.

streamlit run aqua_analytics_premium.py --server.address 0.0.0.0 --server.port 8501