import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import StatCard from '../components/StatCard'
import { api, type Run, type CostMetrics } from '../api/client'

export default function Dashboard() {
  const [runs, setRuns] = useState<Run[]>([])
  const [costMetrics, setCostMetrics] = useState<CostMetrics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.listRuns({ limit: 10 }).catch(() => []),
      api.getCostMetrics().catch(() => null),
    ]).then(([runsData, costData]) => {
      setRuns(runsData)
      setCostMetrics(costData)
      setLoading(false)
    })
  }, [])

  const completedCount = runs.filter((r) => r.status === 'completed').length
  const failedCount = runs.filter((r) => r.status === 'failed').length
  const totalTokens = runs.reduce((sum, r) => sum + r.total_tokens, 0)

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-gray-400">Loading...</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard title="Total Runs" value={runs.length} color="blue" />
        <StatCard title="Completed" value={completedCount} color="green" />
        <StatCard title="Failed" value={failedCount} color="red" />
        <StatCard
          title="Total Cost"
          value={`$${costMetrics?.total_cost_usd.toFixed(4) || '0.00'}`}
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-sm font-semibold text-gray-500 mb-4">Recent Runs</h2>
          <div className="space-y-3">
            {runs.slice(0, 5).map((run) => (
              <Link
                key={run.id}
                to={`/runs/${run.id}`}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition"
              >
                <div>
                  <p className="text-sm font-medium truncate max-w-xs">{run.topic}</p>
                  <p className="text-xs text-gray-400">{new Date(run.created_at).toLocaleString()}</p>
                </div>
                <span
                  className={`text-xs px-2 py-1 rounded-full font-medium ${
                    run.status === 'completed'
                      ? 'bg-green-100 text-green-700'
                      : run.status === 'failed'
                      ? 'bg-red-100 text-red-700'
                      : run.status === 'running'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {run.status}
                </span>
              </Link>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-sm font-semibold text-gray-500 mb-4">Quick Stats</h2>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Total Tokens</span>
              <span className="text-sm font-semibold">{totalTokens.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Avg Latency</span>
              <span className="text-sm font-semibold">
                {runs.length > 0
                  ? (runs.reduce((s, r) => s + r.total_latency_seconds, 0) / runs.length).toFixed(1)
                  : '0'}s
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Success Rate</span>
              <span className="text-sm font-semibold">
                {runs.length > 0 ? ((completedCount / runs.length) * 100).toFixed(0) : '0'}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
