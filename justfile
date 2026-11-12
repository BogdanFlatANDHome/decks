# Презентации Wolf Consult на GitHub Pages: https://bogdanflatandhome.github.io/decks/
# Порядок: правишь src/<имя>.bento.html в Bento → Save → just publish <имя> <сохранённый файл>

set shell := ["bash", "-euo", "pipefail", "-c"]

port := "8765"

default:
    @just --list

# Поведенческие тесты сборки
test:
    python3 -I tests/test_build.py

# Сайт целый: у каждой презентации есть панель стрелок, PDF и превью
lint:
    #!/usr/bin/env bash
    set -euo pipefail
    for f in src/*.bento.html; do
      n=$(basename "$f" .bento.html)
      grep -q 'id="deck-nav-js"' "$n.html" || { echo "нет стрелок: $n.html"; exit 1; }
      test -s "$n.pdf" || { echo "нет PDF: $n.pdf"; exit 1; }
      test -s "thumbs/$n.jpg" || { echo "нет превью: thumbs/$n.jpg"; exit 1; }
    done
    echo "lint ok"

# Тесты + проверка сайта — перед отправкой
check: test lint

# Собрать страницу сайта из исходника (без PDF): just build wolfchat
build name:
    python3 -I tools/build.py {{name}} src/{{name}}.bento.html .

# Снять слайды в браузере → <имя>.pdf и превью thumbs/<имя>.jpg (нужен playwright-cli)
pdf name:
    tools/shots.sh {{name}} {{port}}

# Пересобрать всё: страницы, PDF, превью
all:
    for f in src/*.bento.html; do n=$(basename "$f" .bento.html); just build "$n"; just pdf "$n"; done

# Опубликовать правку из Bento: забирает сохранённый файл в src/, собирает, делает PDF и отправляет на GitHub.
# Пример: just publish wolfchat ~/Загрузки/WolfChat_25.bento.html
publish name file="":
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -n "{{file}}" ]; then
      cp "{{file}}" "src/{{name}}.bento.html"
      sed -i 's/"readonly": *true/"readonly":false/' "src/{{name}}.bento.html"
    fi
    just build {{name}}
    just pdf {{name}}
    just check
    git add "src/{{name}}.bento.html" "{{name}}.html" "{{name}}.pdf" "thumbs/{{name}}.jpg"
    git commit -m "{{name}}: обновление презентации" || true
    git push
