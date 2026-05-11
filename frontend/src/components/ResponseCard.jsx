import ReactMarkdown from 'react-markdown'
import rehypeKatex from 'rehype-katex'
import remarkMath from 'remark-math'
import ScoreDisplay from './ScoreDisplay'

// Convert \[...\] → $$...$$ and \(...\) → $...$ so remark-math can parse them
function normalizeMath(text) {
  return text
    .replace(/\\\[([\s\S]*?)\\\]/g, (_, inner) => `$$${inner}$$`)
    .replace(/\\\(([\s\S]*?)\\\)/g, (_, inner) => `$${inner}$`)
}

export default function ResponseCard({ label, technique, responseText, cached, rating, autoScore, onRatingChange }) {
  return (
    <article className="response-card">
      <div className="card-header">
        <span className="label">Variation {label}</span>
        <span className="technique">{technique}</span>
        {cached && <span className="cached-badge">Cached</span>}
      </div>
      <div className="response-text">
        <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
          {normalizeMath(responseText)}
        </ReactMarkdown>
      </div>
      <div className="rating-controls">
        {[1, 2, 3, 4, 5].map((score) => (
          <button
            key={score}
            type="button"
            className={rating === score ? 'rating-button is-selected' : 'rating-button'}
            onClick={() => onRatingChange(label, score)}
          >
            {score}
          </button>
        ))}
      </div>
      <ScoreDisplay autoScore={autoScore} />
    </article>
  )
}
