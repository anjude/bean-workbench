#!/usr/bin/env python3
"""Generate three quiet, original one-shot game effects and encode compact MP3s."""
import math
import random
import struct
import subprocess
import tempfile
import wave
from pathlib import Path

RATE = 44100
ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'effects'
random.seed(20261118)


def render(name, seconds, voice):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    samples = [voice(i / RATE, seconds) for i in range(round(RATE * seconds))]
    peak = max(max(map(abs, samples)), 1e-9)
    with tempfile.NamedTemporaryFile(suffix='.wav') as temp:
        with wave.open(temp.name, 'wb') as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(RATE)
            out.writeframes(b''.join(struct.pack('<h', int(x / peak * 18000)) for x in samples))
        subprocess.run([
            'ffmpeg', '-y', '-loglevel', 'error', '-i', temp.name,
            '-c:a', 'libmp3lame', '-b:a', '64k', '-ar', str(RATE),
            str(OUTPUT / f'{name}.mp3'),
        ], check=True)


def deploy(t, duration):
    # A gentle water plip: a dropping rounded tone plus a tiny splash.
    envelope = math.exp(-10 * t / duration)
    hz = 470 - 210 * min(1, t / duration)
    phase = 2 * math.pi * (470 * t - 105 * t * t / duration)
    splash = random.uniform(-1, 1) * math.exp(-45 * t / duration)
    return envelope * (.72 * math.sin(phase) + .16 * math.sin(phase * 2)) + .035 * splash


def clash(t, duration):
    # Two muted wooden taps, kept soft and short.
    value = 0.0
    for at, gain in ((0.0, .65), (.075, .35)):
        local = t - at
        if local >= 0:
            env = math.exp(-32 * local / duration)
            value += gain * env * (math.sin(2 * math.pi * 250 * local)
                                   + .22 * math.sin(2 * math.pi * 510 * local))
    return value


def score(t, duration):
    # A small two-note bell, warm rather than triumphant.
    value = 0.0
    for at, hz, gain in ((0.0, 587.33, .55), (.16, 783.99, .42)):
        local = t - at
        if local >= 0:
            env = min(1, local / .012) * math.exp(-5.4 * local / .32)
            value += gain * env * (math.sin(2 * math.pi * hz * local)
                                   + .18 * math.sin(2 * math.pi * hz * 2.01 * local))
    return value


if __name__ == '__main__':
    render('01-deploy', .28, deploy)
    render('02-clash', .24, clash)
    render('03-score', .62, score)
