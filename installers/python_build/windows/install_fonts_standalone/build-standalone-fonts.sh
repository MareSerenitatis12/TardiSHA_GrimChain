#!/usr/bin/env bash
set -euo pipefail
PB="$(cd "$(dirname "$0")/../.." && pwd)"
ROOT="$(cd "$PB/../.." && pwd)"
VERSION="$(cat "$PB/VERSION")"
OUT="$PB/windows/install_fonts_standalone"
SIGNDIR="/app/data/OSSLSIGNCODE"
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"' EXIT
mkdir -p "$BUILD/fonts"
cp -a "$ROOT"/fonts/runtime/. "$BUILD/fonts/"
NSI="$BUILD/GrimChain-Fonts.nsi"
cat > "$NSI" <<'NSI'
Unicode true
RequestExecutionLevel admin
Name "GrimChain Fonts @VERSION@"
VIProductVersion "@VERSION@"
VIAddVersionKey /LANG=1033 "ProductName" "GrimChain Fonts"
VIAddVersionKey /LANG=1033 "CompanyName" "TardiSHA"
VIAddVersionKey /LANG=1033 "FileDescription" "Standalone GrimChain font corpus"
VIAddVersionKey /LANG=1033 "FileVersion" "@VERSION@"
VIAddVersionKey /LANG=1033 "ProductVersion" "@VERSION@"
OutFile "@OUTFILE@"
InstallDir "$PROGRAMFILES64\GrimChain Fonts"
SetCompressor /SOLID lzma
!include "MUI2.nsh"
!include "WinMessages.nsh"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
Section "GrimChain Fonts" SEC_MAIN
  SetShellVarContext all
  InitPluginsDir
  SetOutPath "$PLUGINSDIR\fonts"
  File /r "fonts\*.*"
  nsExec::ExecToLog 'powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "$fonts=(New-Object -ComObject Shell.Application).Namespace(0x14); Get-ChildItem -LiteralPath ''$PLUGINSDIR\fonts'' -File | ForEach-Object { $fonts.CopyHere($_.FullName, 20) }"'
  SendMessage ${HWND_BROADCAST} ${WM_FONTCHANGE} 0 0 /TIMEOUT=5000
  SetOutPath "$INSTDIR"
  WriteUninstaller "$INSTDIR\Uninstall-GrimChain-Fonts.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GrimChain Fonts" "DisplayName" "GrimChain Fonts @VERSION@"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GrimChain Fonts" "DisplayVersion" "@VERSION@"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GrimChain Fonts" "UninstallString" '"$INSTDIR\Uninstall-GrimChain-Fonts.exe"'
SectionEnd
Section "Uninstall"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GrimChain Fonts"
  Delete "$INSTDIR\Uninstall-GrimChain-Fonts.exe"
  RMDir "$INSTDIR"
SectionEnd
NSI
OUTFILE="$OUT/GrimChain-Fonts-$VERSION-Windows-Setup.exe"
python3 - "$NSI" "$VERSION" "$OUTFILE" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); version=sys.argv[2]; outfile=sys.argv[3].replace('\\','/')
s=p.read_text(encoding='utf-8').replace('@VERSION@',version).replace('@OUTFILE@',outfile)
p.write_text(s,encoding='utf-8')
PY
rm -f "$OUTFILE" "$OUT/.GrimChain-Fonts-$VERSION-Windows-Setup.signed.exe"
(cd "$BUILD" && makensis "$(basename "$NSI")" >/dev/null)
SIGNED="$OUT/.GrimChain-Fonts-$VERSION-Windows-Setup.signed.exe"
osslsigncode sign -h sha256 -certs "$SIGNDIR/codesign.crt" -key "$SIGNDIR/codesign.key" -n "GrimChain Fonts $VERSION" -in "$OUTFILE" -out "$SIGNED" >/dev/null
mv -f "$SIGNED" "$OUTFILE"
printf '%s\n' "$OUTFILE"
