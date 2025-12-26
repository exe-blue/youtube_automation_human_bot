# 대시보드 입력 폼 상세 정보

## 📝 1. 영상 등록 폼 (Videos)

### 입력 필드

| 필드 | DB 컬럼 | 타입 | 필수 | 기본값 | 설명 |
|------|---------|------|------|--------|------|
| YouTube URL | `url` | URL | ✅ | - | YouTube 영상 URL |
| 제목 | `title` | 텍스트 (500자) | ✅ | - | 영상 제목 (검색 매칭용) |
| 검색 키워드 | `keyword` | 텍스트 (255자) | ❌ | - | 검색에 사용할 키워드 |
| 영상 길이 | `duration` | 숫자 (초) | ❌ | 자동 추출 | 영상 길이 |
| 목표 시청 횟수 | `target_views` | 숫자 | ✅ | 1 | 몇 회 시청할지 |
| 우선순위 | `priority` | 1-10 | ❌ | 5 | 작업 우선순위 |
| 좋아요 확률 | `like_probability` | 0-1 | ❌ | 0.3 | 좋아요 확률 (30%) |
| 댓글 확률 | `comment_probability` | 0-1 | ❌ | 0.1 | 댓글 확률 (10%) |

### 폼 예시 (HTML)

```html
<form id="video-form">
  <!-- 필수 -->
  <div class="form-group">
    <label>YouTube URL *</label>
    <input type="url" name="url" required 
           placeholder="https://www.youtube.com/watch?v=..." />
  </div>
  
  <div class="form-group">
    <label>제목 *</label>
    <input type="text" name="title" required maxlength="500"
           placeholder="검색에서 찾을 영상 제목" />
  </div>
  
  <div class="form-group">
    <label>목표 시청 횟수 *</label>
    <input type="number" name="target_views" required min="1" value="100"
           placeholder="예: 100" />
    <small>이 영상을 몇 대의 기기로 시청할지</small>
  </div>
  
  <!-- 선택 -->
  <div class="form-group">
    <label>검색 키워드</label>
    <input type="text" name="keyword" maxlength="255"
           placeholder="YouTube에서 검색할 키워드" />
    <small>비워두면 제목으로 검색</small>
  </div>
  
  <div class="form-row">
    <div class="form-group">
      <label>영상 길이 (초)</label>
      <input type="number" name="duration" min="1"
             placeholder="자동 추출됨" />
    </div>
    
    <div class="form-group">
      <label>우선순위</label>
      <select name="priority">
        <option value="1">1 (낮음)</option>
        <option value="3">3</option>
        <option value="5" selected>5 (보통)</option>
        <option value="7">7</option>
        <option value="10">10 (긴급)</option>
      </select>
    </div>
  </div>
  
  <!-- 고급 설정 (접을 수 있음) -->
  <details>
    <summary>고급 설정</summary>
    
    <div class="form-row">
      <div class="form-group">
        <label>좋아요 확률</label>
        <input type="range" name="like_probability" min="0" max="1" step="0.1" value="0.3" />
        <output>30%</output>
      </div>
      
      <div class="form-group">
        <label>댓글 확률</label>
        <input type="range" name="comment_probability" min="0" max="1" step="0.1" value="0.1" />
        <output>10%</output>
      </div>
    </div>
  </details>
  
  <button type="submit">영상 등록</button>
</form>
```

### API 요청

```json
POST /videos
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "keyword": "rick astley never gonna",
  "duration": 213,
  "target_views": 100,
  "priority": 5,
  "like_probability": 0.3,
  "comment_probability": 0.1
}
```

---

## 📝 2. 캠페인 생성 폼 (Campaigns)

### 입력 필드

| 필드 | DB 컬럼 | 타입 | 필수 | 설명 |
|------|---------|------|------|------|
| 캠페인 이름 | `name` | 텍스트 | ✅ | 캠페인 식별 이름 |
| 설명 | `description` | 텍스트 | ❌ | 상세 설명 |
| 대상 영상 | `video_ids` | UUID[] | ✅ | 포함할 영상 목록 |
| 영상당 시청 횟수 | `tasks_per_video` | 숫자 | ✅ | 각 영상을 몇 회 시청 |
| 예약 시간 | `scheduled_at` | 날짜시간 | ❌ | 예약 실행 (즉시 실행이면 비움) |

