# n8n 워크플로우 통합 가이드

## 📋 개요

**n8n**은 오픈소스 워크플로우 자동화 도구로, YouTube 자동화 시스템과 연동하여 다음 기능을 자동화할 수 있습니다:

### n8n 활용 사례
- ✅ **작업 스케줄링**: 특정 시간에 자동으로 작업 생성
- ✅ **알림 시스템**: 작업 완료/실패 시 Slack/Discord/Telegram 알림
- ✅ **기기 모니터링**: 기기 오프라인/과열 감지 시 알림
- ✅ **데이터 동기화**: 외부 서비스와 데이터 연동
- ✅ **리포트 생성**: 일별/주별 통계 리포트 자동 생성
- ✅ **영상 자동 등록**: YouTube API 연동으로 영상 자동 수집

---

## 🚀 1. n8n 설치 및 설정

### Option A: n8n Cloud (권장 - 빠른 시작)

1. [n8n.io](https://n8n.io) 접속
2. **Start Free** 클릭
3. 계정 생성 후 워크스페이스 생성
4. 바로 워크플로우 생성 가능

### Option B: Self-hosted (Docker)

```yaml
# docker-compose.yml에 추가
services:
  n8n:
    image: n8nio/n8n
    container_name: n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your_secure_password
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=Asia/Seoul
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

```bash
# 실행
docker-compose up -d n8n

# 접속: http://localhost:5678
```

### Option C: npm 설치

```bash
npm install -g n8n
n8n start
```

---

## 🔌 2. Supabase 연동 설정

### n8n에서 Supabase Credential 생성

1. **Settings > Credentials > Add Credential**
2. **Supabase** 검색 및 선택
3. 정보 입력:
   - **Host**: `https://xxxxxxxxxxxxx.supabase.co`
   - **Service Role Key**: `eyJhbGciOiJIUzI1NiIs...` (service_role key 사용)

### PostgreSQL 직접 연결 (대안)

1. **Postgres** Credential 추가
2. 정보 입력:
   - **Host**: `db.xxxxxxxxxxxxx.supabase.co`
   - **Database**: `postgres`
   - **User**: `postgres`
   - **Password**: 프로젝트 비밀번호
   - **Port**: `5432`
   - **SSL**: `Allow`

---

## 📊 3. 핵심 워크플로우

### 워크플로우 1: 작업 완료 알림 (Slack/Discord)

```json
{
  "name": "작업 완료 알림",
  "nodes": [
    {
      "name": "Supabase Trigger",
      "type": "n8n-nodes-base.supabaseTrigger",
      "parameters": {
        "table": "tasks",
        "event": "UPDATE"
      }
    },
    {
      "name": "Filter Completed",
      "type": "n8n-nodes-base.filter",
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.new.status }}",
              "operation": "equals",
              "value2": "completed"
            }
          ]
        }
      }
    },
    {
      "name": "Slack",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#youtube-automation",
        "text": "✅ 작업 완료!\n- Task ID: {{ $json.new.id }}\n- Video ID: {{ $json.new.video_id }}"
      }
    }
  ]
}
```

**수동 설정 방법:**

1. **Supabase Trigger** 노드 추가
   - Table: `tasks`
   - Event: `UPDATE`

2. **IF** 노드 추가 (필터)
   - Condition: `{{ $json.new.status }}` equals `completed`

3. **Slack** 노드 추가
   - Channel: `#youtube-automation`
   - Message:
   ```
   ✅ 작업 완료!
   - Task ID: {{ $json.new.id }}
   - Video ID: {{ $json.new.video_id }}
   - 완료 시간: {{ $json.new.completed_at }}
   ```

---

### 워크플로우 2: 기기 과열 알림

```
[Supabase Trigger: devices UPDATE]
        ↓
[IF: battery_temp > 50]
        ↓
[Slack/Discord: 🔥 기기 과열 경고!]
        ↓
[Supabase: Update device status to 'overheat']
```

**노드 설정:**

1. **Supabase Trigger**
   - Table: `devices`
   - Event: `UPDATE`

2. **IF 노드**
   ```javascript
   {{ $json.new.battery_temp > 50 }}
   ```

3. **Slack 노드**
   ```
   🔥 기기 과열 경고!
   - 기기: {{ $json.new.model }} ({{ $json.new.serial_number }})
   - 온도: {{ $json.new.battery_temp }}°C
   - PC: {{ $json.new.pc_id }}
   
   자동으로 작업이 중단됩니다.
   ```

4. **Supabase 노드** (Update)
   - Table: `devices`
   - Operation: `Update`
   - Filter: `id` = `{{ $json.new.id }}`
   - Fields: `status` = `overheat`

---

### 워크플로우 3: 일일 통계 리포트

```
[Schedule Trigger: 매일 오후 6시]
        ↓
[Supabase: Select from daily_stats]
        ↓
[Code: 리포트 포맷팅]
        ↓
[Slack/Email: 일일 리포트 전송]
```

**Schedule Trigger 설정:**
- Mode: `Every Day`
- Hour: `18`
- Minute: `0`
- Timezone: `Asia/Seoul`

**Supabase Query:**
```sql
SELECT * FROM daily_stats 
WHERE date = CURRENT_DATE
```

**Code 노드 (리포트 포맷팅):**
```javascript
const stats = $input.first().json;

const report = `
📊 *일일 YouTube 자동화 리포트*
━━━━━━━━━━━━━━━━━━━━
📅 날짜: ${stats.date}

📈 *작업 현황*
• 완료된 작업: ${stats.total_results}건
• 총 시청 시간: ${Math.floor(stats.total_watch_time / 60)}분
• 평균 시청률: ${stats.avg_watch_percent}%

💬 *인터랙션*
• 좋아요: ${stats.likes}개
• 댓글: ${stats.comments}개
━━━━━━━━━━━━━━━━━━━━
`;

return [{ json: { report } }];
```

---

### 워크플로우 4: 영상 자동 등록 (YouTube API)

```
[Schedule Trigger: 매시간]
        ↓
[HTTP Request: YouTube Data API]
        ↓
[Code: 영상 정보 추출]
        ↓
[Supabase: Insert into videos]
        ↓
[Supabase: Create tasks]
```

**YouTube API 설정:**

1. **HTTP Request 노드**
   - Method: `GET`
   - URL: `https://www.googleapis.com/youtube/v3/search`
   - Query Parameters:
     - `part`: `snippet`
     - `q`: `{{ $json.keyword }}`
     - `type`: `video`
     - `maxResults`: `5`
     - `key`: `YOUR_YOUTUBE_API_KEY`

2. **Code 노드:**
```javascript
const items = $input.first().json.items;

return items.map(item => ({
  json: {
    url: `https://youtube.com/watch?v=${item.id.videoId}`,
    title: item.snippet.title,
    keyword: $input.first().json.keyword,
    priority: 5
  }
}));
```

3. **Supabase 노드** (Insert)
   - Table: `videos`
   - Operation: `Insert`

---

### 워크플로우 5: 작업 자동 생성 스케줄러

```
[Schedule Trigger: 매 30분]
        ↓
