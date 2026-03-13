# Json-Transcript (JT)

> *Extraire n'importe quel outil. Executer partout.*

<video src="assets/json-transcript-fr-720p.webm" width="100%" autoplay loop muted playsinline></video>

**Json-Transcript** est un framework universel de transcription comportementale.
Il extrait le comportement complet de n'importe quel outil logiciel dans un fichier `.jts` portable,
puis l'execute nativement sur n'importe quel runtime cible.

---

## Comment ca fonctionne

```
N'importe quel package Python / repo GitHub / binaire
           ↓  jt extract
      tool.jts
           ↓  jt translate --to rust
   tool_rust.jts
           ↓  jt run
  Execution native Rust
```

---

## Runtimes supportes

| Package | Runtime | Docs |
|---------|---------|------|
| [JTP](JTP/) | Python 3.11+ | [README](JTP/README.md) |
| [JTJS](JTJS/) | JavaScript / TypeScript | [README](JTJS/README.md) |
| [JTJV](JTJV/) | Java 17+ | [README](JTJV/README.md) |
| [JTCS](JTCS/) | C# / .NET 8 | [README](JTCS/README.md) |
| [JTR](JTR/) | Rust 1.75+ | [README](JTR/README.md) |

---

## Demarrage rapide

```bash
curl -sSL https://raw.githubusercontent.com/tryboy869/json-transcript/main/jt.py -o jt.py
python3 jt.py extract --mode A --target flask --lang python
python3 jt.py translate flask.jts --to rust
python3 jt.py run flask_rust.jts --port 8080
```

## Auteur

**Daouda Abdoul Anzize** — Computational Paradigm Designer

Cotonou, Benin

[Portfolio](https://tryboy869.github.io/daa)
