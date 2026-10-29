"""Decision 2 "Chose" clip: a new member clicks through the four final steps, then heads for
"Join Our Discord". A light zoom keeps the step list and its screenshot in view together, and a
soft ring marks each click (the last one is implied; the recording only hovers the button)."""
import sys, subprocess, math, numpy as np
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 1280, 872, 30
AR = W / H
# (out start, src start, src end): the second, in-order pass through the steps, skipping two
# stretches where the cursor sits still
SEGS = [(0.0, 27.6, 33.8), (6.2, 34.6, 37.9), (9.5, 38.7, 41.5)]
DUR = 12.3
WIDE = (640, 436, 1280)
UPPER = (645, 0, 1208)     # 1.06x: keeps the active-step bar and the whole screenshot in frame
LOWER = (645, 872, 1208)   # the same zoom, drifted down for step 4 (clamped to the frame)
KEYS = [(0.0, WIDE), (0.4, WIDE), (1.6, UPPER), (6.4, UPPER), (7.6, LOWER), (9.6, LOWER),
        (10.9, WIDE), (DUR, WIDE)]
# (out time, x, y in the recording)
CLICKS = [(1.75, 173, 300), (4.95, 234, 449), (8.15, 235, 594), (11.2, 636, 812)]
RING = np.array([224, 154, 82], np.float32)   # --wood-light
FADE = 0.3
BG = np.array([255, 255, 255], np.float32)

def ease(k): return 4*k*k*k if k < .5 else 1 - (-2*k + 2)**3 / 2
def cam(t):
    t = min(max(t, 0), DUR)
    for (t0, a), (t1, b) in zip(KEYS, KEYS[1:]):
        if t0 <= t <= t1:
            k = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1
            cx = a[0] + (b[0] - a[0]) * k; cy = a[1] + (b[1] - a[1]) * k
            w = math.exp(math.log(a[2]) + (math.log(b[2]) - math.log(a[2])) * k); h = w / AR
            cx = min(max(cx, w/2), W - w/2); cy = min(max(cy, h/2), H - h/2)
            return (cx - w/2, cy - h/2, cx + w/2, cy + h/2)
    return (0, 0, W, H)
def src_time(t):
    for o, s0, s1 in reversed(SEGS):
        if t >= o: return min(s0 + (t - o), s1 - 1/FPS)

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
def ring(a, t, box):
    # an expanding, fading ring at each click, anti-aliased from a distance field
    sx = W / (box[2] - box[0])
    for tc, x, y in CLICKS:
        k = (t - tc) / 0.6
        if not 0 <= k <= 1: continue
        px, py = (x - box[0]) * sx, (y - box[1]) * sx
        r = (8 + 26 * (1 - (1 - k) ** 3)) * sx
        x0, x1 = int(max(px - r - 6, 0)), int(min(px + r + 6, W))
        y0, y1 = int(max(py - r - 6, 0)), int(min(py + r + 6, H))
        d = np.hypot(XX[y0:y1, x0:x1] - px, YY[y0:y1, x0:x1] - py)
        alpha = np.clip(1.8 - np.abs(d - r) / 1.6, 0, 1) * 0.9 * (1 - k)
        alpha = np.maximum(alpha, (d < r) * 0.16 * (1 - k))   # a faint fill inside the ring
        patch = a[y0:y1, x0:x1]
        a[y0:y1, x0:x1] = patch * (1 - alpha[..., None]) + RING * alpha[..., None]
    return a

dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
idx, cur = -1, None
def frame(i):
    global idx, cur
    while idx < i:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: return cur
        cur = Image.frombytes('RGB', (W, H), buf); idx += 1
    return cur
for f in range(int(DUR * FPS)):
    t = f / FPS
    box = cam(t)
    a = np.asarray(frame(round(src_time(t) * FPS)).resize((W, H), Image.LANCZOS, box=box), np.float32).copy()
    a = ring(a, t, box)
    fade = min(1, t / FADE, (DUR - t) / FADE)
    if fade < 1: a = a * fade + BG * (1 - fade)
    enc.stdin.write(a.clip(0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); dec.kill()
