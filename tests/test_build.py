"""Поведенческие тесты сборки: исходник Bento → страница сайта.

Шов — CLI `tools/build.py <имя> <исходник.bento.html> <папка-вывода>`.
Запуск: just test
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "wolfchat.bento.html"


def doc(html: str) -> dict:
    m = re.search(r'<script type="application/bento\+json" id="bento-doc">(.*?)</script>', html, re.S)
    return json.loads(m.group(1))


def build(name: str, src: Path, out: Path) -> str:
    subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "build.py"), name, str(src), str(out)], check=True)
    return (out / f"{name}.html").read_text(encoding="utf-8")


def test_page_gets_nav_pdf_and_is_readonly():
    with tempfile.TemporaryDirectory() as t:
        html = build("wolfchat", SRC, Path(t))
        assert html.count('id="deck-nav-js"') == 1, "панель стрелок вставлена ровно один раз"
        assert 'data-pdf="wolfchat.pdf"' in html, "кнопка PDF ведёт на свой файл"
        assert doc(html)["readonly"] is True, "на сайте презентация только для просмотра"


def test_page_has_back_button_to_all_products():
    with tempfile.TemporaryDirectory() as t:
        html = build("wolfchat", SRC, Path(t))
        assert 'class="deck-nav-home" href="./"' in html, "в панели есть кнопка назад к списку презентаций"


def test_index_lists_every_deck_from_src():
    with tempfile.TemporaryDirectory() as t:
        out = Path(t)
        (out / "src").mkdir()
        for n in ("wolfchat", "dubli-gostey"):
            (out / "src" / f"{n}.bento.html").write_text(
                (ROOT / "src" / f"{n}.bento.html").read_text(encoding="utf-8"), encoding="utf-8")
        # новая презентация: своё название, подпись и акцент
        new = (ROOT / "src" / "wolfchat.bento.html").read_text(encoding="utf-8")
        d = doc(new)
        d["title"], d["meta"]["subject"], d["theme"]["accent"] = "Новый продукт — что-то", "Подпись нового", "#123456"
        m = re.search(r'(<script type="application/bento\+json" id="bento-doc">)(.*?)(</script>)', new, re.S)
        new = new[:m.start(2)] + json.dumps(d, ensure_ascii=False) + new[m.end(2):]
        (out / "src" / "novyy.bento.html").write_text(new, encoding="utf-8")

        subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "index.py"), str(out)], check=True)
        html = (out / "index.html").read_text(encoding="utf-8")
        for n in ("wolfchat", "dubli-gostey", "novyy"):
            assert f'href="{n}.html"' in html and f'href="{n}.pdf"' in html and f'src="thumbs/{n}.jpg"' in html, n
        assert ">Новый продукт<" in html, "название — часть title до тире"
        assert "Подпись нового" in html and "--accent: #123456" in html
        assert ">WolfChat<" in html and "WhatsApp, Telegram и MAX в Битрикс24" in html


def test_rebuild_from_published_page_does_not_duplicate_nav():
    with tempfile.TemporaryDirectory() as t:
        first = build("wolfchat", SRC, Path(t))
        tmp_src = Path(t) / "again.bento.html"
        tmp_src.write_text(first, encoding="utf-8")
        second = build("wolfchat", tmp_src, Path(t))
        assert second.count('id="deck-nav-js"') == 1
        assert second.count('id="deck-nav-css"') == 1


def test_source_stays_editable_and_slides_unchanged():
    before = SRC.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as t:
        html = build("wolfchat", SRC, Path(t))
    assert SRC.read_text(encoding="utf-8") == before, "исходник не трогаем"
    assert doc(before)["readonly"] is False
    assert doc(html)["slides"] == doc(before)["slides"], "слайды те же"


def test_last_slide_links_to_all_products():
    for name in ("wolfchat", "dubli-gostey"):
        last = doc((ROOT / "src" / f"{name}.bento.html").read_text(encoding="utf-8"))["slides"][-1]
        links = [e["html"] for e in last["elements"] if "decks/" in str(e.get("html", ""))]
        assert links and "Другие продукты Wolf Consult" in links[0], name


if __name__ == "__main__":
    fails = 0
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            try:
                f()
                print("PASS", n)
            except Exception as e:  # noqa: BLE001
                fails += 1
                print("FAIL", n, "—", repr(e))
    sys.exit(1 if fails else 0)
