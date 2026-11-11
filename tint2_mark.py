#!/usr/bin/env python3
# usage: tint2_mark.py [color|reset]   -- puts a colored dot on this terminal's panel icon
import sys, os, subprocess
from PIL import Image, ImageDraw
col = sys.argv[1] if len(sys.argv) > 1 else "limegreen"
wid = os.environ.get("WINDOWID") or subprocess.check_output(["xdotool","getactivewindow"]).decode().strip()
reset = col == "reset"
svg = "/usr/share/icons/hicolor/scalable/apps/org.gnome.Terminal.svg"
png = "/tmp/mark_base.png"
if not reset: subprocess.check_call(["convert","-background","none","-density","600",svg,"-resize","64x64",png])
if not reset:
    im = Image.open(png).convert("RGBA").resize((64,64))
    d = ImageDraw.Draw(im)
    d.ellipse((30,30,62,62), fill=col, outline="black", width=3)
    vals = [64,64] + [(a<<24)|(r<<16)|(g<<8)|b for r,g,b,a in im.getdata()]
import ctypes
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
arr = (ctypes.c_ulong * len(vals))(*vals)   # format 32 => array of C long
x.XChangeProperty(dpy, int(wid, 0), x.XInternAtom(dpy, b"_NET_WM_ICON", 0),
                  x.XInternAtom(dpy, b"CARDINAL", 0), 32, 0, arr, len(vals))
x.XFlush(dpy)
