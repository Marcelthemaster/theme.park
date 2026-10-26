// AVARNETH: VEIL OF EMBERS - startup branding overlay (editor tooling)
// Copyright (c) Eckertengineering. All rights reserved.
//
// Menu: Tools > AVARNETH > Startup
// The installer only touches the contract files inside the located importable asset root (AVE_*.png directly in
// Layers/, Frames/, Particles/, the PNGs named in Animation_Timeline.json and Icons/AVE_Icon_<size>.png; import
// settings only after a confirmation), the generated prefab and, on explicit request with confirmation, the active
// scene (never saved automatically) and the Standalone / default icons and splash screen flags of the Player Settings.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using Object = UnityEngine.Object;

namespace Eckertengineering.Avarneth.Branding.Editor
{
    // ---------------------------------------------------------------------- contract JSON DTOs (JsonUtility)

    // The DTO fields are assigned by JsonUtility, not by C# code.
#pragma warning disable CS0649

    /// <summary>Animation_Timeline.json root object (field names exactly as in the contract).</summary>
    [Serializable]
    internal sealed class TimelineJson
    {
        public string schema;
        public float duration;
        public int canvasWidth;
        public int canvasHeight;
        public int pixelScaleAt1080p;
        public RectJson contentBounds;
        public LayerJson[] layers;
        public string[] particleSprites;
        public ParticleJson[] particles;
    }

    /// <summary>contentBounds object.</summary>
    [Serializable]
    internal sealed class RectJson
    {
        public int x;
        public int y;
        public int width;
        public int height;
    }

    /// <summary>One entry of "layers".</summary>
    [Serializable]
    internal sealed class LayerJson
    {
        public string id;
        public string sprite;
        public string[] frames;
        public float frameStart;
        public float frameEnd;
        public string afterFrames;
        public int x;
        public int y;
        public int order;
        public KeyJson[] keys;
    }

    /// <summary>One entry of a layer's "keys".</summary>
    [Serializable]
    internal sealed class KeyJson
    {
        public float t;
        public float alpha;
        public float dx;
        public float dy;
        public string ease;
    }

    /// <summary>One entry of "particles".</summary>
    [Serializable]
    internal sealed class ParticleJson
    {
        public int sprite;
        public float t0;
        public float life;
        public float x;
        public float y;
        public float vx;
        public float vy;
        public float ay;
        public float alpha;
        public float fadeIn;
        public float fadeOut;
    }

    [Serializable]
    internal sealed class SchemaProbeJson
    {
        public string schema;
    }
#pragma warning restore CS0649

    // ---------------------------------------------------------------------- shared data

    /// <summary>Located importable asset root (the folder that contains Animation_Timeline.json).</summary>
    internal sealed class InstallRoot
    {
        public TextAsset Timeline;
        public string TimelinePath;
        public string RootFolder;
        public string ParentFolder;
        public string PrefabFolder;
        public string PrefabPath;
    }

    /// <summary>Parsed and validated timeline.</summary>
    internal sealed class ParsedTimeline
    {
        public TimelineJson Data;
        public readonly List<string> Errors = new List<string>();
        public readonly List<string> Warnings = new List<string>();
        public bool IsValid => Data != null && Errors.Count == 0;
    }

    /// <summary>Sprites resolved for a timeline.</summary>
    internal sealed class ResolvedSprites
    {
        public readonly Dictionary<string, Sprite> ByPath = new Dictionary<string, Sprite>(StringComparer.Ordinal);
        public readonly List<string> Missing = new List<string>();
        public readonly List<string> Warnings = new List<string>();

        public Sprite Get(string relativePath)
        {
            if (string.IsNullOrEmpty(relativePath)) return null;
            ByPath.TryGetValue(relativePath, out Sprite sprite);
            return sprite;
        }
    }

    // ---------------------------------------------------------------------- installer

    /// <summary>Editor operations of the AVARNETH startup overlay (menu Tools > AVARNETH > Startup).</summary>
    internal static class AvarnethStartupInstaller
    {
        internal const string MenuRoot = "Tools/AVARNETH/Startup/";
        internal const string DialogTitle = "AVARNETH Startup";
        internal const string TimelineAssetName = "Animation_Timeline";
        internal const string PrefabFileName = "AvarnethStartup.prefab";
        internal const string PrefabRootName = "AvarnethStartup";
        internal const string ArtRootName = "ArtRoot";
        internal const string ParticlesContainerName = "Particles";
        internal const string IconPrefix = "AVE_Icon_";
        internal const string ContractFilePrefix = "AVE_";
        internal const string StandardRootName = "Importable_Assets";
        internal const int DefaultSortingOrder = 1000;
        internal const int ParticleOrderSplit = 100;
        internal const float SpritePixelsPerUnit = 100f;
        internal const int MinMaxTextureSize = 2048;

        internal static readonly string[] SpriteFolders = { "Layers", "Frames", "Particles" };
        internal const string IconFolder = "Icons";

        private const string OverrideKeyPrefix = "Eckertengineering.Avarneth.Startup.TimelineGuid.";

        // In 6000.6 EditorUtility.DisplayDialog cuts messages longer than 512 characters and logs them again
        // (Editor/Mono/EditorDialog.cs:142-147, LimitMessageLength). Every dialog message stays below this budget;
        // the full text always goes to the Console.
        internal const int DialogMaxChars = 500;
        private const int DialogLineMaxChars = 100;
        private const int DialogMoreLineReserve = 36;

        // ------------------------------------------------------------------ menu items

        [MenuItem(MenuRoot + "Installer...", false, 0)]
        private static void MenuOpenInstaller()
        {
            AvarnethStartupInstallerWindow.Open();
        }

        [MenuItem(MenuRoot + "Configure Sprite Import Settings", false, 20)]
        private static void MenuConfigureImportSettings()
        {
            if (TryResolveRoot(true, out InstallRoot root)) ConfigureImportSettings(root, true);
        }

        [MenuItem(MenuRoot + "Create or Update Startup Prefab", false, 21)]
        private static void MenuCreateOrUpdatePrefab()
        {
            if (TryResolveRoot(true, out InstallRoot root)) CreateOrUpdatePrefab(root, true);
        }

        [MenuItem(MenuRoot + "Add Startup Overlay To Open Scene...", false, 40)]
        private static void MenuAddOverlayToScene()
        {
            AddOverlayToOpenScene();
        }

        [MenuItem(MenuRoot + "Add Startup Overlay To Open Scene...", true)]
        private static bool MenuAddOverlayToSceneValidate()
        {
            return !EditorApplication.isPlayingOrWillChangePlaymode;
        }

        [MenuItem(MenuRoot + "Player Settings Helper...", false, 60)]
        private static void MenuPlayerSettingsHelper()
        {
            AvarnethPlayerSettingsHelperWindow.Open();
        }

        [MenuItem(MenuRoot + "Validate Installation", false, 80)]
        private static void MenuValidate()
        {
            ValidateInstallation(true);
        }

        // ------------------------------------------------------------------ root location

        private static string OverrideKey => OverrideKeyPrefix + Application.dataPath;

        /// <summary>Timeline chosen explicitly in the installer window (per project, stored in EditorPrefs).</summary>
        internal static TextAsset TimelineOverride
        {
            get
            {
                string guid = EditorPrefs.GetString(OverrideKey, string.Empty);
                if (string.IsNullOrEmpty(guid)) return null;
                string path = AssetDatabase.GUIDToAssetPath(guid);
                return string.IsNullOrEmpty(path) ? null : AssetDatabase.LoadAssetAtPath<TextAsset>(path);
            }
            set
            {
                string path = value != null ? AssetDatabase.GetAssetPath(value) : null;
                string guid = string.IsNullOrEmpty(path) ? null : AssetDatabase.AssetPathToGUID(path);
                if (string.IsNullOrEmpty(guid)) EditorPrefs.DeleteKey(OverrideKey);
                else EditorPrefs.SetString(OverrideKey, guid);
            }
        }

        /// <summary>All TextAssets named Animation_Timeline(.json) whose "schema" matches the contract and whose folder is a usable root.</summary>
        internal static List<string> FindTimelineCandidates()
        {
            return FindTimelineCandidates(null);
        }

        /// <summary>
        /// Like <see cref="FindTimelineCandidates()"/>; contract timelines in an unusable folder (Assets/ itself, or
        /// outside Assets/, e.g. Packages/) are added to <paramref name="rejected"/> instead.
        /// </summary>
        internal static List<string> FindTimelineCandidates(List<string> rejected)
        {
            var result = new List<string>();
            foreach (string guid in AssetDatabase.FindAssets(TimelineAssetName + " t:TextAsset"))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (string.IsNullOrEmpty(path) || result.Contains(path)) continue;
                if (!string.Equals(FileName(path), TimelineAssetName + ".json", StringComparison.OrdinalIgnoreCase)) continue;
                var text = AssetDatabase.LoadAssetAtPath<TextAsset>(path);
                if (text == null || !IsContractTimeline(text)) continue;
                if (IsAllowedRootFolder(ParentPath(path))) result.Add(path);
                else if (rejected != null && !rejected.Contains(path)) rejected.Add(path);
            }

            result.Sort(StringComparer.Ordinal);
            rejected?.Sort(StringComparer.Ordinal);
            return result;
        }

        /// <summary>
        /// The importable asset root must be a subfolder of Assets/: never Assets/ itself (the import settings step
        /// would then work on Assets/Layers, Assets/Particles, ...) and never a read-only package folder.
        /// </summary>
        internal static bool IsAllowedRootFolder(string folder)
        {
            return !string.IsNullOrEmpty(folder) && folder.StartsWith("Assets/", StringComparison.Ordinal) && folder.Length > "Assets/".Length;
        }

