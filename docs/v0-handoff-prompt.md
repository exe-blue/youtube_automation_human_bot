# v0.dev 핸드오프 프롬프트 - YouTube 자동화 대시보드

## 📋 프로젝트 개요

YouTube 영상 자동 시청 시스템의 관리 대시보드입니다. Android 기기 팜을 통해 대규모 영상 시청을 자동화하며, **휴먼 패턴 시뮬레이션**으로 자연스러운 사용자 행동을 생성합니다.

### 핵심 기능
- 📹 영상 관리: YouTube URL 등록, 키워드, 우선순위 설정
- 📱 기기 관리: Android 기기 상태 실시간 모니터링
- 📋 작업 큐: 시청 작업 스케줄링 및 분배
- 🧠 휴먼 패턴: Beta 분포 기반 시청 시간, 터치/스크롤 패턴 시뮬레이션
- 📊 통계: 일별 작업, 인터랙션, 시청 시간 분석

---

## 🛠️ 기술 스택

```json
{
  "framework": "React 18 + TypeScript + Vite",
  "styling": "TailwindCSS (다크 테마)",
  "font": "Pretendard (한글), JetBrains Mono (코드/숫자)",
  "state": ["TanStack Query (서버 상태)", "Zustand (클라이언트 상태)"],
  "animation": "Framer Motion",
  "charts": "Recharts",
  "icons": "Lucide React",
  "routing": "React Router v6",
  "date": "date-fns + date-fns/locale/ko",
  "backend": "Supabase (PostgreSQL + Realtime + Auth + Storage)",
  "automation": "n8n (워크플로우 자동화)"
}
```

### Supabase 연동
- **실시간 구독**: 기기 상태, 작업 현황 실시간 업데이트
- **자동 REST API**: PostgREST 기반 API 자동 생성
- **스토리지**: 스크린샷 저장
- **Row Level Security**: 데이터 보안

### n8n 연동
- **작업 스케줄링**: 정기적 작업 자동 생성
- **알림 시스템**: Slack/Discord/Telegram 알림
- **기기 모니터링**: 과열/오프라인 감지 및 대응
- **리포트 자동화**: 일일/주간 통계 리포트

---

## 🎨 디자인 시스템

### 색상 팔레트 (다크 테마 필수)

```css
:root {
  /* 배경 계층 */
  --dark-900: #0d0d12;    /* 최상위 배경 */
  --dark-800: #12121a;    /* 사이드바 */
  --dark-700: #1a1a24;    /* 카드 배경 */
  --dark-600: #252532;    /* 보더, 구분선 */
  --dark-500: #32324a;    /* 차트 그리드 */
  
  /* 프라이머리 (레드) */
  --primary-600: #dc2626;
  --primary-500: #ef4444;
  --primary-400: #f87171;
  
  /* 액센트 컬러 */
  --accent-cyan: #06b6d4;      /* 좋아요, 작업중, 정보 */
  --accent-purple: #a855f7;    /* 댓글, 패턴, 특별 */
  --accent-emerald: #10b981;   /* 성공, 대기중, 완료 */
  --accent-amber: #f59e0b;     /* 경고, 중간 우선순위 */
  
  /* 텍스트 */
  --text-primary: #ffffff;
  --text-secondary: #94a3b8;   /* slate-400 */
  --text-muted: #64748b;       /* slate-500 */
}
```

### 폰트 설정

```css
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

body {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
}

.font-mono {
  font-family: 'JetBrains Mono', monospace;
}
```

### 컴포넌트 스타일 패턴

```tsx
// 카드 기본
className="bg-dark-700 rounded-xl p-6 border border-dark-600"

// 호버 효과
className="transition-all duration-200 hover:border-primary-500/50 hover:shadow-lg hover:shadow-primary-500/10"

// 버튼 - Primary
className="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"

// 버튼 - Secondary  
className="bg-dark-600 hover:bg-dark-500 text-gray-300 px-4 py-2 rounded-lg font-medium transition-colors"

// 입력 필드
className="w-full bg-dark-600 border border-dark-500 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none transition-colors"

// 상태 배지
const statusStyles = {
  success: "bg-accent-emerald/20 text-accent-emerald",
  warning: "bg-accent-amber/20 text-accent-amber", 
  error: "bg-red-500/20 text-red-400",
  info: "bg-accent-cyan/20 text-accent-cyan",
  neutral: "bg-gray-500/20 text-gray-400"
}
```

