import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import AgentGraph from '../components/AgentGraph'
import { api, type RunDetail as RunDetailType } from '../api/client'
import { WebSocketManager } from '../api/websocket'

export default function RunDetail() {
  const { id } = useParams<{ id: string }>()
  const [run, setRun] = useState<RunDetailType | null>(null)
  const [events, setEvents] = useState<{ type: string; agent?: string; timestamp: number }[]>([])
  const [activeAgent, setActiveAgent] = useState<string>()
  const [completedAgents, setCompletedAgents] = useState<string[]>([])

  useEffect(() => {
    if (!id) return
    api.getRun(id).then(setRun).catch(console.error)
  }, [id])

  useEffect(() => {
    if (!id || run?.status !== 'running') return

    const ws = new WebSocketManager()
    ws.connect(id)

    const unsubscribe = ws.onEvent((event) => {
      setEvents((prev) => [...prev, event])

      if (event.type === 'llm_start' && event.agent) {
        setActiveAgent(event.agent as string)
      }
      if (event.type === 'llm_end' && event.agent) {
        setCompletedAgents((prev) =>
          prev.includes(event.agent as string) ? prev : [...prev, event.agent as string]
        )
      }
      if (event.type === 'run_completed' || event.type === 'run_failed') {
        api.getRun(id).then(setRun).catch(console.error)
      }
    })

    return () => {
      unsubscribe()
      ws.disconnect()
    }
  }, [id, run?.status])

  if (!run) {
    return <div className="flex items-center justify-center h-64 text-gray-400">Loading...</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Run Detail</h1>
      <p className="text-sm text-gray-500 mb-6">ID: {run.id}</p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-500">Topic</p>
          <p className="text-sm font-medium mt-1">{run.topic}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <p className="text-sm text-gray-500">Status</p>
          <p className={`text-sm font-bold mt-1 ${
            run.status === 'completed' ? 'text-green-600' :
            run.status === 'failed' ? 'text-red-600' :
            run.status === 'running' ? 'text-blue-600' :
            'text-gray-600'
          }`}>{run.status.toUpperCase()}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Tokens</span>
            <span className="font-semibold">{run.total_tokens.toLocaleString()}</span>
          </div>
          <div className="flex justify-between text-sm mt-2">
            <span className="text-gray-500">Cost</span>
            <span className="font-semibold">${run.total_cost_usd.toFixed(4)}</span>
          </div>
          <div className="flex justify-between text-sm mt-2">
            <span className="text-gray-500">Latency</span>
            <span className="font-semibold">{run.total_latency_seconds.toFixed(1)}s</span>
          </div>
        </div>
      </div>

      {/* Agent Graph */}
      <div className="mb-6">
        <h2 className="text-sm font-semibold text-gray-500 mb-3">Agent Pipeline</h2>
        <AgentGraph activeAgent={activeAgent} completedAgents={completedAgents} />
      </div>

      {/* Steps Timeline */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h2 className="text-sm font-semibold text-gray-500 mb-4">Execution Steps</h2>
        <div className="space-y-3">
          {run.steps.map((step) => (
            <div key={step.id} className="flex items-center gap-4 p-3 rounded-lg bg-gray-50">
              <span className="text-xs font-mono text-gray-400 w-6">{step.step_order}</span>
              <span className="text-sm font-medium w-32">{step.agent_name}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full ${
                step.status === 'completed' ? 'bg-green-100 text-green-700' :
                step.status === 'failed' ? 'bg-red-100 text-red-700' :
                'bg-gray-100 text-gray-600'
              }`}>{step.status}</span>
              <span className="text-xs text-gray-500 ml-auto">{step.total_tokens} tokens</span>
              <span className="text-xs text-gray-500">${step.cost_usd.toFixed(4)}</span>
              <span className="text-xs text-gray-500">{step.latency_seconds.toFixed(2)}s</span>
            </div>
          ))}
        </div>
      </div>

      {/* Live Events */}
      {events.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-sm font-semibold text-gray-500 mb-4">Live Events</h2>
          <div className="space-y-1 max-h-64 overflow-y-auto font-mono text-xs">
            {events.map((event, i) => (
              <div key={i} className="text-gray-600">
                <span className="text-gray-400">{new Date(event.timestamp * 1000).toLocaleTimeString()}</span>
                {' '}<span className="text-blue-600">{event.type}</span>
                {event.agent && <span className="text-purple-600"> [{event.agent}]</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Report */}
      {run.result && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-sm font-semibold text-gray-500 mb-4">Generated Report</h2>
          <div className="prose prose-sm max-w-none whitespace-pre-wrap text-sm">{run.result}</div>
        </div>
      )}

      {run.error && (
        <div className="bg-red-50 rounded-xl p-6">
          <h2 className="text-sm font-semibold text-red-700 mb-2">Error</h2>
          <pre className="text-xs text-red-600 whitespace-pre-wrap">{run.error}</pre>
        </div>
      )}
    </div>
  )
}
