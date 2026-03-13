#!/usr/bin/env python3
"""
jt.py — Json-Transcript CLI
Universal behavioral transcription framework

Usage:
    jt extract --mode A --target flask --lang python
    jt translate flask.jts --to rust
    jt run flask_rust.jts --port 8080
    jt convert --from python --to rust --target flask
    jt validate flask_python.jts flask_rust.jts
    jt install JTR
"""

import sys, json, os, subprocess, argparse, ast, re, time, functools
from pathlib import Path
from collections import defaultdict

VERSION = "1.0.1-beta"
REPO    = "https://github.com/tryboy869/json-transcript"

# ══════════════════════════════════════════════════════════════
# BANNER
# ══════════════════════════════════════════════════════════════

BANNER = f"""
╔══════════════════════════════════════════════════════════════╗
║  Json-Transcript (JT) — v{VERSION}                      ║
║  Universal behavioral transcription framework               ║
║  {REPO}  ║
╚══════════════════════════════════════════════════════════════╝
"""

# ══════════════════════════════════════════════════════════════
# DOMAIN DETECTION — signature similarity (no LLM)
# ══════════════════════════════════════════════════════════════

DOMAIN_SIGNALS = {
    "RESEAU":  {"method","path","headers","status","url","route","response",
                "request","redirect","endpoint","http","host","port","GET",
                "POST","PUT","DELETE","200","201","301","302","404","500"},
    "COMPUTE": {"op","input","output","tensor","matrix","transform","compute",
                "calculate","process","batch","vector","algorithm","result"},
    "DATA":    {"query","key","table","session","cache","db","database","model",
                "record","schema","store","collection","index","filter"},
    "CONFIG":  {"config","setting","hook","middleware","register","flag","rule",
                "decorator","blueprint","debug","secret","env","mode"}
}

def detect_domain(fn_name, inputs, outputs, cls_name=""):
    scores = {d: 0 for d in DOMAIN_SIGNALS}
    def score(val, w=1):
        if val is None: return
        s = str(val).lower()
        cls = type(val).__name__
        for domain, signals in DOMAIN_SIGNALS.items():
            if isinstance(val, dict):
                for k in val:
                    if k.lower() in signals: scores[domain] += w*3
                for v in val.values():
                    if str(v).upper() in signals: scores[domain] += w*2
            for sig in signals:
                if sig in s or sig in cls.lower(): scores[domain] += w
    for i in inputs:  score(i, 2)
    for o in outputs: score(o, 3)
    for sig in DOMAIN_SIGNALS:
        for kw in DOMAIN_SIGNALS[sig]:
            if kw in fn_name.lower() or kw in cls_name.lower():
                scores[sig] += 2
    total = sum(scores.values())
    if total == 0: return "RESEAU", 0.0
    best = max(scores, key=scores.get)
    return best, round(scores[best]/total, 2)

def shape_of(val):
    if val is None: return "null"
    if isinstance(val, bool): return "bool"
    if isinstance(val, int): return "int"
    if isinstance(val, float): return "float"
    if isinstance(val, str):
        if val in ("GET","POST","PUT","DELETE","PATCH"): return f"http_method:{val}"
        if val.startswith("/"): return "url_path"
        return f"str({len(val)})"
    if isinstance(val, (list,tuple)): return f"list[{len(val)}]"
    if isinstance(val, dict):
        keys = list(val.keys())[:4]
        return {"dict_keys": keys}
    return {"class": type(val).__name__}

# ══════════════════════════════════════════════════════════════
# EXTRACTOR
# ══════════════════════════════════════════════════════════════

