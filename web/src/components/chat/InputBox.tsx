import { useState } from 'react'

type InputBoxProps = {
  onSend: (message: string) => Promise<void>
  disabled?: boolean
}

export function InputBox({ onSend, disabled = false }: InputBoxProps) {
  const [value, setValue] = useState('')

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    const message = value.trim()
    if (!message) return
    setValue('')
    await onSend(message)
  }

  return (
    <form className="input-box" onSubmit={handleSubmit}>
      <textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="输入用户问题，例如：我想订明天晚上的烤肉店"
        rows={4}
        disabled={disabled}
      />
      <button type="submit" disabled={disabled || !value.trim()}>
        发送
      </button>
    </form>
  )
}
