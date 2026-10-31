# Star Quarry: code review (26 Oct 2026)

## Status (checked 30 Oct 2026 against Beta 0.40.11.193)

The review below was written against Beta 0.20.0.124. Most of it has been fixed since; this table says where each item stands now.

| # | Item | Status |
|---|---|---|
| 1 | `parkRank` freeze | Fixed. Ranked a little each frame since Beta 0.20.1; the Park window no longer works a forecast out on the spot (Beta 0.40.10.192). Test: `pwframe`. |
| 2 | `parkRank` cache ignores point changes | Fixed. `econSig` covers points, perks, programs, settlements, research and boosts; rankings expire by wall-clock age (Beta 0.40.10.192). |
| 3 | Service worker caches error pages | Fixed. Only the real game replaces the offline copy (Beta 0.40.11.193). Test: `pwsw`. |
| 4 | Bad saves silently replaced | Fixed. Shape checks, backups that never overwrite each other, no save over an un-backed-up original, a boot-crash net (Beta 0.40.11.193); failed saves warn once. Test: `pwbadsave`. |
| 5 | Toasts overwrite each other | Fixed. A queue that honours each toast's time (up to 8 s). |
| 6 | Long absences undercount probes | Fixed. The guard scales with the offline cap. |
| 7 | Panel rebuilt by `innerHTML` | Fixed. `render` patches the panel in place (`morph`), so buttons and focus survive. |
| 8 | UI state survives Warp and Erase | Fixed. `resetGalaxyUI` clears it. |
| 9 | Offline income uses a simpler model | Fixed. `offline` uses `planetFlow`, with galaxy events counted only for their share of the absence. |
| 10 | Dead code | Fixed. |
| 11 | Duplicated formulas | Fixed. `tripAt` and `offlineCapSec`. |
| 12 | `fmt` rounding and negatives | Fixed. |
| 13 | `tabBadges` hides errors | Fixed. Logged once per tab with `console.error`. |
| 14 | Side effects in getters | Partly. `galNowCalc` no longer writes the save, but `econG`, `galNow` and `fmt` still guard with `typeof S`. |
| 15 | Fragile hull rim shader patch | Fixed. Falls back to a second hook and logs if neither is found. |
| 16 | File size and daily updates | Partly. Three.js and the sky are separate cached files, but `index.html` is still about 750 KB per release. |
| 17 | Readability | Partly. Migrations run once each, in order (`S.mig`, `MIGRATIONS`; test `pwmig`). Still open: very long source lines and a 40-branch click handler. |
| 18 | Accessibility | Fixed. Pinch-zoom is allowed; focus survives redraws (item 7). |

Reviewed: `dev` at Beta 0.20.0.124 (commit c600392): `index.html` (game script), `sw.js`, `manifest.webmanifest`, `version.json`. This session only read the code and measured it in headless Chromium. Per the project rule, **the owning chat makes any changes**. Function names are given rather than line numbers, because the repository holds build output.

How it was checked: the whole game script was read by hand. Then a late-game state (22 planets, 3 crews, 65 points, every program, all research) was loaded into the live page and the heavy functions were timed. Times are from a desktop-class CPU; a phone will be slower.

## High priority

**1. A 0.8–0.9 s freeze every minute in the late game (`parkRank`)**
- Once Station Thrusters is researched, `tabBadges` → `TAB_STATUS.research` calls `parkRank()` every second. The cache expires after 60 s, so a full recompute runs every minute.
- Measured: `parkRank(true)` took **820–880 ms** with 22 planets. It runs `planBalance` for every claimed planet × every destination. On a phone this is likely a multi-second hitch.
- The same stall happens right on the tap when claiming a planet or buying research, because those change the cache key.
- Suggest:
  - The tab badge uses a cheap estimate: income "as is" at each spot, with no `planBalance`.
  - Run the full ranking only while the Station tab is open.
  - Spread it over frames, one destination per frame, or move it into a Web Worker.

**2. `parkRank`'s cache ignores point changes**
- The key uses `crewVer`, but `teamBuy`, `assign`, `unassign`, `planApply`, mission free points (`evGive` 'pts'), `buySettle` and permanent boosts don't bump it.
- The comment says the cache clears "until points … change", but it actually only expires on the 60 s timer. So "Best parking spot" and the Station badge can be up to a minute stale.
- Suggest: one `econVer` counter bumped by every economy change, used by all the economy caches. It could replace `crewVer` and `settleVer`.

**3. The service worker can cache an error page as the offline game (`sw.js`)**
- The navigation handler does `caches.put('./index.html', copy)` without checking `r.ok`.
- A 404 or 5xx from GitHub Pages, for example mid-deploy, replaces the good offline copy. The installed app then opens to an error page when offline.
- Fix: `if (r.ok) caches.open(CACHE).then(c => c.put('./index.html', copy))`.

**4. A bad save is silently replaced**
- If the save doesn't parse, or `S.v !== 1`, the game starts a new run and autosave overwrites the old save 5 s later. An older cached build reading a newer save would wipe it the same way.
- `save()` swallows quota errors, so progress can stop saving without the player knowing.
- Suggest:
  - Copy the raw string to `starquarry_save_bak` before replacing anything.
  - Never overwrite a save whose version is newer than the code.
  - Show a toast once if `setItem` fails.

## Medium priority

