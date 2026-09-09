# GrimChain Fonts — Ubuntu/Debian

Standalone 19-font corpus for GrimChain/TardiSHA 26.18.47.34.

Install:

```sh
sudo apt install ./grimchain-fonts_26.18.47.34-1_all.deb
```

The 19 font files are stored only in `/usr/share/local/fonts/grimchain/`. A discovery symlink at `/usr/local/share/fonts/grimchain` exposes that one physical corpus to Ubuntu fontconfig, then the cache is refreshed.

Uninstall:

```sh
sudo apt remove grimchain-fonts
```

Removal deletes `/usr/share/local/fonts/grimchain/`, removes the discovery symlink, and refreshes the fontconfig cache. TardiSHA is not installed or removed by this package.
