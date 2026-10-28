"""POV edit of the Hi-fi V1 recording: the camera darts between the four looping GIFs
the way a new member's eyes would, then pulls back out."""
import sys, subprocess, math, numpy as np
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 1276, 868, 30
AR = W / H
# (out start, src start, src end): the banner and scroll down, then the still stretches between
# the accidental blue selections (3.4-4.3s and 5.0-5.6s) and a pop-up at 17.4s, which never make the cut
SEGS = [(0.0, 13.3, 16.0), (2.7, 5.7, 10.15), (7.15, 0.0, 3.3), (10.45, 16.1, 17.3), (11.65, 17.55, 18.1)]
DUR = 12.2
WIDE = (638, 434, 1276)
S1, S2 = (351, 280, 700), (927, 280, 700)
S3, S4 = (351, 630, 700), (927, 630, 700)
# eyes dart between the GIFs, faster each time; cuts between stretches land mid-move
KEYS = [(0.0, WIDE), (2.7, (638, 434, 1236)), (3.3, S1), (4.3, S1), (4.8, S4), (5.6, S4),
        (6.0, S2), (6.4, S2), (6.75, S3), (7.0, S3), (7.3, S1), (7.8, S1), (8.05, S4), (8.4, S4),
        (8.6, S2), (8.9, S2), (9.1, S3), (9.5, S3), (10.5, WIDE), (DUR, (638, 434, 1240))]
FADE = 0.3

def ease(k): return 4*k*k*k if k < .5 else 1 - (-2*k + 2)**3 / 2
def cam(t):
    t = min(max(t, 0), DUR)
    for (t0, a), (t1, b) in zip(KEYS, KEYS[1:]):
        if t0 <= t <= t1:
            k = (t - t0) / (t1 - t0)
            # drifts (the slow push-ins) stay linear, eye darts get an ease
            k = k if (t1 - t0) > 2 else ease(k)
            cx = a[0] + (b[0] - a[0]) * k; cy = a[1] + (b[1] - a[1]) * k
            w = math.exp(math.log(a[2]) + (math.log(b[2]) - math.log(a[2])) * k)
            h = w / AR
            cx = min(max(cx, w/2), W - w/2); cy = min(max(cy, h/2), H - h/2)
            return (cx - w/2, cy - h/2, cx + w/2, cy + h/2)
    return (0, 0, W, H)

def src_time(t):
    for o, s0, s1 in reversed(SEGS):
        if t >= o: return min(s0 + (t - o), s1 - 1/FPS)

dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
idx, cur = -1, None
def frame(i):
    global idx, cur
    while idx < i:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: return cur
        cur = Image.frombytes('RGB', (W, H), buf); idx += 1
    return cur
BG = np.array([253, 250, 252], np.float32)
n = int(DUR * FPS)
for f in range(n):
    t = f / FPS
    img = frame(round(src_time(t) * FPS))
    a = np.asarray(img.resize((W, H), Image.LANCZOS, box=cam(t)), np.float32)
    fade = min(1, t / FADE, (DUR - t) / FADE)
    if fade < 1: a = a * fade + BG * (1 - fade)
    enc.stdin.write(a.clip(0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); dec.kill()
