import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import imageio

OUTPUT_DIR = r"c:\Users\Fardin\Desktop\model\app\static\videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

WIDTH, HEIGHT = 1280, 720
FPS = 25
NUM_FRAMES = 50  # 2 second seamless loop

def create_stadium_night_frame(t_norm):
    # t_norm in [0, 1)
    im = Image.new("RGB", (WIDTH, HEIGHT), (8, 14, 28))
    draw = ImageDraw.Draw(im)

    # Gradient background (pitch & sky)
    # Sky deep blue to dark emerald pitch
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        if ratio < 0.55:
            r = int(6 + 10 * ratio)
            g = int(12 + 18 * ratio)
            b = int(28 + 24 * ratio)
        else:
            p_ratio = (ratio - 0.55) / 0.45
            r = int(14 + 10 * p_ratio)
            g = int(45 + 55 * p_ratio)
            b = int(32 + 20 * p_ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Stadium Floodlight Beams (sweeping slowly)
    beam_canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    beam_draw = ImageDraw.Draw(beam_canvas)

    # 4 Floodlight towers (top left, top right, center left, center right)
    towers = [
        (160, 40, -0.4),
        (WIDTH - 160, 40, 0.4),
        (380, 50, -0.15),
        (WIDTH - 380, 50, 0.15),
    ]

    for tx, ty, angle_base in towers:
        # Sweeping angle
        sweep = math.sin(t_norm * 2 * math.pi + tx) * 0.18
        angle = angle_base + sweep
        
        # Beam polygon
        beam_len = 800
        spread = 180
        bx1 = tx + math.sin(angle - 0.18) * beam_len - spread
        by1 = ty + math.cos(angle - 0.18) * beam_len
        bx2 = tx + math.sin(angle + 0.18) * beam_len + spread
        by2 = ty + math.cos(angle + 0.18) * beam_len

        # Light beam
        beam_draw.polygon([(tx, ty), (bx1, by1), (bx2, by2)], fill=(120, 240, 180, 28))
        # Tower lamp glow
        beam_draw.ellipse([tx-25, ty-25, tx+25, ty+25], fill=(220, 255, 240, 160))

    # Cricket Pitch 3D Perspective Lines in center
    pitch_top_y = int(HEIGHT * 0.56)
    pitch_bot_y = HEIGHT
    pt_w_half = 90
    pb_w_half = 340
    cx = WIDTH // 2

    # Pitch surface
    beam_draw.polygon([
        (cx - pt_w_half, pitch_top_y),
        (cx + pt_w_half, pitch_top_y),
        (cx + pb_w_half, pitch_bot_y),
        (cx - pb_w_half, pitch_bot_y)
    ], fill=(160, 140, 100, 45))

    # Floating dust / ambient particles
    np.random.seed(42)
    for i in range(70):
        init_x = (np.random.rand() * WIDTH)
        init_y = (np.random.rand() * HEIGHT)
        speed_y = 15 + (i % 20)
        speed_x = math.sin(i + t_norm * 2 * math.pi) * 20
        
        py = (init_y - t_norm * speed_y * 10) % HEIGHT
        px = (init_x + speed_x) % WIDTH
        size = 2 + (i % 4)
        alpha = int(80 + 70 * math.sin(t_norm * 2 * math.pi + i))
        beam_draw.ellipse([px, py, px+size, py+size], fill=(160, 255, 210, alpha))

    # Composite beam canvas onto base
    im.paste(beam_canvas, (0, 0), beam_canvas)
    return np.array(im)


def create_cyber_matrix_frame(t_norm):
    im = Image.new("RGB", (WIDTH, HEIGHT), (6, 10, 22))
    draw = ImageDraw.Draw(im)

    # Cyber grid floor with scrolling forward motion
    cy = int(HEIGHT * 0.52)
    cx = WIDTH // 2

    # Horizontal grid lines (perspective compressed)
    grid_canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid_canvas)

    num_lines = 16
    for i in range(num_lines):
        line_progress = ((i / num_lines) + t_norm * (1.0 / num_lines)) % 1.0
        # Exponential perspective spacing
        y = cy + int((line_progress ** 2.2) * (HEIGHT - cy))
        alpha = int(25 + line_progress * 130)
        gdraw.line([(0, y), (WIDTH, y)], fill=(6, 182, 212, alpha), width=1)

    # Perspective vertical vanishing lines
    for vx in range(-12, 13):
        bot_x = cx + vx * 120
        gdraw.line([(cx, cy), (bot_x, HEIGHT)], fill=(6, 182, 212, 45), width=1)

    # Futuristic Holographic Cricket Trajectory Parabola Arc
    # Ball traveling in an arc
    arc_points = []
    for step in range(60):
        ratio = step / 59.0
        px = int(cx - 360 + ratio * 720)
        # Parabolic arc
        h_offset = math.sin(ratio * math.pi) * 260
        py = int(cy + 40 - h_offset)
        arc_points.append((px, py))

    # Draw trajectory line
    for i in range(len(arc_points) - 1):
        gdraw.line([arc_points[i], arc_points[i+1]], fill=(74, 222, 128, 90), width=2)

    # Glowing ball on trajectory
    ball_idx = int(t_norm * (len(arc_points) - 1))
    bx, by = arc_points[ball_idx]
    # Ball glow
    gdraw.ellipse([bx-30, by-30, bx+30, by+30], fill=(74, 222, 128, 50))
    gdraw.ellipse([bx-16, by-16, bx+16, by+16], fill=(160, 255, 200, 140))
    gdraw.ellipse([bx-7, by-7, bx+7, by+7], fill=(255, 255, 255, 240))

    # Neural Network Data Nodes pulsing in upper half
    nodes = [
        (220, 180), (380, 140), (540, 210), (700, 160), (860, 130), (1040, 200),
        (300, 260), (480, 310), (800, 280), (960, 290)
    ]
    for i, (nx, ny) in enumerate(nodes):
        pulse = math.sin(t_norm * 2 * math.pi + i * 1.2)
        radius = 5 + int(pulse * 2)
        alpha = int(120 + 80 * pulse)
        gdraw.ellipse([nx-radius, ny-radius, nx+radius, ny+radius], fill=(139, 92, 246, alpha))
        
        # Connect to next node
        if i < len(nodes) - 1:
            nnx, nny = nodes[i+1]
            gdraw.line([(nx, ny), (nnx, nny)], fill=(139, 92, 246, 40), width=1)

    im.paste(grid_canvas, (0, 0), grid_canvas)
    return np.array(im)


