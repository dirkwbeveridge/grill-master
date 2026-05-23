# Grill Master iOS App Feature Roadmap

## Purpose

This document prioritizes new features for converting **Grill Master** from a web app into a more robust, native-feeling iPhone app. The roadmap is organized by product impact, implementation complexity, App Store readiness, and differentiation.

## Prioritization Framework

Features are ranked using four criteria:

| Criteria | Meaning |
|---|---|
| User value | Does this make the app materially more useful while grilling? |
| Native iOS value | Does this make the app feel like a real iPhone app rather than a website wrapper? |
| App Store readiness | Does this reduce rejection risk or improve perceived quality? |
| Build complexity | Can it be implemented quickly without creating unnecessary technical debt? |

Priority levels:

- **P0**: Required for credible App Store-ready v1
- **P1**: High-value differentiators for v1.5
- **P2**: Premium/native features for v2
- **P3**: Future or optional expansion

---

# Executive Priority List

| Priority | Feature | Why it matters |
|---|---|---|
| P0 | Local notifications | Critical for timer reliability when app is backgrounded or phone is locked |
| P0 | Persistent favorites and cook state | Prevents users from losing saved cooks or active sessions |
| P0 | iOS-safe layout and app polish | Makes the app feel native and reduces App Store risk |
| P0 | Food safety and temperature guidance | Builds trust and reduces reliance on time-only cooking estimates |
| P0 | Offline-first behavior | Core grilling functions should work without connectivity |
| P1 | Multi-item grill session planner | Converts the app from a timer into a meal coordinator |
| P1 | “Dinner ready at” reverse scheduling | High-impact feature for coordinating full meals |
| P1 | Cook history and notes | Creates stickiness and personalization |
| P1 | Manual temperature logging | Improves accuracy without requiring Bluetooth hardware |
| P1 | Grill profiles | Personalizes recommendations based on grill type and behavior |
| P2 | Live Activities / Dynamic Island | Strong iOS-native experience during active cooks |
| P2 | Siri Shortcuts | Enables hands-free grilling workflows |
| P2 | Apple Watch companion | Useful for haptic alerts and checking timers outdoors |
| P2 | AI grilling assistant | Differentiating feature for planning meals and troubleshooting |
| P3 | Bluetooth thermometer integration | Powerful but higher complexity due to hardware variability |
| P3 | Rubs, marinades, sauces library | Nice content expansion, but secondary to core utility |
| P3 | Cloud sync / account system | Useful later, but avoid adding login friction early |

---

# P0: App Store-Ready Foundation

## 1. Local Notifications

### Description

Add native local notifications for timer milestones, stage transitions, and completion events.

### Example Notifications

- “Flip ribeye now”
- “Move chicken to indirect heat”
- “Start resting steak”
- “Corn is ready”
- “Dinner is ready”

### Why It Matters

A grilling timer must work when the user locks the phone, switches apps, or walks away. Without native notifications, the app behaves like a web timer and is less reliable.

### Implementation Notes

- Use Capacitor Local Notifications.
- Ask for notification permission contextually when the user starts their first cook.
- Schedule notifications based on absolute timestamps, not only in-memory countdowns.
- On app resume, reconcile current time against active cook state.

### Acceptance Criteria

- User receives a notification when the app is backgrounded.
- User receives a notification when the phone is locked.
- Notifications persist across app minimization.
- If permission is denied, the app clearly warns the user that alerts may not work.

---

## 2. Persistent Favorites and Active Cook State

### Description

Ensure favorites, grill queue, user preferences, and active cook sessions persist reliably.

### Why It Matters

Users should not lose their favorite cook settings, active timers, or session progress when they refresh, close, or reopen the app.

### Implementation Notes

- Use local storage or Capacitor Preferences for lightweight persistence.
- Store active cook sessions with start time, stage durations, current stage, item metadata, and scheduled notification IDs.
- On resume, calculate elapsed time from timestamps rather than trusting a suspended timer loop.

### Acceptance Criteria

- Favorites persist after app restart.
- Active cook state survives app backgrounding.
- App can recover if reopened after a timer should have completed.
- User sees a clear status message when returning late to an active timer.

---

## 3. iOS-Safe Layout and Native Polish

### Description

Optimize the UI for iPhone devices, including safe areas, touch targets, orientation behavior, and app-like navigation.

### Why It Matters

This reduces the risk that the app feels like a thin web wrapper.

### Implementation Notes

