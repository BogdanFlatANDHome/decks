"""Главная сайта из всех презентаций в src/.

python3 -I tools/index.py <корень-сайта>

Для каждого <корень>/src/<имя>.bento.html — карточка: превью thumbs/<имя>.jpg,
название (title из Bento до « — »), подпись (meta.subject, иначе остаток title),
цвет — акцент темы. Порядок — по названию.
"""
import json
import re
import sys
from html import escape
from pathlib import Path

TEMPLATE = (Path(__file__).resolve().parent / "index.template.html").read_text(encoding="utf-8")
DOC = re.compile(r'<script type="application/bento\+json" id="bento-doc">(.*?)</script>', re.S)

CARD = """    <article class="card" style="--accent: {accent}">
      <img class="thumb" src="thumbs/{name}.jpg" alt="Первый слайд: {title}" width="960" height="540" loading="lazy">
      <div class="body">
        <div class="title"><a href="{name}.html">{title}</a></div>
        <div class="desc">{desc}</div>
        <div class="row"><span class="open">Смотреть →</span><a class="pdf" href="{name}.pdf" download>PDF</a></div>
      </div>
    </article>"""


def card(src: Path) -> tuple[str, str]:
    name = src.name.removesuffix(".bento.html")
    d = json.loads(DOC.search(src.read_text(encoding="utf-8")).group(1))
    head, _, rest = d.get("title", name).partition(" — ")
    desc = (d.get("meta") or {}).get("subject") or rest
    accent = (d.get("theme") or {}).get("accent") or "#1d1c21"
    if not re.fullmatch(r"#[0-9A-Fa-f]{3,8}", accent):
        accent = "#1d1c21"
    return head, CARD.format(name=escape(name), title=escape(head), desc=escape(desc), accent=accent)


def main() -> None:
    root = Path(sys.argv[1])
    cards = sorted(card(p) for p in (root / "src").glob("*.bento.html"))
    page = TEMPLATE.split("\n", 1)[1].replace("__CARDS__", "\n".join(c for _, c in cards))
    (root / "index.html").write_text(page, encoding="utf-8")
    print(f"главная: {len(cards)} презентаций(и)")


if __name__ == "__main__":
    main()