**5. Toasts overwrite each other and are cut to 4 s**
- `toast()` replaces whatever is showing and caps every duration at 4000 ms.
- Examples:
  - Claiming Kallyur'Dadh shows "claimed …" and is immediately replaced by "Galaxy Warp is now available".
  - Researching Smelter shows "Smelter complete." and is immediately replaced.
  - The 6 s welcome-back message shows for only 4 s.
- Suggest: a small queue that honours `ms`, or merges messages that arrive in the same tick.

**6. Long absences undercount probes (`probeTick`)**
- The catch-up loop stops at 500 iterations, and each probe takes 2 (launch and return). So it handles at most 250 probes.
- Measured: a 24 h absence with Night Shift has 288 probes. 250 were counted, and the other 38 came back on the next frame with their own toast. Those 38 are missing from the welcome-back message.
- Fix: base the guard on the cap (`2 × cap / PROBE_EVERY + 4`), or count the launches arithmetically.

**7. The panel is rebuilt by `innerHTML` four times a second (`render`)**
- Any changing number (credits, timers) rebuilds the whole tab. The Planet tab took 4.4 ms on desktop.
- Rebuilding also recreates every button, which costs keyboard and screen-reader focus. The `pressing` guard only protects touch.
- Suggest: rebuild the structure only when it changes, and update numbers through `data-bind` spans, like `hud()` already does for the credits.

**8. Per-galaxy UI state survives Warp and Erase**
- `tune` (plans), `perkPick` and `BL` are keyed by planet index and not cleared. A positive plan from the old galaxy can reappear as a dashed preview on the same planet in the new one.
- Clear them, and `PR_CACHE`, in the warp and reset handlers.

**9. Offline income uses a simpler model than live play (`offline`)**
- It uses `haul()` (the cycle average with an unlimited silo) instead of `planetFlow()`. A scan of layouts found at most about 1% more income offline, so this is low impact.
- It also applies the station position and galaxy event multipliers at the moment you return to the whole absence. For example, an Ore rush running at return time counts for all 8 h.
- Suggest: use `planetFlow(i).hauled` and `.over` for consistency.

## Low priority: tidy-ups and style

**10. Dead code**
- `parkAsk` calls `parkForecast(x)` but never uses the result. That's wasted work on every tap, and `parkForecast` can go.
- The "Return to the lane" / "its own lane" branches: `S.park.i` is always ≥ 0 now.
- Ship `mode===2` ("kept for later").
- `hsStep` and the `.cnav` arrow handlers (the arrows were removed).
- `ECON.UP_GROW` and `ECON.TEAM_X` are unused.
- In `overflowSale`, the second `if (S.overAt < now)` can never be true.

**11. Duplicated formulas**
- "Capacity at a phase", `cg / (2·er·distF(...)/v + h)`, is written out in `avgInvT`, `tripRange`, `planetFlow`, `siloNeed` and `capCurve`. One `capAt(i, ph, G)` helper would keep them in step.
- `(has('night') ? 24 : 8) * 3600` appears three times. Use an `offlineCapSec()` helper.

**12. `fmt` rounds inconsistently**
- 9,999 → "10.00 K" and 99,999 → "100.0 K", but 999,999 → "999 K".
- Negative numbers aren't formatted: −2500 → "-2500". `fmt(S.cash - before)` and gain values can be negative.
- Suggest: floor before choosing decimals, and format `Math.abs(n)` with the sign added back.

**13. Errors are hidden**
- `tabBadges` wraps each status in `try { } catch(e) { continue }`, so a bug there silently freezes that tab's alert. At least log it with `console.error`.

**14. Side effects in getters**
- `galNowCalc()` writes `S.ev.gal` while answering "what's running now?".
- `econG()` and `galNow()` guard with `typeof S` because of load order.
- Moving state updates into a tick function (`galTick` already exists) would make these pure.

**15. The hull rim shader patch is fragile**
- `hullRim` string-replaces the r128 `gl_FragColor = vec4( outgoingLight, diffuseColor.a );` line. If Three.js is upgraded, the replacement silently does nothing and the rim glow disappears.
- Add a check that the replacement happened, or use the standard `#include` chunk hook.

**16. File size and daily updates**
- `index.html` is 1.13 MB. 603 KB of that is Three.js r128 (2021) inlined, plus a 78 KB sky image and the 35 KB change log.
- Every daily release makes players re-download all of it.
- Suggest: ship `three.min.js` and the sky as separate files with versioned names, in the service worker's cache-first list. A daily update would then be about 370 KB.

**17. Readability**
- Game-script lines run up to about 800 characters, with many one-letter names.
- Suggest:
  - Format the source copy for humans; the build can still minify the output.
  - Replace the 50-branch `if/else` click handler with an action table (`ACTIONS[a](b)`).
  - Give migrations a version number (`S.mig`) and an ordered list, instead of running every check on every load.

**18. Accessibility**
- `user-scalable=no` blocks pinch-zoom of the UI text for low-vision players.
- See item 7 for focus loss.

## What's working well
- The comments explain the *why*, kept in step with the design doc.
- Missions and galaxy events are deterministic and seeded, with no server.
- Station geometry is cached (`parkG`), distant colonies are detached rather than hidden, and labels are measured once.
- `planetFlow` is one honest whole-orbit model shared by Balance, colours and forecasts.
- User text (the station name) is escaped everywhere it reaches HTML.

## Not checked
- GPU frame times on a real phone. The headless test used software rendering, so its frame times aren't meaningful.
- The music generator and planet texture jobs were only skimmed.
