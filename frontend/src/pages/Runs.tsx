import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type Run } from '../api/client'

export default function Runs() {
  const [runs, setRuns] = useState<Run[]>([])
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(true)

  const fetchRuns = () => {
    setLoading(true)
    api.listRuns({ status: statusFilter || undefined, limit: 50 })
      .then(setRuns)
      .catch(() => setRuns([]))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchRuns() }, [statusFilter])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!topic.trim()) return
    try {
      await api.createRun(topic)
      setTopic('')
      fetchRuns()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create run')
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Pipeline Runs</h1>

      {/* Create Run Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h2 className="text-sm font-semibold text-gray-500 mb-3">New Research Run</h2>
        <div className="flex gap-3">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter a research topic..."
            className="flex-1 px-4 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition"
          >
            Start Run
          </button>
        </div>
      </form>

      {/* Filter */}
      <div className="flex gap-2 mb-4">
        {['', 'pending', 'running', 'completed', 'failed'].map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-3 py-1.5 text-xs rounded-lg font-medium transition ${
              statusFilter === s
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            {s || 'All'}
          </button>
        ))}
      </div>

      {/* Runs List */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tokens</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Latency</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {loading ? (
              <tr><td colSpan={6} className="px-6 py-8 text-center text-gray-400">Loading...</td></tr>
            ) : runs.length === 0 ? (
              <tr><td colSpan={6} className="px-6 py-8 text-center text-gray-400">No runs found</td></tr>
            ) : (
              runs.map((run) => (
                <tr key={run.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <Link to={`/runs/${run.id}`} className="text-sm text-blue-600 hover:underline truncate block max-w-xs">
                      {run.topic}
                    </Link>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                      run.status === 'completed' ? 'bg-green-100 text-green-700' :
                      run.status === 'failed' ? 'bg-red-100 text-red-700' :
                      run.status === 'running' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>{run.status}</span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{run.total_tokens.toLocaleString()}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">${run.total_cost_usd.toFixed(4)}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{run.total_latency_seconds.toFixed(1)}s</td>
                  <td className="px-6 py-4 text-xs text-gray-400">{new Date(run.created_at).toLocaleString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
