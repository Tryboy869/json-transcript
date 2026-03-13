# Contributing to Json-Transcript

## How to contribute

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Add tests if applicable
5. Submit a Pull Request

## Adding a new runtime

1. Create a new folder `JT<X>/`
2. Add `jt<x>.json` with runtime definition
3. Add `README.md` and `README.fr.md`
4. Add translation patterns to `RUNTIME_PATTERNS` in `jt.py`
5. Submit PR

## Reporting issues

Open an issue with:
- JT version
- Command used
- Target tool
- Error output
