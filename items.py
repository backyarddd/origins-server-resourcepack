"""Server-only items: a vanilla base item that the origins mods give components, drawn here through a custom_model_data
override on that base item's model.

Item                 base item     custom_model_data  set by
shiny_reroll_stone   echo_shard    7600001            origins_store recipe data/origins_store/recipe/shiny_reroll_stone.json

Numbers are never changed or reused once released: crafted items keep the number they were made with.

The art is a 16x16 pixel-art grid (one char per texel, binary alpha, same INK outline as the cosmetic icons), generated:
a round gem (a true 14x14 circle) whose facets carry the shiny tier colours (radiant gold, prismatic teal, cosmic
violet, aurora pink).
build() writes the texture, the item model and the base item's model with its override; check() asserts them.
"""
import json
import os

from PIL import Image

NS = 'origins'
ITEMS = [
    # id, vanilla base item, custom_model_data
    ('shiny_reroll_stone', 'echo_shard', 7600001),
]

PALETTE = {
    '.': None,
    'K': (0x0C, 0x11, 0x22),  # INK, the outline of every flat icon
    'W': (0xFF, 0xFF, 0xFF),
    'Y': (0xFF, 0xF0, 0xB8),  # warm highlight
    'G': (0xF7, 0xC9, 0x48),  # radiant
    'g': (0xB8, 0x86, 0x2B),
    'T': (0x7F, 0xE3, 0xD4),  # prismatic
    't': (0x3F, 0xA9, 0x9A),
    'V': (0xB0, 0x7C, 0xFF),  # cosmic
    'v': (0x6E, 0x3F, 0xC4),
    'P': (0xFF, 0x7B, 0xD0),  # aurora pink
}

# Row widths of a 14x14 circle centred in the 16x16 canvas (1 px transparent margin all round).
CIRCLE_WIDTHS = (6, 10, 12, 12, 14, 14, 14, 14, 14, 14, 12, 12, 10, 6)
# The glint on the upper-left crown facet.
HIGHLIGHT = {(4, 6), (5, 5), (6, 4)}


def round_gem():
    """A round brilliant-cut gem seen from above: a teal table, gold crown facets on the left, violet on the right,
    a pink pavilion facet below the table, a white highlight top-left and a 4-neighbour INK outline."""
    inside = set()
    for row, w in enumerate(CIRCLE_WIDTHS):
        y = row + 1
        for x in range(8 - w // 2, 8 + w // 2):
            inside.add((x, y))
    rows = []
    for y in range(16):
        line = ''
        for x in range(16):
            if (x, y) not in inside:
                line += '.'
                continue
            if any(n not in inside for n in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))):
                line += 'K'
                continue
            u, v = x - 7.5, y - 7.5
            if (x, y) in HIGHLIGHT:
                ch = 'W'
            elif abs(u) + abs(v) <= 3:
                ch = 'T'
            elif v > 0 and abs(u) < v - 1:
                ch = 'P'
            elif v < 0 and abs(u) < -v - 1:
                ch = 'Y'
            elif u < 0:
                ch = 'G' if v < 0 else 'g'
            else:
                ch = 'V' if v < 0 else 'v'
            line += ch
        rows.append(line)
    return rows


ART = {
    'shiny_reroll_stone': round_gem(),
}


def image(rows):
    assert len(rows) == 16 and all(len(r) == 16 for r in rows), 'art must be 16 rows of 16 chars'
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = im.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            rgb = PALETTE[ch]
            if rgb is not None:
                px[x, y] = rgb + (255,)
    return im


def paths(pack, item_id, base):
    return (os.path.join(pack, 'assets', NS, 'textures', 'item', item_id + '.png'),
            os.path.join(pack, 'assets', NS, 'models', 'item', item_id + '.json'),
            os.path.join(pack, 'assets', 'minecraft', 'models', 'item', base + '.json'))


def base_model(base, overrides):
    """The vanilla model of a plain generated item (echo_shard) plus our overrides, ascending custom_model_data."""
    return {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'minecraft:item/{base}'},
            'overrides': [{'predicate': {'custom_model_data': cmd}, 'model': f'{NS}:item/{item_id}'}
                          for item_id, cmd in sorted(overrides, key=lambda o: o[1])]}


def build(pack, write_json):
    by_base = {}
    for item_id, base, cmd in ITEMS:
        tex, model, _ = paths(pack, item_id, base)
        os.makedirs(os.path.dirname(tex), exist_ok=True)
        image(ART[item_id]).save(tex)
        write_json(model, {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{NS}:item/{item_id}'}})
        by_base.setdefault(base, []).append((item_id, cmd))
    for base, overrides in by_base.items():
        write_json(paths(pack, '', base)[2], base_model(base, overrides))


def check(pack):
    numbers = [cmd for _, _, cmd in ITEMS]
    assert len(set(numbers)) == len(numbers), f'items: duplicate custom_model_data in {numbers}'
    for item_id, base, cmd in ITEMS:
        tex, model, base_path = paths(pack, item_id, base)
        im = Image.open(tex).convert('RGBA')
        assert im.size == (16, 16), f'{tex}: {im.size}, expected 16x16'
        assert set(im.getchannel('A').tobytes()) <= {0, 255}, f'{tex}: non-binary alpha'
        with open(model, encoding='utf-8') as f:
            assert json.load(f)['textures']['layer0'] == f'{NS}:item/{item_id}', f'{model}: wrong texture'
        with open(base_path, encoding='utf-8') as f:
            overrides = json.load(f).get('overrides', [])
        hits = [o['model'] for o in overrides if o['predicate'] == {'custom_model_data': cmd}]
        assert hits == [f'{NS}:item/{item_id}'], f'{base_path}: custom_model_data {cmd} -> {hits}'
        print(f'ok  {base} #{cmd} -> {NS}:item/{item_id}')