---

## 📐 레이아웃 구조

### 전체 레이아웃

```
┌──────────────────────────────────────────────────────────────────┐
│ ┌────────────┬───────────────────────────────────────────────┐   │
│ │            │                                               │   │
│ │  사이드바   │              메인 콘텐츠                       │   │
│ │  (264px)   │              (flex-1)                         │   │
│ │            │              padding: 32px                     │   │
│ │  - 로고    │                                               │   │
│ │  - 네비    │                                               │   │
│ │  - 설정    │                                               │   │
│ │            │                                               │   │
│ └────────────┴───────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### 사이드바 구조

```tsx
const navItems = [
  { path: '/', icon: LayoutDashboard, label: '대시보드' },
  { path: '/videos', icon: Video, label: '영상 관리' },
  { path: '/devices', icon: Smartphone, label: '기기 관리' },
  { path: '/tasks', icon: ListTodo, label: '작업 큐' },
  { path: '/patterns', icon: Brain, label: '패턴 시뮬레이터' },
  { path: '/stats', icon: BarChart3, label: '통계' },
]
```

---

## 📄 페이지별 상세 명세

### 1. 대시보드 (/)

#### 구성요소
1. **헤더**: 제목 "대시보드", 설명 "시스템 현황을 한눈에 확인하세요"

2. **통계 카드 4개** (grid-cols-4)
   | 카드 | 아이콘 | 색상 | 값 | 서브텍스트 |
   |------|--------|------|-----|-----------|
   | 총 영상 | Video | cyan | {videos.total} | 대기 {pending}개 |
   | 활성 기기 | Smartphone | emerald | {idle}/{total} | 오프라인 {offline}대 |
   | 완료 작업 | CheckCircle | purple | {completed_tasks} | 평균 시청률 {avg}% |
   | 시청 시간 | Clock | amber | {formatTime()} | 누적 시청 |

3. **차트 섹션** (grid-cols-2)
   - 좌: **일별 작업 완료** - AreaChart
     - 빨간 그라데이션 (#ef4444)
     - X축: 날짜, Y축: 작업 수
   - 우: **인터랙션 통계** - 3개 프로그레스바
     - 👍 좋아요 비율 (cyan)
     - 💬 댓글 비율 (purple)
     - 📺 평균 시청률 (emerald)

4. **기기 상태 분포** (grid-cols-4)
   - 대기 중 (emerald), 작업 중 (cyan), 오프라인 (gray), 오류 (red)
   - 각 카드에 펄스 애니메이션 dot

#### 데이터 갱신
- `refetchInterval: 10000` (10초)

#### Framer Motion 애니메이션
```tsx
// 카드 스태거 애니메이션
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}
```

---

### 2. 영상 관리 (/videos)

#### 구성요소
1. **헤더 + 추가 버튼**
   - 우측: "영상 추가" 버튼 (Plus 아이콘)

2. **상태 필터** (5개 버튼)
   ```tsx
   const filters = [
     { value: '', label: '전체', count: total },
     { value: 'pending', label: '대기', count: pending },
     { value: 'processing', label: '처리중', count: processing },
     { value: 'completed', label: '완료', count: completed },
     { value: 'error', label: '오류', count: error },
   ]
   ```

3. **테이블**
   | 컬럼 | 내용 |
   |------|------|
   | 제목 | 제목 + 외부 링크 아이콘 |
   | 키워드 | cyan 색상 텍스트 |
   | 길이 | {duration}초 |
   | 우선순위 | 배지 (8+: red, 5+: amber, else: gray) |
   | 상태 | StatusBadge 컴포넌트 |
   | 완료 | {completed_count}회 |
   | 액션 | 삭제 버튼 (Trash2) |

4. **추가 모달**
   - 필드: URL, 제목, 키워드, 영상 길이(초), 우선순위(1-10)
   - 버튼: 취소, 추가

---

### 3. 기기 관리 (/devices)

#### 구성요소
1. **상태 요약** (grid-cols-5)
   - 전체, 대기 중(emerald), 작업 중(cyan), 오프라인(gray), 오류(red)

2. **기기 카드 그리드** (grid-cols-3)
   ```tsx
   <DeviceCard>
     <Header>
       <Icon + 모델명 + 시리얼>
       <StatusIcon>
     </Header>
     
     <StatusBadge + PC ID>
     
     <HealthGrid cols-2>
       <Battery icon + level%>
       <Thermometer icon + temp°C>
       <Cpu icon + usage%>
       <CheckCircle icon + 처리건수>
     </HealthGrid>
     
     <SuccessRateBar> (total_tasks > 0일 때만)
   </DeviceCard>
   ```

#### 상태별 스타일
```tsx
const statusStyles = {
  idle: { border: 'border-accent-emerald/30', bg: 'bg-accent-emerald/5', icon: <Wifi className="text-accent-emerald" /> },
  busy: { border: 'border-accent-cyan/30', bg: 'bg-accent-cyan/5', icon: <Wifi className="text-accent-cyan animate-pulse" /> },
  offline: { border: 'border-gray-600', bg: 'bg-dark-800', icon: <WifiOff className="text-gray-500" /> },
  error: { border: 'border-red-500/30', bg: 'bg-red-500/5', icon: <XCircle className="text-red-400" /> },
  overheat: { border: 'border-red-500/30', bg: 'bg-red-500/5', icon: <Thermometer className="text-red-400 animate-pulse" /> },
}
```

#### 데이터 갱신
- `refetchInterval: 5000` (5초)

---

### 4. 작업 큐 (/tasks)

#### 구성요소
1. **상태 요약** (grid-cols-5)
   - 전체, 대기(Clock), 실행 중(Play), 완료(CheckCircle), 실패(XCircle)

2. **테이블**
   | 컬럼 | 내용 |
   |------|------|
   | 상태 | 아이콘 + 텍스트 배지 |
   | 영상 ID | font-mono, 8자 truncate |
   | 기기 | font-mono 또는 "미할당" |
   | 우선순위 | 배지 |
   | 시간 | formatDistanceToNow (한국어) |
   | 재시도 | {retry_count}/{max_retries} (빨간색) |

#### 상태 배지 설정
```tsx
const taskStatusConfig = {
  queued: { icon: Clock, color: 'bg-gray-500/20 text-gray-400', label: '대기' },
  assigned: { icon: Pause, color: 'bg-amber-500/20 text-amber-400', label: '할당됨' },
  running: { icon: Play, color: 'bg-accent-cyan/20 text-accent-cyan', label: '실행 중' },
  completed: { icon: CheckCircle, color: 'bg-accent-emerald/20 text-accent-emerald', label: '완료' },
  failed: { icon: XCircle, color: 'bg-red-500/20 text-red-400', label: '실패' },
  cancelled: { icon: XCircle, color: 'bg-gray-500/20 text-gray-400', label: '취소' },
}
```

---

### 5. 패턴 시뮬레이터 (/patterns)

#### 구성요소
1. **2열 레이아웃**

2. **좌측: 단일 패턴 생성**
   - 입력: 영상 길이(초)
   - 버튼: "패턴 생성" (Play 아이콘)
   - 결과 4개 카드:
     - 시청 시간 (Clock): {watch_time}초 ({watch_percent}%)
     - Seek (MousePointer): {seek_count}회
     - 좋아요 (ThumbsUp): Yes/No + 타이밍
     - 댓글 (MessageSquare): Yes/No
   - 추천 액션 리스트

3. **우측: 분포 시뮬레이션**
   - 입력: 영상 길이, 샘플 수
   - 버튼: "분포 시뮬레이션" (Brain 아이콘)
   - PieChart (도넛 차트)
   - 범례 테이블

4. **하단: 알고리즘 설명 카드** (grid-cols-4)
   - 시청 시간 (Beta 분포) - cyan
   - 좋아요 타이밍 - purple
   - 터치 패턴 - amber
   - 스와이프 - emerald

---

### 6. 통계 (/stats)

#### 구성요소
1. **주요 지표** (grid-cols-4)
   - 총 작업 (white)
   - 평균 시청률 (cyan)
   - 좋아요 비율 (purple)
   - 댓글 비율 (emerald)

2. **차트 그리드** (grid-cols-2)
   - 일별 작업 완료: BarChart (빨간)
   - 일별 인터랙션: LineChart (cyan: 좋아요, purple: 댓글)
   - 검색 경로 분포: PieChart (4가지 색상)
   - 일별 시청 시간: BarChart (emerald)

#### 차트 공통 스타일
```tsx
const chartConfig = {
  CartesianGrid: { strokeDasharray: "3 3", stroke: "#32324a" },
  XAxis: { stroke: "#64748b", tick: { fill: '#64748b', fontSize: 12 } },
  YAxis: { stroke: "#64748b", tick: { fill: '#64748b', fontSize: 12 } },
  Tooltip: { 
    contentStyle: { 
      backgroundColor: '#1a1a24', 
      border: '1px solid #32324a',
      borderRadius: '8px'
    }
  }
}
```

---

## 🔧 Zustand 스토어 구조

```typescript
// stores/appStore.ts
interface AppState {
  // 사이드바 상태
  sidebarCollapsed: boolean
  toggleSidebar: () => void
  
