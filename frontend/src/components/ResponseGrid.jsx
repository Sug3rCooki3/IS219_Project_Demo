import ResponseCard from './ResponseCard'

export default function ResponseGrid({ responses, variations, ratings, autoScores, onRatingChange }) {
  if (!responses.length) {
    return null
  }

  return (
    <section className="response-grid">
      {responses.map((response) => {
        const variation = variations.find((item) => item.label === response.label)
        return (
          <ResponseCard
            key={response.label}
            label={response.label}
            technique={variation?.technique ?? ''}
            responseText={response.response}
            cached={response.cached}
            rating={ratings[response.label] ?? null}
            autoScore={autoScores[response.label] ?? null}
            onRatingChange={onRatingChange}
          />
        )
      })}
    </section>
  )
}
