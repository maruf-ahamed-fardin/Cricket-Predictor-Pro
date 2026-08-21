import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import imageio

ARTIFACTS_DIR = r"C:\Users\Fardin\.gemini\antigravity-ide\brain\98f5548b-6c5e-4b14-a8aa-ffaa55881cf8"
OUTPUT_DIR = r"c:\Users\Fardin\Desktop\model\app\static\videos"
POSTER_DIR = r"c:\Users\Fardin\Desktop\model\app\static\img"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(POSTER_DIR, exist_ok=True)

TARGET_W, TARGET_H = 1280, 720
FPS = 25
TOTAL_SECONDS = 10
TOTAL_FRAMES = FPS * TOTAL_SECONDS  # 250 frames!

# Load 4 Master High-Res 8K Photos
img_paths = {
    "stadium": os.path.join(ARTIFACTS_DIR, "stadium_night_real_1787338237067.jpg"),
    "action":  os.path.join(ARTIFACTS_DIR, "cricket_match_action_1787338274979.jpg"),
    "ball":    os.path.join(ARTIFACTS_DIR, "cricket_ball_seam_1787338291914.jpg"),
    "golden":  os.path.join(ARTIFACTS_DIR, "golden_stadium_real_1787338254922.jpg")
}

loaded_images = {}
for k, p in img_paths.items():
    if os.path.exists(p):
        loaded_images[k] = Image.open(p).convert("RGB")
    else:
        print(f"Warning: {p} not found")

def get_scene_frame(img, progress, pan_dir="left_right", zoom_range=(1.0, 1.08)):
    # progress in [0, 1]
    src_w, src_h = img.size
    z_start, z_end = zoom_range
    current_zoom = z_start + (z_end - z_start) * progress
    
    crop_w = int(src_w / current_zoom)
    crop_h = int(src_h / current_zoom)

    # Dynamic camera movement paths
    if pan_dir == "left_right":
        pan_x = (progress - 0.5) * (src_w * 0.08)
        pan_y = math.sin(progress * math.pi) * (src_h * 0.02)
    elif pan_dir == "right_left":
        pan_x = (0.5 - progress) * (src_w * 0.08)
        pan_y = -math.sin(progress * math.pi) * (src_h * 0.02)
    elif pan_dir == "push_tilt":
        pan_x = math.sin(progress * 2 * math.pi) * (src_w * 0.03)
        pan_y = (progress - 0.5) * (src_h * 0.06)
    else: # "curve_sweep"
        pan_x = math.cos(progress * math.pi) * (src_w * 0.06)
        pan_y = math.sin(progress * math.pi) * (src_h * 0.04)

    cx = (src_w / 2) + pan_x
    cy = (src_h / 2) + pan_y

    left = max(0, min(src_w - crop_w, int(cx - crop_w / 2)))
    top = max(0, min(src_h - crop_h, int(cy - crop_h / 2)))
    right = left + crop_w
    bottom = top + crop_h

    cropped = img.crop((left, top, right, bottom))
    return cropped.resize((TARGET_W, TARGET_H), Image.Resampling.BILINEAR)


