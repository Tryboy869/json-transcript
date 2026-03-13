# JTCS — Json-Transcript C# / .NET 8

Runtime package for [Json-Transcript](../) — C# / .NET 8

## Install

```bash
python3 jt.py install JTCS
```

## Commands

```bash
python3 jt.py extract --mode A --target <pkg> --lang csharp
python3 jt.py translate <file.jts> --to csharp
python3 jt.py run <file_csharp.jts>
python3 jt.py convert --from python --to csharp --target <pkg>
```

## Google Colab

```python
!curl -sSL https://raw.githubusercontent.com/tryboy869/json-transcript/main/jt.py -o jt.py
!python3 jt.py install JTCS
!python3 jt.py extract --mode A --target flask --lang python
!python3 jt.py translate flask.jts --to csharp
```

## Runtime: C# / .NET 8

Dependencies: `dotnet add package`
