# 🚀 Aqua-Analytics Premium 배포 가이드

## 📋 개요

Aqua-Analytics Premium은 두 가지 버전으로 배포됩니다:

1. **🌐 GitHub 데모 버전**: 기능 체험용, 임시 저장
2. **🏢 로컬 서버 버전**: 실제 업무용, 영구 저장

---

## 🌐 GitHub 데모 버전 배포

### 1단계: GitHub 푸시
```bash
# 자동 배포 스크립트 실행
deploy_to_github.bat
```

### 2단계: Streamlit Cloud 배포
1. https://share.streamlit.io 접속
2. GitHub 계정으로 로그인 (`iot.ideashare@gmail.com`)
3. "New app" 클릭
4. 설정:
   - Repository: `aqua-analytics/aqua-analytics`
   - Branch: `main`
   - Main file path: `app.py`
5. "Deploy!" 클릭

### 3단계: 배포 완료
- 배포 URL: https://aqua-analytics.streamlit.app
- 자동 업데이트: GitHub 푸시 시 자동 재배포

---

## 🏢 로컬 서버 버전 배포

### 방법 1: 자동 설치 (권장)
```bash
# 관리자 권한으로 실행
install_and_run.bat
```

**기능:**
- Python 자동 설치 (미설치 시)
- 가상환경 자동 생성
- 패키지 자동 설치
- 폴더 구조 자동 생성
- 서버 자동 시작

### 방법 2: 빠른 시작 (설치 완료 후)
```bash
# 일반 실행
quick_start.bat
```

### 방법 3: 수동 설치
```bash
# 1. Python 가상환경 생성
python -m venv aqua_env

# 2. 가상환경 활성화
aqua_env\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 서버 실행
streamlit run aqua_analytics_premium.py --server.address 0.0.0.0 --server.port 8501
```

---

## 🌐 네트워크 설정

### 사내 네트워크 접속 설정

1. **Windows 방화벽 설정**
   ```bash
   # 관리자 권한 CMD에서 실행
   netsh advfirewall firewall add rule name="Aqua-Analytics" dir=in action=allow protocol=TCP localport=8501
   ```

2. **고정 IP 설정 (권장)**
   - 제어판 → 네트워크 및 인터넷 → 네트워크 연결
   - 이더넷 → 속성 → IPv4 → 속성
   - 고정 IP 설정

3. **접속 테스트**
   ```
   로컬: http://localhost:8501
   사내: http://192.168.x.x:8501
   ```

---

## 📊 버전별 특징 비교

| 구분 | GitHub 데모 | 로컬 서버 |
|------|-------------|-----------|
| **용도** | 기능 체험, 마케팅 | 실제 업무 |
| **데이터 저장** | 임시 (세션 기반) | 영구 저장 |
| **접속 방법** | 웹 URL | 사내 네트워크 |
| **설치 필요** | 없음 | Python 환경 |
| **업데이트** | 자동 | 수동 |
| **보안** | 공개 | 사내 전용 |

---

## 🔧 문제 해결

### Python 설치 오류
```bash
# 수동 설치
1. https://python.org 접속
2. Python 3.11.7 다운로드
3. "Add to PATH" 체크 후 설치
4. 시스템 재부팅
```

### 패키지 설치 오류
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 개별 설치
pip install streamlit pandas plotly openpyxl python-dateutil
```

### 네트워크 접속 오류
```bash
# 방화벽 확인
netsh advfirewall firewall show rule name="Aqua-Analytics"

# 포트 사용 확인
netstat -an | findstr :8501
```

### 가상환경 오류
```bash
# 가상환경 삭제 후 재생성
rmdir /s aqua_env
python -m venv aqua_env
```

---

## 📞 지원

- **이메일**: iot.ideashare@gmail.com
- **GitHub**: https://github.com/aqua-analytics/aqua-analytics
- **Issues**: https://github.com/aqua-analytics/aqua-analytics/issues

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

**🌊 깨끗한 환경을 위한 데이터 인사이트**