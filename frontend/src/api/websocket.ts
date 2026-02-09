export interface WSEvent {
  type: string
  run_id: string
  timestamp: number
  agent?: string
  [key: string]: unknown
}

export class WebSocketManager {
  private ws: WebSocket | null = null
  private listeners: ((event: WSEvent) => void)[] = []

  connect(runId: string): void {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    this.ws = new WebSocket(`${protocol}//${host}/api/v1/ws/${runId}`)

    this.ws.onmessage = (event) => {
      try {
        const data: WSEvent = JSON.parse(event.data)
        this.listeners.forEach((listener) => listener(data))
      } catch {
        console.error('Failed to parse WebSocket message')
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    this.ws.onclose = () => {
      console.log('WebSocket closed')
    }
  }

  onEvent(listener: (event: WSEvent) => void): () => void {
    this.listeners.push(listener)
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener)
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.listeners = []
  }
}
