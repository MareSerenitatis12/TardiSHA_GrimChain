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
cp "$ROOT"/fonts/runtime/*.ttf "$BUILD/fonts/"
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
  SetOutPath "$FONTS"
  File /oname=GrimChain-NotoMusic-Regular.ttf "fonts\NotoMusic-Regular.ttf"
  File /oname=GrimChain-NotoSans-Regular.ttf "fonts\NotoSans-Regular.ttf"
  File /oname=GrimChain-NotoSansBalinese-Regular.ttf "fonts\NotoSansBalinese-Regular.ttf"
  File /oname=GrimChain-NotoSansBrahmi-Regular.ttf "fonts\NotoSansBrahmi-Regular.ttf"
  File /oname=GrimChain-NotoSansCuneiform-Regular.ttf "fonts\NotoSansCuneiform-Regular.ttf"
  File /oname=GrimChain-NotoSansCypriot-Regular.ttf "fonts\NotoSansCypriot-Regular.ttf"
  File /oname=GrimChain-NotoSansElbasan-Regular.ttf "fonts\NotoSansElbasan-Regular.ttf"
  File /oname=GrimChain-NotoSansEthiopic-Regular.ttf "fonts\NotoSansEthiopic-Regular.ttf"
  File /oname=GrimChain-NotoSansLydian-Regular.ttf "fonts\NotoSansLydian-Regular.ttf"
  File /oname=GrimChain-NotoSansMath-Regular.ttf "fonts\NotoSansMath-Regular.ttf"
  File /oname=GrimChain-NotoSansNKo-Regular.ttf "fonts\NotoSansNKo-Regular.ttf"
  File /oname=GrimChain-NotoSansRunic-Regular.ttf "fonts\NotoSansRunic-Regular.ttf"
  File /oname=GrimChain-NotoSansSundanese-VariableFont_wght.ttf "fonts\NotoSansSundanese-VariableFont_wght.ttf"
  File /oname=GrimChain-NotoSansSylotiNagri-Regular.ttf "fonts\NotoSansSylotiNagri-Regular.ttf"
  File /oname=GrimChain-NotoSansSymbols-Regular.ttf "fonts\NotoSansSymbols-Regular.ttf"
  File /oname=GrimChain-NotoSansSymbols2-Regular.ttf "fonts\NotoSansSymbols2-Regular.ttf"
  File /oname=GrimChain-NotoSansThaana-Regular.ttf "fonts\NotoSansThaana-Regular.ttf"
  File /oname=GrimChain-NotoSansTifinagh-Regular.ttf "fonts\NotoSansTifinagh-Regular.ttf"
  File /oname=GrimChain-NotoSerifTibetan-Regular.ttf "fonts\NotoSerifTibetan-Regular.ttf"
  SetRegView 64
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoMusic-Regular.ttf (TrueType)" "GrimChain-NotoMusic-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoMusic-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSans-Regular.ttf (TrueType)" "GrimChain-NotoSans-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSans-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansBalinese-Regular.ttf (TrueType)" "GrimChain-NotoSansBalinese-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansBalinese-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansBrahmi-Regular.ttf (TrueType)" "GrimChain-NotoSansBrahmi-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansBrahmi-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansCuneiform-Regular.ttf (TrueType)" "GrimChain-NotoSansCuneiform-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansCuneiform-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansCypriot-Regular.ttf (TrueType)" "GrimChain-NotoSansCypriot-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansCypriot-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansElbasan-Regular.ttf (TrueType)" "GrimChain-NotoSansElbasan-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansElbasan-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansEthiopic-Regular.ttf (TrueType)" "GrimChain-NotoSansEthiopic-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansEthiopic-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansLydian-Regular.ttf (TrueType)" "GrimChain-NotoSansLydian-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansLydian-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansMath-Regular.ttf (TrueType)" "GrimChain-NotoSansMath-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansMath-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansNKo-Regular.ttf (TrueType)" "GrimChain-NotoSansNKo-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansNKo-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansRunic-Regular.ttf (TrueType)" "GrimChain-NotoSansRunic-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansRunic-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansSundanese-VariableFont_wght.ttf (TrueType)" "GrimChain-NotoSansSundanese-VariableFont_wght.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansSundanese-VariableFont_wght.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansSylotiNagri-Regular.ttf (TrueType)" "GrimChain-NotoSansSylotiNagri-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansSylotiNagri-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansSymbols-Regular.ttf (TrueType)" "GrimChain-NotoSansSymbols-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansSymbols-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansSymbols2-Regular.ttf (TrueType)" "GrimChain-NotoSansSymbols2-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansSymbols2-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansThaana-Regular.ttf (TrueType)" "GrimChain-NotoSansThaana-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansThaana-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansTifinagh-Regular.ttf (TrueType)" "GrimChain-NotoSansTifinagh-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSansTifinagh-Regular.ttf") i .r0'
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSerifTibetan-Regular.ttf (TrueType)" "GrimChain-NotoSerifTibetan-Regular.ttf"
  System::Call 'gdi32::AddFontResourceW(w "$FONTS\GrimChain-NotoSerifTibetan-Regular.ttf") i .r0'
  SendMessage ${HWND_BROADCAST} ${WM_FONTCHANGE} 0 0 /TIMEOUT=5000
  SetOutPath "$INSTDIR"
  WriteUninstaller "$INSTDIR\Uninstall-GrimChain-Fonts.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GrimChain Fonts" "DisplayName" "GrimChain Fonts @VERSION@"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GrimChain Fonts" "DisplayVersion" "@VERSION@"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GrimChain Fonts" "UninstallString" '"$INSTDIR\Uninstall-GrimChain-Fonts.exe"'
SectionEnd
Section "Uninstall"
  SetShellVarContext all
  SetRegView 64
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoMusic-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoMusic-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSans-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSans-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansBalinese-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansBalinese-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansBrahmi-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansBrahmi-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansCuneiform-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansCuneiform-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansCypriot-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansCypriot-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansElbasan-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansElbasan-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansEthiopic-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansEthiopic-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansLydian-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansLydian-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansMath-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansMath-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansNKo-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansNKo-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansRunic-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansRunic-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansSundanese-VariableFont_wght.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansSundanese-VariableFont_wght.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansSylotiNagri-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansSylotiNagri-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansSymbols-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansSymbols-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansSymbols2-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansSymbols2-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansThaana-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansThaana-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSansTifinagh-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSansTifinagh-Regular.ttf (TrueType)"
  System::Call 'gdi32::RemoveFontResourceW(w "$FONTS\GrimChain-NotoSerifTibetan-Regular.ttf") i .r0'
  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" "GrimChain NotoSerifTibetan-Regular.ttf (TrueType)"
  Delete "$FONTS\GrimChain-NotoMusic-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSans-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansBalinese-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansBrahmi-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansCuneiform-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansCypriot-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansElbasan-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansEthiopic-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansLydian-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansMath-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansNKo-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansRunic-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansSundanese-VariableFont_wght.ttf"
  Delete "$FONTS\GrimChain-NotoSansSylotiNagri-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansSymbols-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansSymbols2-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansThaana-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSansTifinagh-Regular.ttf"
  Delete "$FONTS\GrimChain-NotoSerifTibetan-Regular.ttf"
  SendMessage ${HWND_BROADCAST} ${WM_FONTCHANGE} 0 0 /TIMEOUT=5000
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
printf '%s
' "$OUTFILE"
