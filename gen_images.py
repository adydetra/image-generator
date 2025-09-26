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
# OUTPUT FOLDER (HARD-CODED)
# ======================
OUTDIR = r"D:\Dewa\Nuxt\bdg-lights-shadow-photobooth\public\img\touchdesigner-result"

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
    ap.add_argument("--width", type=int, default=256, help="Lebar px.")
    ap.add_argument("--height", type=int, default=256, help="Tinggi px.")
    ap.add_argument("--pattern", default="random",
                    choices=["random", "noise", "stripes", "checker", "circle", "gradient"],
                    help="Jenis pola.")
    ap.add_argument("--seed", type=int, default=None, help="Seed RNG (opsional).")
    ap.add_argument("--delay", type=float, default=5.0, help="Jeda detik antar export.")
    args = ap.parse_args()

    if args.count <= 0 or args.width <= 0 or args.height <= 0:
        raise SystemExit("count/width/height harus > 0.")

    os.makedirs(OUTDIR, exist_ok=True)
    rng = random.Random(args.seed if args.seed is not None else datetime.now().timestamp())
    pat_func = pick_pattern(args.pattern, rng)

    digits = max(4, len(str(args.count)))
    for i in range(1, args.count + 1):
        if args.pattern == 'random':
            pat_func = pick_pattern('random', rng)
        filename = f"img_{i:0{digits}d}.png"
        outpath = os.path.join(OUTDIR, filename)
        pixels = pat_func(args.width, args.height, rng)
        save_png(outpath, args.width, args.height, pixels)
        print(f"SAVED: {outpath}")
        if i < args.count and args.delay > 0:
            time.sleep(args.delay)

    print(f"Done. Output folder: {OUTDIR}")

if __name__ == "__main__":
    main()
