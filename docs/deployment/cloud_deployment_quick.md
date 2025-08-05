# 클라우드 빠른 배포 가이드

## ☁️ AWS EC2 무료 티어 배포

### 1단계: EC2 인스턴스 생성
1. AWS 콘솔 → EC2 → "Launch Instance"
2. Ubuntu 20.04 LTS 선택
3. t2.micro (무료 티어) 선택
4. 보안 그룹: 포트 8501 열기

### 2단계: 서버 설정
```bash
# SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker ubuntu

# 애플리케이션 배포
git clone https://github.com/your-repo/lab-analysis-dashboard.git
cd lab-analysis-dashboard
./scripts/deploy.sh production
```

### 3단계: 도메인 연결 (선택사항)
- Route 53에서 도메인 구매
- A 레코드로 EC2 IP 연결

## 🌐 Google Cloud Run 배포

### 1단계: 프로젝트 설정
```bash
# gcloud CLI 설치 및 로그인
gcloud auth login
gcloud config set project your-project-id
```

### 2단계: 배포
```bash
# 컨테이너 빌드 및 배포
gcloud builds submit --tag gcr.io/your-project-id/lab-dashboard
gcloud run deploy lab-dashboard \
  --image gcr.io/your-project-id/lab-dashboard \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 3단계: 접속
- 자동 생성된 URL로 접속 가능