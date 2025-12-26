import { useQuery } from '@tanstack/react-query'
import { Clock, Play, CheckCircle, XCircle, Pause } from 'lucide-react'
import { taskApi } from '../lib/api'
import { formatDistanceToNow } from 'date-fns'
import { ko } from 'date-fns/locale'

export default function Tasks() {
  const { data, isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => taskApi.list({ limit: 100 }),
    refetchInterval: 5000,
  })

  const tasks = data?.data?.tasks || []
  const stats = data?.data || { total: 0, queued: 0, running: 0, completed: 0, failed: 0 }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 헤더 */}
      <div>
        <h1 className="text-3xl font-bold">작업 큐</h1>
        <p className="text-gray-400 mt-2">시청 작업 대기열을 관리합니다</p>
      </div>

      {/* 상태 요약 */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-dark-700 rounded-lg p-4 border border-dark-600">
          <p className="text-sm text-gray-400">전체</p>
          <p className="text-2xl font-bold">{stats.total}</p>
        </div>
        <div className="bg-gray-500/10 rounded-lg p-4 border border-gray-500/30">
          <div className="flex items-center gap-2">
            <Clock size={16} className="text-gray-400" />
            <p className="text-sm text-gray-400">대기</p>
          </div>
          <p className="text-2xl font-bold text-gray-400">{stats.queued}</p>
        </div>
        <div className="bg-accent-cyan/10 rounded-lg p-4 border border-accent-cyan/30">
          <div className="flex items-center gap-2">
            <Play size={16} className="text-accent-cyan" />
            <p className="text-sm text-accent-cyan">실행 중</p>
          </div>
          <p className="text-2xl font-bold text-accent-cyan">{stats.running}</p>
        </div>
        <div className="bg-accent-emerald/10 rounded-lg p-4 border border-accent-emerald/30">
          <div className="flex items-center gap-2">
            <CheckCircle size={16} className="text-accent-emerald" />
            <p className="text-sm text-accent-emerald">완료</p>
          </div>
          <p className="text-2xl font-bold text-accent-emerald">{stats.completed}</p>
        </div>
        <div className="bg-red-500/10 rounded-lg p-4 border border-red-500/30">
          <div className="flex items-center gap-2">
            <XCircle size={16} className="text-red-400" />
            <p className="text-sm text-red-400">실패</p>
          </div>
          <p className="text-2xl font-bold text-red-400">{stats.failed}</p>
        </div>
      </div>

      {/* 작업 테이블 */}
      <div className="bg-dark-700 rounded-xl border border-dark-600 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-400">로딩 중...</div>
        ) : tasks.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            대기 중인 작업이 없습니다
          </div>
        ) : (
          <table>
            <thead>
              <tr className="border-b border-dark-600">
                <th>상태</th>
                <th>영상 ID</th>
                <th>기기</th>
                <th>우선순위</th>
                <th>시간</th>
                <th>재시도</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task: any) => (
                <tr key={task.id}>
                  <td>
                    <TaskStatusBadge status={task.status} />
                  </td>
                  <td>
                    <span className="text-sm font-mono text-gray-400">
                      {task.video_id?.slice(0, 8)}...
                    </span>
                  </td>
                  <td>
                    {task.device_id ? (
                      <span className="text-sm font-mono">
                        {task.device_id.slice(0, 8)}...
                      </span>
                    ) : (
                      <span className="text-gray-500">미할당</span>
                    )}
                  </td>
                  <td>
                    <span className={`px-2 py-1 rounded text-xs ${
                      task.priority >= 8 ? 'bg-red-500/20 text-red-400' :
                      task.priority >= 5 ? 'bg-amber-500/20 text-amber-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {task.priority}
                    </span>
                  </td>
                  <td className="text-sm text-gray-400">
                    {task.queued_at && formatDistanceToNow(new Date(task.queued_at), { 
                      addSuffix: true,
                      locale: ko 
                    })}
                  </td>
                  <td>
                    {task.retry_count > 0 && (
                      <span className="text-xs text-red-400">
                        {task.retry_count}/{task.max_retries}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

function TaskStatusBadge({ status }: { status: string }) {
  const configs = {
    queued: { icon: Clock, color: 'bg-gray-500/20 text-gray-400', label: '대기' },
    assigned: { icon: Pause, color: 'bg-amber-500/20 text-amber-400', label: '할당됨' },
    running: { icon: Play, color: 'bg-accent-cyan/20 text-accent-cyan', label: '실행 중' },
    completed: { icon: CheckCircle, color: 'bg-accent-emerald/20 text-accent-emerald', label: '완료' },
    failed: { icon: XCircle, color: 'bg-red-500/20 text-red-400', label: '실패' },
    cancelled: { icon: XCircle, color: 'bg-gray-500/20 text-gray-400', label: '취소' },
  }

  const config = configs[status as keyof typeof configs] || configs.queued
  const Icon = config.icon

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs ${config.color}`}>
      <Icon size={14} />
      {config.label}
    </span>
  )
}