  // 알림
  notifications: Notification[]
  addNotification: (notification: Omit<Notification, 'id'>) => void
  removeNotification: (id: string) => void
  
  // 필터 상태 (페이지별)
  videoFilter: string
  setVideoFilter: (filter: string) => void
  
  // 모달 상태
  activeModal: string | null
  openModal: (modalId: string) => void
  closeModal: () => void
}

interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
}
```

---

## 🎬 Framer Motion 애니메이션 가이드

### 페이지 전환
```tsx
const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
}

<motion.div
  variants={pageVariants}
  initial="initial"
  animate="animate"
  exit="exit"
  transition={{ duration: 0.3 }}
>
  {children}
</motion.div>
```

### 카드 호버
```tsx
<motion.div
  whileHover={{ scale: 1.02, y: -4 }}
  transition={{ type: "spring", stiffness: 300 }}
>
  <Card />
</motion.div>
```

### 리스트 스태거
```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1
    }
  }
}

const item = {
  hidden: { opacity: 0, x: -20 },
  show: { opacity: 1, x: 0 }
}
```

### 숫자 카운트업
```tsx
import { animate, useMotionValue, useTransform } from 'framer-motion'

const AnimatedNumber = ({ value }: { value: number }) => {
  const count = useMotionValue(0)
  const rounded = useTransform(count, latest => Math.round(latest))
  
  useEffect(() => {
    const controls = animate(count, value, { duration: 1 })
    return controls.stop
  }, [value])
  
  return <motion.span>{rounded}</motion.span>
}
```

---

## 🔌 Supabase 클라이언트 설정

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'
import type { Database } from './database.types'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey)

// 실시간 구독 헬퍼
export const subscribeToTable = (
  table: 'videos' | 'devices' | 'tasks' | 'results',
  callback: (payload: any) => void
) => {
  return supabase
    .channel(`${table}_changes`)
    .on(
      'postgres_changes',
      { event: '*', schema: 'public', table },
      callback
    )
    .subscribe()
}
```

