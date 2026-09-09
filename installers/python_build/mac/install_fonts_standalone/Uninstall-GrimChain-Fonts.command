#!/bin/sh
set -e
if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo: sudo ./Uninstall-GrimChain-Fonts.command" >&2
  exit 1
fi
rm -f /Library/Fonts/GrimChain-*.ttf
pkgutil --forget org.grimchain.fonts >/dev/null 2>&1 || true
killall -u "${SUDO_USER:-$(id -un)}" fontd >/dev/null 2>&1 || true
exit 0
