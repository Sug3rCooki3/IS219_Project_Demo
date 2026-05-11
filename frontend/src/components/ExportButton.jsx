import { useState } from 'react'

import { exportBest } from '../api'

function findStrongestSubScore(bestVariation) {
  const scores = [
    ['clarity', bestVariation.auto_clarity],
    ['relevance', bestVariation.auto_relevance],
    ['completeness', bestVariation.auto_completeness],
  ]
  const max = Math.max(...scores.map(([, v]) => v ?? 0))
  // tiebreak order: clarity → relevance → completeness
  const winner = scores.find(([, v]) => v === max)
  return winner[0]
}

export default function ExportButton({ sessionId, onExport }) {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleClick() {
    setLoading(true)
    try {
      const data = await exportBest(sessionId)
      setResult(data)
      onExport(data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="export-button">
      <button type="button" disabled={sessionId == null || loading} onClick={handleClick}>
        {loading ? 'Exporting…' : 'Export Best'}
      </button>
      {result && (
        <p className="export-result">
          Variation {result.best_variation.label} scored highest — strongest in{' '}
          {findStrongestSubScore(result.best_variation)}.
        </p>
      )}
    </div>
  )
}
