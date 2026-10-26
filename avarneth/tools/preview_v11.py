"""V1.1 preview on the ORIGINAL bootstrap capture (visual mock-up, not a Unity recording).

Background = frames of Existing_Previews/Unity_Capture/Login-20s_COMPRESSED_REFERENCE.mp4 (12 fps, unchanged
pixels outside the retouched text boxes). Retouched for the mock-up only:
* LogoText "World of / Eckertengineering" removed (diffusion fill) and replaced by the AVARNETH header image
  at its RectTransform (x 56, y 86, 408 x 104 at the 1920x1080 reference);
* the remaining visible WOE names (news text, footer) removed and re-set in Liberation Sans (the font of the
  login TMP materials) with the PROPOSED replacement texts listed in V11_TEXT_CHANGES.md;
* while the startup plays, LogoAreaTopLeft (header + accent + 'PRIVATE ENTWICKLUNGSWELT') is hidden and fades in
  during the last 0.4 s - this is the recommended Inspector set-up (CanvasGroup on LogoAreaTopLeft assigned as
  'Login Canvas Group', 'Reveal Login During Fade Out' on); the login form stays visible under the veil.
A label in the frame marks it as a mock-up.
"""
from __future__ import annotations

import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import timeline_eval as te

REF = os.environ.get('AVARNETH_BOOTSTRAP_REF', '/home/user/ref_bootstrap/AVARNETH_Bootstrap_Claude_Reference')
CAPTURE = os.path.join(REF, 'Existing_Previews', 'Unity_Capture', 'Login-20s_COMPRESSED_REFERENCE.mp4')
LOGIN_PNG = os.path.join(REF, 'Existing_Previews', 'Unity_Capture', 'Login.png')
FONT = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
LABEL_FONT = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
W, H = 1920, 1080
CAP_FPS = 12

# boxes in 1920x1080 capture pixels (x0, y0, x1, y1) - measured on Login.png / the scene layout json
TITLE = (52, 84, 468, 192)            # LogoAreaTopLeft/LogoText (56,86 408x104) + margin
ACCENT = (52, 202, 124, 213)          # LogoAreaTopLeft/Accent (64x4 at y 206)
SUBTITLE = (52, 220, 320, 246)        # LogoAreaTopLeft/SubtitleText
NEWS = (52, 832, 470, 913)            # BreakingNewsPanelLeft/NewsBody lines 1-3
FOOTER = (52, 1022, 470, 1044)        # BottomCenterCopyright
HEADER_POS = (56, 86)

NEW_TEXT = [  # (text, x, top-of-ink y, size, colour) - proposals, see V11_TEXT_CHANGES.md
    ('Willkommen in AVARNETH: Veil of Embers.', 56, 837, 16, (221, 214, 196)),
    ('Login, Charakterverwaltung und Welteintritt werden', 56, 874, 16, (221, 214, 196)),
    ('weiterhin über den bestehenden Nakama-Server ausgeführt.', 56, 893, 16, (221, 214, 196)),
    ('© Eckertengineering · AVARNETH: Veil of Embers', 56, 1026, 15, (145, 138, 125)),
]
LABEL = 'VISUAL MOCKUP  ·  original bootstrap capture (12 fps) + AVARNETH V1.1 overlay & header composited  ·  not a Unity recording'


def decode(path, start=0.0, seconds=None, every=1):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(start), '-i', path]
    if seconds is not None:
        cmd += ['-t', str(seconds)]
    cmd += ['-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (W * H * 3)
    fr = np.frombuffer(raw, np.uint8)[:n * W * H * 3].reshape(n, H, W, 3)
    return fr[::every]


def lum(a):
    a = a.astype(np.float32)
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def text_masks(stack):
    """Static text masks: median over frames spread across the 20 s capture (text is static, the artwork
    behind it moves), thresholded and grown by 2 px to include anti-aliasing and shadows."""
    med = np.median(stack, axis=0)
    L = lum(med)
    out = {}
    for name, box, th in (('title', TITLE, 118), ('accent', ACCENT, 118), ('subtitle', SUBTITLE, 105),
                          ('news', NEWS, 112), ('footer', FOOTER, 96)):
        x0, y0, x1, y1 = box
        m = np.zeros((H, W), bool)
        m[y0:y1, x0:x1] = L[y0:y1, x0:x1] > th
        for _ in range(2):
            g = m.copy()
            g[1:] |= m[:-1]; g[:-1] |= m[1:]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]
            m = g
        out[name] = m
    return out


