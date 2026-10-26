# AVARNETH startup — asset & timeline contract (internal, v1)

Single source of truth shared by the Python asset pipeline / preview renderer
and the Unity C# integration. Both sides MUST implement exactly these semantics.

## 1. Pixel grid

* All branding art is authored at **native art resolution** (1 art px).
* Startup composition canvas: **480 × 270 art px** (= 1920 × 1080 / 4).
* At 1920×1080 one art pixel = **4 screen pixels** (integer nearest-neighbour).
* Coordinates: origin top-left of the 480×270 canvas, **x right, y down**, integer art px.

## 2. Unity importable assets (package folder `05_Unity_Integration/Importable_Assets/`)

All files are native 1× PNG, RGBA, straight (non-premultiplied) alpha, sRGB.
Import as: Texture Type = Sprite (2D and UI), Sprite Mode = Single,
Filter Mode = Point (no filter), Generate Mip Maps = off, Compression = None,
Wrap = Clamp, Non-Power-of-2 = None, sRGB = on, Alpha Is Transparency = on,
Pixels Per Unit = 100, Mesh Type = Full Rect, Max Size >= 2048.

```
Importable_Assets/
  Layers/      AVE_*.png            (static layer sprites, one sprite per file)
  Frames/      AVE_<Seq>_<NN>.png   (flipbook frames, NN = 00..; one sprite per file)
  Particles/   AVE_Particle_<NN>.png
  Animation_Timeline.json           (copy of 04_Animated_Startup/Animation_Timeline.json)
```
Sprite paths inside the JSON are **relative to `Importable_Assets/`**, using forward
slashes, e.g. `"Layers/AVE_Emblem.png"`, `"Frames/AVE_EmblemTrace_07.png"`.
(No sprite sheets are needed in Unity: `TextureImporter.spritesheet` is obsolete in
Unity 6000.6; sheets are delivered separately in `04_Animated_Startup/SpriteSheets/`
for reference / other tools.)

## 3. Animation_Timeline.json (JsonUtility-compatible: objects + arrays only)

```json
{
  "schema": "avarneth.startup.timeline/1",
  "duration": 2.0,
  "canvasWidth": 480,
  "canvasHeight": 270,
  "pixelScaleAt1080p": 4,
  "contentBounds": { "x": 0, "y": 0, "width": 480, "height": 270 },
  "layers": [
    {
      "id": "emblem",
      "sprite": "Layers/AVE_Emblem.png",
      "frames": [],
      "frameStart": 0.0,
      "frameEnd": 0.0,
      "afterFrames": "hold",
      "x": 209, "y": 40,
      "order": 30,
      "keys": [
        { "t": 0.00, "alpha": 0.0, "dx": 0.0, "dy": 3.0, "ease": "linear" },
        { "t": 0.30, "alpha": 1.0, "dx": 0.0, "dy": 0.0, "ease": "outCubic" }
      ]
    }
  ],
  "particleSprites": [ "Particles/AVE_Particle_00.png" ],
  "particles": [
    { "sprite": 0, "t0": 1.15, "life": 0.6, "x": 240.0, "y": 180.0,
      "vx": 4.0, "vy": -20.0, "ay": 8.0, "alpha": 1.0,
      "fadeIn": 0.15, "fadeOut": 0.5 }
  ]
}
```

### 3.1 Layers

