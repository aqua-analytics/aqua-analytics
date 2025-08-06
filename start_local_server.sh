#!/bin/bash

# Aqua-Analytics Premium 로컬 서버 시작 스크립트 (macOS/Linux)

echo ""
echo "████████████████████████████████████████████████████████████████"
echo "██                                                            ██"
echo "██           🧪 Aqua-Analytics Premium                        ██"
echo "██              로컬 서버 시작                                ██"
echo "██                                                            ██"
echo "████████████████████████████████████████████████████████████████"
echo ""

# 가상환경 확인
if [ ! -d "aqua_env" ]; then
    echo "❌ 가상환경이 설정되지 않았습니다."
    echo ""
    echo "처음 실행이시라면 다음 명령어를 실행해주세요:"
    echo "  python3 -m venv aqua_env"
    echo "  source aqua_env/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    exit 1
fi

echo "✅ 가상환경 활성화 중..."
source aqua_env/bin/activate

echo ""
echo "🌐 서버 접속 정보:"
echo "────────────────────────────────────────────────────────────────"
echo "   로컬 접속: http://localhost:8501"

# IP 주소 확인 (macOS)
IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
if [ ! -z "$IP" ]; then
    echo "   네트워크 접속: http://$IP:8501"
fi

echo "────────────────────────────────────────────────────────────────"
echo ""

echo "🚀 Aqua-Analytics 서버 시작 중..."
echo ""
echo "⚠️  서버를 중지하려면 Ctrl+C를 누르세요."
echo ""

# Streamlit 실행
streamlit run aqua_analytics_premium.py --server.address 0.0.0.0 --server.port 8501 --server.headless true

echo ""
echo "서버가 종료되었습니다."