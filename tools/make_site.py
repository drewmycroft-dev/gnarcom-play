#!/usr/bin/env python3
"""Assembles the Gnarcom website from releases.json and each release's web
build zip:

    tools/make_site.py <releases.json> <zip_dir> <out_dir>

- Every release's zip must match its sha256 in releases.json and contain only
  the files a Godot web export produces; it is unpacked unchanged into
  <out_dir>/releases/<version>/ next to a build-info.json.
- <out_dir>/index.html is the homepage (newest release first), <out_dir>/latest/
  redirects to the newest release, <out_dir>/releases.json is the public list.
Standard library only.
"""
import hashlib
import html
import json
import shutil
import sys
import zipfile
from pathlib import Path

ALLOWED = {"index.html", "index.js", "index.wasm", "index.pck", "index.png", "index.icon.png",
           "index.apple-touch-icon.png", "index.audio.worklet.js", "index.audio.position.worklet.js"}
REPO = "drewmycroft-dev/gnarcom-play"
SITE_LIMIT = 900 * 1024 * 1024  # GitHub Pages sites max out at 1 GB.


def vkey(v):
    return tuple(int(x) for x in v.split("."))


def unpack(rel, zip_dir, out):
    z = zip_dir / rel["web_asset"]
    digest = hashlib.sha256(z.read_bytes()).hexdigest()
    if digest != rel["sha256"]:
        sys.exit(f"error: {z.name} sha256 {digest} does not match releases.json")
    dest = out / "releases" / rel["version"]
    dest.mkdir(parents=True)
    with zipfile.ZipFile(z) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = Path(info.filename).name
            if name not in ALLOWED:
                sys.exit(f"error: unexpected file in {z.name}: {info.filename}")
            (dest / name).write_bytes(zf.read(info))
    for need in ("index.html", "index.js", "index.wasm", "index.pck"):
        if not (dest / need).is_file():
            sys.exit(f"error: {z.name} has no {need}")
    info = {k: rel[k] for k in ("version", "date", "commit")}
    (dest / "build-info.json").write_text(json.dumps(info, indent=2) + "\n")


def card(rel, latest):
    v = html.escape(rel["version"])
    items = "".join(f"<li>{html.escape(h)}</li>" for h in rel.get("highlights", []))
    badge = '<span class="badge">LATEST</span>' if latest else ""
    return f"""
      <article class="release{' latest' if latest else ''}">
        <header>
          <h3>GNARCOM {v} {badge}</h3>
          <p class="meta">{html.escape(rel["date"])} &middot; {html.escape(rel["title"])}</p>
        </header>
        <ul>{items}</ul>
        <p class="actions">
          <a class="button" href="releases/{v}/">PLAY {v}</a>
          <a class="link" href="https://github.com/{REPO}/releases/tag/v{v}">Release notes</a>
        </p>
      </article>"""


def homepage(releases):
    newest = releases[0]
    cards = "".join(card(r, i == 0) for i, r in enumerate(releases))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gnarcom</title>
