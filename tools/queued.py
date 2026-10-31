"""Say what is waiting to be published: commits on dev that aren't on main yet.

Run by the SessionStart hook in .claude/settings.json, so each Claude session opens with a note when /release has
work queued. Prints a hook JSON object (systemMessage for the user, additionalContext for Claude), or nothing when
dev and main match. Never fails the session: any git error just means no note.

Usage: python -I tools/queued.py
"""
import json
import os
import subprocess

ROOT = os.environ.get('CLAUDE_PROJECT_DIR') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*args, timeout=20):
    r = subprocess.run(['git', '-C', ROOT, *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()


def main():
    try:
        try:
            git('fetch', '-q', 'origin', timeout=15)
            stale = ''
        except Exception:
            stale = ' (could not reach GitHub; using the last fetch)'
        commits = [c for c in git('log', '--format=%h %s', 'origin/main..dev').splitlines() if c]
        if not commits:
            return
        unpushed = len([c for c in git('log', '--format=%h', 'origin/dev..dev').splitlines() if c])
        game = bool(git('diff', '--name-only', 'origin/main', 'dev', '--', 'src/game.html'))
    except Exception:
        return
    n = len(commits)
    kind = 'including game changes' if game else 'docs and tools only, no game changes'
    msg = f'Queued for /release: {n} commit{"s" if n != 1 else ""} on dev not yet on main ({kind}){stale}.'
    if unpushed:
        msg += f' {unpushed} of them not pushed to GitHub yet.'
    detail = msg + '\n' + '\n'.join('  ' + c for c in commits[:15]) + ('\n  ...' if n > 15 else '')
    print(json.dumps({
        'systemMessage': msg,
        'hookSpecificOutput': {
            'hookEventName': 'SessionStart',
            'additionalContext': detail + '\nMention this to the user at the start of your first reply.',
        },
    }))


if __name__ == '__main__':
    main()
