#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
VERSION=$(cat "$ROOT/VERSION")
RELEASE=1
ARCH=$(dpkg --print-architecture)
WHEEL=$(find "$ROOT/dist" -maxdepth 1 -type f -name "tardisha-${VERSION}-*.whl" | sort | head -n 1)
if [ -z "$WHEEL" ]; then
  echo "No platform wheel found for TardiSHA ${VERSION}" >&2
  exit 1
fi
WHEEL_NAME=$(basename "$WHEEL")
PKGROOT=$(mktemp -d)
trap 'rm -rf "$PKGROOT"' EXIT HUP INT TERM
chmod 755 "$PKGROOT"

mkdir -p \
  "$PKGROOT/DEBIAN" \
  "$PKGROOT/usr/bin" \
  "$PKGROOT/usr/lib/tardisha" \
  "$PKGROOT/usr/share/tardisha/wheels" \
  "$PKGROOT/usr/share/doc/tardisha"

cat > "$PKGROOT/DEBIAN/control" <<EOF
Package: tardisha
Version: ${VERSION}-${RELEASE}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.12), python3 (<< 3.13), python3-venv
Maintainer: Magus Jamye Reficul Ahnend
Description: TardiSHA v23 Grimchain and Synodic Magicae Domus runtime
 Installs TardiSHA in the system-owned private virtual environment
 /opt/tardisha/grim-env and exposes grimchain, tardisha, and TardiSHA.
EOF

cat > "$PKGROOT/DEBIAN/postinst" <<EOF
#!/bin/sh
set -e

VENV=/opt/tardisha/grim-env
WHEEL=/usr/share/tardisha/wheels/${WHEEL_NAME}

case "\${1:-configure}" in
  configure)
    if [ ! -f "\$WHEEL" ]; then
      echo "TardiSHA wheel is missing: \$WHEEL" >&2
      exit 1
    fi
    install -d -m 755 /opt/tardisha
    rm -rf "\$VENV"
    python3 -m venv "\$VENV"
    "\$VENV/bin/python" -m pip install --no-index --no-deps --disable-pip-version-check "\$WHEEL"
    chmod -R a+rX,go-w "\$VENV"
    ;;
esac
exit 0
EOF

cat > "$PKGROOT/DEBIAN/prerm" <<'EOF'
#!/bin/sh
set -e
case "${1:-remove}" in
  remove|deconfigure|upgrade|failed-upgrade)
    rm -rf /opt/tardisha/grim-env
    ;;
esac
exit 0
EOF

cat > "$PKGROOT/DEBIAN/postrm" <<'EOF'
#!/bin/sh
set -e
case "${1:-remove}" in
  remove|purge)
    rmdir /opt/tardisha 2>/dev/null || true
    ;;
esac
exit 0
EOF

install -m 755 "$ROOT/packaging/debian/launcher" "$PKGROOT/usr/lib/tardisha/launcher"
ln -s /usr/lib/tardisha/launcher "$PKGROOT/usr/bin/grimchain"
ln -s /usr/lib/tardisha/launcher "$PKGROOT/usr/bin/tardisha"
ln -s /usr/lib/tardisha/launcher "$PKGROOT/usr/bin/TardiSHA"

install -m 644 "$ROOT/packaging/debian/default-config.toml" "$PKGROOT/usr/share/tardisha/default-config.toml"
install -m 644 "$ROOT/packaging/debian/QUICKSTART.txt" "$PKGROOT/usr/share/tardisha/QUICKSTART.txt"
install -m 644 "$WHEEL" "$PKGROOT/usr/share/tardisha/wheels/"
install -m 644 "$ROOT/LICENSE" "$PKGROOT/usr/share/doc/tardisha/LICENSE"
install -m 644 "$ROOT/COPYRIGHT" "$PKGROOT/usr/share/doc/tardisha/COPYRIGHT"
install -m 644 "$ROOT/VERSION" "$PKGROOT/usr/share/doc/tardisha/VERSION"
install -m 644 "$ROOT/COMMANDS.md" "$PKGROOT/usr/share/doc/tardisha/COMMANDS.md"
install -m 644 "$ROOT/DICTIONARY.md" "$PKGROOT/usr/share/doc/tardisha/DICTIONARY.md"
install -m 644 "$ROOT/README.md" "$PKGROOT/usr/share/doc/tardisha/README.md"

chmod 755 "$PKGROOT/DEBIAN/postinst" "$PKGROOT/DEBIAN/prerm" "$PKGROOT/DEBIAN/postrm"
mkdir -p "$ROOT/dist"
rm -f "$ROOT/dist/tardisha_${VERSION}-${RELEASE}_${ARCH}.deb"
dpkg-deb --root-owner-group --build "$PKGROOT" "$ROOT/dist/tardisha_${VERSION}-${RELEASE}_${ARCH}.deb"
