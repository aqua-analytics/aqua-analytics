@echo off
chcp 65001 >nul

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██              🧪 Aqua-Analytics Premium                    ██
echo ██                   빠른 시작                               ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.

:: 가상환경 확인
if not exist "aqua_env" (
    echo ❌ 가상환경이 설정되지 않았습니다.
    echo.
    echo 처음 실행이시라면 'install_and_run.bat'을 실행해주세요.
    echo.
    pause
    exit /b 1
)

echo ✅ 가상환경 활성화 중...
call aqua_env\Scripts\activate.bat

echo.
echo 🌐 서버 접속 정보:
echo ────────────────────────────────────────────────────────────────
echo   로컬 접속: http://localhost:8501

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set IP=%%b
        set IP=!IP: =!
        if not "!IP!"=="" (
            echo   사내 네트워크 접속: http://!IP!:8501
        )
    )
)
echo ────────────────────────────────────────────────────────────────
echo.

echo 🚀 Aqua-Analytics 서버 시작 중...
echo.
echo ⚠️  서버를 중지하려면 Ctrl+C를 누르세요.
echo.

streamlit run aqua_analytics_premium.py --server.address 0.0.0.0 --server.port 8501 --server.headless true

echo.
echo 서버가 종료되었습니다.
pause