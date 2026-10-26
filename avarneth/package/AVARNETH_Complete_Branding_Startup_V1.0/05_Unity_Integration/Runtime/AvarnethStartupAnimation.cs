// AVARNETH: VEIL OF EMBERS - startup branding overlay
// Copyright (c) Eckertengineering. All rights reserved.

using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace Eckertengineering.Avarneth.Branding
{
    /// <summary>What happens to the overlay GameObject once the animation has finished.</summary>
    public enum AvarnethStartupCompletionAction
    {
        /// <summary>Deactivate the overlay GameObject (it can be replayed with <see cref="AvarnethStartupAnimation.Play"/>).</summary>
        DisableGameObject = 0,
        /// <summary>Destroy the overlay GameObject.</summary>
        DestroyGameObject = 1,
    }

    /// <summary>Serialized binding of one timeline layer to its UI Image.</summary>
    [Serializable]
    public sealed class StartupLayerBinding
    {
        /// <summary>Layer id from the timeline.</summary>
        public string id;
        /// <summary>Image that renders the layer (anchor and pivot top-left).</summary>
        public Image image;
        /// <summary>Static sprite (may be null for flipbook layers that never show it).</summary>
        public Sprite sprite;
        /// <summary>Flipbook frames; empty for static layers.</summary>
        public Sprite[] frames;
        /// <summary>Flipbook start time (authored timeline seconds).</summary>
        public float frameStart;
        /// <summary>Flipbook end time (authored timeline seconds).</summary>
        public float frameEnd;
        /// <summary>What the layer shows after the flipbook.</summary>
        public StartupAfterFrames afterFrames;
        /// <summary>Top-left position in art pixels (origin top-left, y down).</summary>
        public Vector2Int position;
        /// <summary>Render order from the timeline (lower = further back).</summary>
        public int order;
        /// <summary>Animation keys sorted by time.</summary>
        public StartupKey[] keys;
    }

    /// <summary>
    /// Plays the AVARNETH startup branding overlay (about 2 s) on top of an existing login scene.
    /// It only drives its own UI Images and, optionally, the interactable/blocksRaycasts/alpha values of one
    /// login CanvasGroup, which are always restored. It never waits for, delays or replaces any login logic.
    /// Until <see cref="Play"/> runs, and whenever the component is disabled, nothing is drawn and no input is blocked.
    /// </summary>
    [DisallowMultipleComponent]
    [AddComponentMenu("Eckertengineering/AVARNETH Startup Animation")]
    public sealed class AvarnethStartupAnimation : MonoBehaviour, IPointerClickHandler
    {
        /// <summary>Default real-time duration in seconds.</summary>
        public const float DefaultDuration = 2f;
        /// <summary>Shortest allowed real-time duration in seconds.</summary>
        public const float MinDuration = 1f;
        /// <summary>Longest allowed real-time duration in seconds.</summary>
        public const float MaxDuration = 3f;

        private const string LogPrefix = "[AVARNETH Startup] ";

        private enum PlayState
        {
            Idle,
            Playing,
            Finished,
        }

        private struct LayerRuntime
        {
            public RectTransform rect;
            public bool hasStaticSprite;
            public int frameCount;
            public bool valid;
            public bool visible;
            public Sprite sprite;
            public int x;
            public int y;
            public float alpha;
        }

        private struct ParticleRuntime
        {
            public RectTransform rect;
            public int width;
            public int height;
            public bool valid;
            public bool visible;
            public int x;
            public int y;
            public float alpha;
        }

        [Header("Playback")]
        [Tooltip("Start playing automatically in Start().")]
        [SerializeField] private bool playOnStart = true;

        [Tooltip("Real-time length of the overlay in seconds. The authored timeline is stretched uniformly.")]
        [SerializeField, Range(MinDuration, MaxDuration)] private float duration = DefaultDuration;

        [Tooltip("Largest frame delta (seconds) that advances the animation, so a loading hitch cannot skip the opening.")]
        [SerializeField, Range(0.01f, 0.5f)] private float maxDeltaTime = 0.1f;

        [Tooltip("How the art pixel size is derived from the screen size.")]
        [SerializeField] private AvarnethPixelScaleMode scaleMode = AvarnethPixelScaleMode.IntegerNearest;

        [Tooltip("What happens to this GameObject when the animation has finished.")]
        [SerializeField] private AvarnethStartupCompletionAction completionAction = AvarnethStartupCompletionAction.DisableGameObject;

        [Header("Input")]
        [Tooltip("Use the transparent full-screen Image as raycast blocker while playing.")]
        [SerializeField] private bool blockInputWhilePlaying = true;

        [Tooltip("Skip the animation with a pointer click (requires an EventSystem in the scene; also blocks raycasts while playing).")]
        [SerializeField] private bool skipOnClick = false;

        [Tooltip("Transparent full-screen Image used as raycast blocker and click target.")]
        [SerializeField] private Image raycastBlocker;

        [Header("Login UI (optional)")]
        [Tooltip("Existing login CanvasGroup. Use one that the login code does not toggle itself (add a dedicated CanvasGroup to the login root if necessary).")]
        [SerializeField] private CanvasGroup loginCanvasGroup;

        [Tooltip("Hide the login CanvasGroup (alpha 0) while playing and fade it back in during the last Reveal Seconds.")]
        [SerializeField] private bool revealLoginDuringFadeOut = false;

        [Tooltip("Length of the login fade-in at the end of the animation (real seconds).")]
        [SerializeField, Min(0f)] private float revealSeconds = 0.4f;

        [Header("Events")]
        [Tooltip("Raised once when the animation has finished or was skipped.")]
        [SerializeField] private UnityEvent onCompleted = new UnityEvent();

        [Header("Timeline data (generated by Tools > AVARNETH > Startup)")]
        [SerializeField] private float authoredDuration = DefaultDuration;
        [SerializeField] private Vector2Int canvasSize = new Vector2Int(480, 270);
        [SerializeField] private RectInt contentBounds = new RectInt(0, 0, 480, 270);
        [SerializeField] private RectTransform artRoot;
        [SerializeField] private StartupLayerBinding[] layers = new StartupLayerBinding[0];
        [SerializeField] private StartupParticleData[] particles = new StartupParticleData[0];
        [SerializeField] private Image[] particleImages = new Image[0];
        [SerializeField] private Sprite[] particleSprites = new Sprite[0];

        /// <summary>Raised once when the animation has finished or was skipped (after the overlay was hidden).</summary>
        public event Action Completed;

        private PlayState _state = PlayState.Idle;
        private double _elapsed;
        private int _playFrame = -1;
        private bool _completedRaised;
        private bool _errorLogged;

        private Canvas _canvas;
        private int _lastScreenWidth = -1;
        private int _lastScreenHeight = -1;
        private float _lastCanvasScale = -1f;
        private AvarnethPixelScaleMode _lastScaleMode;

        private LayerRuntime[] _layerRt;
        private ParticleRuntime[] _particleRt;

        private CanvasGroup _lockedGroup;
        private bool _loginLocked;
        private bool _savedInteractable;
        private bool _savedBlocksRaycasts;
        private float _savedAlpha;
        private bool _alphaModified;

        // ------------------------------------------------------------------ public API

        /// <summary>True while the animation is running.</summary>
        public bool IsPlaying => _state == PlayState.Playing;

        /// <summary>True once the animation has finished or was skipped.</summary>
        public bool IsFinished => _state == PlayState.Finished;

        /// <summary>Real seconds since <see cref="Play"/> (frame deltas clamped).</summary>
        public float Elapsed => (float)_elapsed;

        /// <summary>Current position in the authored timeline (seconds).</summary>
        public float TimelineTime => (float)AvarnethStartupMath.ToTimelineTime(_elapsed, Duration, authoredDuration);

        /// <summary>Real-time duration in seconds, clamped to [1, 3]. Scales the authored timeline uniformly.</summary>
        public float Duration
        {
            get => ClampDuration(duration);
            set => duration = ClampDuration(value);
        }

        /// <summary>Length of the authored timeline in seconds (from Animation_Timeline.json).</summary>
        public float AuthoredDuration => authoredDuration;

        /// <summary>Whether <see cref="Play"/> is called automatically in Start().</summary>
        public bool PlayOnStart
        {
            get => playOnStart;
            set => playOnStart = value;
        }

        /// <summary>Pixel scale mode of the art root.</summary>
        public AvarnethPixelScaleMode ScaleMode
        {
            get => scaleMode;
            set
            {
                scaleMode = value;
                _lastScreenWidth = -1;
            }
        }

        /// <summary>What happens to this GameObject when the animation has finished.</summary>
        public AvarnethStartupCompletionAction CompletionAction
        {
            get => completionAction;
            set => completionAction = value;
        }

        /// <summary>Whether a pointer click skips the animation.</summary>
        public bool SkipOnClick
        {
            get => skipOnClick;
            set
            {
                skipOnClick = value;
                ApplyInputBlocking(_state == PlayState.Playing && isActiveAndEnabled);
            }
        }

        /// <summary>Whether the full-screen raycast blocker is active while playing.</summary>
        public bool BlockInputWhilePlaying
        {
            get => blockInputWhilePlaying;
            set
            {
                blockInputWhilePlaying = value;
                ApplyInputBlocking(_state == PlayState.Playing && isActiveAndEnabled);
            }
        }

        /// <summary>Optional login CanvasGroup that is made non-interactable while playing and restored afterwards.</summary>
        public CanvasGroup LoginCanvasGroup
        {
            get => loginCanvasGroup;
            set
            {
                if (value == loginCanvasGroup) return;
                RestoreLogin();
                loginCanvasGroup = value;
                if (_state == PlayState.Playing && isActiveAndEnabled) LockLogin();
            }
        }

        /// <summary>Whether the login CanvasGroup is hidden while playing and faded in at the end.</summary>
        public bool RevealLoginDuringFadeOut
        {
            get => revealLoginDuringFadeOut;
            set => revealLoginDuringFadeOut = value;
        }

        /// <summary>UnityEvent raised once on completion.</summary>
        public UnityEvent OnCompleted => onCompleted ?? (onCompleted = new UnityEvent());

        /// <summary>Art root whose uniform scale is the art pixel size in screen pixels.</summary>
        public RectTransform ArtRoot => artRoot;

        /// <summary>Composition canvas size in art pixels.</summary>
        public Vector2Int CanvasSize => canvasSize;

        /// <summary>Content bounds in art pixels (origin top-left, y down) used for integer scale fitting.</summary>
        public RectInt ContentBounds => contentBounds;

        /// <summary>Serialized layer bindings in render order.</summary>
        public IReadOnlyList<StartupLayerBinding> Layers => layers ?? Array.Empty<StartupLayerBinding>();

        /// <summary>Serialized baked particles.</summary>
        public IReadOnlyList<StartupParticleData> Particles => particles ?? Array.Empty<StartupParticleData>();

        /// <summary>Images used for the baked particles (same length as <see cref="Particles"/>).</summary>
        public IReadOnlyList<Image> ParticleImages => particleImages ?? Array.Empty<Image>();

        /// <summary>Particle sprite list referenced by <see cref="StartupParticleData.sprite"/>.</summary>
        public IReadOnlyList<Sprite> ParticleSprites => particleSprites ?? Array.Empty<Sprite>();

        /// <summary>Transparent full-screen Image used as raycast blocker and click target.</summary>
        public Image RaycastBlocker => raycastBlocker;

        /// <summary>
        /// (Re)starts the animation from t = 0. Activates this GameObject if it was deactivated; when a parent is
        /// inactive the overlay finishes immediately instead (error logged, completion raised).
        /// Play Mode only; use <see cref="EvaluateAt"/> for edit-mode previews.
        /// </summary>
        public void Play()
        {
            if (!Application.isPlaying)
            {
                Debug.LogWarning(LogPrefix + "Play() is only available in Play Mode. Use EvaluateAt() for previews.", this);
                return;
            }

            _state = PlayState.Playing;
            _completedRaised = false;
            _errorLogged = false;
            _elapsed = 0.0;
            _playFrame = Time.frameCount;

            if (!gameObject.activeSelf) gameObject.SetActive(true);
            enabled = true;

            if (!gameObject.activeInHierarchy)
            {
                // A parent is inactive: Update would never run, so the overlay could never finish and the login
                // would stay locked. Finish cleanly instead (nothing is shown, completion is raised).
                LogErrorOnce("Play() was called while a parent GameObject is inactive.", true);
                Finish();
                return;
            }

            if (!PrepareBindings(out string error))
            {
                LogErrorOnce(error, true);
                Finish();
                return;
            }

            ApplyInputBlocking(true);
            LockLogin();
            UpdatePixelScale(true);
            ApplyTime(0f);
            UpdateLoginReveal();
        }

        /// <summary>Finishes immediately: hides the overlay, restores the login CanvasGroup and raises completion once.</summary>
        public void Skip()
        {
            if (_state == PlayState.Finished) return;
            if (!Application.isPlaying)
            {
                Debug.LogWarning(LogPrefix + "Skip() is only available in Play Mode.", this);
                return;
            }

            Finish();
        }

        /// <summary>
        /// Applies the visual state of authored timeline time <paramref name="timelineTime"/> (seconds) to the layer
        /// and particle Images, e.g. for edit-mode previews. Does not change the play state, does not touch the
        /// login CanvasGroup and never raises completion. Returns false when the bindings are incomplete.
        /// </summary>
        public bool EvaluateAt(float timelineTime)
        {
            if (!PrepareBindings(out string error))
            {
                LogErrorOnce(error, false);
                return false;
            }

            if (!(timelineTime < authoredDuration))
                HideAll();
            else
                ApplyTime(timelineTime);
            return true;
        }

        /// <summary>
        /// Hides all layer and particle Images and, unless playing, switches the raycast blocker off: the neutral
        /// state the generated prefab is saved in. Editor helper (e.g. after <see cref="EvaluateAt"/>); does not
        /// change the play state, does not touch the login CanvasGroup and never raises completion.
        /// </summary>
        public void ClearPreview()
        {
            HideAll();
            if (_state != PlayState.Playing) ApplyInputBlocking(false);
        }

        /// <summary>
        /// Assigns the generated timeline data. Used by the editor installer when it builds the prefab;
        /// playback options (duration, input, login, events) are left unchanged.
        /// </summary>
        public void SetTimelineData(float timelineDuration, Vector2Int timelineCanvasSize, RectInt timelineContentBounds,
            RectTransform timelineArtRoot, StartupLayerBinding[] layerBindings, StartupParticleData[] particleData,
            Image[] particleImageBindings, Sprite[] particleSpriteList, Image blocker)
        {
            authoredDuration = timelineDuration;
            canvasSize = timelineCanvasSize;
            contentBounds = timelineContentBounds;
            artRoot = timelineArtRoot;
            layers = layerBindings ?? new StartupLayerBinding[0];
            particles = particleData ?? new StartupParticleData[0];
            particleImages = particleImageBindings ?? new Image[0];
            particleSprites = particleSpriteList ?? new Sprite[0];
            raycastBlocker = blocker;
            _layerRt = null;
            _particleRt = null;
            _lastScreenWidth = -1;
            _errorLogged = false;

            if (_state == PlayState.Playing && !PrepareBindings(out string error))
            {
                LogErrorOnce(error, true);
                Finish();
            }
        }

        /// <summary>Pointer click handler (EventSystem): skips the animation when <see cref="SkipOnClick"/> is enabled.</summary>
        public void OnPointerClick(PointerEventData eventData)
        {
            if (skipOnClick && _state == PlayState.Playing) Skip();
        }

        // ------------------------------------------------------------------ Unity messages

        private void Awake()
        {
            _canvas = GetComponent<Canvas>();
            if (_canvas == null) _canvas = GetComponentInParent<Canvas>();

            // A fully transparent Image is skipped by the GraphicRaycaster when its CanvasRenderer culls
            // transparent geometry, so the blocker must not cull.
            if (raycastBlocker != null) raycastBlocker.canvasRenderer.cullTransparentMesh = false;

            // Start neutral (nothing drawn, no input blocked) until Play() runs - also when this component is
            // disabled before Start(). Play() applies t = 0 before the first frame is rendered, so nothing pops.
            // Skipped when Play() was already called (e.g. from another script's Awake before this one).
            if (_state != PlayState.Playing)
            {
                HideAll();
                ApplyInputBlocking(false);
            }
        }

        private void Start()
        {
            if (playOnStart && _state == PlayState.Idle) Play();
        }

        private void OnEnable()
        {
            if (_state != PlayState.Playing) return;
            ApplyInputBlocking(true);
            LockLogin();
        }

        private void OnDisable()
        {
            // Disabling the component instead of calling Skip() must not leave art or the blocker over the login.
            // When it is enabled again while playing, the next Update re-applies the current frame.
            HideAll();
            ApplyInputBlocking(false);
            RestoreLogin();
        }

        private void OnDestroy()
        {
            RestoreLogin();
        }

        private void Update()
        {
            if (_state != PlayState.Playing)
            {
                enabled = false;
                return;
            }

            if (Time.frameCount != _playFrame)
                _elapsed += AvarnethStartupMath.ClampDelta(Time.unscaledDeltaTime, maxDeltaTime);

            float playbackDuration = Duration;
            if (_elapsed >= playbackDuration)
            {
                Finish();
                return;
            }

            try
            {
                if (!RuntimeMatchesData() && !PrepareBindings(out string error))
                {
                    LogErrorOnce(error, true);
                    Finish();
                    return;
                }

                UpdatePixelScale(false);
                ApplyTime((float)AvarnethStartupMath.ToTimelineTime(_elapsed, playbackDuration, authoredDuration));
                UpdateLoginReveal();
            }
            catch (Exception e)
            {
                // A reference was destroyed while playing: report once and finish instead of throwing every frame.
                if (!_errorLogged)
                {
                    _errorLogged = true;
                    Debug.LogException(e, this);
                }

                Finish();
            }
        }

        private bool RuntimeMatchesData()
        {
            return _layerRt != null && _particleRt != null
                && _layerRt.Length == (layers != null ? layers.Length : 0)
                && _particleRt.Length == (particles != null ? particles.Length : 0)
                && particleImages != null && particleImages.Length == _particleRt.Length;
        }

        // ------------------------------------------------------------------ playback internals

        private void Finish()
        {
            if (_state == PlayState.Finished) return;
            _state = PlayState.Finished;

            HideAll();
            ApplyInputBlocking(false);
            RestoreLogin();

            enabled = false;
            if (completionAction == AvarnethStartupCompletionAction.DestroyGameObject)
                Destroy(gameObject);
            else
                gameObject.SetActive(false);

            RaiseCompleted();
        }

        private void RaiseCompleted()
        {
            if (_completedRaised) return;
            _completedRaised = true;

            try
            {
                if (onCompleted != null) onCompleted.Invoke();
            }
            catch (Exception e)
            {
                Debug.LogException(e, this);
            }

            try
            {
                Completed?.Invoke();
            }
            catch (Exception e)
            {
                Debug.LogException(e, this);
            }
        }

        private void ApplyTime(float t)
        {
            double time = t;

            for (int i = 0; i < _layerRt.Length; i++)
            {
                StartupLayerBinding b = layers[i];
                ref LayerRuntime rt = ref _layerRt[i];

                AvarnethStartupMath.EvaluateKeys(b.keys, time, out double alpha, out double dx, out double dy);
                int index = AvarnethStartupMath.FlipbookIndex(time, b.frameStart, b.frameEnd, rt.frameCount, b.afterFrames);

                Sprite sprite = null;
                if (index >= 0) sprite = b.frames[index];
                else if (index == AvarnethStartupMath.FrameStaticSprite && rt.hasStaticSprite) sprite = b.sprite;

                if (sprite == null || !AvarnethStartupMath.IsVisibleAlpha(alpha))
                {
                    SetLayerHidden(b.image, ref rt);
                    continue;
                }

                int x = AvarnethStartupMath.Snap(b.position.x + dx);
                int y = AvarnethStartupMath.Snap(b.position.y + dy);
                SetLayerVisible(b.image, ref rt, sprite, x, y, Clamp01((float)alpha));
            }

            for (int i = 0; i < _particleRt.Length; i++)
            {
                ref ParticleRuntime rt = ref _particleRt[i];
                Image image = particleImages[i];

                bool active = AvarnethStartupMath.EvaluateParticle(in particles[i], time, out double px, out double py, out double alpha);
                if (!active || !AvarnethStartupMath.IsVisibleAlpha(alpha))
                {
                    if (!rt.valid || rt.visible)
                    {
                        image.enabled = false;
                        rt.visible = false;
                        rt.valid = true;
                    }
                    continue;
                }

                AvarnethStartupMath.ParticleTopLeft(px, py, rt.width, rt.height, out int left, out int top);
                float a = Clamp01((float)alpha);

                if (!rt.valid || rt.x != left || rt.y != top)
                {
                    rt.rect.anchoredPosition = new Vector2(left, -top);
                    rt.x = left;
                    rt.y = top;
                }

                if (!rt.valid || rt.alpha != a)
                {
                    image.color = new Color(1f, 1f, 1f, a);
                    rt.alpha = a;
                }

                if (!rt.valid || !rt.visible) image.enabled = true;
                rt.visible = true;
                rt.valid = true;
            }
        }

        private static void SetLayerHidden(Image image, ref LayerRuntime rt)
        {
            if (rt.valid && !rt.visible) return;
            image.enabled = false;
            rt.visible = false;
            rt.valid = true;
        }

        private static void SetLayerVisible(Image image, ref LayerRuntime rt, Sprite sprite, int x, int y, float alpha)
        {
            if (!rt.valid || !ReferenceEquals(rt.sprite, sprite))
            {
                image.sprite = sprite;
                Rect r = sprite.rect;
                rt.rect.sizeDelta = new Vector2(r.width, r.height);
                rt.sprite = sprite;
            }

            if (!rt.valid || rt.x != x || rt.y != y)
            {
                rt.rect.anchoredPosition = new Vector2(x, -y);
                rt.x = x;
                rt.y = y;
            }

            if (!rt.valid || rt.alpha != alpha)
            {
                image.color = new Color(1f, 1f, 1f, alpha);
                rt.alpha = alpha;
            }

            if (!rt.valid || !rt.visible) image.enabled = true;
            rt.visible = true;
            rt.valid = true;
        }

        private void HideAll()
        {
            if (layers != null)
            {
                for (int i = 0; i < layers.Length; i++)
                {
                    StartupLayerBinding b = layers[i];
                    if (b != null && b.image != null) b.image.enabled = false;
                }
            }

            if (particleImages != null)
            {
                for (int i = 0; i < particleImages.Length; i++)
                {
                    if (particleImages[i] != null) particleImages[i].enabled = false;
                }
            }

            InvalidateRuntime();
        }

        private void InvalidateRuntime()
        {
            if (_layerRt != null)
                for (int i = 0; i < _layerRt.Length; i++) _layerRt[i].valid = false;
            if (_particleRt != null)
                for (int i = 0; i < _particleRt.Length; i++) _particleRt[i].valid = false;
        }

        /// <summary>Validates all references and (re)builds the per-element caches. Allocates only when sizes change.</summary>
        private bool PrepareBindings(out string error)
        {
            error = null;
            if (artRoot == null) { error = "Art Root is not assigned."; return false; }
            if (!(authoredDuration > 0f)) { error = "Authored duration must be greater than 0."; return false; }
            if (canvasSize.x <= 0 || canvasSize.y <= 0) { error = "Canvas size must be positive."; return false; }

            int layerCount = layers != null ? layers.Length : 0;
            int particleCount = particles != null ? particles.Length : 0;
            if (layerCount == 0 && particleCount == 0) { error = "No timeline data. Run Tools > AVARNETH > Startup > Create / Update Startup Prefab."; return false; }

            for (int i = 0; i < layerCount; i++)
            {
                StartupLayerBinding b = layers[i];
                if (b == null) { error = "Layer binding " + i + " is missing."; return false; }
                if (b.image == null) { error = "Layer '" + b.id + "' has no Image."; return false; }
                if (b.frames != null)
                {
                    for (int f = 0; f < b.frames.Length; f++)
                    {
                        if (b.frames[f] == null) { error = "Layer '" + b.id + "' frame " + f + " has no sprite."; return false; }
                    }
                }
            }

            int imageCount = particleImages != null ? particleImages.Length : 0;
            if (imageCount != particleCount) { error = "Particle Image count (" + imageCount + ") does not match the particle count (" + particleCount + ")."; return false; }

            int spriteCount = particleSprites != null ? particleSprites.Length : 0;
            for (int i = 0; i < particleCount; i++)
            {
                if (particleImages[i] == null) { error = "Particle Image " + i + " is missing."; return false; }
                int s = particles[i].sprite;
                if (s < 0 || s >= spriteCount || particleSprites[s] == null) { error = "Particle " + i + " references a missing particle sprite (" + s + ")."; return false; }
            }

            if (_layerRt == null || _layerRt.Length != layerCount) _layerRt = new LayerRuntime[layerCount];
            if (_particleRt == null || _particleRt.Length != particleCount) _particleRt = new ParticleRuntime[particleCount];

            for (int i = 0; i < layerCount; i++)
            {
                StartupLayerBinding b = layers[i];
                RectTransform rect = b.image.rectTransform;
                SetTopLeftAnchors(rect);
                b.image.raycastTarget = false;
                _layerRt[i] = new LayerRuntime
                {
                    rect = rect,
                    hasStaticSprite = b.sprite != null,
                    frameCount = b.frames != null ? b.frames.Length : 0,
                };
            }

            for (int i = 0; i < particleCount; i++)
            {
                Image image = particleImages[i];
                Sprite sprite = particleSprites[particles[i].sprite];
                RectTransform rect = image.rectTransform;
                SetTopLeftAnchors(rect);
                image.raycastTarget = false;
                if (image.sprite != sprite) image.sprite = sprite;
                Rect r = sprite.rect;
                int w = AvarnethStartupMath.Snap(r.width);   // contract snap floor(v + 0.5), feeds floor(w / 2)
                int h = AvarnethStartupMath.Snap(r.height);
                rect.sizeDelta = new Vector2(w, h);
                _particleRt[i] = new ParticleRuntime { rect = rect, width = w, height = h };
            }

            return true;
        }

        private static void SetTopLeftAnchors(RectTransform rect)
        {
            Vector2 topLeft = new Vector2(0f, 1f);
            if (rect.anchorMin != topLeft) rect.anchorMin = topLeft;
            if (rect.anchorMax != topLeft) rect.anchorMax = topLeft;
            if (rect.pivot != topLeft) rect.pivot = topLeft;
        }

        private void UpdatePixelScale(bool force)
        {
            int w = Screen.width;
            int h = Screen.height;
            float canvasScale = _canvas != null ? _canvas.scaleFactor : 1f;
            if (!(canvasScale > 0f)) canvasScale = 1f;

            if (!force && w == _lastScreenWidth && h == _lastScreenHeight && canvasScale == _lastCanvasScale && scaleMode == _lastScaleMode)
                return;

            _lastScreenWidth = w;
            _lastScreenHeight = h;
            _lastCanvasScale = canvasScale;
            _lastScaleMode = scaleMode;

            double s = AvarnethStartupMath.ComputePixelScale(scaleMode, w, h, canvasSize.x, canvasSize.y,
                contentBounds.x, contentBounds.y, contentBounds.width, contentBounds.height);

            double ox = 0.0;
            double oy = 0.0;
            if (scaleMode != AvarnethPixelScaleMode.Continuous)
            {
                ox = AvarnethStartupMath.PixelAlignOffset(w, canvasSize.x, s);
                oy = AvarnethStartupMath.PixelAlignOffset(h, canvasSize.y, s);
            }

            // Canvas units are screen pixels divided by the canvas scale factor (1 with Constant Pixel Size).
            float scale = (float)(s / canvasScale);
            artRoot.localScale = new Vector3(scale, scale, 1f);
            artRoot.anchoredPosition = new Vector2((float)(ox / canvasScale), (float)(oy / canvasScale));
        }

        private void ApplyInputBlocking(bool playing)
        {
            if (raycastBlocker == null) return;
            bool block = playing && (blockInputWhilePlaying || skipOnClick);
            if (raycastBlocker.raycastTarget != block) raycastBlocker.raycastTarget = block;
            if (raycastBlocker.enabled != block) raycastBlocker.enabled = block;
        }

        private void LockLogin()
        {
            if (!_loginLocked)
            {
                CanvasGroup group = loginCanvasGroup;
                if (group == null) return;
                _lockedGroup = group;
                _savedInteractable = group.interactable;
                _savedBlocksRaycasts = group.blocksRaycasts;
                _savedAlpha = group.alpha;
                _alphaModified = false;
                _loginLocked = true;
            }

            if (_lockedGroup == null) return;
            _lockedGroup.interactable = false;
            _lockedGroup.blocksRaycasts = false;
            if (revealLoginDuringFadeOut)
            {
                _lockedGroup.alpha = 0f;
                _alphaModified = true;
            }
        }

        private void UpdateLoginReveal()
        {
            if (!_loginLocked || !revealLoginDuringFadeOut || _lockedGroup == null) return;
            float a = (float)(_savedAlpha * AvarnethStartupMath.RevealFactor(_elapsed, Duration, revealSeconds));
            if (_lockedGroup.alpha != a)
            {
                _lockedGroup.alpha = a;
                _alphaModified = true;
            }
        }

        /// <summary>
        /// Restores what the overlay changed on the login CanvasGroup (idempotent). interactable / blocksRaycasts
        /// are restored while they still hold the value the overlay wrote (false); a value the login code switched
        /// on meanwhile is kept. alpha is restored only when the overlay wrote it (Reveal Login During Fade Out).
        /// </summary>
        private void RestoreLogin()
        {
            if (!_loginLocked) return;
            _loginLocked = false;

            CanvasGroup group = _lockedGroup;
            _lockedGroup = null;
            bool alphaModified = _alphaModified;
            _alphaModified = false;
            if (group == null) return;

            if (!group.interactable) group.interactable = _savedInteractable;
            if (!group.blocksRaycasts) group.blocksRaycasts = _savedBlocksRaycasts;
            if (alphaModified) group.alpha = _savedAlpha;
        }

        private void LogErrorOnce(string error, bool skipping)
        {
            if (_errorLogged) return;
            _errorLogged = true;
            Debug.LogError(LogPrefix + error + (skipping ? " The overlay is skipped." : string.Empty), this);
        }

        private static float ClampDuration(float value)
        {
            if (!(value >= MinDuration)) return MinDuration;
            return value > MaxDuration ? MaxDuration : value;
        }

        private static float Clamp01(float value)
        {
            if (!(value > 0f)) return 0f;
            return value > 1f ? 1f : value;
        }
    }
}
