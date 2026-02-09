import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

interface LatencyChartProps {
  latencyByAgent: Record<string, number>
  avgLatency: number
  p95Latency: number
}

export default function LatencyChart({ latencyByAgent, avgLatency, p95Latency }: LatencyChartProps) {
  const data = Object.entries(latencyByAgent).map(([name, latency]) => ({
    name,
    latency: Number(latency.toFixed(2)),
  }))

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-semibold text-gray-500">Latency by Agent</h3>
        <div className="flex gap-4 text-xs">
          <span className="text-gray-500">Avg: <strong>{avgLatency.toFixed(2)}s</strong></span>
          <span className="text-gray-500">P95: <strong>{p95Latency.toFixed(2)}s</strong></span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" fontSize={12} />
          <YAxis fontSize={12} tickFormatter={(v) => `${v}s`} />
          <Tooltip formatter={(v: number) => [`${v.toFixed(2)}s`, 'Latency']} />
          <Bar dataKey="latency" fill="#f59e0b" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