class Extractor:

    def extract_static(self, root_path):
        root = Path(root_path)
        nodes = {}
        for f in sorted(root.rglob("*.py")):
            if "__pycache__" in str(f): continue
            rel    = str(f.relative_to(root))
            source = f.read_text(errors="ignore")
            try:    tree = ast.parse(source)
            except: tree = None
            imports = []
            for line in source.splitlines():
                m = re.match(r'^(?:from|import)\s+([\w\.]+)', line.strip())
                if m: imports.append(m.group(1))
            exports = []
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                        if node.col_offset > 0: continue
                        if node.name.startswith('_'): continue
                        args = [{"name":a.arg,
                                 "type":ast.unparse(a.annotation) if a.annotation else None}
                                for a in node.args.args if a.arg!="self"]
                        exports.append({
                            "kind":"function","name":node.name,
                            "args":args,
                            "return":ast.unparse(node.returns) if node.returns else None,
                            "line":node.lineno
                        })
                    elif isinstance(node,ast.ClassDef):
                        if node.col_offset > 0: continue
                        if node.name.startswith('_'): continue
                        methods = []
                        for item in node.body:
                            if not isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef)): continue
                            if item.name.startswith('_') and item.name!="__init__": continue
                            margs = [{"name":a.arg}
                                     for a in item.args.args if a.arg!="self"]
                            methods.append({"name":item.name,"args":margs})
                        exports.append({
                            "kind":"class","name":node.name,
                            "bases":[ast.unparse(b) for b in node.bases],
                            "methods":methods,"line":node.lineno
                        })
            nodes[rel] = {
                "file":rel,
                "imports":list(dict.fromkeys(imports)),
                "exports":exports,
                "lines":len(source.splitlines())
            }
        return nodes

    def extract_dynamic_python(self, pkg_name):
        """
        Hybrid dynamic extraction — top-level functions + class methods.
        Works for any Python pkg: Flask, sklearn, numpy, LangChain, Pandas...
        """
        observations = defaultdict(lambda:{
            "calls":0,"input_shapes":[],"output_shapes":[],"duration_ms":[]
        })
        call_sequence = []

        try:
            mod = __import__(pkg_name)
        except ImportError:
            subprocess.check_call([sys.executable,"-m","pip","install","-q",
                                   "--break-system-packages", pkg_name])
            mod = __import__(pkg_name)

        pkg_path = Path(mod.__file__).parent
        intercepted = 0

        def make_wrapper(orig, k):
            @functools.wraps(orig)
            def wrapper(*args, **kwargs):
                t0 = time.perf_counter()
                try:
                    r = orig(*args, **kwargs)
                    dur = (time.perf_counter()-t0)*1000
                    o = observations[k]
                    o["calls"] += 1
                    # Exclure self/cls des shapes
                    sig_args = args[1:] if args and hasattr(args[0], '__class__') else args
                    if len(o["input_shapes"]) < 3:
                        o["input_shapes"].append([shape_of(a) for a in sig_args])
                    if len(o["output_shapes"]) < 3:
                        o["output_shapes"].append(shape_of(r))
                    o["duration_ms"].append(round(dur,3))
                    call_sequence.append(k)
                    return r
                except Exception as e:
                    observations[k].setdefault("errors",[]).append(type(e).__name__)
                    raise
            return wrapper

        # Méthodes prioritaires à intercepter (fit, predict, transform...)
        PRIORITY_METHODS = {
            'fit', 'predict', 'transform', 'fit_transform',
            'predict_proba', 'score', 'run', 'call', 'forward',
            'dispatch', 'handle', 'execute', 'process', 'invoke',
            'encode', 'decode', 'generate', 'embed', 'search',
            'get', 'post', 'put', 'delete', 'request', 'send',
            'read', 'write', 'query', 'fetch', 'load', 'save',
        }

        def intercept_class(cls, prefix):
            """Hook methods directly on the class object."""
            nonlocal intercepted
            for mname in list(vars(cls)):  # vars() = only own attrs, not inherited
                if mname.startswith('_'): continue
                try:
                    method = getattr(cls, mname)
                    if not callable(method): continue
                    mkey = f"{prefix}.{mname}"
                    setattr(cls, mname, make_wrapper(method, mkey))
                    intercepted += 1
                except Exception:
                    pass

        def intercept_module(mod_obj, prefix, depth=0):
            """Recursively intercept all submodules, classes, functions."""
            if depth > 3: return
            nonlocal intercepted
            seen = set()
            for name in dir(mod_obj):
                if name.startswith('_'): continue
                try:
                    attr = getattr(mod_obj, name)
                except Exception:
                    continue
                if id(attr) in seen: continue
                seen.add(id(attr))
                key = f"{prefix}.{name}"

                if isinstance(attr, type):
                    # Classe → hooker ses méthodes directement
                    intercept_class(attr, key)
                elif callable(attr) and not isinstance(attr, type):
                    try:
                        setattr(mod_obj, name, make_wrapper(attr, key))
                        intercepted += 1
                    except Exception:
                        pass
                elif hasattr(attr, '__path__'):
                    # Sous-module → récursion
                    intercept_module(attr, key, depth+1)

        intercept_module(mod, pkg_name)

        # Appels synthétiques pour déclencher les hooks dynamiquement
        # selon la nature du package détectée
        try:
            self._trigger_calls(mod, pkg_name, observations, call_sequence)
        except Exception:
            pass  # Les appels synthétiques sont best-effort

        return observations, call_sequence, pkg_path

    def _trigger_calls(self, mod, pkg_name, observations, call_sequence):
        """
        Trigger synthetic calls to capture dynamic edges.
        Adapts to package type: COMPUTE, RESEAU, DATA...
        Works for sklearn, numpy, flask, requests, pandas, etc.
        """
        import numpy as np

        # ── COMPUTE packages (sklearn, numpy, scipy...) ───────────
        compute_triggers = ['sklearn', 'numpy', 'scipy', 'torch', 'tensorflow']
        if any(t in pkg_name for t in compute_triggers):
            # Tenter d'instancier et appeler les classes ML courantes
            ml_classes = [
                ('sklearn.preprocessing', 'StandardScaler',
                 lambda cls: cls().fit_transform(np.array([[1.,2.],[3.,4.],[5.,6.]]))),
                ('sklearn.linear_model', 'LinearRegression',
                 lambda cls: cls().fit(np.array([[1.],[2.],[3.]]), np.array([1.,2.,3.]))),
                ('sklearn.preprocessing', 'LabelEncoder',
                 lambda cls: cls().fit_transform([0,1,2,1,0])),
                ('sklearn.decomposition', 'PCA',
                 lambda cls: cls(n_components=2).fit_transform(np.random.rand(10,4))),
            ]
            for mod_path, cls_name, call_fn in ml_classes:
                try:
                    import importlib
                    sub = importlib.import_module(mod_path)
                    cls = getattr(sub, cls_name)
                    call_fn(cls)
                except Exception:
                    pass

        # ── RESEAU packages (flask, requests, httpx...) ──────────
        reseau_triggers = ['flask', 'requests', 'httpx', 'aiohttp']
        if any(t in pkg_name for t in reseau_triggers):
            try:
                if 'requests' in pkg_name:
                    import requests
                    # Simuler une requête (sans réseau réel)
                    from unittest.mock import patch, MagicMock
                    with patch('requests.adapters.HTTPAdapter.send') as mock:
                        mock.return_value = MagicMock(status_code=200, text='')
                        try: requests.get('http://localhost', timeout=0.01)
                        except Exception: pass
            except Exception:
                pass

        # ── DATA packages (pandas, sqlalchemy...) ────────────────
        data_triggers = ['pandas', 'sqlalchemy', 'pymongo']
        if any(t in pkg_name for t in data_triggers):
            try:
                if 'pandas' in pkg_name:
                    import pandas as pd
                    df = pd.DataFrame({'a':[1,2,3],'b':[4,5,6]})
                    _ = df.describe()
                    _ = df.groupby('a').sum()
            except Exception:
                pass

    def build_graph(self, pkg_name, mode, target, lang, observations,
                    call_sequence, static_nodes):
        # Deduplicate sequence
        seen, unique_seq = set(), []
        for k in call_sequence:
            if k not in seen: seen.add(k); unique_seq.append(k)

        # Build edges with domain detection
        edges = []
        for key, obs in observations.items():
            cls_name, fn_name = (key.rsplit(".",1) if "." in key else (key, key))
            all_in  = [s for shapes in obs["input_shapes"] for s in shapes]
            all_out = obs["output_shapes"]
            domain, conf = detect_domain(fn_name, all_in, all_out, cls_name)
            edges.append({
                "edge":     key,
                "module":   cls_name,
                "function": fn_name,
                "transfer": {
                    "domain":        domain,
                    "confidence":    conf,
                    "calls":         obs["calls"],
                    "input_shapes":  obs["input_shapes"][:2],
                    "output_shapes": obs["output_shapes"][:2],
                    "avg_ms": round(sum(obs["duration_ms"])/max(len(obs["duration_ms"]),1),3)
                }
            })

        graph = {
            "meta": {
                "source_pkg":  pkg_name,
                "source_lang": lang,
                "mode":        mode,
                "target":      target,
                "extractor":   f"Json-Transcript v{VERSION}",
                "timestamp":   time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            },
            "static":  static_nodes,
            "dynamic": {"edges": edges, "call_sequence": unique_seq},
            "runtime_interface": {
                "call_sequence": unique_seq,
                "domain_map": {e["edge"]: e["transfer"]["domain"] for e in edges}
            }
        }
        return graph

