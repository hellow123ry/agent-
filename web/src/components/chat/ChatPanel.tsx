import type { ChatMessage } from '../../types/chat'
import { InputBox } from './InputBox'
import { MessageList } from './MessageList'

type ChatPanelProps = {
  sessionId?: string
  messages: ChatMessage[]
  busy: boolean
  error?: string
  onSend: (message: string) => Promise<void>
  onReset: () => Promise<void>
}

export function ChatPanel({ sessionId, messages, busy, error, onSend, onReset }: ChatPanelProps) {
  return (
    <section className="panel chat-panel">
      <div className="panel-header">
        <div>
          <h2>对话调试</h2>
          <p className="panel-subtitle">Session: {sessionId ?? '初始化中'}</p>
        </div>
        <button type="button" className="ghost-button" onClick={onReset} disabled={busy}>
          重置会话
        </button>
      </div>
      {error ? <div className="error-banner">{error}</div> : null}
      <MessageList messages={messages} />
      <InputBox onSend={onSend} disabled={busy || !sessionId} />
    </section>
  )
}
