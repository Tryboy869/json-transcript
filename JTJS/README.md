# JTJS — Json-Transcript JavaScript/TypeScript

Runtime package for [Json-Transcript](../) — JavaScript/TypeScript

## Install

```bash
python3 jt.py install JTJS
```

## Commands

```bash
python3 jt.py extract --mode A --target <pkg> --lang javascript
python3 jt.py translate <file.jts> --to javascript
python3 jt.py run <file_javascript.jts>
python3 jt.py convert --from python --to javascript --target <pkg>
```

## Google Colab

```python
!curl -sSL https://raw.githubusercontent.com/tryboy869/json-transcript/main/jt.py -o jt.py
!python3 jt.py install JTJS
!python3 jt.py extract --mode A --target flask --lang python
!python3 jt.py translate flask.jts --to javascript
```

## Runtime: JavaScript/TypeScript

Dependencies: `npm install express`
