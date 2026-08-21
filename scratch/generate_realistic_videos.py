import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import imageio

OUTPUT_DIR = r"c:\Users\Fardin\Desktop\model\app\static\videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

WIDTH, HEIGHT = 1280, 720
FPS = 25
NUM_FRAMES = 60  # 2.4s seamless loop

def get_smooth_cycle(t_norm):
    # Smooth 0->1->0 cycle for seamless back-and-forth or loop
    return 0.5 - 0.5 * math.cos(t_norm * 2 * math.pi)

# ─── 1. REALISTIC STADIUM AT NIGHT (Floodlights, Turf, Pitch, Stands) ───────────
def create_realistic_stadium_night(t_norm):
    im = Image.new("RGBA", (WIDTH, HEIGHT), (6, 10, 20, 255))
    draw = ImageDraw.Draw(im)

    cam_zoom = 1.0 + 0.04 * math.sin(t_norm * 2 * math.pi)
    cam_pan_x = math.sin(t_norm * 2 * math.pi) * 15

    # Sky gradient (Midnight dark navy)
    for y in range(int(HEIGHT * 0.45)):
        r = int(5 + (y / (HEIGHT * 0.45)) * 12)
        g = int(8 + (y / (HEIGHT * 0.45)) * 18)
        b = int(22 + (y / (HEIGHT * 0.45)) * 28)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    # Stadium Stands (Crowd bokeh lights in tiered bowls)
    stand_top = int(HEIGHT * 0.28)
    stand_bot = int(HEIGHT * 0.50)
    for y in range(stand_top, stand_bot):
        prog = (y - stand_top) / (stand_bot - stand_top)
        draw.line([(0, y), (WIDTH, y)], fill=(int(12 + 15*prog), int(16 + 22*prog), int(30 + 35*prog), 255))

    # Crowd thousands of sparkling bokeh dots
    np.random.seed(88)
    for i in range(220):
        cx = int((np.random.rand() * WIDTH + cam_pan_x) % WIDTH)
        cy = int(stand_top + np.random.rand() * (stand_bot - stand_top))
        flicker = 0.6 + 0.4 * math.sin(t_norm * 4 * math.pi + i * 1.7)
        c_choice = i % 4
        if c_choice == 0:
            c = (255, 230, 180, int(160 * flicker))
        elif c_choice == 1:
            c = (140, 220, 255, int(150 * flicker))
        elif c_choice == 2:
            c = (255, 120, 120, int(120 * flicker))
        else:
            c = (180, 255, 180, int(140 * flicker))
        sz = 1 + (i % 3)
        draw.ellipse([cx-sz, cy-sz, cx+sz, cy+sz], fill=c)

    # Green Grass Outfield with alternating mowed circular lawn stripes
    ground_center_y = int(HEIGHT * 0.85)
    cx_ground = WIDTH // 2 + int(cam_pan_x * 0.6)
    
    # Draw concentric/striped grass field
    for radius in range(950, 40, -18):
        stripe_type = (radius // 18) % 2
        if stripe_type == 0:
            grass_col = (18, 72, 38, 255)
        else:
            grass_col = (26, 92, 48, 255)
        # Perspective oval
        ry = int(radius * 0.42 * cam_zoom)
        rx = int(radius * 1.15 * cam_zoom)
        draw.ellipse([cx_ground - rx, ground_center_y - ry, cx_ground + rx, ground_center_y + ry], fill=grass_col)

    # Clay Cricket Pitch in Center
    pitch_y1 = int(HEIGHT * 0.50)
    pitch_y2 = int(HEIGHT * 0.96)
    pw_top = int(65 * cam_zoom)
    pw_bot = int(240 * cam_zoom)
    
    # Pitch surface (Realistic sandy clay tone)
    pitch_pts = [
        (cx_ground - pw_top, pitch_y1),
        (cx_ground + pw_top, pitch_y1),
        (cx_ground + pw_bot, pitch_y2),
        (cx_ground - pw_bot, pitch_y2)
    ]
    draw.polygon(pitch_pts, fill=(188, 162, 125, 255))
    draw.polygon(pitch_pts, outline=(140, 115, 85, 255), width=2)

    # White Crease Markings & Stumps
    # Batting crease bottom
    draw.line([(cx_ground - pw_bot + 30, int(pitch_y2 - 20)), (cx_ground + pw_bot - 30, int(pitch_y2 - 20))], fill=(255, 255, 255, 240), width=4)
    # Bowling crease top
    draw.line([(cx_ground - pw_top + 10, int(pitch_y1 + 18)), (cx_ground + pw_top - 10, int(pitch_y1 + 18))], fill=(255, 255, 255, 220), width=3)
    # Popping crease & return creases
    draw.line([(cx_ground - 25, int(pitch_y2 - 20)), (cx_ground - 25, int(pitch_y2))], fill=(255, 255, 255, 230), width=3)
    draw.line([(cx_ground + 25, int(pitch_y2 - 20)), (cx_ground + 25, int(pitch_y2))], fill=(255, 255, 255, 230), width=3)

    # 3 Wooden Stumps bottom
    stump_y = int(pitch_y2 - 22)
    for sx in [-8, 0, 8]:
        draw.line([(cx_ground + sx, stump_y), (cx_ground + sx, stump_y - 24)], fill=(240, 210, 160, 255), width=3)
    draw.line([(cx_ground - 10, stump_y - 24), (cx_ground + 10, stump_y - 24)], fill=(240, 210, 160, 255), width=2)

    # Top Stumps
    stump_top_y = int(pitch_y1 + 17)
    for sx in [-4, 0, 4]:
        draw.line([(cx_ground + sx, stump_top_y), (cx_ground + sx, stump_top_y - 12)], fill=(230, 200, 150, 255), width=2)

    # Giant Floodlight Towers & Volumetric Light Cones
    lights = [
        (120, 60, -0.35),
        (WIDTH - 120, 60, 0.35),
        (360, 70, -0.12),
        (WIDTH - 360, 70, 0.12)
    ]
    beam_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beam_layer)

    for lx, ly, angle_bias in lights:
        sweep = math.sin(t_norm * 2 * math.pi + lx) * 0.08
        beam_ang = angle_bias + sweep
        
        # Volumetric cone
        cone_len = 950
        spread = 240
        c1x = lx + math.sin(beam_ang - 0.22) * cone_len - spread
        c1y = ly + math.cos(beam_ang - 0.22) * cone_len
        c2x = lx + math.sin(beam_ang + 0.22) * cone_len + spread
        c2y = ly + math.cos(beam_ang + 0.22) * cone_len
        
        bdraw.polygon([(lx, ly), (c1x, c1y), (c2x, c2y)], fill=(180, 255, 230, 32))
        
        # Light rig truss & bulb glow
        draw.rectangle([lx-28, ly-14, lx+28, ly+14], fill=(30, 40, 55, 255))
        # 8 LED clusters
        for gx in range(-20, 25, 12):
            for gy in [-6, 6]:
                bdraw.ellipse([lx+gx-5, ly+gy-5, lx+gx+5, ly+gy+5], fill=(240, 255, 255, 230))
        # Giant glare halo
        bdraw.ellipse([lx-60, ly-60, lx+60, ly+60], fill=(160, 255, 220, 70))

    # Atmospheric floating light motes
    for i in range(50):
        px = int((i * 47 + t_norm * 60) % WIDTH)
        py = int((i * 31 + math.sin(t_norm * 2 * math.pi + i) * 30) % HEIGHT)
        alpha = int(90 + 70 * math.sin(t_norm * 2 * math.pi + i))
        bdraw.ellipse([px, py, px+3, py+3], fill=(220, 255, 240, alpha))

    im.paste(beam_layer, (0, 0), beam_layer)
    return np.array(im.convert("RGB"))


