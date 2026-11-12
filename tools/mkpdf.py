"""Скриншоты слайдов → PDF (одна страница на слайд) + превью первого слайда.

python3 -I tools/mkpdf.py <папка-с-png> <выход.pdf> <превью.jpg>
"""
import sys
from pathlib import Path

from PIL import Image


def main() -> None:
    shots = sorted(Path(sys.argv[1]).glob("s*.png"))
    if not shots:
        sys.exit("нет скриншотов")
    pages = [Image.open(p).convert("RGB") for p in shots]
    pdf, thumb = Path(sys.argv[2]), Path(sys.argv[3])
    pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=144)
    thumb.parent.mkdir(parents=True, exist_ok=True)
    t = pages[0].copy()
    t.thumbnail((960, 540))
    t.save(thumb, quality=85, optimize=True)
    print(f"{pdf.name}: {len(pages)} стр.; превью {thumb}")


if __name__ == "__main__":
    main()
