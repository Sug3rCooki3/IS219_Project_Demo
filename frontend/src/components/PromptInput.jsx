import { useEffect, useState } from 'react'

export default function PromptInput({ onSubmit, loading, initialValue = '' }) {
  const [value, setValue] = useState(initialValue)

  useEffect(() => {
    setValue(initialValue)
  }, [initialValue])

  function handleSubmit(event) {
    event.preventDefault()
    if (!value.trim() || loading) {
      return
    }
    onSubmit(value)
  }

  return (
    <form className="prompt-input" onSubmit={handleSubmit}>
      <textarea
        placeholder="Enter a math prompt, e.g. What is the chain rule?"
        value={value}
        onChange={(event) => setValue(event.target.value)}
      />
      <button type="submit" disabled={loading || !value.trim()}>
        {loading ? 'Working...' : 'Generate Variations'}
      </button>
    </form>
  )
}
