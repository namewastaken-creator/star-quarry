# Star Quarry

A 3D idle space-mining game. Claim planets, hire mining teams, smelt ore into bars, research upgrades and warp to new galaxies.

No ads, no purchases, no premium currency.

**Play:** https://namewastaken-creator.github.io/star-quarry/

On your phone, open the link and add it to your home screen (Chrome: ⋮ > Add to Home screen; Safari: Share > Add to Home Screen). It then runs full screen and works offline.

## Making changes

All changes to the game are made in one Claude chat, the one the owner chose. Other Claude sessions must not edit, build, bump or push anything in this repository; they can read it and suggest changes for that chat to make.

The repository's `index.html`, `sw.js` and `version.json` are build outputs from that chat's source copy, so editing them here directly would be overwritten by the next build. `tools/bump.py` is kept for reference only and refuses to run.
