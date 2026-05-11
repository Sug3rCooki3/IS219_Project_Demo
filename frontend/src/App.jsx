import { useEffect, useState } from 'react'

import { generateVariations, getHistory, getResponses, saveResults } from './api'
import HistoryPanel from './components/HistoryPanel'
import PromptInput from './components/PromptInput'
import ResponseGrid from './components/ResponseGrid'

function buildSessionPayload(basePrompt, tokenUsage, variations, responses, ratings) {
  return {
    base_prompt: basePrompt,
    token_usage: tokenUsage,
    variations: variations.map((variation) => {
      const matchingResponse = responses.find((response) => response.label === variation.label)
      return {
        label: variation.label,
        technique: variation.technique,
        variation_text: variation.text,
        response_text: matchingResponse?.response ?? '',
        response_cached: matchingResponse?.cached ?? false,
        manual_score: ratings[variation.label] ?? null,
        auto_clarity: null,
        auto_relevance: null,
        auto_completeness: null,
      }
    }),
  }
}

export default function App() {
  const [basePrompt, setBasePrompt] = useState('')
  const [variations, setVariations] = useState([])
  const [responses, setResponses] = useState([])
  const [tokenUsage, setTokenUsage] = useState(null)
  const [ratings, setRatings] = useState({})
  const [autoScores] = useState({})
  const [history, setHistory] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    getHistory()
      .then((data) => setHistory(data.sessions))
      .catch((err) => setError(err.message))
  }, [])

  async function handleSave(nextRatings = ratings) {
    const sessionData = buildSessionPayload(basePrompt, tokenUsage, variations, responses, nextRatings)
    const data = await saveResults(sessionData)
    setCurrentSessionId(data.session_id)
    const historyData = await getHistory()
    setHistory(historyData.sessions)
  }

  async function handleSubmit(prompt) {
    setLoading(true)
    setError(null)
    setCurrentSessionId(null)
    try {
      setBasePrompt(prompt)
      const variationData = await generateVariations(prompt)
      setVariations(variationData.variations)
      setRatings({})

      const responseData = await getResponses(variationData.variations)
      setResponses(responseData.responses)
      setTokenUsage(responseData.token_usage)
    } catch (err) {
      setError(err.message)
      setVariations([])
      setResponses([])
      setTokenUsage(null)
      setRatings({})
    } finally {
      setLoading(false)
    }
  }

  async function handleRatingChange(label, score) {
    const nextRatings = { ...ratings, [label]: score }
    setRatings(nextRatings)

    const ratedCount = variations.filter((variation) => nextRatings[variation.label] != null).length
    if (variations.length === 4 && ratedCount === 4 && currentSessionId == null) {
      try {
        setLoading(true)
        setError(null)
        await handleSave(nextRatings)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
  }

  function handleHistorySelect(session) {
    setBasePrompt(session.base_prompt)
    setCurrentSessionId(session.id)
    setTokenUsage(session.token_usage)

    const sessionVariations = session.variations.map((variation) => ({
      label: variation.label,
      technique: variation.technique,
      text: variation.variation_text,
    }))
    const sessionResponses = session.variations.map((variation) => ({
      label: variation.label,
      response: variation.response_text,
      cached: variation.response_cached,
    }))
    const sessionRatings = Object.fromEntries(
      session.variations.map((variation) => [variation.label, variation.manual_score])
    )

    setVariations(sessionVariations)
    setResponses(sessionResponses)
    setRatings(sessionRatings)
    setError(null)
  }

  return (
    <div className="app-shell">
      <HistoryPanel history={history} onSelect={handleHistorySelect} />
      <main className="main-panel">
        <header className="page-header">
          <p className="eyebrow">Phase 0 MVP</p>
          <h1>Prompt Variation Comparator</h1>
          <p className="subtitle">Generate four fixed math-focused prompt variations, compare responses, and save manual ratings.</p>
        </header>

        <PromptInput onSubmit={handleSubmit} loading={loading} initialValue={basePrompt} />

        {error ? <div className="error-banner">{error}</div> : null}

        <ResponseGrid
          responses={responses}
          variations={variations}
          ratings={ratings}
          autoScores={autoScores}
          onRatingChange={handleRatingChange}
        />
      </main>
    </div>
  )
}
