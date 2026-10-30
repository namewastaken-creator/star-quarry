# Star Quarry: world kits proposal (27 Oct 2026)

> **About this copy (30 Oct 2026).** Moved here from Claude chat. The text below this note is unchanged apart from blank lines. It is kept as the reasoning behind the world kits; **for how they work now, read "Layout and visuals" and "Later changes" in `docs/design-notes.md`**, which win wherever they disagree with this.
> - **Status: fully built.** Stage 1 (framework) to stage 5 (user guide) shipped in Beta 0.24.0.135–0.27.1.139.
> - **Owner's decisions:** the tier tracks in section 2 as proposed; 2 miners per crew (6 in all); the refinery is for show only.
> - **Changed since:** the plot is no longer the compact 120° wedge layout. The mine field moved north to its own works pad (`WORKS`, `MINE_SHIFT`, Beta 0.29.1), `PLOT_R` is 8.4, routes are planned over terrain (`planRoutes`), far reservations go by direction (`OCC_DIR`), and the ocean lighthouse stands on its own reserved islet. Ocean worlds and gas giants have no ground clearing (`uSiteR` 0). The overlap check is `tools/occcheck.py`.
> - **"Suggestion only … the owning chat makes any changes"** describes the old chat workflow; `CLAUDE.md` replaces it.

A proposal for how each planet type builds, looks and animates its base. **Suggestion only:** per the project rule, the owning chat makes any changes. Everything here is visual. Economy, pacing and the guide's rules don't change, except that the guide's colony and settlement descriptions would need rewording.

## 1. The idea: one kit per world type

Today every planet gets the same colony: a hall, habitat, processing dome and rovers. Then `styleSettlement` reskins the settlement afterwards. Instead, each `PTYPE` gets a **kit**: a data entry that says what each structure is, how it's built at each tier, how the miners move and work, and where things may stand.

```js
const KIT = {
  rock:  { site, mine, miner, pad, refinery, settle, link, fx },
  lava:  { ... }, ice: { ... }, gas: { ... }, water: { ... }, veg: { ... }
};
// tiers worked out from the save, never stored
tierOf(i) -> { mine: 1-3, miners: 2-6, pad: 1-3, refinery: 0-3, settle: 0-3 }
```

Every structure is a builder `(w, i, tier, rng) -> Group` that returns that tier's complete model. Changing tier rebuilds that one structure, not the whole base. Shared geometry and textures are cached per type, as `minerGeo` already is per planet size.

## 2. What a full planet has, and what drives each tier

Each structure follows its own progression track, so the base shows *how* the player built the planet, not just how far they got.

| Structure | Tier 1 | Tier 2 | Tier 3 | Driven by |
|---|---|---|---|---|
| **Mine + miners** | claim · 2 miners | Shift Crew · 4 miners | Instructors · 6 miners | crews hired |
| **Landing pad** | claim | 12 hauling points placed | 24 hauling points placed | Speed + Cargo points |
| **Refinery** | Shift Crew hired | Prospecting done | all 5 programs done | training |
| **Settlement** | Outpost | Town | City | settlement level (as now) |

- A fully upgraded planet (3 crews, full points, every program, City) is tier 3 everywhere.
- **Ore path is visible:** miners → refinery → pad loader → hauler. Before the refinery exists, miners unload straight into a hopper at the pad.
- **6 miners instead of today's 9 rovers:** 2 per crew. This is more compact, with fewer overlapping routes. Each miner keeps its crew's graffiti emblem.
- **The tier 3 test:** each tier must change the silhouette at Close-up (level 1), and add finer detail you notice at Closest (level 3).

## 3. Compact site layout (shared by all kits)

All structures sit on one **base plot** in the existing surface frame, about 55–60% of today's spread. The pad is at the centre and three 120° wedges surround it:

```
            Mine wedge
        (3 deposit spots on
         an arc, mine head)
               /\
              /  \
    Refinery  [PAD]  Settlement
     wedge            wedge
```

- **Pad** at the plot's centre. The hauler is the hero, and the close-up camera already frames the base from above.
- **Mine wedge:** the mine head near the pad, with deposits on an arc 0.6–1.0 of the plot radius out. Miner routes are short spokes.
- **Refinery wedge:** next to the pad, so the conveyor or pipe to the pad loader is short.
- **Settlement wedge:** joined to the pad by the kit's `link` (tube, light-bridge, floating walkway, canopy walk…).
- The settlement's own layout (hub, barracks, greenhouse pods, City domes) stays, scaled about 0.8× and packed tighter.

## 4. Nothing on top of features

