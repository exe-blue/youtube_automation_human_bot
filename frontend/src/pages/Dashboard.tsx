import { useQuery } from '@tanstack/react-query'
import { 
  Video, 
  Smartphone, 
  CheckCircle, 
  AlertCircle,
  Clock,
  ThumbsUp,
  MessageSquare,
  Activity
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { api } from '../lib/api'

interface DashboardStats {
  videos: {
    total: number
    pending: number
    completed: number
  }
  devices: {
    total: number
    idle: number
    busy: number
    offline: number
  }
  stats: {
    aggregated: {
      total_tasks: number
      completed_tasks: number
      total_watch_time: number
      avg_watch_percent: number
      like_rate: number
      comment_rate: number
    }
    daily: Array<{
      date: string
      tasks_completed: number
      watch_time: number
      likes: number
    }>
  }
}

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/dashboard').then(res => res.data),
    refetchInterval: 10000, // 10초마다 갱신
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6">
        <p className="text-red-400">대시보드 데이터를 불러올 수 없습니다.</p>
        <p className="text-sm text-gray-500 mt-2">API 서버 연결을 확인해주세요.</p>
      </div>
    )
  }

  const stats = data?.stats?.aggregated || {}
  const daily = data?.stats?.daily || []
  const videos = data?.videos || {}
  const devices = data?.devices || {}

  return (
    <div className="space-y-8 animate-fade-in">
      {/* 헤더 */}
      <div>
        <h1 className="text-3xl font-bold">대시보드</h1>
        <p className="text-gray-400 mt-2">시스템 현황을 한눈에 확인하세요</p>
      </div>

      {/* 상단 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={Video}
          label="총 영상"
          value={videos.total || 0}
          subLabel={`대기 ${videos.pending || 0}개`}
          color="cyan"
        />
        <StatCard
          icon={Smartphone}
          label="활성 기기"
          value={`${devices.idle || 0}/${devices.total || 0}`}
          subLabel={`오프라인 ${devices.offline || 0}대`}
          color="green"
        />
        <StatCard
          icon={CheckCircle}
          label="완료된 작업"
          value={stats.completed_tasks || 0}
          subLabel={`평균 시청률 ${stats.avg_watch_percent || 0}%`}
          color="purple"
        />
        <StatCard
          icon={Clock}
          label="총 시청 시간"
          value={formatWatchTime(stats.total_watch_time || 0)}
          subLabel="누적 시청"
          color="amber"
        />
      </div>

      {/* 차트 섹션 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 일별 작업 완료 차트 */}
        <div className="bg-dark-700 rounded-xl p-6 border border-dark-600">
          <h3 className="text-lg font-semibold mb-4">일별 작업 완료</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={daily.slice().reverse()}>
                <defs>
                  <linearGradient id="colorTasks" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#32324a" />
                <XAxis 
                  dataKey="date" 
                  stroke="#64748b"
                  tick={{ fill: '#64748b', fontSize: 12 }}
                />
                <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1a1a24', 
                    border: '1px solid #32324a',
                    borderRadius: '8px'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="tasks_completed" 
                  stroke="#ef4444" 
                  fillOpacity={1}
                  fill="url(#colorTasks)"
                  name="완료 작업"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 인터랙션 통계 */}
        <div className="bg-dark-700 rounded-xl p-6 border border-dark-600">
          <h3 className="text-lg font-semibold mb-4">인터랙션 통계</h3>
          <div className="space-y-6">
            <div>
              <div className="flex justify-between mb-2">
                <span className="flex items-center gap-2 text-gray-400">
                  <ThumbsUp size={16} className="text-accent-cyan" />
                  좋아요 비율
                </span>
                <span className="font-semibold">{stats.like_rate || 0}%</span>
              </div>
              <div className="h-2 bg-dark-600 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-accent-cyan rounded-full transition-all duration-500"
                  style={{ width: `${stats.like_rate || 0}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <span className="flex items-center gap-2 text-gray-400">
                  <MessageSquare size={16} className="text-accent-purple" />
                  댓글 비율
                </span>
                <span className="font-semibold">{stats.comment_rate || 0}%</span>
              </div>
              <div className="h-2 bg-dark-600 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-accent-purple rounded-full transition-all duration-500"
                  style={{ width: `${stats.comment_rate || 0}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <span className="flex items-center gap-2 text-gray-400">
                  <Activity size={16} className="text-accent-emerald" />
                  평균 시청률
                </span>
                <span className="font-semibold">{stats.avg_watch_percent || 0}%</span>
              </div>
              <div className="h-2 bg-dark-600 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-accent-emerald rounded-full transition-all duration-500"
                  style={{ width: `${stats.avg_watch_percent || 0}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 기기 상태 */}
      <div className="bg-dark-700 rounded-xl p-6 border border-dark-600">
        <h3 className="text-lg font-semibold mb-4">기기 상태 분포</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <DeviceStatusCard label="대기 중" count={devices.idle || 0} color="green" />
          <DeviceStatusCard label="작업 중" count={devices.busy || 0} color="cyan" />
          <DeviceStatusCard label="오프라인" count={devices.offline || 0} color="gray" />
          <DeviceStatusCard label="오류" count={devices.error || 0} color="red" />
        </div>
      </div>
    </div>
  )
}

function StatCard({ 
  icon: Icon, 
  label, 
  value, 
  subLabel, 
  color 
}: { 
  icon: React.ElementType
  label: string
  value: string | number
  subLabel: string
  color: 'cyan' | 'green' | 'purple' | 'amber'
}) {
  const colorClasses = {
    cyan: 'text-accent-cyan bg-accent-cyan/10',
    green: 'text-accent-emerald bg-accent-emerald/10',
    purple: 'text-accent-purple bg-accent-purple/10',
    amber: 'text-accent-amber bg-accent-amber/10',
  }

  return (
    <div className="stat-card card-hover">
      <div className="flex items-start justify-between">
        <div>
          <p className="stat-label">{label}</p>
          <p className="stat-value mt-2">{value}</p>
          <p className="text-xs text-gray-500 mt-1">{subLabel}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  )
}

function DeviceStatusCard({ 
  label, 
  count, 
  color 
}: { 
  label: string
  count: number
  color: 'green' | 'cyan' | 'gray' | 'red'
}) {
  const colorClasses = {
    green: 'border-accent-emerald/30 bg-accent-emerald/10',
    cyan: 'border-accent-cyan/30 bg-accent-cyan/10',
    gray: 'border-gray-600 bg-gray-600/10',
    red: 'border-red-500/30 bg-red-500/10',
  }

  const dotClasses = {
    green: 'bg-accent-emerald',
    cyan: 'bg-accent-cyan',
    gray: 'bg-gray-500',
    red: 'bg-red-500',
  }

  return (
    <div className={`p-4 rounded-lg border ${colorClasses[color]}`}>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${dotClasses[color]} animate-pulse`} />
        <span className="text-sm text-gray-400">{label}</span>
      </div>
      <p className="text-2xl font-bold mt-2">{count}</p>
    </div>
  )
}

function formatWatchTime(seconds: number): string {
  if (seconds < 60) return `${seconds}초`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}분`
  return `${Math.floor(seconds / 3600)}시간`
}

