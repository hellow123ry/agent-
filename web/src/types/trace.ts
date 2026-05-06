export type TraceEvent = {
  id: string
  type: string
  timestamp: number
  latency_ms?: number
  payload: Record<string, unknown>
}
