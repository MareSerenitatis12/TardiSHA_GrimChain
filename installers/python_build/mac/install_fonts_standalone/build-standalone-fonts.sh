#!/usr/bin/env bash
set -euo pipefail
PB="$(cd "$(dirname "$0")/../.." && pwd)"
ROOT="$(cd "$PB/../.." && pwd)"
VERSION="$(cat "$PB/VERSION")"
OUT="$PB/mac/install_fonts_standalone"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PKGROOT="$WORK/root"
META="$WORK/meta"
mkdir -p "$PKGROOT/Library/Fonts" "$META"
for font in "$ROOT"/fonts/runtime/*.ttf; do
  install -m 644 "$font" "$PKGROOT/Library/Fonts/GrimChain-$(basename "$font")"
done
(cd "$PKGROOT" && find . -print | LC_ALL=C sort | cpio -o -H odc 2>/dev/null | gzip -9 > "$META/Payload")
mkbom -u 0 -g 80 "$PKGROOT" "$META/Bom"
FILES=$(find "$PKGROOT" -type f | wc -l)
KB=$(du -sk "$PKGROOT" | awk '{print $1}')
cat > "$META/PackageInfo" <<PKG
<?xml version="1.0" encoding="utf-8"?>
<pkg-info format-version="2" identifier="org.grimchain.fonts" version="$VERSION" install-location="/" auth="root">
  <payload installKBytes="$KB" numberOfFiles="$FILES"/>
</pkg-info>
PKG
OUTFILE="$OUT/GrimChain-Fonts-$VERSION-macOS.pkg"
rm -f "$OUTFILE"
(cd "$META" && bsdtar --format xar -cf "$OUTFILE" PackageInfo Bom Payload)
printf '%s
' "$OUTFILE"
