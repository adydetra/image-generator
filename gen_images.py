# gen_images.py
# Generate gambar PNG random (RGB) tanpa dependency eksternal.
# Output folder di-hardcode; jeda antar export bisa diatur (--delay).

import os
import random
import argparse
import struct
import zlib
import binascii
import time
from datetime import datetime

# ======================
# OUTPUT FOLDER (DEFAULT, DAPAT DIOVERRIDE LEWAT CLI)
# ======================
DEFAULT_OUTDIR = r"D:\Dewa\Nuxt\bdg-lights-shadow-photobooth\public\img\touchdesigner-result"

# ======================
# Util: Tulis PNG (RGB 8-bit, no alpha)
# ======================
def _png_chunk(typ: bytes, data: bytes) -> bytes:
    crc = binascii.crc32(typ)
    crc = binascii.crc32(data, crc) & 0xffffffff
    return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", crc)

def save_png(path, width, height, rgb_iter):
    row_bytes = width * 3
    raw = bytearray()
    it = iter(rgb_iter)
    for _y in range(height):
        raw.append(0)  # filter type 0 (None)
        for _x in range(width):
            r, g, b = next(it)
            raw += bytes((r & 255, g & 255, b & 255))
    compressed = zlib.compress(bytes(raw), level=6)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # RGB8
    srgb = b"\x00"  # intent=Perceptual

    png = bytearray()
    png += sig
    png += _png_chunk(b"IHDR", ihdr)
    png += _png_chunk(b"sRGB", srgb)
    png += _png_chunk(b"IDAT", compressed)
    png += _png_chunk(b"IEND", b"")

    with open(path, "wb") as f:
        f.write(png)

# ======================
# Generator Pola
# ======================
def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def pattern_noise(w, h, rng):
    for _y in range(h):
        for _x in range(w):
            yield (rng.randint(0,255), rng.randint(0,255), rng.randint(0,255))

