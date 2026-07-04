from typing import Any

from ml.recommend import recommend_for_user


def _ids(result: list[dict[str, Any]]) -> list[str]:
    return [r["track_id"] for r in result]


def _scores(result: list[dict[str, Any]]) -> list[float]:
    return [r["score"] for r in result]


def _clusters(result: list[dict[str, Any]]) -> list[int]:
    return [r["cluster_id"] for r in result]


class TestRecommendForUser:
    def test_schema(self) -> None:
        result = recommend_for_user(["synth_track_0000"], n=3)
        assert len(result) <= 3
        for item in result:
            assert isinstance(item, dict)
            assert set(item.keys()) == {"track_id", "score", "cluster_id"}
            assert isinstance(item["track_id"], str)
            assert isinstance(item["score"], float)
            assert isinstance(item["cluster_id"], int)

    def test_scores_descending(self) -> None:
        result = recommend_for_user(["synth_track_0100"], n=10)
        scores = _scores(result)
        assert scores == sorted(scores, reverse=True)

    def test_excludes_recent_tracks(self) -> None:
        recent = ["synth_track_0000", "synth_track_0001"]
        result = recommend_for_user(recent, n=20)
        ids = _ids(result)
        for tid in recent:
            assert tid not in ids

    def test_all_same_cluster(self) -> None:
        recent = ["synth_track_0050"]
        result = recommend_for_user(recent, n=15)
        if result:
            cid = _clusters(result)[0]
            assert all(c == cid for c in _clusters(result))

    def test_empty_recent_ids(self) -> None:
        result = recommend_for_user([], n=5)
        assert len(result) == 5
        ids = _ids(result)
        assert len(set(ids)) == len(ids)

    def test_n_zero(self) -> None:
        result = recommend_for_user(["synth_track_0000"], n=0)
        assert result == []

    def test_n_one(self) -> None:
        result = recommend_for_user(["synth_track_0000"], n=1)
        assert len(result) == 1

    def test_track_ids_not_in_catalog(self) -> None:
        result = recommend_for_user(["nonexistent_track"], n=5)
        assert len(result) == 5

    def test_partial_match(self) -> None:
        result = recommend_for_user(["synth_track_0000", "nope"], n=5)
        assert len(result) == 5
        assert "synth_track_0000" not in _ids(result)

    def test_n_larger_than_available(self) -> None:
        result = recommend_for_user(["synth_track_0000"], n=9999)
        assert len(result) < 9999
        assert "synth_track_0000" not in _ids(result)

    def test_no_duplicates(self) -> None:
        result = recommend_for_user(["synth_track_0100"], n=30)
        ids = _ids(result)
        assert len(ids) == len(set(ids))

    def test_single_recent_track(self) -> None:
        result = recommend_for_user(["synth_track_0200"], n=10)
        assert len(result) == 10

    def test_deterministic(self) -> None:
        a = recommend_for_user(["synth_track_0000"], n=10)
        b = recommend_for_user(["synth_track_0000"], n=10)
        assert a == b

    def test_score_range(self) -> None:
        result = recommend_for_user(["synth_track_0100"], n=10)
        for item in result:
            assert 0.0 <= item["score"] <= 2.0
