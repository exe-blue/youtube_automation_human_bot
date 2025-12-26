import { Outlet, NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Video, 
  Smartphone, 
  ListTodo, 
  Brain,
  BarChart3,
  Settings
} from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { path: '/', icon: LayoutDashboard, label: '대시보드' },
  { path: '/videos', icon: Video, label: '영상 관리' },
  { path: '/devices', icon: Smartphone, label: '기기 관리' },
  { path: '/tasks', icon: ListTodo, label: '작업 큐' },
  { path: '/patterns', icon: Brain, label: '패턴 시뮬레이터' },
  { path: '/stats', icon: BarChart3, label: '통계' },
]

export default function Layout() {
  return (
    <div className="flex min-h-screen">
      {/* 사이드바 */}
      <aside className="w-64 bg-dark-800 border-r border-dark-600 flex flex-col">
        {/* 로고 */}
        <div className="p-6 border-b border-dark-600">
          <h1 className="text-2xl font-bold gradient-text">
            YT Automation
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            휴먼 패턴 시뮬레이션
          </p>
        </div>

        {/* 네비게이션 */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map(({ path, icon: Icon, label }) => (
              <li key={path}>
                <NavLink
                  to={path}
                  className={({ isActive }) =>
                    clsx(
                      'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                      isActive
                        ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                        : 'text-gray-400 hover:text-white hover:bg-dark-700'
                    )
                  }
                >
                  <Icon size={20} />
                  <span>{label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* 하단 설정 */}
        <div className="p-4 border-t border-dark-600">
          <button className="flex items-center gap-3 px-4 py-3 w-full text-gray-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors">
            <Settings size={20} />
            <span>설정</span>
          </button>
        </div>
      </aside>

      {/* 메인 콘텐츠 */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

