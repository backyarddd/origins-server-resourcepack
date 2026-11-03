"""The owner's tool skin shape rules (2026-11-03) as checks, each returning a list of failure strings (empty: pass).

Per set x state, on the 16x16 RGBA texture and its roles grid (set_roles):
1 outline: at most OUT_MAX opaque px outside the reference mask grown by 1 (8-neighbour) and at most MISS_MAX px of the
  reference mask shrunk by 1 (4-neighbour, as the audit measured it) left transparent; across sets (cross_set) each
  set's alpha differs from the per-state majority mask of the sets passed in by at most MEDIAN_MAX px.
2 symmetry: where vanilla is symmetric (SYMMETRY, on vanilla's own axis) at least SYM_MIN of the opaque pixels have an
  opaque mirror; string / line / lure / arrow / rocket pixels and handle cells are left out of the score.
3 one piece: every opaque pixel has an opaque 8-neighbour and the texture is one 8-connected piece (the rod's line and
  lure count as part of the rod).
4 slot grey: at most GREY_MAX px within GREY_DIST (Euclidean RGB) of the slot grey #8B8B8B; a grip pattern on the handle
  with a period under GRIP_PERIOD px (stripe spacing along the handle) keeps the luminance contrast between its wrap
  and plain pixels (mean against mean, Rec. 601) under GRIP_CONTRAST.

Reference masks ('#' opaque) live in shape_masks.json: the alpha of the vanilla 1.21.1 textures (diamond tier for the
tiered tools, the same outline for every tier) and of paxels 0.1.3 diamond_paxel / justhammers 21.1.4 diamond_hammer
(the same as check.PAXEL_MASK / HAMMER_MASK). `masks` rebuilds the file from the jars.

A roles grid is 16 strings of the resolved template roles (toolsets.roles: '1'..'5' head, 'p'..'s' trim, 'u' 'v' 'w'
handle, 'U' 'V' 'W' grip wrap, inlay chars), '.' transparent and OVERLAY where toolsets.textures() draws over the
template (string, line, lure, arrow, rocket, '@' anchors). Without a roles grid nothing is left out of the symmetry
score and the grip rule is skipped.

Run (from the repo root):
  python -I cosmetics/shape_rules.py check [dir] [--sets a,b]   one line per failure, exit 1 on any; dir holds
      <set>_<state>.png (default: pack/assets/origins/textures/item/toolskin); roles come from toolsets.SETS
  python -I cosmetics/shape_rules.py masks [--vanilla JAR] [--paxels JAR] [--hammers JAR]   rewrite shape_masks.json
  python -I cosmetics/shape_rules.py selftest
"""
import argparse
import io
import json
import math
import os
import sys
import zipfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
INSTANCE = os.path.abspath(os.path.join(REPO, '..', '..', '..'))  # Instances/Cobblemon
MASKS_JSON = os.path.join(HERE, 'shape_masks.json')
TOOLSKIN_DIR = os.path.join(REPO, 'pack', 'assets', 'origins', 'textures', 'item', 'toolskin')
VANILLA_JAR = os.path.join(INSTANCE, '..', '..', 'Install', 'versions', '1.21.1', '1.21.1.jar')
PAXELS_JAR = os.path.join(INSTANCE, 'mods', 'paxels-0.1.3-fabric-1.21.1.jar')
HAMMERS_JAR = os.path.join(INSTANCE, 'mods', 'just-hammers-fabric-21.1.4.jar')

# check.TOOLSET_TEXTURES (not imported: check.py imports this module); selftest asserts they match
STATES = ('sword', 'pickaxe', 'axe', 'shovel', 'hoe', 'fishing_rod', 'fishing_rod_cast', 'bow', 'bow_pulling_0',
          'bow_pulling_1', 'bow_pulling_2', 'crossbow_standby', 'crossbow_pulling_0', 'crossbow_pulling_1',
          'crossbow_pulling_2', 'crossbow_arrow', 'crossbow_firework', 'paxel', 'hammer')
SOURCES = {st: ('vanilla', f'assets/minecraft/textures/item/{"diamond_" if st in STATES[:5] else ""}{st}.png')
           for st in STATES[:17]}
SOURCES['paxel'] = ('paxels', 'assets/paxels/textures/item/diamond_paxel.png')
SOURCES['hammer'] = ('hammers', 'assets/justhammers/textures/item/diamond_hammer.png')

