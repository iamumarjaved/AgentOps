import { useEffect, useState } from 'react'
import { api, type Run } from '../api/client'

export default function Experiments() {
  const [runs, setRuns] = useState<Run[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.listRuns({ status: 'completed', limit: 100 })
      .then(setRuns)
      .catch(() => setRuns([]))
      .finally(() => setLoading(false))
  }, [])

  // Group runs by variant
  const variantGroups = runs.reduce((acc, run) => {
    const variant = run.variant || 'default'
    if (!acc[variant]) acc[variant] = []
    acc[variant].push(run)
    return acc
  }, {} as Record<string, Run[]>)

  const variantStats = Object.entries(variantGroups).map(([variant, variantRuns]) => ({
    variant,
    count: variantRuns.length,
    avgTokens: variantRuns.reduce((s, r) => s + r.total_tokens, 0) / variantRuns.length,
    avgCost: variantRuns.reduce((s, r) => s + r.total_cost_usd, 0) / variantRuns.length,
    avgLatency: variantRuns.reduce((s, r) => s + r.total_latency_seconds, 0) / variantRuns.length,
  }))

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-gray-400">Loading...</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Experiments</h1>

      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h2 className="text-sm font-semibold text-gray-500 mb-4">MLflow Integration</h2>
        <p className="text-sm text-gray-600 mb-4">
          View detailed experiment tracking, parameter comparison, and artifact inspection in the MLflow UI.
        </p>
        <a
          href="http://localhost:5000"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition"
        >
          Open MLflow UI
        </a>
      </div>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="text-sm font-semibold text-gray-500">Variant Comparison</h2>
        </div>
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Variant</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Runs</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Tokens</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Cost</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Latency</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {variantStats.length === 0 ? (
              <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-400">No completed runs</td></tr>
            ) : (
              variantStats.map((stat) => (
                <tr key={stat.variant} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium">{stat.variant}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{stat.count}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{Math.round(stat.avgTokens).toLocaleString()}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">${stat.avgCost.toFixed(4)}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{stat.avgLatency.toFixed(1)}s</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
