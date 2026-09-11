# GrimChain Fonts — Ubuntu/Debian

Standalone 38-font corpus for GrimChain/TardiSHA 26.18.47.34.

Install:

```sh
sudo apt install ./grimchain-fonts_26.18.47.34-1_all.deb
```

The 38 font files are installed directly in `/usr/local/share/fonts/tardisha/`, where Ubuntu fontconfig discovers them directly. The font cache is refreshed with `fc-cache -f -v` after installation, and uninstall leaves this directory and its fonts in place.

Uninstall:

```sh
sudo apt remove grimchain-fonts
```

Removal leaves `/usr/local/share/fonts/tardisha/` and all installed fonts in place, then refreshes the fontconfig cache. TardiSHA is not installed or removed by this package.
