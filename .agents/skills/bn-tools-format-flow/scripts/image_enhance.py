#!/usr/bin/env python3
"""图片增强工具：水印、裁剪适配、封面比例裁切。用于公众号排版配图环节。"""
import argparse
import sys
from PIL import Image, ImageDraw, ImageFont


def add_watermark(input_path, output_path, text):
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font_size = max(16, int(w / 28))
    try:
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    margin = int(w * 0.03)
    x, y = w - tw - margin, h - th - margin
    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 110))
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 200))
    out = Image.alpha_composite(img, layer).convert("RGB")
    out.save(output_path)
    print(f"水印完成: {output_path} ({out.size[0]}x{out.size[1]})")


def resize_fit(input_path, output_path, max_width):
    img = Image.open(input_path).convert("RGB")
    w, h = img.size
    if w <= max_width:
        img.save(output_path)
        print(f"无需缩放: {output_path} ({w}x{h})")
        return
    new_h = int(h * max_width / w)
    img = img.resize((max_width, new_h), Image.LANCZOS)
    img.save(output_path)
    print(f"缩放完成: {output_path} ({max_width}x{new_h})")


def cover_crop(input_path, output_path, ratio):
    """按目标宽高比居中裁切，用于把 ImageGen 产出的约 3:2 封面裁成公众号 2.35:1。"""
    if ratio <= 0:
        raise ValueError("封面比例必须大于零")
    img = Image.open(input_path).convert("RGB")
    w, h = img.size
    target_h = int(w / ratio)
    if target_h >= h:
        # 宽度方向不够，改按高度算宽度
        target_w = int(h * ratio)
        if target_w >= w:
            img.save(output_path)
            print(f"无需裁切(已满足比例): {output_path} ({w}x{h})")
            return
        left = (w - target_w) // 2
        img = img.crop((left, 0, left + target_w, h))
    else:
        top = (h - target_h) // 2
        img = img.crop((0, top, w, top + target_h))
    img.save(output_path)
    print(f"封面裁切完成: {output_path} ({img.size[0]}x{img.size[1]}), 比例 {ratio}:1")


def main():
    p = argparse.ArgumentParser(description="图片增强：水印 / 裁剪适配 / 封面比例裁切")
    p.add_argument("input", help="输入图片路径")
    p.add_argument("output", help="输出图片路径")
    p.add_argument("--watermark", action="store_true", help="添加文字水印")
    p.add_argument("--text", default="公众号", help="水印文字")
    p.add_argument("--resize", action="store_true", help="缩放到最大宽度")
    p.add_argument("--max-width", type=int, default=677, help="最大宽度(px)")
    p.add_argument("--cover-crop", action="store_true", help="按目标比例居中裁切为封面")
    p.add_argument("--ratio", type=float, default=2.35, help="封面目标宽高比(默认2.35)")
    args = p.parse_args()

    if args.watermark:
        add_watermark(args.input, args.output, args.text)
    elif args.resize:
        resize_fit(args.input, args.output, args.max_width)
    elif args.cover_crop:
        cover_crop(args.input, args.output, args.ratio)
    else:
        print("请指定 --watermark / --resize / --cover-crop", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
