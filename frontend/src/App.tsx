import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Runs from './pages/Runs'
import RunDetail from './pages/RunDetail'
import Metrics from './pages/Metrics'
import Evaluations from './pages/Evaluations'
import Guardrails from './pages/Guardrails'
import Experiments from './pages/Experiments'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/runs" element={<Runs />} />
        <Route path="/runs/:id" element={<RunDetail />} />
        <Route path="/metrics" element={<Metrics />} />
        <Route path="/evaluations" element={<Evaluations />} />
        <Route path="/guardrails" element={<Guardrails />} />
        <Route path="/experiments" element={<Experiments />} />
      </Route>
    </Routes>
  )
}
