"""Decision 3 "Chose" clip: a visitor opens a common drop's collector book and flips a page,
closes it, scrolls to the rare drops, then opens Trivia and flips through every rare page.
Wide view throughout; a soft ring marks each click. Idle waits between clicks are cut."""
import sys, subprocess, numpy as np
SRC, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 1348, 920, 30
# (out start, src start, src end, speed): each cut lands where the page and cursor are the same on
# both sides; the slow scroll down to the rare drops plays at 2.5x
SEGS = [(0.0, 1.2, 4.4, 1), (3.2, 5.2, 6.9, 1), (4.9, 7.2, 8.9, 1), (6.6, 9.2, 11.0, 1), (8.4, 11.0, 15.0, 2.5),
        (10.0, 15.6, 19.4, 1), (13.8, 19.9, 21.6, 1), (15.5, 22.0, 23.7, 1), (17.2, 24.0, 25.8, 1), (19.0, 26.3, 28.8, 1)]
DUR = 21.5
# (out time, x, y): open Find Me's, next page x2, close, open Trivia, next page x3, close
CLICKS = [(0.55, 394, 378), (3.55, 1136, 460), (5.25, 1136, 460), (7.95, 1062, 250), (11.65, 208, 528),
          (14.15, 1165, 468), (15.85, 1165, 468), (17.55, 1165, 468), (20.75, 1064, 248)]
RING = np.array([224, 154, 82], np.float32)   # --wood-light
FADE = 0.3
BG = np.array([255, 255, 255], np.float32)

def src_time(t):
    for o, s0, s1, v in reversed(SEGS):
        if t >= o: return min(s0 + (t - o) * v, s1 - 1/FPS)

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
def ring(a, t):
    for tc, x, y in CLICKS:
        k = (t - tc) / 0.6
        if not 0 <= k <= 1: continue
        r = 8 + 26 * (1 - (1 - k) ** 3)
        x0, x1 = int(max(x - r - 6, 0)), int(min(x + r + 6, W))
        y0, y1 = int(max(y - r - 6, 0)), int(min(y + r + 6, H))
        d = np.hypot(XX[y0:y1, x0:x1] - x, YY[y0:y1, x0:x1] - y)
        alpha = np.clip(1.8 - np.abs(d - r) / 1.6, 0, 1) * 0.9 * (1 - k)
        alpha = np.maximum(alpha, (d < r) * 0.16 * (1 - k))
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
