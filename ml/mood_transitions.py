from typing import Any

import numpy as np


def classify_mood(valence: float, energy: float) -> str:
    if valence >= 0.5 and energy >= 0.5:
        return "Euphoric"
    elif valence >= 0.5 and energy < 0.5:
        return "Chill"
    elif valence < 0.5 and energy >= 0.5:
        return "Intense"
    else:
        return "Melancholic"


def build_mood_transition_matrix(
    listening_history: list[dict[str, Any]],
) -> dict[str, Any]:
    states = ["Euphoric", "Chill", "Intense", "Melancholic"]
    state_to_idx = {state: i for i, state in enumerate(states)}

    counts = np.zeros((4, 4), dtype=float)

    prev_mood: str | None = None
    for listen in listening_history:
        v = float(listen.get("valence", 0.5))
        e = float(listen.get("energy", 0.5))
        curr_mood = classify_mood(v, e)

        if prev_mood is not None:
            i = state_to_idx[prev_mood]
            j = state_to_idx[curr_mood]
            counts[i, j] += 1.0

        prev_mood = curr_mood

    row_sums = counts.sum(axis=1, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        matrix = np.where(row_sums > 0, counts / np.maximum(row_sums, 1e-9), 0.25)

    return {
        "states": states,
        "transition_matrix": [[round(float(val), 4) for val in row] for row in matrix],
        "total_transitions": int(counts.sum()),
    }
