#!/usr/bin/env python3
"""Star Quarry version bump: Major.Minor.Patch.Build. Run before every publish, then run build.py.

  python3 -I src/bump.py "what changed"              patch +1 (fixes and tweaks, including visual polish)
  python3 -I src/bump.py "one change" --and "another"  one version that lists several changes (any number of --and)
  python3 -I src/bump.py --minor "what changed"      minor +1, patch 0 (a new feature or block of content)
  python3 -I src/bump.py --major "what changed"      major +1, minor and patch 0 (an overhaul, or leaving beta)
  python3 -I src/bump.py --important "fix"           also marks the change important: open games ask players to
                                                     update (at most once a day); other changes install quietly
  python3 -I src/bump.py --sync                      no new version: rewrite the game's CHANGES from changelog.json

The build number (APP_VER.n) rises by one on every bump, whatever else changes, and is what update checks compare.
Major 0 is shown as "Beta"; from major 1 the name is just the number.
Each change-log entry is {d: date, v: version, t: what changed, imp: important}. A version with several changes also
has l, the list of them, and t is those sentences joined with spaces, so anything that reads only t (older games
reading version.json, preflight) still gets the whole note. The What's changed window lists l under the version.
The change log's source of truth is src/changelog.json (newest first). This script writes it into src/game.html as
CHANGES (shown from the Warp tab); build.py writes the last 40 entries into version.json.
Paths are relative to the repository root, so it runs from any clone and any folder.
"""
import datetime, json, os, re, sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(HERE, 'game.html')
LOG = os.path.join(HERE, 'changelog.json')


def main():
    args = sys.argv[1:]
    flags = {a for a in args if a.startswith('--')} - {'--and'}
    # the change text, split into separate changes at each --and (unquoted words within one change still join)
    notes, cur_words = [], []
    for a in args + ['--and']:
        if a == '--and':
            notes.append(' '.join(cur_words).strip()); cur_words = []
        elif not a.startswith('--'):
            cur_words.append(a)
    if len(notes) > 1 and not all(notes):
        sys.exit('bump: each --and needs a change on both sides, e.g.  "one change" --and "another"')
    notes = [x for x in notes if x]
    note = ' '.join(notes)
    unknown = flags - {'--minor', '--major', '--important', '--sync'}
    if unknown:
        sys.exit(f'bump: unknown option {", ".join(sorted(unknown))}')
    s = open(GAME, encoding='utf-8').read()
    log = json.load(open(LOG, encoding='utf-8'))
    m = re.search(r"const APP_VER=\{name:'([^']*)',n:(\d+)\};", s)
    if not m:
        sys.exit('bump: APP_VER not found in src/game.html')
    cur, n = m.group(1), int(m.group(2))
    if '--sync' in flags:
        if note or flags - {'--sync'}:
            sys.exit('bump: --sync takes no change text or other options')
        name = cur
    else:
        if not note:
            sys.exit('bump: say what changed, e.g.  python3 -I src/bump.py "Fix: ..."')
        v = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', cur)
        if not v:
            sys.exit(f'bump: current version {cur!r} is not Major.Minor.Patch.Build')
        ma, mi, pa, b = [int(x) for x in v.groups()]
        if b != n:
            sys.exit(f'bump: build {b} in {cur!r} does not match n={n}')
        if '--major' in flags: ma, mi, pa = ma + 1, 0, 0
        elif '--minor' in flags: mi, pa = mi + 1, 0
        else: pa += 1
        n += 1
        name = f'Beta {ma}.{mi}.{pa}.{n}' if ma == 0 else f'{ma}.{mi}.{pa}.{n}'
        s = s.replace(m.group(0), f"const APP_VER={{name:'{name}',n:{n}}};")
        today = datetime.datetime.now(ZoneInfo('America/Chicago')).date().isoformat()
        e = {'d': today, 'v': name, 't': note, **({'l': notes} if len(notes) > 1 else {})}
        if '--important' in flags:
            e['imp'] = True
        log.insert(0, e)
        json.dump(log, open(LOG, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=0)
    changes = 'const CHANGES=' + json.dumps(log, ensure_ascii=False, separators=(',', ':')) + ';\n'
    s, k = re.subn(r"const CHANGES=\[.*?\];\n", lambda _: changes, s, count=1, flags=re.S)
    if not k:
        sys.exit('bump: CHANGES not found in src/game.html')
    open(GAME, 'w', encoding='utf-8', newline='\n').write(s)
    print(('synced' if '--sync' in flags else 'version'), name, 'build', n, '| changelog entries', len(log))


if __name__ == '__main__':
    main()