def pattern_stripes(w, h, rng):
    base = [rng.randint(0, 255) for _ in range(3)]
    stripe_w = rng.randint(max(8, w // 32), max(9, w // 8))
    for y in range(h):
        for x in range(w):
            k = (x // stripe_w) % 2
            yield (clamp(base[0] + (60 if k else -30)),
                   clamp(base[1] + (60 if k else -30)),
                   clamp(base[2] + (60 if k else -30)))

def pattern_checker(w, h, rng):
    csize = rng.randint(max(8, min(w, h)//32), max(9, min(w, h)//8))
    c1 = (rng.randint(0,255), rng.randint(0,255), rng.randint(0,255))
    c2 = (255 - c1[0], 255 - c1[1], 255 - c1[2])
    for y in range(h):
        for x in range(w):
            cx = (x // csize) % 2
            cy = (y // csize) % 2
            yield c1 if (cx ^ cy) == 0 else c2

def pattern_circle(w, h, rng):
    cx, cy = rng.randint(w//4, 3*w//4), rng.randint(h//4, 3*h//4)
    rmax = rng.randint(min(w, h)//6, min(w, h)//3)
    bg = (rng.randint(0,255), rng.randint(0,255), rng.randint(0,255))
    fg = (rng.randint(0,255), rng.randint(0,255), rng.randint(0,255))
    rr = rmax * rmax
    for y in range(h):
        dy = y - cy
        for x in range(w):
            dx = x - cx
            yield fg if (dx*dx + dy*dy) <= rr else bg

def pattern_gradient(w, h, rng):
    c1 = (rng.randint(0,255), rng.randint(0,255), rng.randint(0,255))
    c2 = (rng.randint(0,255), rng.randint(0,255), rng.randint(0,255))
    vertical = rng.choice([True, False])
    if vertical:
        for y in range(h):
            t = y / (h - 1) if h > 1 else 0
            r = int(c1[0]*(1-t) + c2[0]*t)
            g = int(c1[1]*(1-t) + c2[1]*t)
            b = int(c1[2]*(1-t) + c2[2]*t)
            for _x in range(w):
                yield (r, g, b)
    else:
        for y in range(h):
            for x in range(w):
                t = x / (w - 1) if w > 1 else 0
                r = int(c1[0]*(1-t) + c2[0]*t)
                g = int(c1[1]*(1-t) + c2[1]*t)
                b = int(c1[2]*(1-t) + c2[2]*t)
                yield (r, g, b)

def pattern_digits(width, height, text, fg=(255, 255, 255), bg=(0, 0, 0)):
    glyphs = {
        '0': [
            "01110",
            "10001",
            "10011",
            "10101",
            "11001",
            "10001",
            "01110",
        ],
        '1': [
            "00100",
            "01100",
            "00100",
            "00100",
            "00100",
            "00100",
            "01110",
        ],
        '2': [
            "01110",
            "10001",
            "00001",
            "00010",
            "00100",
            "01000",
            "11111",
        ],
        '3': [
            "01110",
            "10001",
            "00001",
            "00110",
            "00001",
            "10001",
            "01110",
        ],
        '4': [
            "00010",
            "00110",
            "01010",
            "10010",
            "11111",
            "00010",
            "00010",
        ],
        '5': [
            "11111",
            "10000",
            "11110",
            "00001",
            "00001",
            "10001",
            "01110",
        ],
        '6': [
            "00110",
            "01000",
            "10000",
            "11110",
            "10001",
            "10001",
            "01110",
        ],
        '7': [
            "11111",
            "00001",
            "00010",
            "00100",
            "01000",
            "01000",
            "01000",
        ],
        '8': [
            "01110",
            "10001",
            "10001",
            "01110",
            "10001",
            "10001",
            "01110",
        ],
        '9': [
            "01110",
            "10001",
            "10001",
            "01111",
            "00001",
            "00010",
            "01100",
        ],
    }

    if not text:
        text = "0"

    glyph_w = len(next(iter(glyphs.values()))[0])
    glyph_h = len(next(iter(glyphs.values())))
    spacing = 1
    base_width = len(text) * glyph_w + max(0, len(text) - 1) * spacing

    scale_x = max(1, width // max(1, base_width))
    scale_y = max(1, height // glyph_h)
    scale = max(1, min(scale_x, scale_y))

    draw_width = base_width * scale
    draw_height = glyph_h * scale
    offset_x = max(0, (width - draw_width) // 2)
    offset_y = max(0, (height - draw_height) // 2)

    for y in range(height):
        inside_y = offset_y <= y < offset_y + draw_height
        gy = (y - offset_y) // scale if inside_y and scale else 0
        for x in range(width):
            color = bg
            if inside_y and offset_x <= x < offset_x + draw_width:
                bx = (x - offset_x) // scale
                cursor = 0
                for idx, ch in enumerate(text):
                    glyph = glyphs.get(ch, glyphs['0'])
                    char_start = idx * (glyph_w + spacing)
                    if char_start <= bx < char_start + glyph_w:
                        gx = bx - char_start
                        if glyph[gy][gx] == '1':
                            color = fg
                        break
                    cursor = char_start + glyph_w
            yield color


PATTERNS = {
    'noise': pattern_noise,
    'stripes': pattern_stripes,
    'checker': pattern_checker,
    'circle': pattern_circle,
    'gradient': pattern_gradient,
}

def pick_pattern(name, rng):
    if name == 'random':
        return rng.choice(list(PATTERNS.values()))
    return PATTERNS.get(name, pattern_noise)

# ======================
# Main
# ======================
def main():
    ap = argparse.ArgumentParser(description="Generate gambar PNG random tanpa dependency eksternal.")
    ap.add_argument("--count", "-n", type=int, default=1, help="Jumlah gambar.")
    ap.add_argument("--width", type=int, default=1920, help="Lebar px.")
    ap.add_argument("--height", type=int, default=1080, help="Tinggi px.")
    ap.add_argument("--pattern", default="random",
                    choices=["random", "noise", "stripes", "checker", "circle", "gradient", "digits"],
                    help="Jenis pola.")
    ap.add_argument("--seed", type=int, default=None, help="Seed RNG (opsional).")
    ap.add_argument("--delay", type=float, default=5.0, help="Jeda detik antar export.")
    ap.add_argument("--output", "-o", default=DEFAULT_OUTDIR, help="Folder tujuan output.")
    args = ap.parse_args()

    if args.count <= 0 or args.width <= 0 or args.height <= 0:
        raise SystemExit("count/width/height harus > 0.")

    outdir = os.path.abspath(args.output)
    os.makedirs(outdir, exist_ok=True)
    rng = random.Random(args.seed if args.seed is not None else datetime.now().timestamp())
    pat_func = None if args.pattern == 'digits' else pick_pattern(args.pattern, rng)

    digits = max(4, len(str(args.count)))
    for i in range(1, args.count + 1):
        label = f"{i:0{digits}d}"
        if args.pattern == 'random':
            pat_func = pick_pattern('random', rng)
        if args.pattern == 'digits':
            filename = f"{label}.png"
            pixels = pattern_digits(args.width, args.height, label)
        else:
            filename = f"img_{label}.png"
            pixels = pat_func(args.width, args.height, rng)
        outpath = os.path.join(outdir, filename)
        save_png(outpath, args.width, args.height, pixels)
        print(f"SAVED: {outpath}")
        if i < args.count and args.delay > 0:
            time.sleep(args.delay)

    print(f"Done. Output folder: {outdir}")

if __name__ == "__main__":
    main()
