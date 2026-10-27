"""Pixel-art helpers for the cosmetics: every particle sprite is an original ASCII template drawn here, coloured by a
palette; the hats / back items (WEARABLES) and front items (FRONTS) are boxes painted texel by texel, and the ball skins
(BALL_SKINS_ART) are painted onto the box UV of each Cobblemon ball geometry. The tool skin sets live in
cosmetics/toolsets.py. No texture from Mojang, Cobblemon or bought packs is used.

A template is a list of equal-length strings; '.' is transparent and every other character is a role that the palette
maps to an RGB colour. Alpha is binary. Nothing here is random, so the same palette always gives the same bytes.

Particle roles: O outline / darkest, M mid, L light, W highlight, X accent.
"""
import math

from PIL import Image

NAVY, GOLD, LIGHT_GOLD, CREAM = (0x1B, 0x2E, 0x5B), (0xE2, 0xB0, 0x4A), (0xF7, 0xD2, 0x7A), (0xFF, 0xF1, 0xD0)

# 8x8 particle sprites
CIRCLE = [
    "........",
    "..OOOO..",
    ".OLWMMO.",
    ".OWLMMO.",
    ".OMMMMO.",
    ".OMMMMO.",
    "..OOOO..",
    "........",
]
DUST = [
    "........",
    "........",
    "...LM...",
    "..LWMM..",
    "..MMMO..",
    "...MO...",
    "........",
    "........",
]
STAR = [
    "...W....",
    "...L....",
    "..LWL...",
    "WLWWWLW.",
    "..LWL...",
    "...L....",
    "...W....",
    "........",
]
SPARK = [
    "........",
    ".L...L..",
    "..M.M...",
    "...W....",
    "..M.M...",
    ".L...L..",
    "........",
    "........",
]
ZAP = [
    ".....WL.",
    "....WL..",
    "...WL...",
    "..WWWWL.",
    "....WL..",
    "...WL...",
    "..WL....",
    "..L.....",
]
FLAME = [
    "...W....",
    "...LW...",
    "..MLW...",
    "..MLWL..",
    ".MLWWLM.",
    ".MLWWLM.",
    ".OMLLMO.",
    "..OMMO..",
]
PETAL = [
    "........",
    "....OO..",
    "...OLLO.",
    "..OLWLO.",
    ".OLLMO..",
    ".OMMO...",
    "..OO....",
    "........",
]
FLAKE = [
    "...W....",
    ".W.L.W..",
    "..LWL...",
    "WLWWWLW.",
    "..LWL...",
    ".W.L.W..",
    "...W....",
    "........",
]
NOTE = [
    "....OO..",
    "....OLO.",
    "....O.LO",
    "....O...",
    "..OOO...",
    ".OLMO...",
    ".OMMO...",
    "..OO....",
]
HEART = [
    "........",
    ".OO.OO..",
    "OLWOMMO.",
    "OWLMMMO.",
    "OMMMMMO.",
    ".OMMMO..",
    "..OMO...",
    "...O....",
]
COIN = [
    "..OOOO..",
    ".OLLLMO.",
    "OLWLWLMO",
    "OLLMWMMO",
    "OLLMWMMO",
    "OLMMWMMO",
    ".OMMMMO.",
    "..OOOO..",
]
CROWN = [
    "........",
    "W..W..W.",
    "L..L..L.",
    "LM.L.ML.",
    "MLMWMLM.",
    "MMXMXMM.",
    "OOOOOOO.",
    "........",
]
BAT = [
    "........",
    "...O.O..",
    "O..OOO.O",
    "OO.XOX.O",
    "OMOOOOMO",
    ".OM.O.M.",
    "..O...O.",
    "........",
]
PUMPKIN = [
    "...XX...",
    "..OMMO..",
    ".OMLMLO.",
    "OMWMMWMO",
    "OMLMMLMO",
    "OMWWWWMO",
    ".OMMMMO.",
    "..OOOO..",
]
SMOKE = [
    "........",
    "..MMM...",
    ".MLLMM..",
    "MLWLMMM.",
    "MLMMMMMO",
    ".MMMMOO.",
    "..OOO...",
    "........",
]
BUBBLE = [
    "..OOOO..",
    ".O....O.",
    "O.W....O",
    "O.W....O",
    "O......O",
    "O.....LO",
    ".O...LO.",
    "..OOOO..",
]
LEAF = [
    "......OO",
    "....OOLO",
    "...OLLMO",
    "..OLWMO.",
    ".OLMMO..",
    ".OMMO...",
    "O.OO....",
    "........",
]
CONFETTI = [
    "........",
    "........",
    "..LLM...",
    "..LMMO..",
    "..MMOO..",
    "...OO...",
    "........",
    "........",
]

# 16x16 particle sprites
BIG_CROWN = [
    "................",
    "..W....W....W...",
    ".WLW..WLW..WLW..",
    "..L....L....L...",
    "..LM..MLM..ML...",
    "..LLM.MLM.MLL...",
    "..LWLMLWLMLWL...",
    "..LLLLLLLLLLL...",
    "..MLXLLXLLXLM...",
    "..MLXXLXXLXXM...",
    "..MLLLLLLLLLM...",
    "..MMMMMMMMMMM...",
    "..WLWLWLWLWLW...",
    "..OOOOOOOOOOO...",
    "................",
    "................",
]
BOLT = [
    "..........WWL...",
    ".........WWL....",
    "........WWL.....",
    ".......WWL......",
    "......WWL.......",
    ".....WWWWWWL....",
    "........WWL.....",
    ".......WWL......",
    "......WWL.......",
    ".....WWWWWWL....",
    "........WWL.....",
    ".......WWL......",
    "......WWL.......",
    ".....WWL........",
    "....WL..........",
    "...L............",
]

def hexrgb(h):
    h = h.lstrip('#')
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def sprite(template, palette):
    """Draw a template; palette maps role characters to (r, g, b). Unmapped roles fail loudly."""
    h, w = len(template), len(template[0])
    assert all(len(row) == w for row in template), 'template rows must be equal length'
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    for y, row in enumerate(template):
        for x, ch in enumerate(row):
            if ch != '.':
                px[x, y] = palette[ch] + (255,)
    return im


