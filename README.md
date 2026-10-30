# Star Quarry

A 3D idle space-mining game. Claim planets, hire mining teams, smelt ore into bars, research upgrades and warp to new galaxies.

No ads, no purchases, no premium currency.

**Play:** https://namewastaken-creator.github.io/star-quarry/

On your phone, open the link and add it to your home screen (Chrome: ⋮ > Add to Home screen; Safari: Share > Add to Home Screen). It then runs full screen and works offline.

## Making changes

Star Quarry is developed in Claude Code (the Code tab in the Claude desktop app), working from this repository, which is the single source of truth. The game's source is `src/game.html`; `BUILDING.md` has the exact commands to bump, build, check and publish, and `CLAUDE.md` has the rules.

The root `index.html`, `sw.js` and `version.json` are build outputs: edit the source and rebuild rather than editing them directly. Work happens on `dev`; merging to `main` publishes to every player.

The Claude chat that used to build and push the game no longer does; it can read the repository and suggest changes.
