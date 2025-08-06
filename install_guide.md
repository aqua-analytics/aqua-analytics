# 🧪 Aqua-Analytics Premium 설치 가이드

## 📋 개요

이 가이드는 **Aqua-Analytics Premium**을 다른 PC에 설치하여 사내 네트워크에서 사용할 수 있도록 하는 상세한 설치 방법을 제공합니다.

현재 http://localhost:8501 에서 보시는 **완전히 동일한 기능**을 다른 PC에서도 사용할 수 있습니다.

---

## 🎯 설치 방법 선택

### 방법 1: 자동 설치 (권장) ⭐
- **대상**: 처음 설치하는 경우
- **특징**: Python 자동 설치, 원클릭 설정
- **소요 시간**: 5-10분

### 방법 2: 배포 패키지 설치
- **대상**: 여러 PC에 배포하는 경우
- **특징**: ZIP 파일로 간편 배포
- **소요 시간**: 3-5분

### 방법 3: 수동 설치
- **대상**: 개발자 또는 고급 사용자
- **특징**: 단계별 수동 설정
- **소요 시간**: 10-15분

---

## 🚀 방법 1: 자동 설치 (권장)

### 1단계: 파일 다운로드
1. GitHub 저장소 접속: https://github.com/aqua-analytics/aqua-analytics
2. **Code** → **Download ZIP** 클릭
3. 다운로드된 ZIP 파일을 원하는 폴더에 압축 해제

### 2단계: 자동 설치 실행
1. **관리자 권한**으로 명령 프롬프트 실행
   - Windows 키 + R → `cmd` 입력 → Ctrl+Shift+Enter
2. 압축 해제한 폴더로 이동
   ```cmd
   cd C:\path\to\aqua-analytics
   ```
3. 자동 설치 스크립트 실행
   ```cmd
   install_and_run.bat
   ```

### 3단계: 설치 과정
스크립트가 자동으로 다음 작업을 수행합니다:

```
[1/6] Python 설치 상태 확인 중...
[2/6] Python 3.11.7 다운로드 중... (필요시)
[3/6] Python 설치 중...
[4/6] 가상환경 생성 중...
[5/6] 패키지 설치 중...
[6/6] 폴더 구조 생성 중...
```

### 4단계: 서버 시작
설치 완료 후 자동으로 서버가 시작됩니다.

**접속 정보가 표시됩니다:**
```
🌐 서버 접속 정보:
────────────────────────────────────────
  로컬 접속: http://localhost:8501
  사내 네트워크 접속: http://192.168.x.x:8501
────────────────────────────────────────
```

---

## 📦 방법 2: 배포 패키지 설치

### 1단계: 배포 패키지 생성 (원본 PC에서)
1. 원본 PC에서 다음 스크립트 실행:
   ```cmd
   create_deployment_package.bat
   ```
2. 생성된 `aqua-analytics-local-server.zip` 파일 확인

### 2단계: 대상 PC에 배포
1. ZIP 파일을 대상 PC에 복사
2. 원하는 위치에 압축 해제
3. 압축 해제된 폴더로 이동

### 3단계: 초기 설정
```cmd
# 관리자 권한으로 실행
setup_local_server.bat
```

### 4단계: 서버 시작
```cmd
start_server.bat
```

---

## 🔧 방법 3: 수동 설치

### 1단계: Python 설치 확인
```cmd
python --version
```
- Python 3.8 이상이 필요합니다
- 없다면 https://python.org 에서 다운로드

### 2단계: 프로젝트 다운로드
```cmd
git clone https://github.com/aqua-analytics/aqua-analytics.git
cd aqua-analytics
```

### 3단계: 가상환경 생성
```cmd
python -m venv aqua_env
```

### 4단계: 가상환경 활성화
**Windows:**
```cmd
aqua_env\Scripts\activate
```

**macOS/Linux:**
```bash
source aqua_env/bin/activate
```

### 5단계: 패키지 설치
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### 6단계: 폴더 구조 생성
```cmd
mkdir aqua_analytics_data\uploads
mkdir aqua_analytics_data\processed
mkdir aqua_analytics_data\database
mkdir aqua_analytics_data\reports\dashboard
mkdir aqua_analytics_data\reports\integrated
mkdir aqua_analytics_data\standards
mkdir aqua_analytics_data\templates
```

### 7단계: 서버 실행
```cmd
streamlit run aqua_analytics_premium.py --server.address 0.0.0.0 --server.port 8501
```

---

## 🌐 네트워크 설정