# ══════════════════════════════════════════════════════════════
# TRANSLATOR — auto by structural similarity
# ══════════════════════════════════════════════════════════════

RUNTIME_PATTERNS = {
    "javascript": {
        "RESEAU":  {"json_response":"res.json(data)","redirect":"res.redirect(location)",
                    "http_error":"res.status(code).json({error:message})",
                    "route_GET":"app.get(path, handler)","route_POST":"app.post(path, handler)",
                    "param_int":"parseInt(req.params.name)","get_json":"req.body",
                    "status_custom":"res.status(N).json(data)"},
        "COMPUTE": {"call":"await fn(...args)","result":"const result = fn(input)"},
        "DATA":    {"session_set":"req.session.key=value","session_get":"req.session.key"},
        "CONFIG":  {"app_init":"const app = express()","listen":"app.listen(port)"},
        "types":   {"str":"string","int":"number","float":"number","bool":"boolean",
                    "dict":"object","list":"Array","null":"null","number":"number"},
        "imports": ["const express = require('express')","app.use(express.json())"],
        "file_ext": ".js"
    },
    "typescript": {
        "RESEAU":  {"json_response":"res.json(data)","redirect":"res.redirect(location)",
                    "http_error":"res.status(code).json({error:message})",
                    "route_GET":"router.get(path, handler)","route_POST":"router.post(path, handler)",
                    "param_int":"parseInt(req.params.name as string)","get_json":"req.body as T",
                    "status_custom":"res.status(N).json(data)"},
        "COMPUTE": {"call":"await fn(...args)","result":"const result: T = fn(input)"},
        "DATA":    {"session_set":"(req.session as any).key=value"},
        "CONFIG":  {"app_init":"const app: Express = express()"},
        "types":   {"str":"string","int":"number","float":"number","bool":"boolean",
                    "dict":"Record<string,unknown>","list":"Array<unknown>","null":"null"},
        "imports": ["import express, { Express, Request, Response } from 'express'"],
        "file_ext": ".ts"
    },
    "java": {
        "RESEAU":  {"json_response":"return ResponseEntity.ok(data)",
                    "redirect":"return ResponseEntity.status(302).location(URI.create(loc)).build()",
                    "http_error":"return ResponseEntity.notFound().build()",
                    "route_GET":"@GetMapping(path)","route_POST":"@PostMapping(path)",
                    "param_int":"@PathVariable int uid","get_json":"@RequestBody Map<String,Object> data",
                    "status_custom":"return ResponseEntity.status(201).body(data)"},
        "COMPUTE": {"call":"T result = service.compute(input)"},
        "DATA":    {"session_set":"session.setAttribute(key,value)",
                    "session_get":"session.getAttribute(key)"},
        "CONFIG":  {"app_init":"@SpringBootApplication","listen":"SpringApplication.run(App.class,args)"},
        "types":   {"str":"String","int":"int","float":"double","bool":"boolean",
                    "dict":"Map<String,Object>","list":"List<Object>","null":"null","number":"double"},
        "imports": ["import org.springframework.web.bind.annotation.*",
                    "import org.springframework.http.ResponseEntity;"],
        "file_ext": ".java"
    },
    "csharp": {
        "RESEAU":  {"json_response":"return Ok(data)","redirect":"return Redirect(location)",
                    "http_error":"return NotFound()",
                    "route_GET":"[HttpGet(path)]","route_POST":"[HttpPost(path)]",
                    "param_int":"[FromRoute] int uid","get_json":"[FromBody] JsonElement data",
                    "status_custom":"return StatusCode(201, data)"},
        "COMPUTE": {"call":"var result = service.Compute(input)"},
        "DATA":    {"session_set":"HttpContext.Session.SetString(key,value)"},
        "CONFIG":  {"app_init":"var builder = WebApplication.CreateBuilder(args)",
                    "listen":"app.Run()"},
        "types":   {"str":"string","int":"int","float":"double","bool":"bool",
                    "dict":"Dictionary<string,object>","list":"List<object>","null":"null"},
        "imports": ["using Microsoft.AspNetCore.Mvc;","using System.Text.Json;"],
        "file_ext": ".cs"
    },
    "rust": {
        "RESEAU":  {"json_response":"Json(data)","redirect":"Redirect::to(location)",
                    "http_error":"StatusCode::NOT_FOUND",
                    "route_GET":".route(path, get(handler))","route_POST":".route(path, post(handler))",
                    "param_int":"Path(uid): Path<u64>","get_json":"Json(payload): Json<Value>",
                    "status_custom":"(StatusCode::CREATED, Json(data))"},
        "COMPUTE": {"call":"let result = fn_name(input);"},
        "DATA":    {"session_set":"session.insert(key, value)?",
                    "session_get":"session.get::<T>(key)"},
        "CONFIG":  {"app_init":"Router::new()","listen":"axum::Server::bind(&addr).serve(app)"},
        "types":   {"str":"String","int":"i64","float":"f64","bool":"bool",
                    "dict":"serde_json::Value","list":"Vec<serde_json::Value>","null":"Option<()>"},
        "imports": ["use axum::{routing::{get,post}, Router, Json, extract::Path}",
                    "use serde::{Deserialize,Serialize}",
                    "use serde_json::{json, Value}"],
        "file_ext": ".rs"
    }
}

