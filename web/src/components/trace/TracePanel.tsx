import type { TraceEvent } from '../../types/trace'

type TracePanelProps = {
  traces: TraceEvent[]
}

function renderPayload(payload: Record<string, unknown>) {
  return JSON.stringify(payload, null, 2)
}

export function TracePanel({ traces }: TracePanelProps) {
  return (
    <section className="panel trace-panel">
      <div className="panel-header">
        <div>
          <h2>过程追踪</h2>
          <p className="panel-subtitle">Router / Expert / Tool / Filter 事件流</p>
        </div>
      </div>
      {traces.length === 0 ? (
        <div className="empty-state">发送一轮消息后，这里会展示 trace。</div>
      ) : (
        <div className="trace-list">
          {traces.map((trace) => (
            <article key={trace.id} className="trace-card">
              <header>
                <strong>{trace.type}</strong>
                <span>{trace.latency_ms ? `${trace.latency_ms} ms` : 'n/a'}</span>
              </header>
              <pre>{renderPayload(trace.payload)}</pre>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}