        /// <summary>True when the root folder has the name used by the package (Importable_Assets).</summary>
        internal static bool HasStandardRootName(InstallRoot root)
        {
            return root != null && string.Equals(FileName(root.RootFolder), StandardRootName, StringComparison.Ordinal);
        }

        private const string RootLocationHint = "The folder that contains Animation_Timeline.json must be a subfolder of Assets/, e.g. Assets/AVARNETH/Startup/Importable_Assets/.";

        internal static bool IsContractTimeline(TextAsset text)
        {
            if (text == null) return false;
            try
            {
                var probe = JsonUtility.FromJson<SchemaProbeJson>(text.text);
                return probe != null && probe.schema == AvarnethStartupMath.TimelineSchema;
            }
            catch (Exception)
            {
                return false;
            }
        }

        /// <summary>
        /// Resolves the importable asset root from the installer-window override or a unique detected timeline.
        /// When <paramref name="interactive"/> is true, failures are logged and shown in a dialog.
        /// </summary>
        internal static bool TryResolveRoot(bool interactive, out InstallRoot root)
        {
            bool ok = TryResolveRoot(out root, out string error, out bool needsChoice);
            if (!ok && interactive) Fail(error, needsChoice);
            return ok;
        }

        /// <summary>Resolves the importable asset root without logging or dialogs.</summary>
        internal static bool TryResolveRoot(out InstallRoot root, out string error, out bool needsChoice)
        {
            root = null;
            error = null;
            needsChoice = false;

            TextAsset chosen = TimelineOverride;
            if (chosen != null && !IsContractTimeline(chosen))
            {
                error = "The timeline selected in the installer window ('" + AssetDatabase.GetAssetPath(chosen) +
                        "') is not a valid '" + AvarnethStartupMath.TimelineSchema + "' file.";
                needsChoice = true;
                return false;
            }

            if (chosen == null)
            {
                var rejected = new List<string>();
                List<string> candidates = FindTimelineCandidates(rejected);
                if (candidates.Count == 0)
                {
                    if (rejected.Count > 0)
                    {
                        error = ComposeListDialog("Animation_Timeline.json was only found in an unusable folder:\n", rejected,
                            "\n\n" + RootLocationHint);
                        return false;
                    }

                    error = "No TextAsset named '" + TimelineAssetName + "' with schema '" + AvarnethStartupMath.TimelineSchema +
                            "' was found in the project.\n\nCopy the 05_Unity_Integration folder (including Importable_Assets) into a subfolder of Assets/ and let Unity import it.";
                    return false;
                }

                if (candidates.Count > 1)
                {
                    error = ComposeListDialog("Several AVARNETH timelines were found:\n", candidates,
                        "\n\nChoose the one to use in Tools > AVARNETH > Startup > Installer...");
                    needsChoice = true;
                    return false;
                }

                chosen = AssetDatabase.LoadAssetAtPath<TextAsset>(candidates[0]);
            }

            root = CreateRoot(chosen);
            if (root != null) return true;
            error = "The timeline '" + AssetDatabase.GetAssetPath(chosen) + "' cannot be used. " + RootLocationHint;
            needsChoice = TimelineOverride != null;
            return false;
        }

        private static InstallRoot CreateRoot(TextAsset timeline)
        {
            string path = AssetDatabase.GetAssetPath(timeline);
            if (string.IsNullOrEmpty(path)) return null;

            string rootFolder = ParentPath(path);
            if (!IsAllowedRootFolder(rootFolder)) return null;
            string parent = ParentPath(rootFolder); // at least "Assets"

            return new InstallRoot
            {
                Timeline = timeline,
                TimelinePath = path,
                RootFolder = rootFolder,
                ParentFolder = parent,
                PrefabFolder = parent + "/Prefabs",
                PrefabPath = parent + "/Prefabs/" + PrefabFileName,
            };
        }

        private static void Fail(string error, bool offerWindow)
        {
            Debug.LogError("[AVARNETH Startup] " + error);
            if (offerWindow)
            {
                if (Confirm(DialogTitle, error, "Open Installer", "Close"))
                    AvarnethStartupInstallerWindow.Open();
            }
            else
            {
                Alert(DialogTitle, error);
            }
        }

        // ------------------------------------------------------------------ timeline parsing

        internal static ParsedTimeline ParseTimeline(InstallRoot root)
        {
            var result = new ParsedTimeline();
            if (root == null || root.Timeline == null)
            {
                result.Errors.Add("Timeline asset is missing.");
                return result;
            }

            TimelineJson data;
            try
            {
                data = JsonUtility.FromJson<TimelineJson>(root.Timeline.text);
            }
            catch (Exception e)
            {
                result.Errors.Add("Animation_Timeline.json could not be parsed: " + e.Message);
                return result;
            }

            if (data == null)
            {
                result.Errors.Add("Animation_Timeline.json is empty.");
                return result;
            }

            result.Data = data;
            List<string> errors = result.Errors;
            List<string> warnings = result.Warnings;

            if (data.schema != AvarnethStartupMath.TimelineSchema)
                errors.Add("schema is '" + data.schema + "', expected '" + AvarnethStartupMath.TimelineSchema + "'.");
            if (!(data.duration > 0f))
                errors.Add("duration must be greater than 0.");
            if (data.canvasWidth <= 0 || data.canvasHeight <= 0)
                errors.Add("canvasWidth and canvasHeight must be positive.");
            if (data.layers == null) data.layers = new LayerJson[0];
            if (data.particleSprites == null) data.particleSprites = new string[0];
            if (data.particles == null) data.particles = new ParticleJson[0];
            if (data.layers.Length == 0 && data.particles.Length == 0)
                errors.Add("The timeline contains neither layers nor particles.");

            RectJson cb = data.contentBounds;
            if (cb == null || cb.width <= 0 || cb.height <= 0)
                warnings.Add("contentBounds is missing or empty; the full canvas is used.");
            else if (cb.x < 0 || cb.y < 0 || cb.x + cb.width > data.canvasWidth || cb.y + cb.height > data.canvasHeight)
                warnings.Add("contentBounds extends beyond the canvas.");

            var ids = new HashSet<string>(StringComparer.Ordinal);
            for (int i = 0; i < data.layers.Length; i++)
            {
                LayerJson layer = data.layers[i];
                if (layer == null)
                {
                    errors.Add("layers[" + i + "] is null.");
                    continue;
                }

                string label = "Layer '" + layer.id + "' (layers[" + i + "])";
                if (string.IsNullOrEmpty(layer.id)) warnings.Add("layers[" + i + "] has no id.");
                else if (!ids.Add(layer.id)) warnings.Add(label + ": duplicate id.");

                if (layer.frames == null) layer.frames = new string[0];
                bool flipbook = layer.frames.Length > 0;

                if (!flipbook && string.IsNullOrEmpty(layer.sprite))
                    errors.Add(label + ": static layer without sprite.");
                if (flipbook && layer.afterFrames == "sprite" && string.IsNullOrEmpty(layer.sprite))
                    errors.Add(label + ": afterFrames is 'sprite' but no sprite is set.");
                if (flipbook && !(layer.frameEnd > layer.frameStart))
                    warnings.Add(label + ": frameEnd is not greater than frameStart.");
                if (!string.IsNullOrEmpty(layer.afterFrames) && !AvarnethStartupMath.IsKnownAfterFrames(layer.afterFrames))
                    warnings.Add(label + ": unknown afterFrames '" + layer.afterFrames + "' (treated as 'hold').");

                CheckRelativePath(label + " sprite", layer.sprite, true, errors);
                for (int f = 0; f < layer.frames.Length; f++)
                    CheckRelativePath(label + " frames[" + f + "]", layer.frames[f], false, errors);

                if (layer.keys == null || layer.keys.Length == 0)
                {
                    errors.Add(label + ": at least one key is required.");
                    continue;
                }

                for (int k = 0; k < layer.keys.Length; k++)
                {
                    KeyJson key = layer.keys[k];
                    if (key == null)
                    {
                        errors.Add(label + ": keys[" + k + "] is null.");
                        continue;
                    }

                    if (k > 0 && layer.keys[k - 1] != null && key.t < layer.keys[k - 1].t)
                        errors.Add(label + ": keys are not sorted by t (keys[" + k + "]).");
                    if (!string.IsNullOrEmpty(key.ease) && !AvarnethStartupMath.IsKnownEase(key.ease))
                        warnings.Add(label + ": unknown ease '" + key.ease + "' (treated as 'linear').");
                }
            }

            for (int i = 0; i < data.particleSprites.Length; i++)
                CheckRelativePath("particleSprites[" + i + "]", data.particleSprites[i], false, errors);

            for (int i = 0; i < data.particles.Length; i++)
            {
                ParticleJson p = data.particles[i];
                if (p == null)
                {
                    errors.Add("particles[" + i + "] is null.");
                    continue;
                }

                if (p.sprite < 0 || p.sprite >= data.particleSprites.Length)
                    errors.Add("particles[" + i + "] references particle sprite " + p.sprite + " which does not exist.");
                if (!(p.life > 0f))
                    warnings.Add("particles[" + i + "] has no lifetime and is never shown.");
            }

            return result;
        }

        private static void CheckRelativePath(string label, string path, bool optional, List<string> errors)
        {
            if (string.IsNullOrEmpty(path))
            {
                if (!optional) errors.Add(label + " is empty.");
                return;
            }

            if (path.IndexOf('\\') >= 0 || path.IndexOf(':') >= 0 || path.StartsWith("/", StringComparison.Ordinal))
            {
                errors.Add(label + " ('" + path + "') must be a relative path with forward slashes.");
                return;
            }

            foreach (string segment in path.Split('/'))
            {
                if (segment.Length == 0 || segment == "." || segment == "..")
                {
                    errors.Add(label + " ('" + path + "') must stay inside Importable_Assets.");
                    return;
                }
            }
        }

