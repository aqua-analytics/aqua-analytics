#!/bin/bash

# 실험실 품질관리 대시보드 배포 스크립트
# Lab Analysis Dashboard Deployment Script

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로깅 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 설정 변수
PROJECT_NAME="lab-analysis-dashboard"
DOCKER_IMAGE_NAME="lab-dashboard"
DOCKER_TAG="${DOCKER_TAG:-latest}"
ENVIRONMENT="${ENVIRONMENT:-production}"
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

# 도움말 함수
show_help() {
    cat << EOF
실험실 품질관리 대시보드 배포 스크립트

사용법: $0 [옵션] [명령]

명령:
    build       Docker 이미지 빌드
    deploy      애플리케이션 배포
    start       서비스 시작
    stop        서비스 중지
    restart     서비스 재시작
    status      서비스 상태 확인
    logs        로그 확인
    backup      데이터 백업
    restore     데이터 복원
    cleanup     정리 작업
    health      헬스체크 실행

옵션:
    -e, --env ENV       환경 설정 (development, staging, production)
    -t, --tag TAG       Docker 이미지 태그
    -h, --help          도움말 표시

예제:
    $0 build
    $0 deploy -e production
    $0 start
    $0 logs -f
EOF
}

# 환경 확인 함수
check_prerequisites() {
    log_info "필수 요구사항 확인 중..."
    
    # Docker 확인
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되지 않았습니다."
        exit 1
    fi
    
    # Docker Compose 확인
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose가 설치되지 않았습니다."
        exit 1
    fi
    
    # .env 파일 확인
    if [ ! -f ".env" ]; then
        log_warning ".env 파일이 없습니다. .env.example을 복사합니다."
        cp .env.example .env
    fi
    
    log_success "필수 요구사항 확인 완료"
}

# 환경 설정 함수
setup_environment() {
    log_info "환경 설정 중... (${ENVIRONMENT})"
    
    # 필요한 디렉토리 생성
    mkdir -p uploads/pending
    mkdir -p data/processed
    mkdir -p data/standards
    mkdir -p reports
    mkdir -p logs
    mkdir -p backups
    
    # 권한 설정
    chmod 755 uploads data reports logs
    chmod 644 .env
    
    log_success "환경 설정 완료"
}

# Docker 이미지 빌드 함수
build_image() {
    log_info "Docker 이미지 빌드 중..."
    
    # 빌드 컨텍스트 정리
    docker system prune -f
    
    # 이미지 빌드
    docker build \
        --tag "${DOCKER_IMAGE_NAME}:${DOCKER_TAG}" \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VERSION="${DOCKER_TAG}" \
        .
    
    if [ $? -eq 0 ]; then
        log_success "Docker 이미지 빌드 완료: ${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
    else
        log_error "Docker 이미지 빌드 실패"
        exit 1
    fi
}

# 애플리케이션 배포 함수
deploy_application() {
    log_info "애플리케이션 배포 중..."
    
    # 기존 컨테이너 중지 및 제거
    docker-compose down --remove-orphans
    
    # 새 컨테이너 시작
    docker-compose up -d
    
    # 배포 확인
    sleep 10
    if check_health; then
        log_success "애플리케이션 배포 완료"
    else
        log_error "애플리케이션 배포 실패"
        docker-compose logs
        exit 1
    fi
}

# 서비스 시작 함수
start_services() {
    log_info "서비스 시작 중..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        log_success "서비스 시작 완료"
        show_status
    else
        log_error "서비스 시작 실패"
        exit 1
    fi
}

# 서비스 중지 함수
stop_services() {
    log_info "서비스 중지 중..."
    docker-compose down
    
    if [ $? -eq 0 ]; then
        log_success "서비스 중지 완료"
    else
        log_error "서비스 중지 실패"
        exit 1
    fi
}

# 서비스 재시작 함수
restart_services() {
    log_info "서비스 재시작 중..."
    docker-compose restart
    
    if [ $? -eq 0 ]; then
        log_success "서비스 재시작 완료"
        show_status
    else
        log_error "서비스 재시작 실패"
        exit 1
    fi
}

