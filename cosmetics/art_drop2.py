"""Cosmetics drop 2 art (catalog-v2.md): 12 hats and 6 back items (WEARABLES2), 6 front items (FRONTS2) and 10 Poke Ball
skins (BALL_SKINS_ART2), drawn in code with the helpers of cosmetics/art.py. art.py merges these dicts into its own at
the end of the module. Same rules as art.py: model space in pixels (see the contract note above WEARABLES there), no
randomness, every colour original. No logos or text anywhere: the capsule items are plain red / white ball looks.
"""
import colorsys
import math

from cosmetics.art import CREAM, GOLD, LIGHT_GOLD, BallSkin, bevel, el, h32, hexrgb, pair

DARK_GOLD = (0xB0, 0x7A, 0x22)
WHITE = (0xFF, 0xFF, 0xFF)


def stack(y, rows, paint, cx=8, cz=8, rot=None, skip=()):
    """Cubes stacked upward from y, centred on (cx, cz): rows = [(width, height[, depth])]; paint(k) paints row k."""
    out = []
    for k, r in enumerate(rows):
        w, h = r[0], r[1]
        d = r[2] if len(r) > 2 else w
        out.append(el((cx - w / 2, y, cz - d / 2), (cx + w / 2, y + h, cz + d / 2), paint(k), rot=rot, skip=skip))
        y += h
    return out


def silhouette(inside, x0, x1, y0, y1, z0, z1, paint, step=0.5, skip=('south',)):
    """A flat shape as rows of cubes: inside(x, y) is tested at each step-sized cell centre of the box x0..x1, y0..y1."""
    out, n, y = [], int(round((x1 - x0) / step)), y0
    while y < y1 - 1e-9:
        run = None
        for k in range(n + 1):
            on = k < n and inside(x0 + (k + 0.5) * step, y + step / 2)
            if on and run is None:
                run = x0 + k * step
            elif not on and run is not None:
                out.append(el((run, y, z0), (x0 + k * step, y + step, z1), paint, skip=skip))
                run = None
        y += step
    return out


def inside_poly(x, y, pts):
    ins = False
    for k in range(len(pts)):
        (ax, ay), (bx, by) = pts[k], pts[k - 1]
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
            ins = not ins
    return ins


