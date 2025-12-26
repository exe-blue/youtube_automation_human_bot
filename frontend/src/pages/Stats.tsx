import { useQuery } from '@tanstack/react-query'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { statsApi } from '../lib/api'

const COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e']

export default function Stats() {
  const { data, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: () => statsApi.get(),
  })

  const stats = data?.data?.aggregated || {}
  const daily = data?.data?.daily || []

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 헤더 */}
      <div>
        <h1 className="text-3xl font-bold">통계</h1>
        <p className="text-gray-400 mt-2">시스템 운영 통계를 확인합니다</p>
      </div>

      {/* 주요 지표 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="stat-card">
          <p className="stat-label">총 작업</p>
          <p className="stat-value text-white">{stats.total_tasks || 0}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">평균 시청률</p>
          <p className="stat-value text-accent-cyan">{stats.avg_watch_percent || 0}%</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">좋아요 비율</p>
          <p className="stat-value text-accent-purple">{stats.like_rate || 0}%</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">댓글 비율</p>
          <p className="stat-value text-accent-emerald">{stats.comment_rate || 0}%</p>
        </div>
      </div>

      {/* 차트 그리드 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 일별 작업 완료 */}
        <div className="bg-dark-700 rounded-xl p-6 border border-dark-600">
          <h3 className="text-lg font-semibold mb-4">일별 작업 완료</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={daily.slice().reverse()}>
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
                <Bar dataKey="tasks_completed" fill="#ef4444" name="완료" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 일별 인터랙션 */}
        <div className="bg-dark-700 rounded-xl p-6 border border-dark-600">
          <h3 className="text-lg font-semibold mb-4">일별 인터랙션</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={daily.slice().reverse()}>
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
                <Line 
                  type="monotone" 
                  dataKey="likes" 
                  stroke="#06b6d4" 
                  name="좋아요"
                  strokeWidth={2}
                />
                <Line 
                  type="monotone" 
                  dataKey="comments" 
                  stroke="#a855f7" 
                  name="댓글"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 검색 경로 분포 */}
        <div className="bg-dark-700 rounded-xl p-6 border border-dark-600">
          <h3 className="text-lg font-semibold mb-4">검색 경로 분포</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[
                    { name: '키워드 검색', value: stats.search_type_distribution?.[1] || 0 },
                    { name: '최근 1시간', value: stats.search_type_distribution?.[2] || 0 },
                    { name: '제목 검색', value: stats.search_type_distribution?.[3] || 0 },
                    { name: 'URL 직접', value: stats.search_type_distribution?.[4] || 0 },
                  ]}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label
                >
                  {COLORS.map((color, index) => (
                    <Cell key={`cell-${index}`} fill={color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1a1a24', 
                    border: '1px solid #32324a',
                    borderRadius: '8px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-4 mt-4 text-sm">
            {['키워드', '최근', '제목', 'URL'].map((label, i) => (
              <div key={label} className="flex items-center gap-1">
                <div className="w-3 h-3 rounded" style={{ backgroundColor: COLORS[i] }} />
                <span className="text-gray-400">{label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 일별 시청 시간 */}
        <div className="bg-dark-700 rounded-xl p-6 border border-dark-600">
          <h3 className="text-lg font-semibold mb-4">일별 총 시청 시간</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={daily.slice().reverse()}>
                <CartesianGrid strokeDasharray="3 3" stroke="#32324a" />
                <XAxis 
                  dataKey="date" 
                  stroke="#64748b"
                  tick={{ fill: '#64748b', fontSize: 12 }}
                />
                <YAxis 
                  stroke="#64748b" 
                  tick={{ fill: '#64748b', fontSize: 12 }}
                  tickFormatter={(value) => `${Math.floor(value / 60)}분`}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1a1a24', 
                    border: '1px solid #32324a',
                    borderRadius: '8px'
                  }}
                  formatter={(value: number) => [`${Math.floor(value / 60)}분 ${value % 60}초`, '시청 시간']}
                />
                <Bar dataKey="watch_time" fill="#10b981" name="시청 시간" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}

