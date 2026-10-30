"""Make the Claude artifact's framed copy of the game (the phone preview): src/game.html wrapped in the same page
skeleton the artifact host adds to a published page (doctype, charset, viewport, small reset).

  python3 -I src/artifact/mk.py      writes dist/artifact/game.html (git-ignored)

The artifact page itself (src/artifact/preview.html) loads game.html beside it in a phone-sized frame."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open(os.path.join(ROOT, 'src', 'game.html'), encoding='utf-8').read()
head = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
        'body{margin:0;font:14px system-ui,-apple-system,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>'
        '</head><body>')
out = os.path.join(ROOT, 'dist', 'artifact')
os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'game.html'), 'w', encoding='utf-8', newline='\n').write(head + src + '</body></html>')
print('game.html', round(len(head + src) / 1e6, 2), 'MB ->', os.path.relpath(os.path.join(out, 'game.html'), ROOT))
