import { useState, useEffect } from 'react'
import { sendMessage, getMessages } from '../api/chat.js'

export default function Chat() {
  const [room, setRoom] = useState('general')
  const [text, setText] = useState('')
  const [messages, setMessages] = useState([])
  const [error, setError] = useState('')

  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const userId = user.id

  useEffect(() => {
    loadMessages()
  }, [room])

  async function loadMessages() {
    try {
      const data = await getMessages(room)
      setMessages(data.messages)
    } catch {
      setMessages([])
    }
  }

  async function handleSend(e) {
    e.preventDefault()
    setError('')
    try {
      await sendMessage(room, userId, text)
      setText('')
      loadMessages()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message')
    }
  }

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', padding: 24 }}>
      <h2>Chat</h2>
      <div style={{ marginBottom: 16 }}>
        <label>Room: </label>
        <input value={room} onChange={e => setRoom(e.target.value)} style={{ marginRight: 8 }} />
        <button onClick={loadMessages}>Join / Refresh</button>
      </div>
      <div style={{ border: '1px solid #ccc', minHeight: 200, padding: 12, marginBottom: 16, overflowY: 'auto' }}>
        {messages.length === 0 && <p style={{ color: '#aaa' }}>No messages yet.</p>}
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 6 }}>
            <strong>User {m.user_id}:</strong> {m.text}
          </div>
        ))}
      </div>
      <form onSubmit={handleSend}>
        <input placeholder="Message" value={text} onChange={e => setText(e.target.value)} required style={{ marginRight: 8, width: 300 }} />
        <button type="submit">Send</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  )
}