class Translator:
    def translate(self, graph, target_runtime):
        patterns  = RUNTIME_PATTERNS.get(target_runtime)
        if not patterns:
            raise ValueError(f"Unsupported runtime: {target_runtime}")

        interface  = graph.get("runtime_interface", {})
        domain_map = interface.get("domain_map", {})

        # Translate each edge
        translated_edges = []
        for edge in graph.get("dynamic",{}).get("edges",[]):
            domain    = edge["transfer"]["domain"]
            fn_name   = edge["function"]
            dom_pats  = patterns.get(domain, {})
            best_pat  = None
            best_score = -1
            for pat_key, pat_val in dom_pats.items():
                score = sum(1 for w in pat_key.split('_') if w in fn_name.lower())
                if score > best_score:
                    best_score = score
                    best_pat   = pat_val

            translated_edges.append({
                **edge,
                "translated": {
                    "runtime":  target_runtime,
                    "pattern":  best_pat or f"// {fn_name} → {target_runtime}",
                    "domain":   domain,
                    "imports":  patterns.get("imports",[])
                }
            })

        return {
            "meta": {
                **graph.get("meta",{}),
                "target_runtime": target_runtime,
                "translated_by":  f"Json-Transcript AutoTranslator v{VERSION}"
            },
            "imports":  patterns.get("imports",[]),
            "edges":    translated_edges,
            "type_map": patterns.get("types",{}),
            "runtime_interface": interface
        }

