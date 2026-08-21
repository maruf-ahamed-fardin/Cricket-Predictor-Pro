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
NUM_FRAMES = 75  # 3.0 second smooth cinematic loop

def make_cinematic_loop(image_path, out_mp4_path, motion_type="zoom_pan"):
    src_img = Image.open(image_path).convert("RGB")
    src_w, src_h = src_img.size
    
    # Save a copy as high-res poster
    poster_name = os.path.splitext(os.path.basename(out_mp4_path))[0] + "_poster.jpg"
    src_img.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS).save(os.path.join(POSTER_DIR, poster_name), quality=92)

    frames = []
    
    for f in range(NUM_FRAMES):
        t = f / NUM_FRAMES  # 0 to 1
        # Smooth cosine cycle 0 -> 1 -> 0 for perfect seamless loop!
        t_cycle = 0.5 - 0.5 * math.cos(t * 2 * math.pi)

        if motion_type == "drone_fly":
            # Smooth slow drone push-in + subtle horizontal pan
            zoom = 1.0 + 0.10 * t_cycle
            pan_x = (t_cycle - 0.5) * 60
            pan_y = (t_cycle - 0.5) * 30
        elif motion_type == "pan_horizontal":
            # Smooth horizontal pan
            zoom = 1.06 + 0.05 * t_cycle
            pan_x = (t_cycle - 0.5) * 90
            pan_y = math.sin(t * 2 * math.pi) * 15
        elif motion_type == "action_shimmer":
            # Action shot with lens flare breathing
            zoom = 1.03 + 0.06 * t_cycle
            pan_x = (t_cycle - 0.5) * 40
            pan_y = (t_cycle - 0.5) * 20
        else: # "macro_drift"
            zoom = 1.05 + 0.08 * t_cycle
            pan_x = (t_cycle - 0.5) * 50
            pan_y = (t_cycle - 0.5) * 25

        # Compute crop box in source image
        crop_w = int(src_w / zoom)
        crop_h = int(src_h / zoom)
        
        center_x = (src_w / 2) + pan_x
        center_y = (src_h / 2) + pan_y

        left = max(0, min(src_w - crop_w, int(center_x - crop_w / 2)))
        top = max(0, min(src_h - crop_h, int(center_y - crop_h / 2)))
        right = left + crop_w
        bottom = top + crop_h

        cropped = src_img.crop((left, top, right, bottom))
        resized = cropped.resize((TARGET_W, TARGET_H), Image.Resampling.BILINEAR)

        # Subtle cinematic lighting modulation (breathing light flare)
        brightness_mod = 1.0 + 0.05 * math.sin(t * 2 * math.pi)
        enhancer = ImageEnhance.Brightness(resized)
        frame_img = enhancer.enhance(brightness_mod)

        frames.append(np.array(frame_img))

    imageio.mimsave(out_mp4_path, frames, fps=FPS, codec="libx264", quality=9)
    size_kb = os.path.getsize(out_mp4_path) / 1024
    print(f"Generated: {out_mp4_path} ({size_kb:.1f} KB)")


def main():
    videos = [
        ("stadium_night_real_1787338237067.jpg", "stadium_night.mp4", "drone_fly"),
        ("golden_stadium_real_1787338254922.jpg", "golden_stadium.mp4", "pan_horizontal"),
        ("cricket_match_action_1787338274979.jpg", "fast_bowling.mp4", "action_shimmer"),
        ("cricket_ball_seam_1787338291914.jpg", "cyber_matrix.mp4", "macro_drift"),
    ]

    for img_name, out_name, motion in videos:
        img_path = os.path.join(ARTIFACTS_DIR, img_name)
        out_path = os.path.join(OUTPUT_DIR, out_name)
        if os.path.exists(img_path):
            make_cinematic_loop(img_path, out_path, motion)
        else:
            print(f"Image not found: {img_path}")

    # Set stadium_night.mp4 as hero_cricket.mp4
    import shutil
    shutil.copy(os.path.join(OUTPUT_DIR, "stadium_night.mp4"), os.path.join(OUTPUT_DIR, "hero_cricket.mp4"))
    # Also default poster
    shutil.copy(os.path.join(POSTER_DIR, "stadium_night_poster.jpg"), os.path.join(POSTER_DIR, "hero_poster.jpg"))
    print("Default hero_cricket.mp4 and hero_poster.jpg updated.")

if __name__ == "__main__":
    main()
