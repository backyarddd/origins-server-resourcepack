"""Menu icons for every cosmetic: one model per cosmetic, drawn by minecraft:knowledge_book with custom_model_data
7500001 and up (cosmetics/icons.json numbering), plus the preview sheets cosmetics/preview/icons.png (x4, labelled,
grouped by type) and icons_1x.png (real size on a dark and a vanilla-grey slot, x2 nearest).

Refresh after the cosmetics catalog changes (a cosmetics.jsonc, e.g. a fresh copy of the live config):
    python -I cosmetics/icons.py --refresh-catalog <cosmetics.jsonc>
It rewrites cosmetics/icon_catalog.json (the fields the art needs, ids no longer in the file keep their old entry so
their icon keeps building) and appends every new id to cosmetics/icons.json with the next free number. Numbers are
never changed or reused: the configs on the server point at them.

Art, all at one texel per icon pixel (nothing upscaled), light from the top-left, binary alpha, deterministic, and the
same outer outline (INK, 4-neighbour) round every flat icon:
- aura: a small navy critter wrapped in a 1 px glow of the effect's colours, its own particle sprites round it
  (halo effects: a ring of those colours over its head);
- trail: the effect's sprites in a diagonal streak, large at the head (top right) to small at the tail;
- sendout: an Origins ball (navy / cream, gold-ringed button) with the effect's sprites fanning out above it;
- victory: rays in the effect's colours behind its hero sprite (the part sprite when it has one: trophy, crown, bolt);
- nickname: a name tag filled with the style's colours (a left-to-right gradient for several);
- ball_skin: a ball drawn as a lit sphere, its surface sampled from the skin's own art (art.BALL_SKINS_ART);
- emote: the emote's own 16x16 sprite (src/emotes, see CREDITS.md there);
- tool_skin: the set's pickaxe model; hat / back / front: the wearable model itself with a display.gui transform fitted
  to the slot (GUI_VIEW angles, scale and translation computed from the model's projected bounds).
"""
import json
import math
import os
import re
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from cosmetics import art  # noqa: E402
from cosmetics.art import CREAM, GOLD, LIGHT_GOLD, NAVY, hexrgb  # noqa: E402
from cosmetics.check import TOOL_SETS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS_JSON = os.path.join(HERE, 'icons.json')
CATALOG_JSON = os.path.join(HERE, 'icon_catalog.json')
PREVIEW = os.path.join(HERE, 'preview')
NS = 'origins'
FIRST_CMD = 7500001
BASE_ITEM = 'knowledge_book'
PLAIN = f'{NS}:item/icon/plain_{BASE_ITEM}'
CATALOG_FIELDS = ('type', 'name', 'rarity', 'colors', 'effect', 'custom_model_data')
MODEL_TYPES = ('tool_skin', 'hat', 'back', 'front')  # no texture of their own: the icon is an existing model
TYPE_ORDER = ('aura', 'trail', 'sendout', 'victory', 'nickname', 'emote', 'ball_skin', 'tool_skin', 'hat', 'back',
              'front')

INK = (0x0C, 0x11, 0x22)  # the outer outline of every flat icon
RIM = (0x6E, 0x7F, 0xA8)  # the outline next to a near-black pixel instead, so dark art (bats, ink) still reads
EMOTES = os.path.join(ROOT, 'src', 'emotes')


# --- catalog + numbering ---------------------------------------------------------------------------------------------

def strip_jsonc(text):
    """JSON with // line comments -> JSON (a // inside a string is kept)."""
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == '\\':
                out.append(text[i + 1])
                i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
            out.append(c)
        elif text.startswith('//', i):
            while i < n and text[i] != '\n':
                i += 1
            continue
        else:
            out.append(c)
        i += 1
    return ''.join(out)


def load_json(path, default):
    if not os.path.isfile(path):
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def write_lines(path, entries):
    """{key: obj} as a JSON object with one entry per line (diff-friendly)."""
    body = ',\n'.join(f'  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}' for k, v in entries.items())
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('{\n' + body + '\n}\n')


