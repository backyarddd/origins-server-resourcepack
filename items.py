"""Server-only items: a vanilla base item that the origins mods give components, drawn here through a custom_model_data
override on that base item's model.

Item                 base item     custom_model_data  set by
shiny_reroll_stone   echo_shard    7600001            origins_store recipe data/origins_store/recipe/shiny_reroll_stone.json

Numbers are never changed or reused once released: crafted items keep the number they were made with.

The art is a 16x16 pixel-art template (one char per texel, binary alpha, same INK outline as the cosmetic icons):
a faceted crystal whose facets carry the shiny tier colours (radiant gold, prismatic teal, cosmic violet, aurora pink).
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

ART = {
    'shiny_reroll_stone': [
        '......KKKK......',
        '.....KWYTTK.....',
        '....KWGWTTVK....',
        '...KGGWTTTVVK...',
        '..KGGGWTTTVVVK..',
        '..KGGGWTTTVVWK..',
        '.KgGGGWTTTVVVvK.',
        '.KgGGWTTTTTVVvK.',
        '.KggGTTTTTPVvvK.',
        '.KggGTTTTPPVvvK.',
        '..KggTTtPPPvvK..',
        '..KggtttPPvvvK..',
        '...KgtttPvvvK...',
        '....KtttvvvK....',
        '.....KttvvK.....',
        '......KKKK......',
    ],
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
