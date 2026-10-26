// AVARNETH: VEIL OF EMBERS - startup branding overlay
// Copyright (c) Eckertengineering. All rights reserved.
//
// Pure C# implementation of the startup timeline contract (CONTRACT.md, "avarneth.startup.timeline/1").
// This file intentionally has no Unity dependency so the exact same code can be compiled and tested
// outside Unity (see the math test harness) and shared by the runtime component.
//
// Numeric model (relevant for bit-exact comparisons with other implementations):
//  * Serialized data (key times/values, particle data) is stored as 32-bit float, as Unity serializes it.
//  * Every public float entry point widens its inputs to double and evaluates in double precision.
//  * Operation order follows the contract formulas literally: cubes are evaluated as u*u*u,
//    lerp is a + (b - a) * e, particle y is (y + vy*tau) + (0.5*ay)*(tau*tau).
//  * Pixel snapping is floor(v + 0.5) (never banker's rounding).

using System;

namespace Eckertengineering.Avarneth.Branding
{
    /// <summary>Easing curve of the timeline segment that arrives at a key.</summary>
    public enum StartupEase
    {
        /// <summary>e = u</summary>
        Linear = 0,
        /// <summary>e = u^3</summary>
        InCubic = 1,
        /// <summary>e = 1 - (1 - u)^3</summary>
        OutCubic = 2,
        /// <summary>e = u &lt; 0.5 ? 4u^3 : 1 - (-2u + 2)^3 / 2</summary>
        InOutCubic = 3,
        /// <summary>e = u^2 (3 - 2u)</summary>
        Smooth = 4,
        /// <summary>e = u &lt; 1 ? 0 : 1</summary>
        Step = 5,
    }

    /// <summary>What a flipbook layer shows once its frame range has elapsed.</summary>
    public enum StartupAfterFrames
    {
        /// <summary>Keep showing the last frame.</summary>
        Hold = 0,
        /// <summary>Show the static layer sprite.</summary>
        Sprite = 1,
        /// <summary>Hide the layer.</summary>
        Hide = 2,
    }

    /// <summary>How the art pixel size (ArtRoot uniform scale) is derived from the screen size.</summary>
    public enum AvarnethPixelScaleMode
    {
        /// <summary>round(screenHeight / canvasHeight), reduced while the content bounds do not fit, min 1.</summary>
        IntegerNearest = 0,
        /// <summary>floor(screenHeight / canvasHeight), reduced while the content bounds do not fit, min 1.</summary>
        IntegerFloor = 1,
        /// <summary>screenHeight / canvasHeight without integer snapping.</summary>
        Continuous = 2,
    }

    /// <summary>One animation key of a layer (alpha and pixel offset at time <see cref="t"/>).</summary>
    [Serializable]
    public struct StartupKey
    {
        /// <summary>Key time in authored timeline seconds.</summary>
        public float t;
        /// <summary>Layer alpha multiplier at this key.</summary>
        public float alpha;
        /// <summary>Horizontal offset in art pixels (x right).</summary>
        public float dx;
        /// <summary>Vertical offset in art pixels (y down).</summary>
        public float dy;
        /// <summary>Easing of the segment arriving at this key.</summary>
        public StartupEase ease;
    }

    /// <summary>One baked, deterministic particle (centre position in art pixels, y down).</summary>
    [Serializable]
    public struct StartupParticleData
    {
        /// <summary>Index into the particle sprite list.</summary>
        public int sprite;
        /// <summary>Spawn time in authored timeline seconds.</summary>
        public float t0;
        /// <summary>Lifetime in seconds; active while t0 &lt;= t &lt; t0 + life.</summary>
        public float life;
        /// <summary>Spawn centre x.</summary>
        public float x;
        /// <summary>Spawn centre y.</summary>
        public float y;
        /// <summary>Velocity x in art px per second.</summary>
        public float vx;
        /// <summary>Velocity y in art px per second.</summary>
        public float vy;
        /// <summary>Acceleration y in art px per second squared.</summary>
        public float ay;
        /// <summary>Peak alpha.</summary>
        public float alpha;
        /// <summary>Fade-in length as a fraction of the lifetime (0 = none).</summary>
        public float fadeIn;
        /// <summary>Fade-out length as a fraction of the lifetime (0 = none).</summary>
        public float fadeOut;
    }

    /// <summary>Contract math for the startup timeline. Allocation free and deterministic.</summary>
    public static class AvarnethStartupMath
    {
        /// <summary>Flipbook result: show the static layer sprite.</summary>
        public const int FrameStaticSprite = -1;

