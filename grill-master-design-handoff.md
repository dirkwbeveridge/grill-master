# Grill Master — Design Handoff

**For:** Claude Design / Design AI  
**Project:** Grill Master iOS App  
**Purpose:** Portfolio / showcase project. Needs to look impressive and polished.  
**Date:** 2026-05-22

---

## Project Overview

Grill Master is a science-backed grilling timer app. It calculates precise 4-stage cook times for any meat, cut, thickness, doneness level, and grill conditions. The user selects their protein, answers a few setup questions, and gets a step-by-step timer that walks them through searing, flipping, finishing over indirect heat, and resting.

The app is currently built as a single HTML/CSS/JS file (~2,100 lines). It works well functionally. The problem is it looks generic — it reads as "AI-generated UI" rather than a crafted product. The goal of this redesign is to give it a distinct visual identity that would make it stand out in someone's iOS portfolio.

**Deployment target:** iPhone via Capacitor (web app wrapped in native iOS shell). Treat this as an iPhone app design, not a website.

---

## Design Problem

The current UI is competent but generic:
- Dark theme + amber accent is a common pattern that has no personality
- Typography is clean but lacks hierarchy and editorial voice
- Component spacing feels equal everywhere — nothing has weight
- The timer screen (the main event) doesn't feel exciting to look at
- The app has no brand moments — no onboarding, no identity, no delight

**The redesign should make someone say:** "Who built this?" when they see it. It should read as a real product, not an exercise.

---

## Current Design System (Source of Truth)

### Color Tokens

| Token | Hex | Usage |
|---|---|---|
| `--bg` | `#171411` | App background |
| `--surface` | `#1f1c18` | Card / panel background |
| `--surface-2` | `#272320` | Nested surfaces |
| `--surface-3` | `#302c28` | Deepest nesting |
| `--border` | `rgba(255,243,220,0.08)` | Default dividers |
| `--border-2` | `rgba(255,243,220,0.14)` | Emphasized borders |
| `--text` | `#f2ece0` | Primary text (warm off-white) |
| `--text-muted` | `#9e9488` | Secondary labels |
| `--text-faint` | `#5e574f` | Disabled / placeholder |
| `--amber` | `#e8923a` | Primary accent — active states, CTAs |
| `--amber-dim` | `#c9722a` | Amber on hover / pressed |
| `--amber-glow` | `rgba(232,146,58,0.12)` | Amber background tint |
| `--amber-ring` | `rgba(232,146,58,0.30)` | Focus rings |
| `--green` | `#6ab04c` | Success, completion |
| `--green-dim` | `#4e8c33` | Green hover |
| `--red` | `#d95f52` | Cancel, error, destructive |

### Typography

| Token | Value | Usage |
|---|---|---|
| `--font-body` | DM Sans, system-ui, sans-serif | All UI text |
| `--font-mono` | DM Mono, Courier New, monospace | Timers, temperatures, numbers |

**Font sizes in use:**
- Logo: 18px / weight 700 / letter-spacing -0.02em
- Section labels: 11px / weight 700 / letter-spacing 0.08em / uppercase
- Tab labels: 12px / weight 600 / letter-spacing 0.04em / uppercase
- Body: 14–15px / weight 400–500
- Timer display: 64–80px / DM Mono / weight 700
- Stage label: 13px / weight 600

### Spacing & Radius

| Token | Value |
|---|---|
| `--radius-sm` | 6px |
| `--radius-md` | 10px |
| `--radius-lg` | 16px |
| `--radius-xl` | 22px |

Content padding: 24px horizontal, 20px from edges.  
Content max-width: 480px (centered on larger screens).  
Bottom padding: 100px (leaves room for iPhone home indicator).

### Motion

```
--ease: cubic-bezier(0.16, 1, 0.3, 1)
```
Transitions: 200ms for interactive states. Tab changes: instant (no animation currently).

---

## Screen Inventory

### 1. Timer Tab — Setup Flow

The main tab. Users configure their cook before starting.

**Setup steps (sequential):**

| Step | Component | Notes |
|---|---|---|
| 1. Select protein | Icon button grid, 4 columns (mobile), 8 columns (tablet) | 8 proteins: Beef, Pork, Poultry, Lamb, Burger, Sausage, Veggie, Fish |
| 2. Select cut | Pill button grid | Options vary by protein (3–8 cuts) |
| 3. Select thickness | Range slider | 0.5" to 2.5", 0.25" increments. Only shown for boneless cuts. |
| 4. Select heat | Two-button toggle | Medium (375–450°F) or High (450–550°F) |
| 5. Select doneness | Pill button grid | Varies by protein (e.g., beef gets Rare/Med-Rare/Medium/Well; poultry only gets Safe 165°F) |
| 6. Environmental adjustments | Two toggle switches | Winter Mode (+15%) and High Altitude (+25%). Collapsed until protein is selected. |

**Results card** (shown after all steps are filled):
- Shows 4 stage times: Side A / Side B / Indirect / Rest
- Shows target internal temp
- "Start Cook" primary button