- Add safe-area padding for notch, Dynamic Island, and home indicator.
- Ensure minimum 44px touch targets.
- Disable accidental zooming if appropriate.
- Improve keyboard and scrolling behavior.
- Add native-feeling tab transitions and active states.
- Add app icon and launch screen.

### Acceptance Criteria

- UI works on small iPhones and large iPhones.
- No controls are blocked by the home indicator.
- Tabs and buttons feel tappable.
- App launches with a polished splash screen.
- App icon is production quality.

---

## 4. Food Safety and Temperature Guidance

### Description

Add clear guidance that cook times are estimates and internal temperature should be used for final doneness.

### Why It Matters

Grilling time varies by grill, cut, thickness, starting temperature, wind, lid position, and thermometer accuracy. Food safety guidance builds trust.

### Implementation Notes

- Add target internal temperatures by protein and doneness.
- Add short disclaimers where time-based estimates are shown.
- Include rest-time guidance and carryover cooking notes.
- Avoid presenting estimated times as guarantees.

### Acceptance Criteria

- Each protein has clear target temperature guidance.
- Timer screens remind users to verify internal temperature.
- High-risk proteins such as poultry include safety-oriented messaging.
- Guidance is concise and non-disruptive.

---

## 5. Offline-First Behavior

### Description

Ensure all core features work without internet access.

### Why It Matters

Users may grill outside, at parks, in poor Wi-Fi areas, or while traveling.

### Implementation Notes

- Package core logic and content inside the app.
- Avoid external dependencies for timer, favorites, queue, and temperature guide.
- Cache all static assets.
- Do not require login for core use.

### Acceptance Criteria

- App opens without internet.
- User can start and complete a cook offline.
- Favorites and temperature guide work offline.
- No critical UI depends on remote assets.

---

# P1: High-Value Product Differentiators

## 6. Multi-Item Grill Session Planner

### Description

Allow users to coordinate multiple items in one grilling session.

### Example

A user wants to cook:

- Ribeye
- Chicken thighs
- Corn
- Asparagus

The app tells the user what to start, flip, move, rest, or remove at each point in the session.

### Why It Matters

This is the strongest feature candidate. It transforms Grill Master from a timer into a full grill-session coordinator.

### Implementation Notes

- Model each item as a cook plan with stages.
- Support overlapping timers.
- Create a unified session timeline.
- Surface the next action prominently.
- Allow users to mark an action complete, snooze, or adjust timing.

### Acceptance Criteria

- User can add multiple items to a session.
- App shows a combined timeline.
- App identifies the next action.
- Notifications fire for each item and stage.
- User can pause, adjust, or remove an item.

---

## 7. “Dinner Ready At” Reverse Scheduling

### Description

Let users select a target serve time, then automatically calculate when each item should start.

### Example

User selects:

> Dinner ready at 6:30 PM

The app generates:

- 5:55 PM: Preheat grill
- 6:05 PM: Start chicken
- 6:14 PM: Start steak
- 6:21 PM: Add vegetables
- 6:24 PM: Rest steak
- 6:30 PM: Serve

### Why It Matters

This is highly useful for real-world meal coordination and would differentiate the app from ordinary timer apps.

### Implementation Notes

- Use cook duration plus rest duration to calculate backward from target serve time.
- Add preheat time assumptions.
- Allow manual adjustment.
- Integrate with multi-item grill sessions.

### Acceptance Criteria

- User can select a desired serve time.
- App calculates start times for all items.
- App provides a clear timeline.
- User can adjust individual item timing.
- Notifications align to the reverse-scheduled plan.

---

## 8. Cook History and Notes

### Description

Let users save completed cooks with notes, ratings, and optional photos.

### Data to Capture

- Protein
- Cut
- Thickness
- Doneness
- Grill type
- Actual cook time
- Rest time
- User rating
- Notes
- Optional photo

### Why It Matters

Cook history makes the app more personal and gives users a reason to return.

### Implementation Notes

- Start with local-only storage.
- Let users duplicate a prior cook into a new session.
- Add “Was this cooked right?” feedback after a timer ends.
- Use history to improve future defaults.

### Acceptance Criteria

- User can save a completed cook.
- User can rate the result.
- User can add notes.
- User can restart a previous cook plan.
- History persists after app restart.

---

## 9. Manual Temperature Logging

### Description

Allow users to manually enter internal temperature readings during a cook.

### Why It Matters

This improves cooking accuracy without requiring Bluetooth thermometer integration.

### Implementation Notes

- Add target temperature ranges by protein and doneness.
- Let users log temperature at any stage.
- Show progress toward target internal temperature.
- Add carryover cooking guidance during rest.