        /// <summary>Flipbook result: layer hidden.</summary>
        public const int FrameHidden = -2;

        /// <summary>Alpha at or below this value is not drawn.</summary>
        public const double VisibleAlphaThreshold = 0.001;

        /// <summary>Contract schema identifier of Animation_Timeline.json.</summary>
        public const string TimelineSchema = "avarneth.startup.timeline/1";

        // ------------------------------------------------------------------ easing

        /// <summary>Evaluates an easing curve; <paramref name="u"/> is clamped to [0, 1].</summary>
        public static float Ease(StartupEase e, float u)
        {
            return (float)Ease(e, (double)u);
        }

        /// <summary>Double precision variant of <see cref="Ease(StartupEase, float)"/>.</summary>
        public static double Ease(StartupEase e, double u)
        {
            if (!(u > 0.0)) u = 0.0;          // also maps NaN to 0
            else if (u > 1.0) u = 1.0;

            switch (e)
            {
                case StartupEase.InCubic:
                    return u * u * u;
                case StartupEase.OutCubic:
                {
                    double v = 1.0 - u;
                    return 1.0 - v * v * v;
                }
                case StartupEase.InOutCubic:
                {
                    if (u < 0.5) return 4.0 * (u * u * u);
                    double v = -2.0 * u + 2.0;
                    return 1.0 - (v * v * v) / 2.0;
                }
                case StartupEase.Smooth:
                    return u * u * (3.0 - 2.0 * u);
                case StartupEase.Step:
                    return u < 1.0 ? 0.0 : 1.0;
                default:
                    return u;
            }
        }

        /// <summary>Parses a contract ease name (case sensitive); unknown or null names map to Linear.</summary>
        public static StartupEase ParseEase(string s)
        {
            switch (s)
            {
                case "linear": return StartupEase.Linear;
                case "inCubic": return StartupEase.InCubic;
                case "outCubic": return StartupEase.OutCubic;
                case "inOutCubic": return StartupEase.InOutCubic;
                case "smooth": return StartupEase.Smooth;
                case "step": return StartupEase.Step;
                default: return StartupEase.Linear;
            }
        }

        /// <summary>Returns true when <paramref name="s"/> is one of the contract ease names.</summary>
        public static bool IsKnownEase(string s)
        {
            return s == "linear" || s == "inCubic" || s == "outCubic" || s == "inOutCubic" || s == "smooth" || s == "step";
        }

        /// <summary>Parses a contract afterFrames value (case sensitive); unknown or null values map to Hold.</summary>
        public static StartupAfterFrames ParseAfterFrames(string s)
        {
            switch (s)
            {
                case "sprite": return StartupAfterFrames.Sprite;
                case "hide": return StartupAfterFrames.Hide;
                default: return StartupAfterFrames.Hold;
            }
        }

        /// <summary>Returns true when <paramref name="s"/> is one of the contract afterFrames values.</summary>
        public static bool IsKnownAfterFrames(string s)
        {
            return s == "hold" || s == "sprite" || s == "hide";
        }

        // ------------------------------------------------------------------ keys

        /// <summary>
        /// Evaluates layer keys at timeline time <paramref name="t"/> (keys sorted by t).
        /// Before the first key the first values apply, after the last key the last values.
        /// A null or empty key list yields alpha 1 and no offset.
        /// </summary>
        public static void EvaluateKeys(StartupKey[] keys, float t, out float alpha, out float dx, out float dy)
        {
            EvaluateKeys(keys, (double)t, out double a, out double x, out double y);
            alpha = (float)a;
            dx = (float)x;
            dy = (float)y;
        }

        /// <summary>Double precision variant of <see cref="EvaluateKeys(StartupKey[], float, out float, out float, out float)"/>.</summary>
        public static void EvaluateKeys(StartupKey[] keys, double t, out double alpha, out double dx, out double dy)
        {
            if (keys == null || keys.Length == 0)
            {
                alpha = 1.0;
                dx = 0.0;
                dy = 0.0;
                return;
            }

            int last = keys.Length - 1;
            if (t <= keys[0].t)
            {
                alpha = keys[0].alpha;
                dx = keys[0].dx;
                dy = keys[0].dy;
                return;
            }

            if (t >= keys[last].t)
            {
                alpha = keys[last].alpha;
                dx = keys[last].dx;
                dy = keys[last].dy;
                return;
            }

            for (int i = 0; i < last; i++)
            {
                double t1 = keys[i + 1].t;
                if (!(t < t1)) continue;

                double t0 = keys[i].t;
                double span = t1 - t0;
                double u = span > 0.0 ? (t - t0) / span : 1.0;
                double e = Ease(keys[i + 1].ease, u);
                alpha = Lerp(keys[i].alpha, keys[i + 1].alpha, e);
                dx = Lerp(keys[i].dx, keys[i + 1].dx, e);
                dy = Lerp(keys[i].dy, keys[i + 1].dy, e);
                return;
            }

            // Only reachable for NaN or unsorted keys: fall back to the last key.
            alpha = keys[last].alpha;
            dx = keys[last].dx;
            dy = keys[last].dy;
        }

