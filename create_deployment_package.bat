@echo off
echo ====================================
echo  Aqua-Analytics 배포 패키지 생성
echo ====================================

echo.
echo [1/4] 배포 폴더 생성 중...
mkdir aqua-analytics-local-server 2>nul
mkdir aqua-analytics-local-server\docs 2>nul

echo.
echo [2/4] 필수 파일 복사 중...
copy aqua_analytics_premium.py aqua-analytics-local-server\
copy requirements.txt aqua-analytics-local-server\
copy setup_local_server.bat aqua-analytics-local-server\
copy start_server.bat aqua-analytics-local-server\
copy stop_server.bat aqua-analytics-local-server\
copy README.md aqua-analytics-local-server\

echo.
echo [3/4] 폴더 구조 복사 중...
xcopy /E /I src aqua-analytics-local-server\src
xcopy /E /I .streamlit aqua-analytics-local-server\.streamlit
xcopy /E /I sample_data aqua-analytics-local-server\sample_data
xcopy /E /I docs\LOCAL_SERVER_SETUP.md aqua-analytics-local-server\docs\

echo.
echo [4/4] 압축 파일 생성 중...
powershell Compress-Archive -Path "aqua-analytics-local-server" -DestinationPath "aqua-analytics-local-server.zip" -Force

echo.
echo ====================================
echo  배포 패키지 생성 완료!
echo ====================================
echo.
echo 생성된 파일: aqua-analytics-local-server.zip
echo.
echo 사용법:
echo 1. ZIP 파일을 서버 PC에 압축 해제
echo 2. setup_local_server.bat 실행
echo 3. start_server.bat 실행
echo 4. 사내 네트워크에서 접속
echo.
pause