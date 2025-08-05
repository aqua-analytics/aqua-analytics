@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██           🚀 GitHub 데모 버전 배포 스크립트                ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.

echo [1/8] Git 설치 확인 중...
git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Git이 설치되지 않았습니다.
    echo https://git-scm.com 에서 Git을 설치해주세요.
    pause
    exit /b 1
)
echo ✅ Git 설치 확인 완료

echo.
echo [2/8] GitHub 데모용 파일 준비 중...

:: README 파일 교체
if exist "README.md" (
    ren "README.md" "README_LOCAL.md"
)
copy "README_GITHUB.md" "README.md" >nul

:: requirements 파일 교체
if exist "requirements.txt" (
    ren "requirements.txt" "requirements_local.txt"
)
copy "requirements_demo.txt" "requirements.txt" >nul

:: .gitignore 파일 교체
if exist ".gitignore" (
    ren ".gitignore" ".gitignore_local"
)
copy ".gitignore_github" ".gitignore" >nul

:: 데모용 메인 파일 복사
copy "aqua_analytics_demo.py" "app.py" >nul

echo ✅ 데모용 파일 준비 완료

echo.
echo [3/8] Git 저장소 초기화 중...
if not exist ".git" (
    git init
    echo ✅ Git 저장소 초기화 완료
) else (
    echo ✅ Git 저장소가 이미 존재합니다
)

echo.
echo [4/8] GitHub 원격 저장소 설정 중...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/aqua-analytics/aqua-analytics.git
echo ✅ 원격 저장소 설정 완료

echo.
echo [5/8] 파일 스테이징 중...
git add .
echo ✅ 파일 스테이징 완료

echo.
echo [6/8] 커밋 생성 중...
git commit -m "🚀 Initial commit: Aqua-Analytics Premium Demo Version

✨ Features:
- Interactive dashboard for environmental data analysis
- Real-time data visualization with Plotly
- AI-powered insights and recommendations
- Automated report generation
- Multi-format data support (Excel, CSV, JSON)

🌐 Demo Version:
- Optimized for Streamlit Cloud deployment
- Session-based temporary storage
- Minimal dependencies for fast loading

🏢 Local Server Version:
- Full-featured version available for local deployment
- Persistent data storage
- Network access for team collaboration

📧 Contact: iot.ideashare@gmail.com"

if %errorLevel% neq 0 (
    echo ❌ 커밋 생성 실패
    pause
    exit /b 1
)
echo ✅ 커밋 생성 완료

echo.
echo [7/8] GitHub에 푸시 중...
echo.
echo ⚠️  GitHub 로그인이 필요합니다.
echo    사용자명: iot.ideashare@gmail.com
echo    비밀번호: Personal Access Token 입력
echo.

git push -u origin main

if %errorLevel% neq 0 (
    echo.
    echo ❌ 푸시 실패. 다시 시도합니다...
    echo.
    echo 📝 GitHub Personal Access Token이 필요합니다:
    echo    1. GitHub.com → Settings → Developer settings
    echo    2. Personal access tokens → Tokens (classic)
    echo    3. Generate new token (classic)
    echo    4. repo 권한 체크 후 생성
    echo    5. 생성된 토큰을 비밀번호로 사용
    echo.
    
    git push -u origin main
    
    if %errorLevel% neq 0 (
        echo ❌ 푸시 최종 실패
        echo 수동으로 GitHub에 푸시해주세요.
        pause
        exit /b 1
    )
)

echo ✅ GitHub 푸시 완료

echo.
echo [8/8] Streamlit Cloud 배포 안내...
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                    🎉 배포 완료! 🎉                        ██
echo ████████████████████████████████████████████████████████████████
echo.

echo 🌐 다음 단계:
echo ────────────────────────────────────────────────────────────────
echo 1. https://share.streamlit.io 접속
echo 2. GitHub 계정으로 로그인 (iot.ideashare@gmail.com)
echo 3. "New app" 클릭
echo 4. Repository: aqua-analytics/aqua-analytics
echo 5. Branch: main
echo 6. Main file path: app.py
echo 7. "Deploy!" 클릭
echo.
echo 🚀 배포 후 URL: https://aqua-analytics.streamlit.app
echo ────────────────────────────────────────────────────────────────
echo.

echo 📋 로컬 파일 복원 중...
:: 원본 파일들 복원
if exist "README_LOCAL.md" (
    del "README.md"
    ren "README_LOCAL.md" "README.md"
)

if exist "requirements_local.txt" (
    del "requirements.txt"
    ren "requirements_local.txt" "requirements.txt"
)

if exist ".gitignore_local" (
    del ".gitignore"
    ren ".gitignore_local" ".gitignore"
)

del "app.py" >nul 2>&1

echo ✅ 로컬 파일 복원 완료
echo.
echo 🏠 로컬 서버는 install_and_run.bat으로 실행하세요!
echo.
pause