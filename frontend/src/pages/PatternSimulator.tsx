import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { 
  Brain, 
  Play, 
  Clock, 
  ThumbsUp, 
  MessageSquare,
  MousePointer,
  RefreshCw
} from 'lucide-react'
import { patternApi } from '../lib/api'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

export default function PatternSimulator() {
  const [videoDuration, setVideoDuration] = useState(300)
  const [samples, setSamples] = useState(1000)
  const [pattern, setPattern] = useState<any>(null)
  const [distribution, setDistribution] = useState<any>(null)

  const generateMutation = useMutation({
    mutationFn: () => patternApi.generate(videoDuration),
    onSuccess: (res) => setPattern(res.data),
  })

  const distributionMutation = useMutation({
    mutationFn: () => patternApi.watchDistribution(videoDuration, samples),
    onSuccess: (res) => setDistribution(res.data),
  })

  const COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#8b5cf6']

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 헤더 */}
      <div>
        <h1 className="text-3xl font-bold">패턴 시뮬레이터</h1>
        <p className="text-gray-400 mt-2">
          PDF 문서 기반 휴먼 패턴을 시뮬레이션합니다
        </p>
      </div>

      {/* 설정 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 단일 패턴 생성 */}
        <div className="bg-dark-700 rounded-xl p-6 border border-dark-600">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="text-primary-400" />
            <h2 className="text-lg font-semibold">단일 패턴 생성</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">
                영상 길이 (초)
              </label>
              <input
                type="number"
                value={videoDuration}
                onChange={(e) => setVideoDuration(parseInt(e.target.value) || 0)}
                min={1}
                className="w-full"
              />
            </div>
            
            <button
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {generateMutation.isPending ? (
                <RefreshCw className="animate-spin" size={18} />
              ) : (
                <Play size={18} />
              )}
              패턴 생성
            </button>
          </div>

          {/* 생성된 패턴 결과 */}
          {pattern && (
            <div className="mt-6 space-y-4">
              <h3 className="font-medium text-accent-cyan">생성된 패턴</h3>
              
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-dark-600 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
                    <Clock size={14} />
                    시청 시간
                  </div>
                  <p className="text-xl font-bold">
                    {pattern.pattern?.watch?.watch_time}초
                  </p>
                  <p className="text-xs text-gray-500">
                    ({pattern.pattern?.watch?.watch_percent}%)
                  </p>
                </div>
                
                <div className="bg-dark-600 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
                    <MousePointer size={14} />
                    Seek
                  </div>
                  <p className="text-xl font-bold">
                    {pattern.pattern?.watch?.seek_count || 0}회
                  </p>
                </div>
                
                <div className="bg-dark-600 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
                    <ThumbsUp size={14} />
                    좋아요
                  </div>
                  <p className={`text-xl font-bold ${
                    pattern.pattern?.interaction?.should_like ? 'text-accent-cyan' : 'text-gray-500'
                  }`}>
                    {pattern.pattern?.interaction?.should_like ? 'Yes' : 'No'}
                  </p>
                  {pattern.pattern?.interaction?.like_timing && (
                    <p className="text-xs text-gray-500">
                      @ {pattern.pattern.interaction.like_timing}초
                    </p>
                  )}
                </div>
                
                <div className="bg-dark-600 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
                    <MessageSquare size={14} />
                    댓글
                  </div>
                  <p className={`text-xl font-bold ${
                    pattern.pattern?.interaction?.should_comment ? 'text-accent-purple' : 'text-gray-500'
                  }`}>
                    {pattern.pattern?.interaction?.should_comment ? 'Yes' : 'No'}
                  </p>
                </div>
              </div>

              {/* 추천 액션 */}
              {pattern.recommended_actions?.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm text-gray-400 mb-2">추천 액션</h4>
                  <ul className="space-y-1">
                    {pattern.recommended_actions.map((action: string, i: number) => (
                      <li key={i} className="text-sm text-accent-emerald">
                        • {action}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* 분포 시뮬레이션 */}
        <div className="bg-dark-700 rounded-xl p-6 border border-dark-600">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="text-accent-purple" />
            <h2 className="text-lg font-semibold">시청 시간 분포 시뮬레이션</h2>
          </div>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  영상 길이 (초)
                </label>
                <input
                  type="number"
                  value={videoDuration}
                  onChange={(e) => setVideoDuration(parseInt(e.target.value) || 0)}
                  min={1}
                  className="w-full"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  샘플 수
                </label>
                <input
                  type="number"
                  value={samples}
                  onChange={(e) => setSamples(parseInt(e.target.value) || 1000)}
                  min={100}
                  max={10000}
                  className="w-full"
                />
              </div>
            </div>
            
            <button
              onClick={() => distributionMutation.mutate()}
              disabled={distributionMutation.isPending}
              className="btn-secondary w-full flex items-center justify-center gap-2"
            >
              {distributionMutation.isPending ? (
                <RefreshCw className="animate-spin" size={18} />
              ) : (
                <Brain size={18} />
              )}
              분포 시뮬레이션
            </button>
          </div>

          {/* 분포 결과 */}
          {distribution && (
            <div className="mt-6">
              <h3 className="font-medium text-accent-purple mb-4">
                시청 시간 분포 (Beta 분포)
              </h3>
              
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={Object.entries(distribution.distribution).map(([name, value]) => ({
                        name,
                        value: Math.round((value as number) * 100)
                      }))}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}%`}
                    >
                      {Object.keys(distribution.distribution).map((_, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={COLORS[index % COLORS.length]} 
                        />
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

              {/* 분포 테이블 */}
              <div className="mt-4 space-y-2">
                {Object.entries(distribution.distribution).map(([range, value], i) => (
                  <div key={range} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded"
                        style={{ backgroundColor: COLORS[i % COLORS.length] }}
                      />
                      <span className="text-sm text-gray-400">{range}</span>
                    </div>
                    <span className="text-sm font-mono">
                      {(Math.round((value as number) * 1000) / 10)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* PDF 문서 설명 */}
      <div className="bg-dark-700 rounded-xl p-6 border border-dark-600">
        <h2 className="text-lg font-semibold mb-4">휴먼 패턴 알고리즘</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
          <div className="bg-dark-600 rounded-lg p-4">
            <h3 className="font-medium text-accent-cyan mb-2">시청 시간 (Beta 분포)</h3>
            <p className="text-gray-400">
              α=2, β=5 파라미터로 초반 이탈이 많은 Long-tail 분포 생성.
              실제 YouTube 사용자 데이터 기반.
            </p>
          </div>
          <div className="bg-dark-600 rounded-lg p-4">
            <h3 className="font-medium text-accent-purple mb-2">좋아요 타이밍</h3>
            <p className="text-gray-400">
              즉시 2%, 중간 35%, 완료 직후 45%, 지연 18%.
              시청 시간 대비 자연스러운 분포.
            </p>
          </div>
          <div className="bg-dark-600 rounded-lg p-4">
            <h3 className="font-medium text-accent-amber mb-2">터치 패턴</h3>
            <p className="text-gray-400">
              정규분포 오프셋으로 중심에서 약간 벗어난 터치.
              지속 시간 50-200ms 변화.
            </p>
          </div>
          <div className="bg-dark-600 rounded-lg p-4">
            <h3 className="font-medium text-accent-emerald mb-2">스와이프</h3>
            <p className="text-gray-400">
              Ease-in-out (Smoothstep) 곡선으로 자연스러운 가속/감속.
              노이즈 추가로 직선 회피.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

