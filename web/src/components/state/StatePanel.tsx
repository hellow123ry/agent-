import type { ChatState } from '../../types/chat'

type StatePanelProps = {
  state: ChatState | null
}

function renderValue(value: unknown) {
  return JSON.stringify(value, null, 2)
}

export function StatePanel({ state }: StatePanelProps) {
  return (
    <section className="panel state-panel">
      <div className="panel-header">
        <div>
          <h2>会话状态</h2>
          <p className="panel-subtitle">Intent / Task Stack / Blackboard</p>
        </div>
      </div>
      {!state ? (
        <div className="empty-state">状态加载中。</div>
      ) : (
        <div className="state-grid">
          <div className="state-card">
            <span className="state-label">current_intent</span>
            <strong>{state.current_intent || 'unknown'}</strong>
          </div>
          <div className="state-card">
            <span className="state-label">active_task</span>
            <strong>{state.active_task || 'none'}</strong>
          </div>
          <div className="state-card">
            <span className="state-label">task_stack</span>
            <pre>{renderValue(state.task_stack)}</pre>
          </div>
          <div className="state-card">
            <span className="state-label">global_blackboard</span>
            <pre>{renderValue(state.global_blackboard)}</pre>
          </div>
        </div>
      )}
    </section>
  )
}
