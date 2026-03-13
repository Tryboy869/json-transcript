# Changelog

## [1.0.0-beta] — 2026-03-13

### Added
- Initial release
- Hybrid extractor: static (AST) + dynamic (behavioral hooks)
- Domain detection via structural signature similarity (no LLM)
- Auto-translator: Python -> JavaScript/TypeScript/Java/C#/Rust
- CLI: extract, translate, run, convert, validate, install
- Runtime packages: JTP, JTJS, JTJV, JTCS, JTR
- Docker image with all 5 runtimes
- Extraction modes: A (package), C (source), D (binary)
- Validated: Flask 11/11 Python, 11/11 Node.js
- Validated: SmolLM-360M Python->Rust token match (diff < 1e-4)

### Architecture
- `.jts` format: portable behavioral graph
- `jts.json`: central orchestrator (JSON, no shell scripts)
- `jt.py`: unified CLI entry point
