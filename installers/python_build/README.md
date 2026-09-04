# TardiSHA Installers

Final preserved installer line: **26.18.47.34**

Installer contact: **witchofalways@gmail.com**

All platform builds use the finalized runtime in `TardiSHA/ChatGPT_Plans_and_Scripts/TardiSHA/`. The preservation notebook remains the authority and installer builds do not modify it.

## Platform artifacts

- `linux_ubuntu/dist/` — Python wheel/source release and direct Ubuntu/Debian `.deb`
- `linux_ubuntu/launchpad/` — Launchpad source-package set
- `windows/26.18.47.34/` — Windows x64 NSIS installer
- `mac/26.18.47.34/` — macOS universal installer package

## Ubuntu

Install the direct package:

```sh
sudo apt install ./linux_ubuntu/dist/tardisha_26.18.47.34-1_amd64.deb
```

Remove it:

```sh
sudo apt remove tardisha
```

The Ubuntu package owns one physical TardiSHA font corpus at `/usr/share/local/fonts/tardisha/` and refreshes the fontconfig cache after installation. `/usr/local/share/fonts/tardisha` is only a compatibility symlink to that one corpus so the preserved runtime requires no source change.

On removal the package removes the TardiSHA font directory and compatibility symlink, then refreshes the fontconfig cache before finishing.

## Preservation contract

The installer line preserves the exact TardiSHA runtime and the exact 19-font runtime corpus. Windows retains its Windows Fonts behavior. macOS retains its `/Library/Fonts/` behavior.

The documentation sanctuary is user-owned and intentionally deletable without affecting the GrimChain runtime:

- Linux/macOS: `~/.grimchain/`
- Windows: `%USERPROFILE%\.grimchain\`

Top-level release documents remain top-level in the sanctuary. The original `docs/` corpus remains a distinct `docs/` directory beneath it; the two bodies are not flattened into one another.

No installer build writes Python bytecode into the preserved source tree. Local build logs, checksum witnesses, validation records, and diff reports are kept under `.build_records/` rather than mixed with release artifacts.