[Supabase: pending 영상 조회]
        ↓
[Supabase: idle 기기 조회]
        ↓
[Code: 작업 매칭]
        ↓
[Supabase: Insert tasks]
```

**Code 노드 (작업 매칭):**
```javascript
const videos = $('Supabase - Videos').all();
const devices = $('Supabase - Devices').all();

const tasks = [];
const idleDevices = devices.filter(d => d.json.status === 'idle');

videos.forEach((video, index) => {
  if (index < idleDevices.length) {
    tasks.push({
      json: {
        video_id: video.json.id,
        device_id: idleDevices[index].json.id,
        priority: video.json.priority,
        status: 'assigned'
      }
    });
  }
});

return tasks;
```

---

## 🔗 4. 프론트엔드 n8n 웹훅 연동

### 웹훅 URL 설정

n8n에서 **Webhook** 노드 생성 시 URL이 생성됩니다:
```
https://your-n8n.com/webhook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 프론트엔드에서 웹훅 호출

```typescript
// frontend/src/lib/n8n.ts

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

  // 긴급 알림
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

### 대시보드에 n8n 버튼 추가

```tsx
// frontend/src/components/N8nActions.tsx
import { useState } from 'react'
import { Zap, Bell, FileText } from 'lucide-react'
import { n8nWebhooks } from '../lib/n8n'