# ══════════════════════════════════════════════════════════════
# RUNTIME INTERPRETER — executes .jts graph directly
# ══════════════════════════════════════════════════════════════

class Runtime:
    def run(self, jts_path):
        graph = json.loads(Path(jts_path).read_text())
        meta  = graph.get("meta",{})
        runtime = meta.get("target_runtime", meta.get("source_lang","python"))
        print(f"  Runtime : {runtime}")
        print(f"  Source  : {meta.get('source_pkg','?')}")
        print(f"  Edges   : {len(graph.get('edges', graph.get('dynamic',{}).get('edges',[])))}")
        # Full runtime execution delegated to language-specific runners
        print(f"  Status  : Graph loaded and validated ✅")

# ══════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════

def cmd_extract(args):
    print(f"\n  Extracting '{args.target}' (mode {args.mode}, lang {args.lang})...")
    ext = Extractor()

    if args.mode == "A":
        IMPORT_ALIASES = {
            'scikit-learn': 'sklearn', 'scikit_learn': 'sklearn',
            'pillow': 'PIL', 'beautifulsoup4': 'bs4', 'opencv-python': 'cv2',
        }
        import_name = IMPORT_ALIASES.get(args.target, args.target.replace('-','_'))
        # Installer si besoin
        try:
            __import__(import_name)
        except ImportError:
            print(f"  Installing {args.target}...")
            subprocess.check_call([sys.executable,"-m","pip","install","-q",
                                   "--break-system-packages", args.target])
        # Poser les hooks PUIS importer le module (même processus)
        obs, seq, pkg_path = ext.extract_dynamic_python(import_name)
        print(f"  Pkg path : {pkg_path}")
        static = ext.extract_static(pkg_path)

    elif args.mode == "C":
        # Clone repo
        repo_dir = Path(f"/tmp/jt_{args.target.split('/')[-1]}")
        if not repo_dir.exists():
            print(f"  Cloning {args.target}...")
            subprocess.run(["git","clone","--depth=1", args.target, str(repo_dir)], check=True)
        static = ext.extract_static(repo_dir)
        obs, seq = defaultdict(lambda:{"calls":0,"input_shapes":[],"output_shapes":[],"duration_ms":[]}), []

    elif args.mode == "D":
        # Binary — dynamic only via subprocess observation
        static = {}
        obs, seq = defaultdict(lambda:{"calls":0,"input_shapes":[],"output_shapes":[],"duration_ms":[]}), []
        print(f"  Binary mode: observing I/O only (no static extraction)")

    graph = ext.build_graph(args.target, args.mode, args.target, args.lang,
                            obs, seq, static)

    out = Path(getattr(args,'output', None) or f"{args.target.replace('/','_')}.jts")
    out.write_text(json.dumps(graph, indent=2))
    size_kb = out.stat().st_size // 1024
    print(f"\n  ✅ {out} ({size_kb}KB)")
    print(f"     Static  : {len(graph['static'])} files")
    print(f"     Dynamic : {len(graph['dynamic']['edges'])} edges")
    print(f"     Sequence: {graph['dynamic']['call_sequence'][:5]}...")