### Acceptance Criteria

- User can enter a current internal temperature.
- App shows target temperature.
- App warns when approaching target.
- App can recommend removing food from heat before final target where carryover applies.

---

## 10. Grill Profiles

### Description

Let users save grill-specific preferences and behavior.

### Example Profiles

- Weber gas grill
- Charcoal kettle
- Pellet grill
- Kamado
- Flat top griddle
- Indoor grill pan

### Profile Attributes

- Grill type
- Runs hot / normal / cool
- Preferred heat level
- Lid open / lid closed preference
- Direct / indirect setup
- Typical preheat time

### Why It Matters

Different grills cook differently. Profiles create personalization and improve recommendations.

### Implementation Notes

- Start with simple presets.
- Allow optional user adjustments.
- Use profiles to modify estimated cook times and prep instructions.

### Acceptance Criteria

- User can create and save a grill profile.
- User can assign a grill profile to a cook.
- App uses profile to adjust guidance.
- Default profile exists for first-time users.

---

# P2: Native and Premium iOS Features

## 11. Live Activities and Dynamic Island

### Description

Show active grill timers on the lock screen and Dynamic Island.

### Why It Matters

This is one of the best ways to make Grill Master feel like a true iPhone app.

### Display Ideas

- Current item
- Time remaining
- Next action
- Current stage
- Serve time
- Internal temperature target

### Implementation Notes

- Requires native iOS work.
- May require a Capacitor plugin or custom Swift implementation.
- Best implemented after core timer state is reliable.

### Acceptance Criteria

- Active cook appears on lock screen.
- Dynamic Island shows current timer state on supported devices.
- User can see next action without opening the app.
- State remains synchronized with in-app timer.

---

## 12. Siri Shortcuts

### Description

Add voice and shortcut actions for common tasks.

### Example Commands

- “Start ribeye timer”
- “Start chicken thighs”
- “What’s next on the grill?”
- “Save this cook”
- “Pause grill timer”

### Why It Matters

Hands-free operation is useful while cooking.

### Implementation Notes

- Start with shortcuts for favorite cooks.
- Add “next action” query later.
- Requires native shortcut integration.

### Acceptance Criteria

- User can start a favorite cook from Siri or Shortcuts.
- User can ask for the next grill action.
- Shortcut actions are reliable and understandable.

---

## 13. Apple Watch Companion

### Description

Add a lightweight Apple Watch experience for active cooks.

### Watch Features

- Countdown timer
- Current item
- Next action
- Haptic alerts
- Mark stage complete
- Pause or resume timer

### Why It Matters

Grilling often happens away from the phone. Watch haptics are more reliable and noticeable.

### Implementation Notes

- Treat this as v2 after iPhone app stability.
- Keep the watch app minimal.
- Avoid duplicating full app functionality.

### Acceptance Criteria

- Watch displays active cook timer.
- Watch sends haptic alerts at stage transitions.
- User can mark actions complete from the watch.
- Watch state stays synchronized with iPhone.

---

## 14. AI Grilling Assistant

### Description

Add a conversational assistant to help users plan meals, troubleshoot cooks, and generate grill plans.

### Example Prompts

- “I have salmon, asparagus, and corn. I want dinner ready in 45 minutes.”
- “My steak is browning too fast but still rare inside. What should I do?”
- “Build a grill plan for burgers and vegetables for six people.”
- “Suggest a rub for chicken thighs.”

### Why It Matters

This is a compelling differentiator, especially if paired with the session planner.

### Implementation Notes

- Keep AI optional.
- Do not require AI for core timer functionality.
- Add guardrails for food safety.
- Convert AI output into structured cook plans only after user confirmation.

### Acceptance Criteria

- User can ask for a meal plan.
- App returns structured steps and timing.
- User can convert recommendations into a grill session.
- App includes safety guidance and avoids overconfident claims.

---

# P3: Future Expansion

## 15. Bluetooth Thermometer Integration

### Description

Connect to compatible Bluetooth meat thermometers.

### Why It Matters

This would make the app much more powerful, but it introduces hardware complexity.

### Risks

- Device compatibility
- Bluetooth permissions
- Vendor-specific protocols
- Connection reliability
- App Store review complexity
- Customer support burden

### Recommended Timing

Do not implement in v1. Consider after the app has traction and clear demand.

---

## 16. Rubs, Marinades, Sauces, and Pairings Library

### Description

Add a content library with rubs, marinades, sauces, sides, and pairings.

### Why It Matters

Useful, but less important than timer reliability and session planning.