### 폼 예시

```html
<form id="campaign-form">
  <div class="form-group">
    <label>캠페인 이름 *</label>
    <input type="text" name="name" required 
           placeholder="예: 12월 신규 영상 홍보" />
  </div>
  
  <div class="form-group">
    <label>설명</label>
    <textarea name="description" rows="3"
              placeholder="캠페인 목적 및 메모"></textarea>
  </div>
  
  <div class="form-group">
    <label>대상 영상 선택 *</label>
    <select name="video_ids" multiple required>
      <!-- 등록된 영상 목록 -->
      <option value="uuid-1">테스트 영상 1 (대기중)</option>
      <option value="uuid-2">테스트 영상 2 (대기중)</option>
    </select>
    <small>Ctrl+클릭으로 여러 개 선택</small>
  </div>
  
  <div class="form-group">
    <label>영상당 시청 횟수 *</label>
    <input type="number" name="tasks_per_video" required min="1" value="100" />
    <small>선택한 각 영상을 몇 대의 기기로 시청</small>
  </div>
  
  <div class="form-group">
    <label>총 작업 수</label>
    <output id="total-tasks">0개</output>
    <small>영상 수 × 시청 횟수</small>
  </div>
  
  <div class="form-group">
    <label>예약 실행</label>
    <input type="datetime-local" name="scheduled_at" />
    <small>비워두면 즉시 실행</small>
  </div>
  
  <div class="form-actions">
    <button type="button" onclick="saveDraft()">임시 저장</button>
    <button type="submit">캠페인 시작</button>
  </div>
</form>
```

### API 요청

```json
POST /campaigns
{
  "name": "12월 신규 영상 홍보",
  "description": "신규 업로드 영상 3개 홍보 캠페인",
  "video_ids": ["uuid-1", "uuid-2", "uuid-3"],
  "tasks_per_video": 100,
  "scheduled_at": null  // 즉시 실행
}

// 응답
{
  "id": "campaign-uuid",
  "name": "12월 신규 영상 홍보",
  "total_tasks": 300,  // 3개 영상 × 100회
  "status": "running"
}
```

---

## 📝 3. 대량 등록 폼 (Bulk Import)

### CSV 형식

```csv
url,title,keyword,duration,target_views,priority
https://youtube.com/watch?v=xxx1,영상 제목 1,키워드1,300,100,5
https://youtube.com/watch?v=xxx2,영상 제목 2,키워드2,600,50,8
https://youtube.com/watch?v=xxx3,영상 제목 3,키워드3,180,200,3
```

### 폼 예시

```html
<form id="bulk-import-form">
  <div class="form-group">
    <label>CSV 파일 업로드</label>
    <input type="file" name="csv_file" accept=".csv" />
    <small>형식: url, title, keyword, duration, target_views, priority</small>
  </div>
  
  <div class="form-group">
    <label>또는 직접 입력</label>
    <textarea name="csv_text" rows="10"
              placeholder="URL, 제목, 키워드, 길이, 목표횟수, 우선순위 (한 줄에 하나)"></textarea>
  </div>
  
  <!-- 미리보기 -->
  <div id="preview">
    <table>
      <thead>
        <tr><th>URL</th><th>제목</th><th>키워드</th><th>목표</th></tr>
      </thead>
      <tbody id="preview-body"></tbody>
    </table>
    <p>총 <strong id="preview-count">0</strong>개 영상</p>
  </div>
  
  <button type="submit">대량 등록</button>
</form>
```

### API 요청

```json
POST /videos/bulk
{
  "videos": [
    {"url": "...", "title": "...", "keyword": "...", "target_views": 100},
    {"url": "...", "title": "...", "keyword": "...", "target_views": 50}
  ]
}
```

---

## 📝 4. 댓글 템플릿 관리 폼

### 입력 필드

| 필드 | DB 컬럼 | 타입 | 설명 |
|------|---------|------|------|
| 카테고리 | `category` | 선택 | positive, question, emoji 등 |
| 내용 | `content` | 텍스트 | 댓글 내용 |
| 언어 | `language` | 선택 | ko, en, ja 등 |
| 가중치 | `weight` | 1-10 | 선택 확률 가중치 |

