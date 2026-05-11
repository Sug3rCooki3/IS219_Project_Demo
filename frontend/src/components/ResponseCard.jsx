export default function ResponseCard({ label, technique, responseText, rating, onRatingChange }) {
  return (
    <article className="response-card">
      <div className="card-header">
        <span className="label">Variation {label}</span>
        <span className="technique">{technique}</span>
      </div>
      <div className="response-text">{responseText}</div>
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
    </article>
  )
}
