# tint2_mark

Put a colored dot on a terminal's panel icon (tint2 or any EWMH panel) to tell terminal windows apart.

Overlays a dot on the GNOME Terminal icon and sets it as the window's `_NET_WM_ICON`.

## Usage

    tint2_mark.py [color]    # default: limegreen
    tint2_mark.py reset      # restore the original icon

## Requirements

- Python 3 with Pillow
- ImageMagick (`convert`)
- `xdotool` (used when `WINDOWID` is not set)
- libX11, and the GNOME Terminal icon at `/usr/share/icons/hicolor/scalable/apps/org.gnome.Terminal.svg`
