# Grill Master release handoff

Prepared repository material:

- [App Store metadata draft](app-store-metadata.md)
- [App Review and TestFlight notes](review-notes.md)
- [Privacy, account, and release checklist](privacy-and-release-checklist.md)
- [Native screenshot capture plan](screenshot-plan.md)

The public support/privacy site lives in `docs/`. Its GitHub Pages workflow uploads only that directory. Set repository Settings → Pages → Build and deployment → Source to **GitHub Actions**. Automatic deployment is limited to `main`; `workflow_dispatch` supports a deliberate release from an allowed branch. The `github-pages` environment's protection rules may need the selected branch allowed. Publication and public HTTP verification must be recorded after deployment.

The intended base URL is https://dirkwbeveridge.github.io/grill-master/. Public pages do not sell the app or load its cooking bundle. The installed iOS app bundles its own interface, and Apple handles paid distribution. No App Store link is generated until the real app record supplies it.

No source document here establishes App Store readiness, Apple approval, archive signing, notification reliability, a completed privacy/export questionnaire, or production deployment. Complete the explicit pending fields and evidence gates before submission.

Deployment record: Pages workflow run [41385344263](https://github.com/dirkwbeveridge/grill-master/actions/runs/41385344263) succeeded and returned the production base URL. Direct cloud HTTP/content checks remain blocked by network policy. Native validation run [41384119053](https://github.com/dirkwbeveridge/grill-master/actions/runs/41384119053) succeeded and generated `native-ios-screenshots`; visual acceptance of that artifact remains pending. A separate TestFlight binding check confirmed incomplete signing/API setup; no upload has occurred.
