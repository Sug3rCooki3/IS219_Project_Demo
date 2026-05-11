export default function ScoreDisplay({ autoScore }) {
  if (!autoScore) {
    return <div className="score-display score-unavailable">Score unavailable</div>
  }

  const avg = (autoScore.clarity + autoScore.relevance + autoScore.completeness) / 3
  const avgStr = (Math.round(avg * 10) / 10).toFixed(1)

  return (
    <div className="score-display">
      <span>Clarity: {autoScore.clarity} / 5</span>
      <span>Relevance: {autoScore.relevance} / 5</span>
      <span>Completeness: {autoScore.completeness} / 5</span>
      <span className="score-avg">Avg: {avgStr}</span>
    </div>
  )
}
