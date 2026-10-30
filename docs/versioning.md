# Star Quarry: versioning

> **About this copy (30 Oct 2026).** Moved here from Claude chat. The text below this note is unchanged apart from blank lines. "star-quarry-game-design.md" is now `docs/design-notes.md`; this file replaces its "Version and updates" section. The rules for bumping and publishing are in `CLAUDE.md`, and the commands in `BUILDING.md` (on Windows, run them with `python`, not `python3`). Where this file disagrees with the repository, the repository wins. Out of date below:
> - **Prompt:** an open game no longer asks whenever the published `n` is higher. It updates quietly: it notes the old version (`sq_updfrom`) and the next launch loads the new one and says "Updated to …". It asks only when a newer change is marked important (`--important`, `imp` in the `log` in `version.json`), at most once a day (`sq_updask`). Checking by hand on the Warp tab always shows the dialog. See "Quiet updates" under Publishing in `docs/design-notes.md`.
> - **Minor bumps so far** stops at 0.17. The full list is in `src/changelog.json` (Beta 0.41.0.194 when this copy was made).
> - **Tests:** `tools/tests/` now has 14 browser tests (including `pwsw`, `pwframe`, `pwbadsave` and `pwsavecode`), not ten.
> - **Erase save panel:** a Your save card (export, import and restoring backups) now sits above it on the Warp tab (Beta 0.41.0.194).

> **Who changes the game (from 30 Oct 2026):** Star Quarry is developed in Claude Code (the Code tab in the Claude desktop app), working from the GitHub repository `namewastaken-creator/star-quarry`, which is the single source of truth. The source, the change log, the bump and build scripts, the checks and the Android project are all in the repository; `BUILDING.md` has the commands and `CLAUDE.md` the rules. The Claude chat that built and pushed the game until Beta 0.40.9.191 no longer builds or pushes; it can read the project and the repository and suggest changes.

This replaces the "Version and updates" section of star-quarry-game-design.md where they disagree.

- **Version scheme (from Beta 0.16.15.91, 25 Oct 2026):** Major.Minor.Patch.Build, shown as 'Beta 0.16.15.91' while major is 0. `APP_VER` in the game file holds the name and `n`, the build number.
  - **Major:** stays 0 through beta; goes to 1 at the full release (the name then drops 'Beta').
  - **Minor:** a major new feature or block of content (patch resets to 0).
  - **Patch:** fixes and small tweaks, including visual polish.
  - **Build:** `n`, +1 on every publish whatever else changes. Update checks compare it, so it never goes backwards.
- **Renumbering:** the whole change log was renumbered from the old 'Beta 1.0.N' names, which kept the build number (old 1.0.N = build N). Entries from before build numbers (Oct 20–23) have build 0. Minor bumps so far:
  - 0.1 first web release · 0.2 mining teams (up to 3 per planet) · 0.3 hauler flights and docking station · 0.4 space probes · 0.5 settlements · 0.6 weekly events · 0.7 overflow selling · 0.8 ship speed vs cargo
  - 0.9 version checks and updates (build 1) · 0.10 sun and station orbit (19) · 0.11 real orbits and silos (25) · 0.12 Station Thrusters (26) · 0.13 Market Surge (45) · 0.14 specialist crews (48) · 0.15 tuning chart (59) · 0.16 mining crews and the point pool (76) · 0.17 one zoom system for planets, the station and the probe (92)
- **Version comparison (`verKey`, `verGT`):** compares the build number only (4th part; an old 'x.y.z' name counts as build z when it starts 1.0). Games still running old code compare names part by part, so until they reload they may not list the new versions as newer; the update itself still happens because it is decided by `n`.
- **Bump on every publish (in the repository):** `python3 -I src/bump.py "what changed"` (patch +1), `--minor` (minor +1, patch 0), `--major` (major +1), `--important` (players are asked to update), `--sync` (no new version: rewrite `CHANGES` from the change log). Build +1 every time. It writes a dated entry (America/Chicago date) to `src/changelog.json`, the change log's source of truth, and rewrites `CHANGES` and `APP_VER` in `src/game.html`; `python3 -I src/build.py` then writes `version.json` ({name, n, notes, log: last 40}), the `sw.js` cache key and the Android version.
- **Change log:** a 'What's changed' button on the Warp tab's Version card opens a scrollable list grouped by day, newest first. Every item shows its version tag and the change. `version.json` carries `notes` for the newest version, and the update prompt shows them as "What's new: …".
- **Update check:** the game fetches `version.json` (no-store; the service worker never caches it) 20 s after loading, every 30 minutes, and on returning to the foreground if 5+ minutes have passed. For now it always reads `version.json` from the GitHub repository (`raw.githubusercontent.com/namewastaken-creator/star-quarry/main/version.json`, which allows cross-site requests and is cached up to 5 minutes), so a push is noticed without waiting for the Pages deploy. If 'Update now' reloads before the Pages site has the new build, the game says it's still being published and waits 3 minutes before asking again.
- **Prompt:** when the published `n` is higher, an 'Update available' dialog shows the new and current versions.
  - **Update now** saves, reloads, and then toasts 'Updated to Beta x. Your progress came with you.'
  - **Not now** toasts that the player keeps this version, won't be asked again until reload, and can update from the Warp tab. Automatic prompts then stop until the game is reloaded.
  - In the Android app, the dialog explains that updating means installing the newest build (it can't reload into a new version), and offers only OK.
  - Sources are tried in order, each with an 8 s timeout: the repository's raw file, then the GitHub API copy (`api.github.com/.../contents/version.json`, raw), then the Pages site.
  - If all fail, it stays silent unless the player tapped Check. On GitHub Pages, in the Android app or on localhost, the message is 'Couldn't reach GitHub. Check your internet connection'. Anywhere else, such as the Claude artifact, whose page blocks outside connections, it explains that this page blocks the check and points to namewastaken-creator.github.io/star-quarry.
- **Erase save panel:** the last panel on the Warp tab, laid out like the Version panel: a heading, a one-line summary, the 'Erase save and start over' button (tap twice within 4 s), and a note on what's erased (everything except the music setting), that it can't be undone, and that Warp keeps star dust and boosts.

## Repository handoff (30 Oct 2026)

- The pipeline that lived in the owning chat's workspace moved into the repository at Beta 0.40.9.191 (no version bump):
  - `src/game.html` (the source game file), `src/changelog.json`, `src/guide_state.json`, `src/vendor/three-r128.min.js`
  - `src/bump.py` (the only bump script; the reference-only `tools/bump.py` is gone), `src/build.py`, `src/guidecheck.py`, `src/artifact/mk.py` and `preview.html`
  - `android/` (the Android Studio project, without signing material or `local.properties`)
  - `tools/check.py` with the ten browser tests in `tools/tests/`, and the visual check tools in `tools/`
  - `BUILDING.md`, `CLAUDE.md` and a `.gitignore`
- All paths are relative to the repository root. A fresh clone, built with no other files, produced `index.html`, `sw.js` and `version.json` byte-identical to the published Beta 0.40.9.191.
- The build writes the web game straight into the repository root; zips and the artifact copy go to `dist/` (git-ignored); the Android app's `assets/index.html` is a build output and isn't stored.

## Earlier publishing notes (25 Oct 2026)

- The renumbering was made in another session and pushed to `dev` as commit 72966ae. The owning chat then took it into its source and change log, and published Beta 0.17.0.92 on top (commit 751bce0).
