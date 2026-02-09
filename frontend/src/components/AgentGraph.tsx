import { useCallback } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  type Node,
  type Edge,
  Position,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

interface AgentGraphProps {
  activeAgent?: string
  completedAgents?: string[]
}

const agentNodes: Node[] = [
  { id: 'supervisor', position: { x: 300, y: 0 }, data: { label: 'Supervisor' }, sourcePosition: Position.Bottom, targetPosition: Position.Top },
  { id: 'researcher', position: { x: 100, y: 120 }, data: { label: 'Researcher' }, sourcePosition: Position.Bottom, targetPosition: Position.Top },
  { id: 'summarizer', position: { x: 300, y: 120 }, data: { label: 'Summarizer' }, sourcePosition: Position.Bottom, targetPosition: Position.Top },
  { id: 'fact_checker', position: { x: 500, y: 120 }, data: { label: 'Fact Checker' }, sourcePosition: Position.Bottom, targetPosition: Position.Top },
  { id: 'report_writer', position: { x: 300, y: 240 }, data: { label: 'Report Writer' }, sourcePosition: Position.Bottom, targetPosition: Position.Top },
]

const agentEdges: Edge[] = [
  { id: 'e-sup-res', source: 'supervisor', target: 'researcher', animated: true },
  { id: 'e-sup-sum', source: 'supervisor', target: 'summarizer', animated: true },
  { id: 'e-sup-fc', source: 'supervisor', target: 'fact_checker', animated: true },
  { id: 'e-res-sup', source: 'researcher', target: 'supervisor', type: 'smoothstep' },
  { id: 'e-sum-sup', source: 'summarizer', target: 'supervisor', type: 'smoothstep' },
  { id: 'e-fc-sup', source: 'fact_checker', target: 'supervisor', type: 'smoothstep' },
  { id: 'e-sup-rw', source: 'supervisor', target: 'report_writer', animated: true },
]

export default function AgentGraph({ activeAgent, completedAgents = [] }: AgentGraphProps) {
  const getNodeStyle = useCallback(
    (id: string) => {
      if (id === activeAgent) {
        return { background: '#3b82f6', color: 'white', border: '2px solid #1d4ed8' }
      }
      if (completedAgents.includes(id)) {
        return { background: '#22c55e', color: 'white', border: '2px solid #16a34a' }
      }
      return { background: '#f3f4f6', border: '1px solid #d1d5db' }
    },
    [activeAgent, completedAgents]
  )

  const styledNodes = agentNodes.map((node) => ({
    ...node,
    style: { ...getNodeStyle(node.id), borderRadius: '8px', padding: '10px 20px', fontWeight: 600, fontSize: '13px' },
  }))

  return (
    <div className="h-80 bg-white rounded-xl border">
      <ReactFlow
        nodes={styledNodes}
        edges={agentEdges}
        fitView
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  )
}
