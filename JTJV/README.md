# JTJV — Json-Transcript Java 17+

Runtime package for [Json-Transcript](../) — Java 17+

## Install

```bash
python3 jt.py install JTJV
```

## Commands

```bash
python3 jt.py extract --mode A --target <pkg> --lang java
python3 jt.py translate <file.jts> --to java
python3 jt.py run <file_java.jts>
python3 jt.py convert --from python --to java --target <pkg>
```

## Google Colab

```python
!curl -sSL https://raw.githubusercontent.com/tryboy869/json-transcript/main/jt.py -o jt.py
!python3 jt.py install JTJV
!python3 jt.py extract --mode A --target flask --lang python
!python3 jt.py translate flask.jts --to java
```

## Runtime: Java 17+

Dependencies: `maven / gradle`
