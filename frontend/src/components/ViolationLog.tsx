import type { Violation } from '../api/client'

interface ViolationLogProps {
  violations: Violation[]
}

const severityColors: Record<string, string> = {
  critical: 'bg-red-100 text-red-800',
  high: 'bg-orange-100 text-orange-800',
  medium: 'bg-yellow-100 text-yellow-800',
  low: 'bg-gray-100 text-gray-700',
}

const actionColors: Record<string, string> = {
  blocked: 'bg-red-50 text-red-700',
  flagged: 'bg-yellow-50 text-yellow-700',
  sanitized: 'bg-blue-50 text-blue-700',
}

export default function ViolationLog({ violations }: ViolationLogProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b">
        <h3 className="text-sm font-semibold text-gray-500">Recent Violations</h3>
      </div>
      <div className="divide-y">
        {violations.length === 0 ? (
          <p className="p-6 text-sm text-gray-400 text-center">No violations recorded</p>
        ) : (
          violations.map((v) => (
            <div key={v.id} className="px-6 py-4 flex items-center gap-4">
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${severityColors[v.severity] || severityColors.low}`}>
                {v.severity}
              </span>
              <span className={`text-xs px-2 py-1 rounded font-medium ${actionColors[v.action] || ''}`}>
                {v.action}
              </span>
              <div className="flex-1">
                <p className="text-sm font-medium">{v.guard_type}</p>
                <p className="text-xs text-gray-400">{v.direction} &middot; {new Date(v.created_at).toLocaleString()}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