* Render order: ascending `order` (lower = further back). Ties: array order.
* Layer top-left (art px) at time t: `X = x + dx(t)`, `Y = y + dy(t)`, then
  **snap**: `Xs = floor(X + 0.5)`, `Ys = floor(Y + 0.5)` (never banker's rounding).
* Layer size = sprite pixel size (native). Every frame of a flipbook has the same size.
* `alpha(t)` multiplies the sprite's own alpha. Layer is not drawn when alpha <= 0.001.
* **Keys** (sorted by t, at least one key):
  * t <= first.t → first key values; t >= last.t → last key values.
  * between k and k+1: `u = (t - k.t) / (k1.t - k.t)`, `e = ease_{k1.ease}(u)`,
    value = `lerp(k.value, k1.value, e)` for alpha, dx, dy independently.
  * The `ease` of a key describes the segment **arriving at** that key.
* **Easing** (u in [0,1]):
  * `linear`: u
  * `inCubic`: u³
  * `outCubic`: 1 − (1 − u)³
  * `inOutCubic`: u < 0.5 ? 4u³ : 1 − (−2u + 2)³ / 2
  * `smooth`: u²(3 − 2u)
  * `step`: u < 1 ? 0 : 1
  * unknown → linear
* **Flipbook** (`frames` non-empty):
  * t < frameStart → layer hidden.
  * frameStart <= t < frameEnd → index `i = floor((t − frameStart) / (frameEnd − frameStart) × N)`, clamped to [0, N−1].
  * t >= frameEnd → `afterFrames == "hold"`: show last frame;
    `"sprite"`: show `sprite` (static); `"hide"`: hidden.
  * When `frames` is empty the layer always shows `sprite`.

### 3.1b Full-screen layers (revision 2)

* Optional layer field `"fullscreen": true` (missing = false). Such a layer is NOT placed on the
  pixel grid: its sprite is stretched over the whole screen (Unity: child of the overlay Canvas root,
  outside ArtRoot, anchors (0,0)-(1,1), offsets 0, drawn before ArtRoot), `x/y/dx/dy` are ignored,
  only `alpha(t)` applies. Used for the backdrop veil so it always covers 16:9, 16:10 and 21:9 screens.
* Its texture is a smooth gradient (no pixel art) and is imported with **Bilinear** filtering.
* Preview renderer: drawn stretched to the full 480x270 canvas (the sprite is 480x270).

### 3.2 Particles (baked, deterministic — identical in preview and Unity)

* Active while `t0 <= t < t0 + life`. Local `τ = t − t0`, `u = τ / life`.
* Position (centre, art px): `px = x + vx·τ`, `py = y + vy·τ + 0.5·ay·τ²`.
* Alpha: `alpha × fin × fout`, `fin = fadeIn > 0 ? min(1, u / fadeIn) : 1`,
  `fout = (fadeOut > 0 && u > 1 − fadeOut) ? max(0, (1 − u) / fadeOut) : 1`.
* Drawn top-left: `(floor(px + 0.5) − floor(w / 2), floor(py + 0.5) − floor(h / 2))`.
* Particles render above all layers whose `order` < 100, below layers with `order` >= 100.

### 3.3 Time

* `t` = seconds since `Play()`, advanced with `Time.unscaledDeltaTime` (each frame's delta
  clamped to a configurable max, default 0.1 s, so a load hitch cannot skip phase 1).
* At `t >= duration` the overlay is finished: everything hidden, completion raised once.
* Preview frame `i` is sampled at `t = i / fps`.

## 4. Unity overlay (runtime behaviour required by the brief)

* Own Canvas (Screen Space – Overlay, high sorting order, configurable), CanvasScaler
  Constant Pixel Size (scale factor 1), GraphicRaycaster; **no EventSystem** in the prefab.
* `ArtRoot` RectTransform 480×270, centred; its uniform `localScale` = art pixel size in
  screen px. Modes: `IntegerNearest` (default: round(Screen.height/270), reduced while the
  contentBounds would not fit the screen, min 1), `IntegerFloor`, `Continuous`
  (Screen.height/270, no integer snap).
* Children use anchor/pivot top-left (0,1); `anchoredPosition = (Xs, −Ys)`;
  `sizeDelta` = sprite native size.
* Optional full-screen transparent raycast blocker while playing; optional reference to an
  existing login `CanvasGroup` (interactable/blocksRaycasts off while playing, optional
  alpha reveal during the fade-out, original values always restored — also in OnDisable /
  OnDestroy). No Input-Manager / Input-System API (project may use either).
* After completion: stop updating, disable root GameObject (or destroy, configurable),
  fire `UnityEvent` + C# event once. Nothing keeps running.
* Never touches networking, Nakama, authentication, scenes, Product/Company name.
