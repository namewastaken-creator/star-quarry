#!/usr/bin/env python3
"""Run the standard checks against the built game in the repository root (run src/build.py first).

  python3 -I tools/check.py           the ten browser tests in tools/tests/ plus the overlap check (tools/occcheck.py)
  python3 -I tools/check.py pwobj     just the named tests (occcheck included only if named)

Each test serves the repository root on its own localhost port, opens the game in headless Chromium (Playwright) and
prints its findings; a test passes when it prints no page errors. Screenshots go to out/ (git-ignored).
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# the game's text includes characters like U+202F; Windows pipes default to cp1252, which can't print them
sys.stdout.reconfigure(errors='backslashreplace')
TESTS = ['pwobj', 'pwchip', 'pwmed', 'pwtab', 'pwsave', 'pwland', 'pwrc', 'pwneb', 'pwpark2', 'pwaudit']
want = sys.argv[1:] or TESTS + ['occcheck']
bad = []
for k, name in enumerate(want):
    port = str(8710 + k)
    path = os.path.join(HERE, 'occcheck.py' if name == 'occcheck' else os.path.join('tests', name + '.py'))
    args = [sys.executable, '-I', '-X', 'utf8', path, port] + (['390'] if name == 'pwaudit' else [])
    try:
        r = subprocess.run(args, capture_output=True, encoding='utf-8', errors='replace', timeout=600)
        out = (r.stdout + r.stderr).strip().splitlines()
        last = out[-1] if out else ''
        ok = r.returncode == 0 and (('ALL PASS' in last) if name == 'occcheck' else
                                    any(t in last for t in ('errors []', 'errs []')))
    except subprocess.TimeoutExpired:
        ok, last = False, 'timed out'
    print(f'{"PASS" if ok else "FAIL"}  {name:9s} {last[:160]}')
    if not ok: bad.append(name)
print('ALL CHECKS PASS' if not bad else f'{len(bad)} FAILED: {", ".join(bad)}')
sys.exit(1 if bad else 0)
