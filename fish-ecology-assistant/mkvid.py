import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import numpy as np
from PIL import Image
import os
from moviepy import VideoClip

IMG_PATH = r"D:\Reasonix\docs\THREE_PROJECTS_EVOLUTION_warm.png"
OUT_PATH = r"D:\Reasonix\docs\THREE_PROJECTS_EVOLUTION_视频_warm_nomusic.mp4"
W, H, FPS, DUR = 1080, 1920, 60, 120

print("[1] Loading warm image...")
img = Image.open(IMG_PATH)
ow, oh = img.size
print(f"    {ow}x{oh} -> {W}x{int(oh*W/ow)}")

nh = int(oh * W / ow)
img = img.resize((W, nh), Image.LANCZOS)
arr = np.array(img)
scroll_max = nh - H
speed = scroll_max / DUR
print(f"    scroll {scroll_max}px @ {speed:.1f} px/s ({DUR}s)")

print("[2] Generating frames @ 60fps...")
def frame(t):
    y = int(t * speed)
    y = max(0, min(y, scroll_max))
    return arr[y:y+H, 0:W, :3]

clip = VideoClip(frame, duration=DUR).with_fps(FPS)

print(f"[3] Encoding -> {OUT_PATH}")
clip.write_videofile(
    OUT_PATH, codec="libx264", fps=FPS, preset="medium",
    bitrate="8000k", threads=4
)
mb = os.path.getsize(OUT_PATH) / (1024*1024)
print(f"\nDone! {mb:.1f} MB | {W}x{H} | {FPS}fps | {DUR}s | Theme: Warm")