OUT_MAX, MISS_MAX, MEDIAN_MAX = 2, 3, 10
# axe, hoe, rod and paxel are not symmetric in vanilla: no rule for them
SYMMETRY = {'sword': 'x+y=15', 'pickaxe': 'x+y=16', 'shovel': 'x+y=16', 'hammer': 'x+y=15',
            **{st: 'x=y' for st in STATES if st.startswith(('bow', 'crossbow'))}}
SYM_MIN = 0.95
SLOT_GREY, GREY_DIST, GREY_MAX = (139, 139, 139), 45, 3
GRIP_PERIOD, GRIP_CONTRAST = 4, 60
OVERLAY = '~'
HANDLE, WRAP = 'uvwUVW', 'UVW'
N8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
N4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
_masks = None


def pts(ps, n=8):
    s = sorted(ps)
    return str(s) if len(s) <= n else str(s[:n])[:-1] + f', ... {len(s) - n} more]'


def opaque(im):
    a = im.getchannel('A').load()
    return {(x, y) for y in range(16) for x in range(16) if a[x, y]}


def grow(m):
    return m | {(x + dx, y + dy) for x, y in m for dx, dy in N8 if 0 <= x + dx < 16 and 0 <= y + dy < 16}


def shrink(m):
    return {(x, y) for x, y in m if all((x + dx, y + dy) in m for dx, dy in N4)}


def pieces(m):
    """8-connected components of m, largest first."""
    m, out = set(m), []
    while m:
        todo = [m.pop()]
        c = set(todo)
        while todo:
            x, y = todo.pop()
            for dx, dy in N8:
                if (x + dx, y + dy) in m:
                    m.remove((x + dx, y + dy))
                    c.add((x + dx, y + dy))
                    todo.append((x + dx, y + dy))
        out.append(c)
    return sorted(out, key=len, reverse=True)


def mirror(axis, p):
    if axis == 'x=y':
        return p[1], p[0]
    c = int(axis.split('=')[1])
    return c - p[1], c - p[0]


def lum(c):
    return (c[0] * 299 + c[1] * 587 + c[2] * 114) / 1000


