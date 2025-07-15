#test_utils.py
import os
import sys
import shutil
import random
import math
import pathlib
import urllib.request
from typing import Tuple, List

from PIL import Image, ImageDraw
import piexif
import numpy as np

try:
    import ffmpeg  # type: ignore
except ImportError as e:
    msg = f"The 'ffmpeg' module is required but not installed.\n"
    msg += f"You can install it with: pip install ffmpeg-python\nDetails: {e}"
    print(msg)
    raise SystemExit(1)

# --------------------------
# Image Generation Utility
# --------------------------

def generate_background_color(index: int) -> Tuple[int, int, int]:
    hue = (index * 0.15) % 1.0
    import colorsys
    rgb = colorsys.hsv_to_rgb(hue, 0.3, 0.95)
    return tuple(int(x * 255) for x in rgb)


def invert_color(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return tuple(255 - x for x in rgb)


def draw_ammonite_spiral(draw, center, max_radius, revolutions, color, line_width=3):
    points = []
    a = 1.0
    b = 0.15

    for angle_deg in range(0, int(360 * revolutions), 2):
        angle = math.radians(angle_deg)
        r = a * math.exp(b * angle)
        if r > max_radius:
            break
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))

    if len(points) > 1:
        draw.line(points, fill=color, width=line_width)


def build_ammonite_img(
    bg_color_index: int,
    size=(600, 600),
    grid_size=(3, 3)
) -> Image.Image:
    cols, rows = grid_size
    bg_color = generate_background_color(bg_color_index)
    pattern_color = invert_color(bg_color)

    img = Image.new("RGB", size, bg_color)
    draw = ImageDraw.Draw(img)

    cell_w = size[0] // cols
    cell_h = size[1] // rows
    max_radius = min(cell_w, cell_h) // 2 - 10

    for row in range(rows):
        for col in range(cols):
            center_x = col * cell_w + cell_w // 2
            center_y = row * cell_h + cell_h // 2
            draw_ammonite_spiral(draw, (center_x, center_y), max_radius, revolutions=3.5, color=pattern_color, line_width=2)

    return img


def generate_random_image(width, height):
    bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    for _ in range(10):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)

        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            continue

        ux, uy = dx / length, dy / length
        perp_x, perp_y = -uy, ux
        base_half_width = 10

        base_left = (x2 + perp_x * base_half_width, y2 + perp_y * base_half_width)
        base_right = (x2 - perp_x * base_half_width, y2 - perp_y * base_half_width)
        triangle = [(x1, y1), base_left, base_right]

        fill_color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        draw.polygon(triangle, fill=fill_color)

    return img


# --------------------------
# File saving utility
# --------------------------

def save_image_with_exif(img: Image.Image, filename: pathlib.Path, date_str="2024:07:07 12:00:00", format="JPEG"):
    exif_dict = {"0th": {}, "Exif": {}}
    encoded = date_str.encode('ascii')
    exif_dict["0th"][piexif.ImageIFD.DateTime] = encoded
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = encoded
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = encoded
    exif_bytes = piexif.dump(exif_dict)

    img.save(filename, format=format, exif=exif_bytes)
    print(f"{format} file created: {filename}")


def save_image_png(img: Image.Image, filename: pathlib.Path):
    img.save(filename, "PNG")
    print(f"PNG file created: {filename}")


def save_movie(frames: List[Image.Image], filename: pathlib.Path, date_str="2024-07-08T12:00:00", fps=10):
    frame_arrays = [np.array(img.convert("RGB")) for img in frames]
    height, width, _ = frame_arrays[0].shape

    process = (
        ffmpeg
        .input("pipe:", format="rawvideo", pix_fmt="rgb24", s=f"{width}x{height}", framerate=fps)
        .output(filename, pix_fmt="yuv420p", vcodec="libx264", movflags="+faststart", metadata=f"creation_time={date_str}")
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )

    for frame in frame_arrays:
        process.stdin.write(frame.tobytes())

    process.stdin.close()
    process.wait()
    print(f"Video file created: {filename}")


# --------------------------
# Batch creation of test files
# --------------------------

def create_test_files(output_dir: pathlib.Path):
    print(f"def create_test_files({output_dir})")
    output_dir.mkdir(exist_ok=True)

    # 使用例
    save_image_with_exif(img=build_ammonite_img(bg_color_index=1), filename=os.path.join(output_dir, "ammonite_001.jpg"), date_str="2024:07:01 12:00:00", format="JPEG")
    save_image_with_exif(img=build_ammonite_img(bg_color_index=2), filename=os.path.join(output_dir, "ammonite_002.jpg"), date_str="2024:07:02 12:00:00", format="JPEG")
    save_image_with_exif(img=build_ammonite_img(bg_color_index=3), filename=os.path.join(output_dir, "ammonite_003.jpg"), date_str="2024:07:03 12:00:00", format="JPEG")
    save_image_with_exif(img=build_ammonite_img(bg_color_index=4), filename=os.path.join(output_dir, "ammonite_004.jpg"), date_str="2024:07:04 12:00:00", format="JPEG")
    save_image_with_exif(img=build_ammonite_img(bg_color_index=5), filename=os.path.join(output_dir, "ammonite_005.jpg"), date_str="2024:07:05 12:00:00", format="JPEG")
    save_image_with_exif(img=build_ammonite_img(bg_color_index=6), filename=os.path.join(output_dir, "ammonite_006.jpg"), date_str="2024:07:06 12:00:00", format="JPEG")
    save_image_png(img=build_ammonite_img(bg_color_index=7), filename=os.path.join(output_dir, "ammonite_007.png"))
    save_image_with_exif(img=build_ammonite_img(bg_color_index=8), filename=os.path.join(output_dir, "ammonite_008.tif"), date_str="2024:06:01 12:00:00", format="JPEG")
    save_image_with_exif(img=build_ammonite_img(bg_color_index=9), filename=os.path.join(output_dir, "ammonite_009.tif"), date_str="2024:06:02 12:00:00", format="TIFF")
    save_image_with_exif(img=build_ammonite_img(bg_color_index=10), filename=os.path.join(output_dir, "ammonite_010.tif"), date_str="2024:06:03 12:00:00", format="TIFF")
    width = 4000
    height = 3000
    save_image_with_exif(img=generate_random_image(width, height), filename=os.path.join(output_dir, "sample_001.jpg"), date_str="2024:05:01 12:00:00", format="JPEG")
    save_image_with_exif(img=generate_random_image(width, height), filename=os.path.join(output_dir, "sample_002.tif"), date_str="2024:05:02 12:00:00", format="TIFF")

    # Generate one image
    img = generate_random_image(640, 480)

    # Copy the same image to 30 frames to create a list for a video
    frames = [img.copy() for _ in range(60)]
    save_movie(frames, filename=os.path.join(output_dir , "sample_movie.mp4"), date_str="2024-07-08 12:00:00", fps=30)

##
# @brief        After displaying the message string, execute sys.exit(1).
# @param[in]    filename        : target file name [type str]
# @retval       none            : 
def die_print(msg: str) -> None:
    print(msg)
    sys.exit(NG_VAL)

