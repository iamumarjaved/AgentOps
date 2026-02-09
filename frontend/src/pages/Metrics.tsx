import { useEffect, useState } from 'react'
import StatCard from '../components/StatCard'
import CostBreakdown from '../components/CostBreakdown'
import LatencyChart from '../components/LatencyChart'
import { api, type CostMetrics, type TokenMetrics, type LatencyMetrics as LatencyMetricsType } from '../api/client'

export default function Metrics() {
  const [cost, setCost] = useState<CostMetrics | null>(null)
  const [tokens, setTokens] = useState<TokenMetrics | null>(null)
  const [latency, setLatency] = useState<LatencyMetricsType | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.getCostMetrics().catch(() => null),
      api.getTokenMetrics().catch(() => null),
      api.getLatencyMetrics().catch(() => null),
    ]).then(([c, t, l]) => {
      setCost(c)
      setTokens(t)
      setLatency(l)
      setLoading(false)
    })
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-gray-400">Loading...</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Metrics</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard title="Total Cost" value={`$${cost?.total_cost_usd.toFixed(4) || '0'}`} color="purple" />
        <StatCard title="Total Tokens" value={(tokens?.total_tokens || 0).toLocaleString()} color="blue" />
        <StatCard title="Avg Latency" value={`${latency?.average_latency_seconds.toFixed(1) || '0'}s`} color="yellow" />
        <StatCard title="P95 Latency" value={`${latency?.p95_latency_seconds.toFixed(1) || '0'}s`} color="red" />
      </div>

      {cost && (
        <div className="mb-8">
          <CostBreakdown costByAgent={cost.cost_by_agent} costByDay={cost.cost_by_day} />
        </div>
      )}

      {latency && (
        <LatencyChart
          latencyByAgent={latency.latency_by_agent}
          avgLatency={latency.average_latency_seconds}
          p95Latency={latency.p95_latency_seconds}
        />
      )}

      {tokens && Object.keys(tokens.tokens_by_agent).length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6 mt-6">
          <h3 className="text-sm font-semibold text-gray-500 mb-4">Token Usage by Agent</h3>
          <div className="space-y-3">
            {Object.entries(tokens.tokens_by_agent).map(([agent, usage]) => (
              <div key={agent} className="flex items-center gap-4">
                <span className="text-sm font-medium w-32">{agent}</span>
                <div className="flex-1 flex gap-2">
                  <div className="bg-blue-100 rounded-full h-4 flex-1 relative">
                    <div
                      className="bg-blue-500 rounded-full h-4 absolute left-0"
                      style={{ width: `${Math.min((usage.input / (tokens.total_tokens || 1)) * 100 * 3, 100)}%` }}
                    />
                  </div>
                  <div className="bg-green-100 rounded-full h-4 flex-1 relative">
                    <div
                      className="bg-green-500 rounded-full h-4 absolute left-0"
                      style={{ width: `${Math.min((usage.output / (tokens.total_tokens || 1)) * 100 * 3, 100)}%` }}
                    />
                  </div>
                </div>
                <span className="text-xs text-gray-500 w-36 text-right">
                  {usage.input.toLocaleString()} in / {usage.output.toLocaleString()} out
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
