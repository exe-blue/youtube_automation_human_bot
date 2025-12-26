import { useQuery } from '@tanstack/react-query'
import { 
  Smartphone, 
  Wifi, 
  WifiOff, 
  Battery, 
  Thermometer,
  Cpu,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { deviceApi } from '../lib/api'

export default function Devices() {
  const { data, isLoading } = useQuery({
    queryKey: ['devices'],
    queryFn: () => deviceApi.list(),
    refetchInterval: 5000, // 5초마다 갱신
  })

  const devices = data?.data?.devices || []
  const stats = data?.data || { total: 0, idle: 0, busy: 0, offline: 0, error: 0 }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 헤더 */}
      <div>
        <h1 className="text-3xl font-bold">기기 관리</h1>
        <p className="text-gray-400 mt-2">연결된 Android 기기를 관리합니다</p>
      </div>

      {/* 상태 요약 */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-dark-700 rounded-lg p-4 border border-dark-600">
          <p className="text-sm text-gray-400">전체</p>
          <p className="text-2xl font-bold">{stats.total}</p>
        </div>
        <div className="bg-accent-emerald/10 rounded-lg p-4 border border-accent-emerald/30">
          <p className="text-sm text-accent-emerald">대기 중</p>
          <p className="text-2xl font-bold text-accent-emerald">{stats.idle}</p>
        </div>
        <div className="bg-accent-cyan/10 rounded-lg p-4 border border-accent-cyan/30">
          <p className="text-sm text-accent-cyan">작업 중</p>
          <p className="text-2xl font-bold text-accent-cyan">{stats.busy}</p>
        </div>
        <div className="bg-gray-500/10 rounded-lg p-4 border border-gray-500/30">
          <p className="text-sm text-gray-400">오프라인</p>
          <p className="text-2xl font-bold text-gray-400">{stats.offline}</p>
        </div>
        <div className="bg-red-500/10 rounded-lg p-4 border border-red-500/30">
          <p className="text-sm text-red-400">오류</p>
          <p className="text-2xl font-bold text-red-400">{stats.error}</p>
        </div>
      </div>

      {/* 기기 그리드 */}
      {isLoading ? (
        <div className="text-center text-gray-400 py-8">로딩 중...</div>
      ) : devices.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          연결된 기기가 없습니다
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {devices.map((device: any) => (
            <DeviceCard key={device.id} device={device} />
          ))}
        </div>
      )}
    </div>
  )
}

function DeviceCard({ device }: { device: any }) {
  const statusColors = {
    idle: 'border-accent-emerald/30 bg-accent-emerald/5',
    busy: 'border-accent-cyan/30 bg-accent-cyan/5',
    offline: 'border-gray-600 bg-dark-800',
    error: 'border-red-500/30 bg-red-500/5',
    overheat: 'border-red-500/30 bg-red-500/5',
  }

  const statusIcons = {
    idle: <Wifi className="text-accent-emerald" size={20} />,
    busy: <Wifi className="text-accent-cyan animate-pulse" size={20} />,
    offline: <WifiOff className="text-gray-500" size={20} />,
    error: <XCircle className="text-red-400" size={20} />,
    overheat: <Thermometer className="text-red-400 animate-pulse" size={20} />,
  }

  const statusLabels = {
    idle: '대기 중',
    busy: '작업 중',
    offline: '오프라인',
    error: '오류',
    overheat: '과열',
  }

  return (
    <div className={`rounded-xl p-5 border ${statusColors[device.status as keyof typeof statusColors] || statusColors.offline}`}>
      {/* 헤더 */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-dark-600 rounded-lg">
            <Smartphone size={24} />
          </div>
          <div>
            <p className="font-medium">{device.model || 'Android Device'}</p>
            <p className="text-xs text-gray-500">{device.serial_number}</p>
          </div>
        </div>
        {statusIcons[device.status as keyof typeof statusIcons]}
      </div>

      {/* 상태 배지 */}
      <div className="flex items-center gap-2 mb-4">
        <span className={`text-xs px-2 py-1 rounded ${
          device.status === 'idle' ? 'bg-accent-emerald/20 text-accent-emerald' :
          device.status === 'busy' ? 'bg-accent-cyan/20 text-accent-cyan' :
          device.status === 'offline' ? 'bg-gray-500/20 text-gray-400' :
          'bg-red-500/20 text-red-400'
        }`}>
          {statusLabels[device.status as keyof typeof statusLabels] || device.status}
        </span>
        <span className="text-xs text-gray-500">PC: {device.pc_id}</span>
      </div>

      {/* 헬스 정보 */}
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="flex items-center gap-2">
          <Battery size={16} className={
            device.battery_level > 50 ? 'text-accent-emerald' :
            device.battery_level > 20 ? 'text-accent-amber' :
            'text-red-400'
          } />
          <span className="text-gray-400">
            {device.battery_level != null ? `${device.battery_level}%` : '-'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Thermometer size={16} className={
            device.battery_temp > 60 ? 'text-red-400' :
            device.battery_temp > 45 ? 'text-accent-amber' :
            'text-accent-emerald'
          } />
          <span className="text-gray-400">
            {device.battery_temp != null ? `${device.battery_temp}°C` : '-'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Cpu size={16} className="text-accent-purple" />
          <span className="text-gray-400">
            {device.cpu_usage != null ? `${device.cpu_usage}%` : '-'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <CheckCircle size={16} className="text-accent-cyan" />
          <span className="text-gray-400">
            {device.total_tasks || 0}건 처리
          </span>
        </div>
      </div>

      {/* 성공률 */}
      {device.total_tasks > 0 && (
        <div className="mt-4 pt-4 border-t border-dark-600">
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>성공률</span>
            <span>{Math.round((device.success_tasks / device.total_tasks) * 100)}%</span>
          </div>
          <div className="h-1.5 bg-dark-600 rounded-full overflow-hidden">
            <div 
              className="h-full bg-accent-emerald rounded-full"
              style={{ width: `${(device.success_tasks / device.total_tasks) * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}

