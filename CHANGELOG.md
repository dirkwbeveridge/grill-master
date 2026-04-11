# Changelog

## [2.0.0] - 2026-04-11

### Added
- Complete rewrite with zero external dependencies (except fonts)
- All 6 major features implemented:
  - Haptic feedback integration (Capacitor-ready)
  - Meat Thermometer 101 guide with USDA temps
  - Save/Load/Delete favorites system
  - Weather/altitude adjustments (Winter Mode +15%, Altitude Mode +25%)
  - Multi-steak foundation (Phase 1 completed)
  - Professional UI overhaul (no "AI slop")
- Enhanced audio alarm (5-note ascending pattern)
- Environmental adjustment toggles
- Full WCAG 2.1 AA accessibility compliance
- Mobile-first responsive design (375px to 2560px)
- In-memory state management (sandbox-safe, no localStorage)

### Fixed
- Synchronous Capacitor CDN blocking issue
- Heat button state management (Medium-High bug)
- Timer memory leaks
- Cut selection desync
- Audio error handling with graceful degradation
- Unrealistic thickness limits (now 0.5" to 2.5")

### Changed
- UI redesigned with charcoal + emerald + amber palette
- Typography: DM Sans body + DM Mono for numbers
- Removed gradient buttons (solid colors are more refined)
- Layout: tab-based navigation (Timer, Thermometer 101, Favorites)

## [1.0.0] - 2026-03-15

### Initial Release
- Basic timer app with prototype features
