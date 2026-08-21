"""Generate Russian neural TTS clips with edge-tts (optional)."""

from __future__ import annotations

import asyncio
from pathlib import Path

CLIPS = [
    (
        "hook.mp3",
        "Отчёты полны цифр. А что делать с бизнесом — неясно.",
    ),
    (
        "problem.mp3",
        "Выручка, расходы, клиенты. Искать вручную — значит опоздать.",
    ),
    (
        "solution.mp3",
        "Загрузите таблицу — и получите понятную картину бизнеса.",
    ),
    (
        "metrics.mp3",
        "Показатели на одном экране. Падение ценности клиента видно сразу.",
    ),
    (
        "analyst.mp3",
        "Спросите своими словами — получите причину и что делать.",
    ),
    (
        "telegram.mp3",
        "Отчёт придёт в Telegram. Цифры всегда под рукой.",
    ),
    (
        "offer.mp3",
        "KPI Pulse — ваш AI-аналитик бизнеса. Попробуйте.",
    ),
]

VOICE = "ru-RU-DmitryNeural"
OUT = Path(__file__).resolve().parents[1] / "assets" / "voiceover"


async def synthesize() -> None:
    try:
        import edge_tts
    except ImportError as exc:
        raise SystemExit(
            "Установите edge-tts: pip install edge-tts\n"
            "Видео можно собрать без голоса: npm run build:silent"
        ) from exc

    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in CLIPS:
        path = OUT / name
        communicate = edge_tts.Communicate(text, VOICE, rate="+15%", pitch="+4Hz")
        await communicate.save(str(path))
        try:
            from mutagen.mp3 import MP3

            length = MP3(str(path)).info.length
        except Exception:
            length = 0.0
        print(f"Wrote {path}  ({length:.2f}s)")


if __name__ == "__main__":
    asyncio.run(synthesize())
