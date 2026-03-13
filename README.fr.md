<div align="center">

<img src="assets/demo.gif" alt="Json-Transcript" width="100%"/>

<video src="assets/json-transcript-fr-720p.webm" width="100%" autoplay loop muted playsinline></video>

# Json-Transcript (JT)

**Framework universel de transcription comportementale**

*Extraire n'importe quel outil. Exécuter partout.*

[![Version](https://img.shields.io/badge/version-1.0.1--beta-blue?style=flat-square)](https://github.com/Tryboy869/json-transcript/releases)
[![Licence](https://img.shields.io/badge/licence-MIT-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python)](JTP/)
[![JavaScript](https://img.shields.io/badge/JS%2FTS-Node20+-yellow?style=flat-square&logo=javascript)](JTJS/)
[![Java](https://img.shields.io/badge/java-17+-orange?style=flat-square&logo=java)](JTJV/)
[![CSharp](https://img.shields.io/badge/C%23-.NET8-purple?style=flat-square&logo=dotnet)](JTCS/)
[![Rust](https://img.shields.io/badge/rust-1.75+-red?style=flat-square&logo=rust)](JTR/)

</div>

---

## Qu'est-ce que Json-Transcript ?

Json-Transcript extrait le **graph comportemental complet** de n'importe quel outil logiciel — sa structure statique + ses patterns d'exécution en temps réel — dans un fichier `.jts` portable unique. Ce fichier est ensuite exécuté nativement sur n'importe quel runtime cible.

Pas de transpilation. Pas de simulation. **Assimilation comportementale.**

```
N'importe quel package Python / repo GitHub / binaire opaque
              ↓   jt extract
         tool.jts   ←── graph comportemental universel
              ↓   jt translate --to rust
       tool_rust.jts
              ↓   jt run
    Exécution native Rust — zéro dépendance Python
```

---

## Pourquoi Json-Transcript ?

| Problème | Solution |
|----------|----------|
| scikit-learn n'a pas d'équivalent natif en Rust | Extraire sklearn → exécuter sur runtime Rust |
| Un codebase Python de 10 ans doit devenir Go | Extraire → traduire → exécuter |
| Un binaire propriétaire doit être porté | Observer ses I/O → extraire → répliquer |
| Vous voulez LangChain en TypeScript nativement | Extraire → traduire → done |

---

## Runtimes supportés — v1.0.1-beta

| Package | Runtime | Installation |
|---------|---------|-------------|
| **JTP** | Python 3.10+ | `jt install JTP` |
| **JTJS** | JavaScript / TypeScript (Node 20+) | `jt install JTJS` |
| **JTJV** | Java 17+ | `jt install JTJV` |
| **JTCS** | C# / .NET 8 | `jt install JTCS` |
| **JTR** | Rust 1.75+ | `jt install JTR` |

---

## Installation

**Terminal / SSH :**
```bash
curl -sSL https://raw.githubusercontent.com/Tryboy869/json-transcript/main/jt.py -o jt.py
python3 jt.py --help
```

**Google Colab :**
```python
!curl -sSL https://raw.githubusercontent.com/Tryboy869/json-transcript/main/jt.py -o jt.py
!python3 jt.py --help
```

**Docker (tous les runtimes) :**
```bash
docker pull ghcr.io/tryboy869/json-transcript:latest
docker run -it json-transcript jt extract --mode A --target flask --lang python
```

---

## Modes d'extraction

| Mode | Description | Cas d'usage |
|------|-------------|-------------|
| `A` — Package | `pip install` + AST statique + hooks dynamiques | Tout package Python publié |
| `C` — Source | Repo GitHub ou dossier local | Projets open source |
| `D` — Binaire | Observation I/O dynamique uniquement | Outils propriétaires / closed-source |

---

## Commandes

```bash
# Extraire un package Python (mode A)
python3 jt.py extract --mode A --target flask --lang python

# Extraire depuis GitHub (mode C)
python3 jt.py extract --mode C --target https://github.com/pallets/flask --lang python

# Extraire un binaire (mode D)
python3 jt.py extract --mode D --target ./myapp.bin

# Traduire vers un runtime cible
python3 jt.py translate flask.jts --to rust
python3 jt.py translate flask.jts --to javascript
python3 jt.py translate flask.jts --to java
python3 jt.py translate flask.jts --to csharp

# Exécuter le graph sur son runtime (via Docker)
python3 jt.py run flask_rust.jts --port 8080

# Extraire + traduire en une commande
python3 jt.py convert --from python --to rust --target flask

# Valider : comparer référence vs traduit
python3 jt.py validate flask.jts flask_rust.jts

# Installer un package runtime
python3 jt.py install JTR
```

---

## Le format .jts

Un fichier `.jts` est un **graph comportemental portable** — du JSON pur :

```json
{
  "meta": {
    "source_pkg":     "flask",
    "source_lang":    "python",
    "target_runtime": "rust",
    "extractor":      "Json-Transcript v1.0.1-beta"
  },
  "static": {
    "app.py": {
      "imports": ["werkzeug", "click"],
      "exports": [{ "kind": "class", "name": "Flask", "methods": [...] }],
      "lines": 612
    }
  },
  "dynamic": {
    "edges": [
      {
        "edge":     "Flask.dispatch_request",
        "transfer": {
          "domain":       "RESEAU",
          "confidence":   1.0,
          "input_shapes": [{ "method": "http_method:GET", "path": "url_path" }],
          "output_shapes": [{ "class": "Response", "attrs": { "status_code": "int" } }]
        }
      }
    ],
    "call_sequence": ["Flask.add_url_rule", "Flask.dispatch_request", "Flask.make_response"]
  },
  "runtime_interface": {
    "routes": [...],
    "hooks":  { "before_request": true, "after_request": true },
    "domain_map": { "Flask.dispatch_request": "RESEAU" }
  }
}
```

---

## Détection de domaine — Sans LLM

Json-Transcript classifie chaque fonction par **similarité de signature structurelle** — sans IA, sans règles manuelles, sans mapping codé :

| Domaine | Signaux détectés | Exemple |
|---------|-----------------|---------|
| `RESEAU` | `method`, `path`, `status`, `headers`, `url` | Routes Flask, handlers HTTP |
| `COMPUTE` | `tensor`, `matrix`, `op`, `transform`, `fit` | sklearn, numpy, PyTorch |
| `DATA` | `query`, `session`, `db`, `cache`, `key` | SQLAlchemy, Redis, MongoDB |
| `CONFIG` | `hook`, `middleware`, `register`, `blueprint` | Config app, décorateurs |

Chaque domaine mappe vers des **patterns runtime** lors de la traduction :

```
RESEAU + rust   →  axum handler
RESEAU + java   →  @GetMapping controller
COMPUTE + js    →  async function avec typed arrays
DATA + csharp   →  ISession / DbContext
```

---

## Résultats validés

| Source | Cible | Tests | Statut |
|--------|-------|-------|--------|
| Flask (Python) | Python runtime | 11/11 | ✅ |
| Flask (Python) | Node.js runtime | 11/11 | ✅ |
| SmolLM-360M (Python) | Rust (Axum) | Token match | ✅ diff < 1e-4 |
| scikit-learn (Python) | JS / Java / Rust / C# | 4×4/4 | ✅ |

---

## Cas d'usage réels

**1. Migration legacy**
```bash
# 30 ans de logique COBOL → Java moderne
jt extract --mode D --target ./legacy.bin
jt translate legacy.jts --to java
jt run legacy_java.jts
```

**2. Inférence ML sans Python**
```bash
# Pipeline scikit-learn → microservice Rust
jt convert --from python --to rust --target scikit-learn
jt run scikit-learn_rust.jts
```

**3. Portabilité de framework**
```bash
# API Flask → Express (Node.js)
jt convert --from python --to javascript --target flask
jt run flask_javascript.jts --port 3000
```

**4. Réplication de binaire propriétaire**
```bash
# Outil closed-source, pas d'accès au code source
jt extract --mode D --target ./proprietary_tool.bin
jt translate proprietary_tool.jts --to csharp
```

---

## Packages runtime

### JTP — Python
```bash
python3 jt.py extract --mode A --target <pkg> --lang python
python3 jt.py translate <file.jts> --to python
```

### JTJS — JavaScript / TypeScript
```bash
python3 jt.py translate <file.jts> --to javascript
python3 jt.py translate <file.jts> --to typescript
```

### JTJV — Java
```bash
python3 jt.py translate <file.jts> --to java
```

### JTCS — C# / .NET
```bash
python3 jt.py translate <file.jts> --to csharp
```

### JTR — Rust
```bash
python3 jt.py translate <file.jts> --to rust
```

---

## Architecture

```
json-transcript/
├── jt.py                  ← Point d'entrée CLI (un seul fichier, sans install)
├── jts.json               ← Orchestrateur central — JSON contrôle tout
├── Dockerfile             ← Les 5 runtimes en une image
├── JTP/  JTJS/  JTJV/  JTCS/  JTR/   ← Packages runtime
│   └── README.md + README.fr.md + <pkg>.json
└── assets/
    ├── demo.gif
    ├── json-transcript-en-720p.webm
    └── json-transcript-fr-720p.webm
```

**La philosophie :** `jts.json` est l'orchestrateur. Pas de scripts shell, pas de Makefiles — JSON orchestre du JSON.

---

## Changelog

**v1.0.1-beta** — 2026-03-13
- Fix : table d'alias d'import (`scikit-learn` → `sklearn`, `pillow` → `PIL`, etc.)
- Fix : bug d'indentation mode A dans `cmd_extract`
- Amélioration : l'extraction dynamique utilise maintenant `import_name` résolu
- Docs : README réécrit — documentation complète intégrée, pas de dossier docs/ séparé
- Docs : assets vidéo correctement liés (EN/FR)
- Assets : demo.gif + vidéos webm intégrées

**v1.0.0-beta** — 2026-03-13
- Release initiale
- Extracteur hybride : AST statique + hooks comportementaux dynamiques
- Détection de domaine par similarité de signature structurelle (sans LLM)
- Traducteur automatique : Python → JS / TS / Java / C# / Rust
- CLI : extract, translate, run, convert, validate, install
- Packages runtime : JTP, JTJS, JTJV, JTCS, JTR
- Image Docker avec les 5 runtimes
- Modes d'extraction : A (package), C (source), D (binaire)
- Validé : Flask 11/11 Python + 11/11 Node.js
- Validé : SmolLM-360M Python → Rust token match (diff < 1e-4)

---

## Contribuer

1. Fork → `git checkout -b feature/ma-feature`
2. Modifications + tests si applicable
3. Pull Request

Pour ajouter un runtime : créer `JT<X>/`, ajouter `jt<x>.json` + READMEs, ajouter les patterns de traduction dans `RUNTIME_PATTERNS` dans `jt.py`.

---

## Licence

MIT — Copyright (c) 2026 Daouda Abdoul Anzize

---

<div align="center">

**Daouda Abdoul Anzize** — Computational Paradigm Designer

Cotonou, Bénin → Global Remote

[Portfolio](https://tryboy869.github.io/daa) · [Twitter](https://twitter.com/Nexusstudio100) · [LinkedIn](https://linkedin.com/in/anzize-adeleke-daouda)

*"Je ne construis pas des apps. Je construis l'argile que les autres utilisent pour construire des apps."*

</div>
