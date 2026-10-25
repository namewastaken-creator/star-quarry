#!/usr/bin/env python3
"""Star Quarry version bump: Major.Minor.Patch.Build.

  python3 -I tools/bump.py "what changed"              patch +1 (fixes and tweaks)
  python3 -I tools/bump.py --minor "what changed"      minor +1, patch 0 (a new feature or block of content)
  python3 -I tools/bump.py --major "what changed"      major +1, minor and patch 0 (overhaul, or leaving beta)
  python3 -I tools/bump.py --important ...             also marks the change important (players are asked to update)
  python3 -I tools/bump.py --sync                      no new version: rewrite version.json and the sw.js cache key

The build number (APP_VER.n) rises by one on every bump, whatever else changes, and is what update checks compare.
Major 0 is shown as "Beta"; from major 1 the name is just the number.
The change log lives in index.html as CHANGES (newest first); version.json carries the last 40 entries.
Run from anywhere: paths are relative to the repository root (this file's parent folder).
"""
import datetime, hashlib, json, os, re, sys
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME, VJSON, SW = (os.path.join(ROOT, f) for f in ('index.html', 'version.json', 'sw.js'))

def parts(name):
    m = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', name)
    if not m: sys.exit(f'bump: current version {name!r} is not Major.Minor.Patch.Build')
    return [int(x) for x in m.groups()]

def vname(ma, mi, pa, b):
    return (f'Beta {ma}.{mi}.{pa}.{b}' if ma == 0 else f'{ma}.{mi}.{pa}.{b}')

def main():
    args = sys.argv[1:]
    flags = {a for a in args if a.startswith('--')}
    text = ' '.join(a for a in args if not a.startswith('--')).strip()
    unknown = flags - {'--minor', '--major', '--important', '--sync'}
    if unknown: sys.exit(f'bump: unknown option {", ".join(sorted(unknown))}')
    s = open(GAME, encoding='utf-8').read()
    m = re.search(r"const APP_VER=\{name:'([^']*)',n:(\d+)\}", s)
    i = s.index('const CHANGES=') + len('const CHANGES=')
    j = s.index('];', i) + 1
    ch = json.loads(s[i:j])
    name, n = m.group(1), int(m.group(2))
    if '--sync' not in flags:
        if not text: sys.exit('bump: say what changed, e.g. bump.py "Fixed the hire button"')
        ma, mi, pa, b = parts(name)
        if b != n: sys.exit(f'bump: build {b} in the name does not match n={n}')
        if '--major' in flags: ma, mi, pa = ma + 1, 0, 0
        elif '--minor' in flags: mi, pa = mi + 1, 0
        else: pa += 1
        n += 1
        name = vname(ma, mi, pa, n)
        e = {'d': datetime.datetime.now(ZoneInfo('America/Chicago')).date().isoformat(), 'v': name, 't': text}
        if '--important' in flags: e['imp'] = True
        ch.insert(0, e)
        s = s[:i] + json.dumps(ch, ensure_ascii=False, separators=(',', ':')) + s[j:]
        s = s[:m.start()] + f"const APP_VER={{name:'{name}',n:{n}}}" + s[m.end():]
        open(GAME, 'w', encoding='utf-8').write(s)
    log = [{k: c[k] for k in ('v', 't', 'imp') if k in c} for c in ch if c.get('v')][:40]
    notes = ch[0]['t'] if ch and ch[0].get('v') == name else ''
    with open(VJSON, 'w', encoding='utf-8') as f:
        json.dump({'name': name, 'n': n, 'notes': notes, 'log': log}, f, ensure_ascii=False)
    key = hashlib.sha1(s.encode('utf-8')).hexdigest()[:10]
    sw = open(SW, encoding='utf-8').read()
    sw = re.sub(r"const CACHE='starquarry-[0-9a-f]+'", f"const CACHE='starquarry-{key}'", sw)
    open(SW, 'w', encoding='utf-8').write(sw)
    print(f'{name} (build {n})')

main()