def refresh_catalog(src):
    with open(src, encoding='utf-8') as f:
        cosmetics = json.loads(strip_jsonc(f.read()))['cosmetics']
    catalog, icons = load_json(CATALOG_JSON, {}), load_json(ICONS_JSON, {})
    ids = set()
    for c in cosmetics:
        cid = c['id']
        assert re.fullmatch(r'[a-z0-9_]{1,28}', cid) and cid not in ids, f'{src}: bad or duplicate id {cid!r}'
        ids.add(cid)
        catalog[cid] = {k: c[k] for k in CATALOG_FIELDS if k in c}
    nxt = max([e['cmd'] for e in icons.values()], default=FIRST_CMD - 1) + 1
    added = []
    for c in cosmetics:
        if c['id'] not in icons:
            icons[c['id']] = {'cmd': nxt, 'type': c['type']}
            added.append(c['id'])
            nxt += 1
    catalog = {cid: catalog[cid] for cid in icons}  # icons.json order (append-only), removed ids kept
    write_lines(CATALOG_JSON, catalog)
    write_lines(ICONS_JSON, icons)
    gone = [cid for cid in icons if cid not in ids]
    print(f'{len(cosmetics)} cosmetics in {src}: {len(added)} new icon numbers, {len(icons)} total'
          + (f', {len(gone)} no longer in the file (kept): {", ".join(gone)}' if gone else ''))


# --- pixel helpers ---------------------------------------------------------------------------------------------------

def canvas():
    return Image.new('RGBA', (16, 16), (0, 0, 0, 0))


def crop(im):
    box = im.getchannel('A').getbbox()
    return im.crop(box) if box else im


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def mix(a, b, f):
    return tuple(round(x + (y - x) * f) for x, y in zip(a[:3], b[:3]))


def colours(im):
    px = im.convert('RGBA').getdata()
    return [p[:3] for p in px if p[3]]