def create_fast_bowling_frame(t_norm):
    im = Image.new("RGB", (WIDTH, HEIGHT), (14, 8, 22))
    draw = ImageDraw.Draw(im)

    # Background energy gradient
    cx, cy = WIDTH // 2, HEIGHT // 2
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(canvas)

    # Radial vortex swirl
    num_particles = 90
    np.random.seed(101)
    for i in range(num_particles):
        radius_base = 60 + (i * 6.5)
        angle_base = (i * 0.4) + t_norm * 2 * math.pi * (1.5 if i % 2 == 0 else -1.0)
        
        px = cx + math.cos(angle_base) * radius_base * 1.6
        py = cy + math.sin(angle_base) * radius_base * 0.75
        
        # Colors vary between amber, cricket red, and neon cyan
        if i % 3 == 0:
            col = (245, 158, 11, 140)  # Amber
        elif i % 3 == 1:
            col = (239, 68, 68, 120)   # Red
        else:
            col = (6, 182, 212, 100)   # Cyan

        sz = 3 + (i % 5)
        cdraw.ellipse([px-sz, py-sz, px+sz, py+sz], fill=col)

    # Central spinning cricket ball with glowing seam
    ball_r = 75
    cdraw.ellipse([cx-ball_r, cy-ball_r, cx+ball_r, cy+ball_r], fill=(185, 28, 28, 220))
    # Ball shine / 3D highlight
    cdraw.ellipse([cx-ball_r+15, cy-ball_r+12, cx-ball_r+55, cy-ball_r+50], fill=(255, 140, 140, 110))

    # Spinning seam
    seam_angle = t_norm * 2 * math.pi * 2.0
    seam_w = ball_r * 0.95
    seam_h = math.sin(seam_angle) * ball_r * 0.95
    
    # Seam ellipse path
    cdraw.ellipse([cx-seam_w, cy-abs(seam_h), cx+seam_w, cy+abs(seam_h)], outline=(255, 255, 255, 200), width=3)

    # Energy halo
    cdraw.ellipse([cx-ball_r-25, cy-ball_r-25, cx+ball_r+25, cy+ball_r+25], outline=(245, 158, 11, 70), width=4)

    im.paste(canvas, (0, 0), canvas)
    return np.array(im)


