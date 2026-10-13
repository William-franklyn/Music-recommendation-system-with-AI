"""
Breaks down the weighted scoring formula (src/recommender.py _score_song)
factor by factor: genre, mood, energy, acoustic -- each raw sub-score,
its weight, and its weighted contribution to the final score.

Includes four preset examples, each engineered so one factor dominates
the total score, to demonstrate what each of the four weights actually
does in isolation.

Run with:
    python score_breakdown.py
"""

import sys

sys.path.insert(0, "src")

from recommender import load_songs

WEIGHTS = {"genre": 0.35, "mood": 0.30, "energy": 0.25, "acoustic": 0.10}


def breakdown(label: str, song: dict, user_prefs: dict) -> None:
    genre_score = 1.0 if song["genre"].lower() == user_prefs["genre"].lower() else 0.0
    mood_score = 1.0 if song["mood"].lower() == user_prefs["mood"].lower() else 0.0
    energy_score = 1.0 - abs(song["energy"] - user_prefs["energy"])
    acoustic_raw = song["acousticness"]
    acoustic_score = acoustic_raw if user_prefs["likes_acoustic"] else (1.0 - acoustic_raw)

    rows = [
        ("genre", genre_score, WEIGHTS["genre"]),
        ("mood", mood_score, WEIGHTS["mood"]),
        ("energy", energy_score, WEIGHTS["energy"]),
        ("acoustic", acoustic_score, WEIGHTS["acoustic"]),
    ]
    total = sum(w * s for _, s, w in rows)
    dominant = max(rows, key=lambda r: r[1] * r[2])

    print(f"\n=== {label} ===")
    print(f"Song: \"{song['title']}\" by {song['artist']} "
          f"(genre={song['genre']}, mood={song['mood']}, energy={song['energy']}, "
          f"acousticness={song['acousticness']})")
    print(f"User prefs: {user_prefs}")
    print(f"{'factor':<10}{'raw score':<12}{'weight':<10}{'contribution':<12}")
    for name, score, weight in rows:
        print(f"{name:<10}{score:<12.2f}{weight:<10.2f}{weight * score:<12.4f}")
    print(f"{'TOTAL':<10}{'':<12}{'':<10}{total:<12.4f}")
    print(f"-> '{dominant[0]}' drives {dominant[1] * dominant[2] / total:.0%} of this score")


if __name__ == "__main__":
    songs = load_songs("data/songs.csv")
    by_title = {s["title"]: s for s in songs}

    breakdown(
        "Genre isolated",
        by_title["Gym Hero"],
        {"genre": "pop", "mood": "chill", "energy": 0.0, "likes_acoustic": True},
    )
    breakdown(
        "Mood isolated",
        by_title["Storm Runner"],
        {"genre": "jazz", "mood": "intense", "energy": 0.0, "likes_acoustic": True},
    )
    breakdown(
        "Energy isolated",
        by_title["Night Drive Loop"],
        {"genre": "jazz", "mood": "relaxed", "energy": 0.75, "likes_acoustic": True},
    )
    breakdown(
        "Acoustic preference isolated",
        by_title["Gym Hero"],
        {"genre": "jazz", "mood": "chill", "energy": 0.0, "likes_acoustic": False},
    )
