"""Render the 12-second product video from the existing Goose Know assets."""

from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PRODUCT = ROOT / "business-repo/uni-gknow/src"
OUT = HERE / "gknow-food-wheel-sample.mp4"
PREVIEW = HERE / "preview"
W, H, FPS, DURATION = 720, 1280, 24, 12
BG, INK, MUTED, ORANGE = "#fff9ef", "#302c2a", "#746d68", "#e88430"
COLORS = ["#ffb84d", "#ff806b", "#78b9a7", "#8caee8", "#c58bd5", "#f07891", "#6db9cb", "#e5a44f"]
FOODS = ["煲仔饭", "肠粉", "云吞面", "客家菜", "川菜", "湘菜", "轻食沙拉", "糖水"]
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def text_center(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int, fill: str, anchor="mm") -> None:
    draw.text(xy, value, font=font(size), fill=fill, anchor=anchor)


def ease_out(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 4


def alpha_in(t: float, start: float, duration: float = .35) -> float:
    return max(0.0, min(1.0, (t - start) / duration))


def alpha_out(t: float, end: float, duration: float = .35) -> float:
    return max(0.0, min(1.0, (end - t) / duration))


def paste_alpha(base: Image.Image, layer: Image.Image, alpha: float) -> None:
    if alpha <= 0:
        return
    if alpha < 1:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda value: int(value * alpha)))
    base.alpha_composite(layer)


def goose(name: str, size: int) -> Image.Image:
    path = PRODUCT / "assets/expressions" / f"goose-{name}.png"
    image = Image.open(path).convert("RGBA")
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    return image


def base_frame() -> Image.Image:
    im = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.ellipse((-215, -245, 485, 455), fill="#fff0da")
    d.ellipse((510, 965, 1000, 1455), fill="#ffe9cc")
    d.ellipse((605, 60, 645, 100), fill="#ffcf83")
    d.ellipse((80, 1050, 104, 1074), fill="#f4bba4")
    return im


def wheel_image() -> Image.Image:
    s = 520
    im = Image.new("RGBA", (s, s))
    d = ImageDraw.Draw(im)
    box = (8, 8, s - 8, s - 8)
    for idx, color in enumerate(COLORS):
        start = -112.5 + idx * 45
        d.pieslice(box, start, start + 45, fill=color)
    cx = cy = s // 2
    for idx, food in enumerate(FOODS):
        theta = math.radians(-90 + idx * 45)
        x = cx + int(math.cos(theta) * 174)
        y = cy + int(math.sin(theta) * 174)
        text_center(d, (x, y), food, 21, "#493524")
    d.ellipse((cx - 57, cy - 57, cx + 57, cy + 57), fill="#493524", outline="#fffdf8", width=5)
    text_center(d, (cx, cy - 17), "吃什么", 22, "#fff7e8")
    text_center(d, (cx, cy + 18), "鹅拍板", 18, "#fff7e8")
    return im


WHEEL = wheel_image()
GOOSE_SNEAKY = goose("sneaky", 315)
GOOSE_HAPPY = goose("happy", 280)


