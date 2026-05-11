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