def create_golden_stadium_frame(t_norm):
    im = Image.new("RGB", (WIDTH, HEIGHT), (28, 20, 12))
    draw = ImageDraw.Draw(im)

    # Warm Golden Sunset over Stadium Horizon
    # Gradient sky: vibrant orange/gold to warm peach
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        if ratio < 0.48:
            r = int(220 - 90 * ratio)
            g = int(140 - 50 * ratio)
            b = int(50 + 40 * ratio)
        else:
            p_ratio = (ratio - 0.48) / 0.52
            r = int(35 + 25 * p_ratio)
            g = int(95 + 65 * p_ratio)
            b = int(45 + 30 * p_ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(canvas)

    # Sun / Glow disc at horizon
    sun_x = WIDTH // 2 + 120
    sun_y = int(HEIGHT * 0.42)
    sun_pulse = 1.0 + 0.05 * math.sin(t_norm * 2 * math.pi)
    
    cdraw.ellipse([sun_x - 140*sun_pulse, sun_y - 140*sun_pulse, sun_x + 140*sun_pulse, sun_y + 140*sun_pulse], fill=(255, 230, 140, 50))
    cdraw.ellipse([sun_x - 65, sun_y - 65, sun_x + 65, sun_y + 65], fill=(255, 250, 200, 180))

    # Sunbeams shimmering
    for b in range(12):
        angle = (b / 12) * math.pi * 2 + t_norm * 0.4
        bx = sun_x + math.cos(angle) * 700
        by = sun_y + math.sin(angle) * 500
        cdraw.line([(sun_x, sun_y), (bx, by)], fill=(255, 220, 130, 22), width=18)

    # Golden dust sparkles
    np.random.seed(77)
    for i in range(80):
        init_x = (np.random.rand() * WIDTH)
        init_y = (np.random.rand() * HEIGHT)
        py = (init_y - t_norm * 18 * (10 + i % 15)) % HEIGHT
        px = (init_x + math.sin(t_norm * 2 * math.pi + i) * 25) % WIDTH
        alpha = int(90 + 80 * math.sin(t_norm * 2 * math.pi + i * 0.7))
        cdraw.ellipse([px, py, px+4, py+4], fill=(255, 235, 160, alpha))

    im.paste(canvas, (0, 0), canvas)
    return np.array(im)


def main():
    generators = [
        ("stadium_night.mp4", create_stadium_night_frame),
        ("cyber_matrix.mp4", create_cyber_matrix_frame),
        ("fast_bowling.mp4", create_fast_bowling_frame),
        ("golden_stadium.mp4", create_golden_stadium_frame),
    ]

    for filename, func in generators:
        out_path = os.path.join(OUTPUT_DIR, filename)
        print(f"Generating {filename} ({NUM_FRAMES} frames @ {FPS}fps)...")
        frames = []
        for f in range(NUM_FRAMES):
            t_norm = f / NUM_FRAMES
            frame = func(t_norm)
            frames.append(frame)
        
        imageio.mimsave(out_path, frames, fps=FPS, codec="libx264", quality=8)
        size_kb = os.path.getsize(out_path) / 1024
        print(f"Saved: {out_path} ({size_kb:.1f} KB)")

    # Also make stadium_night.mp4 the default hero_cricket.mp4
    default_path = os.path.join(OUTPUT_DIR, "hero_cricket.mp4")
    import shutil
    shutil.copy(os.path.join(OUTPUT_DIR, "stadium_night.mp4"), default_path)
    print("Default hero_cricket.mp4 updated.")

if __name__ == "__main__":
    main()