### 실시간 구독 훅 예시

```typescript
// hooks/useRealtimeDevices.ts
import { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { subscribeToTable } from '../lib/supabase'

export function useRealtimeDevices() {
  const queryClient = useQueryClient()

  useEffect(() => {
    const subscription = subscribeToTable('devices', () => {
      queryClient.invalidateQueries({ queryKey: ['devices'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [queryClient])
}
```

---

## 🤖 n8n 웹훅 연동

```typescript
// lib/n8n.ts
const N8N_WEBHOOK_BASE = import.meta.env.VITE_N8N_WEBHOOK_URL

export const n8nWebhooks = {
  // 수동 작업 트리거
  triggerTask: async (videoId: string, deviceId: string) => {
    const response = await fetch(`${N8N_WEBHOOK_BASE}/trigger-task`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_id: videoId, device_id: deviceId })
    })
    return response.json()
  },

  // 긴급 알림 전송
  sendAlert: async (type: 'error' | 'warning' | 'info', message: string) => {
    await fetch(`${N8N_WEBHOOK_BASE}/alert`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type, message, timestamp: new Date().toISOString() })
    })
  },

  // 일일 리포트 수동 요청
  requestDailyReport: async () => {
    const response = await fetch(`${N8N_WEBHOOK_BASE}/daily-report`, {
      method: 'POST'
    })
    return response.json()
  }
}
```

### 대시보드 n8n 액션 버튼

```tsx
// components/N8nActions.tsx
import { FileText, Bell, Zap } from 'lucide-react'

export function N8nActions() {
  return (
    <div className="flex gap-2">
      <button className="btn-secondary flex items-center gap-2">
        <FileText size={16} />
        리포트 생성
      </button>
      <button className="btn-secondary flex items-center gap-2">
        <Bell size={16} />
        테스트 알림
      </button>
    </div>
  )
}
```

---

## 📡 API 타입 정의

