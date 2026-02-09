import { useEffect, useState } from 'react'
import ViolationLog from '../components/ViolationLog'
import { api, type Violation } from '../api/client'

export default function Guardrails() {
  const [violations, setViolations] = useState<Violation[]>([])
  const [filter, setFilter] = useState<{ guard_type?: string; severity?: string }>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getViolations(filter)
      .then(setViolations)
      .catch(() => setViolations([]))
      .finally(() => setLoading(false))
  }, [filter])

  const guardTypes = [...new Set(violations.map((v) => v.guard_type))]
  const severityCounts = violations.reduce((acc, v) => {
    acc[v.severity] = (acc[v.severity] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Guardrails</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl shadow-sm p-4">
          <p className="text-xs text-gray-500">Total Violations</p>
          <p className="text-2xl font-bold mt-1">{violations.length}</p>
        </div>
        <div className="bg-red-50 rounded-xl p-4">
          <p className="text-xs text-red-600">Critical</p>
          <p className="text-2xl font-bold text-red-700 mt-1">{severityCounts.critical || 0}</p>
        </div>
        <div className="bg-orange-50 rounded-xl p-4">
          <p className="text-xs text-orange-600">High</p>
          <p className="text-2xl font-bold text-orange-700 mt-1">{severityCounts.high || 0}</p>
        </div>
        <div className="bg-yellow-50 rounded-xl p-4">
          <p className="text-xs text-yellow-600">Medium</p>
          <p className="text-2xl font-bold text-yellow-700 mt-1">{severityCounts.medium || 0}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div>
          <label className="text-xs text-gray-500 block mb-1">Guard Type</label>
          <select
            className="px-3 py-1.5 border rounded-lg text-sm"
            value={filter.guard_type || ''}
            onChange={(e) => setFilter({ ...filter, guard_type: e.target.value || undefined })}
          >
            <option value="">All</option>
            {guardTypes.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Severity</label>
          <select
            className="px-3 py-1.5 border rounded-lg text-sm"
            value={filter.severity || ''}
            onChange={(e) => setFilter({ ...filter, severity: e.target.value || undefined })}
          >
            <option value="">All</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center text-gray-400 py-8">Loading...</div>
      ) : (
        <ViolationLog violations={violations} />
      )}
    </div>
  )
}