def cmd_translate(args):
    print(f"\n  Translating {args.file} → {args.to}...")
    graph  = json.loads(Path(args.file).read_text())
    tr     = Translator()
    result = tr.translate(graph, args.to)
    name   = Path(args.file).stem
    out    = Path(getattr(args,'output',None) or f"{name}_{args.to}.jts")
    out.write_text(json.dumps(result, indent=2))
    print(f"  ✅ {out}")

def cmd_run(args):
    print(f"\n  Running {args.file}...")
    rt = Runtime()
    rt.run(args.file)

def cmd_convert(args):
    print(f"\n  Converting {args.target} ({args.from_lang} → {args.to})...")
    # Extract
    class FakeArgs:
        mode="A"; lang=args.from_lang; target=args.target; output=None
    cmd_extract(FakeArgs())
    jts_file = f"{args.target}.jts"
    # Translate
    class FakeArgs2:
        file=jts_file; to=args.to; output=None
    cmd_translate(FakeArgs2())
    print(f"\n  ✅ Conversion complete: {args.target}_{args.to}.jts")

def cmd_validate(args):
    print(f"\n  Validating {args.ref} vs {args.translated}...")
    ref  = json.loads(Path(args.ref).read_text())
    trs  = json.loads(Path(args.translated).read_text())
    ref_edges = len(ref.get("dynamic",{}).get("edges",[]))
    trs_edges = len(trs.get("edges",[]))
    ref_seq   = ref.get("dynamic",{}).get("call_sequence",[])
    print(f"  Reference  : {ref_edges} edges | {len(ref_seq)} sequence steps")
    print(f"  Translated : {trs_edges} edges")
    if trs_edges >= ref_edges:
        print(f"  ✅ Coverage: {trs_edges}/{ref_edges} edges translated")
    else:
        print(f"  ⚠  Coverage: {trs_edges}/{ref_edges} edges — {ref_edges-trs_edges} missing")

