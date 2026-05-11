import { useState } from 'react'

function truncatePrompt(prompt) {
  if (prompt.length <= 60) {
    return prompt
  }
  return `${prompt.slice(0, 60)}...`
}

export default function HistoryPanel({ history, onSelect }) {
  const [isOpen, setIsOpen] = useState(true)

  return (
    <aside className="history-panel">
      <button className="history-toggle" type="button" onClick={() => setIsOpen((open) => !open)}>
        {isOpen ? '▼ History' : '▶ History'}
      </button>

      <div className="history-list" style={{ display: isOpen ? 'block' : 'none' }}>
        {history.length ? (
          history.map((session) => (
            <button key={session.id} type="button" className="history-item" onClick={() => onSelect(session)}>
              <span className="history-prompt">{truncatePrompt(session.base_prompt)}</span>
              <span className="history-date">{session.created_at}</span>
            </button>
          ))
        ) : (
          <p className="history-empty">No history yet.</p>
        )}
      </div>
    </aside>
  )
}
