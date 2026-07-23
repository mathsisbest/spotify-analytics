"""
Script to generate realistic dummy data matching Spotify's extended streaming history JSON export.

Output format matches the actual JSON structure provided by Spotify Privacy Data export:
[
  {
    "ts": "2026-07-20T14:32:10Z",
    "username": "daniel",
    "platform": "ios",
    "ms_played": 210000,
    "conn_country": "US",
    "ip_addr_subsumed": null,
    "user_agent_decrypted": "unknown",
    "master_metadata_track_name": "Midnight City",
    "master_metadata_album_artist_name": "M83",
    "master_metadata_album_album_name": "Hurry Up, We're Dreaming",
    "spotify_track_uri": "spotify:track:68D11603598711",
    "episode_name": null,
    "episode_show_name": null,
    "spotify_episode_uri": null,
    "reason_start": "trackdone",
    "reason_end": "trackdone",
    "shuffle": true,
    "skipped": false,
    "offline": false,
    "offline_timestamp": 0,
    "incognito_mode": false,
    "trackName": "Midnight City",
    "artistName": "M83",
    "albumName": "Hurry Up, We're Dreaming",
    "msPlayed": 210000
  }
]
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

SAMPLE_ARTISTS_TRACKS = [
    ("M83", "Midnight City", "Hurry Up, We're Dreaming", "68D11603598711", 243000),
    ("Daft Punk", "Get Lucky", "Random Access Memories", "2F829103598712", 248000),
    ("The Weeknd", "Blinding Lights", "After Hours", "0VjIj9103598713", 200000),
    ("Tame Impala", "The Less I Know The Better", "Currents", "6t1219103598714", 216000),
    ("Arctic Monkeys", "Do I Wanna Know?", "AM", "516119103598715", 272000),
    ("Dua Lipa", "Levitating", "Future Nostalgia", "391219103598716", 203000),
    ("Glass Animals", "Heat Waves", "Dreamland", "021219103598717", 238000),
    ("Taylor Swift", "Anti-Hero", "Midnights", "0V1219103598718", 200000),
    ("Fleetwood Mac", "Dreams", "Rumours", "0W1219103598719", 257000),
    ("Gorillaz", "Feel Good Inc.", "Demon Days", "0X1219103598720", 222000),
    ("Kendrick Lamar", "HUMBLE.", "DAMN.", "0Y1219103598721", 177000),
    (
        "Billie Eilish",
        "bad guy",
        "WHEN WE ALL FALL ASLEEP, WHERE DO WE GO?",
        "0Z1219103598722",
        194000,
    ),
]


def generate_dummy_history(count: int = 500, username: str = "user_main") -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    base_time = datetime.utcnow() - timedelta(days=30)
    current_time = base_time

    for _ in range(count):
        artist, track, album, track_id, duration = random.choice(SAMPLE_ARTISTS_TRACKS)
        gap_seconds = random.randint(60, 10800)
        current_time += timedelta(seconds=gap_seconds)

        skipped = random.random() < 0.1
        ms_played = random.randint(10000, 40000) if skipped else duration

        records.append(
            {
                "ts": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "username": username,
                "platform": random.choice(["ios", "mac", "web_player"]),
                "ms_played": ms_played,
                "msPlayed": ms_played,
                "conn_country": "US",
                "trackName": track,
                "artistName": artist,
                "albumName": album,
                "master_metadata_track_name": track,
                "master_metadata_album_artist_name": artist,
                "master_metadata_album_album_name": album,
                "spotify_track_uri": f"spotify:track:{track_id}",
                "reason_start": "trackdone" if not skipped else "fwdbtn",
                "reason_end": "trackdone" if not skipped else "fwdbtn",
                "shuffle": random.choice([True, False]),
                "skipped": skipped,
                "offline": False,
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic Spotify streaming history JSON"
    )
    parser.add_argument("--count", type=int, default=500, help="Number of records to generate")
    parser.add_argument("--user", type=str, default="user_main", help="User profile tag")
    parser.add_argument(
        "--out", type=str, default="data/StreamingHistory_dummy.json", help="Output path"
    )
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    records = generate_dummy_history(count=args.count, username=args.user)
    out_path.write_text(json.dumps(records, indent=2))
    print(f"Generated {len(records)} dummy Spotify listening records at {out_path.resolve()}")


if __name__ == "__main__":
    main()
