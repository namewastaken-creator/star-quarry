# Star Quarry: dev builds on the owner's phone (31 Oct 2026)

**Status: suggestion only, nothing built.** The goal is to let the owner's phone run every `dev` build while players keep getting only published builds.

## How it works today

Players already get only live builds. GitHub Pages publishes from `main`, and the in-game update check reads `main/version.json` (`UPD_URL` in `src/game.html`). So nothing has to change for players. The phone just needs a second copy of the game that follows `dev`.

## Options

### 1. A separate "dev" Android app (recommended)

- Add a `dev` build type to `android/app/build.gradle.kts` with `applicationIdSuffix = ".dev"` and a name such as "Star Quarry Dev". It installs alongside the real app.
- It has its own save, so testing can never damage the real game.
- After each `src/build.py` on `dev`, build the dev APK in Android Studio and install it. It updates only when a new APK is installed.
- Needed: once the live version moves ahead of the dev copy, the dev app would ask to "update" to the live version. Turn that prompt off in dev builds.

### 2. A separate dev website that updates itself

- A second GitHub repo (for example `star-quarry-dev`) with Pages turned on. Whenever `dev` is pushed, its built files get copied there, either by a small script or a GitHub Action.
- The phone opens that URL (or a home-screen shortcut to it) and gets every `dev` push automatically. Players never see it.
- This publishes unreleased builds at a public URL. Anyone who finds the link can play them, though nothing points to it.
- Needed: the same update-prompt fix as option 1, and the offline copy (service worker) must stay limited to the dev site. Check this with `pwsw`.

### 3. No setup: the PC over Wi-Fi

- Run `python -m http.server 8000` in the repo root and open `http://<PC's IP>:8000` on the phone.
- Works only while the PC is on and the phone is on the same Wi-Fi.
- Offline play won't work, because browsers allow it only over HTTPS or on localhost.
- Good for a quick look, not as a daily build.
