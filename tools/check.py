#!/usr/bin/env python3
"""Run the standard checks against the built game in the repository root (run src/build.py first).

  python3 -I tools/check.py           the browser tests in tools/tests/ plus the overlap check (tools/occcheck.py)
  python3 -I tools/check.py pwobj     just the named tests (occcheck included only if named)
  python3 -I tools/check.py -j 1      one test at a time (-j N: up to N side by side; the default suits this machine)

Each test serves the repository root on its own free localhost port, opens the game in headless Chromium (Playwright) and
prints its findings; a test passes when it prints no page errors. Screenshots go to out/ (git-ignored).
Tests run side by side, each on its own port with its own browser and screenshot names. pwframe measures frame time,
so it always runs last and alone, after the others have finished.
"""
import os, socket, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
# the game's text includes characters like U+202F; Windows pipes default to cp1252, which can't print them
sys.stdout.reconfigure(errors='backslashreplace')
TESTS = ['pwobj', 'pwchip', 'pwmed', 'pwtab', 'pwsave', 'pwbadsave', 'pwsavecode', 'pwmig', 'pwland', 'pwrc', 'pwneb', 'pwpark2', 'pwframe', 'pwsw', 'pwaudit']
ALONE = {'pwframe'}  # timing-sensitive: never shares the machine with another test

argv = sys.argv[1:]
# software WebGL keeps several cores busy per test, so a quarter of the logical cores, at most 6, at a time
jobs = max(1, min(6, (os.cpu_count() or 4) // 4))
if argv[:1] in (['-j'], ['--jobs']):
    try: jobs = max(1, int(argv[1]))
    except (IndexError, ValueError): sys.exit('usage: check.py [-j N] [test ...]')
    argv = argv[2:]
want = argv or TESTS + ['occcheck']


def free_port():
    # a port nothing is listening on, so two check runs (say from two sessions) never collide
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return str(s.getsockname()[1])


def run(name):
    port = free_port()
    path = os.path.join(HERE, 'occcheck.py' if name == 'occcheck' else os.path.join('tests', name + '.py'))
    args = [sys.executable, '-I', '-X', 'utf8', path, port] + (['390'] if name == 'pwaudit' else [])
    t = time.time()
    try:
        r = subprocess.run(args, capture_output=True, encoding='utf-8', errors='replace', timeout=600)
        out = (r.stdout + r.stderr).strip().splitlines()
        last = out[-1] if out else ''
        ok = r.returncode == 0 and (('ALL PASS' in last) if name == 'occcheck' else
                                    any(t in last for t in ('errors []', 'errs []')))
    except subprocess.TimeoutExpired:
        ok, last = False, 'timed out'
    return name, ok, last, time.time() - t


start = time.time()
bad = []
def report(name, ok, last, secs):
    print(f'{"PASS" if ok else "FAIL"}  {name:9s} {secs:4.0f}s  {last[:160]}', flush=True)
    if not ok: bad.append(name)

shared = [n for n in want if n not in ALONE]
with ThreadPoolExecutor(max_workers=jobs) as pool:
    for f in as_completed([pool.submit(run, n) for n in shared]):
        report(*f.result())
for n in want:
    if n in ALONE: report(*run(n))
verdict = 'ALL CHECKS PASS' if not bad else f'{len(bad)} FAILED: {", ".join(bad)}'
print(f'{verdict}  ({time.time() - start:.0f}s, {jobs} at a time)')
sys.exit(1 if bad else 0)
