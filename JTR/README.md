# JTR — Json-Transcript Rust 1.75+

Runtime package for [Json-Transcript](../) — Rust 1.75+

## Install

```bash
python3 jt.py install JTR
```

## Commands

```bash
python3 jt.py extract --mode A --target <pkg> --lang rust
python3 jt.py translate <file.jts> --to rust
python3 jt.py run <file_rust.jts>
python3 jt.py convert --from python --to rust --target <pkg>
```

## Google Colab

```python
!curl -sSL https://raw.githubusercontent.com/tryboy869/json-transcript/main/jt.py -o jt.py
!python3 jt.py install JTR
!python3 jt.py extract --mode A --target flask --lang python
!python3 jt.py translate flask.jts --to rust
```

## Runtime: Rust 1.75+

Dependencies: `cargo add axum`