def opening(t: float) -> Image.Image:
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((72, 156, 648, 1075), radius=58, fill="#ffffff", outline="#eadfce", width=3)
    d.rounded_rectangle((125, 211, 317, 260), radius=24, fill="#fff0da")
    text_center(d, (221, 236), "鹅懂个啥", 25, ORANGE)
    text_center(d, (360, 363), "今晚吃什么？", 67, INK)
    text_center(d, (360, 438), "别再说随便。", 36, MUTED)
    # Product character asset, with a subtle bob rather than a random expression.
    y = 545 + int(math.sin(t * 4) * 8)
    im.alpha_composite(GOOSE_SNEAKY, (W // 2 - GOOSE_SNEAKY.width // 2, y))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((188, 929, 532, 1008), radius=40, fill=ORANGE)
    text_center(d, (360, 969), "让鹅来拍板", 32, "#ffffff")
    return im


def phone(t: float) -> Image.Image:
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((65, 95, 655, 1160), radius=54, fill="#ffffff", outline="#eadfce", width=3)
    d.rounded_rectangle((93, 118, 627, 1135), radius=38, fill=BG)
    text_center(d, (360, 164), "大转盘", 29, INK)
    d.line((104, 206, 616, 206), fill="#eadfce", width=2)
    d.text((128, 237), "今天吃什么？", font=font(43), fill=INK)
    d.text((130, 305), "选好候选项，鹅来拍板。", font=font(24), fill=MUTED)
    d.ellipse((98, 364, 622, 888), fill="#fffdf8")
    spinning = 3.3 <= t < 7.5
    if t < 3.3:
        angle = 0
    elif spinning:
        angle = 1440 * ease_out((t - 3.3) / 4.2)
    else:
        angle = 1440
    disk = WHEEL.rotate(-angle, resample=Image.Resampling.BICUBIC, expand=False)
    im.alpha_composite(disk, (100, 366))
    d = ImageDraw.Draw(im)
    d.polygon([(360, 378), (337, 341), (383, 341)], fill="#e9684a")
    d.rounded_rectangle((130, 907, 590, 984), radius=38, fill=ORANGE)
    text_center(d, (360, 945), "正在转…" if spinning else "开始转" if t < 7.5 else "再转一次", 29, "#ffffff")
    d.rounded_rectangle((130, 1006, 590, 1108), radius=27, fill="#fff0da")
    if t >= 7.5:
        text_center(d, (360, 1032), "当前结果 · 鹅替你选好了", 18, ORANGE)
        text_center(d, (360, 1075), "煲仔饭", 39, INK)
    else:
        text_center(d, (360, 1036), "本轮结果", 18, ORANGE)
        text_center(d, (360, 1078), "转起来，鹅来拍板", 29, INK)
    return im


def ending() -> Image.Image:
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((75, 150, 645, 1070), radius=55, fill="#ffffff", outline="#eadfce", width=3)
    im.alpha_composite(GOOSE_HAPPY, (W // 2 - GOOSE_HAPPY.width // 2, 300))
    d = ImageDraw.Draw(im)
    text_center(d, (360, 674), "鹅懂个啥", 68, INK)
    text_center(d, (360, 754), "开心玩，顺便认识自己", 30, MUTED)
    d.rounded_rectangle((194, 836, 526, 907), radius=36, fill=ORANGE)
    text_center(d, (360, 872), "今天吃什么？", 30, "#ffffff")
    return im


def frame(t: float) -> Image.Image:
    im = base_frame()
    if t < 2.35:
        paste_alpha(im, opening(t), alpha_out(t, 2.35, .25))
    if 2.05 <= t < 10.0:
        paste_alpha(im, phone(t), alpha_in(t, 2.05, .3) * alpha_out(t, 10.0, .25))
    if t >= 9.7:
        paste_alpha(im, ending(), alpha_in(t, 9.7, .3))
    d = ImageDraw.Draw(im)
    if 2.6 < t < 7.45:
        text_center(d, (360, 1215), "转一下，鹅来拍板", 30, INK)
    elif 7.6 <= t < 9.7:
        text_center(d, (360, 1215), "好，今晚吃煲仔饭。", 30, INK)
    return im.convert("RGB")


def make_audio(path: Path) -> None:
    rate = 44100
    n = int(DURATION * rate)
    events: list[tuple[float, float, float, float]] = []
    # melody: time, duration, frequency, amplitude
    notes = [392, 493.88, 587.33, 493.88, 440, 523.25, 659.25, 587.33]
    for beat in range(24):
        events.append((beat * .5, .32, notes[beat % len(notes)], .085))
    for beat in range(12):
        events.append((beat, .08, 196, .045))
    click = 3.4
    while click < 7.45:
        events.append((click, .035, 800, .065))
        click += .19 + .13 * ((click - 3.4) / 4.05)
    for i, pitch in enumerate((523.25, 659.25, 783.99)):
        events.append((7.5 + i * .12, .4, pitch, .13))
    import array
    samples = array.array("h")
    for i in range(n):
        t = i / rate
        value = 0.0
        for start, duration, frequency, amplitude in events:
            dt = t - start
            if 0 <= dt < duration:
                envelope = (1 - dt / duration) ** 2
                value += amplitude * envelope * (math.sin(2 * math.pi * frequency * dt) + .22 * math.sin(4 * math.pi * frequency * dt))
        samples.append(int(max(-.95, min(.95, value)) * 32767))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(samples.tobytes())


def main() -> None:
    PREVIEW.mkdir(exist_ok=True)
    audio = HERE / "sample-audio.wav"
    make_audio(audio)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(audio), "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(OUT)]
    with subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE) as process:
        assert process.stdin is not None
        for index in range(FPS * DURATION):
            t = index / FPS
            image = frame(t)
            if index in (0, 48, 96, 168, 192, 264):
                image.save(PREVIEW / f"frame-{index:03d}.png")
            process.stdin.write(image.tobytes())
        process.stdin.close()
        error = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
        if process.wait() != 0:
            raise RuntimeError(error[-3000:])
    print(OUT)


if __name__ == "__main__":
    main()
