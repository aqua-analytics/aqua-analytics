@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██           🧪 Aqua-Analytics Premium 설치 및 실행           ██
echo ██                환경 데이터 인사이트 플랫폼                 ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.

:: 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  관리자 권한이 필요합니다. 관리자로 다시 실행해주세요.
    echo.
    echo 방법: 우클릭 → "관리자 권한으로 실행"
    echo.
    pause
    exit /b 1
)

echo ✅ 관리자 권한 확인 완료
echo.

:: Python 설치 확인
echo [1/6] Python 설치 상태 확인 중...
python --version >nul 2>&1
if %errorLevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python !PYTHON_VERSION! 이미 설치됨
    goto :install_packages
)

echo ❌ Python이 설치되지 않았습니다.
echo.

:: Python 다운로드 및 설치
echo [2/6] Python 3.11.7 다운로드 중...
set PYTHON_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe
set PYTHON_INSTALLER=python-installer.exe

echo 다운로드 URL: %PYTHON_URL%
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'}"

if not exist "%PYTHON_INSTALLER%" (
    echo ❌ Python 다운로드 실패
    echo 수동으로 https://python.org 에서 Python을 설치해주세요.
    pause
    exit /b 1
)

echo ✅ Python 다운로드 완료
echo.

echo [3/6] Python 설치 중... (잠시만 기다려주세요)
echo 설치 옵션: PATH 추가, pip 포함, 모든 사용자용 설치
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: 설치 완료 대기
timeout /t 30 /nobreak >nul

:: PATH 새로고침
call refreshenv >nul 2>&1

:: Python 설치 확인
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python 설치 실패
    echo 시스템을 재부팅 후 다시 시도해주세요.
    pause
    exit /b 1
)

echo ✅ Python 설치 완료
del "%PYTHON_INSTALLER%" >nul 2>&1

:install_packages
echo.
echo [4/6] 가상환경 생성 중...
if exist "aqua_env" (
    echo ✅ 가상환경이 이미 존재합니다.
) else (
    python -m venv aqua_env
    if %errorLevel% neq 0 (
        echo ❌ 가상환경 생성 실패
        pause
        exit /b 1
    )
    echo ✅ 가상환경 생성 완료
)

echo.
echo [5/6] 가상환경 활성화 및 패키지 설치 중...
call aqua_env\Scripts\activate.bat

echo pip 업그레이드 중...
python -m pip install --upgrade pip --quiet

echo 필수 패키지 설치 중...
pip install -r requirements.txt --quiet

if %errorLevel% neq 0 (
    echo ❌ 패키지 설치 실패
    echo.
    echo 수동 설치를 시도합니다...
    pip install streamlit pandas plotly openpyxl python-dateutil
)

echo ✅ 패키지 설치 완료

echo.
echo [6/6] 폴더 구조 생성 중...
mkdir aqua_analytics_data\uploads 2>nul
mkdir aqua_analytics_data\processed 2>nul
mkdir aqua_analytics_data\database 2>nul
mkdir aqua_analytics_data\reports\dashboard 2>nul
mkdir aqua_analytics_data\reports\integrated 2>nul
mkdir aqua_analytics_data\standards 2>nul
mkdir aqua_analytics_data\templates 2>nul

echo ✅ 폴더 구조 생성 완료

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                    🎉 설치 완료! 🎉                        ██
echo ████████████████████████████████████████████████████████████████
echo.

:: 네트워크 정보 표시
echo 🌐 서버 접속 정보:
echo ────────────────────────────────────────────────────────────────
echo   로컬 접속: http://localhost:8501
echo   컴퓨터명 접속: http://%COMPUTERNAME%:8501

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

echo 🚀 Aqua-Analytics 서버를 시작합니다...
echo.
echo ⚠️  서버를 중지하려면 Ctrl+C를 누르세요.
echo.

:: Streamlit 실행
streamlit run aqua_analytics_premium.py --server.address 0.0.0.0 --server.port 8501 --server.headless true

echo.
echo 서버가 종료되었습니다.
pause