def load_masks():
    """{state: frozenset of opaque (x, y)} from shape_masks.json, validated."""
    global _masks
    if _masks is None:
        with open(MASKS_JSON, encoding='utf-8') as f:
            raw = json.load(f)
        assert set(raw) == set(STATES), f'{MASKS_JSON}: states {sorted(set(raw) ^ set(STATES))} missing or unknown'
        for st, rows in raw.items():
            assert len(rows) == 16 and all(len(r) == 16 and set(r) <= {'#', '.'} for r in rows), \
                f'{MASKS_JSON}: {st} must be 16 rows of 16 "#" / "."'
        _masks = {st: frozenset((x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == '#')
                  for st, rows in raw.items()}
    return _masks


def outline(state, im):
    m, ref = opaque(im), load_masks()[state]
    out, miss, fails = m - grow(ref), shrink(ref) - m, []
    if len(out) > OUT_MAX:
        fails.append(f'rule 1 outline: {len(out)} px outside the reference grown by 1 (max {OUT_MAX}) {pts(out)}')
    if len(miss) > MISS_MAX:
        fails.append(f'rule 1 outline: {len(miss)} px of the reference shrunk by 1 transparent (max {MISS_MAX}) '
                     f'{pts(miss)}')
    return fails


def symmetry(state, im, roles=None):
    if state not in SYMMETRY:
        return []
    axis, m = SYMMETRY[state], opaque(im)
    scored = {(x, y) for x, y in m if roles is None or roles[y][x] not in HANDLE + OVERLAY}
    bad = {p for p in scored if mirror(axis, p) not in m}
    score = 1 - len(bad) / len(scored) if scored else 1.0
    if score < SYM_MIN:
        return [f'rule 2 symmetry across {axis}: {score:.2f} < {SYM_MIN} (string, arrow, rocket and handle left out), '
                f'no mirror for {pts(bad)}']
    return []


def one_piece(state, im):
    m, fails = opaque(im), []
    lone = [(x, y) for x, y in m if not any((x + dx, y + dy) in m for dx, dy in N8)]
    if lone:
        fails.append(f'rule 3 stray: isolated pixels {pts(lone)}')
    parts = pieces(m)
    if len(parts) > 1:
        fails.append(f'rule 3 one piece: {len(parts)} 8-connected pieces of {[len(c) for c in parts]} px, '
                     f'loose at {pts(set().union(*parts[1:]))}')
    return fails


def readable(state, im, roles=None):
    px, fails = im.load(), []
    grey = {(x, y) for x, y in opaque(im) if math.dist(px[x, y][:3], SLOT_GREY) <= GREY_DIST}
    if len(grey) > GREY_MAX:
        tones = sorted({'#%02X%02X%02X' % px[p][:3] for p in grey})
        fails.append(f'rule 4 slot grey: {len(grey)} px within {GREY_DIST} RGB of #8B8B8B (max {GREY_MAX}) in tones '
                     f'{tones} at {pts(grey)}')
    if roles is None:
        return fails
    hand = [(x, y) for y in range(16) for x in range(16) if roles[y][x] in HANDLE]
    wrap_t = {x - y for x, y in hand if roles[y][x] in WRAP}
    first = min((x - y for x, y in hand), default=None)  # a run cut off by the handle's end has no real start
    starts = sorted(t for t in wrap_t if t - 1 not in wrap_t and t != first)
    if len(starts) < 2:
        return fails
    # shortcut: the stripe spacing is taken along t = x - y (handles run at 45 degrees, 1 / sqrt(2) px per unit);
    # measure along each handle's own direction if a template ever draws a handle at another angle
    period = min(b - a for a, b in zip(starts, starts[1:])) / math.sqrt(2)
    if period >= GRIP_PERIOD:
        return fails
    wrap = [lum(px[p]) for p in hand if roles[p[1]][p[0]] in WRAP]
    plain = [lum(px[p]) for p in hand if roles[p[1]][p[0]] not in WRAP]
    contrast = abs(sum(wrap) / len(wrap) - sum(plain) / len(plain))  # what reads as stripes at slot size
    if contrast >= GRIP_CONTRAST:
        fails.append(f'rule 4 grip: pattern period {period:.1f} px < {GRIP_PERIOD} with luminance contrast '
                     f'{contrast:.0f} between wrap and plain handle pixels (max {GRIP_CONTRAST - 1})')
    return fails


def check_set(name, images, roles_by_state=None):
    """Rules 1-4 on one set: images {state: RGBA image}, roles_by_state {state: roles grid} (optional)."""
    fails = []
    for state, im in images.items():
        if state not in STATES:
            fails.append(f'{name} {state}: no reference mask for this state')
            continue
        if im.size != (16, 16):
            fails.append(f'{name} {state}: {im.size[0]}x{im.size[1]}, must be 16x16')
            continue
        im = im.convert('RGBA')
        roles = (roles_by_state or {}).get(state)
        fails += [f'{name} {state}: {f}' for f in outline(state, im) + symmetry(state, im, roles) +
                  one_piece(state, im) + readable(state, im, roles)]
    return fails


def cross_set(sets):
    """Rule 1 across sets: sets {name: {state: image}}; per state with at least 3 sets, each set's alpha within
    MEDIAN_MAX px of the majority mask (opaque in more than half of them)."""
    fails = []
    for state in STATES:
        have = {n: opaque(imgs[state].convert('RGBA')) for n, imgs in sets.items() if state in imgs}
        if len(have) < 3:
            continue
        major = {(x, y) for y in range(16) for x in range(16)
                 if 2 * sum((x, y) in m for m in have.values()) > len(have)}
        for n, m in have.items():
            if len(m ^ major) > MEDIAN_MAX:
                fails.append(f'{n} {state}: rule 1 outline across sets: {len(m ^ major)} px differ from the majority '
                             f'outline of {len(have)} sets (max {MEDIAN_MAX}) {pts(m ^ major)}')
    return fails


def check_all(sets):
    """Every rule on every set plus the cross-set outline: sets {name: (images, roles_by_state or None)}."""
    fails = []
    for name, (images, roles) in sets.items():
        fails += check_set(name, images, roles)
    return fails + cross_set({n: imgs for n, (imgs, _) in sets.items()})


def set_roles(spec):
    """{state: roles grid} of one toolsets.SETS spec, laid out by toolsets.textures() itself: the spec is rendered
    with a palette that writes each role character into the red channel, so every overlay matches the real build."""
    from cosmetics import toolsets
    probe = dict(spec, palette={chr(c): f'#{c:02X}0000' for c in range(33, 127)})
    out = {}
    for state, im in toolsets.textures(probe).items():
        px = im.load()
        base = toolsets.roles(spec[toolsets.state_template(state)], spec['grip'])
        out[state] = tuple(''.join(
            '.' if not px[x, y][3] else OVERLAY if chr(px[x, y][0]) != base[y][x] or base[y][x] == 'S' else base[y][x]
            for x in range(16)) for y in range(16))
    return out


def build_masks(vanilla=VANILLA_JAR, paxels=PAXELS_JAR, hammers=HAMMERS_JAR):
    """{state: 16 strings} read from the jars' textures (alpha > 0 is '#')."""
    jars, out = {'vanilla': vanilla, 'paxels': paxels, 'hammers': hammers}, {}
    for st in STATES:
        jar, entry = SOURCES[st]
        with zipfile.ZipFile(jars[jar]) as z, Image.open(io.BytesIO(z.read(entry))) as im:
            assert im.size == (16, 16), f'{jars[jar]} {entry}: {im.size}, expected 16x16'
            a = im.convert('RGBA').getchannel('A').load()
            out[st] = [''.join('#' if a[x, y] else '.' for x in range(16)) for y in range(16)]
    return out


def masks_text(masks):
    return json.dumps(masks, indent=1) + '\n'


def load_dir(d, only=None):
    """{set: {state: image}} from <set>_<state>.png files in d."""
    sets, by_len = {}, sorted(STATES, key=len, reverse=True)
    for f in sorted(os.listdir(d)):
        state = next((st for st in by_len if f.endswith(f'_{st}.png')), None)
        name = f[:-len(f'_{state}.png')] if state else None
        if state and (not only or name in only):
            with Image.open(os.path.join(d, f)) as im:
                sets.setdefault(name, {})[state] = im.convert('RGBA').copy()
    return sets


def cli_check(d, only):
    sys.path.insert(0, REPO)
    from cosmetics import toolsets
    sets = {}
    for name, images in load_dir(d, only).items():
        roles = set_roles(toolsets.SETS[name]) if name in toolsets.SETS else {}
        for st in [st for st in roles if st in images]:  # not rendered from today's template: alpha-only rules
            if {(x, y) for y in range(16) for x in range(16) if roles[st][y][x] != '.'} != opaque(images[st]):
                print(f'note: {name} {st}: alpha differs from toolsets.SETS, checked without roles', file=sys.stderr)
                del roles[st]
        sets[name] = (images, roles)
    fails = check_all(sets)
    for f in fails:
        print(f)
    print(f'{len(fails)} failures in {len(sets)} sets, {sum(len(i) for i, _ in sets.values())} textures',
          file=sys.stderr)
    return 1 if fails else 0


def selftest():
    sys.path.insert(0, REPO)
    from cosmetics import check, toolsets
    assert STATES == check.TOOLSET_TEXTURES, 'STATES must equal check.TOOLSET_TEXTURES'
    with open(MASKS_JSON, encoding='utf-8') as f:
        assert f.read() == masks_text(build_masks()), 'shape_masks.json is stale: run `shape_rules.py masks`'
    masks = load_masks()
    rows = lambda st: tuple(''.join('#' if (x, y) in masks[st] else '.' for x in range(16)) for y in range(16))
    assert rows('paxel') == check.PAXEL_MASK and rows('hammer') == check.HAMMER_MASK

    def paint(m, rgb=(200, 40, 40)):
        im = Image.new('RGBA', (16, 16))
        for p in m:
            im.putpixel(p, rgb + (255,))
        return im

    for st in STATES:  # the references pass their own outline / one-piece rules, and symmetry where vanilla has it
        assert not outline(st, paint(masks[st])) and not one_piece(st, paint(masks[st])), st
        if not st.startswith('bow_pulling'):  # vanilla's drawn arrow is off-axis (0.91): set arrows are left out
            assert not symmetry(st, paint(masks[st])), st
    ham = set(masks['hammer'])
    assert check_set('t', {'hammer': paint(ham)}) == []
    f = check_set('t', {'hammer': paint(ham | {(0, 0)})})  # stray pixel
    assert any('rule 3 stray' in x for x in f) and any('rule 3 one piece' in x for x in f), f
    assert any('rule 1' in x for x in check_set('t', {'hammer': paint(ham | {(13, 0), (14, 0), (15, 0)})}))
    inner = sorted(shrink(ham))[:4]
    assert any('transparent (max 3)' in x for x in check_set('t', {'hammer': paint(ham - set(inner[:4]))}))
    assert not any('rule 1' in x for x in check_set('t', {'hammer': paint(ham - set(inner[:3]))}))
    lop = {(13, 5), (14, 5), (13, 6), (14, 6)}  # one side of the head
    f = check_set('t', {'hammer': paint(ham - lop)})
    assert any('rule 2 symmetry' in x for x in f) and not any('rule 3' in x for x in f), f
    assert not symmetry('axe', paint(set(masks['axe']) - lop))  # no rule where vanilla is asymmetric
    for n, want in ((3, False), (4, True)):  # near-grey tones
        im = paint(ham)
        for p in sorted(ham)[:n]:
            im.putpixel(p, (150, 128, 140, 255))
        assert any('rule 4 slot grey' in x for x in check_set('t', {'hammer': im})) == want, n

    def gripped(period, wrap_rgb):  # hammer with its handle stair as the grip; wrap every `period` along t
        grid = [list(r.replace('#', '3')) for r in rows('hammer')]
        im = paint(ham)
        for x, y in check.HAMMER_HANDLE:
            wrap = (x - y) % period < period // 2
            grid[y][x] = 'V' if wrap else 'v'
            im.putpixel((x, y), (wrap_rgb if wrap else (40, 40, 60)) + (255,))
        return check_set('t', {'hammer': im}, {'hammer': [''.join(r) for r in grid]})
    assert any('rule 4 grip' in x for x in gripped(4, (240, 200, 20))), 'hazard-like, high contrast'
    assert not gripped(4, (70, 60, 80)), 'hazard-like, low contrast'
    assert not gripped(6, (240, 200, 20)), 'period 6 / sqrt 2 = 4.2 px is not under 4'
    base = paint(ham)
    blob = paint(ham | {(x, 15) for x in range(11)} | {(0, 14)})  # 12 px off the shape
    f = cross_set({'a': {'hammer': base}, 'b': {'hammer': base}, 'c': {'hammer': base}, 'd': {'hammer': blob}})
    assert len(f) == 1 and f[0].startswith('d hammer: rule 1 outline across sets: 12 px'), f
    assert not cross_set({'a': {'hammer': base}, 'd': {'hammer': blob}}), 'fewer than 3 sets: no median'
    for name, spec in toolsets.SETS.items():  # roles grids line up with the real renders
        assert not any(OVERLAY in r for k in check.TEMPLATES if k in spec for r in spec[k]), f'{name} uses {OVERLAY}'
        roles, ims = set_roles(spec), toolsets.textures(spec)
        assert set(roles) == set(ims), name
        for st, im in ims.items():
            assert {(x, y) for y in range(16) for x in range(16) if roles[st][y][x] != '.'} == opaque(im), (name, st)
        if 'bow' in roles:
            assert all(sum(r.count(OVERLAY) for r in roles[st]) > 0 for st in roles if st.startswith('bow'))
            arrow = sum(r.count(OVERLAY) for r in roles['bow_pulling_2']) - sum(r.count(OVERLAY) for r in roles['bow'])
            assert arrow > 0, f'{name}: the drawn arrow must be overlay'
    print('selftest ok')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('check')
    c.add_argument('dir', nargs='?', default=TOOLSKIN_DIR)
    c.add_argument('--sets', default='', help='comma-separated set names (default: every set in dir)')
    m = sub.add_parser('masks')
    m.add_argument('--vanilla', default=VANILLA_JAR)
    m.add_argument('--paxels', default=PAXELS_JAR)
    m.add_argument('--hammers', default=HAMMERS_JAR)
    sub.add_parser('selftest')
    a = ap.parse_args(argv)
    if a.cmd == 'check':
        return cli_check(a.dir, {s for s in a.sets.split(',') if s})
    if a.cmd == 'masks':
        with open(MASKS_JSON, 'w', encoding='utf-8', newline='\n') as f:
            f.write(masks_text(build_masks(a.vanilla, a.paxels, a.hammers)))
        print(f'wrote {MASKS_JSON} ({len(STATES)} states)')
        return 0
    selftest()
    return 0


if __name__ == '__main__':
    sys.exit(main())
