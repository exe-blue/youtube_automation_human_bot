import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Videos from './pages/Videos'
import Devices from './pages/Devices'
import Tasks from './pages/Tasks'
import PatternSimulator from './pages/PatternSimulator'
import Stats from './pages/Stats'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="videos" element={<Videos />} />
          <Route path="devices" element={<Devices />} />
          <Route path="tasks" element={<Tasks />} />
          <Route path="patterns" element={<PatternSimulator />} />
          <Route path="stats" element={<Stats />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App

