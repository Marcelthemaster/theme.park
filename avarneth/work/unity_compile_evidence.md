# Unity integration – compile & verification evidence

Date: 2026-10-26. Target: Unity **6000.6.0f1**, URP 2D, Windows x64.
Machine: Linux, `dotnet --version` = 8.0.132. No Unity editor is available on this machine.

## 1. Delivered files

Package (`/home/user/theme.park/avarneth/package/AVARNETH_Complete_Branding_Startup_V1.0/`):

| File | Lines | SHA-256 |
|---|---|---|
| `05_Unity_Integration/Runtime/AvarnethStartupTimelineMath.cs` (pure C#, no `using UnityEngine`) | 456 | `9caa1d5c55a4b8940ff4bad6eb9d2f5a550d1913bf7af029e629dcbddf46be41` |
| `05_Unity_Integration/Runtime/AvarnethStartupAnimation.cs` | 840 | `028a4de81afecf498a23001f88656665b7582e1d19062ad699283b83c06af1f7` |
| `05_Unity_Integration/Runtime/Eckertengineering.Avarneth.Startup.asmdef` | 16 | `f962027098f16cbb44041ee0ffd663bece07cd3c365247b05550e421b83ea0f4` |
| `05_Unity_Integration/Editor/AvarnethStartupInstaller.cs` | 1681 | `ee0c5bb2e9406f2fe4d94e1ee243ad5f5fb171bb4b6d6a2b6535f5fec027d2d8` |
| `05_Unity_Integration/Editor/Eckertengineering.Avarneth.Startup.Editor.asmdef` | 19 | `b641e4c5abff7ed52424fe07529b00dc7ecb466f310300a973837d800e5e0c87` |
| `05_Unity_Integration/README_UNITY_FOLDER.txt` | 16 | `7dc7f423eca34d3512a1ec06141c68c5fb990dc5054c764324121014d49c5abb` |
| `07_Documentation/UNITY_INSTALLATION.md` (DE) | 100 | `bd629a1151e58a441ea959e1796925a43557f5a8a471be1f5a138f5179ef46f8` |
| `07_Documentation/PLAYER_SETTINGS.md` (DE) | 80 | `4f9048cdfdab0147ff1b8e206f10a00d47337b2b556e0d8358e1838285518018` |
| `05_Unity_Integration/Materials/.gitkeep` (keeps the intentionally empty folder; Unity ignores dot files) | 0 | – |

\* Hashes are from the state at the time this file was written; re-hash before release (`sha256sum`).

Note: the package contains **three** `.cs` files (math, runtime component, editor installer incl. its two
EditorWindows). The brief mentions "all four .cs files"; there is no fourth package source file. The harness
stub is the only additional `.cs` and lives outside the package.

Harness (outside the package, never shipped):

| Path | Purpose |
|---|---|
| `/tmp/claude-0/unityref/compile/Runtime/Avarneth.Runtime.Harness.csproj` | Runtime-only: the 2 Runtime `.cs` vs UnityEngine modules + UnityEngine.UI, **no UnityEditor reference**; AssemblyName `Eckertengineering.Avarneth.Startup`; XML-doc generation on (CS1591 would flag undocumented public API) |
| `/tmp/claude-0/unityref/compile/Editor/Avarneth.Editor.Harness.csproj` | All 3 package `.cs` + stub vs UnityEngine modules + UnityEngine.UI + UnityEditor |
| `/tmp/claude-0/unityref/compile/EditorSplit/Avarneth.EditorSplit.Harness.csproj` | asmdef-faithful variant: editor `.cs` + stub as assembly `Eckertengineering.Avarneth.Startup.Editor` with a ProjectReference to the runtime harness (proves the editor uses only the runtime's **public** API across the assembly boundary) |
| `/tmp/claude-0/unityref/compile/Stubs/HARNESS_ONLY_UnityEditor6000_6_Stubs.cs` | clearly labelled stub file (section 5) |
| `/tmp/claude-0/unityref/compile/apicheck_6000_6.py` | automated declaration + `[Obsolete]` check against the 6000.6 source (section 4) |
| `/tmp/claude-0/unityref/mathtest/MathTest.csproj`, `Program.cs` | net8.0 console; compiles ONLY `AvarnethStartupTimelineMath.cs` + `Program.cs` |
| `/tmp/claude-0/unityref/mathtest/sample.json` | hand-written sample timeline (all eases incl. unknown → linear, `step`, flipbooks with hold/sprite/hide, empty sprite, order ≥ 100, 3 particles with fade-in/out, acceleration, half-pixel start) |
| `/tmp/claude-0/unityref/mathtest/strict_compare.py` | field-by-field comparison vs. `tools/timeline_eval.py` |

All settings: `TargetFramework netstandard2.1`, `LangVersion 9.0`, `WarningLevel 4`, `Nullable disable`,
warnings shown, `TreatWarningsAsErrors false`. Reference assemblies:
`/tmp/claude-0/unityref/mods/lib/net45/*.dll` (UnityEngine modules 2021.3.33),
`/tmp/claude-0/unityref/ui/lib/UnityEngine.UI.dll` (uGUI 2020.3.21),
`/tmp/claude-0/unityref/sdk/lib/UnityEditor.dll` (UnityEditor 2021.1.14).

## 2. Commands and compiler results (final state, clean builds: `rm -rf bin obj` first)

```
cd /tmp/claude-0/unityref/compile/Runtime     && dotnet build -nologo -v:minimal   -> 0 Error(s), 0 Warning(s)
cd /tmp/claude-0/unityref/compile/Editor      && dotnet build -nologo -v:minimal   -> 0 Error(s), 0 Warning(s)
cd /tmp/claude-0/unityref/compile/Editor      && dotnet build -nologo -v:minimal -p:ShowStubWarnings=true
                                                                                  -> 0 Error(s), 13 Warning(s), all CS0436
cd /tmp/claude-0/unityref/compile/EditorSplit && dotnet build -nologo -v:minimal   -> 0 Error(s), 0 Warning(s)
cd /tmp/claude-0/unityref/mathtest            && dotnet build -nologo -v:minimal   -> 0 Error(s), 0 Warning(s)
```

CS0436 text (expected, harness-only): *"The type 'PlayerSettings' in '…/Stubs/HARNESS_ONLY_UnityEditor6000_6_Stubs.cs'
conflicts with the imported type 'PlayerSettings' in 'UnityEditor, Version=0.0.0.0 …'. Using the type defined in
'…Stubs.cs'."* at `AvarnethStartupInstaller.cs` lines 1541, 1542, 1543, 1558, 1559, 1633, 1646, 1647, 1659, 1668,
1669, 1675, 1676 (every `PlayerSettings` use). The csproj suppresses CS0436 unless `ShowStubWarnings=true`.

Runtime has no editor dependency: no `UnityEditor` reference in the csproj, no `UnityEditor.dll` in the output,
and `strings Eckertengineering.Avarneth.Startup.dll | grep -ci unityeditor` = 0 (referenced assemblies:
netstandard, UnityEngine.CoreModule, UnityEngine.UIModule, UnityEngine.UI).

Iteration history (fixed in the code, references untouched):
1. First editor build: 1 error CS1061 `TextureImporter.GetSourceTextureWidthAndHeight` (public only since 2021.2,
   missing in the 2021.1 reference) → stubbed (section 5); 36 × CS0649 on the JsonUtility DTO fields
   (assigned by JsonUtility, not by code) → `#pragma warning disable/restore CS0649` around the DTO block;
   13 × CS0436 → explained above.
2. All later builds: 0 errors, 0 warnings.

## 3. Math test

```
cd /tmp/claude-0/unityref/mathtest
dotnet bin/Debug/net8.0/avarneth-mathtest.dll --selftest            -> "selftest: 97 passed, 0 failed", exit 0
dotnet bin/Debug/net8.0/avarneth-mathtest.dll sample.json 20 > sample_20fps.csv   -> exit 0, 411 lines (header + 41 frames x 10)
dotnet bin/Debug/net8.0/avarneth-mathtest.dll sample.json 60 > sample_60fps.csv   -> exit 0, 1211 lines
dotnet bin/Debug/net8.0/avarneth-mathtest.dll <05_Unity_Integration/Importable_Assets/Animation_Timeline.json> 60
                                                                     -> exit 0, 6293 lines (12 layers + 40 particles x 121 frames)
dotnet bin/Debug/net8.0/avarneth-mathtest.dll                        -> usage, exit 2
dotnet bin/Debug/net8.0/avarneth-mathtest.dll /nonexistent.json 60   -> "error: Could not find file", exit 1
```

SHA-256: `sample.json` 480be545…8361fb, `sample_20fps.csv` 1ebf09b3…a200d, `sample_60fps.csv` ae64b89b…c0f1.

Self-test covers: every ease at 0/1 and known midpoints, clamping, ParseEase/ParseAfterFrames (exact, unknown,
wrong case, null), `Snap` = floor(v+0.5) incl. 0.5→1, 2.5→3, −0.5→0, −1.5→−1 (no banker's rounding), keys
before/between/after, `step` holding the previous value, empty keys, flipbook before/start/mid/last/hold/sprite/
hide/zero-length, particle activation window, fade-in/out, motion, top-left placement, pixel scale at
1920×1080 (4), 2560×1440 (5), 3840×2160 (8), 1600×900 (3), 1680×1050 (3), 1366×768 (2), 1280×720 (2),
800×600 (1), off-centre content bounds, Continuous, half-pixel alignment, time stretch, delta clamp, reveal factor.

Hand-checked rows (sample, 20 fps): frame 3 emblem alpha 0.8750 / y 40 (outCubic u=0.5, dy 0.375);
frame 10 wordmark x 117 (dx −3.072), particle 1 x 101 (100.5 → floor(101.0)); frame 34 wordmark x 123 /
y 169 (122.5 → 123, 168.5 → 169); frame 26 publisher y 237, particle 0 (241,177) alpha 1.0;
frame 40 (t = duration) all `visible = 0` (contract 3.3).

Cross-check against the Python reference evaluator (`/home/user/theme.park/avarneth/tools/timeline_eval.py`,
which also mirrors float32 storage):

```
python3 /home/user/theme.park/avarneth/tools/crosscheck.py <timeline>      (fps 60, 144, 30)
  real Animation_Timeline.json: 6292 / 15028 / 3172 rows, 0 mismatches
  sample.json:                  1210 / 2890 / 610 rows, 0 mismatches
python3 /tmp/claude-0/unityref/mathtest/strict_compare.py sample.json <real timeline>
  fps 20, 24, 25, 30, 50, 60, 75, 90, 120, 144, 165, 240: 0 mismatches in frame/kind/id/visible/index,
  0 mismatches in any field (x, y, alpha string) of visible rows, for both files
```

Numeric model (documented in the math file header): data stored as float32 (as Unity serializes it), sample time
`t = (float)(i / fps)`, all formulas evaluated in double in contract order. The CSV evaluates exactly what
`AvarnethStartupAnimation.ApplyTime` evaluates (same double overloads).

## 4. UnityEngine / UnityEditor API verification (6000.6.0f1 C# reference source)

Source: `/home/user/unity-technologies/unitycsreference` (tag 6000.6.0f1). Method: `apicheck_6000_6.py` greps
each declaration with its exact signature and inspects the attribute lines directly above it for `[Obsolete]`
(result: 180 checked, 0 missing). Signatures were additionally spot-read by hand (PlayerSettings icon API,
SplashScreen, TextureImporter, PrefabUtility, AssetImporter.SaveAndReimport, NamedBuildTarget).

| API | 6000.6.0f1 source file:line | [Obsolete] |
|---|---|---|
| `UnityEngine.MonoBehaviour (class)` | Runtime/Export/Scripting/MonoBehaviour.bindings.cs:20 | no |
| `Behaviour.enabled` | Runtime/Export/Scripting/Behaviour.bindings.cs:18 | no |
| `Behaviour.isActiveAndEnabled` | Runtime/Export/Scripting/Behaviour.bindings.cs:21 | no |
| `Component.gameObject` | Runtime/Export/Scripting/Component.bindings.cs:34 | no |
| `Component.GetComponent<T>()` | Runtime/Export/Scripting/Component.bindings.cs:51 | no |
| `Component.GetComponentInParent<T>()` | Runtime/Export/Scripting/Component.bindings.cs:147 | no |
| `GameObject(string, params Type[]) ctor` | Runtime/Export/Scripting/GameObject.bindings.cs:416 | no |
| `GameObject.activeSelf` | Runtime/Export/Scripting/GameObject.bindings.cs:302 | no |
| `GameObject.SetActive(bool)` | Runtime/Export/Scripting/GameObject.bindings.cs:300 | no |
| `GameObject.layer` | Runtime/Export/Scripting/GameObject.bindings.cs:297 | no |
| `GameObject.scene` | Runtime/Export/Scripting/GameObject.bindings.cs:486 | no |
| `GameObject.transform` | Runtime/Export/Scripting/GameObject.bindings.cs:285 | no |
| `GameObject.GetComponent<T>()` | Runtime/Export/Scripting/GameObject.bindings.cs:30 | no |
| `GameObject.AddComponent<T>()` | Runtime/Export/Scripting/GameObject.bindings.cs:259 | no |
| `GameObject.GetComponentsInChildren<T>(bool)` | Runtime/Export/Scripting/GameObject.bindings.cs:145 | no |
| `GameObject.GetComponentInChildren<T>(bool)` | Runtime/Export/Scripting/GameObject.bindings.cs:76 | no |
| `Object.Destroy(Object)` | Runtime/Export/Scripting/UnityEngineObject.bindings.cs:672 | no |
| `Object.DestroyImmediate(Object)` | Runtime/Export/Scripting/UnityEngineObject.bindings.cs:683 | no |
| `Object.name` | Runtime/Export/Scripting/UnityEngineObject.bindings.cs:403 | no |
| `Application.isPlaying` | Runtime/Export/Application/Application.bindings.cs:111 | no |
| `Application.dataPath` | Runtime/Export/Application/Application.bindings.cs:186 | no |
| `Time.frameCount` | Runtime/Export/Time/Time.bindings.cs:81 | no |
| `Time.unscaledDeltaTime` | Runtime/Export/Time/Time.bindings.cs:60 | no |
| `Screen.width` | Runtime/Export/Graphics/Graphics.bindings.cs:500 | no |
| `Screen.height` | Runtime/Export/Graphics/Graphics.bindings.cs:501 | no |
| `Debug.Log(object)` | Runtime/Export/Debug/Debug.bindings.cs:134 | no |
| `Debug.LogWarning(object)` | Runtime/Export/Debug/Debug.bindings.cs:223 | no |
| `Debug.LogWarning(object, Object)` | Runtime/Export/Debug/Debug.bindings.cs:226 | no |
| `Debug.LogError(object)` | Runtime/Export/Debug/Debug.bindings.cs:162 | no |
| `Debug.LogError(object, Object)` | Runtime/Export/Debug/Debug.bindings.cs:165 | no |
| `Debug.LogException(Exception, Object)` | Runtime/Export/Debug/Debug.bindings.cs:215 | no |
| `Transform.localScale` | Runtime/Transform/ScriptBindings/Transform.bindings.cs:78 | no |
| `Transform.SetParent(Transform, bool)` | Runtime/Transform/ScriptBindings/Transform.bindings.cs:106 | no |
| `Transform.childCount` | Runtime/Transform/ScriptBindings/Transform.bindings.cs:367 | no |
| `Transform.GetChild(int)` | Runtime/Transform/ScriptBindings/Transform.bindings.cs:467 | no |
| `Transform.SetSiblingIndex(int)` | Runtime/Transform/ScriptBindings/Transform.bindings.cs:383 | no |
| `Transform.parent` | Runtime/Transform/ScriptBindings/Transform.bindings.cs:81 | no |
| `RectTransform.anchorMin` | Runtime/Transform/ScriptBindings/RectTransform.bindings.cs:143 | no |
| `RectTransform.anchorMax` | Runtime/Transform/ScriptBindings/RectTransform.bindings.cs:144 | no |
| `RectTransform.anchoredPosition` | Runtime/Transform/ScriptBindings/RectTransform.bindings.cs:145 | no |
| `RectTransform.sizeDelta` | Runtime/Transform/ScriptBindings/RectTransform.bindings.cs:146 | no |
| `RectTransform.pivot` | Runtime/Transform/ScriptBindings/RectTransform.bindings.cs:147 | no |
| `Vector2Int(int,int)` | Runtime/Export/Math/Vector2Int.cs:45 | no |
| `RectInt(int,int,int,int)` | Runtime/Export/Geometry/RectInt.cs:122 | no |
| `RectInt.x/y/width/height` | Runtime/Export/Geometry/RectInt.cs:58 | no |
| `Rect.width/height` | Runtime/Export/Geometry/Rect.cs:135 | no |
| `Rect.size` | Runtime/Export/Geometry/Rect.cs:147 | no |
| `Color(float,float,float,float)` | Runtime/Export/Math/Color.cs:38 | no |
| `Color.white` | Runtime/Export/Math/Color.cs:866 | no |
| `Vector2(float,float)` / `Vector2.zero` | Runtime/Export/Math/Vector2.cs:62 / :627 | no |
| `Vector3(float,float,float)` / `Vector3.one` | Runtime/Export/Math/Vector3.cs:335 / :729 | no |
| `Mathf.RoundToInt(float)` | Runtime/Export/Math/Mathf.cs:158 | no |
| `Mathf.Approximately(float,float)` | Runtime/Export/Math/Mathf.cs:263 | no |
| `Sprite.rect` | Runtime/2D/Common/ScriptBindings/Sprites.bindings.cs:135 | no |
| `SpriteMeshType` (FullRect = 0) | Runtime/2D/Common/ScriptBindings/Sprites.bindings.cs:27 | no |
| `FilterMode` (Point) | Runtime/Export/Graphics/GraphicsEnums.cs:332 | no |
| `TextureWrapMode` (Clamp) | Runtime/Export/Graphics/GraphicsEnums.cs:339 | no |
| `TextAsset.text` | Runtime/Export/Scripting/TextAsset.cs:23 | no |
| `LayerMask.NameToLayer(string)` | Runtime/Export/Scripting/LayerMask.bindings.cs:52 | no |
| `JsonUtility.FromJson<T>(string)` | Modules/JSONSerialize/Public/JsonUtility.bindings.cs:32 | no |
| `SerializeField` | Runtime/Export/Serialization/Serialization.cs:54 | no |
| `HeaderAttribute(string)` | Runtime/Export/PropertyDrawer/PropertyAttribute.cs:94 | no |
| `TooltipAttribute(string)` | Runtime/Export/PropertyDrawer/PropertyAttribute.cs:63 | no |
| `RangeAttribute(float,float)` | Runtime/Export/PropertyDrawer/PropertyAttribute.cs:108 | no |
| `MinAttribute(float)` | Runtime/Export/PropertyDrawer/PropertyAttribute.cs:122 | no |
| `DisallowMultipleComponent` | Runtime/Export/Scripting/Attributes.cs:12 | no |
| `AddComponentMenu(string)` | Runtime/Export/Scripting/Attributes.cs:42 | no |
| `UnityEvent()` | artifacts/generated/UnityEvent/UnityEvent_0.cs:25 | no |
| `UnityEvent.Invoke()` | artifacts/generated/UnityEvent/UnityEvent_0.cs:55 | no |
| `Canvas.renderMode` | Modules/UI/ScriptBindings/UICanvas.bindings.cs:86 | no |
| `Canvas.scaleFactor` | Modules/UI/ScriptBindings/UICanvas.bindings.cs:89 | no |
| `Canvas.pixelPerfect` | Modules/UI/ScriptBindings/UICanvas.bindings.cs:94 | no |
| `Canvas.sortingOrder` | Modules/UI/ScriptBindings/UICanvas.bindings.cs:98 | no |
| `RenderMode` (ScreenSpaceOverlay = 0) | Modules/UI/ScriptBindings/UICanvas.bindings.cs:12 | no |
| `CanvasGroup.alpha` | Modules/UI/ScriptBindings/CanvasGroup.bindings.cs:22 | no |
| `CanvasGroup.interactable` | Modules/UI/ScriptBindings/CanvasGroup.bindings.cs:23 | no |
| `CanvasGroup.blocksRaycasts` | Modules/UI/ScriptBindings/CanvasGroup.bindings.cs:24 | no |
| `CanvasRenderer.cullTransparentMesh` | Modules/UI/ScriptBindings/CanvasRenderer.bindings.cs:22 | no |
| `SceneManager.sceneCount` | Runtime/Export/SceneManager/SceneManager.bindings.cs:56 | no |
| `SceneManager.GetSceneAt(int)` | Runtime/Export/SceneManager/SceneManager.bindings.cs:103 | no |
| `SceneManager.GetActiveScene()` | Runtime/Export/SceneManager/SceneManager.bindings.cs:81 | no |
| `SceneManager.MoveGameObjectToScene(GameObject, Scene)` | Runtime/Export/SceneManager/SceneManager.bindings.cs:154 | no |
| `Scene.isLoaded` | Runtime/Export/SceneManager/Scene.cs:64 | no |
| `Scene.IsValid()` | Runtime/Export/SceneManager/Scene.cs:48 | no |
| `Scene.name` | Runtime/Export/SceneManager/Scene.cs:58 | no |
| `Scene.GetRootGameObjects()` | Runtime/Export/SceneManager/Scene.cs:115 | no |
| `Scene operator !=` | Runtime/Export/SceneManager/Scene.cs:138 | no |
| `GUILayout.Button(string, params GUILayoutOption[])` | Modules/IMGUI/GUILayout.cs:33 | no |
| `GUILayout.Width(float)` | Modules/IMGUI/GUILayout.cs:458 | no |
| `MenuItem(string, bool, int)` | Editor/Mono/MenuItem.cs:31 | no |
| `MenuItem(string, bool)` | Editor/Mono/MenuItem.cs:25 | no |
| `EditorApplication.isPlayingOrWillChangePlaymode` | Editor/Mono/EditorApplication.bindings.cs:100 | no |
| `EditorPrefs.GetString(string, string)` | Editor/Mono/EditorPrefs.bindings.cs:62 | no |
| `EditorPrefs.SetString(string, string)` | Editor/Mono/EditorPrefs.bindings.cs:55 | no |
| `EditorPrefs.DeleteKey(string)` | Editor/Mono/EditorPrefs.bindings.cs:88 | no |
| `AssetDatabase.FindAssets(string)` | Editor/Mono/AssetDatabase/AssetDatabaseSearching.cs:17 | no |
| `AssetDatabase.FindAssets(string, string[])` | Editor/Mono/AssetDatabase/AssetDatabaseSearching.cs:38 | no |
| `AssetDatabase.GUIDToAssetPath(string)` | Modules/AssetDatabase/Editor/ScriptBindings/AssetDatabase.bindings.cs:613 | no |
| `AssetDatabase.AssetPathToGUID(string)` | Modules/AssetDatabase/Editor/ScriptBindings/AssetDatabase.bindings.cs:628 | no |
| `AssetDatabase.LoadAssetAtPath<T>(string)` | Modules/AssetDatabase/Editor/ScriptBindings/AssetDatabase.bindings.cs:450 | no |
| `AssetDatabase.GetAssetPath(Object)` | Modules/AssetDatabase/Editor/ScriptBindings/AssetDatabase.bindings.cs:409 | no |
| `AssetDatabase.IsValidFolder(string)` | Modules/AssetDatabase/Editor/ScriptBindings/AssetDatabase.bindings.cs:372 | no |
| `AssetDatabase.CreateFolder(string, string)` | Modules/AssetDatabase/Editor/ScriptBindings/AssetDatabase.bindings.cs:172 | no |
| `AssetDatabase.StartAssetEditing()` | Modules/AssetDatabase/Editor/ScriptBindings/AssetDatabase.bindings.cs:238 | no |
| `AssetDatabase.StopAssetEditing()` | Modules/AssetDatabase/Editor/ScriptBindings/AssetDatabase.bindings.cs:244 | no |
| `AssetImporter.GetAtPath(string)` | Editor/Mono/AssetPipeline/AssetImporter.bindings.cs:114 | no |
| `AssetImporter.SaveAndReimport()` (= `AssetDatabase.ImportAsset(assetPath)`, deferred inside Start/StopAssetEditing) | Editor/Mono/AssetPipeline/AssetImporter.bindings.cs:116 | no |
| `TextureImporter.maxTextureSize` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:42 | no |
| `TextureImporter.textureCompression` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:49 | no |
| `TextureImporter.GetPlatformTextureSettings(string)` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:105 | no |
| `TextureImporter.SetPlatformTextureSettings(TextureImporterPlatformSettings)` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:181 | no |
| `TextureImporter.npotScale` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:235 | no |
| `TextureImporter.mipmapEnabled` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:257 | no |
| `TextureImporter.sRGBTexture` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:262 | no |
| `TextureImporter.filterMode` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:344 | no |
| `TextureImporter.wrapMode` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:347 | no |
| `TextureImporter.wrapModeU` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:355 | no |
| `TextureImporter.wrapModeV` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:357 | no |
| `TextureImporter.alphaIsTransparency` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:365 | no |
| `TextureImporter.spriteImportMode` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:370 | no |
| `TextureImporter.spritePixelsPerUnit` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:384 | no |
| `TextureImporter.GetSourceTextureWidthAndHeight(out int, out int)` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:399 | no |
| `TextureImporter.textureType` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:440 | no |
| `TextureImporter.ReadTextureSettings(TextureImporterSettings)` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:444 | no |
| `TextureImporter.SetTextureSettings(TextureImporterSettings)` | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:450 | no |
| `TextureImporterSettings` (class) | Editor/Mono/AssetPipeline/TextureImporterTypes.bindings.cs:32 | no |
| `TextureImporterSettings.spriteMeshType` | Editor/Mono/AssetPipeline/TextureImporterTypes.bindings.cs:473 | no |
| `TextureImporterPlatformSettings.overridden` | Editor/Mono/AssetPipeline/TextureImporterTypes.bindings.cs:654 | no |
| `TextureImporterType` (Default = 0, Sprite = 8) | Editor/Mono/AssetPipeline/TextureImporterEnums.cs:326 | no |
| `TextureImporterCompression` (Uncompressed = 0) | Editor/Mono/AssetPipeline/TextureImporterEnums.cs:353 | no |
| `TextureImporterNPOTScale` (None = 0) | Editor/Mono/AssetPipeline/TextureImporterEnums.cs:284 | no |
| `SpriteImportMode` (Single = 1) | Editor/Mono/AssetPipeline/TextureImporterEnums.cs:380 | no |
| `PrefabUtility.SaveAsPrefabAsset(GameObject, string, out bool)` | Editor/Mono/Prefabs/PrefabUtility.cs:2086 | no |
| `PrefabUtility.LoadPrefabContents(string)` | Editor/Mono/Prefabs/PrefabUtility.cs:2871 | no |
| `PrefabUtility.UnloadPrefabContents(GameObject)` | Editor/Mono/Prefabs/PrefabUtility.cs:2895 | no |
| `PrefabUtility.InstantiatePrefab(Object, Scene)` | Editor/Mono/Prefabs/PrefabUtility.cs:2188 | no |
| `EditorSceneManager.NewPreviewScene()` | Editor/Mono/EditorSceneManager.bindings.cs:94 | no |
| `EditorSceneManager.ClosePreviewScene(Scene)` | Editor/Mono/EditorSceneManager.bindings.cs:132 | no |
| `EditorSceneManager.MarkSceneDirty(Scene)` | Editor/Mono/EditorSceneManager.bindings.cs:225 | no |
| `Undo.RegisterCreatedObjectUndo(Object, string)` | Editor/Mono/Undo/Undo.bindings.cs:124 | no |
| `Undo.GetCurrentGroup()` | Editor/Mono/Undo/Undo.bindings.cs:228 | no |
| `Undo.SetCurrentGroupName(string)` | Editor/Mono/Undo/Undo.bindings.cs:234 | no |
| `Undo.CollapseUndoOperations(int)` | Editor/Mono/Undo/Undo.bindings.cs:243 | no |
| `SerializedObject(Object)` | Editor/Mono/SerializedObject.bindings.cs:24 | no |
| `SerializedObject.FindProperty(string)` | Editor/Mono/SerializedObject.bindings.cs:75 | no |
| `SerializedObject.ApplyModifiedProperties()` | Editor/Mono/SerializedObject.bindings.cs:120 | no |
| `SerializedProperty.objectReferenceValue` | Editor/Mono/SerializedProperty.bindings.cs:1337 | no |
| `Selection.activeGameObject` | Editor/Mono/Selection/Selection.bindings.cs:67 | no |
| `EditorUtility.DisplayDialog(string,string,string,string)` | Editor/Mono/EditorUtility.cs:201 | no |
| `EditorUtility.DisplayDialog(string,string,string)` | Editor/Mono/EditorUtility.cs:206 | no |
| `EditorUtility.IsPersistent(Object)` | Editor/Mono/EditorUtility.bindings.cs:54 | no |
| `EditorGUIUtility.PingObject(Object)` | Editor/Mono/EditorGUIUtility.cs:1335 | no |
| `EditorWindow.GetWindow<T>(bool, string, bool)` | Editor/Mono/EditorWindow.cs:900 | no |
| `EditorWindow.minSize` | Editor/Mono/EditorWindow.cs:1147 | no |
| `EditorWindow.Repaint()` | Editor/Mono/EditorWindow.cs:1131 | no |
| `EditorGUILayout.BeginScrollView(Vector2, params GUILayoutOption[])` | Editor/Mono/EditorGUILayout.cs:1916 | no |
| `EditorGUILayout.EndScrollView()` | Editor/Mono/EditorGUILayout.cs:2057 | no |
| `EditorGUILayout.LabelField(string, GUIStyle, params)` | Editor/Mono/EditorGUILayout.cs:119 | no |
| `EditorGUILayout.LabelField(string, string, params)` | Editor/Mono/EditorGUILayout.cs:134 | no |
| `EditorGUILayout.ObjectField(string, Object, Type, bool, params)` | Editor/Mono/EditorGUILayout.cs:1235 | no |
| `EditorGUILayout.Space()` | Editor/Mono/EditorGUILayout.cs:1685 | no |
| `EditorGUILayout.BeginHorizontal(params GUILayoutOption[])` | Editor/Mono/EditorGUILayout.cs:1778 | no |
| `EditorGUILayout.EndHorizontal()` | Editor/Mono/EditorGUILayout.cs:1806 | no |
| `EditorGUILayout.HelpBox(string, MessageType)` | Editor/Mono/EditorGUILayout.cs:1652 | no |
| `EditorGUI.BeginChangeCheck()` | Editor/Mono/EditorGUI.cs:482 | no |
| `EditorGUI.EndChangeCheck()` | Editor/Mono/EditorGUI.cs:496 | no |
| `EditorGUI.DisabledScope(bool)` | Editor/Mono/EditorGUI.cs:338 | no |
| `EditorStyles.boldLabel` | Editor/Mono/GUI/EditorStyles.cs:35 | no |
| `EditorStyles.wordWrappedLabel` | Editor/Mono/GUI/EditorStyles.cs:51 | no |
| `MessageType` (Info, Warning) | Editor/Mono/EditorGUIUtility.bindings.cs:63 | no |
| `PlayerSettings.SplashScreen.show` | Editor/Mono/PlayerSettingsSplashScreen.bindings.cs:111 | no |
| `PlayerSettings.SplashScreen.showUnityLogo` | Editor/Mono/PlayerSettingsSplashScreen.bindings.cs:114 | no |
| `PlayerSettings.GetIconSizes(NamedBuildTarget, IconKind)` | Editor/Mono/PlatformSupport/PlayerSettingsPlatformIcons.bindings.cs:513 | no |
| `PlayerSettings.GetIcons(NamedBuildTarget, IconKind)` | Editor/Mono/PlatformSupport/PlayerSettingsPlatformIcons.bindings.cs:463 | no |
| `PlayerSettings.SetIcons(NamedBuildTarget, Texture2D[], IconKind)` | Editor/Mono/PlatformSupport/PlayerSettingsPlatformIcons.bindings.cs:433 | no |
| `NamedBuildTarget.Standalone` | Editor/Mono/BuildPipeline/NamedBuildTarget.cs:47 | no |
| `NamedBuildTarget.Unknown` | Editor/Mono/BuildPipeline/NamedBuildTarget.cs:45 | no |
| `IconKind` (Any = −1) | Editor/Mono/PlayerSettings.bindings.cs:310 | no |

Obsolescence findings that changed the design:

- `Object.FindObjectsByType<T>(FindObjectsInactive, FindObjectsSortMode)` is **[Obsolete]** in 6000.6
  (`Runtime/Export/Scripting/UnityEngineObject.bindings.cs:822-823`; the enum `FindObjectsSortMode` itself is
  [Obsolete] at line 56). The non-obsolete replacement `FindObjectsByType<T>(FindObjectsInactive)` (line 870)
  does **not exist** in the 2021.3 reference assembly and cannot be stubbed (it would be a static member of
  `UnityEngine.Object`). The installer therefore implements "already exists in loaded scenes, inactive included"
  by iterating `SceneManager.sceneCount` / `GetSceneAt(i)` / `isLoaded` / `GetRootGameObjects()` /
  `GetComponentsInChildren<T>(true)` – all non-obsolete in 6000.6 and compilable here. This also excludes
  Prefab-Mode preview scenes, which a global find could return. Deviation from the brief's wording, same behaviour.
- `TextureImporter.spritesheet` is [Obsolete] (`TextureImporter.bindings.cs:373`) – not used (contract 2).
- `PlayerSettings.GetIconSizesForTargetGroup` / `SetIconsForTargetGroup` / `GetIconsForTargetGroup` are [Obsolete]
  (`PlayerSettingsPlatformIcons.bindings.cs:429-528`) – not used; the NamedBuildTarget overloads are used.
- `PlayerSettings.SetIcons` (6000.6, line 433-446) writes `icons[i]` into the platform's icon slots by index, so the
  helper always passes an array with exactly `GetIconSizes(...).Length` entries.

uGUI (`com.unity.ugui`, not in the reference source) – verified only by compiling against UnityEngine.UI 2020.3.21:
`Image` (`sprite`, `color`, `enabled`, `raycastTarget`, `type`/`Image.Type.Simple`, `preserveAspect`,
`useSpriteMesh`, `rectTransform`, `canvasRenderer`), `CanvasScaler` (`uiScaleMode`,
`CanvasScaler.ScaleMode.ConstantPixelSize`, `scaleFactor`, `referencePixelsPerUnit`), `GraphicRaycaster`,
`UnityEngine.EventSystems.IPointerClickHandler`, `PointerEventData`, `EventSystem`.

## 5. Stubbed APIs (harness only: `/tmp/claude-0/unityref/compile/Stubs/HARNESS_ONLY_UnityEditor6000_6_Stubs.cs`)

| Stubbed declaration | Copied from 6000.6.0f1 | Why |
|---|---|---|
| `UnityEditor.Build.NamedBuildTarget` (readonly struct, `IEquatable`, `IComparable`) | Editor/Mono/BuildPipeline/NamedBuildTarget.cs:13 | absent in UnityEditor 2021.1 |
| `NamedBuildTarget.Unknown` | Editor/Mono/BuildPipeline/NamedBuildTarget.cs:45 | " |
| `NamedBuildTarget.Standalone` | Editor/Mono/BuildPipeline/NamedBuildTarget.cs:47 | " |
| `NamedBuildTarget.TargetName` | Editor/Mono/BuildPipeline/NamedBuildTarget.cs:87 | " |
| `PlayerSettings.SetIcons(NamedBuildTarget, Texture2D[], IconKind)` | Editor/Mono/PlatformSupport/PlayerSettingsPlatformIcons.bindings.cs:433 | absent in 2021.1 |
| `PlayerSettings.GetIcons(NamedBuildTarget, IconKind)` | Editor/Mono/PlatformSupport/PlayerSettingsPlatformIcons.bindings.cs:463 | absent in 2021.1 |
| `PlayerSettings.GetIconSizes(NamedBuildTarget, IconKind)` | Editor/Mono/PlatformSupport/PlayerSettingsPlatformIcons.bindings.cs:513 | absent in 2021.1 |
| `PlayerSettings.SplashScreen` (nested class) | Editor/Mono/PlayerSettingsSplashScreen.bindings.cs:63 | re-declared only because the stub must shadow the whole `PlayerSettings` class (CS0436) |
| `PlayerSettings.SplashScreen.show` | Editor/Mono/PlayerSettingsSplashScreen.bindings.cs:111 | " |
| `PlayerSettings.SplashScreen.showUnityLogo` | Editor/Mono/PlayerSettingsSplashScreen.bindings.cs:114 | " |
| `TextureImporter.GetSourceTextureWidthAndHeight(out int, out int)` – stubbed as an **extension method** | Editor/Mono/AssetPipeline/TextureImporter.bindings.cs:399 | public since 2021.2; in real Unity the instance method takes precedence over the extension, so the package source binds to the real API |

`UnityEditor.IconKind` is not stubbed (present in 2021.1 and in 6000.6 `PlayerSettings.bindings.cs:310`).

## 6. What this does NOT prove

- **No real Unity 6000.6 compile.** The code was compiled with the .NET 8 SDK Roslyn compiler against
  UnityEngine 2021.3.33 modules, uGUI 2020.3.21 and UnityEditor 2021.1.14 plus a hand-written stub. Unity's own
  compiler, its Roslyn analyzers/suppressors, the asmdef resolution (`"UnityEngine.UI"` name reference) and the
  6000.6 assemblies were not exercised. APIs that exist in both the old references and 6000.6 were compared by
  signature in the 6000.6 source only.
- **Stubbed APIs** (section 5) were type-checked only against signatures copied from the source, not against the
  real 6000.6 binaries; their runtime behaviour (e.g. how `SetIcons` treats Standalone / `Unknown`) was read from
  the C# source, the native parts (`GetIconWidthsForPlatform`, `SetIconsForPlatform`) are not visible.
- **uGUI** was verified only against the 2020.3.21 assembly; `com.unity.ugui` 2.x in Unity 6 is assumed to keep
  these long-stable members.
- **No runtime test.** Nothing ran inside Unity: no Play Mode, no prefab creation, no import, no scene edit, no
  EventSystem click, no CanvasGroup restore, no frame-time or GC measurement, no visual check of pixel snapping or
  scaling at real resolutions. "No per-frame allocation" is by code inspection only.
- The math test proves that `AvarnethStartupTimelineMath.cs` matches the contract and the Python reference
  evaluator bit-for-bit on the sampled frames (float32 data model); it does not prove Unity serializes the JSON
  values to the identical float32 values (JsonUtility parsing was not executed).
- The licence statement about the splash screen (documentation) is based on search-engine excerpts of Unity pages
  that could not be fetched from this machine.