# ─── 2. REALISTIC GOLDEN SUNLIT STADIUM (Lush Greenery, Sunbeams) ──────────────
def create_realistic_golden_stadium(t_norm):
    im = Image.new("RGBA", (WIDTH, HEIGHT), (40, 25, 15, 255))
    draw = ImageDraw.Draw(im)

    cam_pan = math.sin(t_norm * 2 * math.pi) * 12

    # Warm Golden Sky
    for y in range(int(HEIGHT * 0.48)):
        prog = y / (HEIGHT * 0.48)
        r = int(245 - 60 * prog)
        g = int(160 - 30 * prog)
        b = int(70 + 40 * prog)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    # Stadium architectural roof line
    roof_pts = [
        (0, int(HEIGHT * 0.38)),
        (int(WIDTH * 0.3), int(HEIGHT * 0.32)),
        (int(WIDTH * 0.7), int(HEIGHT * 0.32)),
        (WIDTH, int(HEIGHT * 0.38)),
        (WIDTH, int(HEIGHT * 0.48)),
        (0, int(HEIGHT * 0.48))
    ]
    draw.polygon(roof_pts, fill=(50, 45, 55, 255))

    # Sunlit Lush Green Ground
    ground_y = int(HEIGHT * 0.86)
    cx_ground = WIDTH // 2 + int(cam_pan)
    for radius in range(920, 40, -18):
        stripe = (radius // 18) % 2
        grass = (52, 148, 62, 255) if stripe == 0 else (68, 175, 78, 255)
        ry = int(radius * 0.42)
        rx = int(radius * 1.15)
        draw.ellipse([cx_ground - rx, ground_y - ry, cx_ground + rx, ground_y + ry], fill=grass)

    # Golden Sunlit Clay Pitch
    pitch_pts = [
        (cx_ground - 60, int(HEIGHT * 0.52)),
        (cx_ground + 60, int(HEIGHT * 0.52)),
        (cx_ground + 220, int(HEIGHT * 0.95)),
        (cx_ground - 220, int(HEIGHT * 0.95))
    ]
    draw.polygon(pitch_pts, fill=(215, 185, 140, 255))
    # Pitch crease lines
    draw.line([(cx_ground - 180, int(HEIGHT * 0.93)), (cx_ground + 180, int(HEIGHT * 0.93))], fill=(255, 255, 255, 240), width=4)
    draw.line([(cx_ground - 50, int(HEIGHT * 0.54)), (cx_ground + 50, int(HEIGHT * 0.54))], fill=(255, 255, 255, 220), width=3)

    # Sun & Shimmering Flare
    beam_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beam_layer)

    sun_x = int(WIDTH * 0.78 + cam_pan * 0.5)
    sun_y = int(HEIGHT * 0.28)
    
    # Sun disk & corona
    bdraw.ellipse([sun_x-180, sun_y-180, sun_x+180, sun_y+180], fill=(255, 235, 160, 45))
    bdraw.ellipse([sun_x-80, sun_y-80, sun_x+80, sun_y+80], fill=(255, 250, 210, 160))
    bdraw.ellipse([sun_x-35, sun_y-35, sun_x+35, sun_y+35], fill=(255, 255, 255, 250))

    # Anamorphic horizontal lens flare line
    bdraw.line([(0, sun_y), (WIDTH, sun_y)], fill=(255, 245, 190, 80), width=3)

    # Shimmering sunbeams across pitch
    for i in range(8):
        ang = (i / 8) * 1.2 + 0.9 + math.sin(t_norm * 2 * math.pi) * 0.05
        bx = sun_x - math.cos(ang) * 900
        by = sun_y + math.sin(ang) * 750
        bdraw.line([(sun_x, sun_y), (bx, by)], fill=(255, 225, 140, 25), width=24)

    # Floating golden dust motes
    for i in range(60):
        px = int((i * 41 + t_norm * 45) % WIDTH)
        py = int((i * 29 + math.sin(t_norm * 2 * math.pi + i) * 20) % HEIGHT)
        alpha = int(110 + 90 * math.sin(t_norm * 2 * math.pi + i * 1.3))
        bdraw.ellipse([px, py, px+4, py+4], fill=(255, 240, 170, alpha))

    im.paste(beam_layer, (0, 0), beam_layer)
    return np.array(im.convert("RGB"))


