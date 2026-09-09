#!/bin/sh
set -eu
PB=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
ROOT=$(CDPATH= cd -- "$PB/../.." && pwd)
VERSION=$(cat "$PB/VERSION")
OUT="$PB/linux_ubuntu/install_fonts_standalone"
PKGROOT=$(mktemp -d)
trap 'rm -rf "$PKGROOT"' EXIT HUP INT TERM
mkdir -p "$PKGROOT/DEBIAN" "$PKGROOT/usr/share/local/fonts/grimchain"
cp -a "$ROOT"/fonts/runtime/*.ttf "$PKGROOT/usr/share/local/fonts/grimchain/"
chmod 644 "$PKGROOT/usr/share/local/fonts/grimchain/"*.ttf
cat > "$PKGROOT/DEBIAN/control" <<CONTROL
Package: grimchain-fonts
Version: ${VERSION}-1
Section: fonts
Priority: optional
Architecture: all
Depends: fontconfig
Maintainer: Magus Jamye Reficul Ahnend <witchofalways@gmail.com>
Description: GrimChain standalone font corpus
 The preserved 19-font GrimChain runtime corpus, independently installable from TardiSHA.
CONTROL
cat > "$PKGROOT/DEBIAN/postinst" <<'POST'
#!/bin/sh
set -e
rm -rf /usr/local/share/fonts/grimchain
install -d -m 755 /usr/local/share/fonts
ln -s /usr/share/local/fonts/grimchain /usr/local/share/fonts/grimchain
fc-cache -f >/dev/null 2>&1 || true
exit 0
POST
chmod 755 "$PKGROOT/DEBIAN/postinst"
cat > "$PKGROOT/DEBIAN/postrm" <<'POST'
#!/bin/sh
set -e
case "${1:-}" in
  remove|purge)
    rm -rf /usr/share/local/fonts/grimchain
    rm -f /usr/local/share/fonts/grimchain
    ;;
esac
fc-cache -f >/dev/null 2>&1 || true
exit 0
POST
chmod 755 "$PKGROOT/DEBIAN/postrm"
OUTFILE="$OUT/grimchain-fonts_${VERSION}-1_all.deb"
rm -f "$OUTFILE"
dpkg-deb --root-owner-group --build "$PKGROOT" "$OUTFILE"
printf '%s
' "$OUTFILE"