        /// <summary>Same rules as <see cref="CheckRelativePath"/>: relative, forward slashes, no empty, "." or ".." segment.</summary>
        internal static bool IsSafeRelativePath(string path)
        {
            if (string.IsNullOrEmpty(path)) return false;
            if (path.IndexOf('\\') >= 0 || path.IndexOf(':') >= 0 || path.StartsWith("/", StringComparison.Ordinal)) return false;
            foreach (string segment in path.Split('/'))
                if (segment.Length == 0 || segment == "." || segment == "..") return false;
            return true;
        }

        internal static IEnumerable<string> ReferencedSpritePaths(TimelineJson data)
        {
            foreach (LayerJson layer in data.layers)
            {
                if (layer == null) continue;
                if (!string.IsNullOrEmpty(layer.sprite)) yield return layer.sprite;
                if (layer.frames == null) continue;
                foreach (string frame in layer.frames)
                    if (!string.IsNullOrEmpty(frame)) yield return frame;
            }

            foreach (string sprite in data.particleSprites)
                if (!string.IsNullOrEmpty(sprite)) yield return sprite;
        }

        internal static ResolvedSprites ResolveSprites(InstallRoot root, TimelineJson data)
        {
            var result = new ResolvedSprites();
            foreach (string relative in ReferencedSpritePaths(data))
            {
                if (result.ByPath.ContainsKey(relative)) continue;

                string assetPath = root.RootFolder + "/" + relative;
                Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(assetPath);
                result.ByPath[relative] = sprite;
                if (sprite != null)
                {
                    if (AssetImporter.GetAtPath(assetPath) is TextureImporter importer)
                    {
                        try
                        {
                            importer.GetSourceTextureWidthAndHeight(out int w, out int h);
                            Rect r = sprite.rect;
                            if (AvarnethStartupMath.Snap(r.width) != w || AvarnethStartupMath.Snap(r.height) != h)
                                result.Warnings.Add(relative + ": sprite is " + r.width + "x" + r.height + " but the source PNG is " + w + "x" + h + " (check Max Size / Sprite Mode).");
                        }
                        catch (InvalidOperationException)
                        {
                            // Texture still importing; size check skipped.
                        }
                    }

                    continue;
                }

                if (AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath) != null)
                    result.Missing.Add(relative + " (not imported as Sprite - run Configure Sprite Import Settings)");
                else
                    result.Missing.Add(relative + " (file not found)");
            }

            foreach (LayerJson layer in data.layers)
            {
                if (layer == null || layer.frames == null || layer.frames.Length < 2) continue;
                Sprite first = result.Get(layer.frames[0]);
                if (first == null) continue;
                for (int f = 1; f < layer.frames.Length; f++)
                {
                    Sprite frame = result.Get(layer.frames[f]);
                    if (frame != null && frame.rect.size != first.rect.size)
                    {
                        result.Warnings.Add("Layer '" + layer.id + "': flipbook frames differ in size (" + layer.frames[f] + ").");
                        break;
                    }
                }
            }