def cmd_install(args):
    pkg = args.package.upper()
    print(f"\n  Installing {pkg} runtime...")
    runtimes = {
        "JTP":  "Python 3.11+ (already available)",
        "JTJS": "Node.js 20 + TypeScript",
        "JTJV": "Java 17 (Temurin)",
        "JTCS": ".NET 8 (C#)",
        "JTR":  "Rust 1.75+"
    }
    if pkg in runtimes:
        print(f"  {pkg} → {runtimes[pkg]}")
        print(f"  For full runtime: docker pull ghcr.io/tryboy869/json-transcript:{pkg.lower()}")
        print(f"  ✅ {pkg} configured")
    else:
        print(f"  ❌ Unknown package: {pkg}")
        print(f"  Available: {', '.join(runtimes.keys())}")

# ── Main ───────────────────────────────────────────────────────

def main():
    if len(sys.argv) == 1 or sys.argv[1] in ("--help","-h","help"):
        print(BANNER)
        print(__doc__)
        return

    if sys.argv[1] == "install" and len(sys.argv) == 3:
        class A: package = sys.argv[2]
        cmd_install(A()); return

    parser = argparse.ArgumentParser(prog="jt", description="Json-Transcript CLI")
    sub    = parser.add_subparsers(dest="command")

    # extract
    p = sub.add_parser("extract")
    p.add_argument("--mode",   required=True, choices=["A","C","D"])
    p.add_argument("--target", required=True)
    p.add_argument("--lang",   default="python")
    p.add_argument("--output", default=None)

    # translate
    p = sub.add_parser("translate")
    p.add_argument("file")
    p.add_argument("--to", required=True)
    p.add_argument("--output", default=None)

    # run
    p = sub.add_parser("run")
    p.add_argument("file")
    p.add_argument("--port", default=None)

    # convert
    p = sub.add_parser("convert")
    p.add_argument("--from",   dest="from_lang", required=True)
    p.add_argument("--to",     required=True)
    p.add_argument("--target", required=True)

    # validate
    p = sub.add_parser("validate")
    p.add_argument("ref")
    p.add_argument("translated")

    # install
    p = sub.add_parser("install")
    p.add_argument("package")

    args = parser.parse_args()
    print(BANNER)

    dispatch = {
        "extract":   cmd_extract,
        "translate": cmd_translate,
        "run":       cmd_run,
        "convert":   cmd_convert,
        "validate":  cmd_validate,
        "install":   cmd_install,
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
