# YouTube 자동화 시스템 (마이크로서비스 아키텍처)

휴먼 패턴 시뮬레이션이 적용된 YouTube 자동 시청 시스템.

## 📐 아키텍처 개요

```
┌──────────────────────────────────────────────────────────────────┐
│                    Frontend Dashboard (React)                     │
└──────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                    API Gateway (:8000)                            │
└──────────────────────────────────────────────────────────────────┘
        │           │           │           │           │
        ▼           ▼           ▼           ▼           ▼
   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
   │ Video  │  │ Device │  │  Task  │  │ Pattern│  │ Result │
   │ :8001  │  │ :8002  │  │ :8003  │  │ :8004  │  │ :8005  │
   └────────┘  └────────┘  └────────┘  └────────┘  └────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │ PC Agent │ │ PC Agent │ │ PC Agent │
              │ + Laixi  │ │ + Laixi  │ │ + Laixi  │
              └──────────┘ └──────────┘ └──────────┘
```

## 🚀 빠른 시작

### 1. Docker Compose로 실행

```bash
# 환경 변수 설정
cp .env.example .env

# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 2. 개별 서비스 실행 (개발용)

```bash
# Human Pattern Service
cd services/human-pattern-service
pip install -r requirements.txt
python main.py

# API Gateway
cd services/api-gateway
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
npm install
npm run dev
```

## 📁 디렉토리 구조

```
ai-farm/
├── services/                    # 마이크로서비스
│   ├── api-gateway/             # API Gateway (:8000)
│   ├── video-service/           # 영상 관리 (:8001)
│   ├── device-service/          # 기기 관리 (:8002)
│   ├── task-service/            # 작업 스케줄링 (:8003)
│   ├── human-pattern-service/   # 휴먼 패턴 생성 (:8004)
│   └── result-service/          # 결과 수집 (:8005)
│
├── shared/                      # 공유 모듈
│   ├── schemas/                 # Pydantic 스키마
│   └── database/                # DB 스키마
│
├── scripts/                     # Laixi (AutoX.js) 스크립트
│   ├── youtube_automation.js    # 메인 자동화 스크립트
│   └── human_patterns.js        # 휴먼 패턴 모듈
│
├── frontend/                    # React 대시보드
│
├── docker-compose.yml
└── ARCHITECTURE.md              # 상세 아키텍처 문서
```

## 🧠 휴먼 패턴 알고리즘

PDF 문서 기반 실제 사용자 행동 시뮬레이션:

### 시청 시간 분포 (Beta 분포)
- **α=2, β=5** 파라미터로 Long-tail 분포 생성
- 즉시 이탈 (0-10초): 35%
- 초반 이탈 (10-30초): 25%
- 짧은 시청 (30초-1분): 15%
- 중간 시청 (1-3분): 12%
- 긴 시청 (3-5분): 8%
- 완전 시청 (5분+): 5%

### 좋아요 타이밍 분포
- 시청 시작 5초 이내: 2%
- 시청 중간 지점: 35%
- 시청 완료 직후: 45%
- 시청 완료 후 10초+: 18%

### 터치 패턴
- **정규분포 오프셋**: 버튼 중심에서 약간 벗어난 터치
- **터치 지속 시간**: 50-200ms 범위 내 정규분포

### 스와이프 패턴
- **Smoothstep 이징**: 천천히 시작 → 빠르게 → 천천히 끝
- **노이즈 추가**: 직선 회피를 위한 랜덤 흔들림

## 📡 API 엔드포인트

### 인증
모든 API 요청에 `Authorization: Bearer {API_KEY}` 헤더 필요.

### 주요 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 시스템 헬스체크 |
| GET | `/videos` | 영상 목록 |
| POST | `/videos` | 영상 등록 |
| GET | `/devices` | 기기 목록 |
| POST | `/devices` | 기기 등록 |
| GET | `/tasks` | 작업 목록 |
| POST | `/tasks` | 작업 생성 |
| GET | `/tasks/next?device_id={id}` | 다음 작업 요청 |
| POST | `/patterns/generate` | 패턴 생성 |
| GET | `/stats` | 전체 통계 |

## ⚙️ 환경 변수

```env
# 데이터베이스
DB_PASSWORD=securepassword123

# API 키 (쉼표로 구분)
API_KEYS=test-key-123,admin-key-456

# 서비스 URL (Docker 내부)
VIDEO_SERVICE_URL=http://video-service:8001
DEVICE_SERVICE_URL=http://device-service:8002
TASK_SERVICE_URL=http://task-service:8003
PATTERN_SERVICE_URL=http://pattern-service:8004
RESULT_SERVICE_URL=http://result-service:8005
```

## 📱 Laixi 스크립트 사용법

1. `scripts/` 폴더의 파일을 Laixi 앱의 Scripts 폴더에 복사
2. `youtube_automation.js` 실행
3. 서버 URL과 API Key 입력
4. 영상 추가 또는 서버에서 가져오기
5. 시작 버튼 클릭

## 🔒 보안 고려사항

⚠️ **이 시스템은 자사 플랫폼 테스트 목적으로만 사용해야 합니다.**

- YouTube, TikTok 등 타사 플랫폼에서의 사용은 약관 위반입니다
- API 키를 안전하게 관리하세요
- 프로덕션 환경에서는 HTTPS를 사용하세요

## 📊 대시보드 기능

- **실시간 모니터링**: 작업 상태, 기기 상태
- **통계 차트**: 일별 작업 완료, 인터랙션 비율
- **패턴 시뮬레이터**: 휴먼 패턴 미리보기
- **영상/기기 관리**: CRUD 인터페이스

## 📚 참고 자료

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 상세 아키텍처 문서
- [PDF 문서] - 휴먼 패턴 알고리즘 원본

---

**라이선스**: Private - 내부 사용 전용