def create_10s_master_montage():
    print(f"Rendering 10-Second Cinematic Cricket Montage ({TOTAL_FRAMES} frames @ {FPS}fps)...")
    
    # 4 scenes in 10 seconds:
    # Scene 1: Stadium Night (0s - 2.8s) -> 70 frames
    # Scene 2: Batsman Action (2.4s - 5.4s) -> 75 frames (overlap 10 frames)
    # Scene 3: Ball Seam (5.0s - 7.8s) -> 70 frames (overlap 10 frames)
    # Scene 4: Golden Sunlit Stadium (7.4s - 10.0s) -> 65 frames (overlap 10 frames)
    # Final crossfade loops back to Scene 1!

    scenes = [
        {"name": "stadium", "start_f": 0,   "end_f": 70,  "pan": "left_right", "zoom": (1.02, 1.10)},
        {"name": "action",  "start_f": 60,  "end_f": 135, "pan": "push_tilt",  "zoom": (1.08, 1.02)},
        {"name": "ball",    "start_f": 125, "end_f": 195, "pan": "right_left", "zoom": (1.03, 1.12)},
        {"name": "golden",  "start_f": 185, "end_f": 250, "pan": "curve_sweep", "zoom": (1.05, 1.11)},
    ]

    all_frames = []

    # Dynamic lighting overlay layer
    lens_flare = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(lens_flare)
    # Shimmering flare center
    fdraw.ellipse([TARGET_W//2 - 280, -100, TARGET_W//2 + 280, 200], fill=(255, 240, 200, 22))

    for f in range(TOTAL_FRAMES):
        t_global = f / TOTAL_FRAMES
        
        # Find which scenes are active at frame f
        active = []
        for s in scenes:
            if s["start_f"] <= f <= s["end_f"]:
                p = (f - s["start_f"]) / (s["end_f"] - s["start_f"])
                active.append((s, p))

        # Handle loop blend from end (golden) back to start (stadium)
        loop_fade_start = 238
        if f >= loop_fade_start:
            loop_p = (f - loop_fade_start) / (TOTAL_FRAMES - loop_fade_start)
            stadium_p = (f - loop_fade_start) / (scenes[0]["end_f"] - scenes[0]["start_f"])
            # Mix in beginning stadium frame
            stadium_img = get_scene_frame(loaded_images["stadium"], stadium_p, scenes[0]["pan"], scenes[0]["zoom"])
        else:
            loop_p = 0
            stadium_img = None

        if len(active) == 1:
            s, p = active[0]
            base_frame = get_scene_frame(loaded_images[s["name"]], p, s["pan"], s["zoom"])
        elif len(active) >= 2:
            # Crossfade transition between scene 1 and scene 2
            s1, p1 = active[0]
            s2, p2 = active[1]
            img1 = get_scene_frame(loaded_images[s1["name"]], p1, s1["pan"], s1["zoom"])
            img2 = get_scene_frame(loaded_images[s2["name"]], p2, s2["pan"], s2["zoom"])
            
            # Blend weight: ease-in-out cosine
            overlap_duration = s1["end_f"] - s2["start_f"]
            current_overlap_f = f - s2["start_f"]
            blend_ratio = current_overlap_f / max(1, overlap_duration)
            blend_weight = 0.5 - 0.5 * math.cos(blend_ratio * math.pi)
            
            base_frame = Image.blend(img1, img2, blend_weight)
        else:
            base_frame = get_scene_frame(loaded_images["golden"], 1.0)

        # Apply loop transition if near end
        if loop_p > 0 and stadium_img is not None:
            loop_weight = 0.5 - 0.5 * math.cos(loop_p * math.pi)
            base_frame = Image.blend(base_frame, stadium_img, loop_weight)

        # Add cinematic ambient atmosphere (floating glowing motes)
        frame_rgba = base_frame.convert("RGBA")
        mote_canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
        mdraw = ImageDraw.Draw(mote_canvas)
        
        # 35 floating dust/light motes
        for i in range(35):
            mx = int((i * 67 + f * 1.8) % TARGET_W)
            my = int((i * 43 + math.sin(f * 0.08 + i) * 25) % TARGET_H)
            alpha = int(45 + 35 * math.sin(f * 0.12 + i))
            sz = 2 + (i % 3)
            mdraw.ellipse([mx-sz, my-sz, mx+sz, my+sz], fill=(255, 255, 230, alpha))

        # Dynamic subtle light sweep
        sweep_x = int(math.sin(t_global * 4 * math.pi) * (TARGET_W * 0.3) + TARGET_W * 0.5)
        mdraw.ellipse([sweep_x - 300, -80, sweep_x + 300, 180], fill=(255, 245, 210, 18))

        frame_rgba.paste(mote_canvas, (0, 0), mote_canvas)

        # Cinematic color enhancement
        enhancer = ImageEnhance.Contrast(frame_rgba.convert("RGB"))
        frame_final = enhancer.enhance(1.06)

        all_frames.append(np.array(frame_final))

    out_mp4 = os.path.join(OUTPUT_DIR, "stadium_night.mp4")
    hero_mp4 = os.path.join(OUTPUT_DIR, "hero_cricket.mp4")
    
    imageio.mimsave(out_mp4, all_frames, fps=FPS, codec="libx264", quality=9)
    imageio.mimsave(hero_mp4, all_frames, fps=FPS, codec="libx264", quality=9)
    
    size_kb = os.path.getsize(hero_mp4) / 1024
    print(f"Saved 10s Master Video: {hero_mp4} ({size_kb:.1f} KB, {len(all_frames)} frames)")


def create_10s_single_theme(theme_name, img_key, out_filename):
    print(f"Rendering 10s Themed Video for {theme_name}...")
    img = loaded_images[img_key]
    all_frames = []
    
    # 2 camera movement passes (e.g. forward sweep then tilt pan) that loop seamlessly!
    for f in range(TOTAL_FRAMES):
        t = f / TOTAL_FRAMES
        # Smooth cyclical progress
        cycle = 0.5 - 0.5 * math.cos(t * 2 * math.pi)
        
        frame = get_scene_frame(img, cycle, "left_right", (1.0, 1.15))
        
        # Subtle lighting pulse
        pulse = 1.0 + 0.04 * math.sin(t * 4 * math.pi)
        frame = ImageEnhance.Brightness(frame).enhance(pulse)
        all_frames.append(np.array(frame))

    out_path = os.path.join(OUTPUT_DIR, out_filename)
    imageio.mimsave(out_path, all_frames, fps=FPS, codec="libx264", quality=9)
    print(f"Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


if __name__ == "__main__":
    create_10s_master_montage()
    create_10s_single_theme("Golden Stadium", "golden", "golden_stadium.mp4")
    create_10s_single_theme("Fast Bowling Match", "action", "fast_bowling.mp4")
    create_10s_single_theme("Cyber Ball Seam", "ball", "cyber_matrix.mp4")
    print("All 10-second cinematic videos rendered successfully!")
