import database
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/export-best")
def export_best(session_id: int):
    session = database.get_session_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    variations = session["variations"]

    def score_key(v: dict) -> float:
        auto = [v.get("auto_clarity"), v.get("auto_relevance"), v.get("auto_completeness")]
        if all(x is not None for x in auto):
            return sum(auto) / 3
        manual = v.get("manual_score")
        return float(manual) if manual is not None else 0.0

    best = max(variations, key=score_key)

    auto = [best.get("auto_clarity"), best.get("auto_relevance"), best.get("auto_completeness")]
    combined_score = round(sum(auto) / 3, 1) if all(x is not None for x in auto) else None

    return {
        "session_id": session_id,
        "best_variation": {
            "label": best["label"],
            "technique": best["technique"],
            "variation_text": best["variation_text"],
            "response_text": best["response_text"],
            "manual_score": best["manual_score"],
            "auto_clarity": best["auto_clarity"],
            "auto_relevance": best["auto_relevance"],
            "auto_completeness": best["auto_completeness"],
            "combined_score": combined_score,
        },
    }
