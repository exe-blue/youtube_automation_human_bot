import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, ExternalLink, Search } from 'lucide-react'
import { videoApi } from '../lib/api'

export default function Videos() {
  const [showAddModal, setShowAddModal] = useState(false)
  const [filter, setFilter] = useState<string>('')
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['videos', filter],
    queryFn: () => videoApi.list({ status: filter || undefined, limit: 100 }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => videoApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] })
    },
  })

  const videos = data?.data?.videos || []
  const stats = data?.data || { total: 0, pending: 0, processing: 0, completed: 0, error: 0 }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">영상 관리</h1>
          <p className="text-gray-400 mt-2">시청 대상 YouTube 영상을 관리합니다</p>
        </div>
        <button 
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          영상 추가
        </button>
      </div>

      {/* 상태 필터 */}
      <div className="flex gap-2">
        {[
          { value: '', label: '전체', count: stats.total },
          { value: 'pending', label: '대기', count: stats.pending },
          { value: 'processing', label: '처리중', count: stats.processing },
          { value: 'completed', label: '완료', count: stats.completed },
          { value: 'error', label: '오류', count: stats.error },
        ].map(({ value, label, count }) => (
          <button
            key={value}
            onClick={() => setFilter(value)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === value
                ? 'bg-primary-500 text-white'
                : 'bg-dark-700 text-gray-400 hover:bg-dark-600'
            }`}
          >
            {label} ({count})
          </button>
        ))}
      </div>

      {/* 영상 테이블 */}
      <div className="bg-dark-700 rounded-xl border border-dark-600 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-400">로딩 중...</div>
        ) : videos.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            등록된 영상이 없습니다
          </div>
        ) : (
          <table>
            <thead>
              <tr className="border-b border-dark-600">
                <th>제목</th>
                <th>키워드</th>
                <th>길이</th>
                <th>우선순위</th>
                <th>상태</th>
                <th>완료</th>
                <th>액션</th>
              </tr>
            </thead>
            <tbody>
              {videos.map((video: any) => (
                <tr key={video.id}>
                  <td>
                    <div className="flex items-center gap-2">
                      <span className="truncate max-w-xs">{video.title || '제목 없음'}</span>
                      {video.url && (
                        <a 
                          href={video.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-gray-400 hover:text-primary-400"
                        >
                          <ExternalLink size={16} />
                        </a>
                      )}
                    </div>
                  </td>
                  <td>
                    <span className="text-accent-cyan">{video.keyword || '-'}</span>
                  </td>
                  <td>{video.duration ? `${video.duration}초` : '-'}</td>
                  <td>
                    <span className={`px-2 py-1 rounded text-xs ${
                      video.priority >= 8 ? 'bg-red-500/20 text-red-400' :
                      video.priority >= 5 ? 'bg-amber-500/20 text-amber-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {video.priority}
                    </span>
                  </td>
                  <td>
                    <StatusBadge status={video.status} />
                  </td>
                  <td>{video.completed_count || 0}회</td>
                  <td>
                    <button
                      onClick={() => deleteMutation.mutate(video.id)}
                      className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* 영상 추가 모달 */}
      {showAddModal && (
        <AddVideoModal onClose={() => setShowAddModal(false)} />
      )}
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const styles = {
    pending: 'bg-gray-500/20 text-gray-400',
    processing: 'bg-accent-cyan/20 text-accent-cyan',
    completed: 'bg-accent-emerald/20 text-accent-emerald',
    error: 'bg-red-500/20 text-red-400',
  }
  
  const labels = {
    pending: '대기',
    processing: '처리중',
    completed: '완료',
    error: '오류',
  }

  return (
    <span className={`px-2 py-1 rounded text-xs ${styles[status as keyof typeof styles] || styles.pending}`}>
      {labels[status as keyof typeof labels] || status}
    </span>
  )
}

function AddVideoModal({ onClose }: { onClose: () => void }) {
  const [formData, setFormData] = useState({
    url: '',
    title: '',
    keyword: '',
    duration: 0,
    priority: 5,
  })
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (data: typeof formData) => videoApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] })
      onClose()
    },
  })

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-dark-700 rounded-xl p-6 w-full max-w-md border border-dark-600">
        <h2 className="text-xl font-bold mb-4">영상 추가</h2>
        
        <form onSubmit={(e) => {
          e.preventDefault()
          mutation.mutate(formData)
        }} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">YouTube URL</label>
            <input
              type="url"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              placeholder="https://www.youtube.com/watch?v=..."
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-400 mb-1">제목</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="영상 제목"
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-400 mb-1">검색 키워드</label>
            <input
              type="text"
              value={formData.keyword}
              onChange={(e) => setFormData({ ...formData, keyword: e.target.value })}
              placeholder="검색에 사용할 키워드"
              className="w-full"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">영상 길이 (초)</label>
              <input
                type="number"
                value={formData.duration}
                onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) || 0 })}
                placeholder="300"
                className="w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">우선순위 (1-10)</label>
              <input
                type="number"
                min={1}
                max={10}
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 5 })}
                className="w-full"
              />
            </div>
          </div>
          
          <div className="flex gap-2 justify-end mt-6">
            <button type="button" onClick={onClose} className="btn-secondary">
              취소
            </button>
            <button type="submit" className="btn-primary" disabled={mutation.isPending}>
              {mutation.isPending ? '추가 중...' : '추가'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

