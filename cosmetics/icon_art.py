"""Hand-drawn 16x16 menu icons for the effect cosmetics (aura, trail, sendout, victory) and the nickname styles.

Each type keeps its own templates in one file: icon_art_aura.py, icon_art_trail.py, icon_art_burst.py (sendout),
icon_art_victory.py and icon_art_nick.py. Each exports ICONS {cosmetic id: callable -> 16x16 RGBA}, merged here into
ICONS, which icons.flat_icon looks up before anything else. What they share (drawn, relabel, rainbow and the palettes
more than one type uses) lives in icon_art_base.py, which imports no type file, so every type file imports on its own.

A template follows the house convention (cosmetics/art.py header): 16 strings of 16 characters, '.' transparent, every
other character a role the palette maps to an RGB colour; binary alpha, deterministic, original art only. Draw the art
alone: icons.outline adds the shared INK outline (RIM next to near-black art) round it afterwards, so leave one clear
pixel between shapes that should read apart and keep row / column 0 and 15 clear next to art. Rules every icon keeps:
- the shapes are the effect's own sprites (cosmetics/build.py EFFECTS / PARTS, art_fx2.py EFFECTS2 / PARTS2) redrawn
  bigger, never a different motif, laid out the way the effect moves in game;
- the colours are that effect's own palette (relabel maps its O / M / L / W / X roles onto template characters);
  rainbow-tinted effects use RAINBOW in order;
- light from the top-left; with the outline, the opaque box is >= 12 px in its larger dimension.

To add an icon: draw its template in its type's file and add the id to that file's ICONS.
"""
from cosmetics import icon_art_aura, icon_art_burst, icon_art_nick, icon_art_trail, icon_art_victory

ICONS = {}
for _part in (icon_art_aura, icon_art_trail, icon_art_burst, icon_art_victory, icon_art_nick):
    _dup = set(ICONS) & set(_part.ICONS)
    assert not _dup, f'{_part.__name__}: icon ids already registered: {", ".join(sorted(_dup))}'
    ICONS.update(_part.ICONS)
