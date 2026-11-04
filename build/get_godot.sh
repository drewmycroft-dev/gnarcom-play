#!/usr/bin/env bash
# Downloads Godot 4.7.2 (Linux) and its export templates from the official
# Godot GitHub release into <dir>, verifies them against pinned SHA-512
# hashes, and keeps only the editor binary and the web template:
#   <dir>/Godot_v4.7.2-stable_linux.x86_64
#   <dir>/templates/web_nothreads_release.zip, version.txt
set -euo pipefail
dir="$1"
mkdir -p "$dir" && cd "$dir"
RELEASE="https://github.com/godotengine/godot/releases/download/4.7.2-stable"
ZIP="Godot_v4.7.2-stable_linux.x86_64.zip"
TPZ="Godot_v4.7.2-stable_export_templates.tpz"
# From the release's SHA512-SUMS.txt (pinned, so a tampered download fails).
ZIP_SHA512="9aa00f7a605200940bce3027a567b782f49bd8e940dd06ae9e987bd65aee1b1467edd56ed84fcdcbdd44354bf613bdbb4e5d2913e925850368e150c59ed54c65"
TPZ_SHA512="ca4d71c4d7b81dfc15d1a98baa07534aa95b03fdda78a0075b06672e1648d2e5f40980c9adc28d23e1b92e732ee7bf3461997aa804af74ec2fcd7a93ccb84079"
curl -fsSL --retry 3 -o "$ZIP" "$RELEASE/$ZIP"
echo "$ZIP_SHA512  $ZIP" | sha512sum -c --quiet
curl -fsSL --retry 3 -o "$TPZ" "$RELEASE/$TPZ"
echo "$TPZ_SHA512  $TPZ" | sha512sum -c --quiet
unzip -oq "$ZIP"
unzip -oq -j "$TPZ" templates/web_nothreads_release.zip templates/version.txt -d templates
rm -f "$ZIP" "$TPZ"
echo "godot ready in $dir"
