# Json-Transcript — Full Documentation

## Architecture

```
jts.json              <- Central orchestrator (JSON, not shell)
jt.py                 <- CLI entry point
Dockerfile            <- All 5 runtimes in one image
JTP/ JTJS/ JTJV/ JTCS/ JTR/  <- Runtime packages
docs/                 <- Documentation
assets/               <- demo.gif, demo.mp4
```

## The .jts format

```json
{
  "meta": { "source_pkg", "source_lang", "target_runtime" },
  "static": { "file.py": { "imports", "exports", "lines" } },
  "dynamic": {
    "edges": [
      {
        "edge": "Flask.dispatch_request",
        "transfer": {
          "domain": "RESEAU",
          "confidence": 1.0,
          "input_shapes": [...],
          "output_shapes": [...]
        }
      }
    ]
  },
  "runtime_interface": { "routes", "hooks", "domain_map" }
}
```

## Domain detection

Json-Transcript classifies every function by domain using structural signature similarity:

| Domain | Key signals |
|--------|------------|
| RESEAU | method, path, status, url, headers |
| COMPUTE | tensor, matrix, op, transform |
| DATA | query, session, db, cache, key |
| CONFIG | hook, middleware, register, flag |

## Commands reference

| Command | Description |
|---------|------------|
| `jt extract` | Extract behavioral graph |
| `jt translate` | Translate to target runtime |
| `jt run` | Execute .jts graph |
| `jt convert` | Extract + translate in one step |
| `jt validate` | Compare reference vs translated |
| `jt install` | Install runtime package |
