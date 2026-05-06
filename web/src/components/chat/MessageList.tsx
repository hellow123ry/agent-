import type { ChatMessage } from '../../types/chat'

type MessageListProps = {
  messages: ChatMessage[]
}

export function MessageList({ messages }: MessageListProps) {
  if (messages.length === 0) {
    return <div className="empty-state">还没有消息，先发一条试试。</div>
  }

  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <article key={`${message.role}-${index}`} className={`message-card role-${message.role}`}>
          <header>
            <span className="message-role">{message.role}</span>
            <span className="message-type">{message.message_type}</span>
          </header>
          <pre>{message.content}</pre>
        </article>
      ))}
    </div>
  )
}
