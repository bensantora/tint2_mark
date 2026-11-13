#!/usr/bin/env python3
# usage: tint2_mark.py [color|reset]   -- puts a colored dot on this terminal's panel icon
# The finished icon for each color is cached in ~/.cache/tint2_mark/, so only the first use is slow.
import sys, os, subprocess, ctypes
col = sys.argv[1] if len(sys.argv) > 1 else "limegreen"
wid = os.environ.get("WINDOWID") or subprocess.check_output(["xdotool","getactivewindow"]).decode().strip()
reset = col == "reset"
svg = "/usr/share/icons/hicolor/scalable/apps/org.gnome.Terminal.svg"
cache_dir = os.path.expanduser("~/.cache/tint2_mark")
cache = os.path.join(cache_dir, "".join(ch for ch in col if ch.isalnum() or ch in "#-_") + ".bin")

def build_icon():
    """Draw the terminal icon with a dot and return it as _NET_WM_ICON data (width, height, pixels)."""
    from PIL import Image, ImageDraw
    png = os.path.join(cache_dir, "base.png")
    subprocess.check_call(["convert","-background","none","-density","600",svg,"-resize","64x64",png])
    im = Image.open(png).convert("RGBA").resize((64,64))
    d = ImageDraw.Draw(im)
    d.ellipse((30,30,62,62), fill=col, outline="black", width=3)
    vals = [64,64] + [(a<<24)|(r<<16)|(g<<8)|b for r,g,b,a in im.getdata()]
    return (ctypes.c_ulong * len(vals))(*vals)   # format 32 => array of C long

if not reset:
    if os.path.exists(cache) and os.path.getmtime(cache) >= os.path.getmtime(svg):
        data = open(cache, "rb").read()
        arr = (ctypes.c_ulong * (len(data) // ctypes.sizeof(ctypes.c_ulong))).from_buffer_copy(data)
    else:
        os.makedirs(cache_dir, exist_ok=True)
        arr = build_icon()
        with open(cache + ".tmp", "wb") as f: f.write(bytes(arr))
        os.replace(cache + ".tmp", cache)

x = ctypes.CDLL("libX11.so.6")
x.XOpenDisplay.restype = ctypes.c_void_p
x.XInternAtom.restype = ctypes.c_ulong
x.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
x.XChangeProperty.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong,
                              ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
dpy = x.XOpenDisplay(None)
if reset:
    x.XDeleteProperty.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong]
    x.XDeleteProperty(dpy, int(wid, 0), x.XInternAtom(dpy, b"_NET_WM_ICON", 0))
    x.XFlush(dpy); sys.exit(0)
x.XChangeProperty(dpy, int(wid, 0), x.XInternAtom(dpy, b"_NET_WM_ICON", 0),
                  x.XInternAtom(dpy, b"CARDINAL", 0), 32, 0, arr, len(arr))
x.XFlush(dpy)
