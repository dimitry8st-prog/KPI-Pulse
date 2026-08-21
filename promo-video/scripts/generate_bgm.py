"""Original royalty-free corporate pulse bed for the KPI Pulse promo."""

from __future__ import annotations

import math
import wave
from pathlib import Path

import numpy as np

SAMPLE_RATE = 44100
DURATION = 36.0
BPM = 96.0


def env(n: int, attack: float, release: float) -> np.ndarray:
    a = max(1, int(attack * SAMPLE_RATE))
    r = max(1, int(release * SAMPLE_RATE))
    out = np.ones(n, dtype=np.float64)
    out[:a] = np.linspace(0, 1, a)
    if r < n:
        out[-r:] = np.linspace(1, 0, r)
    return out


def sine(freq: float, n: int) -> np.ndarray:
    t = np.arange(n) / SAMPLE_RATE
    return np.sin(2 * math.pi * freq * t)


def noise(n: int) -> np.ndarray:
    rng = np.random.default_rng(8)
    return rng.uniform(-1, 1, n)


def lowpass(signal: np.ndarray, cutoff: float) -> np.ndarray:
    rc = 1.0 / (2 * math.pi * cutoff)
    dt = 1.0 / SAMPLE_RATE
    alpha = dt / (rc + dt)
    out = np.zeros_like(signal)
    acc = 0.0
    for i, sample in enumerate(signal):
        acc += alpha * (sample - acc)
        out[i] = acc
    return out


def place(dest: np.ndarray, start: int, src: np.ndarray) -> None:
    end = min(len(dest), start + len(src))
    dest[start:end] += src[: end - start]


def main() -> None:
    n = int(DURATION * SAMPLE_RATE)
    beat = 60.0 / BPM
    left = np.zeros(n)
    right = np.zeros(n)

    chords = [
        [110.00, 164.81, 220.00, 329.63],  # Am
        [87.31, 130.81, 174.61, 261.63],  # F
        [130.81, 164.81, 196.00, 261.63],  # C
        [98.00, 146.83, 196.00, 246.94],  # G
    ]
    bar = beat * 4

    # Warm pads
    for bar_i in range(int(DURATION / bar) + 1):
        chord = chords[bar_i % 4]
        start = int(bar_i * bar * SAMPLE_RATE)
        length = int(bar * SAMPLE_RATE * 1.05)
        pad = np.zeros(length)
        for freq in chord:
            pad += 0.09 * sine(freq, length)
            pad += 0.04 * sine(freq * 2, length)
        pad *= env(length, 0.12, 0.45)
        place(left, start, pad * 0.92)
        place(right, start, pad * 1.08)

    # Soft kick + hat
    for i, t0 in enumerate(np.arange(0, DURATION, beat)):
        start = int(t0 * SAMPLE_RATE)
        if i % 2 == 0:
            kn = int(0.18 * SAMPLE_RATE)
            t = np.arange(kn) / SAMPLE_RATE
            kick = np.sin(2 * math.pi * (62 * np.exp(-18 * t)) * t) * env(kn, 0.002, 0.16)
            place(left, start, kick * 0.22)
            place(right, start, kick * 0.22)
        hn = int(0.04 * SAMPLE_RATE)
        hat = lowpass(noise(hn), 9000) * env(hn, 0.001, 0.03) * (0.035 if i % 2 else 0.02)
        place(left, start, hat * 0.8)
        place(right, start, hat)

    # Light pentatonic motif
    melody = [329.63, 392.00, 440.00, 523.25, 440.00, 392.00, 349.23, 329.63]
    for i, t0 in enumerate(np.arange(0, DURATION, beat * 2)):
        freq = melody[i % len(melody)]
        start = int(t0 * SAMPLE_RATE)
        ln = int(0.55 * SAMPLE_RATE)
        note = 0.07 * sine(freq, ln) + 0.03 * sine(freq * 2.01, ln)
        note *= env(ln, 0.02, 0.28)
        place(left, start, note)
        place(right, start + 80, note * 0.85)

    # Master fade + limiter
    fade_in = env(n, 0.8, 2.4)
    mix_l = np.clip(left * fade_in * 0.85, -0.95, 0.95)
    mix_r = np.clip(right * fade_in * 0.85, -0.95, 0.95)

    out_dir = Path(__file__).resolve().parents[1] / "assets" / "music"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "kpi-pulse-bed.wav"
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        interleaved = np.empty(n * 2, dtype=np.int16)
        interleaved[0::2] = (mix_l * 32767).astype(np.int16)
        interleaved[1::2] = (mix_r * 32767).astype(np.int16)
        wav.writeframes(interleaved.tobytes())
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