The current build keeps features clear of what *exists*. That breaks when a later tier grows into a tree, boulder or lava pool. The fix is to reserve space up front:

1. **Pick the site first** (`pickSite(i)`). Score candidate centres by the kit's `site` rule: land for veg, open sea for water, a calm cloud band for gas, flat ground away from volcanoes for lava, a flat plain or frozen lake for ice, and anywhere for rock. Use the same noise as `featLand`.
2. **Reserve every structure's tier 3 footprint at claim time.** Register discs in an occupancy list `occ = [{x, z, r, kind}]`: each structure at full size, each deposit, each miner route as a capsule, and each link.
3. **Place features after, against `occ`,** using true surface distances. Volcanoes, peaks, spires, boulders, trees, flowers, palms and islands all test against it. Features never need rebuilding when the base grows.
4. **Clean the ground under the plot.** Pass the site centre and radius into `DETAIL_GLSL` (`uSite`), so the close-up detail layer fades out under the plot: no glowing lava cracks under the domes, no frozen-lake cracks under the pad, no canopy texture under the buildings. Draw a type-specific ground treatment instead: cooled basalt, packed snow, cleared earth or regolith.
5. **Water is the exception, and the rule still holds:** structures float on open sea, and islands count as features. Nothing stands on an island.

## 5. The six kits

Every miner shares one **chassis contract**, so crew colours, emblems, glow and the 18 s work cycle keep working:

- slots: `body`, `drive`, `tool`, `cargo`, `beacon`, `tag`
- each kit swaps the parts that go in the slots

### Rock: Vesk, Orra, Kallyur'Dadh, Nyx-4, Myrr, Obelis

*The baseline industrial look: honest machinery cut into stone.*

- **Mine:** an open pit with terraced benches and a steel headframe.
  - T1: a shallow cut, with one bench.
  - T2: a deeper pit, a second bench and a ramp.
  - T3: three benches, the headframe winding wheel turning, and floodlight masts.
- **Miner:** today's laser miner (wheels, laser drill, glass ore capsule). It works the bench faces, and dust kicks up where the beam hits.
- **Pad:** a concrete apron with lit rim.
  - T2: a hangar and fuel tanks.
  - T3: a control tower and a second ring of approach lights.
- **Refinery:** crusher, ball mill and smelt stack, with a conveyor to the pad loader.
  - T2: flotation cells.
  - T3: a tall stack with a heat shimmer and a glowing tap hole.
- **Settlement:** domes bermed with regolith (half-buried, banked), plus window bands. The link is a covered tube.
- **Features:** boulders and spires ring the plot, never inside it.

### Lava: Cinder, Harrow

*Industry that uses the heat instead of fighting it.*

- **Site:** a cooled basalt plateau. Volcanoes, lava rivers and pools stay outside `occ`.
- **Mine:** a **magma tap**, a heat-shielded caisson over its own small lava channel. The channel belongs to the mine, so it isn't a feature conflict.
  - T1: one tap.
  - T2: a second tap, with a cooling-crust skimmer.
  - T3: a tap gantry with a pulsing crucible.
- **Miner:** a heavy **tracked crawler**. It has a heat-shield cowl and a long-handled ladle arm that dips into the channel. Its cargo is a crucible that glows orange while full, and it vents coolant mist.
- **Pad:** a raised deck on stilts with a blast deflector.
  - T2: coolant towers that steam on every landing.
  - T3: deflector walls and heat-shield shutters on the hangar.
- **Refinery:** a natural **lava foundry**, with crucibles fed by gravity and a pour channel. Glowing ingots slide along a conveyor to the pad loader.
  - T3: a second pour line and a spark shower.
- **Settlement:** the current heat-shielded charcoal domes on stilts with ember vents. The settlement's lava pools move outside the plot as features.

### Ice: Mirrow, Vire, Ossa, Grael

*Warm machines in a frozen world. Steam is the signature.*

- **Site:** a flat plain or frozen lake. Peak ranges are kept out.
- **Mine:** a **thermal bore**, a melt-drill derrick over a round shaft, with a steam plume.
  - T1: one bore.
  - T2: an ice-block cutting field with sawn terraces.
  - T3: twin bores and a heated pipe bridge.
- **Miner:** a **tracked snowcat** with a front rotary cutter, throwing ice spray. The cargo bin is frosted, and the cab has warm windows. It leaves crisp tread trails in the snow.
- **Pad:** an insulated pad on stilts, with de-icing vents that steam during descent.
  - T2: a Quonset hangar.
  - T3: a heated runway light line and a windsock mast.
- **Refinery:** a **melt-and-filter plant**: heated tanks, a steam column, and drip icicles on the pipes.
  - T3: a glowing heat exchanger coil.
