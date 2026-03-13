# Json-Transcript — Documentation complete

## Architecture

```
jts.json              <- Orchestrateur central (JSON, pas shell)
jt.py                 <- Point d'entree CLI
Dockerfile            <- Les 5 runtimes en une seule image
JTP/ JTJS/ JTJV/ JTCS/ JTR/  <- Packages runtime
docs/                 <- Documentation
assets/               <- demo.gif, demo.mp4
```

## Le format .jts

Un fichier .jts contient :
- **meta** : source, version, runtime cible
- **static** : structure complete du code source
- **dynamic** : comportements observes a l'execution avec domaines detectes
- **runtime_interface** : interface de controle du runtime cible

## Detection de domaine

Json-Transcript classifie chaque fonction par domaine via similarite structurelle :

| Domaine | Signaux cles |
|---------|-------------|
| RESEAU | method, path, status, url |
| COMPUTE | tensor, matrix, op, transform |
| DATA | query, session, db, cache |
| CONFIG | hook, middleware, register |
