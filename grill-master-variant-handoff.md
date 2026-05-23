# Grill Master — Visual Variant Selection Brief

**For:** Claude (acting as design lead)
**From:** Dirk Beveridge
**Decision needed:** Pick one of three visual variants (A, B, or C) for my iOS app redesign.

---

## What I need from you

Read the full brief. Then return:

1. **Your pick.** One variant. No hedging.
2. **Why, in 2-3 sentences.** What it does that the others don't.
3. **One specific improvement** you would make to your picked variant before I implement it. (e.g., "tighten the line-height on the stage label," "the cream card in B should have a subtle paper grain," etc.)
4. **One risk to watch.** What could go wrong as this scales across screens.

Be opinionated. Don't list pros and cons of all three. Pick.

---

## Project context

**Grill Master** is a science-backed grilling timer being rebuilt as an iPhone app. It calculates 4-stage cook times (Sear Side A → Side B → Indirect heat → Rest) for any meat, cut, thickness, and doneness level. The existing app is a single-file HTML/CSS/JS web app (~2,100 lines) with Capacitor scaffolding for iOS. It works but looks generic — described as "AI-formatted." That's the problem this redesign solves.

The app will eventually have a **Live Activity / Dynamic Island** widget and an **Apple Watch companion**, so the visual system needs to translate to very small surfaces (the Dynamic Island is roughly 122×37pt; the Watch face is even smaller).

## Audience and goals

This is a **portfolio / showcase project**. The audience is recruiters, hiring managers, and design leads watching a 30-second screen recording on a phone. The bar isn't "useful product" — it's **memorable craft**. The redesign needs to make someone pause the video.

## Brand voice — "Pitmaster's notebook"

Already chosen. The voice is:

- **Earned authority, not enthusiasm.** Like a chef who knows their craft. No exclamation points. No emoji. No "Let's grill!" energy.
- **Imperatives over questions.** `Cut.` not `STEP 2 • PROTEIN`. `Flip.` not `Time to Flip!`. Numbers presented as facts.
- **Hand-built feel.** Warm browns over digital black. Slab serifs or wood-cut display faces paired with monospaced numbers. Mechanical animations, not bouncy.
- **Hierarchy through scale and weight, not color.** The current app uses amber for everything — logo, accent, progress, label, CTA. That's part of why it reads as generic.

---

## The three variants

Each shows the **active timer screen** during the Sear Side A stage of a 1.5" ribeye, medium-rare. This is the hero screen — the moment someone screenshots.

### Variant A — Leather-bound

**Concept:** Deepest browns. Serif throughout for prose, monospace for numbers. Strong notebook-page metaphor with rules and folio numbers. Most editorial.

**Colors:**
- Background: `#1a120a` (deep brown-black, almost charred wood)
- Page rule: `#3a2818`
- Header label: `#c9a875` (aged-paper warm tan)
- Primary numeral: `#f0d9a8` (cream)
- Annotations: `#8a6840` (worn leather)
- Folio mark: `#5c4a32`

**Typography:**
- Header & captions: Georgia / Times serif, uppercase, letter-spacing 4px
- Body annotations: Georgia italic
- Numerals & labels: Courier monospace, letter-spacing 3px

**HTML mockup:**
```html
<div style="background:#1a120a;padding:24px;font-family:Georgia,serif;position:relative;">
  <div style="position:absolute;top:8px;right:12px;color:#5c4a32;font-size:9px;letter-spacing:3px;font-family:'Courier New',monospace;">№ 047</div>
  <div style="color:#c9a875;font-size:11px;letter-spacing:4px;text-transform:uppercase;font-weight:700;margin-bottom:24px;border-bottom:1px solid #3a2818;padding-bottom:8px;">Ribeye · 1.5" · Med-Rare</div>
  <div style="text-align:center;">
    <div style="color:#8a6840;font-size:9px;letter-spacing:3px;text-transform:uppercase;font-family:'Courier New',monospace;margin-bottom:4px;">Side A</div>
    <div style="color:#f0d9a8;font-size:64px;font-family:'Courier New',monospace;font-weight:700;line-height:1;letter-spacing:-2px;">3:42</div>
    <div style="color:#8a6840;font-size:10px;font-style:italic;margin-top:8px;">searing</div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:20px;padding-top:14px;border-top:1px solid #3a2818;font-family:'Courier New',monospace;font-size:9px;letter-spacing:2px;color:#5c4a32;">
    <span>FLIP · 3:42</span><span>FINISH · 2:00</span><span>REST · 5:00</span>
  </div>
</div>
```

---

### Variant B — Prep Ticket

**Concept:** Cream order-ticket card floating on dark surface. The kitchen-pass / butcher-paper metaphor made literal. Most visually striking. Breaks the "every app is dark mode" pattern, which is rare for portfolio apps.

**Colors:**
- App background: `#14110c` (near-black, very warm)
- Card (paper): `#f4ead3` (warm cream, slightly aged)
- Card text: `#1a1410` (near-black ink)
- Stage accent: `#7a3d1f` (rust / fire brick)
- Annotations: `#5c4a32` and `#c9a875`

**Typography:**
- Title: Georgia serif, weight 700, uppercase
- Numerals: Courier monospace, weight 700
- Stage label: Georgia serif, uppercase, letter-spacing 3px
- Annotations: Courier monospace

