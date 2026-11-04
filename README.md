# Gnarcom: play in your browser

**Play: https://drewmycroft-dev.github.io/gnarcom-play/**

Gnarcom is an original third-person tactical shooter: 4v4 team deathmatch,
Navy SEALs vs insurgents, on a nighttime harbor. Made with Godot 4.

Controls: WASD move · mouse aim · left click fire · right click aim down
sights · Shift sprint · C crouch · Space jump · R reload · 1/2 or mouse wheel
switch weapons · Q swap shoulder · Tab scoreboard · Esc menu. Click the game
to start (the browser needs a click to lock the mouse).

Runs in current Chrome, Edge and Firefox (WebGL 2). A computer with a
graphics card is recommended.

## About this repository

This repository only publishes the game. It contains no game source code:
the [workflow](.github/workflows/publish.yml) builds the web version from a
private repository when started by hand and uploads just the exported files
to GitHub Pages.

Credits: reload sounds from "Gun reload sounds" by SpringySpringo (CC0,
OpenGameArt). Everything else is generated in code.