# ─── 3. REALISTIC FAST BOWLING / KOOKABURRA CRICKET BALL SPIN (Macro HD) ─────────
def create_realistic_ball_spin(t_norm):
    im = Image.new("RGBA", (WIDTH, HEIGHT), (12, 16, 24, 255))
    draw = ImageDraw.Draw(im)

    # Outfield blur in background
    for y in range(HEIGHT):
        prog = y / HEIGHT
        r = int(14 + 18 * prog)
        g = int(45 + 50 * prog)
        b = int(25 + 20 * prog)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    cx, cy = WIDTH // 2, HEIGHT // 2
    ball_r = 135  # Large macro close-up

    # 3D Shaded Red Leather Ball
    ball_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(ball_layer)

    # Shadow under ball
    bdraw.ellipse([cx-ball_r-20, cy+ball_r-10, cx+ball_r+20, cy+ball_r+35], fill=(0, 0, 0, 120))

    # Base sphere gradient
    for r in range(ball_r, 0, -2):
        ratio = r / ball_r
        # Deep cherry red to bright crimson highlight
        cr = int(215 - 55 * ratio)
        cg = int(25 - 15 * ratio)
        cb = int(32 - 18 * ratio)
        offset_x = int(-25 * (1 - ratio))
        offset_y = int(-25 * (1 - ratio))
        bdraw.ellipse([cx + offset_x - r, cy + offset_y - r, cx + offset_x + r, cy + offset_y + r], fill=(cr, cg, cb, 255))

    # Specular curved highlight on glossy leather
    bdraw.ellipse([cx - 75, cy - 85, cx - 15, cy - 35], fill=(255, 160, 160, 140))
    bdraw.ellipse([cx - 65, cy - 75, cx - 35, cy - 45], fill=(255, 255, 255, 220))

    # Realistic White Seam Stitching (Rotating smoothly in 3D perspective)
    spin_angle = t_norm * 2 * math.pi
    seam_tilt = 0.35  # 20 degree tilt

    # Number of visible stitches along seam ellipse
    num_stitches = 36
    for s in range(num_stitches):
        theta = (s / num_stitches) * 2 * math.pi + spin_angle
        # 3D sphere coordinate
        sx_3d = math.cos(theta) * ball_r * 0.98
        sy_3d = math.sin(theta) * ball_r * 0.98 * math.sin(seam_tilt)
        sz_3d = math.sin(theta) * ball_r * 0.98 * math.cos(seam_tilt)

        # Only draw front facing stitches
        if sz_3d > -15:
            # Rotate by tilt
            final_x = cx + sx_3d
            final_y = cy + sy_3d
            
            # Stitch width and orientation
            stitch_len = 6
            st_ang = theta + math.pi / 2
            dx = math.cos(st_ang) * stitch_len
            dy = math.sin(st_ang) * stitch_len
            
            # White thread stitch
            bdraw.line([(final_x - dx, final_y - dy), (final_x + dx, final_y + dy)], fill=(255, 255, 255, 230), width=3)
            # Seam seam ridge shadow
            bdraw.line([(final_x - dx + 1, final_y - dy + 1), (final_x + dx + 1, final_y + dy + 1)], fill=(90, 10, 15, 160), width=2)

    # Gold "KOOKABURRA PRO" logo stamp rotating on leather
    logo_theta = spin_angle + 1.2
    if math.cos(logo_theta) > 0:
        lx = cx + math.sin(logo_theta) * 45
        ly = cy + 30
        bdraw.ellipse([lx-14, ly-14, lx+14, ly+14], outline=(235, 195, 80, 180), width=2)

    # Motion speed lines & air trail particles
    for i in range(40):
        line_ang = (i / 40) * 2 * math.pi
        rad_start = ball_r + 8
        rad_end = ball_r + 35 + int(math.sin(t_norm * 4 * math.pi + i) * 15)
        x1 = cx + math.cos(line_ang) * rad_start
        y1 = cy + math.sin(line_ang) * rad_start
        x2 = cx + math.cos(line_ang) * rad_end
        y2 = cy + math.sin(line_ang) * rad_end
        bdraw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 45), width=2)

    im.paste(ball_layer, (0, 0), ball_layer)
    return np.array(im.convert("RGB"))


