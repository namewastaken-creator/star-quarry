"""Guide check, run by build.py: warns when gameplay code changed but the user guide (GUIDE) didn't.

Fingerprints the gameplay sections of src/game.html (DATA, STATE, ECONOMY, EVENTS, STATION THRUSTERS;
comment lines, the change log and the version number left out) and the GUIDE text, and compares them with
src/guide_state.json from the last time they were in step.
  - guide changed too  -> state updated silently
  - rules changed only -> WARNING every build until the guide is updated, or until
                          `python3 -I src/build.py --guide-ok` records that the change doesn't affect the guide
"""
import re, json, hashlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'game.html')
STATE = os.path.join(HERE, 'guide_state.json')

def section(s, start, end):
    a = s.index(f'/* ===================== {start} ====')
    b = s.index(f'/* ===================== {end} ====', a)
    return s[a:b]

def rules_text(s):
    parts = [section(s, 'DATA', 'FORMAT'), section(s, 'STATION THRUSTERS', 'STATION NAME')]
    out = []
    for line in '\n'.join(parts).split('\n'):
        t = line.strip()
        if not t or t.startswith('//') or t.startswith('/*') or t.startswith('*') or t.endswith('*/'):
            continue
        if t.startswith('const CHANGES=') or 'APP_VER=' in t:
            continue
        out.append(t)
    return '\n'.join(out)

def guide_text(s):
    a = s.index('const GUIDE=[')
    return s[a:s.index('\nfunction showGuide', a)]

def h(t):
    return hashlib.sha256(t.encode()).hexdigest()[:16]

def check(ack=False):
    s = open(SRC, encoding='utf-8').read()  # explicit, or Windows reads cp1252 and the fingerprints differ
    now = {'rules': h(rules_text(s)), 'guide': h(guide_text(s))}
    old = json.load(open(STATE, encoding='utf-8')) if os.path.exists(STATE) else None
    if old is None or ack or now['guide'] != old['guide'] or now['rules'] == old['rules']:
        json.dump(now, open(STATE, 'w', encoding='utf-8', newline='\n'))
        if ack and old and now['rules'] != old['rules']:
            print('guide check: gameplay change recorded as not affecting the user guide')
        return True
    print('\n' + '!' * 72)
    print('WARNING: gameplay code changed since the user guide was last updated.')
    print('Check GUIDE in src/game.html (Warp tab > User guide, incl. Tips and tricks)')
    print('and update any section this change affects. If nothing in it is affected,')
    print('rebuild with:  python3 -I src/build.py --guide-ok')
    print('!' * 72 + '\n')
    return False

if __name__ == '__main__':
    check('--guide-ok' in sys.argv)