def strip(images):
    """Lay equal-size frames left to right into one sheet."""
    w, h = images[0].size
    assert all(i.size == (w, h) for i in images), 'frames must share one size'
    sheet = Image.new('RGBA', (w * len(images), h), (0, 0, 0, 0))
    for i, im in enumerate(images):
        sheet.paste(im, (i * w, 0))
    return sheet


def shades(base, light=None, dark=None):
    """Palette O/M/L/W/X from one base colour: darker outline, base mid, lighter light, near-white highlight."""
    r, g, b = hexrgb(base) if isinstance(base, str) else base
    mix = lambda c, t, f: tuple(round(a + (t_ - a) * f) for a, t_ in zip(c, t))  # noqa: E731
    m = (r, g, b)
    return {'O': hexrgb(dark) if dark else mix(m, (0, 0, 0), 0.45), 'M': m,
            'L': hexrgb(light) if light else mix(m, (255, 255, 255), 0.4), 'W': mix(m, (255, 255, 255), 0.75),
            'X': mix(m, (255, 255, 255), 0.75)}


# ---------------------------------------------------------------------------------------------------------------------
# Wearables (hats, back items): vanilla JSON block models drawn as boxes in the client contract's model space, in
# pixels: (8, 0, 8) = bone pivot (the neck), +y up, +z toward the player's back, +x toward the player's own right (a
# Blockbench model facing north). Head cube
# x 4..12, y 0..8, z 4..12 (its skin overlay reaches 0.5 further); torso x 4..12, y -12..0, z 6..10 (overlay to 10.25).
# An element is dict(frm, to, paint[, rot=(axis, angle, origin)][, skip=faces][, mirror=True]). paint(face, i, j, w, h,
# p) returns the role of texel (i, j) of a w x h face, '.' for transparent; p is the texel centre in model space before
# rotation (for a mirrored element: x as on the unmirrored original, so one painter serves both wings).

