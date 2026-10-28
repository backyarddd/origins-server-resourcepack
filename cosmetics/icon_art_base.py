"""What every icon_art type file shares: drawn() (template + palette -> outlined icon), relabel(), and the palettes
more than one type uses. Imports no type file, so each type file imports on its own (see icon_art.py for the rules)."""
from cosmetics import art, icons
from cosmetics import build as cb
from cosmetics.art import shades

ROLES = 'OMLWX'


def relabel(palette, chars, roles=ROLES):
    """A palette's roles under new template characters: relabel(P_ORANGE, 'omlw') -> {'o': P_ORANGE['O'], ...}, so
    two palettes of one effect can share a template."""
    assert len(chars) <= len(roles), f'relabel: {chars!r} names more roles than {roles!r}'
    return {c: palette[r] for c, r in zip(chars, roles)}


def drawn(template, palette):
    """A 16x16 template + palette -> callable that returns the outlined icon. The template is checked now, so a bad one
    fails at import, not halfway through a build."""
    assert len(template) == 16 and all(len(row) == 16 for row in template), 'icon templates are 16 rows of 16'
    unknown = {ch for row in template for ch in row if ch != '.'} - set(palette)
    assert not unknown, f'icon template uses roles with no colour: {"".join(sorted(unknown))}'

    def make():
        return icons.outline(art.sprite(template, palette))
    return make


def rainbow(i, chars, roles=ROLES):
    """RAINBOW[i] as the effects shade it (art.shades), its roles (default O, M, L, W order) under chars."""
    return relabel(shades(cb.RAINBOW[i]), chars, roles)


# src/emotes/emote_laugh.png's own colours (the face outline is left to the shared INK outline)
P_LAUGH = {'D': (0xFF, 0xE0, 0x7A), 'E': (0xFF, 0xC8, 0x3D), 'H': (0xE0, 0x9A, 0x1F), 'F': (0x3B, 0x24, 0x12),
           'G': (0xFF, 0xFF, 0xFF), 'I': (0xE5, 0x38, 0x3B), 'A': (0x4F, 0xB3, 0xFF), 'B': (0xBF, 0xE6, 0xFF)}
# src/emotes/emote_skull.png's own colours: W bone, G bone shade, D sockets (its outline is left to the shared INK)
P_SKULL = {'W': (0xFF, 0xFF, 0xFF), 'G': (0xC9, 0xCE, 0xD6), 'D': (0x3B, 0x24, 0x12)}