### 폼 예시

```html
<form id="comment-form">
  <div class="form-row">
    <div class="form-group">
      <label>카테고리</label>
      <select name="category">
        <option value="positive">긍정적</option>
        <option value="question">질문</option>
        <option value="emoji">이모지</option>
        <option value="general">일반</option>
      </select>
    </div>
    
    <div class="form-group">
      <label>언어</label>
      <select name="language">
        <option value="ko">한국어</option>
        <option value="en">영어</option>
        <option value="ja">일본어</option>
      </select>
    </div>
  </div>
  
  <div class="form-group">
    <label>댓글 내용 *</label>
    <textarea name="content" required rows="2"
              placeholder="좋은 영상이네요!"></textarea>
  </div>
  
  <div class="form-group">
    <label>가중치 (선택 확률)</label>
    <input type="range" name="weight" min="1" max="10" value="5" />
    <output>5</output>
    <small>높을수록 자주 선택됨</small>
  </div>
  
  <button type="submit">템플릿 추가</button>
</form>
```

---

## 📝 5. 기기 수동 등록 폼

### 입력 필드

| 필드 | DB 컬럼 | 타입 | 필수 | 설명 |
|------|---------|------|------|------|
| 시리얼 번호 | `serial_number` | 텍스트 | ✅ | ADB 시리얼 |
| PC ID | `pc_id` | 텍스트 | ✅ | 연결된 마스터 PC |
| 모델명 | `model` | 텍스트 | ❌ | Galaxy S21 등 |

### 폼 예시

```html
<form id="device-form">
  <div class="form-group">
    <label>시리얼 번호 *</label>
    <input type="text" name="serial_number" required 
           placeholder="ABC123456789" />
    <small>adb devices로 확인</small>
  </div>
  
  <div class="form-group">
    <label>마스터 PC *</label>
    <select name="pc_id" required>
      <option value="PC-001">PC-001 (온라인, 50대)</option>
      <option value="PC-002">PC-002 (오프라인)</option>
    </select>
  </div>
  
  <div class="form-group">
    <label>모델명</label>
    <input type="text" name="model" placeholder="Galaxy S21" />
  </div>
  
  <button type="submit">기기 등록</button>
</form>
```

---

## 🔄 폼 검증 규칙

### 영상 등록

```javascript
const videoValidation = {
  url: {
    required: true,
    pattern: /^https?:\/\/(www\.)?youtube\.com\/watch\?v=[\w-]{11}/,
    message: '유효한 YouTube URL을 입력하세요'
  },
  title: {
    required: true,
    minLength: 1,
    maxLength: 500,
    message: '제목은 1-500자 사이여야 합니다'
  },
  target_views: {
    required: true,
    min: 1,
    max: 10000,
    message: '목표 시청 횟수는 1-10000 사이여야 합니다'
  },
  priority: {
    min: 1,
    max: 10,
    default: 5
  },
  like_probability: {
    min: 0,
    max: 1,
    default: 0.3
  },
  comment_probability: {
    min: 0,
    max: 1,
    default: 0.1
  }
};
```

### 자동 추출

```javascript
// URL에서 YouTube ID 추출
function extractYouTubeId(url) {
  const match = url.match(/(?:v=|\/v\/|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
  return match ? match[1] : null;
}

// YouTube API로 메타데이터 추출 (선택)
async function fetchVideoMetadata(videoId) {
  // duration, title, channel_name 자동 채우기
}
```

---

## 📊 폼 → DB → API 매핑

### 영상 등록 흐름

```
[프론트엔드 폼]
      │
      │ POST /videos
      ▼
[API Gateway]
      │
      │ 검증 + youtube_video_id 추출
      ▼
[Video Service]
      │
      │ INSERT INTO videos
      ▼
[PostgreSQL]
      │
      │ youtube_video_id 중복 체크 (UNIQUE)
      ▼
[응답]
{
  "id": "uuid",
  "youtube_video_id": "dQw4w9WgXcQ",
  "status": "pending",
  "target_views": 100,
  "completed_count": 0
}
```

