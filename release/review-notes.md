# App Review and TestFlight notes

Prepared notes must be reconciled with the exact submitted binary. Replace the pending fields below before sending them to Apple. Do not submit source-review or browser-test results as native runtime verification.

## App Review information

- Contact first/last name: **PENDING — release owner**.
- Private contact email: **PENDING — monitored address provided by release owner**.
- Contact phone: **PENDING — release owner**.
- Demo account: no sign-in is required for the current app. Confirm this remains true in the submission build.
- Attachments: add a short native screen recording only if it helps explain timer stage progression or recovery behavior; ensure it matches the submitted build.

## Review notes draft

> Grill Master is a local grilling timer and cook log. No account or login is required, and there are no in-app purchases in this build. The paid download is configured through App Store Connect.
>
> To exercise the main flow, open Timer, select Gas, Beef, Ribeye, a thickness, heat, and doneness, then review the estimated cook plan and tap Start Cook. Follow the on-screen stage confirmation prompts. Pause and resume are available during the cook. The Queue tab lets you organize multiple items; the Log stores named cooks locally; the Temp tab contains temperature guidance.
>
> The app requests local notification permission for cooking reminders. Denying permission should leave the cooking interface usable. Notification delivery depends on iOS settings. External Support and Privacy links open the published support site. Cooking times are estimates and the app asks users to verify internal temperature with a food thermometer.
>
> The cooking interface and cooking data are bundled with the app. No Grill Master account, cloud service, remote code download, or advertising SDK is required for the core workflow.

**Final-build verification required:** verify exact labels, multi-item queue behavior, permission-denied behavior, offline operation, and storage persistence before pasting this draft. If Siri/App Intents or Live Activities are added, explain only the exact shipped entry points and provide tested invocation steps. Do not imply those features exist merely because code or an entitlement was added.

## TestFlight “What to Test” draft

Please test Timer, Queue, Log, and Temp on your iPhone or iPad. Cooking times are estimates; use a food thermometer for every cook.

1. Build a cook plan and check that the settings match your food.
2. Start, pause, resume, and end a cook. Check each stage prompt and its controls.
3. Add two different items to the Queue. Check that continuing or extending one item affects only that item, including when two items finish together.
4. Test reminders with notification permission allowed and denied, the app in the background, the phone locked, and Focus settings enabled. Tell us which state applied if an alert fails.
5. Background and reopen the app during an active stage. Relaunch after ending the app and check recovered cook/queue state. Check paused and expired stages separately.
6. Save a named cook in the Log, relaunch, and load it. Report a save error without posting private data.
7. Try large text, VoiceOver, external keyboard, Reduce Motion, iPad rotation/window resizing, and offline mode.
8. On supported iOS versions, invoke Configure Cook, Active Cook, and Temperature Guide from Shortcuts/Siri. Verify the destination opens and no cook starts without confirmation.
9. Add the Current Cook widget. Start, pause, resume, and cancel a main cook; check its snapshot and tap destination.
10. On a compatible device with Live Activities enabled, check the lock-screen/Dynamic Island countdown and stage updates. Let a stage expire while away and verify it asks you to check the cook instead of claiming unattended stage completion.

When reporting a bug, include device, OS, build, steps, expected result, actual result, and the relevant cook settings. Use TestFlight’s feedback mechanism for private diagnostic attachments. Public website support will use a private email address once the owner supplies and verifies it; GitHub Issues is not a customer support channel.

## Release evidence record

| Required evidence | Status/location |
| --- | --- |
| Signed archive, exact version/build and commit | PENDING |
| Xcode and SDK versions satisfying current Apple upload requirements | PENDING |
| App Store Connect build processing/validation result | PENDING |
| iPhone and iPad native test matrix | PENDING |
| Physical iPhone locked/background alert test | PENDING |
| Native screenshot set | PENDING; see screenshot-plan.md |
| Published policy/support URLs return HTTP 200 | PENDING deployment verification |
| External TestFlight beta review, if applicable | PENDING |
| Submission/release approval | PENDING; Apple determines approval |
