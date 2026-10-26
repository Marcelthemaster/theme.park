AVARNETH source data
====================
native_1x/   Master pixel art at native resolution (1 art pixel = 1 image pixel). Edit these.
exports_2x/  Integer nearest-neighbour upscales x2.
exports_8x/  Integer nearest-neighbour upscales x8 (4K / print).
             (The x4 exports - 1080p - are in the parent folder.)
palette/     Master palette (GIMP .gpl, .hex, code table, swatch). All brand pixels use only these colours.
pixelmaps/   Hand-specified 16/24/32 px icons as editable palette-code text grids.
generator/   Python 3 sources that generate every asset deterministically
             (requires numpy, pillow, scipy, ffmpeg for previews):  python3 build_all.py
Never scale these images with bilinear/bicubic filtering - integer nearest-neighbour only.