        /// <summary>a + (b - a) * e, evaluated in double precision.</summary>
        public static double Lerp(double a, double b, double e)
        {
            return a + (b - a) * e;
        }

        // ------------------------------------------------------------------ flipbook

        /// <summary>
        /// Flipbook frame for timeline time <paramref name="t"/>: a frame index &gt;= 0,
        /// <see cref="FrameStaticSprite"/> (-1) to show the static sprite or <see cref="FrameHidden"/> (-2).
        /// With <paramref name="frameCount"/> == 0 the static sprite is always shown.
        /// </summary>
        public static int FlipbookIndex(float t, float frameStart, float frameEnd, int frameCount, StartupAfterFrames after)
        {
            return FlipbookIndex((double)t, (double)frameStart, (double)frameEnd, frameCount, after);
        }

        /// <summary>Double precision variant of <see cref="FlipbookIndex(float, float, float, int, StartupAfterFrames)"/>.</summary>
        public static int FlipbookIndex(double t, double frameStart, double frameEnd, int frameCount, StartupAfterFrames after)
        {
            if (frameCount <= 0) return FrameStaticSprite;
            if (t < frameStart) return FrameHidden;

            if (t < frameEnd)
            {
                double f = Math.Floor((t - frameStart) / (frameEnd - frameStart) * frameCount);
                if (!(f > 0.0)) return 0;
                if (f >= frameCount - 1) return frameCount - 1;
                return (int)f;
            }

            if (t >= frameEnd)
            {
                switch (after)
                {
                    case StartupAfterFrames.Sprite: return FrameStaticSprite;
                    case StartupAfterFrames.Hide: return FrameHidden;
                    default: return frameCount - 1;
                }
            }

            return FrameHidden; // NaN time
        }

        // ------------------------------------------------------------------ particles

        /// <summary>
        /// Evaluates a baked particle at timeline time <paramref name="t"/>. Returns false while inactive
        /// (outside t0 &lt;= t &lt; t0 + life); <paramref name="x"/>/<paramref name="y"/> are the centre in art px.
        /// </summary>
        public static bool EvaluateParticle(in StartupParticleData p, float t, out float x, out float y, out float alpha)
        {
            bool active = EvaluateParticle(in p, (double)t, out double px, out double py, out double a);
            x = (float)px;
            y = (float)py;
            alpha = (float)a;
            return active;
        }

        /// <summary>Double precision variant of <see cref="EvaluateParticle(in StartupParticleData, float, out float, out float, out float)"/>.</summary>
        public static bool EvaluateParticle(in StartupParticleData p, double t, out double x, out double y, out double alpha)
        {
            double t0 = p.t0;
            double life = p.life;
            if (!(life > 0.0) || !(t >= t0) || !(t < t0 + life))
            {
                x = p.x;
                y = p.y;
                alpha = 0.0;
                return false;
            }

            double tau = t - t0;
            double u = tau / life;
            double fadeIn = p.fadeIn;
            double fadeOut = p.fadeOut;

            double fin = fadeIn > 0.0 ? Math.Min(1.0, u / fadeIn) : 1.0;
            double fout = (fadeOut > 0.0 && u > 1.0 - fadeOut) ? Math.Max(0.0, (1.0 - u) / fadeOut) : 1.0;

            x = p.x + p.vx * tau;
            y = p.y + p.vy * tau + 0.5 * p.ay * (tau * tau);
            alpha = p.alpha * fin * fout;
            return true;
        }

        /// <summary>
        /// Top-left draw position of a particle sprite of size <paramref name="width"/> x <paramref name="height"/>:
        /// (floor(px + 0.5) - floor(w / 2), floor(py + 0.5) - floor(h / 2)).
        /// </summary>
        public static void ParticleTopLeft(double px, double py, int width, int height, out int left, out int top)
        {
            left = Snap(px) - FloorHalf(width);
            top = Snap(py) - FloorHalf(height);
        }