**States:**
- Empty: Shows prompt to select protein
- Partial: Steps complete so far are visible, incomplete steps are hidden
- Ready: Results card appears, Start Cook enabled
- Active cook: Setup form hides, timer display takes over

---

### 2. Timer Tab — Active Cook State

Replaces setup form when a cook is in progress.

**Elements:**
- Stage indicator: current stage name ("Sear — Side A")
- Large countdown: `3:42` in DM Mono, ~80px
- Progress bar: 4 segments, current segment filled in amber
- Stage queue: remaining stages with their times
- Pause / Cancel buttons
- Stage completion overlay (modal): appears when a stage ends ("Time to Flip!")
  - Snooze (+30s) option
  - Confirm / advance to next stage

**States:**
- Running (default)
- Paused: timer frozen, pause button becomes resume
- Stage complete: overlay appears, timer pauses
- Cook complete: success state, "Cook Complete" message, option to save

---

### 3. Grill Queue Tab

Multi-item cook coordinator. Up to 4 lanes (items) can run simultaneously.

**Lane card structure:**
- Cut name + doneness label
- Compact countdown display
- Stage progress (4 dots)
- Start / Pause / Remove controls

**States per lane:**
- Not started (waiting)
- Active (counting down)
- Stage transition (awaiting confirmation)
- Done

**Empty state:** "Add items to coordinate multiple cooks on the same grill"

---

### 4. Temp Guide Tab

Read-only reference screen. No interaction.

**Structure:**
- Section per doneness level (Rare → Well for beef, etc.)
- Color swatch showing meat color at that doneness
- USDA minimum temperature
- Description (e.g., "Cool red center")
- Pro tips section at the bottom

---

### 5. Favorites Tab

Saved cook configurations.

**Favorite card:**
- Name (user-defined, e.g., "Dad's Ribeye")
- Protein + cut label
- Thickness, doneness, heat level
- Load / Delete actions

**Empty state:** "No saved favorites yet. Cook something and save it."

**Save modal:** Triggered from the active cook screen after cook completes. Simple text input for name.

---

### 6. Modals & Overlays

| Modal | Trigger | Contents |
|---|---|---|
| Stage confirm | Timer stage ends | Stage name, action instruction, Snooze (+30s), Confirm |
| Save favorite | After cook completes | Text input for name, Save / Cancel |
| Toast notification | Various actions | Short message, auto-dismisses 2.2s |
| Alarm banner | Stage end | Fixed bottom banner, audio + haptic, action button |

---

## Key User Flow

The primary flow for 90% of sessions:

```
Open app
→ Timer tab (default)
→ Tap protein icon (e.g., Beef)
→ Tap cut (e.g., Ribeye)
→ Drag thickness slider to 1.5"
→ Tap heat level (High)
→ Tap doneness (Med-Rare)
→ Results card appears: Side A 3:30 / Side B 3:30 / Indirect 2:00 / Rest 7:30
→ Tap "Start Cook"
→ Large timer counts down
→ Stage complete → overlay: "Time to Flip!" → tap Confirm
→ Timer continues through all 4 stages
→ Cook complete → option to save as favorite
```

---

## Features Being Added (New Screens to Design)

The following features are planned and will require new UI. Design should accommodate them:

### v1.0 (App Store launch) — already partially built, needs polish
- Local notification permission prompt (contextual, when first cook starts)
- App icon and splash screen
- Food safety inline callouts on timer screens

### v1.5 — New screens needed

**Multi-item session planner:**
- Session view: timeline showing all items and their relative start/end times
- "Next action" card: prominently shows what to do right now
- Add item flow: quick version of the setup flow (protein → cut → doneness → thickness)

**"Dinner Ready At" reverse scheduler:**
- Time picker: select target serve time
- Generated schedule: list of start times per item, working backward
- Adjustments: tap any item to shift its timing

**Cook history:**
- History list: past cooks with date, protein/cut, rating
- Cook detail: full session summary, notes, option to repeat
- "How did it go?" prompt: appears after cook completes (star rating + optional note)

**Manual temperature logging:**
- Temperature input: simple number pad overlay during active cook
- Progress indicator: current temp vs. target temp (e.g., 118°F → 135°F)

**Grill profiles:**
- Profile list: saved grills with icon and name
- Create profile: grill type picker, runs hot/normal/cool toggle, preheat time

### v2.0 — Native iOS features (design direction only, not full specs)
- Live Activity / Lock Screen widget: shows current item, time remaining, next action
- Apple Watch UI: minimal single-screen with timer, stage name, haptic button

---

## UI Direction Options

Four directions explored during brainstorming. Designer should choose one or propose a hybrid.

### Option A: Tactile & Warm
Leather-and-fire aesthetic. Serif typeface touches, deeper warm browns, premium BBQ brand energy. Feels like a product from a specialty grill brand.

- Background shifts warmer: `#1a120a`
- Accent leans more orange-gold
- Consider a serif for display text (Georgia, or a custom food-brand font)
- Button and card surfaces feel denser, less airy

### Option B: Clean & Minimal
iOS-native feel. Tight typography, high contrast, restrained palette. Looks at home next to Things or Fantastical.