```typescript
// types/api.ts

export interface Video {
  id: string
  url: string | null
  title: string | null
  keyword: string | null
  duration: number | null
  priority: number
  status: 'pending' | 'processing' | 'completed' | 'error'
  completed_count: number
  error_count: number
  created_at: string
  updated_at: string
}

export interface Device {
  id: string
  serial_number: string
  pc_id: string
  model: string | null
  status: 'idle' | 'busy' | 'offline' | 'error' | 'overheat'
  last_heartbeat: string | null
  battery_temp: number | null
  cpu_usage: number | null
  memory_usage: number | null
  battery_level: number | null
  total_tasks: number
  success_tasks: number
  error_tasks: number
}

export interface Task {
  id: string
  video_id: string
  device_id: string | null
  status: 'queued' | 'assigned' | 'running' | 'completed' | 'failed' | 'cancelled'
  priority: number
  pattern_config: Record<string, unknown>
  retry_count: number
  max_retries: number
  queued_at: string
  assigned_at: string | null
  started_at: string | null
  completed_at: string | null
  error_message: string | null
}

export interface DashboardData {
  videos: {
    total: number
    pending: number
    processing: number
    completed: number
    error: number
  }
  devices: {
    total: number
    idle: number
    busy: number
    offline: number
    error: number
  }
  stats: {
    aggregated: AggregatedStats
    daily: DailyStats[]
  }
}

export interface AggregatedStats {
  total_tasks: number
  completed_tasks: number
  failed_tasks: number
  total_watch_time: number
  avg_watch_percent: number
  like_rate: number
  comment_rate: number
  search_type_distribution: Record<number, number>
}

export interface DailyStats {
  date: string
  tasks_completed: number
  tasks_failed: number
  watch_time: number
  likes: number
  comments: number
}

export interface PatternResponse {
  pattern: {
    watch: {
      watch_time: number
      watch_percent: number
      seek_count: number
    }
    interaction: {
      should_like: boolean
      like_timing: number | null
      should_comment: boolean
      comment_timing: number | null
    }
  }
  recommended_actions: string[]
}
```

---

## 🔐 환경 변수

```env
# frontend/.env.local

# Supabase
VITE_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...

# n8n Webhooks
VITE_N8N_WEBHOOK_URL=https://your-n8n.com/webhook
```

---

## ⛔ 금지 사항

1. **폰트**: Inter, Roboto, Arial 사용 금지 → Pretendard 사용
2. **테마**: 밝은 테마 사용 금지 → 다크 테마만
3. **로깅**: console.log 사용 금지 → 적절한 에러 핸들링
4. **any 타입**: TypeScript any 타입 금지 → 명시적 타입 정의
5. **매직 넘버**: 하드코딩된 숫자 금지 → 상수 정의

---

## ✅ 구현 체크리스트

### 필수 구현
- [ ] 6개 페이지 전체 구현
- [ ] 사이드바 네비게이션 (활성 상태 표시)
- [ ] 다크 테마 완전 적용
- [ ] Recharts 차트 4종 (Area, Bar, Line, Pie)
- [ ] 반응형 레이아웃 (md, lg 브레이크포인트)
- [ ] 로딩/에러 상태 UI
- [ ] Framer Motion 애니메이션
- [ ] Zustand 스토어 설정

### Supabase 연동
- [ ] @supabase/supabase-js 설치
- [ ] Supabase 클라이언트 설정
- [ ] 실시간 구독 (devices, tasks)
- [ ] API 함수를 Supabase 쿼리로 교체

### n8n 연동
- [ ] 웹훅 유틸리티 함수 생성
- [ ] 대시보드에 n8n 액션 버튼 추가
- [ ] 리포트 생성 버튼
- [ ] 테스트 알림 버튼

### 선택 구현
- [ ] 토스트 알림 시스템
- [ ] 키보드 단축키
- [ ] 다크/라이트 테마 토글 (미래 확장용)

---

## 📦 설치해야 할 패키지

```bash
npm install @supabase/supabase-js @tanstack/react-query zustand framer-motion recharts lucide-react date-fns react-router-dom clsx
```

---

이 프롬프트를 v0.dev에 전달하여 대시보드를 구현해주세요.
한국어 UI를 사용합니다.

**주요 연동 서비스:**
- 🗄️ **Supabase**: 데이터베이스 + 실시간 구독
- 🤖 **n8n**: 워크플로우 자동화 + 알림