def tones(im):
    """(dark, mid, light) of a sprite: its opaque colours by luminance at 15 / 50 / 85 %."""
    cs = sorted(colours(im), key=lum)
    return cs[int(len(cs) * 0.15)], cs[len(cs) // 2], cs[min(len(cs) - 1, int(len(cs) * 0.85))]


def halve(im):
    """Exact 2:1 reduction for the 16x16 emote sprites: each 2x2 block becomes its most common opaque colour (ties: the
    darker one, which keeps outlines and features), opaque when at least two of the four are."""
    w, h = (im.width + 1) // 2, (im.height + 1) // 2
    src, out = im.load(), Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = out.load()
    for y in range(h):
        for x in range(w):
            block = [src[i, j][:3] for i in (2 * x, 2 * x + 1) for j in (2 * y, 2 * y + 1)
                     if i < im.width and j < im.height and src[i, j][3]]
            if len(block) >= 2:
                px[x, y] = min(set(block), key=lambda c: (-block.count(c), lum(c))) + (255,)
    return out


def fit(im, n, halving=True):
    """The sprite cropped to its pixels, kept at its own size when its longer side is at most n; a 16x16 sprite is
    halved exactly when that fits (halve, unless halving=False); anything else is shrunk with a box filter, alpha
    >= 50 % and its colours snapped back to the sprite's own."""
    im = crop(im.convert('RGBA'))
    if max(im.size) <= n:
        return im
    if halving and max(im.size) > 8 and max((im.width + 1) // 2, (im.height + 1) // 2) <= max(n, 8):
        return crop(halve(im))
    k = n / max(im.size)
    size = (max(1, round(im.width * k)), max(1, round(im.height * k)))
    small = im.convert('RGBa').resize(size, Image.BOX).convert('RGBA')
    pal = sorted(set(colours(im)))
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    spx, opx = small.load(), out.load()
    for y in range(size[1]):
        for x in range(size[0]):
            r, g, b, a = spx[x, y]
            if a >= 128:
                opx[x, y] = min(pal, key=lambda c: (c[0] - r) ** 2 + (c[1] - g) ** 2 + (c[2] - b) ** 2) + (255,)
    return out


def put(cv, im, x, y):
    """Paste an opaque-or-clear sprite with its top-left at (x, y); parts outside the 16x16 are dropped."""
    px, cp = im.load(), cv.load()
    for j in range(im.height):
        for i in range(im.width):
            if px[i, j][3] and 0 <= x + i < 16 and 0 <= y + j < 16:
                cp[x + i, y + j] = px[i, j]


def put_c(cv, im, cx, cy):
    """Paste centred on (cx, cy) (pixel-centre coordinates)."""
    put(cv, im, round(cx - im.width / 2 + 0.01), round(cy - im.height / 2 + 0.01))


def dark_patch(px, x, y):
    """True when the art pixel at (x, y) and every art pixel round it (8-neighbour) is near-black: dark art such as
    bats or ink, not merely the dark outline of a bright sprite."""
    return all(lum(px[i, j][:3]) < 80 for i in range(max(0, x - 1), min(16, x + 2))
               for j in range(max(0, y - 1), min(16, y + 2)) if px[i, j][3])


def outline(cv):
    """The family outline: every clear pixel next (4-neighbour) to art becomes INK, or RIM next to dark art (see
    dark_patch); art that already ends in INK is left as it is."""
    px = cv.load()
    edge = {}
    for y in range(16):
        for x in range(16):
            if px[x, y][3]:
                continue
            near = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if 0 <= x + dx < 16 and 0 <= y + dy < 16 and px[x + dx, y + dy][3]
                    and px[x + dx, y + dy][:3] not in (INK, RIM)]
            if near:
                edge[x, y] = RIM if any(dark_patch(px, *p) for p in near) else INK
    for p, c in edge.items():
        px[p] = c + (255,)
    return cv


def tinted(im, colour):
    """A neutral sprite multiplied by a colour (what particle tinting does in game)."""
    out = im.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (r * colour[0] // 255, g * colour[1] // 255, b * colour[2] // 255, 255)
    return out


# --- effect icons ----------------------------------------------------------------------------------------------------

CRITTER = [  # the aura wearer: a small original eared critter, lit from the top-left
    ".O..O.",
    "OLOOMO",
    "OWLLMO",
    "OXLMXO",
    "OLMMMO",
    ".OOOO.",
]
P_CRITTER = {'O': INK, 'M': (0x24, 0x36, 0x66), 'L': (0x34, 0x4D, 0x8C), 'W': (0x4E, 0x69, 0xAE), 'X': CREAM}
BALL9 = [  # the send-out ball: Origins navy top, cream bottom, dark band, gold-ringed white button
    "...OOO...",
    ".OOnnNOO.",
    ".OnNNNNO.",
    "OnNNGNNNO",
    "OOOGWGOOO",
    "OCCCGCCcO",
    ".OCCCCcO.",
    ".OOCccOO.",
    "...OOO...",
]
# the navy is lifted a step (brand navy vanishes on a dark menu slot)
P_BALL9 = {'O': INK, 'N': (0x2E, 0x4A, 0x8C), 'n': (0x5A, 0x7C, 0xC8), 'G': GOLD, 'W': (0xFF, 0xFF, 0xFF), 'C': CREAM,
           'c': (0xD9, 0xC6, 0x9C)}


def effect_frames(eid):
    """The effect's own particle sprites (rainbow-tinted effects: their neutral sprite in the rainbow colours) and its
    hero sprite (the part sprite, e.g. trophy / crown / bolt) or None."""
    from cosmetics import build as cb  # lazy: cosmetics/build.py imports this module
    p = cb.EFFECTS[eid]
    frames = p['frames']
    if 'tint' in p:
        frames = [tinted(f, hexrgb(c)) for f in frames for c in cb.RAINBOW]
    hero = None
    if 'part' in p:
        hero = cb.PARTS[f'{eid}_{p["part"]}']['frames'][0]
    return [f.convert('RGBA') for f in frames], hero


def ring(cv, cx, cy, rx, ry, frames, front):
    """An ellipse ring, coloured by the frames' light tones in turn round it; front=True draws only its lower half."""
    cols = [tones(f)[2] for f in frames]
    px = cv.load()
    pts = {}
    for k in range(720):
        a = math.radians(k / 2)
        x, y = round(cx + rx * math.cos(a)), round(cy + ry * math.sin(a))
        pts.setdefault((x, y), k)
    for (x, y), k in pts.items():
        if 0 <= x < 16 and 0 <= y < 16 and (y > cy) == front:
            px[x, y] = cols[(k * len(cols)) // 720] + (255,)


def glow(cv, frames):
    """The aura itself: a 1 px rim round everything drawn so far, in the effect's light tones (they alternate round
    the rim from the top-left, one colour per 3 pixels)."""
    cols = [tones(f)[2] for f in frames]
    px = cv.load()
    rim = sorted({(x + dx, y + dy) for y in range(16) for x in range(16) if px[x, y][3]
                  for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                  if 0 <= x + dx < 16 and 0 <= y + dy < 16 and not px[x + dx, y + dy][3]},
                 key=lambda p: math.atan2(p[1] - 10, p[0] - 7.5))
    for k, p in enumerate(rim):
        px[p] = cols[(k // 3) % len(cols)] + (255,)


def icon_aura(eid):
    frames, _ = effect_frames(eid)
    cv = canvas()
    put(cv, art.sprite(CRITTER, P_CRITTER), 5, 9)
    glow(cv, frames)
    if 'halo' in eid:  # the name promises a halo: a ring of its colours over the critter's head
        ring(cv, 7.5, 6, 4.5, 1.5, frames, front=False)
        ring(cv, 7.5, 6, 4.5, 1.5, frames, front=True)
        put_c(cv, fit(frames[0], 5), 2.5, 2.5)
        put_c(cv, fit(frames[-1], 5), 13, 2.5)
    else:
        put_c(cv, fit(frames[0], 7), 3.5, 3.5)
        put_c(cv, fit(frames[1 % len(frames)], 6), 12.5, 3.5)
        put_c(cv, fit(frames[2 % len(frames)], 4), 1.5 if len(frames) % 2 else 14, 12.5)
    return outline(cv)


def icon_trail(eid):
    frames, _ = effect_frames(eid)
    cv = canvas()
    cols = [tones(f)[1] for f in frames]
    px = cv.load()
    for k, (x, y) in enumerate(((2, 14), (3, 13), (5, 12), (6, 11), (8, 10), (9, 8))):  # the dotted streak
        if k % 2 == 0:
            px[x, y] = cols[k % len(cols)] + (255,)
    put_c(cv, fit(frames[-1], 4), 4, 11.5)
    put_c(cv, fit(frames[1 % len(frames)], 5), 7.5, 7.5)
    put_c(cv, fit(frames[0], 7), 11.5, 4)
    return outline(cv)


def icon_sendout(eid):
    frames, _ = effect_frames(eid)
    cv = canvas()
    for k, (x, y) in enumerate(((2.5, 5.5), (7.5, 2.5), (12.5, 5.5))):  # the burst fans out over the ball
        put_c(cv, fit(frames[k % len(frames)], 5), x, y)
    tick = [tones(f)[2] for f in frames]
    px = cv.load()
    for k, pts in enumerate((((2, 9), (1, 10)), ((7, 5), (7, 6)), ((12, 9), (13, 10)))):
        for p in pts:
            if not px[p][3]:
                px[p] = tick[k % len(tick)] + (255,)
    put(cv, art.sprite(BALL9, P_BALL9), 3, 7)
    return outline(cv)


def icon_victory(eid):
    frames, hero = effect_frames(eid)
    cv = canvas()
    px = cv.load()
    # rays in the effect's own light / mid tones; a dark tone (an emote's outline) falls back to the Origins golds
    light = [c if lum(c) >= 100 else LIGHT_GOLD for c in (tones(f)[2] for f in frames)]
    mid = [c if lum(c) >= 100 else GOLD for c in (tones(f)[1] for f in frames)]
    for k in range(8):  # rays: long on the axes, short on the diagonals
        a = math.radians(k * 45 - 90)
        r1 = 7.6 if k % 2 == 0 else 6.2
        for s in range(8):
            r = 3 + (r1 - 3) * s / 7
            x, y = math.floor(7.5 + r * math.cos(a) + 0.5), math.floor(7.5 + r * math.sin(a) + 0.5)
            if 0 <= x < 16 and 0 <= y < 16:
                px[x, y] = (light if r < r1 - 1.5 else mid)[k % len(light)] + (255,)
    if hero is not None:  # a 16x16 part sprite (trophy, crown, bolt): shrunk to 12, the hero fills the burst
        art_ = fit(hero, 12, halving=False)
    else:  # an emote of 13 px or less (GG, 100) stays legible at its own size; a full face is halved
        art_ = fit(frames[0], 13)
    put_c(cv, art_, 7.5, 7.5)
    return outline(cv)


# --- nickname tag ----------------------------------------------------------------------------------------------------

TAG = [
    "....OOOOOOOOOOOO",
    "...OHHHHHHHHHHHO",
    "..OHBBBBBBBBBBBO",
    ".OHBkkBBBBBBBBSO",
    "OHBBkkBTTTBTTBSO",
    "OBBBBBBBBBBBBBSO",
    ".OBBBBBTTBTTTBSO",
    "..OBBBBBBBBBBBSO",
    "...OSSSSSSSSSSSO",
    "....OOOOOOOOOOOO",
]
# the tag's string: up out of the hole into a small loop (light gold on the lit left side)
STRING = [(4, 5), (4, 4), (4, 3), (3, 2), (3, 1), (4, 0), (5, 0), (6, 1), (6, 2), (5, 3)]


def gradient(colors, t):
    cs = [hexrgb(c) for c in colors]
    if len(cs) == 1:
        return cs[0]
    t *= len(cs) - 1
    k = min(int(t), len(cs) - 2)
    return mix(cs[k], cs[k + 1], t - k)


def icon_nickname(colors):
    cv = canvas()
    px = cv.load()
    y0 = 4
    for j, row in enumerate(TAG):
        for i, ch in enumerate(row):
            if ch == '.':
                continue
            base = gradient(colors, max(0, min(1, (i - 2) / 12)))
            c = {'O': INK, 'B': base, 'H': mix(base, (255, 255, 255), 0.45), 'S': mix(base, (0, 0, 0), 0.3),
                 'k': INK, 'T': mix(base, (0, 0, 0), 0.5) if lum(base) > 110 else mix(base, (255, 255, 255), 0.6)}[ch]
            px[i, y0 + j] = c + (255,)
    for x, y in STRING:
        px[x, y + 1] = (LIGHT_GOLD if x < 5 else GOLD) + (255,)
    return outline(cv)


# --- ball skin -------------------------------------------------------------------------------------------------------

LIGHT = (-0.5, 0.62, 0.6)  # toward the light: left, up, toward the viewer
TILT = math.radians(18)  # seen a little from above, so the band curves and the top cap shows


def ball_texel(skin, x, y, z):
    """The skin's colour at a point of the unit sphere (object space, +y up, +z toward the viewer)."""
    cap = 0.80
    if y > cap or y < -cap:
        top = y > 0
        a = min(7, max(0, int((x / 0.6 + 1) * 4)))
        b = min(7, max(0, int((z / 0.6 + 1) * 4)))
        return skin.surface('cap_top' if top else 'cap_bottom', a, b)
    col = int(((math.atan2(x, z) / (2 * math.pi)) % 1) * 32)
    if abs(y) <= 0.14:
        return hexrgb(skin.band if y >= 0 else skin.band_low)
    if y > 0:
        row = min(2, int((cap - y) / (cap - 0.14) * 3))
    else:
        row = 5 + min(2, int((-0.14 - y) / (cap - 0.14) * 3))
    return skin.surface('side', col, row)


def icon_ball(skin):
    cv = canvas()
    px = cv.load()
    R = 6.9
    ln = math.sqrt(sum(c * c for c in LIGHT))
    lx, ly, lz = (c / ln for c in LIGHT)
    ct, st = math.cos(TILT), math.sin(TILT)
    for py in range(16):
        for qx in range(16):
            nx, ny = (qx + 0.5 - 8) / R, -(py + 0.5 - 8) / R
            d = nx * nx + ny * ny
            if d > 1:
                continue
            nz = math.sqrt(1 - d)
            # view -> object: undo the tilt about x (the top leans toward the viewer)
            oy, oz = ny * ct + nz * st, -ny * st + nz * ct
            # the button: a disc round the front of the band
            bd = math.hypot(nx, oy)
            if oz > 0 and bd < 0.36:
                c = hexrgb(skin.band_low) if bd > 0.24 else hexrgb(skin.button_hi if (nx < -0.05 and oy > 0.04)
                                                                    else skin.button)
            else:
                c = ball_texel(skin, nx, oy, oz)
            dot = nx * lx + ny * ly + nz * lz
            f = 1.08 if dot > 0.55 else 0.94 if dot > 0.1 else 0.78 if dot > -0.35 else 0.64
            c = tuple(min(255, round(v * f)) for v in c)
            if dot > 0.93:
                c = mix(c, (255, 255, 255), 0.6)
            px[qx, py] = c + (255,)
    return outline(cv)


# --- wearables: display.gui fitted to the slot, and a renderer of the GUI view ---------------------------------------

GUI_VIEW = {'hat': (25, 225, 0), 'back': (15, 20, 0), 'front': (10, 200, 0)}  # display.gui rotation per kind
MARGIN = 0.75  # px kept free round the fitted model in the 16x16 slot


def rot_xyz(p, r):
    """JOML rotationXYZ(x, y, z) applied to p (= Rx * Ry * Rz * p), degrees; +z toward the viewer in the GUI."""
    x, y, z = p
    for axis, deg in (('z', r[2]), ('y', r[1]), ('x', r[0])):
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        if axis == 'x':
            y, z = y * c - z * s, y * s + z * c
        elif axis == 'y':
            x, z = x * c + z * s, -x * s + z * c
        else:
            x, y = x * c - y * s, x * s + y * c
    return x, y, z


def element_corners(model):
    from cosmetics import build as cb
    out = []
    for e in model['elements']:
        pts = [(x, y, z) for x in (e['from'][0], e['to'][0]) for y in (e['from'][1], e['to'][1])
               for z in (e['from'][2], e['to'][2])]
        r = e.get('rotation')
        if r:
            pts = [cb.rotate(p, r['axis'], r['angle'], r['origin']) for p in pts]
        out += pts
    return out


def fit_gui(model, rotation):
    """display.gui for the model: the rotation, the largest scale (<= 4) that keeps every projected corner MARGIN px
    inside the 16x16 slot, and the translation that centres it. ItemTransform order: translate, rotate, scale."""
    pts = [rot_xyz((x - 8, y - 8, z - 8), rotation) for x, y, z in element_corners(model)]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    s = min((16 - 2 * MARGIN) / (x1 - x0), (16 - 2 * MARGIN) / (y1 - y0), 4)
    s = math.floor(s * 100) / 100
    t = [round(-s * (x0 + x1) / 2, 2), round(-s * (y0 + y1) / 2, 2), 0]
    return {'rotation': list(rotation), 'translation': t, 'scale': [s, s, s]}


def render_gui(model, tex, gui, size):
    """The model as the GUI draws it in a 16x16 slot, rasterised at size x size (orthographic, painter's order,
    flat side lighting)."""
    from cosmetics import build as cb
    k = size / 16
    s, t, r = gui['scale'][0], gui['translation'], gui['rotation']
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    faces = []
    for n, (pts, rgb, normal) in enumerate(cb.model_quads(model, tex)):
        nx, ny, nz = rot_xyz(normal, r)
        if nz <= 1e-6:
            continue
        q = [rot_xyz((x - 8, y - 8, z - 8), r) for x, y, z in pts]
        q = [(8 + t[0] + s * x, 8 - t[1] - s * y, s * z) for x, y, z in q]
        f = min(1.0, 0.55 + 0.45 * nz + 0.15 * max(0, ny))  # roughly the GUI's side lighting
        faces.append((sum(p[2] for p in q) / 4, n, [(x * k, y * k) for x, y, _ in q],
                      tuple(min(255, round(c * f)) for c in rgb)))
    for _, _, poly, rgb in sorted(faces):
        draw.polygon(poly, fill=rgb + (255,))
    return im


def wearable(pack, cid):
    with open(os.path.join(pack, 'assets', NS, 'models', 'cosmetic', cid + '.json'), encoding='utf-8') as f:
        model = json.load(f)
    with Image.open(os.path.join(pack, 'assets', NS, 'textures', 'cosmetic', cid + '.png')) as im:
        tex = im.convert('RGBA')
    return model, tex


def tool_set(entry, cid):
    sets = {v: k for k, v in TOOL_SETS.items()}
    cmd = entry.get('custom_model_data')
    assert cmd in sets, f'icon {cid}: tool skin custom_model_data {cmd} is not a set in check.TOOL_SETS'
    return sets[cmd]


# --- build -----------------------------------------------------------------------------------------------------------

def flat_icon(cid, entry):
    kind = entry['type']
    if kind == 'nickname':
        return icon_nickname(entry['colors'])
    if kind == 'ball_skin':
        return icon_ball(art.BALL_SKINS_ART[cid])
    if kind == 'emote':
        with Image.open(os.path.join(EMOTES, cid + '.png')) as im:
            return im.convert('RGBA')
    eid = entry['effect'].split(':', 1)[1].rsplit('/', 1)[1]
    return {'aura': icon_aura, 'trail': icon_trail, 'sendout': icon_sendout, 'victory': icon_victory}[kind](eid)


def build(pack, write_json):
    """Write the icon textures + models, knowledge_book.json and the previews; returns {id: (type, preview image at
    x4)}."""
    icons, catalog = load_json(ICONS_JSON, {}), load_json(CATALOG_JSON, {})
    assert icons, f'{ICONS_JSON} is empty: run python -I cosmetics/icons.py --refresh-catalog <cosmetics.jsonc>'
    models = os.path.join(pack, 'assets', NS, 'models', 'item', 'icon')
    textures = os.path.join(pack, 'assets', NS, 'textures', 'item', 'icon')
    for d in (models, textures):
        shutil.rmtree(d, ignore_errors=True)  # only this module's own output
    os.makedirs(textures)
    shown = {}
    for cid, e in icons.items():
        entry = catalog[cid]
        kind = entry['type']
        assert kind == e['type'], f'icon {cid}: type {kind} in the catalog, {e["type"]} in icons.json'
        if kind == 'tool_skin':
            s = tool_set(entry, cid)
            write_json(os.path.join(models, cid + '.json'), {'parent': f'{NS}:item/toolskin/{s}_pickaxe'})
            with Image.open(os.path.join(pack, 'assets', NS, 'textures', 'item', 'toolskin', f'{s}_pickaxe.png')) as im:
                img = im.convert('RGBA')
            shown[cid] = (kind, img, None)
        elif kind in ('hat', 'back', 'front'):
            model, tex = wearable(pack, cid)
            gui = fit_gui(model, GUI_VIEW[kind])
            write_json(os.path.join(models, cid + '.json'), {'parent': f'{NS}:cosmetic/{cid}', 'display': {'gui': gui}})
            shown[cid] = (kind, None, (model, tex, gui))
        else:
            img = flat_icon(cid, entry)
            assert img.size == (16, 16), f'icon {cid}: {img.size}'
            img.save(os.path.join(textures, cid + '.png'), optimize=True)
            write_json(os.path.join(models, cid + '.json'), {'parent': 'minecraft:item/generated',
                                                             'textures': {'layer0': f'{NS}:item/icon/{cid}'}})
            shown[cid] = (kind, img, None)
    write_json(os.path.join(models, f'plain_{BASE_ITEM}.json'),
               {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'minecraft:item/{BASE_ITEM}'}})
    order = sorted(icons, key=lambda c: icons[c]['cmd'])
    overrides = [{'predicate': {'custom_model_data': icons[c]['cmd']}, 'model': f'{NS}:item/icon/{c}'} for c in order]
    overrides.append({'predicate': {'custom_model_data': icons[order[-1]]['cmd'] + 1}, 'model': PLAIN})
    write_json(os.path.join(pack, 'assets', 'minecraft', 'models', 'item', BASE_ITEM + '.json'),
               {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'minecraft:item/{BASE_ITEM}'},
                'overrides': overrides})
    preview(shown, os.path.join(PREVIEW, 'icons.png'))
    preview_1x(shown, os.path.join(PREVIEW, 'icons_1x.png'))
    print(f'icons: {len(icons)} cosmetic icons on minecraft:{BASE_ITEM} (custom_model_data '
          f'{icons[order[0]]["cmd"]}..{icons[order[-1]]["cmd"]}, catch-all {icons[order[-1]]["cmd"] + 1})')


# --- previews --------------------------------------------------------------------------------------------------------

SLOT_FILL, SLOT_DARK, SLOT_LIGHT = (0x17, 0x1D, 0x2E), (0x0A, 0x0E, 0x18), (0x2E, 0x38, 0x55)
GREY_FILL, GREY_DARK, GREY_LIGHT = (0x8B, 0x8B, 0x8B), (0x37, 0x37, 0x37), (0xFF, 0xFF, 0xFF)


def slot(scale, fill=SLOT_FILL, dark=SLOT_DARK, light=SLOT_LIGHT):
    """An 18x18 inventory-style slot (inset: dark top-left edge, light bottom-right) at the given scale."""
    im = Image.new('RGBA', (18 * scale, 18 * scale), fill + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 18 * scale - 1, scale - 1], fill=dark + (255,))
    d.rectangle([0, 0, scale - 1, 18 * scale - 1], fill=dark + (255,))
    d.rectangle([0, 17 * scale, 18 * scale - 1, 18 * scale - 1], fill=light + (255,))
    d.rectangle([17 * scale, scale, 18 * scale - 1, 18 * scale - 1], fill=light + (255,))
    return im


def icon_at(item, px):
    """The icon as the slot shows it at px x px: flat art nearest-scaled, models rendered at that resolution."""
    _, img, m = item
    if m:
        return render_gui(m[0], m[1], m[2], px)
    return img.resize((px, px), Image.NEAREST)


def groups(shown):
    return [(t, [c for c, v in shown.items() if v[0] == t]) for t in TYPE_ORDER if any(v[0] == t for v in
                                                                                        shown.values())]


def preview(shown, path, cols=12):
    font = ImageFont.load_default()
    scale, pad, label_h, head_h = 4, 10, 14, 22
    cw, ch = 18 * scale + 34, 18 * scale + label_h + 8
    gs = groups(shown)
    height = pad + sum(head_h + ((len(ids) + cols - 1) // cols) * ch for _, ids in gs) + pad
    sheet = Image.new('RGBA', (pad * 2 + cols * cw, height), (0x10, 0x14, 0x20, 255))
    draw = ImageDraw.Draw(sheet)
    y = pad
    for kind, ids in gs:
        draw.text((pad, y + 4), f'{kind} ({len(ids)})', fill=LIGHT_GOLD + (255,), font=font)
        y += head_h
        for k, cid in enumerate(ids):
            x, yy = pad + (k % cols) * cw, y + (k // cols) * ch
            s = slot(scale)
            s.alpha_composite(icon_at(shown[cid], 16 * scale), (scale, scale))
            sheet.alpha_composite(s, (x + (cw - s.width) // 2, yy))
            label = cid.split('_', 1)[1] if cid.split('_', 1)[0] in ('aura', 'trail', 'sendout', 'victory', 'nick',
                                                                     'emote', 'ball', 'ts', 'hat', 'back',
                                                                     'front') else cid
            label = label if len(label) <= 17 else label[:16] + '.'
            tw = draw.textlength(label, font=font)
            draw.text((x + (cw - tw) / 2, yy + 18 * scale + 2), label, fill=CREAM + (255,), font=font)
        y += ((len(ids) + cols - 1) // cols) * ch
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path, optimize=True)


def preview_1x(shown, path, cols=12):
    """Real size: every icon at 16x16 in an 18x18 slot (models rendered at 32, what GUI scale 2 draws), the whole
    sheet x2 nearest; dark menu slots on the left, vanilla grey slots on the right."""
    gs = groups(shown)
    rows = sum((len(ids) + cols - 1) // cols for _, ids in gs) + len(gs)
    panel_w = cols * 18 + 4
    base = Image.new('RGBA', (2 * panel_w + 8, rows * 18 + 8), (0x10, 0x14, 0x20, 255))
    big = []
    for side, colours_ in enumerate(((SLOT_FILL, SLOT_DARK, SLOT_LIGHT), (GREY_FILL, GREY_DARK, GREY_LIGHT))):
        r = 0
        for kind, ids in gs:
            for k, cid in enumerate(ids):
                x, y = 4 + side * (panel_w + 4) + (k % cols) * 18, 4 + (r + k // cols) * 18
                base.alpha_composite(slot(1, *colours_), (x, y))
                if shown[cid][2]:
                    big.append((x, y, cid))
                else:
                    base.alpha_composite(shown[cid][1], (x + 1, y + 1))
            r += (len(ids) + cols - 1) // cols + 1
    sheet = base.resize((base.width * 2, base.height * 2), Image.NEAREST)
    for x, y, cid in big:
        sheet.alpha_composite(icon_at(shown[cid], 32), (2 * x + 2, 2 * y + 2))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path, optimize=True)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--refresh-catalog':
        refresh_catalog(sys.argv[2])
    else:
        sys.exit('usage: python -I cosmetics/icons.py --refresh-catalog <cosmetics.jsonc>  (icons are built by '
                 'python -I build.py)')
