# Plan — zhanguo_qunxiong (scope frozen 2026-11-23)

**Shipped build:** Godot 4 WebGL export (`zhanguo-godot/`), deployed at
https://zhanguo-godot.zhanguo-godot.workers.dev/ and mirrored on GitHub Pages.
Full design background: [`../research/design/design_doc.md`](../research/design/design_doc.md).

## Frozen scope (final, 2026-11-23)

- 87-province conquest map, 7 playable great states + minor states acting on interest
- HOI4-style focus tree (schools of the age, sources quoted in-game)
- Statecraft: laws, taxation, officials, corruption, stability
- Diplomacy: treaties, mediation, negotiation
- Warfare: 15 unit types, 13 counter relations, 4 formations, siege, corps merging
- Data layer: 190 generals / 1215 cited battle records / units / provinces, exported
  from a shared SQLite source as JSON
- Verification: 17 headless Godot self-check scripts + Playwright smoke suite
  against both deployed URLs + web-prototype theme-contrast and turn-loop tests
- Design paper: `../paper/design-paper.pdf`

## Non-goals (explicitly cut at the freeze)

- Six-lesson tutorial and the LLM King You agent (live in the web prototype,
  not carried into the shipped build)
- Naval / riverine movement beyond terrain modifiers
- Deep coalition diplomacy (合纵连横 full mechanics)
- Multiplayer, 3D scenes, full battle animations
- Line-by-line re-verification of all 1215 battle records (integrity-checked + sampled)

## Remaining known limits (accepted)

- Voronoi map geometry does not hug historical passes and rivers
- 87-province economy not stress-tested past ~35 turns
- Knowledge-as-asset learning claim remains an unmeasured design hypothesis