- Background goes true near-black: `#0f0f0f`
- Accent becomes a single color (orange or red), used sparingly
- Heavy use of negative space
- System font (`-apple-system`) for body, DM Mono only for timer

### Option C: Bold & High-Contrast
Fire-gradient hero on the active timer card, heavy type weight, aggressive contrast. Readable at arm's length from a hot grill.

- Timer screen features an orange-to-red gradient hero card
- White text on gradient, very large type
- Rest of UI stays dark and quiet to make the timer card pop
- Stage transitions feel like level completions

### Option D: Cockpit / Pro
Data-dense, monospace throughout, glowing readout aesthetic. Feels like precision instrumentation.

- All type in DM Mono or a technical font
- Accent color shifts to cyan (`#00d4ff`) or green (`#00ff9d`)
- Borders glow subtly
- Dense information layout — more data per screen

---

## Platform Requirements (iPhone)

These are non-negotiable for App Store submission:

| Requirement | Detail |
|---|---|
| Safe areas | Top: Dynamic Island / notch. Bottom: 34px home indicator. Use `env(safe-area-inset-*)` |
| Minimum touch target | 44×44pt per Apple HIG |
| Viewport | `width=device-width, initial-scale=1.0, viewport-fit=cover` |
| Status bar | Dark content (white icons) over dark background |
| Overscroll | Suppress bounce or handle gracefully |
| Orientation | Portrait only (locked) for v1 |
| App icon | 1024×1024px, no transparency, no rounded corners in source (iOS applies mask) |
| Splash screen | Full-screen, matches app background color, shows logo |

**Supported devices (minimum):**

| Device | Screen | Note |
|---|---|---|
| iPhone SE (3rd gen) | 375×667pt | Smallest supported |
| iPhone 15 / 16 | 390×844pt | Primary target |
| iPhone 15 / 16 Plus | 430×932pt | Largest common size |
| iPhone 15 / 16 Pro Max | 440×956pt | Dynamic Island, large screen |

---

## Accessibility Requirements

Already implemented in current app — preserve in redesign:

- All interactive elements keyboard accessible
- `role="tab"` / `role="tablist"` / `role="tabpanel"` on navigation
- `role="dialog"` / `aria-modal` on overlays
- `role="alert"` / `aria-live="assertive"` on alarm banner
- Color contrast: 7:1+ on primary text, 4.5:1+ on muted text
- No animations that flash > 3Hz
- `aria-pressed` on toggle buttons
- Minimum 44px touch targets

---

## Component List

| Component | Variants | States |
|---|---|---|
| Tab bar | 4 tabs | Default, Active |
| Protein icon button | 8 proteins | Default, Selected, Hover |
| Pill button (cuts/doneness) | Various | Default, Selected, Disabled |
| Range slider | Thickness | Default, Dragging |
| Heat toggle | Medium / High | Off / On (one active) |
| Toggle switch | On/Off | Default, On, Disabled |
| Results card | — | Hidden, Visible |
| Timer display | — | Running, Paused, Complete |
| Progress bar | 4 segments | Inactive, Active, Complete |
| Stage confirm overlay | Flip, Indirect, Rest, Done | — |
| Save modal | — | Default, Filled, Saving |
| Favorite card | — | Default, Hover, Empty state |
| Lane card (queue) | — | Not started, Active, Paused, Done |
| Toast | — | Default (auto-dismiss) |
| Alarm banner | — | Active, Dismissed |
| Temp guide card | Per doneness level | — |

---

## What "AI Formatted" Means (Design Anti-Patterns to Avoid)

The current app has these issues that make it read as AI-generated:

1. **Equal visual weight everywhere.** Every section label, every card, every button has the same visual presence. Nothing breathes.
2. **Amber on everything.** The accent color does too much work — active state, progress, labels, logos. It loses meaning.
3. **No brand moment.** The header is just a logo icon and text. There's no personality.
4. **Generic timer presentation.** The countdown is just large monospaced text. It doesn't feel like *this* app's timer — it could be any timer.
5. **Pill buttons for everything.** Cuts, doneness, and heat level all use the same pill pattern. No visual differentiation between selection types.
6. **Section labels feel like scaffolding.** `STEP 1 • PROTEIN`, `STEP 2 • CUT` — these read like field labels from a form builder, not designed copy.

---

## Suggested Design Priorities

If the designer needs to focus on a subset, in order:

1. **Active timer screen** — the main event. This is what someone demos. Make it extraordinary.
2. **Timer setup flow** — the journey to the timer. Needs personality and forward motion.
3. **Tab navigation** — sets the tone for the whole app.
4. **Grill Queue / multi-item view** — the differentiating feature. Should look and feel intentional.
5. **Favorites tab** — lower priority but needs good empty state and card design.
6. **Temp Guide** — mostly typographic, just needs clean hierarchy.

---

## What's Not in Scope for This Redesign

- Backend / API work
- Changing the cooking algorithm
- Adding features beyond what's listed in this doc
- Login or account system
- Monetization UI
- Onboarding screens (nice to have, not required)
