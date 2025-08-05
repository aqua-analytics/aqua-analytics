# Streamlit Cloud 배포 가이드

## 🌟 Streamlit Cloud 무료 배포

### 1단계: GitHub 저장소 준비
```bash
# GitHub에 저장소 생성 후
git add .
git commit -m "실험실 품질관리 대시보드 완성"
git push origin main
```

### 2단계: Streamlit Cloud 배포
1. https://share.streamlit.io 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 저장소 선택: `your-username/lab-analysis-dashboard`
5. Main file path: `app.py`
6. "Deploy!" 클릭

### 3단계: 공유
- 자동 생성된 URL로 누구나 접속 가능
- 예: `https://your-app-name.streamlit.app`

### 주의사항
- 파일 업로드 크기 제한: 200MB
- 메모리 제한: 1GB
- 무료 계정: 3개 앱까지