from spotify_analytics.extended_history import parse_extended_history_json


def test_parse_extended_history_valid() -> None:
    raw = """
    [
        {
            "ts": "2023-05-01T12:00:00Z",
            "ms_played": 180000,
            "master_metadata_track_name": "Extended Song",
            "master_metadata_album_artist_name": "Extended Artist",
            "master_metadata_album_album_name": "Extended Album",
            "spotify_track_uri": "spotify:track:ext123"
        }
    ]
    """
    res = parse_extended_history_json(raw)
    assert len(res) == 1
    assert res[0]["master_metadata_track_name"] == "Extended Song"
    assert res[0]["spotify_track_uri"] == "spotify:track:ext123"


def test_parse_extended_history_invalid() -> None:
    raw = "not a list"
    assert parse_extended_history_json(raw) == []
