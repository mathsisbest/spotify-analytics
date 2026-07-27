from ml.mood_transitions import build_mood_transition_matrix, classify_mood
from ml.recommend import recommend_cosine


def test_classify_mood() -> None:
    assert classify_mood(0.8, 0.8) == "Euphoric"
    assert classify_mood(0.8, 0.2) == "Chill"
    assert classify_mood(0.2, 0.8) == "Intense"
    assert classify_mood(0.2, 0.2) == "Melancholic"


def test_build_mood_transition_matrix() -> None:
    history = [
        {"valence": 0.8, "energy": 0.8},
        {"valence": 0.2, "energy": 0.2},
        {"valence": 0.8, "energy": 0.2},
    ]
    res = build_mood_transition_matrix(history)
    assert "states" in res
    assert "transition_matrix" in res
    assert len(res["transition_matrix"]) == 4


def test_recommend_cosine() -> None:
    user_tracks = [{"track_id": "t1", "danceability": 0.5, "energy": 0.5}]
    catalog = [
        {"track_id": "t1", "danceability": 0.5, "energy": 0.5},
        {"track_id": "t2", "danceability": 0.6, "energy": 0.6},
        {"track_id": "t3", "danceability": 0.1, "energy": 0.1},
    ]
    recs = recommend_cosine(user_tracks, catalog, recent_track_ids=["t1"], n=2)
    assert len(recs) <= 2
    assert all("score" in r for r in recs)
