import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

interface CostBreakdownProps {
  costByAgent: Record<string, number>
  costByDay: { date: string; cost_usd: number }[]
}

export default function CostBreakdown({ costByAgent, costByDay }: CostBreakdownProps) {
  const agentData = Object.entries(costByAgent).map(([name, cost]) => ({
    name,
    cost: Number(cost.toFixed(4)),
  }))

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-sm font-semibold text-gray-500 mb-4">Cost by Agent</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={agentData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" fontSize={12} />
            <YAxis fontSize={12} tickFormatter={(v) => `$${v}`} />
            <Tooltip formatter={(v: number) => [`$${v.toFixed(4)}`, 'Cost']} />
            <Bar dataKey="cost" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-sm font-semibold text-gray-500 mb-4">Cost Over Time</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={costByDay}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" fontSize={11} tickFormatter={(d) => new Date(d).toLocaleDateString()} />
            <YAxis fontSize={12} tickFormatter={(v) => `$${v}`} />
            <Tooltip formatter={(v: number) => [`$${v.toFixed(4)}`, 'Cost']} />
            <Bar dataKey="cost_usd" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
