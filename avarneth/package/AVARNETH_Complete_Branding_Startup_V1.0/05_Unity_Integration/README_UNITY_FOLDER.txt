AVARNETH: VEIL OF EMBERS - Unity startup overlay (Unity 6000.6, URP 2D, Windows x64)

Copy this whole 05_Unity_Integration folder into the project, e.g. Assets/AVARNETH/Startup/
(no package manager, no extra frameworks, no custom shaders; the standard UI/Default material is used).

  Runtime/            AvarnethStartupAnimation + pure C# timeline math (asmdef Eckertengineering.Avarneth.Startup)
  Editor/             Tools > AVARNETH > Startup menu (asmdef Eckertengineering.Avarneth.Startup.Editor, Editor only)
  Importable_Assets/  filled by the art pipeline; must contain:
                        Layers/  Frames/  Particles/  Icons/  Animation_Timeline.json
  Prefabs/            generated in Unity by "Create or Update Startup Prefab" (AvarnethStartup.prefab)
  Materials/          intentionally empty: the standard UI/Default material is used

Order: Configure Sprite Import Settings -> Create or Update Startup Prefab -> open the existing
bootstrap/login scene -> Add Startup Overlay To Open Scene... -> save the scene yourself.
The installer finds Importable_Assets via Animation_Timeline.json (schema avarneth.startup.timeline/1),
so the folder may live anywhere under Assets/. Full guide: 07_Documentation/UNITY_INSTALLATION.md