<meta name="description" content="Gnarcom: a third-person tactical military shooter you can play in your browser.">
<style>
  :root {{ --bg: #0d0f0c; --panel: #161a14; --line: #2c3326; --text: #d9dccf; --dim: #8d9585;
          --accent: #b9a46a; --go: #6f8b3a; --go-hi: #86a547; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--text);
         font: 16px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }}
  .wrap {{ max-width: 920px; margin: 0 auto; padding: 0 16px; }}
  .hero {{ border-bottom: 1px solid var(--line); padding: 56px 0 40px;
          background: linear-gradient(180deg, #151a11 0%, var(--bg) 100%); }}
  .tag {{ color: var(--accent); letter-spacing: .3em; font-size: 12px; font-weight: 700; margin: 0 0 10px; }}
  h1 {{ font-size: clamp(44px, 9vw, 84px); letter-spacing: .12em; margin: 0; line-height: 1; font-weight: 800; }}
  .lede {{ color: var(--dim); max-width: 620px; margin: 18px 0 28px; font-size: 18px; }}
  .button {{ display: inline-block; background: var(--go); color: #0b0d09; font-weight: 800; letter-spacing: .12em;
            text-decoration: none; padding: 13px 22px; border-radius: 3px; border: 1px solid var(--go-hi); }}
  .button:hover {{ background: var(--go-hi); }}
  .button.big {{ font-size: 18px; padding: 16px 28px; }}
  .note {{ color: var(--dim); font-size: 14px; margin-top: 12px; }}
  h2 {{ letter-spacing: .2em; font-size: 14px; color: var(--accent); margin: 44px 0 16px; }}
  .release {{ background: var(--panel); border: 1px solid var(--line); border-left: 3px solid var(--line);
             border-radius: 3px; padding: 18px 20px; margin-bottom: 14px; }}
  .release.latest {{ border-left-color: var(--accent); }}
  .release h3 {{ margin: 0; letter-spacing: .1em; font-size: 18px; }}
  .badge {{ font-size: 11px; letter-spacing: .15em; color: #0b0d09; background: var(--accent);
           padding: 2px 7px; border-radius: 2px; vertical-align: middle; margin-left: 6px; }}
  .meta {{ color: var(--dim); margin: 4px 0 8px; font-size: 14px; }}
  .release ul {{ margin: 8px 0 14px; padding-left: 20px; }}
  .actions {{ margin: 0; display: flex; gap: 18px; align-items: center; flex-wrap: wrap; }}
  .link {{ color: var(--accent); }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }}
  .box {{ background: var(--panel); border: 1px solid var(--line); border-radius: 3px; padding: 16px 18px; }}
  .box h3 {{ margin: 0 0 8px; font-size: 14px; letter-spacing: .15em; color: var(--accent); }}
  .box p, .box ul {{ margin: 0; color: var(--text); font-size: 15px; }}
  .box ul {{ padding-left: 18px; }}
  kbd {{ font: 13px ui-monospace, monospace; background: #222820; border: 1px solid var(--line);
        border-radius: 3px; padding: 0 5px; }}
  footer {{ border-top: 1px solid var(--line); margin-top: 48px; padding: 22px 0 40px; color: var(--dim); font-size: 13px; }}
</style>
</head>
<body>
  <section class="hero">
    <div class="wrap">
      <p class="tag">TACTICAL THIRD-PERSON SHOOTER</p>
      <h1>GNARCOM</h1>
      <p class="lede">Squad-based team deathmatch on a nighttime harbor. Pick an operator, move with your team,
        and play straight in your browser: no install.</p>
      <a class="button big" href="releases/{html.escape(newest["version"])}/">PLAY GNARCOM {html.escape(newest["version"])}</a>
      <p class="note">Desktop Chrome or Edge recommended. Click the game to lock the mouse; Esc releases it.</p>
    </div>
  </section>
  <main class="wrap">
    <h2>VERSIONS</h2>
    {cards}
    <h2>FIELD MANUAL</h2>
    <div class="grid">
      <div class="box"><h3>CONTROLS</h3><ul>
        <li><kbd>WASD</kbd> move, mouse aim</li>
        <li>Left click fire, right click aim</li>
        <li><kbd>Shift</kbd> sprint, <kbd>C</kbd> crouch, <kbd>Space</kbd> jump</li>
        <li><kbd>R</kbd> reload, <kbd>1</kbd>/<kbd>2</kbd>/<kbd>3</kbd> or wheel swap</li>
        <li><kbd>Q</kbd> shoulder, <kbd>Tab</kbd> score, <kbd>Esc</kbd> menu</li>
      </ul></div>
      <div class="box"><h3>REQUIREMENTS</h3><ul>
        <li>A desktop browser with WebGL 2</li>
        <li>A graphics card is recommended</li>
        <li>Mouse and keyboard</li>
        <li>Every version stays playable here</li>
      </ul></div>
    </div>
  </main>
  <footer>
    <div class="wrap">Gnarcom is an original game made with Godot. Each version is preserved exactly as released.
      Credits: reload sounds "Gun reload sounds" by SpringySpringo (CC0, OpenGameArt); everything else is original.</div>
  </footer>
</body>
</html>
"""


def redirect(version):
    v = html.escape(version)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Gnarcom (latest)</title>
<meta http-equiv="refresh" content="0; url=../releases/{v}/">
<link rel="canonical" href="../releases/{v}/"></head>
<body style="background:#0d0f0c;color:#d9dccf;font-family:system-ui,sans-serif">
<p>Opening <a style="color:#b9a46a" href="../releases/{v}/">Gnarcom {v}</a>...</p></body></html>
"""


def main():
    releases_json, zip_dir, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    releases = json.loads(releases_json.read_text())["releases"]
    versions = [r["version"] for r in releases]
    if len(set(versions)) != len(versions):
        sys.exit("error: duplicate versions in releases.json")
    releases.sort(key=lambda r: vkey(r["version"]), reverse=True)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for rel in releases:
        unpack(rel, zip_dir, out)
    (out / "index.html").write_text(homepage(releases))
    (out / "latest").mkdir()
    (out / "latest" / "index.html").write_text(redirect(releases[0]["version"]))
    shutil.copy(releases_json, out / "releases.json")
    (out / ".nojekyll").write_text("")
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    if size > SITE_LIMIT:
        sys.exit(f"error: site is {size // 2**20} MB, over the {SITE_LIMIT // 2**20} MB budget")
    print(f"site ok: {len(releases)} release(s), latest {releases[0]['version']}, {size / 2**20:.1f} MB")


if __name__ == "__main__":
    main()
