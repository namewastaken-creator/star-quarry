---
name: release
description: Publish a new version of Star Quarry to players - bump, build, check, gate with tools/preflight.py, then merge dev into main with the user's explicit yes. Use when the user says /release, "publish", "release", "ship it" or "push it live".
---

# Release Star Quarry

Pushing `main` updates the live game for every player (GitHub Pages, and every open game's update check). Follow these
steps in order. **Stop at the first failure**, tell the user plainly what failed and what you suggest, and don't carry
on until it's fixed. Never skip a step because it passed last time.

**Python command:** on Windows use `python` (`python3` there is the Microsoft Store shortcut, not real Python);
elsewhere use `python3`. Below it is written `python`.

**Run one step per command**, and check each result before the next. Never chain steps so that a failure carries on
into the next one.

## 1. Start clean

- `git status -sb` and `git fetch origin`. You must be on `dev`.
- If there are uncommitted changes, show the user what they are and ask whether they belong in this release. Don't
  commit, stash or discard them without asking.
- If `dev` is behind `origin/dev`, run `git pull --ff-only`. If `origin/main` has commits `dev` doesn't (check with
  `git merge-base --is-ancestor origin/main dev`), stop and ask.

## 2. Decide what's in it

- Look at what changed since the last release: `git log --oneline origin/main..dev`, and
  `git diff origin/main..dev -- src/game.html`.
- If nothing players would notice has changed since `main`, say so: there's nothing to publish. Tooling-only commits
  go out with the next real release.
- Draft **one short, player-facing change-log sentence**: what the player will notice, not how the code changed (see
  the recent entries in `src/changelog.json` for the voice). Pick the bump size from CLAUDE.md:
  no flag = patch (fixes, tweaks, visual polish), `--minor` = a major new feature or block of content,
  `--major` = an overhaul or leaving beta. Suggest `--important` only for a fix that matters to players.
- **STOP: show the user the sentence and the bump size, and wait for them to approve or change it.**

## 3. Bump and build

- `python -I src/bump.py "<approved sentence>" [--minor|--major] [--important]`
- `python -I src/build.py`
- If the build prints a **guide check WARNING**, gameplay changed but the user guide didn't. Read `GUIDE` in
  `src/game.html`. If a section is affected, update it (in the same plain style) and build again. If nothing in the
  guide is affected, tell the user why, and with their OK run `python -I src/build.py --guide-ok`.

## 4. Look at it

- Make sure the local server is running (Preview pane, `star-quarry` in `.claude/launch.json`), and open
  `http://localhost:8000/src/artifact/preview.html?src=/index.html`.
- Check the change itself, plus a new game at iPhone size and at iPad mini size. Watch the console for errors.
- If the change affects late-game play or performance, test it with a late-game save too (CLAUDE.md).
- Show the user screenshots of what changed.

## 5. Commit and push to dev

- Commit `src/`, the build outputs at the repository root and `android/app/build.gradle.kts`. Use the message
  `<version name>: <a short lower-case summary of the change>`, matching earlier releases, for example
  `Beta 0.40.9.191: larger lava lakes with fewer cracks`.
- `git push origin dev`

## 6. Gate

- `python -I tools/preflight.py`. It takes several minutes (it runs all the checks). Run it in the background and
  wait for it to finish.
- It must end with `READY TO PUBLISH <version>`. If it prints `NOT READY`, follow its `fix:` line, then repeat from
  the step that line points to, and run the gate again. Never publish on an older READY: the gate must pass on the
  exact commit being merged.

## 7. Publish (only with the user's explicit yes)

- **STOP: tell the user the version, the change-log sentence, and that this updates the live game for every player.
  Ask for a clear yes.** Approval of an earlier release, or of the change-log sentence, does not count.
- Then, one command at a time:
  - `git checkout main`
  - `git pull --ff-only`
  - `git merge --ff-only dev` (if this refuses, stop and ask; never force anything on `main`)
  - `git push origin main`
  - `git checkout dev`

## 8. Confirm it's live

- After a minute or two, fetch `https://raw.githubusercontent.com/namewastaken-creator/star-quarry/main/version.json`
  and `https://namewastaken-creator.github.io/star-quarry/version.json`. Both should show the new version name and
  build number. GitHub Pages can take a few minutes, so check again before calling it a failure.
- Tell the user it's live, with the version and the change-log sentence.

## If something goes wrong after publishing

Don't try to undo a release by moving `main` backwards: build numbers must never go down, and players may already
have the new version. Fix forward with a new release (step 1 onwards), using `--important` if players need it quickly.