        /// <summary>floor(v / 2) for integers (also correct for negative values).</summary>
        public static int FloorHalf(int v)
        {
            return v >= 0 ? v / 2 : -((-v + 1) / 2);
        }

        // ------------------------------------------------------------------ snapping, time, scale

        /// <summary>Contract pixel snap: floor(v + 0.5).</summary>
        public static int Snap(float v)
        {
            return (int)Math.Floor(v + 0.5);
        }

        /// <summary>Contract pixel snap: floor(v + 0.5).</summary>
        public static int Snap(double v)
        {
            return (int)Math.Floor(v + 0.5);
        }

        /// <summary>Alpha visibility rule: drawn only when alpha &gt; 0.001.</summary>
        public static bool IsVisibleAlpha(double alpha)
        {
            return alpha > VisibleAlphaThreshold;
        }

        /// <summary>
        /// Maps real seconds since Play() to authored timeline seconds when the authored timeline is
        /// uniformly stretched to <paramref name="playbackDuration"/>.
        /// </summary>
        public static double ToTimelineTime(double elapsedSeconds, double playbackDuration, double authoredDuration)
        {
            if (!(playbackDuration > 0.0) || !(authoredDuration > 0.0)) return elapsedSeconds;
            return elapsedSeconds * (authoredDuration / playbackDuration);
        }

        /// <summary>Clamps a frame delta to [0, maxDelta]; NaN and negative deltas become 0.</summary>
        public static double ClampDelta(double delta, double maxDelta)
        {
            if (!(delta > 0.0)) return 0.0;
            if (maxDelta > 0.0 && delta > maxDelta) return maxDelta;
            return delta;
        }

        /// <summary>
        /// Linear 0..1 factor of a reveal that runs over the last <paramref name="revealSeconds"/>
        /// of <paramref name="duration"/> (0 before the reveal window, 1 at the end).
        /// </summary>
        public static double RevealFactor(double elapsed, double duration, double revealSeconds)
        {
            if (!(duration > 0.0)) return 1.0;
            double reveal = revealSeconds < duration ? revealSeconds : duration;
            if (!(reveal > 0.0)) return elapsed >= duration ? 1.0 : 0.0;
            double u = (elapsed - (duration - reveal)) / reveal;
            if (!(u > 0.0)) return 0.0;
            return u >= 1.0 ? 1.0 : u;
        }

        /// <summary>
        /// Art pixel size in screen pixels for a canvas of <paramref name="canvasWidth"/> x <paramref name="canvasHeight"/>
        /// art px centred on a screen. Integer modes are reduced (min 1) while the content bounds
        /// (art px, origin top-left, y down) would extend beyond the screen.
        /// </summary>
        public static double ComputePixelScale(AvarnethPixelScaleMode mode, int screenWidth, int screenHeight,
            int canvasWidth, int canvasHeight, int contentX, int contentY, int contentWidth, int contentHeight)
        {
            if (screenWidth <= 0 || screenHeight <= 0 || canvasWidth <= 0 || canvasHeight <= 0) return 1.0;

            double raw = (double)screenHeight / canvasHeight;
            if (mode == AvarnethPixelScaleMode.Continuous) return raw;

            int s = mode == AvarnethPixelScaleMode.IntegerFloor ? (int)Math.Floor(raw) : Snap(raw);
            if (s < 1) s = 1;

            if (contentWidth <= 0 || contentHeight <= 0)
            {
                contentX = 0;
                contentY = 0;
                contentWidth = canvasWidth;
                contentHeight = canvasHeight;
            }

            // Content extent measured from the canvas centre, doubled (keeps everything integral).
            long halfW2 = Math.Max(Math.Abs(2L * contentX - canvasWidth), Math.Abs(2L * (contentX + contentWidth) - canvasWidth));
            long halfH2 = Math.Max(Math.Abs(2L * contentY - canvasHeight), Math.Abs(2L * (contentY + contentHeight) - canvasHeight));

            while (s > 1 && (halfW2 * s > screenWidth || halfH2 * s > screenHeight))
                s--;

            return s;
        }

        /// <summary>
        /// Offset (screen px) that moves the edge of a centred box of <paramref name="boxSize"/> x <paramref name="scale"/>
        /// pixels onto a whole pixel of a screen of <paramref name="screenSize"/> pixels (0 or +-0.5 for integer scales).
        /// </summary>
        public static double PixelAlignOffset(int screenSize, int boxSize, double scale)
        {
            double edge = (screenSize - boxSize * scale) * 0.5;
            return Math.Floor(edge + 0.5) - edge;
        }
    }
}
