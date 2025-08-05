# Heroku 배포 가이드

## 🚀 Heroku 배포 (무료 티어 종료, 유료)

### 1단계: Heroku 설정 파일 생성

#### Procfile 생성
```bash
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
```

#### runtime.txt 생성
```bash
echo "python-3.9.16" > runtime.txt
```

### 2단계: Heroku CLI 설치 및 배포
```bash
# Heroku CLI 설치
# https://devcenter.heroku.com/articles/heroku-cli

# 로그인
heroku login

# 앱 생성
heroku create your-lab-dashboard

# 환경 변수 설정
heroku config:set LOG_LEVEL=INFO
heroku config:set MAX_FILE_SIZE=50

# 배포
git add .
git commit -m "Heroku 배포 설정"
git push heroku main
```

### 3단계: 접속
- URL: `https://your-lab-dashboard.herokuapp.com`