"""Decision 2 "Chose" clip: a new member clicks through the four final steps, then heads for
"Join Our Discord". The view stays wide so the whole design is always in frame, and a soft ring
marks each click (the last one is implied; the recording only hovers the button)."""
import sys, subprocess, numpy as np
SRC, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 1276, 870, 30
# (out start, src start, src end): the scroll in and the stretches where the cursor sits still
# are left out
SEGS = [(0.0, 3.7, 8.0), (4.3, 8.4, 12.3), (8.2, 13.0, 18.8)]
DUR = 14.0
# (out time, x, y): Steps 1-4, then the implied click on Join Our Discord
CLICKS = [(1.42, 145, 170), (4.42, 268, 300), (7.22, 267, 451), (9.92, 291, 597), (13.05, 649, 811)]
RING = np.array([224, 154, 82], np.float32)   # --wood-light
FADE = 0.3
BG = np.array([255, 255, 255], np.float32)

def src_time(t):
    for o, s0, s1 in reversed(SEGS):
        if t >= o: return min(s0 + (t - o), s1 - 1/FPS)

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
def ring(a, t):
    # an expanding, fading ring at each click, anti-aliased from a distance field
    for tc, x, y in CLICKS:
        k = (t - tc) / 0.6
        if not 0 <= k <= 1: continue
        r = 8 + 26 * (1 - (1 - k) ** 3)
        x0, x1 = int(max(x - r - 6, 0)), int(min(x + r + 6, W))
        y0, y1 = int(max(y - r - 6, 0)), int(min(y + r + 6, H))
        d = np.hypot(XX[y0:y1, x0:x1] - x, YY[y0:y1, x0:x1] - y)
        alpha = np.clip(1.8 - np.abs(d - r) / 1.6, 0, 1) * 0.9 * (1 - k)
        alpha = np.maximum(alpha, (d < r) * 0.16 * (1 - k))   # a faint fill inside the ring
        a[y0:y1, x0:x1] = a[y0:y1, x0:x1] * (1 - alpha[..., None]) + RING * alpha[..., None]
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
        cur = np.frombuffer(buf, np.uint8).reshape(H, W, 3); idx += 1
    return cur
for f in range(int(DUR * FPS)):
    t = f / FPS
    a = ring(frame(round(src_time(t) * FPS)).astype(np.float32), t)
    fade = min(1, t / FADE, (DUR - t) / FADE)
    if fade < 1: a = a * fade + BG * (1 - fade)
    enc.stdin.write(a.clip(0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); dec.kill()
