# 📦 설치 가이드

> 실험실 품질관리 대시보드의 설치 및 초기 설정을 위한 단계별 가이드

## 📋 목차

1. [시스템 요구사항](#시스템-요구사항)
2. [설치 방법](#설치-방법)
3. [초기 설정](#초기-설정)
4. [검증 및 테스트](#검증-및-테스트)
5. [문제 해결](#문제-해결)

## 💻 시스템 요구사항

### 하드웨어 요구사항

#### 최소 사양
- **CPU**: 2코어 (2.0GHz 이상)
- **메모리**: 4GB RAM
- **저장공간**: 20GB 여유 공간
- **네트워크**: 100Mbps 인터넷 연결

#### 권장 사양
- **CPU**: 4코어 (2.5GHz 이상)
- **메모리**: 8GB RAM 이상
- **저장공간**: 100GB SSD
- **네트워크**: 1Gbps 인터넷 연결

### 소프트웨어 요구사항

#### 지원 운영체제
- **Linux**: Ubuntu 20.04+, CentOS 8+, RHEL 8+
- **macOS**: 10.15+ (Catalina 이상)
- **Windows**: Windows 10/11, Windows Server 2019+

#### 필수 소프트웨어
- **Python**: 3.9 이상
- **pip**: 21.0 이상
- **Git**: 2.25 이상 (선택사항)

#### Docker 사용 시 (권장)
- **Docker**: 20.10 이상
- **Docker Compose**: 2.0 이상

### 브라우저 요구사항
- **Chrome**: 90 이상
- **Firefox**: 88 이상
- **Safari**: 14 이상
- **Edge**: 90 이상

## 🚀 설치 방법

### 방법 1: Docker 설치 (권장)

Docker를 사용한 설치는 가장 간단하고 안정적인 방법입니다.

#### 1단계: Docker 설치

**Ubuntu/Debian:**
```bash
# 시스템 업데이트
sudo apt update

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# 로그아웃 후 다시 로그인하거나 다음 명령 실행
newgrp docker

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**CentOS/RHEL:**
```bash
# Docker 저장소 추가
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Docker 설치
sudo yum install -y docker-ce docker-ce-cli containerd.io

# Docker 서비스 시작
sudo systemctl start docker
sudo systemctl enable docker

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**macOS:**
```bash
# Homebrew를 사용한 설치
brew install --cask docker

# 또는 Docker Desktop 다운로드
# https://www.docker.com/products/docker-desktop
```

**Windows:**
```powershell
# Docker Desktop 다운로드 및 설치
# https://www.docker.com/products/docker-desktop

# 또는 Chocolatey 사용
choco install docker-desktop
```

#### 2단계: 애플리케이션 다운로드

```bash
# Git을 사용한 다운로드 (권장)
git clone https://github.com/your-repo/lab-analysis-dashboard.git
cd lab-analysis-dashboard

# 또는 ZIP 파일 다운로드
wget https://github.com/your-repo/lab-analysis-dashboard/archive/main.zip
unzip main.zip
cd lab-analysis-dashboard-main
```

#### 3단계: 환경 설정

```bash
# 환경 변수 파일 생성
cp .env.example .env

# 환경 변수 편집 (선택사항)
nano .env
```

#### 4단계: 애플리케이션 실행

```bash
# 자동 배포 스크립트 사용 (권장)
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# 또는 Docker Compose 직접 사용
docker-compose up -d
```

#### 5단계: 설치 확인

```bash
# 컨테이너 상태 확인
docker-compose ps

# 애플리케이션 접속 테스트
curl http://localhost:8501/_stcore/health

# 브라우저에서 접속
# http://localhost:8501
```

### 방법 2: Python 직접 설치

Python 환경에서 직접 설치하는 방법입니다.

#### 1단계: Python 환경 준비

**Ubuntu/Debian:**
```bash
# Python 및 pip 설치
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 시스템 패키지 설치 (WeasyPrint 의존성)
sudo apt install -y libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev libffi-dev shared-mime-info
```

**CentOS/RHEL:**
```bash
# Python 및 pip 설치
sudo yum install -y python3 python3-pip

# 개발 도구 설치
sudo yum groupinstall -y "Development Tools"
sudo yum install -y cairo-devel pango-devel gdk-pixbuf2-devel libffi-devel
```

**macOS:**
```bash
# Homebrew를 사용한 Python 설치
brew install python

# 또는 pyenv 사용
brew install pyenv
pyenv install 3.9.16
pyenv global 3.9.16
```

**Windows:**
```powershell
# Python 공식 사이트에서 다운로드
# https://www.python.org/downloads/

# 또는 Chocolatey 사용
choco install python

# 또는 Microsoft Store에서 설치
```

#### 2단계: 가상환경 생성

```bash
# 프로젝트 디렉토리로 이동
cd lab-analysis-dashboard

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

#### 3단계: 의존성 설치

```bash
# pip 업그레이드
pip install --upgrade pip

# 의존성 설치
pip install -r requirements.txt

# 설치 확인
pip list
```

#### 4단계: 디렉토리 구조 생성

```bash
# 필요한 디렉토리 생성
mkdir -p uploads/pending
mkdir -p data/processed
mkdir -p data/standards
mkdir -p reports
mkdir -p logs
```

#### 5단계: 애플리케이션 실행

```bash
# Streamlit 애플리케이션 실행
streamlit run app.py

# 또는 특정 포트로 실행
streamlit run app.py --server.port=8502

# 백그라운드 실행
nohup streamlit run app.py > logs/app.log 2>&1 &
```

### 방법 3: 개발 환경 설치

개발자를 위한 설치 방법입니다.

#### 1단계: 개발 도구 설치

```bash
# Git 설치
sudo apt install -y git  # Ubuntu/Debian
sudo yum install -y git  # CentOS/RHEL
brew install git         # macOS

# 코드 에디터 (VS Code 권장)
# https://code.visualstudio.com/
```

#### 2단계: 저장소 포크 및 클론

```bash
# GitHub에서 저장소 포크 후
git clone https://github.com/YOUR_USERNAME/lab-analysis-dashboard.git
cd lab-analysis-dashboard

# 원본 저장소를 upstream으로 추가
git remote add upstream https://github.com/original-repo/lab-analysis-dashboard.git
```

#### 3단계: 개발 환경 설정

```bash
# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 개발 의존성 포함 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 도구들

# pre-commit 훅 설정
pre-commit install
```

#### 4단계: 개발 서버 실행

```bash
# 개발 모드로 실행 (자동 재로드)
streamlit run app.py --server.runOnSave=true

# 디버그 모드
export APP_DEBUG=true
export LOG_LEVEL=DEBUG
streamlit run app.py
```

## ⚙️ 초기 설정

### 환경 변수 설정

`.env` 파일을 편집하여 환경에 맞게 설정합니다:

```bash
# .env 파일 편집
nano .env
```

**주요 설정 항목:**

```bash
# 애플리케이션 기본 설정
APP_PORT=8501                    # 애플리케이션 포트
APP_HOST=0.0.0.0                # 바인딩 호스트
APP_DEBUG=false                 # 디버그 모드

# 파일 처리 설정
MAX_FILE_SIZE=50                # 최대 파일 크기 (MB)
UPLOAD_TIMEOUT=300              # 업로드 타임아웃 (초)
SUPPORTED_FORMATS=xlsx,xls      # 지원 파일 형식

# 보안 설정
AUTO_DELETE_HOURS=24            # 파일 자동 삭제 시간
MAX_CONCURRENT_USERS=20         # 최대 동시 사용자
ENABLE_FILE_VALIDATION=true     # 파일 검증 활성화

# 성능 설정
MEMORY_LIMIT=1g                 # 메모리 제한
CPU_LIMIT=1                     # CPU 제한
CACHE_ENABLED=true              # 캐시 활성화

# 로깅 설정
LOG_LEVEL=INFO                  # 로그 레벨
LOG_FORMAT=json                 # 로그 형식
LOG_FILE_PATH=logs/app.log      # 로그 파일 경로
```

### 디렉토리 권한 설정

```bash
# 업로드 디렉토리 권한 설정
chmod 755 uploads/pending
chmod 755 data/processed
chmod 755 reports
chmod 755 logs

# 소유자 설정 (필요한 경우)
chown -R $USER:$USER uploads data reports logs
```

### 방화벽 설정

**Ubuntu/Debian (UFW):**
```bash
# UFW 활성화
sudo ufw enable

# 애플리케이션 포트 허용
sudo ufw allow 8501/tcp

# SSH 포트 허용 (원격 접속 시)
sudo ufw allow ssh
```

**CentOS/RHEL (firewalld):**
```bash
# 방화벽 서비스 시작
sudo systemctl start firewalld
sudo systemctl enable firewalld

# 포트 허용
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```

### 시스템 서비스 등록 (선택사항)

시스템 부팅 시 자동으로 시작되도록 설정:

```bash
# systemd 서비스 파일 생성
sudo nano /etc/systemd/system/lab-dashboard.service
```

**서비스 파일 내용:**
```ini
[Unit]
Description=Lab Analysis Dashboard
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/lab-analysis-dashboard
Environment=PATH=/path/to/lab-analysis-dashboard/venv/bin
ExecStart=/path/to/lab-analysis-dashboard/venv/bin/streamlit run app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**서비스 활성화:**
```bash
# 서비스 등록 및 시작
sudo systemctl daemon-reload
sudo systemctl enable lab-dashboard
sudo systemctl start lab-dashboard

# 서비스 상태 확인
sudo systemctl status lab-dashboard
```

## ✅ 검증 및 테스트

### 기본 기능 테스트

#### 1. 애플리케이션 접속 테스트

```bash
# 헬스체크 엔드포인트 테스트
curl -f http://localhost:8501/_stcore/health

# 예상 응답:
# {"status": "healthy", "timestamp": "2024-01-15T10:30:00Z"}
```

#### 2. 웹 인터페이스 테스트

브라우저에서 `http://localhost:8501` 접속 후:

1. **페이지 로딩 확인**
   - 메인 페이지가 정상적으로 로드되는지 확인
   - 사이드바와 메인 콘텐츠 영역이 표시되는지 확인

2. **파일 업로드 테스트**
   - 샘플 Excel 파일 업로드
   - 파일 검증 과정 확인
   - 에러 메시지 표시 확인

3. **대시보드 기능 테스트**
   - KPI 카드 표시 확인
   - 차트 렌더링 확인
   - 테이블 인터랙션 확인

#### 3. 성능 테스트

```bash
# 메모리 사용량 확인
free -h

# CPU 사용량 확인
top -p $(pgrep -f streamlit)

# 디스크 사용량 확인
df -h

# 네트워크 연결 확인
netstat -tulpn | grep 8501
```

### 자동 테스트 실행

#### 1. 단위 테스트

```bash
# 가상환경 활성화 (Python 설치 시)
source venv/bin/activate

# 테스트 실행
pytest tests/unit/ -v

# 커버리지 포함 테스트
pytest tests/unit/ --cov=src --cov-report=html
```

#### 2. 통합 테스트

```bash
# 통합 테스트 실행
pytest tests/integration/ -v

# 특정 테스트 실행
python tests/integration/test_complete_workflow.py
```

#### 3. 성능 벤치마크

```bash
# 성능 테스트 실행
python tests/integration/test_performance_benchmarks.py

# 브라우저 호환성 테스트
python tests/integration/test_browser_compatibility.py
```

### 로그 확인

#### 1. 애플리케이션 로그

```bash
# 실시간 로그 모니터링
tail -f logs/app.log

# 에러 로그만 확인
grep "ERROR" logs/app.log

# JSON 로그 파싱 (jq 설치 필요)
cat logs/app.log | jq '.level, .message'
```

#### 2. 시스템 로그

```bash
# systemd 서비스 로그 (서비스 등록 시)
sudo journalctl -u lab-dashboard -f

# Docker 로그 (Docker 설치 시)
docker-compose logs -f lab-dashboard
```

## 🔧 문제 해결

### 일반적인 설치 문제

#### 1. Python 의존성 설치 실패

**증상:**
```
ERROR: Failed building wheel for some-package
```

**해결방법:**
```bash
# 시스템 패키지 설치 (Ubuntu/Debian)
sudo apt install -y python3-dev build-essential libffi-dev libssl-dev

# pip 업그레이드
pip install --upgrade pip setuptools wheel

# 개별 패키지 설치 시도
pip install --no-cache-dir package-name
```

#### 2. WeasyPrint 설치 오류

**증상:**
```
ERROR: Failed to build WeasyPrint
```

**해결방법:**
```bash
# Ubuntu/Debian
sudo apt install -y libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev libffi-dev shared-mime-info

# CentOS/RHEL
sudo yum install -y cairo-devel pango-devel gdk-pixbuf2-devel libffi-devel

# macOS
brew install cairo pango gdk-pixbuf libffi
```

#### 3. 포트 충돌 오류

**증상:**
```
OSError: [Errno 98] Address already in use
```

**해결방법:**
```bash
# 포트 사용 프로세스 확인
lsof -i :8501

# 프로세스 종료
kill -9 PID

# 다른 포트 사용
streamlit run app.py --server.port=8502
```

#### 4. 권한 오류

**증상:**
```
PermissionError: [Errno 13] Permission denied
```

**해결방법:**
```bash
# 디렉토리 권한 설정
chmod -R 755 uploads data reports logs

# 소유자 변경
chown -R $USER:$USER .

# Docker 사용 시 볼륨 권한 설정
docker-compose down
sudo chown -R 1000:1000 uploads data reports
docker-compose up -d
```

### Docker 관련 문제

#### 1. Docker 데몬 연결 오류

**증상:**
```
Cannot connect to the Docker daemon
```

**해결방법:**
```bash
# Docker 서비스 시작
sudo systemctl start docker

# 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
newgrp docker

# Docker 소켓 권한 확인
ls -la /var/run/docker.sock
```

#### 2. 이미지 빌드 실패

**증상:**
```
ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully
```

**해결방법:**
```bash
# Docker 캐시 삭제
docker system prune -a

# 빌드 시 캐시 사용 안함
docker-compose build --no-cache

# 개별 이미지 빌드
docker build --no-cache -t lab-dashboard .
```

#### 3. 볼륨 마운트 오류

**증상:**
```
Error response from daemon: invalid mount config
```

**해결방법:**
```bash
# 절대 경로 사용
# docker-compose.yml에서 상대 경로를 절대 경로로 변경

# 볼륨 권한 확인
ls -la uploads/ data/ reports/

# 볼륨 재생성
docker-compose down -v
docker-compose up -d
```

### 성능 관련 문제

#### 1. 메모리 부족

**증상:**
- 애플리케이션 응답 없음
- OOM (Out of Memory) 오류

**해결방법:**
```bash
# 메모리 사용량 확인
free -h
docker stats

# 스왑 메모리 추가
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Docker 메모리 제한 증가
# docker-compose.yml에서 memory 제한 조정
```

#### 2. 디스크 공간 부족

**증상:**
```
No space left on device
```

**해결방법:**
```bash
# 디스크 사용량 확인
df -h

# 불필요한 파일 삭제
docker system prune -a
sudo apt autoremove
sudo apt autoclean

# 로그 파일 정리
sudo journalctl --vacuum-time=7d
```

### 네트워크 관련 문제

#### 1. 외부 접속 불가

**증상:**
- 로컬에서는 접속 가능하지만 외부에서 접속 불가

**해결방법:**
```bash
# 방화벽 설정 확인
sudo ufw status
sudo firewall-cmd --list-all

# 포트 리스닝 확인
netstat -tulpn | grep 8501

# 바인딩 주소 확인
# .env 파일에서 APP_HOST=0.0.0.0 설정
```

#### 2. DNS 해상도 문제

**증상:**
- 도메인으로 접속 불가

**해결방법:**
```bash
# DNS 설정 확인
nslookup your-domain.com

# /etc/hosts 파일 확인
cat /etc/hosts

# DNS 서버 변경
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

### 지원 요청

문제가 지속될 경우 다음 정보와 함께 지원을 요청하세요:

#### 1. 시스템 정보 수집

```bash
# 시스템 정보
uname -a
cat /etc/os-release

# Python 정보
python3 --version
pip --version

# Docker 정보 (해당하는 경우)
docker --version
docker-compose --version

# 애플리케이션 로그
tail -100 logs/app.log
```

#### 2. 에러 정보 수집

```bash
# 에러 메시지 전체 복사
# 스크린샷 첨부
# 재현 단계 상세 기록
```

#### 3. 연락처

- **이메일**: support@example.com
- **GitHub Issues**: https://github.com/your-repo/lab-analysis-dashboard/issues
- **문서**: https://github.com/your-repo/lab-analysis-dashboard/wiki

---

**📚 다음 단계**
- [사용자 가이드](user_guide.md) - 애플리케이션 사용 방법
- [배포 가이드](deployment_guide.md) - 프로덕션 배포 방법
- [API 문서](api_documentation.md) - 개발자를 위한 기술 문서