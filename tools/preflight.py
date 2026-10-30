#!/usr/bin/env python3
"""Release gate: run on dev after the release is bumped, built and committed, before merging dev into main.

  python3 -I tools/preflight.py              every step below; prints READY TO PUBLISH only if all pass
  python3 -I tools/preflight.py --no-tests   skip the browser checks (quick look only; never enough to publish)

Steps, in order (it stops at the first failure and says what to do):
  1. on branch dev, nothing uncommitted or untracked
  2. dev is pushed (matches origin/dev) and main can fast-forward to it (origin/main is behind dev, not beside it)
  3. the build number in src/game.html is higher than on origin/main, and the newest change-log entry is this version
  4. a fresh build gives no guide-check warning and changes nothing (the committed outputs are this source's build)
  5. all the checks pass (tools/check.py)
"""
import os, re, json, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = [sys.executable, '-I', '-X', 'utf8']
sys.stdout.reconfigure(errors='backslashreplace')
APP_VER = re.compile(r"const APP_VER=\{name:'([^']+)',n:(\d+)\};")

def git(*args, check=True):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, encoding='utf-8', errors='replace')
    if check and r.returncode: fail(f'git {" ".join(args)} failed: {(r.stderr or r.stdout).strip()}')
    return r.stdout.strip()

def changed():
    # content changes only: on Windows a rebuilt file can differ from the checkout in line endings alone, which git
    # status reports but git diff (rightly) doesn't
    return [l for l in (git('diff', '--name-only', 'HEAD') + '\n' + git('ls-files', '--others', '--exclude-standard')).splitlines() if l]

def fail(msg, fix=None):
    print(f'\nNOT READY: {msg}' + (f'\n  fix: {fix}' if fix else ''))
    sys.exit(1)

def ok(msg): print(f'ok    {msg}')

# 1. branch and working tree
branch = git('rev-parse', '--abbrev-ref', 'HEAD')
if branch != 'dev': fail(f'on branch {branch!r}, not dev', 'git checkout dev')
if changed(): fail('uncommitted changes: ' + ', '.join(changed()), 'commit them to dev (or undo them) first')
ok('on dev, nothing uncommitted')

# 2. pushed, and main fast-forwards to dev
git('fetch', '-q', 'origin')
if git('rev-parse', 'HEAD') != git('rev-parse', 'origin/dev'): fail('dev is not the same as origin/dev', 'git pull --ff-only, then git push origin dev')
if subprocess.run(['git', 'merge-base', '--is-ancestor', 'origin/main', 'HEAD'], cwd=ROOT).returncode:
    fail('origin/main has commits that dev does not', 'merge origin/main into dev, rebuild, check and commit, then run this again')
ahead = git('rev-list', '--count', 'origin/main..HEAD')
if ahead == '0': fail('dev has nothing that main does not; there is nothing to publish')
ok(f'dev is pushed and {ahead} commit(s) ahead of main')

# 3. version bumped, change log matches
src = open(os.path.join(ROOT, 'src', 'game.html'), encoding='utf-8').read()
m = APP_VER.search(src)
if not m: fail('APP_VER not found in src/game.html')
name, n = m.group(1), int(m.group(2))
mm = APP_VER.search(git('show', 'origin/main:src/game.html'))
main_name, main_n = (mm.group(1), int(mm.group(2))) if mm else ('none', -1)
if n <= main_n: fail(f'build number {n} is not higher than main\'s {main_n} ({main_name})', 'python3 -I src/bump.py "what changed", then build, commit and push')
log = json.load(open(os.path.join(ROOT, 'src', 'changelog.json'), encoding='utf-8'))
top = next((c for c in log if c.get('v')), None)
if not top or top['v'] != name: fail(f'newest change-log entry is {top and top["v"]!r}, not {name!r}', 'bump with src/bump.py; never edit the version or change log by hand')
ok(f'{name} (build {n}) is newer than main\'s {main_name}; change log: "{top["t"]}"' + (' [important]' if top.get('imp') else ''))

# 4. a fresh build reproduces the committed outputs
r = subprocess.run(PY + [os.path.join(ROOT, 'src', 'build.py')], cwd=ROOT, capture_output=True, encoding='utf-8', errors='replace')
out = (r.stdout + r.stderr).strip()
if r.returncode: fail('the build failed:\n' + out)
if 'WARNING' in out: fail('the guide check warned that gameplay changed but the user guide did not',
                          'update GUIDE in src/game.html, or if the guide is unaffected run python3 -I src/build.py --guide-ok; then commit and push')
if changed(): fail('a fresh build changed: ' + ', '.join(changed()), 'the committed build is out of date: build, commit and push, then run this again')
ok(out.splitlines()[-1])

# 5. the checks
if '--no-tests' in sys.argv:
    print('\nskipped the browser checks (--no-tests): NOT READY TO PUBLISH until they run')
    sys.exit(1)
print('...   running all the checks (several minutes)', flush=True)
r = subprocess.run(PY + [os.path.join(ROOT, 'tools', 'check.py')], cwd=ROOT, capture_output=True, encoding='utf-8', errors='replace')
print('\n'.join('      ' + l for l in r.stdout.strip().splitlines()))
if r.returncode: fail('checks failed (see above)', 'fix the cause, then build, commit, push and run this again')
if changed(): fail('the checks changed tracked files: ' + ', '.join(changed()))
ok('all checks pass')

print(f'\nREADY TO PUBLISH {name}')