### Windows 방화벽 설정
관리자 권한 명령 프롬프트에서 실행:
```cmd
netsh advfirewall firewall add rule name="Aqua-Analytics" dir=in action=allow protocol=TCP localport=8501
```

### 고정 IP 설정 (권장)
1. **제어판** → **네트워크 및 인터넷** → **네트워크 연결**
2. **이더넷** 우클릭 → **속성**
3. **인터넷 프로토콜 버전 4(TCP/IPv4)** → **속성**
4. **다음 IP 주소 사용** 선택
5. 고정 IP 주소 입력 (예: 192.168.1.100)

### 접속 테스트
- **로컬**: http://localhost:8501
- **사내 네트워크**: http://[서버IP]:8501

---

## 📱 사용 방법

### 첫 실행 시
1. 브라우저에서 서버 주소 접속
2. **📊 샘플 데이터 로드** 버튼 클릭
3. 대시보드에서 기능 확인

### 실제 데이터 사용
1. **📄 보고서 관리** → **📁 새 파일 분석** 탭
2. Excel 파일 업로드
3. 업로드 일자 및 의뢰 기관 입력
4. **📊 파일 분석 시작** 클릭

### 주요 기능
- **📊 대시보드**: 실시간 데이터 분석 및 시각화
- **📈 통합 분석**: 다중 파일 통합 분석
- **📄 보고서 관리**: 분석 이력 관리 및 보고서 생성
- **🛡️ 시험 규격 관리**: 환경 기준 관리

---

## 🔄 일상 사용

### 서버 시작
```cmd
# Windows
quick_start.bat

# macOS/Linux
./start_local_server.sh
```

### 서버 중지
- 터미널에서 **Ctrl+C** 누르기
- 또는 `stop_server.bat` 실행

### 자동 시작 설정 (선택사항)
1. **작업 스케줄러** 실행
2. **기본 작업 만들기**
3. 시작 프로그램: `quick_start.bat`
4. 트리거: **컴퓨터 시작 시**

---

## 🛠️ 문제 해결

### Python 설치 오류
```cmd
# 수동 설치
1. https://python.org 접속
2. Python 3.11.7 다운로드
3. "Add to PATH" 체크 후 설치
4. 시스템 재부팅
```

### 패키지 설치 오류
```cmd
# pip 업그레이드
python -m pip install --upgrade pip

# 개별 설치
pip install streamlit pandas plotly openpyxl python-dateutil psutil
```

### 포트 사용 중 오류
```cmd
# 포트 사용 프로세스 확인
netstat -ano | findstr :8501

# 프로세스 종료 (PID 확인 후)
taskkill /PID [PID번호] /F
```

### 네트워크 접속 불가
1. **방화벽 설정 확인**
   ```cmd
   netsh advfirewall firewall show rule name="Aqua-Analytics"
   ```

2. **IP 주소 확인**
   ```cmd
   ipconfig
   ```

3. **포트 열림 확인**
   ```cmd
   telnet [서버IP] 8501
   ```

### 가상환경 오류
```cmd
# 가상환경 삭제 후 재생성
rmdir /s aqua_env
python -m venv aqua_env
```

---

## 📊 시스템 요구사항

### 최소 사양
- **OS**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **CPU**: 2코어 이상
- **메모리**: 4GB RAM
- **저장공간**: 2GB 이상
- **네트워크**: 인터넷 연결 (초기 설치 시)

### 권장 사양
- **OS**: Windows 11, macOS 12+, Ubuntu 20.04+
- **CPU**: 4코어 이상
- **메모리**: 8GB RAM
- **저장공간**: 5GB 이상
- **네트워크**: 기가비트 이더넷

---

## 🔐 보안 고려사항

### 네트워크 보안
- 사내 네트워크에서만 접속 허용
- 필요시 VPN 연결 후 사용
- 정기적인 보안 업데이트

### 데이터 보안
- 중요 데이터는 정기적으로 백업
- 접근 권한 관리
- 로그 모니터링

---

## 📞 지원 및 문의

### 기술 지원
- **이메일**: iot.ideashare@gmail.com
- **GitHub Issues**: https://github.com/aqua-analytics/aqua-analytics/issues

### 문서 및 자료
- **GitHub Repository**: https://github.com/aqua-analytics/aqua-analytics
- **온라인 데모**: https://aqua-analytics.streamlit.app
- **설치 가이드**: 이 문서

### 업데이트
- GitHub에서 최신 버전 확인
- 정기적인 업데이트 권장
- 변경사항은 릴리스 노트 참조

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

**🌊 깨끗한 환경을 위한 데이터 인사이트**

*Aqua-Analytics Premium으로 환경 데이터 분석의 새로운 경험을 시작하세요!*