def seg_dist(x, y, a, b):
    (ax, ay), (bx, by) = a, b
    t = max(0, min(1, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
    return math.hypot(x - ax - t * (bx - ax), y - ay - t * (by - ay))


def _fuzz(base, shade, light):
    """Speckled fluff (pom-poms)."""
    def paint(face, i, j, w, h, p):
        n = h32(i, j, sum(map(ord, face)))
        return light if n % 7 == 0 else shade if n % 3 == 0 else base
    return paint


def _template(rows, roles):
    """Painter for the north face from an ASCII template seen from the front; other faces take roles['*']."""
    def paint(face, i, j, w, h, p):
        if face != 'north':
            return roles['*']
        ch = rows[j][i]
        return roles[ch]
    return paint


def _box(m, light, dark, top=None, bottom=None):
    return bevel(m=m, light=light, dark=dark, top=top, bottom=bottom)


# ---------------------------------------------------------------------------------------------------------------------
# Hats (head bone: head cube x 4..12, y 0..8, z 4..12, skin overlay reaches 0.5 further)

def _party_row(k):
    m, d = ('P', 'p') if k % 2 == 0 else ('B', 'b')

    def paint(face, i, j, w, h, p):
        if face == 'up':
            return m
        if face == 'down':
            return d
        if face in ('north', 'west') and h32(i, j, k, len(face)) % 13 == 0:
            return 'W'  # confetti dots
        return d if face in ('east', 'south') else m
    return paint


PARTY_TILT = ('z', 22.5, [8, 14.5, 8])


def _wedges(face, i, j, w, h, p):
    """Beanie panels: six wedges around the crown in red, yellow and blue."""
    c = 'RYB'[int((math.atan2(p[2] - 8, p[0] - 8) + math.pi) / (math.pi / 3)) % 3]
    return c.lower() if face == 'down' or (face != 'up' and j == h - 1) else c


def _blade(tip):
    return lambda face, i, j, w, h, p: tip if max(abs(p[0] - 8), abs(p[2] - 8)) > 2.5 else ('y' if face == 'down' else 'Y')


def _cowboy_brim(face, i, j, w, h, p):
    if face == 'up':
        if min(i, j, w - 1 - i, h - 1 - j) == 1:
            return 'D'  # stitched edge
        return 'L' if 0 in (i, j) or i == w - 1 or j == h - 1 else 'M'
    return 'O'


def _cowboy_crown(face, i, j, w, h, p):
    if face == 'up':
        return 'D' if abs(p[0] - 8) < 0.5 else 'L'  # the crease along the top
    if face == 'down':
        return 'O'
    return 'L' if j == 0 else 'M'


def _puff(face, i, j, w, h, p):
    if face == 'up':
        return 'w' if (i + j) % 5 == 0 else 'W'
    if face == 'down':
        return 'g'
    if j == h - 1:
        return 'g'
    return 'w' if int(math.floor((p[0] + p[2]) * 2)) % 4 == 0 else 'W'  # pleats


def _chef_band(face, i, j, w, h, p):
    if face == 'up':
        return 'W'
    if face == 'down':
        return 'g'
    return 'd' if int(math.floor((p[0] + p[2]) * 2)) % 4 == 0 else ('g' if j == h - 1 else 'w')


def _horn(k):
    def paint(face, i, j, w, h, p):
        if face == 'up':
            return 'C'
        if face == 'down':
            return 'c'
        if k == 3:
            return 'T' if face != 'north' or j % 2 else 't'
        return 'c' if int(math.floor(p[0] * 2)) % 4 == 0 else 'C'  # growth rings
    return paint


def _horn_chain():
    """Four tapering segments, each turned a bit further up (0, 22.5, 45, 45 degrees) about the previous one's end."""
    out, x, y = [], 13, 8
    for k, (length, thick, ang) in enumerate(((1.5, 3, 0), (2, 2.5, 22.5), (2.5, 2, 45), (2, 1.5, 45))):
        out.append(el((x - 0.5, y - thick / 2, 8 - thick / 2), (x + length, y + thick / 2, 8 + thick / 2), _horn(k),
                      rot=('z', ang, [x, y, 8])))
        x += length * math.cos(math.radians(ang))
        y += length * math.sin(math.radians(ang))
        x, y = round(x * 4) / 4, round(y * 4) / 4
    return out


def _star_at(i, j, k):
    """A tiny plus-shaped star in a 5x3-texel cell (one cell in three has one)."""
    ci, cj = i // 5, j // 3
    if h32(ci, cj, k) % 3:
        return None
    d = abs(i - (ci * 5 + 2)) + abs(j - (cj * 3 + 1))
    return 'g' if d == 0 else 'G' if d == 1 else None


def _wiz(k):
    def paint(face, i, j, w, h, p):
        if face == 'up':
            return 'n'
        if face == 'down':
            return 'k'
        return _star_at(i, j, k) or ('n' if j == 0 else 'k' if j == h - 1 else 'N')
    return paint


def _wiz_brim(face, i, j, w, h, p):
    rim = max(abs(p[0] - 8), abs(p[2] - 8)) > 6.0
    if face == 'up':
        if rim:
            return 'G'
        return _star_at(i, j, 9) or 'n'
    return 'G' if rim and face != 'down' else ('k' if face == 'down' else 'N')


def _skull_patch():
    rows = [['D'] * 24 for _ in range(12)]
    for k in range(22):  # two crossed bones, 2 texels thick
        for x, y in ((1 + k, 1 + k * 9 // 21), (22 - k, 1 + k * 9 // 21)):
            for dx in (0, 1):
                rows[y][min(23, x + dx)] = 'W'
    for x, y in ((0, 0), (1, 0), (0, 1), (22, 0), (23, 0), (23, 1), (0, 10), (1, 10), (0, 11), (1, 11), (22, 10),
                 (23, 10), (22, 11), (23, 11)):
        rows[y][x] = 'W'  # bone knobs
    skull = ["..WWWWWW..", ".WWWWWWWW.", "WWWWWWWWWW", "WWKKWWKKWW", "WWKKWWKKWW", "WWWWKKWWWW", ".WWWWWWWW.",
             "..WKWWKW..", "..WWWWWW.."]
    for j, row in enumerate(skull):
        for i, ch in enumerate(row):
            if ch != '.':
                rows[1 + j][7 + i] = ch
    rows = [''.join(r) for r in rows]

    def paint(face, i, j, w, h, p):
        if face != 'north':
            return 'D'
        if 0 in (i, j) or i == w - 1 or j == h - 1:
            return 'G'
        return 'Z' if rows[j][i] == 'K' else 'w' if rows[j][i] == 'W' else 'D'
    return paint


def _flap(face, i, j, w, h, p):
    if face == 'up':
        return 'G'
    return 'G' if j == 0 else 'L' if i == 0 else 'M'


def _tricorn_brim(face, i, j, w, h, p):
    if face == 'up':
        return 'G' if 0 in (i, j) or i == w - 1 or j == h - 1 else 'M'
    return 'O' if face != 'down' else 'D'


def _ear_white(inner_from):
    def paint(face, i, j, w, h, p):
        if face == 'north':
            if 0 < i < w - 1 and j >= inner_from:
                return 'P' if j % 4 else 'p'
            return 'W'
        return 'w' if face in ('east', 'south', 'down') else 'W'
    return paint


def _cat_ear(face, i, j, w, h, p):
    if face == 'north' and 0 < i < w - 1 and j >= 1:
        return 'P'
    return 'L' if face == 'up' else 'M'


def _cone(k, white):
    m, l, d = ('W', 'W', 'w') if white else ('O', 'L', 'D')

    def paint(face, i, j, w, h, p):
        if face == 'up':
            return l
        if face == 'down':
            return d
        return d if face in ('east', 'south') else m
    return paint


def _knit(fold):
    def paint(face, i, j, w, h, p):
        rib = (int(math.floor(p[0] * 2)) + int(math.floor(p[2] * 2))) % 2
        if face == 'up':
            return 'T' if (i + j) % 2 else 'L'
        if face == 'down':
            return 't'
        if fold:
            return 'L' if j == 0 else ('t' if j == h - 1 else ('T' if rib else 'L'))
        return 'T' if (rib + j) % 2 else 't'
    return paint


def _helmet_red(k):
    def paint(face, i, j, w, h, p):
        if face == 'up':
            return 'R'
        if face == 'down':
            return 'r'
        return 'r' if face in ('east', 'south') else 'q' if face == 'west' and j == 0 else 'R'
    return paint


def _helmet_white(face, i, j, w, h, p):
    if face == 'up':
        return 'W'
    if face == 'down':
        return 'g'
    return 'g' if j == h - 1 or face in ('east', 'south') else 'W'


def _button(ring, fill, inner):
    def paint(face, i, j, w, h, p):
        if face != 'north':
            return ring
        if 0 in (i, j) or i == w - 1 or j == h - 1:
            return ring
        return fill if 1 < i < w - 2 and 1 < j < h - 2 else inner
    return paint


# the wizard's cone bends forward twice; the second pivot is the top centre of the first bent part after its rotation
_JY = 15 + 3 * math.cos(math.radians(22.5))
_JZ = 8 - 3 * math.sin(math.radians(22.5))
JY, JZ = round(_JY * 4) / 4, round(_JZ * 4) / 4

BUNNY_ROT = ('z', -22.5, [10, 8.5, 7.25])

HATS2 = {
    'hat_party_hat': dict(
        palette={'P': (0xFF, 0x7E, 0xB6), 'p': (0xD1, 0x4A, 0x86), 'B': (0x4F, 0xA3, 0xFF), 'b': (0x2C, 0x70, 0xC6),
                 'W': WHITE, 'Y': (0xFF, 0xE0, 0x66), 'y': (0xC9, 0x9A, 0x12)},
        elements=stack(8.5, [(8, 1.5), (7, 1.5), (6, 1.5), (5, 1.5)], _party_row)
        + stack(14.5, [(4, 1.5), (3, 1.5), (2, 1.5), (1, 1.5)], lambda k: _party_row(k + 4), rot=PARTY_TILT)
        + [el((7, 19.5, 7), (9, 21.5, 9), _fuzz('Y', 'y', 'W'), rot=PARTY_TILT)]),
    'hat_propeller_cap': dict(
        palette={'R': (0xE3, 0x41, 0x2F), 'r': (0xA3, 0x20, 0x14), 'Y': (0xFF, 0xD2, 0x2E), 'y': (0xC9, 0x9A, 0x12),
                 'B': (0x3F, 0x8C, 0xFF), 'b': (0x24, 0x58, 0xB8), 'K': (0x26, 0x26, 0x30), 'S': (0xB8, 0xC0, 0xCC)},
        elements=stack(6.5, [(10, 2.5), (8, 1.5), (5, 1)], lambda k: _wedges) + [
            el((7, 11.5, 7), (9, 12, 9), bevel(m='Y', light='Y', dark='y')),
            el((7.75, 12, 7.75), (8.25, 13.5, 8.25), bevel(m='S', light='S', dark='K')),
            el((3, 13.5, 7.5), (13, 14, 8.5), _blade('R'), rot=('y', 45, [8, 13.5, 8])),
            el((7.5, 14, 3), (8.5, 14.5, 13), _blade('B'), rot=('y', 45, [8, 13.5, 8])),
            el((7.5, 14.5, 7.5), (8.5, 15, 8.5), bevel(m='K', light='S', dark='K')),
        ]),
    'hat_cowboy': dict(
        palette={'O': (0x3E, 0x24, 0x10), 'D': (0x5E, 0x3A, 0x1B), 'M': (0x8A, 0x5A, 0x2B), 'L': (0xA8, 0x72, 0x3A),
                 'k': (0x2A, 0x1A, 0x10), 'K': (0x3D, 0x27, 0x17), 'G': GOLD, 'g': LIGHT_GOLD, 'd': DARK_GOLD},
        elements=[el((3, 8.5, 1), (13, 9, 15), _cowboy_brim)]
        + pair([el((13, 8.5, 1.5), (16, 9, 14.5), _cowboy_brim, rot=('z', 22.5, [13, 8.75, 8]))])
        + [el((4.5, 9, 4.5), (11.5, 11, 11.5), bevel(m='M', light='L', dark='D')),
           el((4.75, 11, 4.75), (11.25, 12.5, 11.25), bevel(m='M', light='L', dark='D')),
           el((5, 12.5, 5), (11, 13.5, 11), _cowboy_crown),
           el((4.25, 9.5, 4.25), (11.75, 10.5, 11.75), bevel(m='k', light='K', dark='k'), skip=('up', 'down')),
           el((7, 9.5, 3.75), (9, 10.5, 4.25), bevel(m='G', light='g', dark='d', top='g'))]),
    'hat_chef': dict(
        palette={'W': WHITE, 'w': (0xEC, 0xF0, 0xF6), 'g': (0xC9, 0xD3, 0xDE), 'd': (0xB0, 0xBC, 0xCC)},
        elements=[el((4, 8.5, 4), (12, 10.5, 12), _chef_band), el((3, 10.5, 3), (13, 13, 13), _puff),
                  el((3.5, 13, 3.5), (12.5, 15.5, 12.5), _puff), el((4.5, 15.5, 4.5), (11.5, 16.5, 11.5), _puff)]),
    'hat_viking': dict(
        palette={'O': (0x2B, 0x2E, 0x36), 'D': (0x4A, 0x50, 0x5C), 'M': (0x7B, 0x84, 0x92), 'L': (0xA9, 0xB3, 0xC2),
                 'W': (0xDD, 0xE5, 0xEE), 'C': (0xF1, 0xE4, 0xC4), 'c': (0xCF, 0xBB, 0x8F), 'T': (0xA8, 0x93, 0x66),
                 't': (0x7A, 0x66, 0x3E)},
        elements=stack(6.5, [(10, 2.5), (9, 1), (8, 1), (6, 1), (4, 0.5)], lambda k: _box('M', 'L', 'D', top='L', bottom='O'))
        + [el((2.75, 6.5, 2.75), (13.25, 7.5, 13.25), _box('D', 'M', 'O', top='M', bottom='O')),
           el((7.5, 11.5, 4.5), (8.5, 12.5, 11.5), _box('L', 'W', 'M', top='W')),
           el((7.5, 2.5, 3), (8.5, 6.5, 3.5), _box('M', 'L', 'D'), skip=('south',)),
           el((12.5, 6.5, 6.5), (13.5, 9.5, 9.5), _box('D', 'M', 'O'))]
        + pair(_horn_chain())),
    'hat_wizard': dict(
        palette={'N': (0x1F, 0x2E, 0x6B), 'n': (0x37, 0x4C, 0x9C), 'k': (0x12, 0x1B, 0x42), 'G': GOLD,
                 'g': LIGHT_GOLD},
        elements=[el((1.5, 8.5, 3.5), (14.5, 9, 12.5), _wiz_brim), el((3.5, 8.5, 1.5), (12.5, 9, 3.5), _wiz_brim),
                  el((3.5, 8.5, 12.5), (12.5, 9, 14.5), _wiz_brim)]
        + stack(9, [(8, 1.5), (7, 1.5), (6, 1.5), (5, 1.5)], _wiz)
        + stack(15, [(4, 1.5), (3, 1.5)], lambda k: _wiz(k + 4), rot=('x', -22.5, [8, 15, 8]))
        + stack(JY, [(2, 1.5), (1, 1.5)], lambda k: _wiz(k + 6), cz=JZ, rot=('x', -45, [8, JY, JZ]))),
    'hat_pirate': dict(
        density=4,
        palette={'M': (0x22, 0x22, 0x2B), 'L': (0x3A, 0x3A, 0x46), 'O': (0x0C, 0x0C, 0x10), 'D': (0x15, 0x15, 0x1B),
                 'G': GOLD, 'w': (0xF2, 0xF4, 0xF8), 'Z': (0x08, 0x08, 0x0A)},
        elements=[el((3.75, 8.5, 3.75), (12.25, 12, 12.25), bevel(m='M', light='L', dark='D', top='L')),
                  el((5, 8.75, 3.5), (11, 11.75, 3.75), _skull_patch()),
                  el((3, 8.5, 1.5), (13, 9, 3.75), _tricorn_brim)]
        # the other three brim corners folded up against the crown: two side plates and a back plate, flaring outward
        + pair([el((12.25, 8.5, 3.75), (13.25, 12.5, 12.25), _flap, rot=('z', 22.5, [12.25, 8.5, 8]))])
        + [el((3.75, 8.5, 12.25), (12.25, 12.5, 13.25), _flap, rot=('x', -22.5, [8, 8.5, 12.25]))]),
    'hat_bunny_ears': dict(
        palette={'W': WHITE, 'w': (0xE8, 0xEE, 0xF4), 'P': (0xFF, 0xA8, 0xC8), 'p': (0xE0, 0x7A, 0xA3)},
        elements=pair([el((9, 8.5, 6.5), (11, 13.5, 8), _ear_white(1), rot=BUNNY_ROT),
                       el((9.25, 13.5, 6.75), (10.75, 15.5, 7.75), _ear_white(1), rot=BUNNY_ROT)])),
    'hat_cat_ears': dict(
        density=4,
        palette={'M': (0x1C, 0x1C, 0x24), 'L': (0x38, 0x38, 0x46), 'P': (0xFF, 0x9F, 0xBF)},
        elements=pair(stack(8.5, [(4, 1.25, 2.5), (3, 1.25, 2.5), (2, 1.25, 2.5), (1, 1.25, 2.5)],
                            lambda k: _cat_ear, cx=10.25, cz=5.75))),
    'hat_traffic_cone': dict(
        palette={'O': (0xFF, 0x7A, 0x1A), 'L': (0xFF, 0xA3, 0x4D), 'D': (0xC2, 0x55, 0x08), 'W': WHITE,
                 'w': (0xD6, 0xDC, 0xE4)},
        elements=[el((3, 8.5, 3), (13, 9.5, 13), bevel(m='D', light='O', dark='D', top='O'))]
        + stack(9.5, [(7, 1), (6, 1), (6, 1), (5, 1), (5, 1), (4, 1), (3, 1), (3, 1)],
                lambda k: _cone(k, k in (2, 3, 5)))),
    'hat_beanie': dict(
        palette={'T': (0x1F, 0xA3, 0xA8), 't': (0x14, 0x7A, 0x80), 'L': (0x4F, 0xC9, 0xCC), 'W': WHITE,
                 'w': (0xE8, 0xEE, 0xF4), 'g': (0xC9, 0xD3, 0xDE)},
        elements=[el((3, 6.5, 3), (13, 9, 13), _knit(True)), el((3.5, 9, 3.5), (12.5, 11, 12.5), _knit(False)),
                  el((4.5, 11, 4.5), (11.5, 12, 11.5), _knit(False)),
                  el((6.5, 12, 6.5), (9.5, 15, 9.5), _fuzz('W', 'w', 'g'))]),
    'hat_capsule_helmet': dict(
        palette={'R': (0xE3, 0x41, 0x2F), 'r': (0xA3, 0x20, 0x14), 'q': (0xFF, 0x7A, 0x66), 'W': WHITE,
                 'g': (0xD6, 0xDC, 0xE4), 'K': (0x1A, 0x1A, 0x1E), 'k': (0x0A, 0x0A, 0x0C)},
        elements=stack(7, [(10, 2), (9, 1.5), (7, 1), (5, 1)], _helmet_red)
        + [el((2.75, 6, 2.75), (13.25, 7, 13.25), bevel(m='K', light='K', dark='k', top='K')),
           el((7, 5.5, 2.25), (9, 7.5, 2.75), _button('K', 'W', 'g')),
           el((3, 1, 10.5), (13, 6, 13), _helmet_white)]
        + pair([el((11, 1, 3), (13, 6, 10.5), _helmet_white)])),
}


# ---------------------------------------------------------------------------------------------------------------------
# Back items (body bone: torso x 4..12, y -12..0, z 6..10; skin overlay reaches 10.25)

ANGEL_ROT = ('y', -22.5, [8.5, -3, 10.5])
DRAGON_ROT = ('y', -22.5, [9, -3, 10.5])


def _angel(face, i, j, w, h, p):
    u, y = p[0] - 8.5, p[1]
    if face not in ('north', 'south') or not 0 <= u <= 10:
        return '.'
    lead = 1.5 + 3.2 * math.sin(min(u, 5) / 5 * math.pi / 2) - (max(u - 5, 0) / 5) ** 1.5 * 13.7
    f = (u / 1.25) % 1
    base = -3.5 - 5.5 * u / 10
    low = base - 1.6 * (1 - (2 * f - 1) ** 2)
    if y > lead or y < low:
        return '.'
    if y > lead - 0.55:
        return 'g'
    if y < low + 0.55:
        return 'G'
    if y < low + 1.3:
        return 'Y'
    if y > base + 3.5:
        return 'w' if (int(math.floor(u * 1.6)) + int(math.floor(y * 1.6))) % 2 else 'W'  # coverts, scale rows
    return 'g' if f < 0.1 else ('w' if f > 0.55 else 'W')


_DRAGON_TIPS = [(10, 2.0), (9.5, -3.5), (6.5, -9.0), (3.0, -10.0)]
_DRAGON_WRIST = (3.5, 4.0)


def _dragon_outline():
    wx, wy = _DRAGON_WRIST
    pts = [(0, 0), (wx, wy), _DRAGON_TIPS[0]]
    seq = _DRAGON_TIPS + [(0, -7)]
    for (ax, ay), (bx, by) in zip(seq, seq[1:]):
        mx, my = (ax + bx) / 2, (ay + by) / 2
        d = math.hypot(mx - wx, my - wy)
        pts += [(mx - (mx - wx) / d * 1.7, my - (my - wy) / d * 1.7), (bx, by)]
    return pts


_DRAGON_POLY = _dragon_outline()
_DRAGON_BONES = [((0, 0), _DRAGON_WRIST, 0.65)] + [(_DRAGON_WRIST, t, 0.45) for t in _DRAGON_TIPS]


def _dragon(face, i, j, w, h, p):
    u, y = p[0] - 9, p[1]
    if face not in ('north', 'south'):
        return '.'
    if not inside_poly(u, y, _DRAGON_POLY):
        return '.'
    if any(seg_dist(u, y, a, b) < r for a, b, r in _DRAGON_BONES):
        return 'O'
    if any(not inside_poly(u + dx, y + dy, _DRAGON_POLY) for dx, dy in ((0.6, 0), (-0.6, 0), (0, 0.6), (0, -0.6))):
        return 'D'
    near = min(seg_dist(u, y, a, b) for a, b, _ in _DRAGON_BONES)
    return 'H' if near < 1.1 and (int(math.floor(u * 2)) + int(math.floor(y * 2))) % 2 == 0 else (
        'L' if near < 1.6 else 'M')


def _canister(face, i, j, w, h, p):
    if face == 'up':
        return 'L'
    if face == 'down':
        return 'D'
    y = p[1]
    if -5.5 <= y < -4.0:
        return 'r' if y < -5.0 else 'R'  # red stripe
    if -8.5 < y <= -8.0 or -2.0 < y <= -1.5:
        return 'O'  # seams between the rings
    if face in ('east', 'west'):
        return 'D'
    u = (p[0] - 8.5) / 3 if p[0] > 8 else (p[0] - 4.5) / 3
    return 'D' if u < 0.2 else 'W' if 0.45 < u < 0.6 else 'L' if u < 0.75 else 'M' if u < 0.9 else 'D'


def _nozzle(face, i, j, w, h, p):
    if face == 'up':
        return 'b'
    if face == 'down':
        return 'n'  # the glowing mouth
    return 'n' if j == h - 1 else 'N' if j > 0 else 'b'


# Acoustic guitar, drawn upright before GUITAR_ROT: neck up along x = 8, soundboard = the south face at z = GTR_TOP.
# The body is 0.5-tall rows whose widths trace two bouts (lower wide, upper narrower, a waist between); every
# soundboard detail (binding, amber edge, rosette, grain) is painted from the texel's model position, so the rows
# read as one surface. The strap crosses the back the other way, from behind the left shoulder to the right side.
GTR_BOUTS = ((-10.9, 3.75, 2.6), (-7.6, 3.0, 1.8))  # (centre y, half width, half height) of the lower / upper bout
GTR_Y0, GTR_Y1, GTR_TOP = -13.5, -6.0, 12.5
GTR_HOLE = -8.4  # sound hole centre y (x = 8)


def _gtr_half(y):
    """Body half width at height y, snapped down to the 0.25 px texel grid (density 4)."""
    hw = max(a * math.sqrt(1 - ((y - c) / b) ** 2) if abs(y - c) < b else 0 for c, a, b in GTR_BOUTS)
    return math.floor(hw * 4) / 4


GTR_ROWS = [_gtr_half(GTR_Y0 + 0.5 * k + 0.25) for k in range(int((GTR_Y1 - GTR_Y0) / 0.5))]


def _gtr_in(x, y):
    return GTR_Y0 <= y < GTR_Y1 and abs(x - 8) < GTR_ROWS[int((y - GTR_Y0) // 0.5)]


def _gtr_edge(x, y, r):
    return any(not _gtr_in(x + dx, y + dy) for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)))


def _gtr_body(face, i, j, w, h, p):
    x, y, z = p
    if face == 'north':
        return 'k'  # back wood
    if face != 'south':
        return 'B' if z > GTR_TOP - 0.25 else 'S'  # sides, binding along the soundboard edge
    if _gtr_edge(x, y, 0.25):
        return 'B'
    d = math.hypot(x - 8, y - GTR_HOLE)
    if d < 1.0:
        return 'O'
    if d < 1.25:
        return 'R'  # rosette
    if d < 1.5:
        return 'r'
    if _gtr_edge(x, y, 0.5):
        return 'E'  # amber shading just inside the binding
    return 'G' if h32(int((x - 4) * 4), 7) % 7 == 0 else 'T'  # a few grain lines


def _gtr_neck(face, i, j, w, h, p):
    x, y, z = p
    if face == 'south':
        if y > -1.25:
            return 'W'  # nut
        k = (-1.25 - y) / 0.75  # a fret every 3 texels below the nut
        if 0 < i < w - 1 and k % 1 > 2 / 3 and y > -6:
            return 'f'
        if i in (2, 3) and int(k) in (2, 4) and 1 / 3 < k % 1 < 2 / 3:
            return 'W'  # dot inlays
        return 'F'
    if face in ('east', 'west'):
        return 'F' if z > 12.75 else 'N'
    return 'N'


def _gtr_head(face, i, j, w, h, p):
    if face == 'south':
        return 'N' if i in (0, w - 1) or j == 0 else 'F'
    return 'N'


def _gtr_bridge(face, i, j, w, h, p):
    if face == 'south' and 1 < i < w - 2:
        return 'W' if j == 0 else ('w' if j == 2 and i % 2 else 'D')  # saddle, bridge pins
    return 'D'


def _gtr_strap(face, i, j, w, h, p):
    if face != 'south':
        return 'x'
    if i in (0, w - 1):
        return 'x'
    return 'Y' if i == 1 and j % 3 == 0 else 'X'  # stitching


def _sheath(face, i, j, w, h, p):
    y = p[1]
    if -9.7 < y < -9.2 or -7.7 < y < -7.2:
        return 'g'  # gold bands
    if face in ('north', 'south'):
        if i in (0, w - 1):
            return 'D'
        return 'S' if i == 1 and j % 3 == 0 else ('N' if i < w // 2 else 'M')  # stitching
    return 'D'


def _grip(face, i, j, w, h, p):
    return 'k' if j % 2 else 'B'


def _solid_o(face, i, j, w, h, p):
    return 'O'


GUITAR_ROT = ('z', -45, [8, -6, 11])  # neck over the wearer's right shoulder
SWORD_ROT = ('z', -45, [8, -5, 11])  # hilt over the right shoulder


# Capsule pack: a slim pill-shaped shell hugging the back, drawn in three stacked layers (each inset a little more, so
# the edge steps down like a rounded bevel); every layer is 0.25-tall rows whose widths trace a rounded rectangle, rows
# of equal width merged. Red top half, white bottom half, a dark seam band and a raised button; every texel is painted
# from its model position, so the rows read as one surface.
CAP_X, CAP_Y = 8, -6.5  # centre of the back face
CAP_HW, CAP_HH, CAP_R = 3.0, 4.0, 2.5  # half width, half height, corner radius of the outer layer
CAP_LAYERS = ((0, 10.25, 11.5), (0.25, 11.5, 12.25), (0.75, 12.25, 12.75))  # (inset, z from, z to)
CAP_TOP = CAP_LAYERS[-1][2]


def _cap_half(y, inset):
    """Half width of the inset rounded rectangle at height y, snapped down to the 0.25 px texel grid."""
    hw, hh, r = CAP_HW - inset, CAP_HH - inset, CAP_R - inset
    dy = abs(y - CAP_Y)
    if dy >= hh:
        return 0
    over = dy - (hh - r)
    if over > 0:
        hw -= r - math.sqrt(r * r - over * over)
    return math.floor(hw * 4) / 4


def _cap_rows(half, y0, y1, z0, z1, paint):
    """Rows of cubes 0.25 tall from y0 to y1, x = CAP_X +- half(y), equal rows merged; hidden faces skipped."""
    runs = []
    for k in range(round((y1 - y0) * 4)):
        hw = half(y0 + 0.25 * k + 0.125)
        if runs and runs[-1][2] == hw:
            runs[-1][1] += 0.25
        elif hw:
            runs.append([y0 + 0.25 * k, y0 + 0.25 * k + 0.25, hw])
    out = []
    for n, (a, b, hw) in enumerate(runs):
        skip = {'north'}
        if n + 1 < len(runs) and runs[n + 1][2] >= hw and runs[n + 1][0] == b:
            skip.add('up')
        if n and runs[n - 1][2] >= hw and runs[n - 1][1] == a:
            skip.add('down')
        out.append(el((CAP_X - hw, a, z0), (CAP_X + hw, b, z1), paint, skip=skip))
    return out


def _cap(face, i, j, w, h, p):
    x, y, z = p
    dy = y - CAP_Y
    ring = math.hypot(x - CAP_X, dy) < 1.3
    if abs(dy) < 0.5:
        return 'k' if face == 'south' and dy > 0.25 and not ring else 'K'  # seam band, lit along its top edge
    if face == 'south' and ring:
        return 'K'  # the dark ring round the button
    if dy > 0:
        if face == 'down':
            return 'r'
        if face == 'south' and z > CAP_TOP - 0.1 and (abs(x - 6.5) < 0.25 and abs(y + 4.0) < 0.5 or
                                                      abs(x - 6.75) < 0.5 and abs(y + 3.75) < 0.25):
            return 'q'  # glint on the dome
        return 'R'
    if face == 'down':
        return 'g'
    return 'g' if face == 'south' and dy < -3.0 else 'W'  # the white rounds off underneath


def _cap_button(face, i, j, w, h, p):
    x, y, z = p
    d = math.hypot(x - CAP_X, y - CAP_Y)
    if face != 'south' or d > 0.55:  # a 4 x 4 texel face in a round dark rim
        return 'K'
    return 'g' if x - CAP_X + CAP_Y - y > 0.45 else 'W'


def _cap_strap(face, i, j, w, h, p):
    return 'X' if face == 'south' and 0 < i < w - 1 else 'x'


def _cap_handle(face, i, j, w, h, p):
    return 'X' if face == 'up' else 'x'


BACKS2 = {
    'back_angel_wings': dict(
        palette={'W': WHITE, 'w': (0xE8, 0xEE, 0xF4), 'g': (0xC9, 0xD3, 0xDE), 'G': GOLD, 'Y': LIGHT_GOLD},
        elements=pair([el((8.5, -11, 10.5), (18.5, 4.5, 11), _angel, rot=ANGEL_ROT)])),
    'back_dragon_wings': dict(
        palette={'O': (0x1A, 0x0A, 0x0C), 'D': (0x5A, 0x0E, 0x14), 'M': (0x9A, 0x1C, 0x22), 'L': (0xB8, 0x2C, 0x2E),
                 'H': (0xD4, 0x4A, 0x3E)},
        elements=pair([el((9, -10.5, 10.5), (19.5, 5, 11), _dragon, rot=DRAGON_ROT),
                       el((12, 4, 10.5), (13, 6.5, 11), _solid_o, rot=DRAGON_ROT)])),
    'back_jetpack': dict(
        palette={'M': (0x8A, 0x92, 0xA0), 'L': (0xB8, 0xC0, 0xCC), 'W': (0xE8, 0xEE, 0xF4), 'D': (0x5A, 0x61, 0x70),
                 'O': (0x30, 0x34, 0x40), 'R': (0xD0, 0x2E, 0x2E), 'r': (0x8A, 0x16, 0x1A), 'N': (0xFF, 0x8A, 0x1F),
                 'n': (0xFF, 0xD0, 0x7A), 'b': (0xC2, 0x5A, 0x0A)},
        elements=pair([el((8.5, -9, 10.5), (11.5, -1, 13.5), _canister),
                       el((8.75, -1, 10.75), (11.25, -0.5, 13.25), _box('L', 'W', 'D', top='W')),
                       el((9, -10.5, 11), (11, -9, 13), _nozzle),
                       el((8.75, -9.5, 10.75), (11.25, -9, 13.25), _box('O', 'O', 'O'))])
        + [el((7.5, -7.5, 10.5), (8.5, -2.5, 12), _box('D', 'M', 'O'))]),
    'back_guitar': dict(
        density=4,
        palette={'T': (0xDE, 0x9E, 0x52), 'G': (0xCE, 0x8C, 0x44), 'E': (0xB0, 0x6A, 0x2C), 'B': (0x4A, 0x28, 0x12),
                 'S': (0x8C, 0x4E, 0x22), 'k': (0x74, 0x40, 0x1C), 'O': (0x1C, 0x10, 0x08), 'R': (0xF2, 0xDC, 0xA8),
                 'r': (0x6A, 0x3A, 0x18), 'D': (0x3A, 0x20, 0x10), 'W': (0xFF, 0xF1, 0xD0), 'w': (0xD6, 0xD8, 0xDC),
                 'F': (0x34, 0x20, 0x12), 'f': (0xB8, 0xA8, 0x8C), 'N': (0x6E, 0x3C, 0x1A), 'P': (0xC9, 0xD3, 0xDE),
                 'p': (0xF0, 0xF4, 0xF8), 'X': (0x2A, 0x2A, 0x30), 'x': (0x16, 0x16, 0x1A), 'Y': GOLD},
        elements=[el((8 - hw, GTR_Y0 + 0.5 * k, 10.5), (8 + hw, GTR_Y0 + 0.5 * k + 0.5, GTR_TOP), _gtr_body,
                     rot=GUITAR_ROT) for k, hw in enumerate(GTR_ROWS) if hw]
        + [el((7.25, -6.75, 11.5), (8.75, -1, 13), _gtr_neck, rot=GUITAR_ROT),
           el((6.75, -1, 11.5), (9.25, 1, 12.5), _gtr_head, rot=GUITAR_ROT),
           el((6.5, -11.5, GTR_TOP), (9.5, -10.75, GTR_TOP + 0.25), _gtr_bridge, rot=GUITAR_ROT),
           el((7.75, -13.75, 11.25), (8.25, -13.5, 11.75), bevel(m='P', light='p', dark='P'), rot=GUITAR_ROT)]
        + [el((x, y, 11.75), (x + 0.5, y + 0.5, 12.25), bevel(m='P', light='p', dark='P'), rot=GUITAR_ROT)
           for x in (6.25, 9.25) for y in (-0.75, 0)]  # tuning pegs; the top left one ends at y = -0.17, under the head
        + [el((8, -8.5, 10.25), (9, 1, 10.5), _gtr_strap, rot=('z', 45, [8.5, -3.75, 10.5]))]),  # on the torso overlay
    'back_capsule_pack': dict(
        density=4,
        palette={'R': (0xE3, 0x41, 0x2F), 'r': (0xA3, 0x20, 0x14), 'q': (0xFF, 0x7A, 0x66), 'W': WHITE,
                 'g': (0xD6, 0xDC, 0xE4), 'K': (0x1A, 0x1A, 0x1E), 'k': (0x3A, 0x3A, 0x44),
                 'X': (0x2A, 0x2A, 0x30), 'x': (0x16, 0x16, 0x1A), 'Y': GOLD, 'y': LIGHT_GOLD, 'd': DARK_GOLD},
        elements=[e for inset, z0, z1 in CAP_LAYERS
                  for e in _cap_rows(lambda y, i=inset: _cap_half(y, i), CAP_Y - CAP_HH + inset,
                                     CAP_Y + CAP_HH - inset, z0, z1, _cap)]
        + _cap_rows(lambda y: math.floor(math.sqrt(max(0, 1 - (y - CAP_Y) ** 2)) * 4) / 4, CAP_Y - 1, CAP_Y + 1,
                    CAP_TOP, CAP_TOP + 0.25, _cap_button)
        + [el((7, -2.25, 10.75), (9, -1.75, 11.25), _cap_handle),  # carry loop on top
           el((7, -2.5, 10.75), (7.5, -2.25, 11.25), _cap_handle),
           el((8.5, -2.5, 10.75), (9, -2.25, 11.25), _cap_handle)]
        + pair([el((5.5, -11, 10.25), (6.5, 0, 10.5), _cap_strap),  # shoulder straps on the torso overlay
                el((5.25, -1.5, 10.25), (6.75, -1, 10.75), bevel(m='Y', light='y', dark='d'))])),  # gold slider
    'back_sword_sheath': dict(
        palette={'N': (0x7A, 0x4A, 0x26), 'M': (0x5C, 0x35, 0x19), 'D': (0x3E, 0x26, 0x14), 'S': (0xC9, 0xA2, 0x7A),
                 'g': GOLD, 'd': DARK_GOLD, 'L': LIGHT_GOLD, 'B': (0x1B, 0x2E, 0x5B), 'k': (0x0E, 0x18, 0x30)},
        elements=[el((7, -12, 10.5), (9, -4, 12), _sheath, rot=SWORD_ROT),
                  el((7.5, -13, 10.75), (8.5, -12, 11.75), _box('g', 'L', 'd'), rot=SWORD_ROT),
                  el((6.75, -4, 10.25), (9.25, -3, 12.25), _box('g', 'L', 'd', top='L'), rot=SWORD_ROT),
                  el((5.5, -3, 10.75), (10.5, -2, 11.75), _box('g', 'L', 'd', top='L'), rot=SWORD_ROT),
                  el((7.5, -2, 11), (8.5, 1.5, 11.5), _grip, rot=SWORD_ROT),
                  el((7.25, 1.5, 10.75), (8.75, 3, 11.75), _box('g', 'L', 'd', top='L'), rot=SWORD_ROT)]),
}

WEARABLES2 = {**HATS2, **BACKS2}


# ---------------------------------------------------------------------------------------------------------------------
# Front items (body bone, on the chest: every cube at z <= 6.5; the jacket layer starts at 5.75, so the visible parts
# stay in front of that)

def _links(face, i, j, w, h, p):
    if face != 'north':
        return 'D'
    return 'D' if i in (0, w - 1) else ('L' if (j // 3) % 2 else 'M')


def _plate(face, i, j, w, h, p):
    if face != 'north':
        return 'D'
    if i == 0 or j == 0:
        return 'L'
    if i == w - 1 or j == h - 1:
        return 'D'
    return 'W' if (i, j) == (2, 2) else 'M' if min(i, j, w - 1 - i, h - 1 - j) == 1 else 'd'


def _jewel(face, i, j, w, h, p):
    if face != 'north' or 0 in (i, j) or i == w - 1 or j == h - 1:
        return 'k'
    return 'q' if (i, j) in ((1, 1), (2, 1), (1, 2)) else 'Q'


def _bail(face, i, j, w, h, p):
    return 'L' if j == 0 else 'D' if face != 'north' else 'M'


def _bib(top=False, bottom=False):
    def paint(face, i, j, w, h, p):
        if face != 'north':
            return 'w'
        if i in (0, w - 1) or (top and j == 0) or (bottom and j == h - 1):
            return 'B'
        return 'd' if h32(i, j, 4) % 23 == 0 else 'W' if (i + j) % 6 else 'w'
    return paint


HEART = ["..RR..RR..", ".RqRRRRRR.", ".RRRRRRRR.", "..RRRRRR..", "...RRRR...", "....rr...."]


def _heart_small(face, i, j, w, h, p):
    """A 2 x 1.5 px red heart (8 x 6 texels) cut from the middle of HEART."""
    if face != 'north':
        return 'r'
    return HEART[j][1 + i]


def _cord(face, i, j, w, h, p):
    return 'L' if face == 'north' and j % 3 == 0 else 'K'


def _bail_dark(face, i, j, w, h, p):
    return 'L' if face == 'north' else 'K'


def _chain_thin(face, i, j, w, h, p):
    return 'C' if j % 4 < 2 else 'c'


def _capsule_row(k):
    def paint(face, i, j, w, h, p):
        if k == 2:  # black band with the button in the middle
            if face == 'north' and abs(i - (w - 1) / 2) < 2:
                return 'W' if abs(i - (w - 1) / 2) < 1.5 else 'g'
            return 'K'
        red = k > 2
        if face == 'up':
            return 'R' if red else 'W'
        if face == 'down':
            return 'r' if red else 'g'
        if red:
            return 'q' if face == 'north' and i >= w - 3 and j < 2 else 'r' if face in ('east', 'south') else 'R'
        return 'g' if face in ('east', 'south') or i < 2 else 'W'
    return paint


def _heart_inside(x, y, scale=1.0, yc=-8.4, r=2.6):
    xx, yy = (x - 8) / (r * scale), (y - yc) / (r * scale)
    return (xx * xx + yy * yy - 1) ** 3 - xx * xx * yy ** 3 <= 0


def _heart_paint(face, i, j, w, h, p):
    if face != 'north':
        return 'D'
    x, y = p[0], p[1]
    if any(not _heart_inside(x + dx, y + dy) for dx, dy in ((0.5, 0), (-0.5, 0), (0, 0.5), (0, -0.5))):
        return 'D'  # rim
    if _heart_inside(x, y, 0.7) and not _heart_inside(x, y, 0.55):
        return 'd'  # engraved inner outline
    if _heart_inside(x, y, 0.55):
        return 'W' if (x - 8) > 0.35 and y > -8.2 else 'L'
    return 'L' if (x - 8) + (y + 8.4) > 0.9 else 'M'


def _star_poly(cx, cy, big, small):
    pts = []
    for k in range(10):
        a = math.radians(90 + 36 * k)
        r = big if k % 2 == 0 else small
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


STAR_C, STAR_BIG, STAR_SMALL = (8, -9.5), 4.6, 1.9
STAR_POLY = _star_poly(*STAR_C, STAR_BIG, STAR_SMALL)


def _star_paint(face, i, j, w, h, p):
    if face != 'north':
        return 'D'
    x, y = p[0], p[1]
    if any(not inside_poly(x + dx, y + dy, STAR_POLY) for dx, dy in ((0.5, 0), (-0.5, 0), (0, 0.5), (0, -0.5))):
        return 'O'
    dx, dy = x - STAR_C[0], y - STAR_C[1]
    if math.hypot(dx, dy) < 1.0:
        return 'W'
    d = (math.degrees(math.atan2(dy, dx)) - 90 + 36) % 72 - 36  # angle from the nearest arm's axis
    return 'L' if d < 0 else 'D'


def _ribbon_stripes(face, i, j, w, h, p):
    if face != 'north':
        return 'k'
    return 'R' if i < w / 2 else 'B'


def _blossom(petal, shade, centre):
    rows = ["..aaa..", ".aaaaa.", "aaaCaaa", "aaCCCaa", "aaaCaaa", ".aaaaa.", "..aaa.."]

    def paint(face, i, j, w, h, p):
        if face != 'north':
            return shade
        ch = rows[j][i]
        if ch == '.':
            return '.'
        if ch == 'C':
            return centre
        return shade if j == 6 or i == 6 else petal
    return paint


def _leaf(face, i, j, w, h, p):
    return 'v' if j else 'V'


def _lei():
    out = []
    looks = [('P', 'p', 'C'), ('Y', 'y', 'c'), ('U', 'u', 'C')]
    for k in range(7):
        t = -1 + k / 3
        cx, cy = round((8 + 4.25 * t) * 4) / 4, round((-4 + 3.4 * t * t) * 4) / 4
        z0 = 4.75 if k % 2 else 5.0
        out.append(el((cx + 0.5, cy - 1.5, 5.5), (cx + 1.5, cy - 1, 5.75), _leaf))
        out.append(el((cx - 0.875, cy - 0.875, z0), (cx + 0.875, cy + 0.875, z0 + 0.5), _blossom(*looks[k % 3])))
    return out


CHAIN_ROT = ('z', 45, [8, -5.5, 5.25])
RIBBON_ROT = ('z', 45, [8, -5, 5.4])
CORD_ROT = ('z', 45, [8, -4.5, 5.25])
LOCKET_ROT = ('z', 45, [8, -5.5, 5.25])

FRONTS2 = {
    'front_gold_chain': dict(
        density=4,
        palette={'D': DARK_GOLD, 'M': GOLD, 'L': LIGHT_GOLD, 'W': CREAM, 'd': (0xC9, 0x93, 0x2E),
                 'Q': (0xD0, 0x2E, 0x4A), 'q': (0xFF, 0x7A, 0x8E), 'k': (0x5A, 0x10, 0x20)},
        elements=pair([el((7.5, -5.5, 5.0), (8.5, 1.5, 5.5), _links, rot=CHAIN_ROT)]) + [
            el((7.5, -7, 4.75), (8.5, -5.25, 5.25), _bail),
            el((6.5, -10, 4.75), (9.5, -7, 5.5), _plate),
            el((7.25, -9.25, 4.5), (8.75, -7.75, 4.75), _jewel)]),
    'front_baby_bib': dict(
        density=4,
        palette={'W': WHITE, 'w': (0xE6, 0xEC, 0xF4), 'B': (0x8F, 0xC8, 0xF5), 'd': (0xB8, 0xD8, 0xF2),
                 'R': (0xE3, 0x41, 0x4F), 'q': (0xFF, 0x8A, 0x96), 'r': (0xA8, 0x1F, 0x2E)},
        # the neckline: four half-pixel rows per side, each a bit wider than the one above
        elements=[el((4, y0, 5.25), (5.5 + k * 0.5, y1, 5.75), _bib(top=(y1 == 0))) for k, (y0, y1) in
                  enumerate(((-0.5, 0), (-1, -0.5), (-1.5, -1), (-2, -1.5)))]
        + [el((10.5 - k * 0.5, y0, 5.25), (12, y1, 5.75), _bib(top=(y1 == 0))) for k, (y0, y1) in
           enumerate(((-0.5, 0), (-1, -0.5), (-1.5, -1), (-2, -1.5)))]
        + [el((4, -9, 5.25), (12, -2, 5.75), _bib()),
           el((4.5, -10, 5.25), (11.5, -9, 5.75), _bib()),
           el((5.5, -11, 5.25), (10.5, -10, 5.75), _bib(bottom=True)),
           el((7, -7.25, 5.0), (9, -5.75, 5.25), _heart_small)]),
    'front_capsule_pendant': dict(
        density=4,
        palette={'R': (0xE3, 0x41, 0x2F), 'r': (0xA3, 0x20, 0x14), 'q': (0xFF, 0x7A, 0x66), 'W': WHITE,
                 'g': (0xD6, 0xDC, 0xE4), 'K': (0x1A, 0x1A, 0x1E), 'L': (0x4A, 0x4A, 0x54)},
        elements=pair([el((7.75, -4.5, 5.0), (8.25, 2.5, 5.5), _cord, rot=CORD_ROT)])
        + stack(-9.5, [(2, 1, 2), (4, 1, 2), (4, 1, 2), (4, 1, 2), (2, 1, 2)], _capsule_row, cx=8, cz=4.75)
        + [el((7.5, -4.5, 4.5), (8.5, -4, 5), _bail_dark)]),
    'front_heart_locket': dict(
        density=4,
        palette={'D': DARK_GOLD, 'M': GOLD, 'L': LIGHT_GOLD, 'W': CREAM, 'd': (0x8A, 0x5E, 0x18),
                 'C': (0xE8, 0xEE, 0xF4), 'c': (0x8E, 0x9B, 0xAD)},
        elements=pair([el((7.75, -5.5, 5.0), (8.25, 1, 5.5), _chain_thin, rot=LOCKET_ROT)])
        + silhouette(_heart_inside, 4.5, 11.5, -11.5, -5, 5.0, 5.75, _heart_paint)),
    'front_star_medal': dict(
        density=4,
        palette={'O': (0x7A, 0x53, 0x13), 'D': DARK_GOLD, 'M': GOLD, 'L': LIGHT_GOLD, 'W': CREAM,
                 'R': (0xC8, 0x2A, 0x2A), 'B': (0x2E, 0x5F, 0xC4), 'k': (0x0E, 0x18, 0x30)},
        elements=pair([el((7, -5, 5.25), (8.5, 2, 5.5), _ribbon_stripes, rot=RIBBON_ROT)])
        + silhouette(lambda x, y: inside_poly(x, y, STAR_POLY), 3.5, 12.5, -14, -4.5, 5.0, 5.5, _star_paint)),
    'front_flower_lei': dict(
        density=4,
        palette={'P': (0xFF, 0x7E, 0xB6), 'p': (0xC2, 0x50, 0x7F), 'Y': (0xFF, 0xE0, 0x66), 'y': (0xC9, 0x9A, 0x12),
                 'U': (0xA3, 0x7B, 0xFF), 'u': (0x6C, 0x4A, 0xC4), 'C': (0xFF, 0xE0, 0x66), 'c': (0xE8, 0x6A, 0x1A),
                 'V': (0x3F, 0x8A, 0x3A), 'v': (0x2E, 0x6B, 0x24)},
        elements=_lei()),
}


# ---------------------------------------------------------------------------------------------------------------------
# Ball skins: see art.BallSkin. surface(region, a, b): region 'cap_top' / 'cap_bottom' (8x8, a = x, b = y) or 'side'
# (a = column 0..31 around the ball, b = row 0..7 from the top; rows 3 and 4 are the equator band, drawn by the base).

def _smooth(t):
    return t * t * (3 - 2 * t)


def vnoise(x, y, scale, salt, wrap=None):
    """Smooth value noise in 0..1 on a lattice of `scale` texels; wrap (a multiple of scale) makes it tile in x."""
    gx, gy = x / scale, y / scale
    x0, y0 = math.floor(gx), math.floor(gy)
    fx, fy = _smooth(gx - x0), _smooth(gy - y0)

    def g(ix, iy):
        if wrap:
            ix %= wrap // scale
        return (h32(ix, iy, salt) & 0xFFFF) / 65535

    top = g(x0, y0) * (1 - fx) + g(x0 + 1, y0) * fx
    bot = g(x0, y0 + 1) * (1 - fx) + g(x0 + 1, y0 + 1) * fx
    return top * (1 - fy) + bot * fy


def _voronoi_gap(a, b, cw, ch, salt, wrap=None):
    """Distance gap between the nearest and second nearest feature point: small along the cell borders (cracks)."""
    cx, cy = a // cw, b // ch
    ds = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            gx, gy = cx + dx, cy + dy
            hx = gx % (wrap // cw) if wrap else gx
            px = gx * cw + h32(hx, gy, salt) % cw + 0.5
            py = gy * ch + h32(hx, gy, salt + 1) % ch + 0.5
            ds.append(math.hypot(a + 0.5 - px, b + 0.5 - py))
    ds.sort()
    return ds[1] - ds[0]


def _ring(a, b):
    return max(abs(a - 3.5), abs(b - 3.5))


class Neon(BallSkin):
    band, band_low, button, button_hi = '#00E5FF', '#FF3DE0', '#FF3DE0', '#FFFFFF'
    BASE, CYAN, MAG, GLOW_C, GLOW_M = '#0A0A12', '#00E5FF', '#FF3DE0', '#0A2A38', '#2E0B33'

    def surface(self, region, a, b):
        if region != 'side':
            top = region == 'cap_top'
            line, centre, glow = (self.CYAN, self.MAG, self.GLOW_C) if top else (self.MAG, self.CYAN, self.GLOW_M)
            r = _ring(a, b)
            if r == 2.5:
                return hexrgb(line)
            if r == 0.5:
                return hexrgb(centre)
            return hexrgb(glow) if r in (1.5, 3.5) and (a + b) % 2 == 0 else hexrgb(self.BASE)
        if b < 3:  # lid: cyan dashes with magenta drops
            if a % 16 == 4:
                return hexrgb(self.MAG)
            if b == 1 and a % 8 != 7:
                return hexrgb(self.CYAN)
            return hexrgb(self.GLOW_C) if b in (0, 2) and a % 8 != 7 else hexrgb(self.BASE)
        if a % 16 == 12:
            return hexrgb(self.CYAN)
        if b == 6 and a % 8 != 3:
            return hexrgb(self.MAG)
        return hexrgb(self.GLOW_M) if b in (5, 7) and a % 8 != 3 else hexrgb(self.BASE)


class Lava(BallSkin):
    band, band_low, button, button_hi = '#3A2018', '#1C0F0B', '#FF8A1F', '#FFD36B'
    ROCK = ('#1B1613', '#241D19', '#2E2621')

    def surface(self, region, a, b):
        wrap = 32 if region == 'side' else None
        bottom = region == 'cap_bottom' or (region == 'side' and b > 4)
        gap = _voronoi_gap(a, b, 8 if wrap else 5, 4 if wrap else 5, 31 if bottom else 7, wrap)
        wide = 1.5 if bottom else 0.8  # the lower half is nearly molten
        if gap < wide * 0.45:
            return hexrgb('#FFD36B')
        if gap < wide:
            return hexrgb('#FF8A1F' if h32(a, b) % 3 else '#FF5A1F')
        if gap < wide + 0.55:
            return hexrgb('#8A2A10')
        return hexrgb(self.ROCK[h32(a, b, 5) % 3])


class Ocean(BallSkin):
    band, band_low, button, button_hi = '#CFEFFF', '#8FCBEA', '#E8F8FF', '#FFFFFF'
    DEEP = ('#0B2E6B', '#154A9E', '#5FAEEA')
    SHALLOW = ('#7CC6EA', '#A6DCF2', '#F2FBFF')

    def surface(self, region, a, b):
        bottom = region == 'cap_bottom' or (region == 'side' and b > 4)
        pal = self.SHALLOW if bottom else self.DEEP
        if region == 'side':
            t = b + 1.3 * math.sin(a * math.pi / 4)  # four waves around the ball
        else:
            t = math.hypot(a - 3.5, b - 3.5) * 0.9  # ripples
        return hexrgb(pal[int(math.floor(t)) % 3])


class Camo(BallSkin):
    band, band_low, button, button_hi = '#4A4F2A', '#33381C', '#C8B87A', '#EFE3AE'

    def surface(self, region, a, b):
        side = region == 'side'
        x, y = (a + 0.5, b + 0.5) if side else (a + 0.5 + 8 * (region == 'cap_bottom'), b + 0.5 + 9)
        salt = {'side': 1, 'cap_top': 2, 'cap_bottom': 3}[region]
        n = vnoise(x, y, 4, salt, 32 if side else None)
        m = vnoise(x, y, 8 if side else 4, salt + 10, 32 if side else None)
        if m > 0.72:
            return hexrgb('#1F2414')
        if n > 0.62:
            return hexrgb('#7A5C33')
        if n < 0.3:
            return hexrgb('#B39B62')
        return hexrgb('#4F6B2A' if n > 0.45 else '#5B7A32')


class Checker(BallSkin):
    band, band_low, button, button_hi = '#D8322A', '#8E1B16', '#FFFFFF', '#FFFFFF'

    def surface(self, region, a, b):
        if region == 'cap_top':
            return hexrgb('#15151A' if (a // 2 + b // 2) % 2 else '#F2F2F5')
        if region == 'cap_bottom':
            return hexrgb('#DDE0E6' if (a // 2 + b // 2) % 2 else '#F6F6F8')
        top = b < 3
        row = (2 - b) // 2 if top else (b - 5) // 2
        odd = (a // 2 + row) % 2
        if top:
            return hexrgb('#15151A' if odd else '#F2F2F5')
        return hexrgb('#DDE0E6' if odd else '#F6F6F8')


class Candy(BallSkin):
    band, band_low, button, button_hi = '#E8366F', '#B01F52', '#FFFFFF', '#FFD1E6'

    def surface(self, region, a, b):
        bottom = region == 'cap_bottom' or (region == 'side' and b > 4)
        pink, shade = ('#FFB3D1', '#F08CB4') if bottom else ('#FF5C9E', '#E8458A')
        t = (a + b) % 4
        if t < 2:
            return hexrgb('#FFF5F8')
        return hexrgb(pink if t == 2 else shade)


class Marble(BallSkin):
    band, band_low, button, button_hi = '#7C8190', '#575C69', '#D9DCE4', '#FFFFFF'

    def surface(self, region, a, b):
        side = region == 'side'
        salt = {'side': 1, 'cap_top': 2, 'cap_bottom': 3}[region]
        x, y = (a + 2 * b + 0.5, b + 0.5) if side else (a + 0.5 + 9 * salt, b + 0.5 + 5 * salt)
        n = 0.65 * vnoise(x, y, 8, salt, 32 if side else None) + 0.35 * vnoise(x, y, 4, salt + 7, 32 if side else None)
        v = abs(n - 0.5)
        if v < 0.025:
            return hexrgb('#6C7280')
        if v < 0.06:
            return hexrgb('#9AA0AD')
        return hexrgb('#E4E6EB' if h32(a, b, salt) % 6 == 0 or v < 0.09 else '#F2F3F6')


class Toxic(BallSkin):
    band, band_low, button, button_hi = '#6FBF1B', '#3D7A0A', '#C6FF4D', '#F2FFB0'
    GOO, GOO_L, GOO_D, PURPLE = '#8DDC1F', '#B8F54A', '#5EA10E', ('#6A3AB0', '#5B2E9E', '#7C4AC8')
    DEEP = ('#3B1D66', '#2E1552', '#4B2680')

    def surface(self, region, a, b):
        if region == 'cap_top':
            r = math.hypot(a - 3.5, b - 3.5) + (h32(a, b, 3) % 3 - 1) * 0.45
            if r < 2.7:
                return hexrgb(self.GOO_L if (a, b) in ((2, 2), (3, 2)) else self.GOO)
            return hexrgb(self.PURPLE[h32(a, b, 5) % 3])
        if region == 'cap_bottom' or b > 4:
            n = h32(a, b, 8)
            return hexrgb(self.GOO if n % 41 == 0 else self.DEEP[n % 3])
        length = (1, 1, 2, 3)[h32(a // 2, 11) % 4]  # ooze drips down from the top, 1 to 3 rows
        if b < length:
            if b == 0:
                return hexrgb(self.GOO_L if h32(a, 2) % 4 == 0 else self.GOO)
            return hexrgb(self.GOO_D if b == length - 1 else self.GOO)
        return hexrgb(self.PURPLE[h32(a, b, 5) % 3])


class Holo(BallSkin):
    band, band_low, button, button_hi = '#C8CCE0', '#9096B2', '#FFFFFF', '#E6F7FF'

    def surface(self, region, a, b):
        bottom = region == 'cap_bottom' or (region == 'side' and b > 4)
        step = (a + 2 * b) // 2 if region == 'side' else (a + b) // 2
        hue = ((step % 12) / 12 + (0.5 if bottom else 0)) % 1
        if h32(a, b, 4) % 19 == 0:
            return WHITE
        s = 0.42 if (a + b) % 2 else 0.36
        return tuple(round(c * 255) for c in colorsys.hsv_to_rgb(hue, s, 1.0))


class Watermelon(BallSkin):
    band, band_low, button, button_hi = '#E7F2C3', '#B7D88C', '#1B1B1B', '#4A4A4A'

    def surface(self, region, a, b):
        if region == 'cap_top':
            if _ring(a, b) < 1:
                return hexrgb('#6B4A1E')  # the stem scar
            k = int((math.atan2(b - 3.5, a - 3.5) + math.pi) / (math.pi / 4)) % 2
            return hexrgb('#4FB848' if k else '#1E6B2B')
        if region == 'side' and b < 3:
            return hexrgb('#4FB848' if ((a + b % 2) // 2) % 2 else '#1E6B2B')  # striped rind
        if region == 'cap_bottom' and _ring(a, b) == 3.5:
            return hexrgb('#BFE08A')
        if region == 'side' and b == 7:
            return hexrgb('#F2F8D8')
        if h32(a, b, 5) % 7 == 0 and _ring(a, b) < 3.5:
            return hexrgb('#1B1B1B')  # seed
        return hexrgb('#FF5470' if b == 5 else '#E8384F')


BALL_SKINS_ART2 = {'ball_neon': Neon(), 'ball_lava': Lava(), 'ball_ocean': Ocean(), 'ball_camo': Camo(),
                   'ball_checker': Checker(), 'ball_candy': Candy(), 'ball_marble': Marble(), 'ball_toxic': Toxic(),
                   'ball_holo': Holo(), 'ball_watermelon': Watermelon()}
