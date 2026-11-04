# Gnarcom: play in your browser

**Play: https://drewmycroft-dev.github.io/gnarcom-play/**

Gnarcom is an original third-person tactical shooter: 4v4 team deathmatch,
Navy SEALs vs insurgents, on a nighttime harbor. Made with Godot 4. Every
released version stays playable on the site:

- Homepage with all versions: https://drewmycroft-dev.github.io/gnarcom-play/
- Newest version: https://drewmycroft-dev.github.io/gnarcom-play/latest/
- A specific version: `https://drewmycroft-dev.github.io/gnarcom-play/releases/<version>/`

Controls: WASD move · mouse aim · left click fire · right click aim down
sights · Shift sprint · C crouch · Space jump · R reload · 1/2/3 or mouse
wheel switch weapons · Q swap shoulder · Tab scoreboard · Esc menu. Click the
game to start (the browser needs a click to lock the mouse). Desktop Chrome or
Edge with WebGL 2 recommended.

## About this repository

This repository only publishes the game; it contains no game source code.

- Each version's browser build is attached to its
  [release](https://github.com/drewmycroft-dev/gnarcom-play/releases)
  (`gnarcom-<version>-web.zip`) and listed with its checksum in
  [releases.json](releases.json).
- The [deploy workflow](.github/workflows/deploy.yml) runs only when started
  by hand: it downloads every listed release, checks its checksum and files,
  unpacks it unchanged into `/releases/<version>/`, builds the homepage with
  [tools/make_site.py](tools/make_site.py), and publishes to GitHub Pages.
  Older versions are never rebuilt or replaced.
- `build/` holds the scripts that export a version's browser build from the
  game's (private) source at release time.

Credits: reload sounds from "Gun reload sounds" by SpringySpringo (CC0,
OpenGameArt). Everything else is original.