# ─── 4. REALISTIC HAWK-EYE AI CRICKET ANALYTICS (Pitch Map & 3D Trajectory) ────
def create_realistic_cyber_analytics(t_norm):
    im = Image.new("RGBA", (WIDTH, HEIGHT), (6, 12, 24, 255))
    draw = ImageDraw.Draw(im)

    # Dark high-tech stadium broadcast background
    for y in range(HEIGHT):
        prog = y / HEIGHT
        r = int(4 + 10 * prog)
        g = int(8 + 20 * prog)
        b = int(18 + 35 * prog)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    cx = WIDTH // 2

    # 3D Hawk-Eye Cricket Pitch Grid
    pitch_y1 = int(HEIGHT * 0.42)
    pitch_y2 = int(HEIGHT * 0.94)
    pw1 = 70
    pw2 = 280

    # 3D Pitch surface
    draw.polygon([(cx - pw1, pitch_y1), (cx + pw1, pitch_y1), (cx + pw2, pitch_y2), (cx - pw2, pitch_y2)], fill=(12, 28, 48, 240), outline=(6, 182, 212, 180), width=2)

    # Grid segments (Good length, Full, Short zones)
    zones = [0.25, 0.50, 0.75]
    zone_cols = [
        (239, 68, 68, 70),   # Full (Red)
        (74, 222, 128, 80),  # Good length (Green)
        (245, 158, 11, 70)   # Short (Amber)
    ]
    for i, z_ratio in enumerate(zones):
        zy = int(pitch_y1 + z_ratio * (pitch_y2 - pitch_y1))
        zw = int(pw1 + z_ratio * (pw2 - pw1))
        draw.line([(cx - zw, zy), (cx + zw, zy)], fill=(6, 182, 212, 120), width=2)

    # Center stump target line
    draw.line([(cx, pitch_y1), (cx, pitch_y2)], fill=(6, 182, 212, 90), width=2)

    # 3D Animated Ball Trajectory (Delivery release -> Bounce -> Stumps hit)
    arc_points = []
    # Segment 1: Release to pitch bounce
    bounce_x = cx + int(math.sin(t_norm * 2 * math.pi) * 20)
    bounce_y = int(pitch_y1 + 0.65 * (pitch_y2 - pitch_y1))

    release_x = cx - 180
    release_y = int(HEIGHT * 0.35)

    hit_x = cx + 8
    hit_y = int(HEIGHT * 0.90)

    # Bezier curve for release -> bounce
    for step in range(35):
        t = step / 34.0
        # Quadratic bezier
        bx = (1-t)**2 * release_x + 2*(1-t)*t * (cx - 40) + t**2 * bounce_x
        by = (1-t)**2 * release_y + 2*(1-t)*t * (bounce_y - 120) + t**2 * bounce_y
        arc_points.append((int(bx), int(by)))

    # Bezier curve for bounce -> stumps
    for step in range(25):
        t = step / 24.0
        bx = (1-t)**2 * bounce_x + 2*(1-t)*t * (cx + 10) + t**2 * hit_x
        by = (1-t)**2 * bounce_y + 2*(1-t)*t * (bounce_y - 65) + t**2 * hit_y
        arc_points.append((int(bx), int(by)))

    # Draw continuous glowing trajectory ribbon
    beam_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beam_layer)

    for i in range(len(arc_points) - 1):
        p1, p2 = arc_points[i], arc_points[i+1]
        bdraw.line([p1, p2], fill=(6, 182, 212, 160), width=4)
        bdraw.line([p1, p2], fill=(255, 255, 255, 240), width=2)

    # Traveling Ball with Glow
    ball_idx = int(t_norm * (len(arc_points) - 1))
    bx, by = arc_points[ball_idx]
    
    bdraw.ellipse([bx-25, by-25, bx+25, by+25], fill=(74, 222, 128, 60))
    bdraw.ellipse([bx-12, by-12, bx+12, by+12], fill=(160, 255, 210, 180))
    bdraw.ellipse([bx-5, by-5, bx+5, by+5], fill=(255, 255, 255, 255))

    # Impact ring on bounce
    bdraw.ellipse([bounce_x-22, bounce_y-9, bounce_x+22, bounce_y+9], outline=(74, 222, 128, 180), width=3)

    # 3D Glowing Virtual Stumps
    for sx in [-10, 0, 10]:
        bdraw.line([(hit_x + sx, hit_y), (hit_x + sx, hit_y - 32)], fill=(239, 68, 68, 220), width=3)
    bdraw.line([(hit_x - 12, hit_y - 32), (hit_x + 12, hit_y - 32)], fill=(239, 68, 68, 220), width=3)

    # HUD Analytics Overlay (Speed, Deviation, Spin Rate)
    # Speed box
    bdraw.rectangle([60, 100, 240, 170], fill=(10, 20, 38, 200), outline=(6, 182, 212, 180), width=1)
    bdraw.text((75, 110), "DELIVERY SPEED", fill=(6, 182, 212, 255))
    bdraw.text((75, 130), "146.8 KM/H", fill=(255, 255, 255, 255))

    # Deviation box
    bdraw.rectangle([WIDTH - 240, 100, WIDTH - 60, 170], fill=(10, 20, 38, 200), outline=(74, 222, 128, 180), width=1)
    bdraw.text((WIDTH - 225, 110), "SEAM DEVIATION", fill=(74, 222, 128, 255))
    bdraw.text((WIDTH - 225, 130), "+2.4 DEG IN", fill=(255, 255, 255, 255))

    im.paste(beam_layer, (0, 0), beam_layer)
    return np.array(im.convert("RGB"))


def main():
    generators = [
        ("stadium_night.mp4", create_realistic_stadium_night),
        ("golden_stadium.mp4", create_realistic_golden_stadium),
        ("fast_bowling.mp4", create_realistic_ball_spin),
        ("cyber_matrix.mp4", create_realistic_cyber_analytics),
    ]

    for filename, func in generators:
        out_path = os.path.join(OUTPUT_DIR, filename)
        print(f"Rendering photorealistic {filename} ({NUM_FRAMES} frames @ {FPS}fps)...")
        frames = []
        for f in range(NUM_FRAMES):
            t_norm = f / NUM_FRAMES
            frame = func(t_norm)
            frames.append(frame)
        
        imageio.mimsave(out_path, frames, fps=FPS, codec="libx264", quality=9)
        size_kb = os.path.getsize(out_path) / 1024
        print(f"Saved: {out_path} ({size_kb:.1f} KB)")

    # Update default hero_cricket.mp4
    import shutil
    shutil.copy(os.path.join(OUTPUT_DIR, "stadium_night.mp4"), os.path.join(OUTPUT_DIR, "hero_cricket.mp4"))
    print("Updated default hero_cricket.mp4.")

if __name__ == "__main__":
    main()
