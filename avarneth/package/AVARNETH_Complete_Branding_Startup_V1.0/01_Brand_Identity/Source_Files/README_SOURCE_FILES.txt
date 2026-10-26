AVARNETH source data
====================
native_1x/   Master pixel art at native resolution (1 art pixel = 1 image pixel), as generated.
             Use these as the reference for any manual retouching; note that re-running the generator
             recreates all files from code (edit generator/*.py to change the art permanently).
exports_2x/  Integer nearest-neighbour upscales x2.
exports_8x/  Integer nearest-neighbour upscales x8 (4K / print).
             (The x4 exports - 1080p - are in the parent folder.)
palette/     Master palette (GIMP .gpl, .hex, code table, swatch). All brand pixels use only these colours.
pixelmaps/   Generated text dumps (palette cell codes) of the per-size icon drawings 16-42 px and the
             48/64 px icon masters - for review and manual pixel edits; they are output, not input.
generator/   Python 3 sources that generate every asset deterministically
             (numpy, pillow, scipy; ffmpeg for previews):
               AVARNETH_PACKAGE_DIR=/path/to/output python3 build_all.py
             Without AVARNETH_PACKAGE_DIR the output goes to ../package/AVARNETH_Complete_Branding_Startup_V1.0
             relative to the generator folder (copy generator/ to a work folder first).
             qa.py / crosscheck.py / qa_report.py / finalize.py are the QA tools used for this delivery; the C#
             checks additionally need the compile harness described in 07_Documentation/UNITY_COMPILE_EVIDENCE.md
             (not shipped: it contains signatures copied from Unity's reference-only source).
Never scale these images with bilinear/bicubic filtering - integer nearest-neighbour only.
