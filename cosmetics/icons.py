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
- aura, trail, sendout, victory, nickname: hand-drawn 16x16 templates in cosmetics/icon_art_*.py (icon_art.py has the
  rules); a new cosmetic of these types fails the build until its template is drawn;
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
from cosmetics.art import CREAM, LIGHT_GOLD, hexrgb  # noqa: E402
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


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def mix(a, b, f):
    return tuple(round(x + (y - x) * f) for x, y in zip(a[:3], b[:3]))


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
# Per-wearable framing where the kind's default view reads badly (too thin, edge-on or dark): rotation replaces
# GUI_VIEW[kind], margin replaces MARGIN. Only display.gui changes; the models and textures stay as they are.
GUI_OVERRIDE: dict[str, dict] = {
    'hat_flower_crown': {'rotation': [50, 180, 0], 'margin': 0.4},  # square-on: the ring of flowers, not a thin diamond
    'hat_golden_halo': {'rotation': [40, 180, 0], 'margin': 0.4},  # tipped up so the ring opens
    'hat_pirate': {'rotation': [10, 200, 0], 'margin': 0.4},  # low 3/4: gold brim and the skull, not the top's frame
    'hat_bunny_ears': {'rotation': [10, 180, 0], 'margin': 0.4},  # front: both ears side by side, pink inside
    'hat_cat_ears': {'rotation': [0, 210, 0], 'margin': 0.4},  # level 3/4: pink inner ears, not the stepped tops
    'back_bat_wings': {'rotation': [10, 0, 0], 'margin': 0.4},  # flat from behind: the full scalloped wing span
    'back_ball_bandolier': {'rotation': [10, 20, -25], 'margin': 0.4},  # strap corner to corner: bigger balls
    'back_capsule_pack': {'rotation': [-30, 20, 0], 'margin': 0.4},  # from below: the pill, strap tops lie flat
    'front_gold_chain': {'margin': 0.4},
    'front_capsule_pendant': {'rotation': [15, 200, 0], 'margin': 0.4},
}


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


def fit_gui(model, rotation, margin=MARGIN):
    """display.gui for the model: the rotation, the largest scale (<= 4) that keeps every projected corner margin px
    inside the 16x16 slot, and the translation that centres it. ItemTransform order: translate, rotate, scale."""
    pts = [rot_xyz((x - 8, y - 8, z - 8), rotation) for x, y, z in element_corners(model)]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    s = min((16 - 2 * margin) / (x1 - x0), (16 - 2 * margin) / (y1 - y0), 4)
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
    from cosmetics import icon_art  # lazy: icon_art and its type files import this module
    if cid in icon_art.ICONS:
        return icon_art.ICONS[cid]()
    kind = entry['type']
    if kind == 'ball_skin':
        return icon_ball(art.BALL_SKINS_ART[cid])
    if kind == 'emote':
        with Image.open(os.path.join(EMOTES, cid + '.png')) as im:
            return im.convert('RGBA')
    raise AssertionError(f'icon {cid}: no hand-drawn {kind} icon in cosmetics/icon_art*.py')


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
            o = GUI_OVERRIDE.get(cid, {})
            gui = fit_gui(model, o.get('rotation', GUI_VIEW[kind]), o.get('margin', MARGIN))
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
