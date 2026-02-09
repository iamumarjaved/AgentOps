const BASE_URL = '/api/v1'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': localStorage.getItem('api_key') || '',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || 'Request failed')
  }

  return response.json()
}

export const api = {
  // Health
  health: () => request<{ status: string; version: string }>('/health'),

  // Runs
  createRun: (topic: string, config?: Record<string, unknown>) =>
    request<{ id: string; status: string }>('/runs', {
      method: 'POST',
      body: JSON.stringify({ topic, config: config || {} }),
    }),

  listRuns: (params?: { status?: string; limit?: number; offset?: number }) => {
    const search = new URLSearchParams()
    if (params?.status) search.set('status', params.status)
    if (params?.limit) search.set('limit', String(params.limit))
    if (params?.offset) search.set('offset', String(params.offset))
    return request<Run[]>(`/runs?${search}`)
  },

  getRun: (id: string) => request<RunDetail>(`/runs/${id}`),
  getRunSteps: (id: string) => request<AgentStep[]>(`/runs/${id}/steps`),

  // Metrics
  getCostMetrics: () => request<CostMetrics>('/metrics/cost'),
  getTokenMetrics: () => request<TokenMetrics>('/metrics/tokens'),
  getLatencyMetrics: () => request<LatencyMetrics>('/metrics/latency'),

  // Evaluations
  triggerEvaluation: (runId: string, scorers?: string[]) =>
    request('/evaluations/trigger', {
      method: 'POST',
      body: JSON.stringify({ run_id: runId, scorers }),
    }),
  getEvaluationSummary: () => request<EvaluationSummary>('/evaluations/summary'),
  getRunEvaluations: (runId: string) => request<EvaluationResult[]>(`/evaluations/${runId}`),

  // Guardrails
  getViolations: (params?: { guard_type?: string; severity?: string }) => {
    const search = new URLSearchParams()
    if (params?.guard_type) search.set('guard_type', params.guard_type)
    if (params?.severity) search.set('severity', params.severity)
    return request<Violation[]>(`/guardrails/violations?${search}`)
  },
}

// Types
export interface Run {
  id: string
  topic: string
  status: string
  total_tokens: number
  total_cost_usd: number
  total_latency_seconds: number
  variant: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
}

export interface RunDetail extends Run {
  result: string | null
  error: string | null
  steps: AgentStep[]
}

export interface AgentStep {
  id: string
  agent_name: string
  step_order: number
  status: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  cost_usd: number
  latency_seconds: number
  tool_calls: unknown[] | null
  started_at: string | null
  completed_at: string | null
}

export interface CostMetrics {
  total_cost_usd: number
  cost_by_agent: Record<string, number>
  cost_by_day: { date: string; cost_usd: number }[]
}

export interface TokenMetrics {
  total_tokens: number
  tokens_by_agent: Record<string, { input: number; output: number }>
}

export interface LatencyMetrics {
  average_latency_seconds: number
  p95_latency_seconds: number
  latency_by_agent: Record<string, number>
}

export interface EvaluationSummary {
  average_scores: Record<string, number>
  total_evaluations: number
}

export interface EvaluationResult {
  id: string
  run_id: string
  scorer_name: string
  score: number
  reasoning: string | null
  created_at: string
}

export interface Violation {
  id: string
  run_id: string | null
  guard_type: string
  direction: string
  action: string
  severity: string
  details: Record<string, unknown>
  created_at: string
}
