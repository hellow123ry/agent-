export type ChatMessage = {
  role: string
  content: string
  message_type: string
}

export type ChatState = {
  current_intent: string
  active_task: string
  task_stack: string[]
  global_blackboard: Record<string, unknown>
}

export type ChatSession = {
  session_id: string
  messages: ChatMessage[]
  state: ChatState
}

export type ChatTurnResponse = ChatSession & {
  traces: TraceEvent[]
}

import type { TraceEvent } from './trace'