export function N8nActions() {
  const [loading, setLoading] = useState<string | null>(null)

  const handleAction = async (action: string, fn: () => Promise<void>) => {
    setLoading(action)
    try {
      await fn()
      // 성공 토스트
    } catch (error) {
      // 에러 토스트
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="flex gap-2">
      <button
        onClick={() => handleAction('report', n8nWebhooks.requestDailyReport)}
        disabled={loading === 'report'}
        className="btn-secondary flex items-center gap-2"
      >
        <FileText size={16} />
        리포트 생성
      </button>
      
      <button
        onClick={() => handleAction('alert', () => 
          n8nWebhooks.sendAlert('info', '테스트 알림')
        )}
        disabled={loading === 'alert'}
        className="btn-secondary flex items-center gap-2"
      >
        <Bell size={16} />
        테스트 알림
      </button>
    </div>
  )
}
```

---

## 🎯 5. 추천 워크플로우 템플릿

### 필수 워크플로우

| 워크플로우 | 트리거 | 용도 |
|-----------|--------|------|
| **작업 완료 알림** | Supabase (tasks UPDATE) | 작업 완료 시 Slack 알림 |
| **작업 실패 알림** | Supabase (tasks UPDATE) | 작업 실패 시 긴급 알림 |
| **기기 과열 감지** | Supabase (devices UPDATE) | 과열 시 자동 중지 + 알림 |
| **기기 오프라인 감지** | Schedule (5분) | 하트비트 미수신 기기 감지 |
| **일일 리포트** | Schedule (매일 18:00) | 일일 통계 리포트 |

### 선택 워크플로우

| 워크플로우 | 트리거 | 용도 |
|-----------|--------|------|
| 영상 자동 등록 | Schedule / Webhook | YouTube API로 영상 수집 |
| 작업 자동 배정 | Schedule (30분) | idle 기기에 작업 자동 할당 |
| 주간 리포트 | Schedule (매주 월요일) | 주간 통계 요약 |
| 에러 집계 | Schedule (매시간) | 에러 패턴 분석 |
| 백업 알림 | Schedule (매일) | DB 백업 상태 확인 |

---

## 📱 6. 알림 채널 설정

### Slack 연동

1. [Slack API](https://api.slack.com/apps) 에서 앱 생성
2. **OAuth & Permissions > Bot Token Scopes** 추가:
   - `chat:write`
   - `channels:read`
3. 워크스페이스에 앱 설치
4. n8n에서 Slack Credential 추가

### Discord 연동

1. Discord 서버에서 **설정 > 연동 > 웹훅** 생성
2. 웹훅 URL 복사
3. n8n HTTP Request 노드 사용:
```javascript
// Discord Webhook Body
{
  "content": "{{ $json.message }}",
  "embeds": [{
    "title": "YouTube 자동화 알림",
    "color": 5814783,
    "fields": [
      { "name": "상태", "value": "{{ $json.status }}", "inline": true }
    ]
  }]
}
```

### Telegram 연동

1. @BotFather에서 봇 생성
2. Bot Token 획득
3. n8n Telegram 노드 사용

---

## 🔧 7. 환경 변수 정리

### 프론트엔드 (.env.local)

```env
# Supabase
VITE_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...

# n8n Webhooks
VITE_N8N_WEBHOOK_URL=https://your-n8n.com/webhook
VITE_N8N_TRIGGER_TASK=https://your-n8n.com/webhook/trigger-task
VITE_N8N_DAILY_REPORT=https://your-n8n.com/webhook/daily-report
VITE_N8N_ALERT=https://your-n8n.com/webhook/alert
```

### n8n 환경 변수 (Self-hosted)

```env
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=secure_password

# Supabase
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIs...

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL=#youtube-automation

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=-100...
```

---

## ✅ n8n 통합 체크리스트

### 설정
- [ ] n8n 설치 (Cloud 또는 Self-hosted)
- [ ] Supabase Credential 추가
- [ ] Slack/Discord/Telegram Credential 추가 (선택)

### 필수 워크플로우
- [ ] 작업 완료 알림 워크플로우
- [ ] 작업 실패 알림 워크플로우
- [ ] 기기 과열 감지 워크플로우
- [ ] 기기 오프라인 감지 워크플로우
- [ ] 일일 리포트 워크플로우

### 프론트엔드 연동
- [ ] 환경 변수 설정
- [ ] n8n 웹훅 유틸리티 함수 생성
- [ ] 대시보드에 n8n 액션 버튼 추가

### 테스트
- [ ] 웹훅 테스트 (Postman 또는 curl)
- [ ] 알림 채널 테스트
- [ ] 스케줄 트리거 테스트

---

## 📚 참고 자료

- [n8n 공식 문서](https://docs.n8n.io/)
- [n8n Supabase 노드](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.supabase/)
- [n8n 워크플로우 템플릿](https://n8n.io/workflows)
- [Supabase Realtime 문서](https://supabase.com/docs/guides/realtime)

