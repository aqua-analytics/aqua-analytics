# 🚀 배포 가이드

> 실험실 품질관리 대시보드의 프로덕션 배포를 위한 완전한 가이드

## 📋 목차

1. [배포 개요](#배포-개요)
2. [사전 요구사항](#사전-요구사항)
3. [Docker 배포](#docker-배포)
4. [클라우드 배포](#클라우드-배포)
5. [모니터링 설정](#모니터링-설정)
6. [보안 설정](#보안-설정)
7. [백업 및 복구](#백업-및-복구)
8. [문제 해결](#문제-해결)

## 🎯 배포 개요

### 지원되는 배포 환경

- **로컬 서버**: 온프레미스 서버 환경
- **클라우드**: AWS, Azure, GCP
- **컨테이너**: Docker, Kubernetes
- **PaaS**: Heroku, Streamlit Cloud

### 배포 아키텍처

```
┌─ Load Balancer ─────────────────────────────────────┐
│  Nginx / Apache / Cloud LB                         │
└─────────────────┬───────────────────────────────────┘
                  │
┌─ Application Layer ─────────────────────────────────┐
│  ┌─ Container 1 ─┐  ┌─ Container 2 ─┐             │
│  │ Lab Dashboard │  │ Lab Dashboard │  ...         │
│  │ (Port 8501)   │  │ (Port 8502)   │             │
│  └───────────────┘  └───────────────┘             │
└─────────────────────────────────────────────────────┘
┌─ Storage Layer ─────────────────────────────────────┐
│  ┌─ File Storage ─┐  ┌─ Database ────┐             │
│  │ Uploads        │  │ PostgreSQL    │  (Optional) │
│  │ Reports        │  │ MongoDB       │             │
│  │ Logs           │  │ Redis Cache   │             │
│  └────────────────┘  └───────────────┘             │
└─────────────────────────────────────────────────────┘
┌─ Monitoring Layer ──────────────────────────────────┐
│  Prometheus + Grafana + ELK Stack                  │
└─────────────────────────────────────────────────────┘
```

## 📋 사전 요구사항

### 시스템 요구사항

#### 최소 사양
- **CPU**: 2 코어
- **메모리**: 4GB RAM
- **디스크**: 20GB 여유 공간
- **네트워크**: 100Mbps

#### 권장 사양
- **CPU**: 4 코어 이상
- **메모리**: 8GB RAM 이상
- **디스크**: 100GB SSD
- **네트워크**: 1Gbps

### 소프트웨어 요구사항

#### 필수 소프트웨어
```bash
# Docker 및 Docker Compose
Docker Engine 20.10+
Docker Compose 2.0+

# 또는 Python 환경
Python 3.9+
pip 21.0+
```

#### 선택적 소프트웨어
```bash
# 웹 서버 (리버스 프록시)
Nginx 1.18+
Apache 2.4+

# 모니터링
Prometheus 2.30+
Grafana 8.0+

# 로그 관리
Elasticsearch 7.0+
Logstash 7.0+
Kibana 7.0+
```

### 네트워크 요구사항

#### 포트 설정
- **8501**: Streamlit 애플리케이션 (기본)
- **9090**: Prometheus 모니터링 (선택)
- **3000**: Grafana 대시보드 (선택)
- **80/443**: HTTP/HTTPS (리버스 프록시)

#### 방화벽 설정
```bash
# Ubuntu/Debian
sudo ufw allow 8501/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

## 🐳 Docker 배포

### 단일 컨테이너 배포

#### 1. 저장소 준비

```bash
# 저장소 클론
git clone https://github.com/your-repo/lab-analysis-dashboard.git
cd lab-analysis-dashboard

# 환경 설정
cp .env.example .env
```

#### 2. 환경 변수 설정

```bash
# .env 파일 편집
nano .env
```

**프로덕션 환경 설정**:
```bash
# 애플리케이션 설정
APP_PORT=8501
APP_DEBUG=false
APP_HOST=0.0.0.0

# 보안 설정
AUTO_DELETE_HOURS=24
MAX_CONCURRENT_USERS=50
ENABLE_FILE_VALIDATION=true

# 성능 설정
MEMORY_LIMIT=2g
CPU_LIMIT=2
MAX_FILE_SIZE=100

# 로깅 설정
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_PATH=logs/app.log
```

#### 3. 배포 실행

```bash
# 자동 배포 스크립트 사용
chmod +x scripts/deploy.sh
./scripts/deploy.sh production

# 또는 수동 배포
docker-compose -f docker-compose.yml up -d
```

#### 4. 배포 확인

```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f lab-dashboard

# 헬스체크
curl http://localhost:8501/_stcore/health
```

### 다중 컨테이너 배포 (고가용성)

#### 1. Docker Compose 설정

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  lab-dashboard-1:
    build: .
    container_name: lab-dashboard-1
    ports:
      - "8501:8501"
    environment:
      - INSTANCE_ID=1
    volumes:
      - shared-uploads:/app/uploads
      - shared-data:/app/data
      - shared-reports:/app/reports
    restart: unless-stopped

  lab-dashboard-2:
    build: .
    container_name: lab-dashboard-2
    ports:
      - "8502:8501"
    environment:
      - INSTANCE_ID=2
    volumes:
      - shared-uploads:/app/uploads
      - shared-data:/app/data
      - shared-reports:/app/reports
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: lab-dashboard-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - lab-dashboard-1
      - lab-dashboard-2
    restart: unless-stopped

volumes:
  shared-uploads:
  shared-data:
  shared-reports:
```

#### 2. Nginx 로드 밸런서 설정

```nginx
# nginx.conf
upstream lab_dashboard {
    server lab-dashboard-1:8501;
    server lab-dashboard-2:8501;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # HTTP to HTTPS 리다이렉트
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL 설정
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # 보안 헤더
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # 프록시 설정
    location / {
        proxy_pass http://lab_dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 지원
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 타임아웃 설정
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 정적 파일 캐싱
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 3. 고가용성 배포 실행

```bash
# 다중 컨테이너 배포
docker-compose -f docker-compose.prod.yml up -d

# 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 로드 밸런서 테스트
curl -H "Host: your-domain.com" http://localhost
```

## ☁️ 클라우드 배포

### AWS 배포

#### 1. EC2 인스턴스 설정

```bash
# EC2 인스턴스 생성 (Ubuntu 20.04 LTS)
# 인스턴스 타입: t3.medium 이상 권장

# SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker ubuntu

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 애플리케이션 배포

```bash
# 애플리케이션 다운로드
git clone https://github.com/your-repo/lab-analysis-dashboard.git
cd lab-analysis-dashboard

# 환경 설정
cp .env.example .env
nano .env  # AWS 환경에 맞게 수정

# 배포 실행
./scripts/deploy.sh production
```

#### 3. ELB (Elastic Load Balancer) 설정

```bash
# Application Load Balancer 생성
aws elbv2 create-load-balancer \
    --name lab-dashboard-alb \
    --subnets subnet-12345678 subnet-87654321 \
    --security-groups sg-12345678

# 타겟 그룹 생성
aws elbv2 create-target-group \
    --name lab-dashboard-targets \
    --protocol HTTP \
    --port 8501 \
    --vpc-id vpc-12345678 \
    --health-check-path /_stcore/health
```

### Azure 배포

#### 1. Container Instances 사용

```bash
# Azure CLI 로그인
az login

# 리소스 그룹 생성
az group create --name lab-dashboard-rg --location eastus

# 컨테이너 인스턴스 생성
az container create \
    --resource-group lab-dashboard-rg \
    --name lab-dashboard \
    --image your-registry/lab-dashboard:latest \
    --cpu 2 \
    --memory 4 \
    --ports 8501 \
    --environment-variables \
        APP_PORT=8501 \
        LOG_LEVEL=INFO
```

#### 2. App Service 사용

```bash
# App Service Plan 생성
az appservice plan create \
    --name lab-dashboard-plan \
    --resource-group lab-dashboard-rg \
    --sku B2 \
    --is-linux

# Web App 생성
az webapp create \
    --resource-group lab-dashboard-rg \
    --plan lab-dashboard-plan \
    --name lab-dashboard-app \
    --deployment-container-image-name your-registry/lab-dashboard:latest
```

### GCP 배포

#### 1. Cloud Run 사용

```bash
# gcloud CLI 설정
gcloud auth login
gcloud config set project your-project-id

# 컨테이너 이미지 빌드 및 푸시
gcloud builds submit --tag gcr.io/your-project-id/lab-dashboard

# Cloud Run 서비스 배포
gcloud run deploy lab-dashboard \
    --image gcr.io/your-project-id/lab-dashboard \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2
```

#### 2. GKE (Kubernetes) 사용

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lab-dashboard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lab-dashboard
  template:
    metadata:
      labels:
        app: lab-dashboard
    spec:
      containers:
      - name: lab-dashboard
        image: gcr.io/your-project-id/lab-dashboard:latest
        ports:
        - containerPort: 8501
        env:
        - name: APP_PORT
          value: "8501"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
---
apiVersion: v1
kind: Service
metadata:
  name: lab-dashboard-service
spec:
  selector:
    app: lab-dashboard
  ports:
  - port: 80
    targetPort: 8501
  type: LoadBalancer
```

```bash
# Kubernetes 배포
kubectl apply -f k8s-deployment.yaml

# 서비스 상태 확인
kubectl get services
kubectl get pods
```

## 📊 모니터링 설정

### Prometheus + Grafana 설정

#### 1. 모니터링 스택 배포

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped

volumes:
  prometheus-data:
  grafana-data:
```

#### 2. Prometheus 설정

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'lab-dashboard'
    static_configs:
      - targets: ['lab-dashboard:8501']
    metrics_path: '/_stcore/metrics'
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

#### 3. Grafana 대시보드 설정

```json
{
  "dashboard": {
    "title": "Lab Dashboard Monitoring",
    "panels": [
      {
        "title": "Application Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"lab-dashboard\"}",
            "legendFormat": "Status"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "process_resident_memory_bytes{job=\"lab-dashboard\"}",
            "legendFormat": "Memory Usage"
          }
        ]
      },
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(process_cpu_seconds_total{job=\"lab-dashboard\"}[5m])",
            "legendFormat": "CPU Usage"
          }
        ]
      }
    ]
  }
}
```

### 로그 모니터링 (ELK Stack)

#### 1. ELK Stack 배포

```yaml
# docker-compose.elk.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    container_name: logstash
    volumes:
      - ./elk/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
      - ./logs:/usr/share/logstash/logs
    ports:
      - "5044:5044"
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    container_name: kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch-data:
```

#### 2. Logstash 설정

```ruby
# elk/logstash.conf
input {
  file {
    path => "/usr/share/logstash/logs/app.log"
    start_position => "beginning"
    codec => "json"
  }
}

filter {
  if [level] {
    mutate {
      add_field => { "log_level" => "%{level}" }
    }
  }
  
  date {
    match => [ "timestamp", "ISO8601" ]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "lab-dashboard-logs-%{+YYYY.MM.dd}"
  }
  
  stdout {
    codec => rubydebug
  }
}
```

## 🔒 보안 설정

### SSL/TLS 설정

#### 1. Let's Encrypt 인증서

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx

# 인증서 발급
sudo certbot --nginx -d your-domain.com

# 자동 갱신 설정
sudo crontab -e
# 다음 라인 추가:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 2. 자체 서명 인증서 (개발/테스트용)

```bash
# SSL 디렉토리 생성
mkdir -p ssl

# 개인키 생성
openssl genrsa -out ssl/key.pem 2048

# 인증서 요청 생성
openssl req -new -key ssl/key.pem -out ssl/cert.csr

# 자체 서명 인증서 생성
openssl x509 -req -days 365 -in ssl/cert.csr -signkey ssl/key.pem -out ssl/cert.pem
```

### 방화벽 설정

#### 1. UFW (Ubuntu)

```bash
# UFW 활성화
sudo ufw enable

# 기본 정책 설정
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 필요한 포트만 허용
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 특정 IP에서만 관리 포트 접근 허용
sudo ufw allow from YOUR_ADMIN_IP to any port 9090  # Prometheus
sudo ufw allow from YOUR_ADMIN_IP to any port 3000  # Grafana
```

#### 2. iptables

```bash
# 기본 정책 설정
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# 기본 연결 허용
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# SSH 허용
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# HTTP/HTTPS 허용
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 설정 저장
iptables-save > /etc/iptables/rules.v4
```

### 애플리케이션 보안

#### 1. 환경 변수 보안

```bash
# .env 파일 권한 설정
chmod 600 .env

# Docker secrets 사용 (Docker Swarm)
echo "your-secret-value" | docker secret create app-secret -

# Kubernetes secrets 사용
kubectl create secret generic app-secrets \
  --from-literal=database-password=your-password \
  --from-literal=api-key=your-api-key
```

#### 2. 컨테이너 보안

```dockerfile
# Dockerfile 보안 강화
FROM python:3.9-slim

# 비root 사용자 생성
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 애플리케이션 디렉토리 설정
WORKDIR /app
COPY --chown=appuser:appuser . .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 비root 사용자로 실행
USER appuser

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py"]
```

## 💾 백업 및 복구

### 데이터 백업

#### 1. 파일 시스템 백업

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/lab-dashboard"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="lab-dashboard-backup-${DATE}.tar.gz"

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

# 데이터 백업
tar -czf $BACKUP_DIR/$BACKUP_FILE \
  uploads/ \
  data/ \
  reports/ \
  logs/ \
  config/ \
  .env

# 오래된 백업 파일 삭제 (30일 이상)
find $BACKUP_DIR -name "lab-dashboard-backup-*.tar.gz" -mtime +30 -delete

echo "백업 완료: $BACKUP_DIR/$BACKUP_FILE"
```

#### 2. Docker 볼륨 백업

```bash
#!/bin/bash
# docker-backup.sh

# 실행 중인 컨테이너 중지
docker-compose down

# 볼륨 백업
docker run --rm \
  -v lab-analysis-dashboard_uploads:/data/uploads \
  -v lab-analysis-dashboard_data:/data/data \
  -v lab-analysis-dashboard_reports:/data/reports \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/volumes-backup-$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# 컨테이너 재시작
docker-compose up -d

echo "Docker 볼륨 백업 완료"
```

#### 3. 자동 백업 설정

```bash
# crontab 설정
crontab -e

# 매일 새벽 2시에 백업 실행
0 2 * * * /path/to/backup.sh

# 매주 일요일 새벽 3시에 Docker 볼륨 백업
0 3 * * 0 /path/to/docker-backup.sh
```

### 복구 절차

#### 1. 파일 시스템 복구

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "사용법: $0 <백업파일>"
  exit 1
fi

# 서비스 중지
docker-compose down

# 기존 데이터 백업 (안전을 위해)
mv uploads uploads.old
mv data data.old
mv reports reports.old

# 백업 파일 복원
tar -xzf $BACKUP_FILE

# 권한 설정
chown -R 1000:1000 uploads data reports

# 서비스 재시작
docker-compose up -d

echo "복구 완료"
```

#### 2. Docker 볼륨 복구

```bash
#!/bin/bash
# docker-restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "사용법: $0 <볼륨백업파일>"
  exit 1
fi

# 컨테이너 중지
docker-compose down

# 볼륨 복구
docker run --rm \
  -v lab-analysis-dashboard_uploads:/data/uploads \
  -v lab-analysis-dashboard_data:/data/data \
  -v lab-analysis-dashboard_reports:/data/reports \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/$BACKUP_FILE -C /data

# 컨테이너 재시작
docker-compose up -d

echo "Docker 볼륨 복구 완료"
```

### 재해 복구 계획

#### 1. RTO/RPO 목표
- **RTO (Recovery Time Objective)**: 4시간
- **RPO (Recovery Point Objective)**: 1시간

#### 2. 복구 우선순위
1. **핵심 애플리케이션**: 실험실 대시보드
2. **데이터**: 업로드된 파일, 생성된 보고서
3. **설정**: 환경 변수, 구성 파일
4. **로그**: 감사 및 디버깅용

#### 3. 복구 절차서

```markdown
# 재해 복구 절차

## 1단계: 상황 평가
- [ ] 장애 범위 확인
- [ ] 데이터 손실 정도 평가
- [ ] 복구 방법 결정

## 2단계: 인프라 복구
- [ ] 서버/클라우드 인스턴스 복구
- [ ] 네트워크 연결 확인
- [ ] 도메인/DNS 설정 확인

## 3단계: 애플리케이션 복구
- [ ] 최신 백업 파일 확인
- [ ] 데이터 복구 실행
- [ ] 애플리케이션 배포
- [ ] 서비스 상태 확인

## 4단계: 검증 및 모니터링
- [ ] 기능 테스트 실행
- [ ] 데이터 무결성 확인
- [ ] 모니터링 시스템 복구
- [ ] 사용자 알림
```

## 🔧 문제 해결

### 일반적인 배포 문제

#### 1. 컨테이너 시작 실패

**증상**:
```bash
docker-compose ps
# lab-dashboard   Exit 1
```

**해결방법**:
```bash
# 로그 확인
docker-compose logs lab-dashboard

# 일반적인 원인들:
# 1. 환경 변수 오류
# 2. 포트 충돌
# 3. 볼륨 마운트 오류
# 4. 메모리 부족

# 포트 충돌 확인
netstat -tulpn | grep 8501

# 메모리 사용량 확인
free -h
docker stats
```

#### 2. 성능 저하

**증상**:
- 페이지 로딩 속도 저하
- 파일 업로드 실패
- 메모리 부족 오류

**해결방법**:
```bash
# 리소스 사용량 확인
docker stats
htop

# 로그 분석
tail -f logs/app.log | grep ERROR

# 컨테이너 재시작
docker-compose restart lab-dashboard

# 리소스 제한 조정
# docker-compose.yml에서 memory/cpu 제한 증가
```

#### 3. 네트워크 연결 문제

**증상**:
- 외부에서 접근 불가
- 로드 밸런서 오류
- SSL 인증서 오류

**해결방법**:
```bash
# 방화벽 상태 확인
sudo ufw status
iptables -L

# 포트 리스닝 확인
netstat -tulpn | grep :80
netstat -tulpn | grep :443

# SSL 인증서 확인
openssl x509 -in ssl/cert.pem -text -noout

# DNS 확인
nslookup your-domain.com
```

### 모니터링 및 알림

#### 1. 헬스체크 스크립트

```bash
#!/bin/bash
# health-check.sh

ENDPOINT="http://localhost:8501/_stcore/health"
TIMEOUT=10

# 헬스체크 실행
response=$(curl -s -w "%{http_code}" --max-time $TIMEOUT $ENDPOINT)
http_code="${response: -3}"

if [ "$http_code" = "200" ]; then
    echo "✅ 서비스 정상"
    exit 0
else
    echo "❌ 서비스 오류 (HTTP $http_code)"
    
    # 자동 복구 시도
    docker-compose restart lab-dashboard
    
    # 알림 발송 (예: Slack, 이메일)
    # send_alert "Lab Dashboard 서비스 오류 발생"
    
    exit 1
fi
```

#### 2. 자동 복구 스크립트

```bash
#!/bin/bash
# auto-recovery.sh

LOG_FILE="/var/log/lab-dashboard-recovery.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# 서비스 상태 확인
if ! docker-compose ps | grep -q "Up"; then
    log_message "서비스 다운 감지, 복구 시작"
    
    # 컨테이너 재시작
    docker-compose down
    docker-compose up -d
    
    # 복구 확인
    sleep 30
    if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        log_message "서비스 복구 완료"
    else
        log_message "서비스 복구 실패, 관리자 개입 필요"
        # 긴급 알림 발송
    fi
fi
```

#### 3. 모니터링 대시보드 설정

**Grafana 알림 규칙**:
```json
{
  "alert": {
    "name": "Lab Dashboard Down",
    "message": "Lab Dashboard 서비스가 다운되었습니다",
    "frequency": "10s",
    "conditions": [
      {
        "query": {
          "queryType": "",
          "refId": "A",
          "model": {
            "expr": "up{job=\"lab-dashboard\"} == 0",
            "interval": "",
            "legendFormat": "",
            "refId": "A"
          }
        },
        "reducer": {
          "type": "last",
          "params": []
        },
        "evaluator": {
          "params": [1],
          "type": "lt"
        }
      }
    ],
    "executionErrorState": "alerting",
    "noDataState": "no_data",
    "for": "1m"
  }
}
```

---

**📚 관련 문서**
- [사용자 가이드](user_guide.md) - 최종 사용자를 위한 가이드
- [API 문서](api_documentation.md) - 개발자를 위한 API 가이드
- [README](../README.md) - 프로젝트 개요 및 빠른 시작