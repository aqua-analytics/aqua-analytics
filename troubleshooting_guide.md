# 🛠️ Aqua-Analytics Premium 문제 해결 가이드

## 🚨 일반적인 오류 및 해결 방법

### 1. "Python이 설치되지 않았습니다" 오류

#### 증상
```
❌ Python이 설치되지 않았습니다.
'python'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```

#### 해결 방법
1. **Python 수동 설치**
   - https://python.org 접속
   - "Download Python 3.11.7" 클릭
   - 다운로드된 파일 실행
   - **중요**: "Add Python to PATH" 체크박스 반드시 선택
   - 설치 완료 후 컴퓨터 재부팅

2. **PATH 환경변수 수동 설정**
   ```
   제어판 → 시스템 → 고급 시스템 설정 → 환경 변수
   시스템 변수에서 Path 선택 → 편집
   다음 경로 추가:
   C:\Program Files\Python311
   C:\Program Files\Python311\Scripts
   ```

### 2. "관리자 권한이 필요합니다" 오류

#### 해결 방법
1. **관리자 권한으로 실행**
   - `install_and_run_fixed.bat` 파일 우클릭
   - "관리자 권한으로 실행" 선택

2. **또는 일반 사용자로 실행**
   - `simple_install.bat` 사용 (Python이 이미 설치된 경우)

### 3. "파일이 없습니다" 오류

#### 증상
```
❌ 오류: aqua_analytics_premium.py 파일이 없습니다.
❌ 오류: requirements.txt 파일이 없습니다.
```

#### 해결 방법
1. **전체 프로젝트 다운로드 확인**
   - GitHub에서 "Code" → "Download ZIP" 클릭
   - ZIP 파일을 완전히 압축 해제
   - 모든 파일이 있는지 확인

2. **올바른 폴더에서 실행**
   - `aqua_analytics_premium.py` 파일이 있는 폴더에서 실행
   - 명령 프롬프트에서 `dir` 명령으로 파일 확인

### 4. "패키지 설치 실패" 오류

#### 증상
```
❌ 패키지 설치 실패
ERROR: Could not install packages due to an EnvironmentError
```

#### 해결 방법
1. **인터넷 연결 확인**
   - 안정적인 인터넷 연결 필요
   - 방화벽/보안 프로그램 확인

2. **pip 업그레이드**
   ```cmd
   python -m pip install --upgrade pip
   ```

3. **개별 패키지 설치**
   ```cmd
   pip install streamlit
   pip install pandas
   pip install plotly
   pip install openpyxl
   pip install python-dateutil
   pip install psutil
   ```

### 5. "포트 사용 중" 오류

#### 증상
```
Port 8501 is already in use
```

#### 해결 방법
1. **다른 Streamlit 프로세스 종료**
   ```cmd
   taskkill /f /im streamlit.exe
   ```

2. **포트 사용 프로세스 확인 및 종료**
   ```cmd
   netstat -ano | findstr :8501
   taskkill /PID [PID번호] /F
   ```

### 6. "가상환경 생성 실패" 오류

#### 해결 방법
1. **기존 가상환경 삭제 후 재생성**
   ```cmd
   rmdir /s aqua_env
   python -m venv aqua_env
   ```

2. **디스크 공간 확인**
   - 최소 2GB 이상의 여유 공간 필요

### 7. "브라우저에서 접속 안됨" 오류

#### 해결 방법
1. **방화벽 설정**
   ```cmd
   netsh advfirewall firewall add rule name="Aqua-Analytics" dir=in action=allow protocol=TCP localport=8501
   ```

2. **수동 브라우저 접속**
   - 브라우저에서 직접 입력: `http://localhost:8501`

3. **다른 포트 사용**
   ```cmd
   streamlit run aqua_analytics_premium.py --server.port 8502
   ```

## 🔧 고급 문제 해결

### PowerShell 실행 정책 오류

#### 증상
```
PowerShell 스크립트 실행이 비활성화되어 있습니다.
```

#### 해결 방법
```powershell
# 관리자 권한 PowerShell에서 실행
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows Defender 차단

#### 해결 방법
1. Windows Defender 설정 열기
2. 바이러스 및 위협 방지 → 설정 관리
3. 실시간 보호 일시 비활성화
4. 설치 완료 후 다시 활성화

### 네트워크 프록시 문제

#### 해결 방법
```cmd
# 프록시 설정이 있는 경우
pip install --proxy http://proxy.company.com:8080 streamlit
```

## 📋 단계별 완전 수동 설치

모든 자동 설치가 실패하는 경우:

### 1단계: Python 설치
1. https://python.org 접속
2. Python 3.11.7 다운로드
3. 설치 시 "Add Python to PATH" 체크
4. 컴퓨터 재부팅

### 2단계: 프로젝트 다운로드
1. https://github.com/aqua-analytics/aqua-analytics
2. "Code" → "Download ZIP"
3. 압축 해제

### 3단계: 명령 프롬프트에서 실행
```cmd
cd C:\path\to\aqua-analytics
python -m venv aqua_env
aqua_env\Scripts\activate.bat
pip install --upgrade pip
pip install streamlit pandas plotly openpyxl python-dateutil psutil
mkdir aqua_analytics_data\uploads
mkdir aqua_analytics_data\processed
mkdir aqua_analytics_data\database
streamlit run aqua_analytics_premium.py --server.address 0.0.0.0 --server.port 8501
```

## 🆘 최종 해결책

위의 모든 방법이 실패하는 경우:

### 방법 1: 온라인 데모 사용
- https://aqua-analytics.streamlit.app
- 로컬 설치와 동일한 기능 제공

### 방법 2: Docker 사용 (고급 사용자)
```cmd
docker run -p 8501:8501 aqua-analytics
```

### 방법 3: 기술 지원 요청
- 이메일: iot.ideashare@gmail.com
- GitHub Issues: https://github.com/aqua-analytics/aqua-analytics/issues

## 📞 추가 도움

### 시스템 정보 수집
문제 해결을 위해 다음 정보를 수집해주세요:

```cmd
# 시스템 정보
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# Python 정보
python --version
pip --version

# 네트워크 정보
ipconfig
netstat -an | findstr :8501

# 오류 메시지 전체 복사
```

이 정보와 함께 문의하시면 더 정확한 해결책을 제공할 수 있습니다.

---

**🌊 문제가 해결되지 않으면 언제든 문의하세요!**