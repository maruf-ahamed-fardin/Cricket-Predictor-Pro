"""
Generate a cinematic 60fps cricket stadium & match action MP4 video loop for the Hero Section.
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import imageio

WIDTH = 1280
HEIGHT = 720
FPS = 30
DURATION_SEC = 5
TOTAL_FRAMES = FPS * DURATION_SEC

OUTPUT_DIR = r"c:\Users\Fardin\Desktop\model\app\static\videos"
IMG_DIR = r"c:\Users\Fardin\Desktop\model\app\static\img"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

VIDEO_PATH = os.path.join(OUTPUT_DIR, "hero_cricket.mp4")
POSTER_PATH = os.path.join(IMG_DIR, "hero_poster.jpg")

print(f"Generating {TOTAL_FRAMES} frames ({DURATION_SEC}s @ {FPS}fps) for cinematic cricket loop...")

writer = imageio.get_writer(VIDEO_PATH, fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p")

for frame_idx in range(TOTAL_FRAMES):
    t = frame_idx / TOTAL_FRAMES  # 0.0 to 1.0
    phase = t * 2 * math.pi

    # Base Background Image (Dark Stadium Night Sky)
    im = Image.new("RGBA", (WIDTH, HEIGHT), (6, 10, 20, 255))
    draw = ImageDraw.Draw(im)

    # 1. Atmospheric Stadium Gradient (Deep Teal & Midnight Blue)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(6 + 10 * ratio + 8 * math.sin(phase + ratio * 2))
        g = int(12 + 25 * ratio + 12 * math.sin(phase + ratio * 2))
        b = int(24 + 40 * ratio + 15 * math.cos(phase + ratio * 2))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    # 2. Stadium Floodlight Beams (4 Towers)
    beam_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    beam_draw = ImageDraw.Draw(beam_layer)

    towers = [
        (120, 80, 450, 600, (74, 222, 128)),
        (350, 60, 550, 550, (34, 211, 238)),
        (930, 60, 730, 550, (34, 211, 238)),
        (1160, 80, 830, 600, (74, 222, 128))
    ]

    for tx, ty, target_x, target_y, col in towers:
        # Tower base
        beam_draw.rectangle([tx - 8, ty, tx + 8, ty + 120], fill=(20, 30, 50, 200))
        # Floodlight bank
        beam_draw.ellipse([tx - 24, ty - 12, tx + 24, ty + 12], fill=(240, 255, 250, 255))
        # Volumetric cone
        pulse = 0.85 + 0.15 * math.sin(phase * 2 + tx)
        alpha = int(35 * pulse)
        beam_draw.polygon([
            (tx, ty),
            (target_x - 180, target_y),
            (target_x + 180, target_y)
        ], fill=(col[0], col[1], col[2], alpha))

    im = Image.alpha_composite(im, beam_layer)
    draw = ImageDraw.Draw(im)

    # 3. Cricket Outfield & Pitch (Perspective Oval)
    # Outfield
    draw.ellipse([80, 360, WIDTH - 80, 820], fill=(12, 45, 28, 240), outline=(34, 197, 94, 80), width=4)
    draw.ellipse([180, 410, WIDTH - 180, 770], fill=(16, 60, 36, 255), outline=(74, 222, 128, 120), width=2)
    # Cricket 22-Yard Pitch
    pitch_pts = [
        (WIDTH//2 - 60, 460),
        (WIDTH//2 + 60, 460),
        (WIDTH//2 + 90, 680),
        (WIDTH//2 - 90, 680)
    ]
    draw.polygon(pitch_pts, fill=(180, 150, 110, 220), outline=(217, 180, 130, 255), width=2)
    # Crease markings
    draw.line([(WIDTH//2 - 75, 500), (WIDTH//2 + 75, 500)], fill=(255, 255, 255, 200), width=2)
    draw.line([(WIDTH//2 - 85, 640), (WIDTH//2 + 85, 640)], fill=(255, 255, 255, 200), width=3)

    # 4. Animated Stumps (Wickets)
    stump_x = WIDTH // 2
    stump_y = 485
    for sx in [stump_x - 8, stump_x, stump_x + 8]:
        draw.line([(sx, stump_y), (sx, stump_y - 32)], fill=(245, 245, 245, 240), width=3)
    draw.line([(stump_x - 12, stump_y - 32), (stump_x + 12, stump_y - 32)], fill=(250, 204, 21, 255), width=3)

    # 5. Animated AI Cricket Ball Trajectory
    ball_t = (t * 1.5) % 1.0  # loops 1.5 times
    # Parabolic trajectory from bowler to batsman and out into outfield
    start_x, start_y = 200, 580
    apex_x, apex_y = WIDTH // 2 - 40, 320
    end_x, end_y = WIDTH - 150, 420

    # Quadratic Bezier
    bx = (1 - ball_t)**2 * start_x + 2 * (1 - ball_t) * ball_t * apex_x + ball_t**2 * end_x
    by = (1 - ball_t)**2 * start_y + 2 * (1 - ball_t) * ball_t * apex_y + ball_t**2 * end_y

    # Trajectory trace with glowing points
    pts = []
    for step in np.linspace(0, ball_t, 25):
        px = (1 - step)**2 * start_x + 2 * (1 - step) * step * apex_x + step**2 * end_x
        py = (1 - step)**2 * start_y + 2 * (1 - step) * step * apex_y + step**2 * end_y
        pts.append((px, py))

    if len(pts) > 1:
        for i in range(len(pts) - 1):
            alpha = int(255 * (i / len(pts)))
            draw.line([pts[i], pts[i+1]], fill=(74, 222, 128, alpha), width=3)

    # Ball with Cyber Glow & Seam
    ball_radius = 11 + int(2 * math.sin(phase))
    draw.ellipse([bx - ball_radius - 6, by - ball_radius - 6, bx + ball_radius + 6, by + ball_radius + 6], fill=(74, 222, 128, 60))
    draw.ellipse([bx - ball_radius, by - ball_radius, bx + ball_radius, by + ball_radius], fill=(239, 68, 68, 255), outline=(255, 255, 255, 240), width=2)
    # Seam rotation
    seam_angle = phase * 4
    dx = math.cos(seam_angle) * ball_radius
    dy = math.sin(seam_angle) * ball_radius
    draw.line([(bx - dx, by - dy), (bx + dx, by + dy)], fill=(255, 255, 255, 220), width=2)

    # 6. Futuristic Cyber Grid Floating Nodes (Subtle AI Theme)
    for i, nx in enumerate(range(100, WIDTH, 180)):
        ny = 220 + int(35 * math.sin(phase + i * 0.8))
        draw.ellipse([nx - 3, ny - 3, nx + 3, ny + 3], fill=(34, 211, 238, 160))
        if i > 0:
            prev_x = nx - 180
            prev_y = 220 + int(35 * math.sin(phase + (i - 1) * 0.8))
            draw.line([(prev_x, prev_y), (nx, ny)], fill=(34, 211, 238, 40), width=1)

    # Convert to RGB numpy array for imageio
    rgb_frame = np.array(im.convert("RGB"))
    writer.append_data(rgb_frame)

    if frame_idx == 0:
        im.convert("RGB").save(POSTER_PATH, "JPEG", quality=90)

writer.close()
print(f"Video generated successfully at {VIDEO_PATH}")
print(f"Poster image saved at {POSTER_PATH}")
