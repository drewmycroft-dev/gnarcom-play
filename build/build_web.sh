#!/usr/bin/env bash
# Builds the Gnarcom browser version from a checkout of the (private) Gnarcom
# source and writes ONLY the web build files to an output folder.
#
#   build/build_web.sh <source_dir> <out_dir>
#
# Gets Godot 4.7.2 with build/get_godot.sh (official release, pinned SHA-512)
# unless GODOT_BIN and GODOT_TEMPLATES (a folder holding
# web_nothreads_release.zip and version.txt) are set. Godot's own log is kept
# in <out_dir>/../godot_*.log (not published) so the public CI log never lists
# source files; only error lines are shown.
set -euo pipefail

GODOT_VERSION="4.7.2"
# The only files a Godot web export should produce.
ALLOWED="index.html index.js index.wasm index.pck index.png index.icon.png index.apple-touch-icon.png index.audio.worklet.js index.audio.position.worklet.js"

src="$(cd "$1" && pwd)"
mkdir -p "$2"
out="$(cd "$2" && pwd)"
work="${WORK_DIR:-$(dirname "$out")/godot-work}"
mkdir -p "$work"

if [ -z "${GODOT_BIN:-}" ]; then
	"$(dirname "$0")/get_godot.sh" "$work"
	GODOT_BIN="$work/Godot_v${GODOT_VERSION}-stable_linux.x86_64"
	GODOT_TEMPLATES="$work/templates"
fi

# Lay Godot out the way the project's tools/godot.sh expects (self-contained).
tools="$src/tools"
mkdir -p "$tools/editor_data/export_templates/${GODOT_VERSION}.stable"
cp "$GODOT_BIN" "$tools/Godot_v${GODOT_VERSION}-stable_linux.x86_64"
chmod +x "$tools/Godot_v${GODOT_VERSION}-stable_linux.x86_64"
cp "$GODOT_TEMPLATES/web_nothreads_release.zip" "$GODOT_TEMPLATES/version.txt" \
	"$tools/editor_data/export_templates/${GODOT_VERSION}.stable/"
touch "$tools/._sc_" "$tools/.gdignore"

grep -q '^name="Web"' "$src/export_presets.cfg" || {
	echo "error: the source has no \"Web\" export preset (build the branch with the web changes)" >&2
	exit 1
}

cd "$src"
G=./tools/godot.sh
logs="$(dirname "$out")"
$G --headless --path . --import > "$logs/godot_import.log" 2>&1 || true
rm -rf "$out"/*
$G --headless --path . --export-release "Web" "$out/index.html" > "$logs/godot_export.log" 2>&1 || true
grep -E "^(ERROR|SCRIPT ERROR)" "$logs/godot_export.log" | head -20 || true

# Publish nothing but the expected web files.
for f in "$out"/* "$out"/.[!.]*; do
	[ -e "$f" ] || continue
	name="$(basename "$f")"
	case " $ALLOWED " in
		*" $name "*) ;;
		*) echo "error: unexpected file in the web build: $name" >&2; exit 1 ;;
	esac
done
for f in index.html index.wasm index.pck index.js; do
	[ -s "$out/$f" ] || { echo "error: export failed (missing $f)" >&2; exit 1; }
done
pck=$(stat -c %s "$out/index.pck")
[ "$pck" -lt 20000000 ] || { echo "error: index.pck is $pck bytes; something extra got packed" >&2; exit 1; }
echo "web build ok:"
ls -l "$out" | awk 'NR>1 {printf "  %-32s %10s bytes\n", $9, $5}'
