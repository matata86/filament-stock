#!/bin/sh
# Render brand-src/icon.svg to custom_components/filament_stock/brand/*.png (headless Chrome, transparent).
set -e
cd "$(dirname "$0")"
out=../custom_components/filament_stock/brand
tmp=$(mktemp -d)
mkdir -p "$out"
for variant in light dark; do
  class=""; prefix=""
  [ "$variant" = dark ] && class=' class="dark"' && prefix=dark_
  for size in 256 512; do
    sed "s|<svg |<svg$class |; s|width=\"512\" height=\"512\"|width=\"$size\" height=\"$size\"|" icon.svg > "$tmp/i.svg"
    printf '<html><body style="margin:0;background:transparent">%s</body></html>' "$(cat "$tmp/i.svg")" > "$tmp/i.html"
    google-chrome --headless --disable-gpu --hide-scrollbars --default-background-color=00000000 \
      --window-size=$size,$size --screenshot="$tmp/i.png" "file://$tmp/i.html" 2>/dev/null
    name=icon; [ $size = 512 ] && name=icon@2x
    cp "$tmp/i.png" "$out/$prefix$name.png"
  done
done
rm -r "$tmp"
ls -l "$out"
