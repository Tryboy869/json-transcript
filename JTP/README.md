# JTP — Json-Transcript Python 3.11+

Runtime package for [Json-Transcript](../) — Python 3.11+

## Install

```bash
python3 jt.py install JTP
```

## Commands

```bash
python3 jt.py extract --mode A --target <pkg> --lang python
python3 jt.py translate <file.jts> --to python
python3 jt.py run <file_python.jts>
python3 jt.py convert --from python --to python --target <pkg>
```

## Google Colab

```python
!curl -sSL https://raw.githubusercontent.com/tryboy869/json-transcript/main/jt.py -o jt.py
!python3 jt.py install JTP
!python3 jt.py extract --mode A --target flask --lang python
!python3 jt.py translate flask.jts --to python
```

## Runtime: Python 3.11+

Dependencies: `pip install flask`