- **Settlement:** the current frosted ice-glass domes, with crystal clusters kept at the plot's edge.

### Gas: Thale, Solace, Eon, Tessaly, Zenith

*There's no ground, so everything floats. Silhouette comes from lift and tethers.*

- **Site:** a calm band between storm ovals. The three storms and lightning cells are kept out.
- **Mine:** a **cloud scoop**, a floating harvester ring trailing intake funnels down into the clouds, with a vortex in the cloud texture beneath it.
  - T2: a second ring.
  - T3: a long dangling condenser spine that glows as it pulls ore crystals out.
- **Miner:** a **scoop drone** that dives into the cloud deck and resurfaces trailing vapour. It has a wide intake mouth, stub wings and a glowing lift ring. Its cargo is a pressure sphere.
- **Pad:** a floating deck held by lift jets.
  - T2: mooring arms and fuel spheres.
  - T3: a docking cradle with a faint tractor beam guiding the hauler in.
- **Refinery:** a cryo-separation column hanging below its own platform, with centrifuge tanks.
  - T3: a flare stack with a blue-white flame.
- **Settlement:** the current hovering platforms, plus small aerostat envelopes on the City tier. Links are light-bridges.

### Water: Pearlsea, Nerida, Undine

*A harbour on open sea, with mining that happens below the surface.*

- **Site:** open sea over shallows. Islands are features, and nothing stands on them.
- **Mine:** a **dredge rig** over a seamount. A semi-submersible platform with legs into the water, and a riser pipe pulsing with slurry.
  - T2: a second riser and a crane.
  - T3: a moon-pool deck with lights glowing down into the water.
- **Miner:** a **submersible skimmer**. It skims to its deposit, dives (a ring of foam, then its lights fading under the surface), resurfaces with a full cargo pod, and leaves a wake behind it.
- **Pad:** a floating helideck on a pontoon.
  - T2: a breakwater ring.
  - T3: an enclosed harbour basin with a lighthouse beacon.
- **Refinery:** **brine evaporation pans** on floats, with crystallised ore rakes and a flotation tank.
  - T3: a desalination tower.
- **Settlement:** the current pontoon decks with float collars, now joined by floating walkways that bob with the swell.

### Veg: Verdance, Sylvan

*Light-touch mining. The base sits in a clearing, and the forest frames it.*

- **Site:** a meadow clearing on land. Trees and flowers are placed after, ringing the plot so it reads as a clearing cut from the forest.
- **Mine:** **root bores**: narrow extraction shafts with mossy rims, and a bioleach pond that glows faintly green.
  - T2: a terraced dig with retaining walls.
  - T3: a living-roof mine head with hanging vines.
- **Miner:** a **six-legged walker** that steps through the grass without leaving roads. It has harvest claws and a woven cargo pod.
- **Pad:** timber and composite on stilts.
  - T2: a greenhouse hangar.
  - T3: a canopy-height tower with a platform at treetop level.
- **Refinery:** **bioleaching vats** with a green glow and fungal mats.
  - T3: a spore-filter chimney giving off a gentle mist.
- **Settlement:** domes with living roofs and moss. The City tier adds a canopy walkway ring at treetop height. The link is a raised timber walk.

## 6. Performance

- Build the full kit only for the focused planet, as `buildFeatures` does now. Distant planets show a low-detail silhouette (pad, one block per structure), and colonies out of view stay detached.
- Use `InstancedMesh` for repeats: benches, tanks, pontoons, lights, trees around the plot.
- Budget about 15–20 K triangles per tier 3 base at Closest.
- Every light goes through `glowify`, as the visual rules require.
- All per-type textures are drawn once and shared, extending `surfTex` with basalt, packed snow, cleared earth and decking.

## 7. Suggested build order

1. **Framework:** `KIT`, `tierOf`, `pickSite`, `occ` reservation, `uSite` in `DETAIL_GLSL`, and a rock kit that recreates today's look on the compact plot. Check that no feature overlaps `occ` on all 22 planets with a script, like `pwaudit.py`.
2. **Miner chassis contract,** and then the six miners.
3. **Pad and refinery tiers** for each type.
4. **Settlement:** fold `styleSettlement` into the kits.
5. **Guide:** reword the colony and settlement parts.

## Decisions for the owner

- **Tier triggers:** are the tracks in section 2 right, or should every structure simply follow crews hired?
- **Miner count:** 2 per crew (6), or keep 3 per crew (9)?
- **Refinery:** keep it visual only, or later make it the home of Ore yield and Prospecting in the UI?
