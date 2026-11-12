#!/usr/bin/env bash
# Снимает каждый слайд собранной страницы <имя>.html в браузере (playwright-cli)
# и собирает <имя>.pdf + превью первого слайда thumbs/<имя>.jpg.
# tools/shots.sh <имя> [порт]
set -euo pipefail
name=$1
port=${2:-8765}
root=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d)
cd "$root"
test -f "$name.html" || { echo "нет $name.html — сначала just build $name"; exit 1; }

total=$(python3 -I -c '
import re, json, sys
s = open(sys.argv[1], encoding="utf-8").read()
d = json.loads(re.search(r"<script type=\"application/bento\+json\" id=\"bento-doc\">(.*?)</script>", s, re.S).group(1))
print(sum(1 for x in d["slides"] if not x.get("hidden")))' "$name.html")

python3 -I -m http.server "$port" --bind 127.0.0.1 --directory "$root" >/dev/null 2>&1 &
srv=$!
pw() { playwright-cli -s=decks-shots "$@" >/dev/null 2>&1; }
cleanup() { pw close || true; kill "$srv" 2>/dev/null || true; rm -rf "$work"; }
trap cleanup EXIT
sleep 1

pw open "about:blank"
pw resize 1920 1080
hide='() => { const s = document.createElement("style"); s.textContent = "#deck-nav, .reveal .slide-number, .reveal .progress { display: none !important }"; document.head.appendChild(s) }'
for ((i = 0; i < total; i++)); do
  pw goto "http://127.0.0.1:$port/$name.html#/$i"
  sleep 2.5
  pw eval "$hide"
  sleep 0.3
  pw screenshot --filename="$work/$(printf 's%03d' "$i").png"
done
pw close

python3 -I "$root/tools/mkpdf.py" "$work" "$root/$name.pdf" "$root/thumbs/$name.jpg"
