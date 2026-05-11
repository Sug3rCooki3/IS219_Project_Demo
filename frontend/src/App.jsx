import { useEffect, useState } from 'react'

import { autoScore, generateVariations, getHistory, getResponses, saveResults } from './api'
import ExportButton from './components/ExportButton'
import HistoryPanel from './components/HistoryPanel'
import PromptInput from './components/PromptInput'
import ResponseGrid from './components/ResponseGrid'

function buildSessionPayload(basePrompt, tokenUsage, variations, responses, ratings, autoScores) {
  return {
    base_prompt: basePrompt,
    token_usage: tokenUsage,
    variations: variations.map((variation) => {
      const matchingResponse = responses.find((response) => response.label === variation.label)
      const score = autoScores[variation.label]
      return {
        label: variation.label,
        technique: variation.technique,
        variation_text: variation.text,
        response_text: matchingResponse?.response ?? '',
        response_cached: matchingResponse?.cached ?? false,
        manual_score: ratings[variation.label] ?? null,
        auto_clarity: score?.clarity ?? null,
        auto_relevance: score?.relevance ?? null,
        auto_completeness: score?.completeness ?? null,
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
  const [autoScores, setAutoScores] = useState({})
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
    const sessionData = buildSessionPayload(basePrompt, tokenUsage, variations, responses, nextRatings, autoScores)
    const data = await saveResults(sessionData)
    setCurrentSessionId(data.session_id)
    const historyData = await getHistory()
    setHistory(historyData.sessions)
  }

  async function handleSubmit(prompt) {
    setLoading(true)
    setError(null)
    setCurrentSessionId(null)
    setAutoScores({})
    try {
      setBasePrompt(prompt)
      const variationData = await generateVariations(prompt)
      setVariations(variationData.variations)
      setRatings({})

      const responseData = await getResponses(variationData.variations)
      setResponses(responseData.responses)
      setTokenUsage(responseData.token_usage)

      // Phase 1: auto-score each response (non-fatal if it fails)
      try {
        const scores = {}
        await Promise.all(
          responseData.responses.map(async (r) => {
            const score = await autoScore(r.label, r.response)
            scores[r.label] = score
          })
        )
        setAutoScores(scores)
      } catch {
        // auto-score failure is non-fatal — scores stay empty
      }
    } catch (err) {
      setError(err.message)
      setVariations([])
      setResponses([])
      setTokenUsage(null)
      setRatings({})
      setAutoScores({})
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
    setAutoScores(
      Object.fromEntries(
        session.variations
          .filter((v) => v.auto_clarity != null)
          .map((v) => [
            v.label,
            { clarity: v.auto_clarity, relevance: v.auto_relevance, completeness: v.auto_completeness },
          ])
      )
    )
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
        <ExportButton sessionId={currentSessionId} onExport={() => {}} />
      </main>
    </div>
  )
}