            return result;
        }

        // ------------------------------------------------------------------ import settings

        /// <summary>
        /// Contract PNGs directly in <c>root/sub</c>: files named AVE_*.png, no subfolders (FindAssets with a folder
        /// list also searches subfolders, see 6000.6 AssetDatabaseSearching.cs:26-36), nothing outside the root.
        /// </summary>
        internal static List<string> CollectContractPngs(InstallRoot root, string sub)
        {
            var result = new List<string>();
            string folder = root.RootFolder + "/" + sub;
            if (!AssetDatabase.IsValidFolder(folder)) return result;

            foreach (string guid in AssetDatabase.FindAssets("t:Texture2D", new[] { folder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (string.IsNullOrEmpty(path) || result.Contains(path)) continue;
                if (!string.Equals(ParentPath(path), folder, StringComparison.Ordinal)) continue;
                string file = FileName(path);
                if (!file.StartsWith(ContractFilePrefix, StringComparison.Ordinal)) continue;
                if (!file.EndsWith(".png", StringComparison.OrdinalIgnoreCase)) continue;
                result.Add(path);
            }

            result.Sort(StringComparer.Ordinal);
            return result;
        }

        /// <summary>
        /// Sprite PNGs the contract names: AVE_*.png directly in Layers/, Frames/, Particles/ plus every PNG in those
        /// folders that <paramref name="data"/> references (pass null when the timeline is invalid).
        /// </summary>
        internal static List<string> CollectSpritePngs(InstallRoot root, TimelineJson data)
        {
            var set = new SortedSet<string>(StringComparer.Ordinal);
            foreach (string sub in SpriteFolders)
                set.UnionWith(CollectContractPngs(root, sub));

            if (data != null)
            {
                foreach (string relative in ReferencedSpritePaths(data))
                {
                    if (!IsSafeRelativePath(relative) || !relative.EndsWith(".png", StringComparison.OrdinalIgnoreCase)) continue;
                    int slash = relative.IndexOf('/');
                    if (slash <= 0 || Array.IndexOf(SpriteFolders, relative.Substring(0, slash)) < 0) continue;
                    string assetPath = root.RootFolder + "/" + relative;
                    if (AssetImporter.GetAtPath(assetPath) != null) set.Add(assetPath);
                }
            }

            return new List<string>(set);
        }

        /// <summary>Icon PNGs the contract names: Icons/AVE_Icon_&lt;size&gt;.png.</summary>
        internal static List<string> CollectIconPngs(InstallRoot root)
        {
            return new List<string>(FindIconFiles(root).Values);
        }

        internal static string RelativeToRoot(InstallRoot root, string assetPath)
        {
            string prefix = root.RootFolder + "/";
            return assetPath.StartsWith(prefix, StringComparison.Ordinal) ? assetPath.Substring(prefix.Length) : assetPath;
        }

        internal static List<string> RelativeToRoot(InstallRoot root, IEnumerable<string> assetPaths)
        {
            var result = new List<string>();
            foreach (string path in assetPaths) result.Add(RelativeToRoot(root, path));
            return result;
        }

        /// <summary>Appends every deviation from the contract sprite import settings to <paramref name="problems"/>.</summary>
        internal static void CheckSpriteSettings(TextureImporter ti, List<string> problems)
        {
            if (ti.textureType != TextureImporterType.Sprite) problems.Add("Texture Type is " + ti.textureType + " (expected Sprite)");
            if (ti.spriteImportMode != SpriteImportMode.Single) problems.Add("Sprite Mode is " + ti.spriteImportMode + " (expected Single)");
            if (ti.filterMode != FilterMode.Point) problems.Add("Filter Mode is " + ti.filterMode + " (expected Point)");
            if (ti.mipmapEnabled) problems.Add("Generate Mip Maps is on");
            if (ti.textureCompression != TextureImporterCompression.Uncompressed) problems.Add("Compression is " + ti.textureCompression + " (expected None)");
            if (ti.wrapModeU != TextureWrapMode.Clamp || ti.wrapModeV != TextureWrapMode.Clamp) problems.Add("Wrap Mode is not Clamp");
            if (ti.npotScale != TextureImporterNPOTScale.None) problems.Add("Non-Power of 2 is " + ti.npotScale + " (expected None)");
            if (!ti.sRGBTexture) problems.Add("sRGB is off");
            if (!ti.alphaIsTransparency) problems.Add("Alpha Is Transparency is off");
            if (!Mathf.Approximately(ti.spritePixelsPerUnit, SpritePixelsPerUnit)) problems.Add("Pixels Per Unit is " + ti.spritePixelsPerUnit.ToString(CultureInfo.InvariantCulture) + " (expected 100)");
            if (ti.maxTextureSize < MinMaxTextureSize) problems.Add("Max Size is " + ti.maxTextureSize + " (expected >= 2048)");

            var settings = new TextureImporterSettings();
            ti.ReadTextureSettings(settings);
            if (settings.spriteMeshType != SpriteMeshType.FullRect) problems.Add("Mesh Type is " + settings.spriteMeshType + " (expected Full Rect)");

            CheckStandaloneOverride(ti, problems);
        }

        /// <summary>Appends every deviation from the icon import settings to <paramref name="problems"/>.</summary>
        internal static void CheckIconSettings(TextureImporter ti, List<string> problems)
        {
            if (ti.textureType != TextureImporterType.Default) problems.Add("Texture Type is " + ti.textureType + " (expected Default)");
            if (ti.filterMode != FilterMode.Point) problems.Add("Filter Mode is " + ti.filterMode + " (expected Point)");
            if (ti.mipmapEnabled) problems.Add("Generate Mip Maps is on");
            if (ti.textureCompression != TextureImporterCompression.Uncompressed) problems.Add("Compression is " + ti.textureCompression + " (expected None)");
            if (ti.npotScale != TextureImporterNPOTScale.None) problems.Add("Non-Power of 2 is " + ti.npotScale + " (expected None)");
            if (ti.maxTextureSize < MinMaxTextureSize) problems.Add("Max Size is " + ti.maxTextureSize + " (expected >= 2048)");
            CheckStandaloneOverride(ti, problems);
        }

        private static void CheckStandaloneOverride(TextureImporter ti, List<string> problems)
        {
            TextureImporterPlatformSettings standalone = ti.GetPlatformTextureSettings("Standalone");
            if (standalone != null && standalone.overridden) problems.Add("has a Standalone platform override");
        }

        private static bool ApplySpriteSettings(TextureImporter ti)
        {
            var problems = new List<string>();
            CheckSpriteSettings(ti, problems);
            if (problems.Count == 0) return false;

            ti.textureType = TextureImporterType.Sprite;
            ti.spriteImportMode = SpriteImportMode.Single;
            ti.filterMode = FilterMode.Point;
            ti.mipmapEnabled = false;
            ti.textureCompression = TextureImporterCompression.Uncompressed;
            ti.wrapMode = TextureWrapMode.Clamp;
            ti.npotScale = TextureImporterNPOTScale.None;
            ti.sRGBTexture = true;
            ti.alphaIsTransparency = true;
            ti.spritePixelsPerUnit = SpritePixelsPerUnit;
            if (ti.maxTextureSize < MinMaxTextureSize) ti.maxTextureSize = MinMaxTextureSize;

            var settings = new TextureImporterSettings();
            ti.ReadTextureSettings(settings);
            if (settings.spriteMeshType != SpriteMeshType.FullRect)
            {
                settings.spriteMeshType = SpriteMeshType.FullRect;
                ti.SetTextureSettings(settings);
            }

            DisableStandaloneOverride(ti);
            return true;
        }

        private static bool ApplyIconSettings(TextureImporter ti)
        {
            var problems = new List<string>();
            CheckIconSettings(ti, problems);
            if (problems.Count == 0) return false;

            ti.textureType = TextureImporterType.Default;
            ti.filterMode = FilterMode.Point;
            ti.mipmapEnabled = false;
            ti.textureCompression = TextureImporterCompression.Uncompressed;
            ti.npotScale = TextureImporterNPOTScale.None;
            if (ti.maxTextureSize < MinMaxTextureSize) ti.maxTextureSize = MinMaxTextureSize;
            DisableStandaloneOverride(ti);
            return true;
        }

        private static void DisableStandaloneOverride(TextureImporter ti)
        {
            TextureImporterPlatformSettings standalone = ti.GetPlatformTextureSettings("Standalone");
            if (standalone == null || !standalone.overridden) return;
            standalone.overridden = false;
            ti.SetPlatformTextureSettings(standalone);
        }

        /// <summary>
        /// Applies the contract import settings to the contract files of the root only (see <see cref="CollectSpritePngs"/>
        /// and <see cref="CollectIconPngs"/>). When <paramref name="interactive"/> is true, nothing is changed before the
        /// user confirmed a dialog that names the root and the number of files that will change.
        /// </summary>
        internal static void ConfigureImportSettings(InstallRoot root, bool interactive)
        {
            var missingFolders = new List<string>();
            foreach (string sub in SpriteFolders)
                if (!AssetDatabase.IsValidFolder(root.RootFolder + "/" + sub)) missingFolders.Add(sub + "/");
            if (!AssetDatabase.IsValidFolder(root.RootFolder + "/" + IconFolder)) missingFolders.Add(IconFolder + "/");

            ParsedTimeline parsed = ParseTimeline(root);
            List<string> spritePaths = CollectSpritePngs(root, parsed.IsValid ? parsed.Data : null);
            List<string> iconPaths = CollectIconPngs(root);

            // Determine what would change before touching anything.
            var spriteChanges = new List<string>();
            var iconChanges = new List<string>();
            var failed = new List<string>();
            var problems = new List<string>();
            foreach (string path in spritePaths)
            {
                if (!(AssetImporter.GetAtPath(path) is TextureImporter ti)) { failed.Add(path); continue; }
                problems.Clear();
                CheckSpriteSettings(ti, problems);
                if (problems.Count > 0) spriteChanges.Add(path);
            }

            foreach (string path in iconPaths)
            {
                if (!(AssetImporter.GetAtPath(path) is TextureImporter ti)) { failed.Add(path); continue; }
                problems.Clear();
                CheckIconSettings(ti, problems);
                if (problems.Count > 0) iconChanges.Add(path);
            }

            int planned = spriteChanges.Count + iconChanges.Count;
            if (planned > 0 && interactive)
            {
                string confirm =
                    "Apply the AVARNETH import settings to " + planned + " texture(s) in\n" + root.RootFolder + "?\n\n" +
                    "Sprites (Layers, Frames, Particles): " + spriteChanges.Count + " of " + spritePaths.Count + "\n" +
                    "Icons (Icons/AVE_Icon_<size>.png): " + iconChanges.Count + " of " + iconPaths.Count + "\n\n" +
                    "Only AVE_*.png files directly in these folders and the PNGs named in Animation_Timeline.json are changed. " +
                    "Edit > Undo cannot revert import settings." +
                    (HasStandardRootName(root) ? string.Empty : "\n\nNote: this folder is not named " + StandardRootName + ".");
                if (!Confirm(DialogTitle, confirm, "Apply", "Cancel")) return;
            }

            int changed = 0;
            if (planned > 0)
            {
                AssetDatabase.StartAssetEditing();
                try
                {
                    foreach (string path in spriteChanges)
                    {
                        if (!(AssetImporter.GetAtPath(path) is TextureImporter ti) || !ApplySpriteSettings(ti)) continue;
                        ti.SaveAndReimport();
                        changed++;
                    }

                    foreach (string path in iconChanges)
                    {
                        if (!(AssetImporter.GetAtPath(path) is TextureImporter ti) || !ApplyIconSettings(ti)) continue;
                        ti.SaveAndReimport();
                        changed++;
                    }
                }
                finally
                {
                    AssetDatabase.StopAssetEditing();
                }
            }

            string summary = "Root: " + root.RootFolder + "\n" +
                             "Sprite PNGs: " + spritePaths.Count + ", icon PNGs: " + iconPaths.Count + ", reimported: " + changed + "." +
                             (missingFolders.Count > 0 ? "\nMissing folders: " + string.Join(", ", missingFolders) : string.Empty) +
                             (parsed.IsValid ? string.Empty : "\nAnimation_Timeline.json is invalid; only AVE_*.png files were considered.");

            var log = new StringBuilder("[AVARNETH Startup] Configure Sprite Import Settings\n" + summary);
            foreach (string path in spriteChanges) log.Append("\n  reimported (sprite): " + path);
            foreach (string path in iconChanges) log.Append("\n  reimported (icon): " + path);
            foreach (string path in failed) log.Append("\n  no TextureImporter: " + path);
            Debug.Log(log.ToString());

            if (!interactive) return;
            if (failed.Count > 0) Alert(DialogTitle, ComposeListDialog(summary + "\n\nNo TextureImporter for:\n", RelativeToRoot(root, failed), string.Empty));
            else Alert(DialogTitle, summary);
        }

        // ------------------------------------------------------------------ prefab

        /// <summary>Creates or updates &lt;parent of root&gt;/Prefabs/AvarnethStartup.prefab. Never writes a partial prefab.</summary>
        internal static bool CreateOrUpdatePrefab(InstallRoot root, bool interactive)
        {
            ParsedTimeline parsed = ParseTimeline(root);
            if (!parsed.IsValid)
            {
                return Abort(interactive, "Animation_Timeline.json is invalid. The prefab was not written.\n\n", parsed.Errors);
            }

            ResolvedSprites sprites = ResolveSprites(root, parsed.Data);
            if (sprites.Missing.Count > 0)
            {
                return Abort(interactive, sprites.Missing.Count + " sprite(s) are missing. The prefab was not written.\n\n", sprites.Missing);
            }

            GameObject existing = AssetDatabase.LoadAssetAtPath<GameObject>(root.PrefabPath);
            if (existing != null && existing.GetComponent<AvarnethStartupAnimation>() == null)
            {
                return Abort(interactive, "'" + root.PrefabPath + "' exists but is not an AVARNETH startup prefab. Move or delete it first.");
            }

            if (!EnsureFolder(root.ParentFolder, "Prefabs"))
            {
                return Abort(interactive, "The folder '" + root.PrefabFolder + "' could not be created.");
            }

            bool success = false;
            string error = null;

            try
            {
                if (existing != null)
                {
                    // Update in place: the root and its components keep their file IDs, so overrides on scene
                    // instances (e.g. the assigned login CanvasGroup) stay valid. Nothing is saved on error.
                    GameObject contents = PrefabUtility.LoadPrefabContents(root.PrefabPath);
                    try
                    {
                        error = Populate(contents, parsed.Data, sprites, false);
                        if (error == null) PrefabUtility.SaveAsPrefabAsset(contents, root.PrefabPath, out success);
                    }
                    finally
                    {
                        PrefabUtility.UnloadPrefabContents(contents);
                    }
                }
                else
                {
                    // Build in an isolated preview scene so the open scenes are never touched.
                    Scene preview = EditorSceneManager.NewPreviewScene();
                    try
                    {
                        var go = new GameObject(PrefabRootName, typeof(RectTransform));
                        SceneManager.MoveGameObjectToScene(go, preview);
                        error = Populate(go, parsed.Data, sprites, true);
                        if (error == null) PrefabUtility.SaveAsPrefabAsset(go, root.PrefabPath, out success);
                    }
                    finally
                    {
                        EditorSceneManager.ClosePreviewScene(preview);
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogException(e);
                error = e.GetType().Name + ": " + e.Message;
                success = false;
            }

            if (error != null || !success)
            {
                return Abort(interactive, "The prefab was not written. " + (error ?? "PrefabUtility.SaveAsPrefabAsset failed."));
            }

            GameObject asset = AssetDatabase.LoadAssetAtPath<GameObject>(root.PrefabPath);
            if (asset != null) EditorGUIUtility.PingObject(asset);

            var warnings = new List<string>();
            int wrongImports = CountWrongSpriteImports(root, parsed.Data);
            if (wrongImports > 0) warnings.Add(wrongImports + " texture(s) differ from the contract import settings - run Configure Sprite Import Settings.");
            warnings.AddRange(parsed.Warnings);
            warnings.AddRange(sprites.Warnings);

            string message = (existing != null ? "Updated " : "Created ") + root.PrefabPath + "\n" +
                             parsed.Data.layers.Length + " layer(s), " + parsed.Data.particles.Length + " particle(s).";
            string head = message + (warnings.Count > 0 ? "\n\nWarnings:\n" : string.Empty);

            Debug.Log("[AVARNETH Startup] " + head + string.Join("\n", warnings));
            if (interactive) Alert(DialogTitle, warnings.Count > 0 ? ComposeListDialog(head, warnings, string.Empty) : message);
            return true;
        }

        private static bool Abort(bool interactive, string message, IList<string> lines = null)
        {
            Debug.LogError("[AVARNETH Startup] " + message + (lines != null ? string.Join("\n", lines) : string.Empty));
            if (interactive) Alert(DialogTitle, lines != null ? ComposeListDialog(message, lines, string.Empty) : message);
            return false;
        }

        private static int CountWrongSpriteImports(InstallRoot root, TimelineJson data)
        {
            int count = 0;
            var problems = new List<string>();
            foreach (string path in CollectSpritePngs(root, data))
            {
                if (!(AssetImporter.GetAtPath(path) is TextureImporter ti)) continue;
                problems.Clear();
                CheckSpriteSettings(ti, problems);
                if (problems.Count > 0) count++;
            }

            return count;
        }

        private static bool EnsureFolder(string parent, string name)
        {
            string path = parent + "/" + name;
            if (AssetDatabase.IsValidFolder(path)) return true;
            string guid = AssetDatabase.CreateFolder(parent, name);
            return !string.IsNullOrEmpty(guid) && AssetDatabase.IsValidFolder(path);
        }

        /// <summary>Builds the overlay hierarchy below <paramref name="root"/>. Returns an error message or null.</summary>
        private static string Populate(GameObject root, TimelineJson data, ResolvedSprites sprites, bool created)
        {
            int uiLayer = LayerMask.NameToLayer("UI");
            if (uiLayer >= 0) root.layer = uiLayer;

            int canvasWidth = data.canvasWidth;
            int canvasHeight = data.canvasHeight;
            RectInt bounds = data.contentBounds != null && data.contentBounds.width > 0 && data.contentBounds.height > 0
                ? new RectInt(data.contentBounds.x, data.contentBounds.y, data.contentBounds.width, data.contentBounds.height)
                : new RectInt(0, 0, canvasWidth, canvasHeight);

            // Root: Canvas (overlay) + CanvasScaler (constant pixel size) + GraphicRaycaster + blocker Image + component.
            GetOrAdd<RectTransform>(root);

            bool canvasAdded = root.GetComponent<Canvas>() == null;
            Canvas canvas = GetOrAdd<Canvas>(root);
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.pixelPerfect = false;
            if (created || canvasAdded) canvas.sortingOrder = DefaultSortingOrder;

            CanvasScaler scaler = GetOrAdd<CanvasScaler>(root);
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ConstantPixelSize;
            scaler.scaleFactor = 1f;
            scaler.referencePixelsPerUnit = 100f;

            GetOrAdd<GraphicRaycaster>(root);

            // Saved switched off; Play() enables it (and its raycast target) only while the overlay plays.
            Image blocker = GetOrAdd<Image>(root);
            blocker.sprite = null;
            blocker.color = new Color(0f, 0f, 0f, 0f);
            blocker.raycastTarget = false;
            blocker.enabled = false;
            blocker.canvasRenderer.cullTransparentMesh = false;

            AvarnethStartupAnimation animation = GetOrAdd<AvarnethStartupAnimation>(root);

            // Regenerate the art subtree; other children added by the user are kept.
            for (int i = root.transform.childCount - 1; i >= 0; i--)
            {
                Transform child = root.transform.GetChild(i);
                if (child.name == ArtRootName || (animation.ArtRoot != null && child == animation.ArtRoot.transform))
                    Object.DestroyImmediate(child.gameObject);
            }

            RectTransform artRoot = CreateRect(ArtRootName, root.transform, uiLayer);
            artRoot.SetSiblingIndex(0);
            artRoot.anchorMin = new Vector2(0.5f, 0.5f);
            artRoot.anchorMax = new Vector2(0.5f, 0.5f);
            artRoot.pivot = new Vector2(0.5f, 0.5f);
            artRoot.anchoredPosition = Vector2.zero;
            artRoot.sizeDelta = new Vector2(canvasWidth, canvasHeight);
            float editScale = data.pixelScaleAt1080p > 0 ? data.pixelScaleAt1080p : 1f;
            artRoot.localScale = new Vector3(editScale, editScale, 1f);

            // Render order: ascending order, ties keep array order; particles between order < 100 and >= 100.
            var sorted = new List<int>(data.layers.Length);
            for (int i = 0; i < data.layers.Length; i++) sorted.Add(i);
            sorted.Sort((a, b) =>
            {
                int c = data.layers[a].order.CompareTo(data.layers[b].order);
                return c != 0 ? c : a.CompareTo(b);
            });

            var bindings = new List<StartupLayerBinding>(sorted.Count);
            RectTransform particleContainer = null;

            foreach (int index in sorted)
            {
                LayerJson layer = data.layers[index];
                if (particleContainer == null && layer.order >= ParticleOrderSplit)
                    particleContainer = CreateParticleContainer(artRoot, canvasWidth, canvasHeight, uiLayer);

                Sprite staticSprite = sprites.Get(layer.sprite);
                var frames = new Sprite[layer.frames.Length];
                for (int f = 0; f < frames.Length; f++)
                {
                    frames[f] = sprites.Get(layer.frames[f]);
                    if (frames[f] == null) return "Layer '" + layer.id + "': frame sprite '" + layer.frames[f] + "' is missing.";
                }

                Sprite initial = staticSprite != null ? staticSprite : (frames.Length > 0 ? frames[0] : null);
                if (initial == null) return "Layer '" + layer.id + "' has no sprite.";

                string name = string.IsNullOrEmpty(layer.id) ? "Layer_" + index : layer.id;
                Image image = CreateImage(name, artRoot, initial, uiLayer);
                image.rectTransform.anchoredPosition = new Vector2(layer.x, -layer.y);

                var keys = new StartupKey[layer.keys.Length];
                for (int k = 0; k < keys.Length; k++)
                {
                    KeyJson key = layer.keys[k];
                    keys[k] = new StartupKey
                    {
                        t = key.t,
                        alpha = key.alpha,
                        dx = key.dx,
                        dy = key.dy,
                        ease = AvarnethStartupMath.ParseEase(key.ease),
                    };
                }

                bindings.Add(new StartupLayerBinding
                {
                    id = layer.id,
                    image = image,
                    sprite = staticSprite,
                    frames = frames,
                    frameStart = layer.frameStart,
                    frameEnd = layer.frameEnd,
                    afterFrames = AvarnethStartupMath.ParseAfterFrames(layer.afterFrames),
                    position = new Vector2Int(layer.x, layer.y),
                    order = layer.order,
                    keys = keys,
                });
            }

            if (particleContainer == null)
                particleContainer = CreateParticleContainer(artRoot, canvasWidth, canvasHeight, uiLayer);

            var particleSpriteList = new Sprite[data.particleSprites.Length];
            for (int i = 0; i < particleSpriteList.Length; i++)
            {
                particleSpriteList[i] = sprites.Get(data.particleSprites[i]);
                if (particleSpriteList[i] == null) return "Particle sprite '" + data.particleSprites[i] + "' is missing.";
            }

            var particleData = new StartupParticleData[data.particles.Length];
            var particleImages = new Image[data.particles.Length];
            for (int i = 0; i < particleData.Length; i++)
            {
                ParticleJson p = data.particles[i];
                particleData[i] = new StartupParticleData
                {
                    sprite = p.sprite,
                    t0 = p.t0,
                    life = p.life,
                    x = p.x,
                    y = p.y,
                    vx = p.vx,
                    vy = p.vy,
                    ay = p.ay,
                    alpha = p.alpha,
                    fadeIn = p.fadeIn,
                    fadeOut = p.fadeOut,
                };

                Sprite sprite = particleSpriteList[p.sprite];
                Image image = CreateImage("P" + i.ToString("000", CultureInfo.InvariantCulture), particleContainer, sprite, uiLayer);
                AvarnethStartupMath.ParticleTopLeft(p.x, p.y, AvarnethStartupMath.Snap(sprite.rect.width), AvarnethStartupMath.Snap(sprite.rect.height), out int left, out int top);
                image.rectTransform.anchoredPosition = new Vector2(left, -top);
                particleImages[i] = image;
            }

            animation.SetTimelineData(data.duration, new Vector2Int(canvasWidth, canvasHeight), bounds, artRoot,
                bindings.ToArray(), particleData, particleImages, particleSpriteList, blocker);

            // Evaluating t = 0 validates every binding. The prefab is then saved neutral (all Images and the blocker
            // off), so an overlay that is disabled or never started cannot cover the login; Play() applies t = 0
            // before the first frame is rendered.
            if (!animation.EvaluateAt(0f)) return "The generated bindings are incomplete (see Console).";
            animation.ClearPreview();
            return null;
        }

        private static RectTransform CreateParticleContainer(RectTransform artRoot, int width, int height, int uiLayer)
        {
            RectTransform container = CreateRect(ParticlesContainerName, artRoot, uiLayer);
            SetTopLeft(container);
            container.anchoredPosition = Vector2.zero;
            container.sizeDelta = new Vector2(width, height);
            return container;
        }

        private static RectTransform CreateRect(string name, Transform parent, int uiLayer)
        {
            var go = new GameObject(name, typeof(RectTransform));
            if (uiLayer >= 0) go.layer = uiLayer;
            var rect = (RectTransform)go.transform;
            rect.SetParent(parent, false);
            rect.localScale = Vector3.one;
            return rect;
        }

        private static Image CreateImage(string name, Transform parent, Sprite sprite, int uiLayer)
        {
            RectTransform rect = CreateRect(name, parent, uiLayer);
            SetTopLeft(rect);
            Image image = rect.gameObject.AddComponent<Image>();
            image.sprite = sprite;
            image.type = Image.Type.Simple;
            image.preserveAspect = false;
            image.useSpriteMesh = false;
            image.raycastTarget = false;
            image.color = Color.white;
            Rect r = sprite.rect;
            rect.sizeDelta = new Vector2(r.width, r.height); // native size (sprite PPU 100 == canvas reference PPU 100)
            return image;
        }

        private static void SetTopLeft(RectTransform rect)
        {
            var topLeft = new Vector2(0f, 1f);
            rect.anchorMin = topLeft;
            rect.anchorMax = topLeft;
            rect.pivot = topLeft;
        }

        private static T GetOrAdd<T>(GameObject go) where T : Component
        {
            T component = go.GetComponent<T>();
            return component != null ? component : go.AddComponent<T>();
        }

        // ------------------------------------------------------------------ scene

        /// <summary>Components of type T in all loaded scenes, including inactive objects.</summary>
        internal static List<T> FindInLoadedScenes<T>() where T : Component
        {
            var result = new List<T>();
            for (int i = 0; i < SceneManager.sceneCount; i++)
            {
                Scene scene = SceneManager.GetSceneAt(i);
                if (!scene.isLoaded) continue;
                foreach (GameObject go in scene.GetRootGameObjects())
                    result.AddRange(go.GetComponentsInChildren<T>(true));
            }

            return result;
        }

        /// <summary>
        /// True when a loaded scene contains an enabled EventSystem on an active GameObject. Uses the serialized
        /// state: Behaviour.isActiveAndEnabled is the native IsAddedToManager (6000.6 Behaviour.bindings.cs:20-24),
        /// which is not a reliable "will be active at runtime" signal in Edit Mode.
        /// </summary>
        internal static bool HasActiveEventSystem()
        {
            foreach (EventSystem es in FindInLoadedScenes<EventSystem>())
                if (es.enabled && es.gameObject.activeInHierarchy) return true;
            return false;
        }

        internal static void AddOverlayToOpenScene()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                Alert(DialogTitle, "Exit Play Mode before adding the overlay.");
                return;
            }

            List<AvarnethStartupAnimation> existing = FindInLoadedScenes<AvarnethStartupAnimation>();
            if (existing.Count > 0)
            {
                AvarnethStartupAnimation first = existing[0];
                EditorGUIUtility.PingObject(first);
                Alert(DialogTitle,
                    "An AVARNETH startup overlay already exists in the loaded scenes:\n\n" + first.gameObject.scene.name + ": " + Shorten(HierarchyPath(first.transform), 200) +
                    "\n\nNothing was changed.");
                return;
            }

            if (!TryResolveRoot(true, out InstallRoot root)) return;

            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(root.PrefabPath);
            if (prefab == null || prefab.GetComponent<AvarnethStartupAnimation>() == null)
            {
                if (!Confirm(DialogTitle, "The startup prefab '" + root.PrefabPath + "' does not exist yet.\n\nCreate it now?", "Create Prefab", "Cancel"))
                    return;
                if (!CreateOrUpdatePrefab(root, true)) return;
                prefab = AssetDatabase.LoadAssetAtPath<GameObject>(root.PrefabPath);
                if (prefab == null) return;
            }

            Scene scene = SceneManager.GetActiveScene();
            if (!scene.IsValid() || !scene.isLoaded)
            {
                Alert(DialogTitle, "There is no open scene. Open the existing bootstrap / login scene first.");
                return;
            }

            // Remember the selection before anything changes it.
            GameObject selected = Selection.activeGameObject;
            CanvasGroup selectedGroup = selected != null && !EditorUtility.IsPersistent(selected) ? selected.GetComponent<CanvasGroup>() : null;

            string sceneLabel = string.IsNullOrEmpty(scene.name) ? "(untitled)" : scene.name;
            if (!Confirm(DialogTitle,
                    "Add an instance of\n" + root.PrefabPath + "\nto the active scene '" + sceneLabel + "'?\n\n" +
                    "Only the overlay object is added. The scene is marked as modified but NOT saved.",
                    "Add Overlay", "Cancel"))
                return;

            int undoGroup = Undo.GetCurrentGroup();
            Undo.SetCurrentGroupName("Add AVARNETH Startup Overlay");

            var instance = PrefabUtility.InstantiatePrefab(prefab, scene) as GameObject;
            if (instance == null)
            {
                Alert(DialogTitle, "The prefab could not be instantiated.");
                return;
            }

            Undo.RegisterCreatedObjectUndo(instance, "Add AVARNETH Startup Overlay");
            var animation = instance.GetComponent<AvarnethStartupAnimation>();

            if (selectedGroup != null && animation != null)
            {
                string groupName = Shorten(selected.name, 80);
                if (selectedGroup.gameObject.scene != scene)
                {
                    Alert(DialogTitle,
                        "The selected CanvasGroup '" + groupName + "' is in another scene. Cross-scene references are not supported; assign the Login Canvas Group manually.");
                }
                else if (Confirm(DialogTitle,
                             "The selected GameObject '" + groupName + "' has a CanvasGroup.\n\n" +
                             "Assign it as Login Canvas Group? While the overlay plays, Interactable and Blocks Raycasts are switched off; " +
                             "the original values are restored afterwards (a value your code switched on meanwhile is kept).\n\n" +
                             "Use a CanvasGroup that your login code does not change itself.",
                             "Assign", "Don't Assign"))
                {
                    var so = new SerializedObject(animation);
                    SerializedProperty property = so.FindProperty("loginCanvasGroup");
                    if (property != null)
                    {
                        property.objectReferenceValue = selectedGroup;
                        so.ApplyModifiedProperties();
                    }
                }
            }

            EditorSceneManager.MarkSceneDirty(scene);
            Undo.CollapseUndoOperations(undoGroup);
            Selection.activeGameObject = instance;
            EditorGUIUtility.PingObject(instance);

            if (animation != null && animation.SkipOnClick && !HasActiveEventSystem())
            {
                Alert(DialogTitle,
                    "Skip On Click is enabled, but no active EventSystem was found in the loaded scenes.\n\n" +
                    "Clicks can only skip the overlay when an EventSystem exists at runtime. If your bootstrap creates one at runtime this is fine; " +
                    "no EventSystem is created automatically.");
            }
        }

        private static string HierarchyPath(Transform t)
        {
            string path = t.name;
            for (Transform p = t.parent; p != null; p = p.parent) path = p.name + "/" + path;
            return path;
        }

        // ------------------------------------------------------------------ validation

        internal static void ValidateInstallation(bool interactive)
        {
            var errors = new List<string>();
            var warnings = new List<string>();
            var info = new List<string>();
            var details = new List<string>(); // Console only

            var rejected = new List<string>();
            List<string> candidates = FindTimelineCandidates(rejected);
            info.Add("Timelines found: " + candidates.Count + (candidates.Count > 0 ? " (" + string.Join(", ", candidates) + ")" : string.Empty));
            if (rejected.Count > 0) warnings.Add("Ignored timeline(s) outside a subfolder of Assets/: " + string.Join(", ", rejected));

            if (!TryResolveRoot(out InstallRoot root, out string rootError, out bool _))
            {
                errors.Add("The importable asset root could not be located: " + rootError);
                Report(interactive, errors, warnings, info, details);
                return;
            }

            info.Add("Root: " + root.RootFolder);
            info.Add("Prefab path: " + root.PrefabPath);
            if (!HasStandardRootName(root)) warnings.Add("The root folder is not named " + StandardRootName + ": " + root.RootFolder);

            foreach (string sub in SpriteFolders)
                if (!AssetDatabase.IsValidFolder(root.RootFolder + "/" + sub)) errors.Add("Folder missing: " + root.RootFolder + "/" + sub);
            if (!AssetDatabase.IsValidFolder(root.RootFolder + "/" + IconFolder)) warnings.Add("Folder missing: " + root.RootFolder + "/" + IconFolder + " (icons cannot be assigned)");

            ParsedTimeline parsed = ParseTimeline(root);
            errors.AddRange(parsed.Errors);
            warnings.AddRange(parsed.Warnings);

            if (parsed.Data != null)
            {
                TimelineJson d = parsed.Data;
                int frameCount = 0;
                foreach (LayerJson layer in d.layers)
                    if (layer != null && layer.frames != null) frameCount += layer.frames.Length;
                info.Add("Timeline: duration " + d.duration.ToString(CultureInfo.InvariantCulture) + " s, canvas " + d.canvasWidth + "x" + d.canvasHeight +
                         ", " + d.layers.Length + " layer(s), " + frameCount + " flipbook frame(s), " + d.particles.Length + " particle(s).");

                ResolvedSprites sprites = ResolveSprites(root, d);
                foreach (string missing in sprites.Missing) errors.Add("Sprite missing: " + missing);
                warnings.AddRange(sprites.Warnings);
            }

            // Import settings: one summary line per group for the dialog, one line per file for the Console.
            var problems = new List<string>();
            List<string> spritePaths = CollectSpritePngs(root, parsed.IsValid ? parsed.Data : null);
            int wrongSprites = 0;
            foreach (string path in spritePaths)
            {
                if (!(AssetImporter.GetAtPath(path) is TextureImporter ti)) continue;
                problems.Clear();
                CheckSpriteSettings(ti, problems);
                if (problems.Count == 0) continue;
                wrongSprites++;
                details.Add("Import settings " + RelativeToRoot(root, path) + ": " + string.Join("; ", problems));
            }

            List<string> iconPaths = CollectIconPngs(root);
            int wrongIcons = 0;
            foreach (string path in iconPaths)
            {
                if (!(AssetImporter.GetAtPath(path) is TextureImporter ti)) continue;
                problems.Clear();
                CheckIconSettings(ti, problems);
                if (problems.Count == 0) continue;
                wrongIcons++;
                details.Add("Import settings " + RelativeToRoot(root, path) + ": " + string.Join("; ", problems));
            }

            info.Add("Contract PNGs: " + spritePaths.Count + " sprite(s), " + iconPaths.Count + " icon(s).");
            if (wrongSprites > 0) warnings.Add(wrongSprites + " of " + spritePaths.Count + " sprite PNG(s) have wrong import settings - run Configure Sprite Import Settings.");
            if (wrongIcons > 0) warnings.Add(wrongIcons + " of " + iconPaths.Count + " icon PNG(s) have wrong import settings - run Configure Sprite Import Settings.");

            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(root.PrefabPath);
            if (prefab == null)
            {
                warnings.Add("Prefab not created yet: " + root.PrefabPath);
            }
            else
            {
                var animation = prefab.GetComponent<AvarnethStartupAnimation>();
                if (animation == null)
                {
                    errors.Add("Prefab has no AvarnethStartupAnimation component: " + root.PrefabPath);
                }
                else
                {
                    info.Add("Prefab present: " + root.PrefabPath + " (" + animation.Layers.Count + " layer binding(s), " + animation.Particles.Count + " particle(s)).");
                    if (animation.ArtRoot == null) errors.Add("Prefab: Art Root is not assigned.");
                    if (animation.RaycastBlocker == null) warnings.Add("Prefab: raycast blocker Image is not assigned.");
                    for (int i = 0; i < animation.Layers.Count; i++)
                    {
                        StartupLayerBinding b = animation.Layers[i];
                        if (b == null || b.image == null) errors.Add("Prefab: layer binding " + i + " has no Image.");
                    }

                    if (animation.ParticleImages.Count != animation.Particles.Count) errors.Add("Prefab: particle Image count does not match the particle count.");
                    if (parsed.Data != null && (animation.Layers.Count != parsed.Data.layers.Length || animation.Particles.Count != parsed.Data.particles.Length))
                        warnings.Add("Prefab is out of date with Animation_Timeline.json - run Create or Update Startup Prefab.");

                    Canvas canvas = prefab.GetComponent<Canvas>();
                    if (canvas == null || canvas.renderMode != RenderMode.ScreenSpaceOverlay) errors.Add("Prefab: root Canvas is missing or not Screen Space - Overlay.");
                    if (prefab.GetComponentInChildren<EventSystem>(true) != null) errors.Add("Prefab contains an EventSystem; remove it (the scene provides one).");
                }
            }

            List<AvarnethStartupAnimation> inScenes = FindInLoadedScenes<AvarnethStartupAnimation>();
            info.Add("Overlay instances in loaded scenes: " + inScenes.Count);
            if (inScenes.Count > 1) warnings.Add("More than one overlay instance is in the loaded scenes.");
            foreach (AvarnethStartupAnimation a in inScenes)
            {
                if (a.SkipOnClick && !HasActiveEventSystem()) warnings.Add("Skip On Click is enabled but no active EventSystem is in the loaded scenes.");
                if (a.LoginCanvasGroup == null) info.Add("Overlay '" + a.name + "': no Login Canvas Group assigned (optional).");
            }

            Report(interactive, errors, warnings, info, details);
        }

        private static void Report(bool interactive, List<string> errors, List<string> warnings, List<string> info, List<string> details)
        {
            var sb = new StringBuilder();
            sb.AppendLine("AVARNETH startup installation: " + errors.Count + " error(s), " + warnings.Count + " warning(s).");
            foreach (string line in info) sb.AppendLine("  " + line);
            foreach (string line in errors) sb.AppendLine("ERROR: " + line);
            foreach (string line in warnings) sb.AppendLine("WARNING: " + line);
            foreach (string line in details) sb.AppendLine("  " + line);

            if (errors.Count > 0) Debug.LogError("[AVARNETH Startup] " + sb);
            else if (warnings.Count > 0) Debug.LogWarning("[AVARNETH Startup] " + sb);
            else Debug.Log("[AVARNETH Startup] " + sb);

            if (!interactive) return;

            var lines = new List<string>();
            foreach (string line in errors) lines.Add("ERROR: " + line);
            foreach (string line in warnings) lines.Add("WARNING: " + line);
            if (lines.Count == 0) lines.Add("Everything looks fine.");
            string message = ComposeListDialog(errors.Count + " error(s), " + warnings.Count + " warning(s).\n\n", lines,
                "\n\nThe full report is in the Console.");
            Alert(DialogTitle + " - Validation", message);
        }

        // ------------------------------------------------------------------ icons

        /// <summary>AVARNETH icon textures in &lt;root&gt;/Icons named AVE_Icon_&lt;size&gt;.png, keyed by size.</summary>
        internal static SortedDictionary<int, string> FindIconFiles(InstallRoot root)
        {
            var result = new SortedDictionary<int, string>();
            foreach (string path in CollectPngs(root, IconFolder))
            {
                string file = FileName(path);
                if (!file.StartsWith(IconPrefix, StringComparison.Ordinal)) continue;
                string number = file.Substring(IconPrefix.Length, file.Length - IconPrefix.Length - ".png".Length);
                if (int.TryParse(number, NumberStyles.None, CultureInfo.InvariantCulture, out int size) && size > 0 && !result.ContainsKey(size))
                    result.Add(size, path);
            }

            return result;
        }

        /// <summary>Exact size if available, otherwise the smallest larger icon; null when none fits.</summary>
        internal static string PickIcon(SortedDictionary<int, string> icons, int size)
        {
            foreach (KeyValuePair<int, string> pair in icons)
                if (pair.Key >= size) return pair.Value;
            return null;
        }

        // ------------------------------------------------------------------ helpers

        internal static string FileName(string assetPath)
        {
            int slash = assetPath.LastIndexOf('/');
            return slash >= 0 ? assetPath.Substring(slash + 1) : assetPath;
        }

        internal static string ParentPath(string assetPath)
        {
            int slash = assetPath.LastIndexOf('/');
            return slash > 0 ? assetPath.Substring(0, slash) : null;
        }

        internal static string JoinLimited(IList<string> lines)
        {
            var sb = new StringBuilder();
            int count = Math.Min(lines.Count, DialogListLimit);
            for (int i = 0; i < count; i++) sb.AppendLine("- " + lines[i]);
            if (lines.Count > count) sb.AppendLine("- ... and " + (lines.Count - count) + " more (see Console)");
            return sb.ToString().TrimEnd();
        }
    }

    // ---------------------------------------------------------------------- installer window

    /// <summary>Lets the user pick the timeline (importable asset root) and run the installer steps.</summary>
    internal sealed class AvarnethStartupInstallerWindow : EditorWindow
    {
        private List<string> _candidates = new List<string>();
        private InstallRoot _root;
        private string _rootError;
        private Vector2 _scroll;

        internal static void Open()
        {
            var window = GetWindow<AvarnethStartupInstallerWindow>(false, "AVARNETH Startup", true);
            window.minSize = new Vector2(420f, 320f);
            window.Refresh();
        }

        private void OnEnable()
        {
            Refresh();
        }

        private void OnFocus()
        {
            Refresh();
        }

        private void Refresh()
        {
            _candidates = AvarnethStartupInstaller.FindTimelineCandidates();
            if (!AvarnethStartupInstaller.TryResolveRoot(out _root, out _rootError, out bool _)) _root = null;
            Repaint();
        }

        private void OnGUI()
        {
            _scroll = EditorGUILayout.BeginScrollView(_scroll);

            EditorGUILayout.LabelField("Importable asset root", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("The root is the folder that contains Animation_Timeline.json (schema " + AvarnethStartupMath.TimelineSchema + ").", EditorStyles.wordWrappedLabel);

            TextAsset current = AvarnethStartupInstaller.TimelineOverride;
            EditorGUI.BeginChangeCheck();
            var picked = (TextAsset)EditorGUILayout.ObjectField("Timeline override", current, typeof(TextAsset), false);
            if (EditorGUI.EndChangeCheck())
            {
                if (picked != null && !AvarnethStartupInstaller.IsContractTimeline(picked))
                    EditorUtility.DisplayDialog(AvarnethStartupInstaller.DialogTitle, "'" + AssetDatabase.GetAssetPath(picked) + "' is not an AVARNETH startup timeline.", "OK");
                else
                    AvarnethStartupInstaller.TimelineOverride = picked;
                Refresh();
            }

            if (current != null && GUILayout.Button("Clear Override (use automatic detection)"))
            {
                AvarnethStartupInstaller.TimelineOverride = null;
                Refresh();
            }

            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Detected timelines: " + _candidates.Count, EditorStyles.boldLabel);
            foreach (string path in _candidates)
            {
                EditorGUILayout.BeginHorizontal();
                EditorGUILayout.LabelField(path, EditorStyles.wordWrappedLabel);
                if (GUILayout.Button("Use", GUILayout.Width(50f)))
                {
                    AvarnethStartupInstaller.TimelineOverride = AssetDatabase.LoadAssetAtPath<TextAsset>(path);
                    Refresh();
                }
                EditorGUILayout.EndHorizontal();
            }

            if (GUILayout.Button("Refresh")) Refresh();

            EditorGUILayout.Space();
            InstallRoot root = _root;
            bool resolved = root != null;
            if (resolved)
                EditorGUILayout.HelpBox("Root: " + root.RootFolder + "\nPrefab: " + root.PrefabPath, MessageType.Info);
            else
                EditorGUILayout.HelpBox(_rootError ?? "No usable timeline found.", MessageType.Warning);

            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Steps", EditorStyles.boldLabel);
            using (new EditorGUI.DisabledScope(!resolved))
            {
                if (GUILayout.Button("1. Configure Sprite Import Settings")) AvarnethStartupInstaller.ConfigureImportSettings(root, true);
                if (GUILayout.Button("2. Create or Update Startup Prefab")) AvarnethStartupInstaller.CreateOrUpdatePrefab(root, true);
                using (new EditorGUI.DisabledScope(EditorApplication.isPlayingOrWillChangePlaymode))
                {
                    if (GUILayout.Button("3. Add Startup Overlay To Open Scene...")) AvarnethStartupInstaller.AddOverlayToOpenScene();
                }
            }

            if (GUILayout.Button("Player Settings Helper...")) AvarnethPlayerSettingsHelperWindow.Open();
            if (GUILayout.Button("Validate Installation")) AvarnethStartupInstaller.ValidateInstallation(true);

            EditorGUILayout.EndScrollView();
        }
    }

    // ---------------------------------------------------------------------- player settings helper

    /// <summary>
    /// Shows the splash screen flags and Standalone icons and, after confirmation, assigns the AVARNETH icons
    /// or disables the Unity splash screen. Never touches any other Player Setting.
    /// </summary>
    internal sealed class AvarnethPlayerSettingsHelperWindow : EditorWindow
    {
        private InstallRoot _root;
        private SortedDictionary<int, string> _iconFiles = new SortedDictionary<int, string>();
        private int[] _sizes = new int[0];
        private Texture2D[] _current = new Texture2D[0];
        private Texture2D _defaultIcon;
        private Vector2 _scroll;

        internal static void Open()
        {
            var window = GetWindow<AvarnethPlayerSettingsHelperWindow>(false, "AVARNETH Player Settings", true);
            window.minSize = new Vector2(460f, 380f);
            window.Refresh();
        }

        private void OnEnable()
        {
            Refresh();
        }

        private void OnFocus()
        {
            Refresh();
        }

        private void Refresh()
        {
            _iconFiles = new SortedDictionary<int, string>();
            if (AvarnethStartupInstaller.TryResolveRoot(out _root, out string _, out bool _))
                _iconFiles = AvarnethStartupInstaller.FindIconFiles(_root);
            else
                _root = null;

            _sizes = PlayerSettings.GetIconSizes(NamedBuildTarget.Standalone, IconKind.Any) ?? new int[0];
            _current = PlayerSettings.GetIcons(NamedBuildTarget.Standalone, IconKind.Any) ?? new Texture2D[0];
            Texture2D[] defaults = PlayerSettings.GetIcons(NamedBuildTarget.Unknown, IconKind.Any) ?? new Texture2D[0];
            _defaultIcon = defaults.Length > 0 ? defaults[0] : null;
            Repaint();
        }

        private void OnGUI()
        {
            _scroll = EditorGUILayout.BeginScrollView(_scroll);

            EditorGUILayout.HelpBox("This window only changes the Standalone icons, the Default Icon and the two splash screen flags, " +
                                    "each after a confirmation. Company Name, Product Name, identifiers, scripting backend and all other settings are never changed.",
                MessageType.Info);

            // Splash screen
            EditorGUILayout.LabelField("Splash Image", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Show Splash Screen", PlayerSettings.SplashScreen.show ? "On" : "Off");
            EditorGUILayout.LabelField("Show Unity Logo", PlayerSettings.SplashScreen.showUnityLogo ? "On" : "Off");
            if (GUILayout.Button("Disable Unity Splash Screen...")) DisableSplash();

            EditorGUILayout.Space();

            // Icons
            EditorGUILayout.LabelField("Icon (PC, Mac & Linux Standalone)", EditorStyles.boldLabel);
            if (_root == null)
            {
                EditorGUILayout.HelpBox("The importable asset root was not found (see Tools > AVARNETH > Startup > Installer...).", MessageType.Warning);
            }
            else
            {
                EditorGUILayout.LabelField("AVARNETH icons found", _iconFiles.Count == 0 ? "none" : string.Join(", ", KeysAsStrings(_iconFiles)));
            }

            int[] sizes = _sizes;
            Texture2D[] current = _current;
            bool overridden = current.Length == sizes.Length && Array.Exists(current, t => t != null);
            EditorGUILayout.LabelField("Override for Standalone", overridden ? "On" : "Off (Default Icon is used)");
            for (int i = 0; i < sizes.Length; i++)
            {
                Texture2D tex = i < current.Length ? current[i] : null;
                string planned = _root != null ? AvarnethStartupInstaller.PickIcon(_iconFiles, sizes[i]) : null;
                EditorGUILayout.LabelField(sizes[i] + " px", (tex != null ? tex.name : "(not set)") + "   ->   " + (planned != null ? AvarnethStartupInstaller.FileName(planned) : "(no AVARNETH icon)"));
            }

            using (new EditorGUI.DisabledScope(_root == null || _iconFiles.Count == 0 || sizes.Length == 0))
            {
                if (GUILayout.Button("Assign AVARNETH Standalone Icons..."))
                {
                    Refresh();
                    AssignStandaloneIcons(_sizes, _current);
                }
            }

            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Default Icon (all platforms)", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Current", _defaultIcon != null ? _defaultIcon.name : "(not set)");
            using (new EditorGUI.DisabledScope(_root == null || _iconFiles.Count == 0))
            {
                if (GUILayout.Button("Assign AVARNETH Default Icon...")) AssignDefaultIcon();
            }

            EditorGUILayout.Space();
            if (GUILayout.Button("Refresh")) Refresh();
            EditorGUILayout.EndScrollView();
        }

        private static IEnumerable<string> KeysAsStrings(SortedDictionary<int, string> icons)
        {
            foreach (int key in icons.Keys) yield return key.ToString(CultureInfo.InvariantCulture);
        }

        private void AssignStandaloneIcons(int[] sizes, Texture2D[] current)
        {
            var planned = new Texture2D[sizes.Length];
            var changes = new List<string>();
            for (int i = 0; i < sizes.Length; i++)
            {
                Texture2D before = i < current.Length ? current[i] : null;
                string path = AvarnethStartupInstaller.PickIcon(_iconFiles, sizes[i]);
                Texture2D tex = path != null ? AssetDatabase.LoadAssetAtPath<Texture2D>(path) : null;
                planned[i] = tex != null ? tex : before; // no fitting AVARNETH icon: keep the current one
                if (planned[i] != before)
                    changes.Add(sizes[i] + " px: " + (before != null ? before.name : "(not set)") + " -> " + AvarnethStartupInstaller.FileName(path));
                else
                    changes.Add(sizes[i] + " px: unchanged");
            }

            string message = "PlayerSettings.SetIcons(Standalone) will set:\n\n" + string.Join("\n", changes) +
                             "\n\nNo other Player Setting is changed. Use File > Save Project to write ProjectSettings to disk.";
            if (!EditorUtility.DisplayDialog("Assign AVARNETH Standalone Icons", message, "Assign Icons", "Cancel")) return;

            PlayerSettings.SetIcons(NamedBuildTarget.Standalone, planned, IconKind.Any);
            Debug.Log("[AVARNETH Startup] Standalone icons assigned:\n" + string.Join("\n", changes));
            Refresh();
        }

        private void AssignDefaultIcon()
        {
            // The Default Icon is scaled by Unity for every size, so the largest AVARNETH icon is used.
            string path = null;
            foreach (KeyValuePair<int, string> pair in _iconFiles) path = pair.Value;
            Texture2D tex = path != null ? AssetDatabase.LoadAssetAtPath<Texture2D>(path) : null;
            if (tex == null) return;

            int[] sizes = PlayerSettings.GetIconSizes(NamedBuildTarget.Unknown, IconKind.Any) ?? new int[0];
            Texture2D[] current = PlayerSettings.GetIcons(NamedBuildTarget.Unknown, IconKind.Any) ?? new Texture2D[0];
            int length = Math.Max(1, sizes.Length);
            var planned = new Texture2D[length];
            for (int i = 0; i < length; i++) planned[i] = i < current.Length ? current[i] : null;
            Texture2D before = planned[0];
            planned[0] = tex;

            string message = "PlayerSettings.SetIcons(Default) will set the Default Icon:\n\n" +
                             (before != null ? before.name : "(not set)") + " -> " + AvarnethStartupInstaller.FileName(path) +
                             "\n\nNo other Player Setting is changed. Use File > Save Project to write ProjectSettings to disk.";
            if (!EditorUtility.DisplayDialog("Assign AVARNETH Default Icon", message, "Assign Default Icon", "Cancel")) return;

            PlayerSettings.SetIcons(NamedBuildTarget.Unknown, planned, IconKind.Any);
            Debug.Log("[AVARNETH Startup] Default icon assigned: " + path);
            Refresh();
        }

        private void DisableSplash()
        {
            string message =
                "This sets Player Settings > Splash Image:\n" +
                "- Show Splash Screen: " + (PlayerSettings.SplashScreen.show ? "On" : "Off") + " -> Off\n" +
                "- Show Unity Logo: " + (PlayerSettings.SplashScreen.showUnityLogo ? "On" : "Off") + " -> Off\n\n" +
                "Licence note: Unity announced on 12 Sep 2024 that the Made with Unity splash screen is optional for games made with Unity 6, " +
                "including Unity Personal. For older editor versions Personal projects had to show it. Check the licence terms that apply to " +
                "your subscription before shipping.\n\nNo other Player Setting is changed.";
            if (!EditorUtility.DisplayDialog("Disable Unity Splash Screen", message, "Disable Splash Screen", "Cancel")) return;

            PlayerSettings.SplashScreen.show = false;
            PlayerSettings.SplashScreen.showUnityLogo = false;
            Debug.Log("[AVARNETH Startup] Splash screen disabled (show = false, showUnityLogo = false).");
            Repaint();
        }
    }
}
