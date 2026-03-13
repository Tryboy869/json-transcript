# Changelog

All notable changes to Json-Transcript are documented here.

---

## [1.0.1-beta] — 2026-03-13

### Fixed
- Import alias map added to `cmd_extract`: `scikit-learn` → `sklearn`, `pillow` → `PIL`, `beautifulsoup4` → `bs4`, `opencv-python` → `cv2`
- Indentation bug in extraction mode A (`cmd_extract`) that caused `pkg_path` and dynamic extraction to be unreachable
- Dynamic extraction now correctly uses resolved `import_name` instead of raw target string

### Changed
- README.md fully rewritten: complete inline documentation, no separate `docs/` folder
- README.fr.md fully rewritten: complete French documentation inline
- Video assets properly linked: EN video in README.md, FR video in README.fr.md
- `demo.gif` used as preview image in both READMEs
- Removed `docs/` folder (documentation now lives in README files)

### Validated
- scikit-learn extracted (626 files, mode A) → JS / Java / Rust / C# — 4×4/4 ✅

### Fixed (extraction)
- Dynamic extractor now hooks class methods recursively (not just top-level functions)
- Added synthetic call triggers for COMPUTE/RESEAU/DATA packages
- sklearn: 27 dynamic edges captured (StandardScaler, LinearRegression, PCA, LabelEncoder)
- Fix: hooks now placed before any user code runs (correct ordering)

---

## [1.0.0-beta] — 2026-03-13

### Added
- Initial release of Json-Transcript
- Hybrid extractor: static AST analysis + dynamic behavioral hooks
- Domain detection via structural signature similarity — no LLM required
- Auto-translator: Python → JavaScript / TypeScript / Java / C# / Rust
- CLI commands: `extract`, `translate`, `run`, `convert`, `validate`, `install`
- Runtime packages: JTP (Python), JTJS (JS/TS), JTJV (Java), JTCS (C#), JTR (Rust)
- Docker image containing all 5 runtimes
- Extraction modes: A (installable package), C (source/GitHub), D (opaque binary)
- `.jts` portable behavioral graph format

### Validated
- Flask (Python) → Python runtime: 11/11 PASS
- Flask (Python) → Node.js runtime: 11/11 PASS
- SmolLM-360M (Python) → Rust: token match, diff < 1e-4
- scikit-learn (Python) → 4 runtimes: 4/4 PASS each
