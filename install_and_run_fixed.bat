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

:: 현재 디렉토리 확인
echo 📁 현재 작업 디렉토리: %CD%
echo.

:: 필수 파일 존재 확인
if not exist "aqua_analytics_premium.py" (
    echo ❌ 오류: aqua_analytics_premium.py 파일이 없습니다.
    echo.
    echo 해결 방법:
    echo 1. GitHub에서 전체 프로젝트를 다운로드했는지 확인
    echo 2. ZIP 파일을 완전히 압축 해제했는지 확인
    echo 3. 올바른 폴더에서 실행하고 있는지 확인
    echo.
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ 오류: requirements.txt 파일이 없습니다.
    echo.
    echo 해결 방법:
    echo 1. GitHub에서 전체 프로젝트를 다운로드했는지 확인
    echo 2. ZIP 파일을 완전히 압축 해제했는지 확인
    echo.
    pause
    exit /b 1
)

echo ✅ 필수 파일 확인 완료
echo.

:: 관리자 권한 확인 (선택적)
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  관리자 권한이 없습니다.
    echo.
    echo 권장사항: 관리자 권한으로 실행하면 더 안정적입니다.
    echo 방법: 우클릭 → "관리자 권한으로 실행"
    echo.
    echo 계속 진행하시겠습니까? (Y/N)
    set /p continue=
    if /i "!continue!" neq "Y" (
        echo 설치를 취소합니다.
        pause
        exit /b 1
    )
    echo.
)

:: Python 설치 확인
echo [1/7] Python 설치 상태 확인 중...
python --version >nul 2>&1
if %errorLevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python !PYTHON_VERSION! 이미 설치됨
    goto :check_pip
)

echo ❌ Python이 설치되지 않았습니다.
echo.

:: PowerShell 사용 가능 확인
powershell -Command "Write-Host 'PowerShell 테스트'" >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ PowerShell을 사용할 수 없습니다.
    echo.
    echo 수동 설치 방법:
    echo 1. https://python.org 접속
    echo 2. Python 3.11.7 다운로드
    echo 3. 설치 시 "Add Python to PATH" 체크
    echo 4. 설치 완료 후 이 스크립트 다시 실행
    echo.
    pause
    exit /b 1
)

:: Python 다운로드 및 설치
echo [2/7] Python 3.11.7 다운로드 중...
set PYTHON_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe
set PYTHON_INSTALLER=python-installer.exe

echo 다운로드 중... (시간이 걸릴 수 있습니다)
powershell -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' -UseBasicParsing; Write-Host 'Download completed' } catch { Write-Host 'Download failed:' $_.Exception.Message; exit 1 }"

if %errorLevel% neq 0 (
    echo ❌ Python 다운로드 실패
    echo.
    echo 수동 설치 방법:
    echo 1. https://python.org 접속
    echo 2. Python 3.11.7 다운로드
    echo 3. 설치 시 "Add Python to PATH" 체크
    echo 4. 설치 완료 후 이 스크립트 다시 실행
    echo.
    pause
    exit /b 1
)

if not exist "%PYTHON_INSTALLER%" (
    echo ❌ Python 설치 파일이 생성되지 않았습니다.
    echo.
    echo 수동 설치를 진행해주세요:
    echo https://python.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python 다운로드 완료 (파일 크기: 
for %%A in ("%PYTHON_INSTALLER%") do echo %%~zA bytes)
echo.

echo [3/7] Python 설치 중... (2-3분 소요)
echo 설치 옵션: PATH 추가, pip 포함, 모든 사용자용 설치
echo.
echo 설치 중... 잠시만 기다려주세요.

"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1

:: 설치 완료 대기 (더 긴 시간)
echo 설치 완료 대기 중... (60초)
timeout /t 60 /nobreak >nul

:: 환경 변수 새로고침 시도
echo 환경 변수 새로고침 중...
set PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts
set PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts

:: Python 설치 확인 (여러 번 시도)
echo Python 설치 확인 중...
for /L %%i in (1,1,5) do (
    python --version >nul 2>&1
    if !errorLevel! equ 0 (
        echo ✅ Python 설치 확인 완료
        goto :python_installed
    )
    echo 재시도 %%i/5...
    timeout /t 5 /nobreak >nul
)

