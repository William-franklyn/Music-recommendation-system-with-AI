import logging
from typing import List, Dict, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


def _score_song(song: Dict, user_prefs: Dict) -> float:
    genre_score = 1.0 if song["genre"].lower() == user_prefs.get("genre", "").lower() else 0.0
    mood_score = 1.0 if song["mood"].lower() == user_prefs.get("mood", "").lower() else 0.0
    energy_score = 1.0 - abs(song["energy"] - user_prefs.get("energy", 0.5))
    acoustic_raw = song["acousticness"]
    acoustic_score = acoustic_raw if user_prefs.get("likes_acoustic", False) else (1.0 - acoustic_raw)

    return (0.35 * genre_score +
            0.30 * mood_score +
            0.25 * energy_score +
            0.10 * acoustic_score)


def _build_rule_explanation(song: Dict, user_prefs: Dict, score: float) -> str:
    parts = []
    if song["genre"].lower() == user_prefs.get("genre", "").lower():
        parts.append(f"matches your favorite genre ({song['genre']})")
    if song["mood"].lower() == user_prefs.get("mood", "").lower():
        parts.append(f"fits your '{song['mood']}' mood")
    energy_diff = abs(song["energy"] - user_prefs.get("energy", 0.5))
    if energy_diff < 0.1:
        parts.append("has very close energy to your target")
    elif energy_diff < 0.2:
        parts.append("has similar energy to your target")
    if not parts:
        parts.append("is a reasonable match for your overall taste")
    confidence = "High" if score >= 0.7 else "Medium" if score >= 0.45 else "Low" 
    return f"[Confidence: {confidence}] " + "; ".join(parts).capitalize() + "."


def load_songs(csv_path: str) -> List[Dict]:
    df = pd.read_csv(csv_path)
    songs = df.to_dict(orient="records")
    logger.info(f"Loaded {len(songs)} songs from {csv_path}")
    return songs


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    if not songs:
        logger.warning("recommend_songs called with empty song list")
        return []

    k = max(1, min(k, len(songs)))

    scored = []
    for song in songs:
        score = _score_song(song, user_prefs)
        explanation = _build_rule_explanation(song, user_prefs, score)
        scored.append((song, round(score, 4), explanation))

    scored.sort(key=lambda x: x[1], reverse=True)
    logger.info(f"Top result: '{scored[0][0]['title']}' score={scored[0][1]}")
    return scored[:k]
