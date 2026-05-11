const BASE = 'http://localhost:8000'

async function handleJsonResponse(res) {
  if (!res.ok) {
    throw new Error((await res.json()).detail)
  }
  return res.json()
}

export async function generateVariations(basePrompt) {
  const res = await fetch(`${BASE}/generate-variations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ base_prompt: basePrompt }),
  })
  return handleJsonResponse(res)
}

export async function getResponses(variations) {
  const res = await fetch(`${BASE}/get-responses`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ variations }),
  })
  return handleJsonResponse(res)
}

export async function streamResponse(label, text, onChunk, onDone, onError) {
  const res = await fetch(`${BASE}/stream-response`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ label, text }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const data = line.slice(6)
      try {
        const parsed = JSON.parse(data)
        if (parsed.chunk !== undefined) onChunk(parsed.chunk)
        if (parsed.done) { onDone(); return }
        if (parsed.error) { onError(parsed.error); return }
      } catch {}
    }
  }
  onDone()
}

export async function saveResults(sessionData) {
  const res = await fetch(`${BASE}/save-results`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(sessionData),
  })
  return handleJsonResponse(res)
}

export async function getHistory() {
  const res = await fetch(`${BASE}/history`)
  return handleJsonResponse(res)
}

export async function autoScore(label, responseText) {
  const res = await fetch(`${BASE}/auto-score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ label, response_text: responseText }),
  })
  return handleJsonResponse(res)
}

export async function exportBest(sessionId) {
  const res = await fetch(`${BASE}/export-best?session_id=${sessionId}`)
  return handleJsonResponse(res)
}
