"""Исходник Bento → страница сайта.

python3 -I tools/build.py <имя> <исходник.bento.html> <папка-вывода>

Делает <папка>/<имя>.html: только просмотр (readonly) + панель стрелок и кнопка PDF.
Исходник не меняет. Старую панель (если файл уже собирался) вырезает, чтобы не задвоить.
"""
import re
import sys
from pathlib import Path

NAV = (Path(__file__).resolve().parent / "nav.html").read_text(encoding="utf-8")
OLD_NAV = re.compile(
    r"\n?(<!-- deck-nav[:\s].*?)?<style id=\"deck-nav-css\">.*?<script id=\"deck-nav-js\".*?</script>\n?(<!-- deck-nav:end -->\n?)?",
    re.S,
)


def main() -> None:
    name, src, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    html = src.read_text(encoding="utf-8")
    html = OLD_NAV.sub("", html)
    html, n = re.subn(r'"readonly":\s*false', '"readonly":true', html, count=1)
    if n == 0 and not re.search(r'"readonly":\s*true', html):
        sys.exit(f"{src}: не нашёл флаг readonly в bento-doc")
    end = html.rfind("</body>")
    if end < 0:
        sys.exit(f"{src}: нет </body>")
    html = html[:end] + NAV.replace("__PDF__", f"{name}.pdf") + html[end:]
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.html").write_text(html, encoding="utf-8")
    print(f"собрано: {out / (name + '.html')}")


if __name__ == "__main__":
    main()