**HTML mockup:**
```html
<div style="background:#14110c;padding:18px;">
  <div style="background:#f4ead3;color:#1a1410;padding:18px 16px;border-radius:2px;position:relative;box-shadow:0 8px 24px rgba(0,0,0,0.5);">
    <div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:1.5px solid #1a1410;padding-bottom:8px;margin-bottom:12px;">
      <span style="font-family:Georgia,serif;font-weight:700;font-size:14px;text-transform:uppercase;letter-spacing:1px;">Ribeye</span>
      <span style="font-family:'Courier New',monospace;font-size:10px;">1.5" · MED-RARE</span>
    </div>
    <div style="text-align:center;padding:8px 0;">
      <div style="font-family:'Courier New',monospace;font-size:60px;font-weight:700;color:#1a1410;line-height:1;letter-spacing:-2px;">3:42</div>
      <div style="font-family:Georgia,serif;font-size:11px;text-transform:uppercase;letter-spacing:3px;color:#7a3d1f;font-weight:700;margin-top:2px;">SIDE A · SEAR</div>
    </div>
    <div style="font-family:'Courier New',monospace;font-size:9px;color:#5c4a32;display:flex;justify-content:space-between;border-top:1px dashed #c9a875;padding-top:8px;margin-top:8px;">
      <span>flip 3:42</span><span>finish 2:00</span><span>rest 5:00</span>
    </div>
  </div>
</div>
```

---

### Variant C — Charred

**Concept:** Modern editorial layout with one strong vertical rule. Burnt-orange accent used sparingly. The most contemporary — feels like a "Field Notes" app for grilling. Easiest to translate to Watch and Dynamic Island because the layout is composable: a vertical accent + a number + small labels works at any size.

**Colors:**
- Background: `#0f0a06` (deepest warm black)
- Header eyebrow: `#7a5a3a`
- Vertical rule: `#d4661a` (burnt orange / ember)
- Stage label (small): `#5c4a32`
- Primary numeral: `#f5e4c8`
- Stage label (accent): `#d4661a`
- Progress (inactive): `#3a2818`

**Typography:**
- Header eyebrow: Courier monospace, weight 700, letter-spacing 4px
- Stage label (small): Courier monospace, weight 700, letter-spacing 3px
- Primary numeral: Courier monospace, weight 500, letter-spacing -3px
- Stage label (accent): system-ui, weight 600, letter-spacing 2px

**HTML mockup:**
```html
<div style="background:#0f0a06;padding:20px;font-family:-apple-system,sans-serif;">
  <div style="color:#7a5a3a;font-size:10px;letter-spacing:4px;text-transform:uppercase;font-family:'Courier New',monospace;margin-bottom:6px;font-weight:700;">RIBEYE / 1.5 IN / MED-RARE</div>
  <div style="border-left:3px solid #d4661a;padding-left:14px;margin:10px 0;">
    <div style="color:#5c4a32;font-size:9px;letter-spacing:3px;text-transform:uppercase;font-weight:700;">SIDE A</div>
    <div style="color:#f5e4c8;font-size:72px;font-family:'Courier New',monospace;font-weight:500;line-height:1;letter-spacing:-3px;margin:2px 0;">3:42</div>
    <div style="color:#d4661a;font-size:11px;letter-spacing:2px;text-transform:uppercase;font-weight:600;">searing</div>
  </div>
  <div style="display:flex;gap:1px;margin-top:16px;">
    <div style="flex:1;height:3px;background:#d4661a;"></div>
    <div style="flex:1;height:3px;background:#3a2818;"></div>
    <div style="flex:1;height:3px;background:#3a2818;"></div>
    <div style="flex:1;height:3px;background:#3a2818;"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:6px;font-family:'Courier New',monospace;font-size:9px;color:#5c4a32;letter-spacing:1px;">
    <span>SIDE B</span><span>FINISH</span><span>REST</span><span>DONE</span>
  </div>
</div>
```

---

## Evaluation criteria

Weight these in your recommendation:

1. **Does it break the "AI-formatted dark mode + amber accent" pattern?** This is the central problem we're solving. The variant should look like a designed product, not a template.
2. **Will it translate to Dynamic Island and Apple Watch?** Those are tiny surfaces. A variant that depends on rich typographic chrome may not survive the compression.
3. **Is the Pitmaster voice present visually, not just in copy?** Does the visual style itself feel "earned authority" rather than enthusiastic or playful?
4. **Does it scale to other screens?** This is the hero timer. But there's also: setup, the log (cook history), grill queue, stage transition overlays, and the cook complete state. The variant has to work for all of them.

## Constraints already locked

Don't re-litigate these:

- **Brand voice:** Pitmaster's notebook (already chosen)
- **Audience:** Portfolio / showcase
- **Stack:** Vanilla JS + Capacitor, no React
- **No emoji, no exclamation points**
- **Numbers are facts** — Courier or DM Mono for all numerals

## What "Claude Design" should NOT do

- Don't propose a new variant. Pick from A, B, or C. (You can propose tweaks to the picked one.)
- Don't ask clarifying questions before answering. Make the call with the information given.
- Don't hedge.