def h32(*vals):
    """Small deterministic hash (FNV-1a over ints) for speckle patterns; no randomness anywhere."""
    x = 2166136261
    for v in vals:
        x = ((x ^ (v & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return x


def el(frm, to, paint, rot=None, skip=()):
    return {'frm': list(frm), 'to': list(to), 'paint': paint, 'rot': rot, 'skip': set(skip)}


def mirrored(e):
    """The element reflected through x = 8 (the player's centre line)."""
    rot = e['rot']
    if rot:
        axis, angle, origin = rot
        rot = (axis, -angle if axis in 'yz' else angle, [16 - origin[0]] + list(origin[1:]))
    return {**e, 'frm': [16 - e['to'][0]] + e['frm'][1:], 'to': [16 - e['frm'][0]] + e['to'][1:], 'rot': rot,
            'mirror': not e.get('mirror', False)}


def pair(elements):
    """The elements plus their mirror images (left and right wing)."""
    return elements + [mirrored(e) for e in elements]


def _solid(role):
    return lambda face, i, j, w, h, p: role


def bevel(m='M', light='L', dark='O', top=None, bottom=None):
    """Sides: light top row, dark bottom row, mid between; up / down faces take top / bottom (default light / dark)."""
    def paint(face, i, j, w, h, p):
        if face == 'up':
            return top or light
        if face == 'down':
            return bottom or dark
        if j == 0:
            return light
        return dark if j == h - 1 and h > 2 else m
    return paint


def gem(face, i, j, w, h, p):
    """A cut stone: highlight in the top-left texel, shadow in the bottom-right."""
    if (i, j) == (0, 0):
        return 'n'
    return 'k' if (i, j) == (w - 1, h - 1) else 'N'


def _sparkle_ring(face, i, j, w, h, p):
    if face == 'up':
        return 'W' if (i + j) % 4 == 0 else 'L'
    return 'D' if face == 'down' else ('L' if j == 0 else 'M')


def _top_hat_crown(face, i, j, w, h, p):
    if face in ('up', 'down'):
        return 'L' if 0 in (i, j) or i == w - 1 or j == h - 1 else 'M'
    if j == 0:
        return 'L'
    return 'W' if i == 2 else 'M'  # one sheen stripe down each side


def _brim(face, i, j, w, h, p):
    if face == 'up':
        return 'L' if 0 in (i, j) or i == w - 1 or j == h - 1 else 'M'
    return 'O'


def _cap_crown(face, i, j, w, h, p):
    if face == 'up':
        return 'k' if i == w // 2 or j == h // 2 else 'N'  # panel seams
    if face == 'down':
        return 'k'
    return 'n' if j == 0 else ('k' if j == h - 1 else 'N')


def _emblem(face, i, j, w, h, p):
    if face != 'north':
        return 'd'
    if 0 in (i, j) or i == w - 1 or j == h - 1:
        return 'G'
    return 'W' if i in (w // 2 - 1, w // 2) and j in (h // 2 - 1, h // 2) else 'N'


def _vine(face, i, j, w, h, p):
    return 'l' if int(p[0] + p[2]) % 3 == 0 else ('v' if face == 'down' else 'V')


def _flower(petal, shade, centre):
    def paint(face, i, j, w, h, p):
        if face == 'up':
            if (i in (0, w - 1)) and (j in (0, h - 1)):
                return '.'
            return centre if 0 < i < w - 1 and 0 < j < h - 1 else petal
        if face == 'down':
            return shade
        return petal if j == 0 else shade
    return paint


def _witch(face, i, j, w, h, p):
    if face == 'up':
        return 'L'
    if face == 'down':
        return 'D'
    return 'L' if j == 0 else ('D' if j == h - 1 and h > 3 else 'M')


def _pack_body(face, i, j, w, h, p):
    if face in ('up', 'down'):
        return 'D'
    if 0 in (i, j) or i == w - 1 or j == h - 1:
        return 'D'
    return 'L' if (i + j) % 7 == 0 else 'M'  # worn leather grain


def _pack_flap(face, i, j, w, h, p):
    if face == 'up':
        return 'n' if j == 0 else 'N'
    if face == 'down':
        return 'k'
    return 'g' if j == h - 1 else ('n' if j == 0 else 'N')  # gold trim along the bottom edge


def _pocket(face, i, j, w, h, p):
    if face != 'south':
        return 'D'
    return 'S' if 0 in (i, j) or i == w - 1 or j == h - 1 else 'M'


def _buckle(face, i, j, w, h, p):
    if face != 'south':
        return 'd'
    return 'd' if 0 < i < w - 1 and 0 < j < h - 1 else 'g'


def _bedroll(face, i, j, w, h, p):
    if face in ('east', 'west'):
        return 'r' if (i, j) in ((1, 1), (1, 2), (2, 1), (2, 2)) else 'R'  # rolled-up spiral end
    return 'r' if int(p[0] * 2) % 6 == 0 else 'R'  # tie bands


def _feathers(cut_from_x, cut_below_y):
    """White feathers in overlapping rows; the outer lower corner is cut away so the wing tapers to a tip."""
    def paint(face, i, j, w, h, p):
        x, y = p[0], p[1]
        if x > cut_from_x and y < cut_below_y + (x - cut_from_x) * 1.2:
            return '.'
        if face in ('up', 'east', 'west', 'down'):
            return 'w'
        row = int((y + 20) * 2) % 3
        return 'g' if row == 0 else ('W' if (int(x * 2) + row) % 4 else 'w')
    return paint


def _strap(face, i, j, w, h, p):
    if face in ('north', 'south'):
        return 'S' if i in (0, w - 1) and j % 3 == 0 else 'M'  # stitching
    return 'D'


def _mini_ball(face, i, j, w, h, p, cy):
    dy = p[1] - cy
    if face == 'south' and abs(p[0] - 8) < 0.5 and abs(dy) < 0.5:
        return 'W' if abs(p[0] - 8) < 0.25 and abs(dy) < 0.25 else 'K'
    if face == 'up':
        return 'q' if i == 1 and j == 1 else 'R'
    if face == 'down':
        return 'W'
    if abs(dy) < 0.125 + 0.125:
        return 'K'
    if dy > 0:
        return 'q' if dy > 0.75 and i == 1 else 'R'
    return 'w' if dy < -0.75 else 'W'


def _bat_wing(face, i, j, w, h, p):
    x, y = p[0], p[1]
    # three scallops between the finger tips along the lower edge
    seg = (x - 9) / (5.5 / 3)
    frac = seg - int(seg)
    if y < -7.5 + 2.2 * (1 - (2 * frac - 1) ** 2) and x > 9.4:
        return '.'
    if face not in ('north', 'south'):
        return 'O'
    if y > -1.6:
        return 'O'  # arm bone along the top
    # finger bones fanning out from the wrist (inner top corner)
    for slope in (0.35, 0.95, 2.2):
        if abs((-1.3 - y) - slope * (x - 9.2)) < 0.3:
            return 'O'
    return 'L' if (i + j) % 5 == 0 else 'M'


def _ball_strap_paint(cy):
    return lambda face, i, j, w, h, p: _mini_ball(face, i, j, w, h, p, cy)


BAND_ROT = ('z', -22.5, [8, -6, 10.5])  # bandolier: top end over the player's right shoulder (+x)
WING_ROT = ('y', -22.5, [8.5, -3, 10.5])  # wings swing their outer edge back (+z), away from the torso
BAT_ROT = ('y', -22.5, [9, -4, 10.5])

DARK_GOLD = (0x7A, 0x53, 0x13)
WEARABLES = {
    'hat_royal_crown': dict(
        palette={'O': DARK_GOLD, 'D': (0xB0, 0x7A, 0x22), 'M': GOLD, 'L': LIGHT_GOLD, 'W': CREAM, 'N': NAVY,
                 'n': (0x4A, 0x6F, 0xC4), 'k': (0x0E, 0x18, 0x30)},
        elements=[
            el((3, 7.5, 3), (13, 10, 3.5), bevel()), el((3, 7.5, 12.5), (13, 10, 13), bevel()),
            el((3, 7.5, 3.5), (3.5, 10, 12.5), bevel()), el((12.5, 7.5, 3.5), (13, 10, 12.5), bevel()),
            # corner posts and middle points
            el((3, 10, 3), (4, 12, 4), bevel(top='W')), el((12, 10, 3), (13, 12, 4), bevel(top='W')),
            el((3, 10, 12), (4, 12, 13), bevel(top='W')), el((12, 10, 12), (13, 12, 13), bevel(top='W')),
            el((7.5, 10, 3), (8.5, 12.5, 3.5), bevel(top='W')), el((7.5, 10, 12.5), (8.5, 12.5, 13), bevel(top='W')),
            el((3, 10, 7.5), (3.5, 12.5, 8.5), bevel(top='W')), el((12.5, 10, 7.5), (13, 12.5, 8.5), bevel(top='W')),
            # navy gems: three on the front, one on each other side
            el((7.25, 8, 2.5), (8.75, 9.5, 3), gem), el((4.5, 8.25, 2.5), (5.5, 9.25, 3), gem),
            el((10.5, 8.25, 2.5), (11.5, 9.25, 3), gem), el((7.25, 8, 13), (8.75, 9.5, 13.5), gem),
            el((2.5, 8, 7.25), (3, 9.5, 8.75), gem), el((13, 8, 7.25), (13.5, 9.5, 8.75), gem),
        ]),
    'hat_top_hat': dict(
        palette={'O': (0x0C, 0x0C, 0x0E), 'M': (0x1E, 0x1E, 0x24), 'L': (0x34, 0x34, 0x3E), 'W': (0x4A, 0x4A, 0x58),
                 'd': (0xB0, 0x7A, 0x22), 'G': GOLD, 'g': LIGHT_GOLD},
        elements=[
            el((2, 8.5, 2), (14, 9, 14), _brim),
            el((4.5, 9, 4.5), (11.5, 15.5, 11.5), _top_hat_crown),
            el((4, 9, 4), (12, 10.5, 12), bevel(m='G', light='g', dark='d'), skip=('up', 'down')),
        ]),
    'hat_origins_cap': dict(
        palette={'N': NAVY, 'n': (0x2E, 0x4A, 0x8C), 'k': (0x0E, 0x18, 0x30), 'G': GOLD, 'g': LIGHT_GOLD,
                 'd': (0xB0, 0x7A, 0x22), 'W': CREAM},
        elements=[
            el((3, 6.5, 3), (13, 10, 13), _cap_crown),
            el((4, 10, 4), (12, 11, 12), _cap_crown),
            el((7.5, 11, 7.5), (8.5, 11.5, 8.5), bevel(m='G', light='g', dark='d')),
            el((4, 6.5, -0.5), (12, 7, 3), bevel(m='G', light='g', dark='d', top='G')),  # brim, toward the front
            el((6.5, 7.5, 2.5), (9.5, 9.5, 3), _emblem),
        ]),
    'hat_flower_crown': dict(
        palette={'V': (0x3F, 0x8A, 0x3A), 'v': (0x2E, 0x6B, 0x24), 'l': (0x7C, 0xCB, 0x62),
                 'P': (0xFF, 0x9C, 0xC7), 'p': (0xC2, 0x50, 0x7F), 'F': (0xFF, 0xFF, 0xFF), 'f': (0xC9, 0xD3, 0xDE),
                 'Y': (0xFF, 0xE0, 0x66), 'y': (0xC9, 0x9A, 0x12), 'o': (0xFF, 0x9F, 0x3D)},
        elements=[
            el((3, 8, 3), (13, 8.5, 3.5), _vine), el((3, 8, 12.5), (13, 8.5, 13), _vine),
            el((3, 8, 3.5), (3.5, 8.5, 12.5), _vine), el((12.5, 8, 3.5), (13, 8.5, 12.5), _vine),
        ] + [
            el((cx - 1, 8.25, cz - 1), (cx + 1, 9.25, cz + 1), _flower(*look))
            for (cx, cz), look in zip(
                [(3.25, 3.25), (6.5, 3.25), (9.5, 3.25), (12.75, 3.25), (12.75, 6.5), (12.75, 9.5),
                 (12.75, 12.75), (9.5, 12.75), (6.5, 12.75), (3.25, 12.75), (3.25, 9.5), (3.25, 6.5)],
                [('P', 'p', 'Y'), ('F', 'f', 'Y'), ('Y', 'y', 'o')] * 4)
        ]),
    'hat_golden_halo': dict(
        palette={'D': (0xB0, 0x7A, 0x22), 'M': GOLD, 'L': LIGHT_GOLD, 'W': CREAM},
        # an octagon: four bars, and the same four turned 45 degrees about the head's vertical axis
        elements=[el(f, t, _sparkle_ring, rot=r) for r in (None, ('y', 45, [8, 11, 8])) for f, t in (
            ((6, 11, 3), (10, 11.5, 4)), ((6, 11, 12), (10, 11.5, 13)),
            ((3, 11, 6), (4, 11.5, 10)), ((12, 11, 6), (13, 11.5, 10)))]),
    'hat_witch': dict(
        palette={'O': (0x2E, 0x1A, 0x47), 'D': (0x43, 0x2A, 0x6A), 'M': (0x5B, 0x3A, 0x8C), 'L': (0x7E, 0x57, 0xB5),
                 'B': (0xFF, 0x8A, 0x1F), 'b': (0xC2, 0x5A, 0x0A), 'c': (0xFF, 0xC0, 0x4D)},
        elements=[
            el((1.5, 8.5, 1.5), (14.5, 9, 14.5), bevel(m='M', light='L', dark='D', bottom='O')),
            el((4, 9, 4), (12, 12, 12), _witch),
            el((3.5, 9, 3.5), (12.5, 10.5, 12.5), bevel(m='B', light='c', dark='b'), skip=('up', 'down')),
            el((5, 12, 5.5), (11, 14.5, 11), _witch),
            el((6, 14.5, 7), (10, 16.5, 11), _witch),
            # the bent tip leans back toward +z
            el((6.5, 16, 8.5), (9.5, 18, 11.5), _witch, rot=('x', 22.5, [8, 16, 10])),
            el((7, 17, 11), (9, 18.5, 13.5), _witch, rot=('x', 45, [8, 17.5, 11.5])),
        ]),
    'back_explorer_pack': dict(
        palette={'O': (0x3E, 0x26, 0x14), 'D': (0x5C, 0x35, 0x19), 'M': (0x7A, 0x4A, 0x26),
                 'L': (0x9C, 0x6A, 0x3C), 'S': (0xC9, 0xA2, 0x7A), 'N': NAVY, 'n': (0x2E, 0x4A, 0x8C),
                 'k': (0x0E, 0x18, 0x30), 'g': GOLD, 'd': (0x7A, 0x53, 0x13), 'R': (0xD9, 0xC4, 0x9A),
                 'r': (0xA8, 0x91, 0x5F)},
        elements=[
            el((5, -10.5, 10.5), (11, -2.5, 13.5), _pack_body),
            el((4.5, -5, 10.5), (11.5, -2, 14), _pack_flap),
            el((7, -5.5, 14), (9, -4, 14.5), _buckle),
            el((6, -9.5, 13.5), (10, -6.5, 14), _pocket),
            el((4, -2, 10.75), (12, -0.5, 12.25), _bedroll),
        ]),
    'back_feather_wings': dict(
        palette={'W': (0xFF, 0xFF, 0xFF), 'w': (0xE8, 0xEE, 0xF4), 'g': (0xC9, 0xD3, 0xDE)},
        elements=pair([el((8.5, -6, 10.5), (14, -0.5, 11), _feathers(12.5, -4.5), rot=WING_ROT),
                       el((9, -10, 10.75), (13.5, -6, 11.25), _feathers(11, -10.5), rot=WING_ROT)])),
    'back_ball_bandolier': dict(
        density=4,
        palette={'D': (0x3E, 0x26, 0x14), 'M': (0x7A, 0x4A, 0x26), 'S': (0xC9, 0xA2, 0x7A),
                 'R': (0xE3, 0x41, 0x2F), 'q': (0xFF, 0x7A, 0x66), 'W': (0xFF, 0xFF, 0xFF), 'w': (0xD6, 0xDC, 0xE4),
                 'K': (0x1A, 0x1A, 0x1A), 'g': GOLD, 'd': (0x7A, 0x53, 0x13)},
        elements=[
            el((7.25, -12.5, 10.25), (8.75, 0.5, 10.75), _strap, rot=BAND_ROT),
            el((7, -1, 10.75), (9, 0, 11), _buckle, rot=BAND_ROT),
        ] + [el((7, cy - 1, 10.75), (9, cy + 1, 12.25), _ball_strap_paint(cy), rot=BAND_ROT)
             for cy in (-10, -6.5, -3)]),
    'back_bat_wings': dict(
        palette={'O': (0x1A, 0x10, 0x24), 'M': (0x3A, 0x24, 0x50), 'L': (0x4A, 0x30, 0x66)},
        elements=pair([el((9, -7.5, 10.5), (14.5, -1, 11), _bat_wing, rot=BAT_ROT),
                       el((14, -1, 10.5), (14.5, 0, 11), _solid('O'), rot=BAT_ROT)])
        + [el((7, -4.5, 10.25), (9, -1.5, 10.75), _solid('O'))]),
}


# Front items: drawn on the body bone like the back items, on the chest. The torso's front face is z = 6; every cube
# stays at z <= 6.5 (check.FRONT_BOX), so it sits on the chest and sinks at most 0.5 into it. The collar line is y = 0.

def _scarf_band(face, i, j, w, h, p):
    """Collar band: navy with a gold stripe every 3 pixels, a lit top edge and a shadowed bottom edge."""
    if face == 'up':
        return 'n'
    if face == 'down':
        return 'k'
    if j == 0:
        return 'n'
    if j == h - 1:
        return 'k'
    return 'G' if int(p[0] * 2) % 6 == 0 else 'N'


def _scarf_tail(stripe, main, light, dark, tip=None, flame=False):
    """A hanging scarf end: stripes across it, a fringe (or flame points) at the bottom edge."""
    def paint(face, i, j, w, h, p):
        if face in ('up', 'down'):
            return dark
        if face in ('east', 'west'):
            return dark if j >= h - 2 else main
        if flame:
            # three flame points: the bottom 4 rows are cut into tongues of different heights
            cut = h - 1 - j
            if cut < 4 and (i % 4 in (0, 3)) and cut < 4 - (i // 4) % 2 * 2:
                return '.'
            if tip and j >= h - 6:
                return tip if (i + j) % 3 else light
        elif j == h - 1 and i % 2:
            return '.'  # fringe
        if stripe and j % 6 == 3:
            return stripe
        return light if i == 0 else dark if i == w - 1 else main
    return paint


def _knot(face, i, j, w, h, p):
    if face == 'north':
        return 'n' if (i, j) == (0, 0) else 'k' if j == h - 1 or i == w - 1 else 'N'
    return 'k'


def _ribbon(face, i, j, w, h, p):
    """Navy ribbon with gold edges."""
    if face != 'north':
        return 'k'
    return 'G' if i in (0, w - 1) else 'N'


def _medal(face, i, j, w, h, p):
    """A gold disc with a raised five-point star (north face), dark gold rim elsewhere."""
    if face != 'north':
        return 'D'
    cx, cy = (w - 1) / 2, (h - 1) / 2
    dx, dy = i - cx, j - cy
    r = math.hypot(dx, dy)
    if r > w / 2:
        return '.'
    if r > w / 2 - 1.2:
        return 'D' if dx + dy > 0 else 'L'
    a = math.atan2(-dy, dx) - math.pi / 2  # 0 = straight up
    star = 1.9 + 2.3 * abs(math.cos(a * 5 / 2)) ** 3
    if r <= star:
        return 'W' if dx + dy < 0 else 'L'
    return 'M'


BADGES = [  # 8 original 5x5 badge shapes and their colours, top to bottom along the sash
    (["..#..", ".###.", "#####", ".###.", "..#.."], 'b1'),  # diamond
    ([".###.", "#####", "#####", "#####", ".###."], 'b2'),  # round
    (["...##", "..###", ".###.", "###..", "#...."], 'b3'),  # leaf
    (["..##.", ".##..", "####.", "..##.", ".##.."], 'b4'),  # bolt
    (["..#..", "#####", ".###.", ".#.#.", "#...#"], 'b5'),  # star
    (["##.##", "#####", "#####", ".###.", "..#.."], 'b6'),  # heart
    (["..#..", ".###.", ".###.", "#####", ".###."], 'b7'),  # drop
    (["#####", "#####", "#####", ".###.", "..#.."], 'b8'),  # shield
]


def _sash(face, i, j, w, h, p):
    """Red sash with gold edges carrying the 8 badges down its front."""
    if face != 'north':
        return 'r'
    if i in (0, w - 1):
        return 'G'
    for k, (shape, colour) in enumerate(BADGES):
        top = 2 + k * 6
        bi, bj = i - (w - 5) // 2, j - top
        if 0 <= bi < 5 and 0 <= bj < 5 and shape[bj][bi] == '#':
            first = next(x for x in range(5) if shape[bj][x] == '#')
            return colour.upper() if bi == first or bj == 0 else colour
    return 'R' if (i + j) % 7 else 'q'


def _chain(face, i, j, w, h, p):
    """Silver chain: alternating light and dark links."""
    return 'C' if (i + j) % 2 == 0 else 'c'


def _crystal(face, i, j, w, h, p):
    """Glowing cyan crystal: white glint top-left, deep cyan bottom-right, bright core."""
    if face != 'north':
        return 'D'
    if (i, j) == (0, 0) or (i, j) == (1, 0):
        return 'W'
    if i == w - 1 or j == h - 1:
        return 'D'
    return 'L' if (i + j) % 3 == 0 else 'M'


def _bow_wing(face, i, j, w, h, p):
    """Bow tie wing: gold, pinched toward the knot (inner texels cut top and bottom), a fold shadow by the knot."""
    inner = abs(p[0] - 8)  # distance from the centre line in pixels
    if face == 'north':
        if inner < 1.25 and j in (0, h - 1):
            return '.'
        if inner < 1.25:
            return 'D'
        return 'W' if j == 0 and inner > 2 else 'L' if j == 0 else 'D' if j == h - 1 else 'M'
    return 'D'


def _bow_knot(face, i, j, w, h, p):
    return 'L' if face == 'north' and j == 0 else 'D' if face != 'north' else 'M'


def _vine_cord(face, i, j, w, h, p):
    return 'l' if int(p[1] * 2) % 3 == 0 else 'V'


def _pumpkin(face, i, j, w, h, p):
    """A tiny jack-o'-lantern: ribs on every side, carved eyes and grin glowing on the front."""
    if face == 'up':
        return 'b' if i % 3 == 0 else 'O'
    if face == 'down':
        return 'b'
    if face == 'north':
        eyes = j in (2, 3) and (i in (2, 3, w - 4, w - 3)) and not (j == 2 and i in (2, w - 3))
        mouth = (j == 5 and 2 <= i <= w - 3) or (j == 6 and 3 <= i <= w - 4 and i % 2)
        if eyes or mouth:
            return 'Y'
    if i % 3 == 0:
        return 'b'
    return 'o' if j == 0 else 'b' if j == h - 1 else 'O'


def _stem(face, i, j, w, h, p):
    return 'l' if face == 'up' or j == 0 else 'V'


SCARF_PAL = {'N': NAVY, 'n': (0x2E, 0x4A, 0x8C), 'k': (0x0E, 0x18, 0x30), 'G': GOLD, 'g': LIGHT_GOLD}
TIE_ROT = ('z', -22.5, [9.75, -3, 5.25])  # the long end swings a little toward the chest's centre
FRONT_SASH_ROT = ('z', 22.5, [8.25, -6, 5.75])  # right shoulder to left hip

FRONTS = {
    'front_trainer_scarf': dict(
        palette=SCARF_PAL,
        elements=[
            el((3.5, -2, 5), (12.5, 0, 6), _scarf_band),
            el((8, -3, 4.5), (10, -1.5, 5.5), _knot),
            el((9, -9, 5), (10.5, -3, 5.5), _scarf_tail('G', 'N', 'n', 'k'), rot=TIE_ROT),
        ]),
    'front_champion_medal': dict(
        density=4,
        palette={'N': NAVY, 'k': (0x0E, 0x18, 0x30), 'G': GOLD, 'D': (0xB0, 0x7A, 0x22), 'M': GOLD,
                 'L': LIGHT_GOLD, 'W': CREAM},
        elements=pair([el((6.5, -5, 5.5), (7.5, 0, 6), _ribbon, rot=('z', 22.5, [7, -5, 5.75]))]) + [
            el((7.5, -5.25, 5.25), (8.5, -4.5, 5.75), _bow_knot),
            el((6.5, -8.25, 5), (9.5, -5.25, 5.5), _medal),
        ]),
    'front_badge_sash': dict(
        density=4,
        palette={'R': (0xC8, 0x2A, 0x2A), 'r': (0x8A, 0x16, 0x1A), 'q': (0xB0, 0x22, 0x24), 'G': GOLD,
                 'b1': (0x9A, 0xA6, 0xC4), 'B1': (0xE8, 0xEE, 0xF8), 'b2': (0x55, 0xE6, 0xE6), 'B2': (0xC8, 0xFF, 0xFF),
                 'b3': (0x5D, 0xBB, 0x4A), 'B3': (0xB5, 0xF0, 0x8E), 'b4': (0xFF, 0xD2, 0x2E), 'B4': (0xFF, 0xF4, 0xB0),
                 'b5': (0xF7, 0xD2, 0x7A), 'B5': (0xFF, 0xFF, 0xFF), 'b6': (0xFF, 0x7A, 0xC8), 'B6': (0xFF, 0xD0, 0xEC),
                 'b7': (0x4A, 0x8C, 0xFF), 'B7': (0xB8, 0xD4, 0xFF),
                 'b8': (0xA3, 0x7B, 0xFF), 'B8': (0xE0, 0xD2, 0xFF)},
        elements=[el((7, -12.5, 5.5), (9.5, 0.5, 6), _sash, rot=FRONT_SASH_ROT)]),
    'front_crystal_amulet': dict(
        density=4,
        palette={'C': (0xE8, 0xEE, 0xF4), 'c': (0x8E, 0x9B, 0xAD), 'W': (0xFF, 0xFF, 0xFF),
                 'L': (0x9B, 0xEA, 0xF5), 'M': (0x55, 0xC3, 0xDE), 'D': (0x2F, 0x86, 0xA8)},
        elements=pair([el((7, -4.5, 5.5), (7.5, 0, 5.75), _chain, rot=('z', 22.5, [7.25, -4.5, 5.6]))]) + [
            el((7.25, -7.25, 5), (8.75, -5.75, 5.5), _crystal, rot=('z', 45, [8, -6.5, 5.25])),
            el((7.75, -5.25, 5.25), (8.25, -4.5, 5.5), _chain),
        ]),
    'front_ember_scarf': dict(
        palette={'O': (0xF0, 0x6A, 0x12), 'o': (0xFF, 0x9F, 0x3D), 'd': (0xB0, 0x3A, 0x08),
                 't': (0xC8, 0x24, 0x10), 'T': (0xFF, 0x5A, 0x1F)},
        elements=[
            el((3.5, -2, 5), (12.5, 0, 6), lambda f, i, j, w, h, p: 'o' if f == 'up' or j == 0 else
               'd' if f == 'down' or j == h - 1 else 'O'),
            # two loose ends hanging side by side, swinging toward the wearer's left
            el((8, -9, 5), (9.5, -2, 5.5), _scarf_tail(None, 'O', 'o', 'd', tip='t', flame=True),
               rot=('z', -22.5, [8.75, -2, 5.25])),
            el((9.75, -7, 5.25), (11.25, -2, 5.75), _scarf_tail(None, 'O', 'o', 'd', tip='T', flame=True),
               rot=('z', -22.5, [10.5, -2, 5.5])),
        ]),
    'front_gold_bow_tie': dict(
        density=4,
        palette={'M': GOLD, 'L': LIGHT_GOLD, 'W': CREAM, 'D': (0xB0, 0x7A, 0x22)},
        elements=pair([el((5, -2.5, 5.5), (7.5, -0.25, 5.75), _bow_wing)]) + [
            el((7.5, -1.75, 5.25), (8.5, -0.75, 5.75), _bow_knot),
        ]),
    'front_pumpkin_pendant': dict(
        density=4,
        palette={'O': (0xF0, 0x7A, 0x12), 'o': (0xFF, 0x9F, 0x3D), 'b': (0xA8, 0x4C, 0x08),
                 'Y': (0xFF, 0xD2, 0x2E), 'V': (0x2F, 0x6B, 0x1E), 'l': (0x5D, 0xBB, 0x4A)},
        elements=pair([el((7, -4.5, 5.5), (7.5, 0, 5.75), _vine_cord, rot=('z', 22.5, [7.25, -4.5, 5.6]))]) + [
            el((6.75, -7.5, 4.75), (9.25, -5.5, 5.75), _pumpkin),
            el((7.75, -5.5, 5), (8.25, -4.75, 5.5), _stem),
        ]),
}


FACES = ('north', 'south', 'west', 'east', 'up', 'down')
NORMALS = {'north': (0, 0, -1), 'south': (0, 0, 1), 'west': (-1, 0, 0), 'east': (1, 0, 0), 'up': (0, 1, 0),
           'down': (0, -1, 0)}


def face_corners(face, f, t):
    """Corners TL, TR, BR, BL of a face as its texture lies on it, per the vanilla block model default UVs (e.g. north
    u = 16 - x, v = 16 - y; up u = x, v = z): an explicit uv rect [u1, v1, u2, v2] puts (u1, v1) at TL."""
    return {
        'north': [(t[0], t[1], f[2]), (f[0], t[1], f[2]), (f[0], f[1], f[2]), (t[0], f[1], f[2])],
        'south': [(f[0], t[1], t[2]), (t[0], t[1], t[2]), (t[0], f[1], t[2]), (f[0], f[1], t[2])],
        'west': [(f[0], t[1], f[2]), (f[0], t[1], t[2]), (f[0], f[1], t[2]), (f[0], f[1], f[2])],
        'east': [(t[0], t[1], t[2]), (t[0], t[1], f[2]), (t[0], f[1], f[2]), (t[0], f[1], t[2])],
        'up': [(f[0], t[1], f[2]), (t[0], t[1], f[2]), (t[0], t[1], t[2]), (f[0], t[1], t[2])],
        'down': [(f[0], f[1], t[2]), (t[0], f[1], t[2]), (t[0], f[1], f[2]), (f[0], f[1], f[2])],
    }[face]


def face_size(face, f, t):
    dx, dy, dz = (t[i] - f[i] for i in range(3))
    return {'north': (dx, dy), 'south': (dx, dy), 'west': (dz, dy), 'east': (dz, dy), 'up': (dx, dz),
            'down': (dx, dz)}[face]


def lerp3(a, b, s):
    return tuple(a[k] + (b[k] - a[k]) * s for k in range(3))


def paint_face(e, face, density, palette):
    """The face's texels as an RGBA image (None if the face has no area or is fully transparent)."""
    fw, fh = face_size(face, e['frm'], e['to'])
    w, h = fw * density, fh * density
    if w == 0 or h == 0:
        return None
    assert w == int(w) and h == int(h), f'face {face} of {e["frm"]}..{e["to"]} is not a whole number of texels'
    w, h = int(w), int(h)
    tl, tr, br, bl = face_corners(face, e['frm'], e['to'])
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    for j in range(h):
        for i in range(w):
            p = lerp3(lerp3(tl, tr, (i + 0.5) / w), lerp3(bl, br, (i + 0.5) / w), (j + 0.5) / h)
            if e.get('mirror'):
                p = (16 - p[0], p[1], p[2])
            role = e['paint'](face, i, j, w, h, p)
            if role != '.':
                px[i, j] = palette[role] + (255,)
    return im if im.getbbox() else None


# ---------------------------------------------------------------------------------------------------------------------
# Ball skins: one 64x32-style texture per skin and Cobblemon ball geometry, laid out on that geometry's box UV (read
# from the Cobblemon jar into cosmetics/cobblemon_balls.json). Box UV per cube at (u, v), size (w, h, d): top face at
# (u + d, v), bottom face at (u + d + w, v), the four sides in one strip at v + d, front (north) at u + d.
# The ball surface is addressed as: caps (top / bottom, 8x8), the side strip (column 0..31 around, row 0..7 from top;
# rows 3 and 4 are the equator band), inner faces (seen only when the ball opens) and the small parts (button / latch,
# plates, knob, wings) of the ancient geometry.

def box_faces(u, v, w, h, d):
    """{slot: (x, y, w, h)} texture rects of a box-UV cube."""
    return {'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d), 'east': (u, v + d, d, h),
            'north': (u + d, v + d, w, h), 'west': (u + d + w, v + d, d, h), 'south': (u + 2 * d + w, v + d, w, h)}


SIDE_ORDER = ('east', 'north', 'west', 'south')


def ball_part(cube):
    w, h, d = cube['size']
    if (w, h, d) == (8, 4, 8):
        return cube['bone'] + ('_shell' if cube.get('inflate') else '')
    if d == 0 and w == 2:
        return 'button'
    if d == 0:
        return 'plate'
    if (w, h, d) == (3, 1, 3):
        return 'knob'
    if (w, h, d) == (3, 3, 3):
        return 'wing'
    raise AssertionError(f'unknown ball cube {cube}: teach art.ball_part about it')


def _hex(s):
    return hexrgb(s)


class BallSkin:
    """Colours + surface functions of one skin; subclasses override surface()."""
    band, band_low, button, button_hi, inner, inner_ring = ('#141414', '#0A0A0A', '#FFFFFF', '#FFFFFF', '#2A2A30',
                                                            '#44444C')

    def surface(self, region, a, b):
        raise NotImplementedError

    def colour(self, part, slot, x, y, w, h):
        """RGB for one texel of a cube face, or None for transparent."""
        if part == 'button':
            return _hex(self.button_hi) if (x, y) == (0, 0) else _hex(self.button)
        if part == 'knob':
            return _hex(self.button_hi) if slot == 'top' and (x, y) == (1, 1) else _hex(self.button)
        if part in ('plate', 'wing'):
            edge = 0 in (x, y) or x == w - 1 or y == h - 1
            return _hex(self.band_low) if edge else _hex(self.band)
        half, shell = part.split('_')[0], part.endswith('_shell')
        if slot in ('top', 'bottom'):
            outer = (half, slot) in (('lid', 'top'), ('bottom', 'bottom'))
            if not outer:
                if shell:
                    return None
                ring = max(abs(x - 3.5), abs(y - 3.5))
                return _hex(self.inner_ring) if 1.5 < ring < 2.5 else _hex(self.inner)
            return self.surface('cap_top' if half == 'lid' else 'cap_bottom', x, y)
        row = y if half == 'lid' else 4 + y
        col = SIDE_ORDER.index(slot) * 8 + x
        if row in (3, 4):
            if shell:
                return None  # the shell stops short of the band so it reads as an inset groove
            return _hex(self.band) if row == 3 else _hex(self.band_low)
        return self.surface('side', col, row)


class Galaxy(BallSkin):
    band, band_low, button, button_hi = '#8A4FD8', '#5B2E9E', '#E8DDFF', '#FFFFFF'

    def surface(self, region, a, b):
        n = h32(a, b, len(region))
        if n % 11 == 0:
            return _hex('#FFFFFF')
        if n % 17 == 3:
            return _hex('#B9A8FF')
        return _hex(('#140F33', '#22184F', '#22184F', '#33246E')[(n >> 8) % 4])


class Gilded(BallSkin):
    band, band_low, button, button_hi = '#E2B04A', '#B07A22', '#F7D27A', '#FFF1D0'

    def surface(self, region, a, b):
        if region == 'cap_top':
            if (a in (3, 4) and 1 <= b <= 6) or (b in (3, 4) and 1 <= a <= 6):
                return _hex('#F7D27A') if (a in (3, 4) and b in (3, 4)) else _hex('#E2B04A')  # gold sparkle
            return _hex('#2E4A8C') if (a + b) % 7 == 0 else _hex('#1B2E5B')
        if region == 'cap_bottom':
            return _hex('#EADBB5') if (a + b) % 5 == 0 else _hex('#FFF1D0')
        if b < 3:
            return _hex('#2E4A8C') if b == 0 else _hex('#1B2E5B')
        return _hex('#EADBB5') if b == 7 else _hex('#FFF1D0')


class Crystal(BallSkin):
    band, band_low, button, button_hi = '#2A6F8F', '#1D4F66', '#B3D9FF', '#FFFFFF'
    FACETS = ('#7FE3F2', '#C8F6FF', '#3FA9C9')

    def surface(self, region, a, b):
        if region == 'cap_bottom' or (region == 'side' and b > 4):
            return _hex('#D6E6F0') if (region == 'side' and b == 7) or h32(a, b) % 9 == 0 else _hex('#F4FAFF')
        facet = ((a + b) // 2 + (a - b) // 3) % 3  # diagonal facets
        if h32(a, b, 7) % 23 == 0:
            return _hex('#FFFFFF')
        return _hex(self.FACETS[facet])


def _crack_set():
    """Glowing cracks: deterministic zig-zag walks over the side strip and the caps."""
    side, caps = set(), set()
    for k, start in enumerate((2, 9, 15, 22, 28)):
        x = start
        for row in range(8):
            if row not in (3, 4):
                side.add((x % 32, row))
            x += (-1, 0, 1)[h32(k, row) % 3]
    for k, (x, y) in enumerate(((1, 1), (6, 2), (2, 6))):
        for step in range(5):
            caps.add((x, y))
            x, y = max(0, min(7, x + (-1, 0, 1)[h32(k, step, 1) % 3])), max(0, min(7, y + 1 - 2 * (k == 2)))
    return side, caps


class Ember(BallSkin):
    band, band_low, button, button_hi = '#121212', '#0A0A0A', '#FF7A2F', '#FFB347'
    SIDE, CAPS = _crack_set()

    def surface(self, region, a, b):
        cracks = self.SIDE if region == 'side' else self.CAPS
        if (a, b) in cracks:
            return _hex('#FFB347') if h32(a, b) % 3 == 0 else _hex('#FF5A1F')
        return _hex(('#242424', '#2E2B29', '#383533')[h32(a, b, 5) % 3])


class Sakura(BallSkin):
    band, band_low, button, button_hi = '#B85C84', '#8A3F60', '#FFFFFF', '#FFD1E6'

    def surface(self, region, a, b):
        if region == 'cap_bottom' or (region == 'side' and b > 4):
            return _hex('#EADBB5') if region == 'side' and b == 7 else _hex('#FFF1D0')
        # white petal marks: a 2-texel petal with a pale tip at sparse anchors
        for da, db in ((0, 0), (-1, 0), (0, -1)):
            if h32(a + da, b + db, 3) % 9 == 0:
                return _hex('#FFFFFF') if (da, db) == (0, 0) else _hex('#FFD1E6')
        return _hex('#F48FB8') if (a + 2 * b) % 9 == 0 else _hex('#F7A8C8')


class Pumpkin(BallSkin):
    band, band_low, button, button_hi = '#141414', '#0A0A0A', '#3E7A1E', '#5DBB4A'

    def surface(self, region, a, b):
        if region == 'side':
            rib = a % 4
            base = ('#C25A0A', '#F07A12', '#FF9F3D', '#F07A12') if b < 3 else ('#A84C08', '#D9680F', '#E8862E',
                                                                                 '#D9680F')
            return _hex(base[rib])
        ribs = a in (0, 7) or b in (0, 7) or a == b or a + b == 7
        if region == 'cap_top':
            return _hex('#C25A0A') if ribs else _hex('#F07A12')
        return _hex('#A84C08') if ribs else _hex('#D9680F')


BALL_SKINS_ART = {'ball_galaxy': Galaxy(), 'ball_gilded': Gilded(), 'ball_crystal': Crystal(), 'ball_ember': Ember(),
                  'ball_sakura': Sakura(), 'ball_pumpkin': Pumpkin()}


def ball_texture(skin, geometry):
    """Draw a skin on one Cobblemon ball geometry ({'texture': [w, h], 'cubes': [...]}). Face rects must not overlap."""
    tw, th = geometry['texture']
    im = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    px = im.load()
    painted = set()
    for cube in geometry['cubes']:
        part = ball_part(cube)
        w, h, d = cube['size']
        for slot, (fx, fy, fw, fh) in box_faces(*cube['uv'], w, h, d).items():
            if fw == 0 or fh == 0:
                continue
            for y in range(fh):
                for x in range(fw):
                    assert (fx + x, fy + y) not in painted, f'ball UV overlap at {(fx + x, fy + y)}'
                    painted.add((fx + x, fy + y))
                    c = skin.colour(part, slot, x, y, fw, fh)
                    if c is not None:
                        px[fx + x, fy + y] = c + (255,)
    return im


if __name__ == '__main__':
    # self-check: particle templates are rectangular, sprites are binary alpha and deterministic
    a, b = sprite(STAR, shades('#E2B04A')), sprite(STAR, shades('#E2B04A'))
    assert a.tobytes() == b.tobytes()
    assert set(a.getchannel('A').tobytes()) <= {0, 255}
    print('art ok')


if __name__ != '__main__':  # the drop 2 art imports this module's helpers, so it is merged in last
    from cosmetics.art_drop2 import BALL_SKINS_ART2, FRONTS2, WEARABLES2  # noqa: E402

    WEARABLES.update(WEARABLES2)
    FRONTS.update(FRONTS2)
    BALL_SKINS_ART.update(BALL_SKINS_ART2)