def inpaint(img, mask, box, iters=400):
    """Diffusion fill of the masked pixels inside box (Jacobi iterations of the 4-neighbour mean)."""
    x0, y0, x1, y1 = box
    x0, y0, x1, y1 = x0 - 4, y0 - 4, x1 + 4, y1 + 4
    reg = img[y0:y1, x0:x1].astype(np.float32)
    m = mask[y0:y1, x0:x1]
    if not m.any():
        return img
    known = ~m
    reg[m] = reg[known].mean(axis=0)
    for _ in range(iters):
        p = np.pad(reg, ((1, 1), (1, 1), (0, 0)), mode='edge')
        avg = (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]) * 0.25
        reg[m] = avg[m]
    out = img.copy()
    out[y0:y1, x0:x1] = np.clip(reg + 0.5, 0, 255).astype(np.uint8)
    return out


def draw_texts(img):
    pil = Image.fromarray(img)
    d = ImageDraw.Draw(pil)
    for text, x, top, size, colr in NEW_TEXT:
        f = ImageFont.truetype(FONT, size)
        off = f.getbbox('Wk')[1]
        d.text((x, top - off), text, font=f, fill=colr)
    return np.array(pil)


def draw_label(img):
    pil = Image.fromarray(img)
    d = ImageDraw.Draw(pil, 'RGBA')
    f = ImageFont.truetype(LABEL_FONT, 15)
    tw = d.textlength(LABEL, font=f)
    x = int(1220 - tw / 2)
    d.rectangle((x - 10, 8, x + tw + 10, 32), fill=(8, 9, 15, 175))
    d.text((x, 12), LABEL, font=f, fill=(246, 214, 140, 255))
    return np.array(pil)


def plates(frame, masks, header_rgba):
    """clean = LogoArea hidden (title/accent/subtitle removed); final = header shown + accent/subtitle kept."""
    base = frame
    for name, box in (('news', NEWS), ('footer', FOOTER)):
        base = inpaint(base, masks[name], box)
    base = draw_texts(base)
    final = inpaint(base, masks['title'], TITLE)
    clean = inpaint(final, masks['accent'], ACCENT)
    clean = inpaint(clean, masks['subtitle'], SUBTITLE)
    final = composite(final, header_rgba, *HEADER_POS)
    return clean, final


def composite(rgb, rgba, x, y):
    out = rgb.copy()
    h, w = rgba.shape[:2]
    a = rgba[..., 3:4].astype(np.float32) / 255.0
    reg = out[y:y + h, x:x + w].astype(np.float32)
    out[y:y + h, x:x + w] = np.clip(reg * (1 - a) + rgba[..., :3] * a + 0.5, 0, 255).astype(np.uint8)
    return out


def reveal(t, duration=2.0, seconds=0.4):
    """AvarnethStartupMath.RevealFactor (runtime): linear 0 -> 1 over the last `seconds`."""
    u = (t - (duration - seconds)) / seconds
    return 0.0 if u <= 0 else (1.0 if u >= 1 else u)


def overlay_rgba(tl, arr, t, scale):
    ov = te.render(tl, arr, t)
    return np.repeat(np.repeat(ov, scale, 0), scale, 1)


def render_preview(tl, arr, header2x, out_mp4, seconds=4.5, fps=60, stills=None):
    n_cap = int(np.ceil(seconds * CAP_FPS)) + 1
    frames = decode(CAPTURE, 0.0, seconds + 0.2)[:n_cap]
    masks = text_masks(decode(CAPTURE, 0.0, None, every=8))
    cache = {}
    scale = W // tl['canvasWidth']
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps),
           '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
           '-metadata', 'title=AVARNETH V1.1 - bootstrap matched preview (VISUAL MOCKUP on the original capture)', out_mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    saved = {}
    for i in range(int(round(seconds * fps))):
        t = i / fps
        ci = min(len(frames) - 1, int(t * CAP_FPS))
        if ci not in cache:
            cache.clear()
            cache[ci] = plates(frames[ci], masks, header2x)
        clean, final = cache[ci]
        r = reveal(t)
        bg = clean if r <= 0 else (final if r >= 1 else
                                   np.clip(clean * (1 - r) + final * r + 0.5, 0, 255).astype(np.uint8))
        img = composite(bg, overlay_rgba(tl, arr, t, scale), 0, 0) if t < tl['duration'] else bg
        img = draw_label(img)
        if stills and any(abs(t - s) < 0.5 / fps for s in stills):
            saved[round(t, 3)] = img
        p.stdin.write(np.ascontiguousarray(img).tobytes())
    p.stdin.close()
    assert p.wait() == 0
    return saved, masks, frames


if __name__ == '__main__':
    print('use v11_build.py', file=sys.stderr)
