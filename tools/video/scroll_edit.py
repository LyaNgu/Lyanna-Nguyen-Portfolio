"""Hi-fi V1 clip: a gentle eased scroll from the section heading down to the four step cards,
then a steady hold while every GIF plays at once.

The recording's own scroll jumps in wheel steps, so the scroll is rebuilt: live frames from the
settled view slide down under the sticky nav, with the heading strip filled from a still frame
taken 100px higher up the page."""
import sys, subprocess, numpy as np
SRC, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 1276, 868, 30
NAV = 80          # sticky nav height, stays put while the page moves
LIFT = 100        # the heading view sits this far above the settled view
CARDS = 100       # first row of the step cards in the settled view
HEAD_T = 15.4     # a still frame of the heading view
# (out start, src start, src end): stretches of the settled view, skipping the accidental blue
# selections at 3.4-4.3s and 5.0-5.6s
SEGS = [(0.0, 5.7, 10.15), (4.45, 0.0, 3.3)]
DUR = 7.75
SCROLL = (0.6, 2.0)
FADE = 0.25

def grab(t):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', str(t), '-i', SRC, '-frames:v', '1',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3)
head = grab(HEAD_T)

def ease(k): return 4*k*k*k if k < .5 else 1 - (-2*k + 2)**3 / 2
def lift(t):
    k = min(max((t - SCROLL[0]) / (SCROLL[1] - SCROLL[0]), 0), 1)
    return LIFT * (1 - ease(k))
def src_time(t):
    for o, s0, s1 in reversed(SEGS):
        if t >= o: return min(s0 + (t - o), s1 - 1/FPS)

def shift(live, d):
    # page rows above the cards (the heading, and the strip half-hidden under the nav) always
    # come from the still, so no clipped text slides into view
    out = np.empty_like(live)
    out[:NAV] = head[:NAV]      # the nav is see-through; the still has blank page behind it
    out[CARDS + d:] = live[CARDS:H - d]
    out[NAV:CARDS + d] = head[NAV + LIFT - d:CARDS + LIFT]
    return out.astype(np.float32)
def compose(live, o):
    # subpixel scroll: blend the two nearest whole-pixel offsets
    lo = int(o); f = o - lo
    if f < 0.01: return shift(live, lo)
    return shift(live, lo) * (1 - f) + shift(live, lo + 1) * f

dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
# the stretches run out of order, so keep the decoded frames (the source is short)
frames, idx = {}, -1
def frame(i):
    global idx
    while idx < i:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        idx += 1; frames[idx] = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    return frames[min(i, idx)]
BG = np.array([253, 250, 252], np.float32)
for f in range(int(DUR * FPS)):
    t = f / FPS
    a = compose(frame(round(src_time(t) * FPS)), lift(t))
    fade = min(1, t / FADE, (DUR - t) / FADE)
    if fade < 1: a = a * fade + BG * (1 - fade)
    enc.stdin.write(a.clip(0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); dec.kill()
