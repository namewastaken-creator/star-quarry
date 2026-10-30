# Building Star Quarry

Everything needed to change, build, check and publish the game is in this repository. Run every command from the
repository root (the scripts work out their own paths, so any clone in any folder works).

## Layout

| Path | What it is |
|---|---|
| `src/game.html` | **The game's source.** One human-readable HTML file: styles, markup and the whole game script. Edit this. |
| `src/changelog.json` | The change log's source of truth (newest first). Written by `bump.py`, never by hand. |
| `src/guide_state.json` | Fingerprints used by `guidecheck.py` (see below). Updated by the build. |
| `src/vendor/three-r128.min.js` | Three.js r128, the only library. |
| `src/bump.py` | Bumps the version and adds a change-log entry. |
| `src/build.py` | Builds the web game and the Android app's game file. Runs `guidecheck.py`. |
| `src/guidecheck.py` | Warns when gameplay code changed but the in-game user guide (`GUIDE`) didn't. |
| `src/artifact/` | The Claude artifact phone preview: `preview.html` (the frame page) and `mk.py`. |
| `android/` | The Android Studio project (a full-screen WebView around the game). |
| `docs/design-notes.md` | The game's rules, balance numbers and design history. Add to "Later changes" when a release changes them. |
| `docs/code-review-2026-10-26.md` | The 26 Oct 2026 code review, with a status table at the top. |
| `tools/check.py` | Runs the standard checks (browser tests in `tools/tests/` and the overlap check). |
| `tools/tests/lategame.json` | A maxed late-game save (every planet, crew, point, perk, program, settlement and research). `pwframe` loads it to time frames; remake it with `tools/tests/mklategame.py` after a save-format change. |
| `tools/*.py` | Visual check tools that render close-ups of the 3D scene (see the top of each file). |
| `index.html`, `sw.js`, `version.json`, `manifest.webmanifest`, `three-r128.min.js`, `sky-*.jpg` | **Build outputs** at the root, served by GitHub Pages from `main`. Never edit them by hand. |
| `icon-*.png`, `apple-touch-icon.png` | Web app icons (static, not generated). |
| `dist/`, `out/` | Zips, the artifact copy and screenshots. Git-ignored. |

## Requirements

- **Python 3.11 or newer** (tested with 3.13). The bump and build scripts use only the standard library.
  On Windows also run `pip install tzdata` (bump.py dates entries in America/Chicago time via `zoneinfo`).
- **For the checks only:** `pip install playwright pillow` (tested with Playwright 1.56 and Pillow 12), then
  `python3 -m playwright install chromium`.
- **For the Android app:** Android Studio (it brings its own JDK 17 and downloads Gradle 8.7 on first sync).

## Publish routine

1. **Edit** `src/game.html`.
2. **Bump** the version and log the change in one short, player-facing sentence:
   ```
   python3 -I src/bump.py "Lava lakes are larger, with fewer cracks."
   ```
   - no flag: patch +1 (fixes and small tweaks, including visual polish)
   - `--minor`: a major new feature or block of content (patch resets to 0)
   - `--major`: an overhaul, or leaving beta
   - `--important`: open games ask players to update (only for fixes that matter)
   - `--sync`: no new version; just rewrite the game's `CHANGES` from `src/changelog.json`

   The build number rises by one on every bump; update checks compare only that, so it never goes backwards.
3. **Build:**
   ```
   python3 -I src/build.py
   ```
   It writes the web game to the repository root, `android/app/src/main/assets/index.html`, the Android version
   in `android/app/build.gradle.kts`, and `dist/StarQuarry-Web.zip` / `dist/StarQuarry-Android.zip`.
   If it prints a **guide check WARNING**, gameplay changed but the user guide (`GUIDE` in `src/game.html`, shown
   from the Warp tab) didn't: update the guide, or if nothing in it is affected, rebuild with
   `python3 -I src/build.py --guide-ok`.
   If the release changes the game's rules, numbers or how a system works, add an entry for it under "Later
   changes" at the end of `docs/design-notes.md`, headed with the new version name.
4. **Check:**
   ```
   python3 -I tools/check.py
   ```
   The browser tests in `tools/tests/` plus the overlap check (nothing on a planet stands inside the base or the mining field). All
   must pass. It takes several minutes (software WebGL). Also look at the change yourself: serve the root
   (`python3 -m http.server 8000`, then http://localhost:8000) and check at phone width (about 390 px).
   http://localhost:8000/src/artifact/preview.html?src=/index.html shows the game in phone- and iPad-sized frames
   with buttons for each screen size and Rotate.
5. **Commit and push to `dev`.** Commit `src/`, the build outputs at the root, `android/app/build.gradle.kts` and
   `docs/design-notes.md` if it changed.
6. **Gate:**
   ```
   python3 -I tools/preflight.py
   ```
   It checks that you're on a clean, pushed `dev` that `main` can fast-forward to, that the version was bumped past
   `main`'s with a matching change-log entry, that a fresh build changes nothing and gives no guide warning, and that
   all the checks pass. Publish only when it ends with `READY TO PUBLISH`; otherwise it says what to fix.
7. **Publish:** `git checkout main`, `git pull --ff-only`, `git merge --ff-only dev`, `git push origin main`, then
   `git checkout dev`. GitHub Pages redeploys within a minute or two; open games notice the new `version.json` (read
   from `main` on raw.githubusercontent.com) and offer the update. Never force-push `main`; fix a bad release with a
   new one.

In Claude Code, `/release` runs this whole routine (`.claude/skills/release/SKILL.md`), stopping for your approval
of the change-log sentence and again before publishing.

On Windows, type `python` wherever these steps say `python3` (`python3` there is the Microsoft Store shortcut).

Optional, for the Claude artifact phone preview: `python3 -I src/artifact/mk.py` writes `dist/artifact/game.html`;
publish `src/artifact/preview.html` with `game.html` beside it.

## Android app

1. Run `python3 -I src/build.py` first: the game file the app loads (`android/app/src/main/assets/index.html`) is a
   build output and isn't stored in the repository.
2. In Android Studio, **File > Open** the `android` folder and let Gradle sync.
3. **Build > Build App Bundle(s) / APK(s) > Build APK(s)**. The APK lands in `android/app/build/outputs/apk/`.
   Release builds are signed with the debug key so they install directly; set up your own signing config before
   uploading to the Play Store, and keep the keystore and its passwords **out of the repository** (`.gitignore`
   already ignores `*.jks`, `*.keystore`, `keystore.properties` and `local.properties`).

`versionCode` and `versionName` are set by the build from the game's build number and version name.
