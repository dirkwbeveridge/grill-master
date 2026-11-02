# Static site validation

Validated November 1, 2026 against the prepared `docs/` files. These checks concern the public support site and listing-copy limits; they do not validate the native app or constitute a legal/privacy review.

## Completed

- Strict local HTML parser check: balanced elements, unique IDs, internal resource paths, and fragment targets pass for all three pages.
- Served under the intended `/grill-master/` subpath. Home, privacy, and support returned HTTP 200 locally.
- Chromium rendered each page at 390 × 844 and 1440 × 1000. All six renders had no horizontal overflow, no page errors, one H1, and named links.
- Captured and visually inspected all six full-page screenshots at `/tmp/grill-master-site/{phone,desktop}-{home,privacy,support}.png`. These files are local evidence, not shipped website assets or native App Store screenshots.
- Resource monitoring found no external requests from any page on initial load. The site uses only local CSS and installed font stacks; it has no JavaScript, forms, embedded third-party content, font downloads, or tracking code.
- Body, secondary, link, button, and paper-sheet foreground/background pairs exceed 4.5:1 contrast. Keyboard skip links, focus-visible outlines, semantic navigation/article headings, native disclosure controls, and unrestricted viewport zoom are implemented.
- App Store name, subtitle, promotional text, and keywords meet their respective 30/30/170/100-character limits. Prepared lengths are 26/22/135/72 after the approved App Store title change.

## Evidence limits and pending checks

The bundled Playwright Chromium executable was absent; verification used the installed `/usr/bin/chromium`. The Impeccable context/detector launcher is absent, so no detector result is claimed. Existing source palette/brand context was read directly. Native VoiceOver and iOS Safari testing are not claimed.

A successful public GitHub Pages deployment and HTTP checks against the production URLs remain pending. External destination availability was not established by the local-link checks. The Pages workflow needs repository Pages configured for GitHub Actions and any deployment-branch/environment protection requirements satisfied. Network/API access and the release owner's GitHub authority determine whether those settings can be completed.

The final signed app must still be compared with the privacy description (including local session persistence and removal of external runtime fonts), and the release owner's legal identity/private contact requirements remain pending. See the release checklist for App Store account, native evidence, signing, privacy, age-rating, and export dependencies.