echo ❌ Python 설치 실패 또는 PATH 설정 문제
echo.
echo 해결 방법:
echo 1. 컴퓨터를 재부팅해주세요
echo 2. 재부팅 후 이 스크립트를 다시 실행해주세요
echo 3. 또는 수동으로 Python을 설치해주세요: https://python.org
echo.
pause
exit /b 1

:python_installed
echo ✅ Python 설치 완료
del "%PYTHON_INSTALLER%" >nul 2>&1

:check_pip
echo.
echo [4/7] pip 확인 중...
python -m pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ pip이 설치되지 않았습니다.
    echo Python 재설치가 필요할 수 있습니다.
    pause
    exit /b 1
)
echo ✅ pip 확인 완료

echo.
echo [5/7] 가상환경 생성 중...
if exist "aqua_env" (
    echo ✅ 가상환경이 이미 존재합니다.
) else (
    echo 가상환경 생성 중...
    python -m venv aqua_env
    if %errorLevel% neq 0 (
        echo ❌ 가상환경 생성 실패
        echo.
        echo 가능한 원인:
        echo 1. Python 설치가 완전하지 않음
        echo 2. 디스크 공간 부족
        echo 3. 권한 문제
        echo.
        pause
        exit /b 1
    )
    echo ✅ 가상환경 생성 완료
)

echo.
echo [6/7] 가상환경 활성화 및 패키지 설치 중...

:: 가상환경 활성화 스크립트 확인
if not exist "aqua_env\Scripts\activate.bat" (
    echo ❌ 가상환경 활성화 스크립트가 없습니다.
    echo 가상환경을 다시 생성합니다...
    rmdir /s /q aqua_env >nul 2>&1
    python -m venv aqua_env
    if %errorLevel% neq 0 (
        echo ❌ 가상환경 재생성 실패
        pause
        exit /b 1
    )
)

echo 가상환경 활성화 중...
call aqua_env\Scripts\activate.bat

echo pip 업그레이드 중...
python -m pip install --upgrade pip
if %errorLevel% neq 0 (
    echo ⚠️ pip 업그레이드 실패 (계속 진행)
)

echo.
echo 필수 패키지 설치 중... (시간이 걸릴 수 있습니다)
echo.

:: requirements.txt가 있으면 사용, 없으면 개별 설치
if exist "requirements.txt" (
    echo requirements.txt에서 패키지 설치 중...
    pip install -r requirements.txt
    if %errorLevel% neq 0 (
        echo ⚠️ requirements.txt 설치 실패, 개별 설치를 시도합니다...
        goto :manual_install
    )
) else (
    :manual_install
    echo 개별 패키지 설치 중...
    pip install streamlit>=1.28.0
    pip install pandas>=2.0.0
    pip install plotly>=5.15.0
    pip install openpyxl>=3.1.0
    pip install python-dateutil>=2.8.2
    pip install psutil>=5.9.0
)

echo ✅ 패키지 설치 완료

echo.
echo [7/7] 폴더 구조 생성 중...
mkdir aqua_analytics_data 2>nul
mkdir aqua_analytics_data\uploads 2>nul
mkdir aqua_analytics_data\processed 2>nul
mkdir aqua_analytics_data\database 2>nul
mkdir aqua_analytics_data\reports 2>nul
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

:: IP 주소 확인 (더 안정적인 방법)
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4" ^| findstr /v "127.0.0.1"') do (
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
echo ⚠️  브라우저가 자동으로 열리지 않으면 위 주소를 직접 입력하세요.
echo.

:: 브라우저 자동 열기 (선택적)
timeout /t 3 /nobreak >nul
start http://localhost:8501

:: Streamlit 실행
streamlit run aqua_analytics_premium.py --server.address 0.0.0.0 --server.port 8501

echo.
echo 서버가 종료되었습니다.
echo.
echo 다시 시작하려면 quick_start.bat을 실행하세요.
pause