### Example Content

- Steak rubs
- Chicken marinades
- Salmon glazes
- BBQ sauces
- Vegetable seasoning
- Suggested sides

### Recommended Timing

Add after core workflows are stable. This could become a premium content module later.

---

## 17. Cloud Sync and Account System

### Description

Allow users to sync cook history, favorites, and profiles across devices.

### Why It Matters

Useful for retention, but not necessary for initial launch.

### Risks

- Login friction
- Privacy policy complexity
- Backend cost
- Security requirements
- Support overhead

### Recommended Timing

Avoid in v1. Add only when users have enough saved data to justify sync.

---

# Recommended Release Plan

## Version 1.0: Credible App Store Launch

Build these first:

1. Capacitor iOS shell
2. Local notifications
3. Persistent favorites
4. Persistent active cook state
5. Offline-first behavior
6. iOS-safe layout
7. App icon and splash screen
8. Food safety and temperature guidance
9. Basic TestFlight QA

### Goal

Deliver a reliable, native-feeling grilling timer that can pass App Store review and work in real-world outdoor cooking scenarios.

---

## Version 1.5: Differentiated Grill Planner

Build next:

1. Multi-item grill session planner
2. “Dinner ready at” reverse scheduling
3. Cook history and notes
4. Manual temperature logging
5. Grill profiles

### Goal

Make the app meaningfully better than a generic timer.

---

## Version 2.0: Premium Native Experience

Build after traction:

1. Live Activities / Dynamic Island
2. Siri Shortcuts
3. Apple Watch companion
4. AI grilling assistant
5. Optional premium feature gating

### Goal

Make Grill Master feel like a premium iOS cooking companion.

---

## Version 3.0: Ecosystem Expansion

Build only if justified by usage:

1. Bluetooth thermometer integrations
2. Cloud sync
3. Shared household profiles
4. Advanced content library
5. Subscription or paid premium tier

### Goal

Expand from a utility app into a broader grilling platform.

---

# Best Single Feature to Build

## “Dinner Ready At” Multi-Item Grill Planning

This should be the long-term anchor feature.

Most grilling apps and timers answer:

> “How long should I cook this?”

Grill Master should answer:

> “How do I get the whole meal done at the same time?”

That is the product wedge.

---

# Codex Implementation Prompt

Use the following prompt with Codex when starting the feature build:

```text
You are working on the Grill Master iOS app conversion. Review the existing single-file HTML/CSS/JavaScript app and implement the roadmap in phases.

Phase 1 objective:
Make the app App Store-ready as a reliable iPhone grilling timer.

Prioritize:
1. Capacitor iOS project setup
2. Local notifications for timer milestones
3. Persistent favorites and active cook state
4. Offline-first behavior
5. iOS safe-area layout polish
6. App icon and splash screen placeholders
7. Food safety and internal temperature guidance

Constraints:
- Preserve existing app behavior unless explicitly improving it.
- Keep core functionality available offline.
- Do not introduce a login requirement.
- Use absolute timestamps for timer recovery.
- Keep the implementation simple and maintainable.
- Add comments where native bridge behavior is introduced.
- Provide a concise implementation summary and testing checklist when complete.

Acceptance tests:
- App runs locally in browser.
- App runs in iOS simulator.
- User can start a cook timer.
- User receives a local notification when the app is backgrounded.
- Favorites persist after app restart.
- Active cook state recovers after app restart.
- Temperature guidance appears for relevant proteins.
- Layout works on small and large iPhone screens.
```

---

# Testing Checklist

## Timer Reliability

- Start timer and keep app open.
- Start timer and lock phone.
- Start timer and switch apps.
- Start timer and force-close app.
- Reopen after timer should have completed.
- Verify notifications and recovered state.

## Persistence

- Save favorite.
- Restart app.
- Confirm favorite remains.
- Start multi-stage cook.
- Background app.
- Reopen and verify correct stage.

## iOS Layout

- Test on small iPhone.
- Test on large iPhone.
- Test portrait orientation.
- Verify safe-area behavior.
- Verify tab navigation.
- Verify touch target size.

## Offline Behavior

- Enable airplane mode.
- Open app.
- Start cook.
- View temperature guide.
- Save favorite.
- Complete timer.

## App Store Readiness

- Confirm app icon exists.
- Confirm splash screen exists.
- Confirm privacy policy is available.
- Confirm support URL is available.
- Confirm no unnecessary permissions are requested.
- Confirm notification permission is requested contextually.
- Confirm food safety guidance is visible.
