#!/bin/sh
set -eu
PB=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
ROOT=$(CDPATH= cd -- "$PB/../.." && pwd)
VERSION=$(cat "$PB/VERSION")
OUT="$PB/linux_ubuntu/install_fonts_standalone"
PKGROOT=$(mktemp -d)
trap 'rm -rf "$PKGROOT"' EXIT HUP INT TERM
mkdir -p "$PKGROOT/DEBIAN" "$PKGROOT/usr/share/grimchain-fonts/font-bundle"
cp -a "$ROOT"/fonts/runtime/. "$PKGROOT/usr/share/grimchain-fonts/font-bundle/"
find "$PKGROOT/usr/share/grimchain-fonts/font-bundle" -maxdepth 1 -type f -exec chmod 644 {} +
cat > "$PKGROOT/DEBIAN/control" <<CONTROL
Package: grimchain-fonts
Version: ${VERSION}-1
Section: fonts
Priority: optional
Architecture: all
Depends: fontconfig
Maintainer: Magus Jamye Reficul Ahnend <witchofalways@gmail.com>
Description: GrimChain standalone font corpus
 The preserved 38-font GrimChain runtime corpus, independently installable from TardiSHA.
CONTROL
cat > "$PKGROOT/DEBIAN/postinst" <<'POST'
#!/bin/sh
set -e
install -d -m 755 /usr/local/share/fonts/tardisha
cp -a /usr/share/grimchain-fonts/font-bundle/. /usr/local/share/fonts/tardisha/
find /usr/local/share/fonts/tardisha -maxdepth 1 -type f -exec chmod 644 {} +
fc-cache -f -v >/dev/null 2>&1 || true
exit 0
POST
chmod 755 "$PKGROOT/DEBIAN/postinst"
cat > "$PKGROOT/DEBIAN/postrm" <<'POST'
#!/bin/sh
set -e
fc-cache -f -v >/dev/null 2>&1 || true
exit 0
POST
chmod 755 "$PKGROOT/DEBIAN/postrm"
OUTFILE="$OUT/grimchain-fonts_${VERSION}-1_all.deb"
rm -f "$OUTFILE"
dpkg-deb --root-owner-group --build "$PKGROOT" "$OUTFILE"
printf '%s
' "$OUTFILE"
