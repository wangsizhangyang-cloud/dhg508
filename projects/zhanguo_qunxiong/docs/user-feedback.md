# User Feedback Log

Two external testers used the deployed build on their own devices
(2026-11-16 to 2026-11-22). Each issue was fixed and locked in with a
regression test, per the Week 10–11 requirement (>= 2 external testers,
fixes turned into permanent tests).

## Tester 1 — visual fatigue

- **What they did:** played a full campaign session on a laptop browser.
- **What they reported:** font colours and background were 刺眼 (harsh on
  the eyes) after a few minutes; long text panels were tiring to read.
- **Fix:** palette reworked to soften text/background contrast against the
  dark panels (`--txt` softened, backgrounds darkened slightly).
- **Locked in as:** WCAG colour-contrast guard —
  `战国群雄游戏/tests/theme-contrast.test.mjs` parses the theme variables
  and asserts AA ratios (text >= 4.5, accents >= 3) plus a
  no-invisible-colour check. A regression to the harsh palette fails the
  build.

## Tester 2 — cumbersome controls

- **What they did:** played through nation selection, army movement and
  several battles.
- **What they reported:** operations too cumbersome — too many clicks to
  move armies and confirm each turn.
- **Fix:** movement and turn-confirmation flow streamlined into fewer,
  combined actions; keyboard shortcuts (Space = end turn) promoted to
  first-class interaction, documented in-game.
- **Locked in as:** Playwright interaction test —
  `战国群雄游戏/tests/turn-flow.spec.mjs` boots the game, picks Qin, and
  requires that a single Space keypress (and the end-turn button) advances
  the turn with zero console errors. A regression to the verbose
  modal-click flow fails the build.

## Summary

| Issue | Severity | Fix | Regression test |
|---|---|---|---|
| Harsh colour scheme | Medium (readability) | Softened palette | `theme-contrast.test.mjs` (9 assertions) |
| Cumbersome controls | High (playability) | Streamlined order + turn flow, hotkeys | `turn-flow.spec.mjs` (3 E2E tests) |
