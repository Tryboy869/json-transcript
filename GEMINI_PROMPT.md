# GEMINI PROMPT — Json-Transcript Visual Assets

## Instructions

Copy this prompt into Google Gemini (gemini.google.com) to generate
the HTML file that produces the demo.gif and demo.mp4 assets.

---

## PROMPT

```
You are an expert frontend developer and motion designer specializing in
developer tooling visuals for 2026. Create a single self-contained HTML file
that generates TWO visual assets for a project called "Json-Transcript":

PROJECT CONTEXT:
- Name: Json-Transcript (JT)
- Tagline: "Extract any tool. Run anywhere."
- Author: Daouda Abdoul Anzize — Computational Paradigm Designer
- What it does: Extracts the behavioral graph of any software tool
  into a portable .jts file, then runs it on any target runtime
- Supported runtimes: Python, JavaScript/TypeScript, Java, C#, Rust
- Key commands:
    jt extract --mode A --target flask --lang python
    jt translate flask.jts --to rust
    jt run flask_rust.jts --port 8080

ASSET 1 — demo.gif (animated, 800x450px)
Design requirements:
- Dark background (#0d1117 GitHub-style)
- Show a terminal animation sequence:
  1. Command appears character by character:
     "$ jt extract --mode A --target flask --lang python"
  2. Progress animation with colored dots
     "[RESEAU] Flask.dispatch_request conf=1.00"
     "[CONFIG] Flask.add_url_rule conf=0.50"
     "[DATA  ] Flask.open_session conf=0.75"
     "✅ flask.jts (117KB) — 24 files | 8 edges"
  3. Second command:
     "$ jt translate flask.jts --to rust"
     "✅ flask_rust.jts generated"
  4. Third command:
     "$ jt run flask_rust.jts --port 8080"
     "✅ SUBSTITUTION VALIDATED | Python → Rust | Match 11/11"
  5. Final frame: Json-Transcript logo + tagline glow effect
- Color palette: 
  - Background: #0d1117
  - Terminal green: #39ff14 (neon)
  - Command text: #58a6ff (GitHub blue)
  - Success: #3fb950 (GitHub green)
  - Domain tags: #f78166 (red), #d2a8ff (purple), #79c0ff (blue)
  - Author accent: #ffa657 (orange)
- Font: JetBrains Mono or Fira Code (monospace)
- Animation: smooth typing effect, no flickering
- Duration: 8-10 seconds loop
- Professional, high-quality, worthy of a GitHub README

ASSET 2 — demo.mp4 preview frame (1280x720px, static frame for thumbnail)
Design requirements:
- Split screen layout:
  LEFT PANEL (dark #0d1117):
    - Large terminal showing the extract/translate/run pipeline
    - Animated domain classification: RESEAU / COMPUTE / DATA / CONFIG
    - Each domain highlighted with its color
  RIGHT PANEL (slightly lighter #161b22):
    - Graph visualization showing the .jts behavioral graph
    - Nodes: Flask functions (circles)
    - Edges: colored by domain
    - Center node: "flask.jts" glowing
    - Surrounding nodes: "flask_rust.jts", "flask_js.jts", "flask_java.jts"
  TOP BAR:
    - "Json-Transcript" logo (bold, gradient purple→blue)
    - "v1.0.0-beta" badge
    - "Extract any tool. Run anywhere." tagline
  BOTTOM BAR:
    - "by Daouda Abdoul Anzize" 
    - GitHub: tryboy869/json-transcript
    - 5 runtime badges: 🐍 Python  ⚡ JS/TS  ☕ Java  # C#  🦀 Rust

TECHNICAL REQUIREMENTS:
- Single HTML file, no external dependencies except Google Fonts
- Use canvas API or CSS animations for the GIF animation
- Include a "Download GIF" button that exports the animation as animated GIF
  using CCapture.js or gif.js (load from CDN)
- Include a "Download MP4 frame" button that exports the static frame as PNG
  (suitable for video thumbnail)
- The HTML must work standalone in a browser
- Add a "Preview" button to play the animation in the browser
- Quality: professional, clean, 2026 dev aesthetic
- No generic AI clipart — pure terminal/code aesthetic

OUTPUT: A complete, working, beautiful single HTML file.
Generate the full file now, no truncation.
```

---

## After generating

1. Download the HTML file from Gemini
2. Open it in Chrome
3. Click "Download GIF" → save as `assets/demo.gif`
4. Click "Download MP4 frame" → save as `assets/demo_thumb.png`
5. Use a screen recorder for `assets/demo.mp4`
6. Place both files in the `assets/` folder of the repo
7. Run the deploy script: `python3 deploy_colab.py`

---

## Alternative: Simple placeholder assets

If Gemini generation is not available, use these quick alternatives:

**For demo.gif:**
Use asciinema (https://asciinema.org) to record a terminal session:
```bash
asciinema rec demo.cast
python3 jt.py extract --mode A --target flask --lang python
python3 jt.py translate flask.jts --to rust
python3 jt.py run flask_rust.jts
```
Then convert with agg: `agg demo.cast assets/demo.gif`

**For demo.mp4:**
Record the same session with OBS or any screen recorder.
