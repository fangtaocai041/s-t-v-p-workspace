"""
make_video.py — 将长图渲染为纵向滚屏视频 + 未闻花名BGM
输出: MP4 H.264, 1080×1920, 30fps, 适合抖音/视频号
"""
from moviepy import VideoClip, ImageClip, AudioFileClip, CompositeAudioClip
import numpy as np
from PIL import Image
import os

# === 配置 ===
IMG_PATH = r"D:\Reasonix\docs\THREE_PROJECTS_EVOLUTION_dark.png"
AUDIO_PATH = r"D:\Reasonix\docs\secret_base.mp3"
OUT_PATH = r"D:\Reasonix\docs\THREE_PROJECTS_EVOLUTION_视频.mp4"

VIEWPORT_W = 1080
VIEWPORT_H = 1920
FPS = 30

# === 加载图片 ===
print("📷 加载长图...")
pil_img = Image.open(IMG_PATH)
orig_w, orig_h = pil_img.size
print(f"   原始分辨率: {orig_w}×{orig_h}")

# 缩放到 1080 宽度
new_w = VIEWPORT_W
new_h = int(orig_h * new_w / orig_w)
pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)
print(f"   缩放至: {new_w}×{new_h}")

img_array = np.array(pil_img)
scroll_max = new_h - VIEWPORT_H
print(f"   可滚动范围: 0 → {scroll_max} px")

# === 加载音频 ===
print("🎵 加载BGM: secret_base.mp3")
audio = AudioFileClip(AUDIO_PATH)
audio_duration = audio.duration
print(f"   音频时长: {audio_duration:.1f}s ({audio_duration/60:.1f} min)")

# === 滚屏速度：刚好在音乐播完时滚到底 ===
# 如果想音乐播完时刚好滚到底，用这个:
# scroll_speed = scroll_max / audio_duration   # px/sec
# 但音乐 369s 太长，滚 ~30 px/s 太慢。折中：设 90 秒滚完，音乐淡出
VIDEO_DURATION = min(90, audio_duration)  # 90 秒或音乐时长
scroll_speed = scroll_max / VIDEO_DURATION  # px/sec
print(f"   视频时长: {VIDEO_DURATION:.1f}s, 滚速: {scroll_speed:.1f} px/s")

# === 帧生成函数 ===
def make_frame(t):
    """ t: 0..VIDEO_DURATION, 返回 1920×1080×3 numpy array """
    y = int(t * scroll_speed)
    y = max(0, min(y, scroll_max))
    # crop: [y : y+1920, 0:1080]
    frame = img_array[y:y + VIEWPORT_H, 0:VIEWPORT_W, :3]  # RGB
    return frame

print("🎬 生成视频帧...")
clip = VideoClip(make_frame, duration=VIDEO_DURATION)
clip = clip.with_fps(FPS)

# === 音频：截取前 VIDEO_DURATION 秒，末尾淡出 ===
bgm = audio.subclipped(0, VIDEO_DURATION)
bgm = bgm.with_effects([("audio_fadeout", 3)])  # 最后3秒淡出
clip = clip.with_audio(bgm)

# === 导出 ===
print(f"💾 导出 MP4 → {OUT_PATH}")
clip.write_videofile(
    OUT_PATH,
    codec="libx264",
    fps=FPS,
    preset="medium",
    bitrate="5000k",
    audio_codec="aac",
    audio_bitrate="192k",
    threads=4,
)

# 文件大小
size_mb = os.path.getsize(OUT_PATH) / (1024 * 1024)
print(f"\n✅ 完成! {OUT_PATH}")
print(f"📏 文件大小: {size_mb:.1f} MB")
print(f"📐 分辨率: {VIEWPORT_W}×{VIEWPORT_H}, {FPS}fps")
print(f"⏱  时长: {VIDEO_DURATION:.1f}s")
