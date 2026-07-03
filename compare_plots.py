"""
Stitch before/after plots side-by-side to show the AnswerSurvival packer fix's impact.

Pairs every PNG in plots_before_fix/ with the same-named PNG in plots/ (regenerated
with the fixed packer), labels each half "BEFORE FIX" / "AFTER FIX", and writes the
combined image to plots_comparison/.

Usage:
  python compare_plots.py
  python compare_plots.py --before plots_before_fix --after plots --out plots_comparison
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LABEL_HEIGHT = 40
GAP = 8
BG = (255, 255, 255)
BEFORE_COLOR = (200, 40, 40)
AFTER_COLOR = (30, 140, 30)


def _font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def stitch(before_path: Path, after_path: Path, out_path: Path):
    before_img = Image.open(before_path).convert("RGB")
    after_img = Image.open(after_path).convert("RGB")

    h = max(before_img.height, after_img.height)
    w = before_img.width + after_img.width + GAP

    canvas = Image.new("RGB", (w, h + LABEL_HEIGHT), BG)
    draw = ImageDraw.Draw(canvas)
    font = _font(22)

    draw.rectangle([0, 0, before_img.width, LABEL_HEIGHT], fill=(255, 235, 235))
    draw.text((10, 8), "BEFORE FIX", fill=BEFORE_COLOR, font=font)
    canvas.paste(before_img, (0, LABEL_HEIGHT))

    x2 = before_img.width + GAP
    draw.rectangle([x2, 0, x2 + after_img.width, LABEL_HEIGHT], fill=(230, 250, 230))
    draw.text((x2 + 10, 8), "AFTER FIX", fill=AFTER_COLOR, font=font)
    canvas.paste(after_img, (x2, LABEL_HEIGHT))

    out_path.parent.mkdir(exist_ok=True, parents=True)
    canvas.save(out_path)


def run(before_dir: str, after_dir: str, out_dir: str):
    before, after, out = Path(before_dir), Path(after_dir), Path(out_dir)
    if not before.exists():
        raise FileNotFoundError(f"{before} not found -- nothing to compare against.")

    paired, skipped = 0, 0
    for before_png in sorted(before.glob("*.png")):
        after_png = after / before_png.name
        if not after_png.exists():
            skipped += 1
            continue
        stitch(before_png, after_png, out / before_png.name)
        paired += 1
        print(f"  {before_png.name}")

    print(f"\n{paired} comparison images written to {out}/ ({skipped} skipped -- no matching 'after' plot yet)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=str, default="plots_before_fix")
    parser.add_argument("--after", type=str, default="plots")
    parser.add_argument("--out", type=str, default="plots_comparison")
    args = parser.parse_args()
    run(args.before, args.after, args.out)