# 상태 확인 함수
show_status() {
    log_info "서비스 상태 확인 중..."
    docker-compose ps
    
    echo ""
    log_info "컨테이너 리소스 사용량:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# 로그 확인 함수
show_logs() {
    local follow_flag=""
    if [ "$1" = "-f" ] || [ "$1" = "--follow" ]; then
        follow_flag="-f"
    fi
    
    log_info "애플리케이션 로그 확인 중..."
    docker-compose logs $follow_flag lab-dashboard
}

# 헬스체크 함수
check_health() {
    log_info "헬스체크 실행 중..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
            log_success "애플리케이션이 정상적으로 실행 중입니다."
            return 0
        fi
        
        log_info "헬스체크 시도 $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    log_error "헬스체크 실패: 애플리케이션이 응답하지 않습니다."
    return 1
}

# 백업 함수
backup_data() {
    log_info "데이터 백업 중..."
    
    mkdir -p "$BACKUP_DIR"
    
    # 데이터 디렉토리 백업
    if [ -d "data" ]; then
        tar -czf "${BACKUP_DIR}/data_backup.tar.gz" data/
        log_success "데이터 백업 완료: ${BACKUP_DIR}/data_backup.tar.gz"
    fi
    
    # 업로드 파일 백업
    if [ -d "uploads" ]; then
        tar -czf "${BACKUP_DIR}/uploads_backup.tar.gz" uploads/
        log_success "업로드 파일 백업 완료: ${BACKUP_DIR}/uploads_backup.tar.gz"
    fi
    
    # 보고서 백업
    if [ -d "reports" ]; then
        tar -czf "${BACKUP_DIR}/reports_backup.tar.gz" reports/
        log_success "보고서 백업 완료: ${BACKUP_DIR}/reports_backup.tar.gz"
    fi
    
    # 설정 파일 백업
    cp .env "${BACKUP_DIR}/"
    cp docker-compose.yml "${BACKUP_DIR}/"
    
    log_success "전체 백업 완료: $BACKUP_DIR"
}

# 복원 함수
restore_data() {
    if [ -z "$1" ]; then
        log_error "백업 디렉토리를 지정해주세요."
        echo "사용법: $0 restore <백업_디렉토리>"
        exit 1
    fi
    
    local backup_path="$1"
    
    if [ ! -d "$backup_path" ]; then
        log_error "백업 디렉토리가 존재하지 않습니다: $backup_path"
        exit 1
    fi
    
    log_info "데이터 복원 중... ($backup_path)"
    
    # 서비스 중지
    docker-compose down
    
    # 데이터 복원
    if [ -f "${backup_path}/data_backup.tar.gz" ]; then
        tar -xzf "${backup_path}/data_backup.tar.gz"
        log_success "데이터 복원 완료"
    fi
    
    if [ -f "${backup_path}/uploads_backup.tar.gz" ]; then
        tar -xzf "${backup_path}/uploads_backup.tar.gz"
        log_success "업로드 파일 복원 완료"
    fi
    
    if [ -f "${backup_path}/reports_backup.tar.gz" ]; then
        tar -xzf "${backup_path}/reports_backup.tar.gz"
        log_success "보고서 복원 완료"
    fi
    
    # 서비스 재시작
    docker-compose up -d
    
    log_success "데이터 복원 완료"
}

# 정리 함수
cleanup() {
    log_info "정리 작업 실행 중..."
    
    # 중지된 컨테이너 제거
    docker container prune -f
    
    # 사용하지 않는 이미지 제거
    docker image prune -f
    
    # 사용하지 않는 볼륨 제거
    docker volume prune -f
    
    # 사용하지 않는 네트워크 제거
    docker network prune -f
    
    # 오래된 로그 파일 정리 (30일 이상)
    find logs/ -name "*.log*" -mtime +30 -delete 2>/dev/null || true
    
    # 오래된 백업 파일 정리 (90일 이상)
    find backups/ -type d -mtime +90 -exec rm -rf {} + 2>/dev/null || true
    
    log_success "정리 작업 완료"
}

# 메인 함수
main() {
    # 명령행 인수 처리
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -t|--tag)
                DOCKER_TAG="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            build)
                check_prerequisites
                setup_environment
                build_image
                exit 0
                ;;
            deploy)
                check_prerequisites
                setup_environment
                build_image
                deploy_application
                exit 0
                ;;
            start)
                check_prerequisites
                start_services
                exit 0
                ;;
            stop)
                stop_services
                exit 0
                ;;
            restart)
                restart_services
                exit 0
                ;;
            status)
                show_status
                exit 0
                ;;
            logs)
                shift
                show_logs "$@"
                exit 0
                ;;
            backup)
                backup_data
                exit 0
                ;;
            restore)
                shift
                restore_data "$@"
                exit 0
                ;;
            cleanup)
                cleanup
                exit 0
                ;;
            health)
                check_health
                exit 0
                ;;
            *)
                log_error "알 수 없는 명령: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 명령이 지정되지 않은 경우 도움말 표시
    show_help
}

# 스크립트 실행
main "$@"