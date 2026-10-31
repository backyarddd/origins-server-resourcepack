"""Validate the server pack so a broken file can never ship: one bad JSON or texture fails every client's reload.

Checks, each failing with a readable AssertionError:
- every .json / .mcmeta under pack/ is strict JSON (UTF-8, no BOM, no NaN/Infinity);
- every assets/<ns>/bedrock/particles/**/<p>.particle.json: format_version 1.10.0, identifier exactly <ns>:<p>, an
  emitter rate and lifetime, a known material, events pointing at effects in the pack, and its texture resolved the way
  Cobblemon 1.8.1 does it (see README "Cosmetics") to a PNG in the pack whose size equals the billboard UV's
  texture_width x texture_height, with binary alpha;
- every model under assets/<ns>/models: parent, textures and override models exist in the pack or in the vanilla
  allowlist below; no override points back at its own model (the model baker would recurse); every texture a model
  uses is a 16x16 PNG (cosmetic models: a square 16..128 PNG) inside a blocks-atlas directory (vanilla block/ and
  item/, or a directory source in the pack's assets/minecraft/atlases/blocks.json), else it bakes as missing; cosmetic
  model textures must sit under a directory source the pack itself adds (cosmetic/), not a vanilla folder;
- every cosmetic model assets/origins/models/cosmetic/<id>.json (hats, back items, front items; one per id in HATS /
  BACKS / FRONTS): elements only, every cube corner inside -16..32, from <= to, rotations on one axis by
  -45/-22.5/0/22.5/45, every face uv inside 0..16 and its texture a variable defined in the model; front items also
  keep every (rotated) corner inside FRONT_BOX: on the chest, z <= 6.5 (at most 0.5 into the torso's front face);
- tool skin sets (TOOL_SETS): every set has all 19 TOOLSET_TEXTURES as a model origins:item/toolskin/<set>_<state>
  with the parent that holds it like the vanilla item and a 16x16 texture; and for each of the 64 item models (33
  vanilla + MOD_TOOL_ITEMS, 6 paxels and 25 hammers) every
  probe custom_model_data (none, below, each set, CATCH_ALL and above) x item properties (cast; pulling / pull at and
  between the vanilla thresholds; charged, firework) is resolved the way the 1.21.1 client does (last matching
  override wins, predicate values are >=) and must land on the set's texture for that state, or vanilla's;
- every Poke Ball variation file assets/<ns>/bedrock/poke_balls/variations/*.json: a ball Cobblemon ships, an order
  above Cobblemon's own set for that ball (later in the resolver's list wins, see README "Cosmetics"), every variation
  keyed on at least one aspect (an aspect-less variation would reskin the ball for everyone), its texture a PNG in the
  pack sized like its model's texture, its model and poser ids known to Cobblemon (cosmetics/cobblemon_balls.json,
  read from the Cobblemon jar by `python -I cosmetics/build.py --refresh-cobblemon <jar>`) or shipped in the pack;
  and every ball skin in BALL_SKINS has a variation on aspect origins_ball_<skin id> for every Cobblemon ball;
- menu icons (cosmetics/icons.py, check_icons): every icon_catalog.json id numbered in icons.json, numbers unique and
  contiguous from 7500001, one model origins:item/icon/<id> per id (flat types: item/generated + a 16x16 binary-alpha
  texture; tool skins: the set's pickaxe; hats / back / front items: the wearable model with a display.gui inside
  the client's clamps), and minecraft:item/knowledge_book with one override per id ascending then the catch-all to
  the plain look, every number resolving to its own icon.
  Aura / trail / sendout / victory icons: art at least 12 px, and no two of a type within 24 pixels of each other;
  every hand-drawn template (cosmetics/icon_art.ICONS) has its id in icons.json (no orphan templates).

Run:  python -I cosmetics/check.py [pack dir]   (default: pack/ next to this folder)
"""
import json
import math
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import items as server_items  # noqa: E402
from cosmetics import standins  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(os.path.dirname(HERE), 'pack')
COBBLEMON_BALLS = os.path.join(HERE, 'cobblemon_balls.json')
PNG_SIG = b'\x89PNG\r\n\x1a\n'
TIERS = ('wooden', 'stone', 'iron', 'golden', 'diamond', 'netherite')
TOOL_ITEMS = [f'{t}_{k}' for k in ('sword', 'pickaxe', 'axe', 'shovel', 'hoe') for t in TIERS] + ['fishing_rod', 'bow',
                                                                                                'crossbow']
# Modded tools the sets also skin (pinned: paxels 0.1.3, justhammers 21.1.4; models read from those jars): full id
NEW_STATES = ('paxel', 'hammer')
HAMMER_KINDS = ('hammer', 'reinforced_hammer', 'impact_hammer', 'reinforced_impact_hammer', 'destructor_hammer')
MOD_TOOL_ITEMS = [f'paxels:{t}_paxel' for t in TIERS] + [
    f'justhammers:{t}_{k}' for k in HAMMER_KINDS for t in ('stone', 'iron', 'gold', 'diamond', 'netherite')]
# tool skin sets (catalog v1.2): id -> custom_model_data; CATCH_ALL and up render the vanilla look again
TOOL_SETS = {'crystal': 73101, 'ember': 73102, 'gold': 73103, 'tidal': 73104, 'verdant': 73105, 'volt': 73106,
             'frost': 73107, 'shadow': 73108, 'mystic': 73109, 'dragon': 73110, 'celestial': 73111, 'pumpkin': 73112}
CATCH_ALL = 73113
# per item: its base state, then the vanilla 1.21.1 overrides in their vanilla order as (predicate, state). A state
# names the vanilla model and texture minecraft:item/<state> and a set's texture origins:item/toolskin/<set>_<state>
# (the tiered tools' base state is the tool type; their vanilla texture is the item itself)
ITEM_STATES = {
    'fishing_rod': ('fishing_rod', [({'cast': 1}, 'fishing_rod_cast')]),
    'bow': ('bow', [({'pulling': 1}, 'bow_pulling_0'), ({'pulling': 1, 'pull': 0.65}, 'bow_pulling_1'),
                    ({'pulling': 1, 'pull': 0.9}, 'bow_pulling_2')]),
    'crossbow': ('crossbow_standby', [({'pulling': 1}, 'crossbow_pulling_0'),
                                      ({'pulling': 1, 'pull': 0.58}, 'crossbow_pulling_1'),
                                      ({'pulling': 1, 'pull': 1.0}, 'crossbow_pulling_2'),
                                      ({'charged': 1}, 'crossbow_arrow'),
                                      ({'charged': 1, 'firework': 1}, 'crossbow_firework')]),
}
for _item in TOOL_ITEMS[:30]:
    ITEM_STATES[_item] = (_item.split('_', 1)[1], [])
for _item in MOD_TOOL_ITEMS:  # every hammer kind and tier shares one hammer design; the vanilla look is the item itself
    ITEM_STATES[_item] = ('paxel' if _item.startswith('paxels:') else 'hammer', [])
TOOLSET_TEXTURES = ('sword', 'pickaxe', 'axe', 'shovel', 'hoe') + tuple(
    s for item in ('fishing_rod', 'bow', 'crossbow') for s in [ITEM_STATES[item][0]] + [st for _, st in
                                                                                       ITEM_STATES[item][1]]
) + NEW_STATES
# the parent each set model needs so it is held like the vanilla item (bow / crossbow carry their own display)
TOOLSET_PARENT = {'fishing_rod': 'minecraft:item/handheld_rod', 'bow': 'minecraft:item/bow',
                  'crossbow': 'minecraft:item/crossbow'}
# vanilla 1.21.1 resources this pack may reference without shipping them (checked against the 1.21.1 client jar)
_VANILLA_STATES = [st for item in ('fishing_rod', 'bow', 'crossbow') for _, st in ITEM_STATES[item][1]]
VANILLA_MODELS = {'minecraft:item/' + n for n in ['generated', 'handheld', 'handheld_rod', 'paper'] + TOOL_ITEMS
                  + _VANILLA_STATES}


def vanilla_texture(item, state):
    """The vanilla texture of an item in a state (a tiered or modded tool's base texture is the item itself)."""
    if ':' in item:
        ns, name = item.split(':')
        return f'{ns}:item/{name}'
    return 'minecraft:item/' + (item if state == ITEM_STATES[item][0] and item in TOOL_ITEMS[:30] else state)


VANILLA_TEXTURES = {'minecraft:item/paper'} | {vanilla_texture(i, st) for i, (base, states) in ITEM_STATES.items()
                                               for st in [base] + [s for _, s in states]}
# The modded tools' base models and textures ship in the pinned mod jars (paxels 0.1.3, justhammers 21.1.4), not here.
VANILLA_MODELS |= {vanilla_texture(i, None) for i in MOD_TOOL_ITEMS}
# The armor stand-in models (standins.py) parent vanilla armor models and use the horse armor texture.
VANILLA_MODELS |= standins.vanilla_models()
VANILLA_TEXTURES |= standins.VANILLA_TEXTURES
# menu icons (cosmetics/icons.py): the base item and its plain look
ICON_ITEM = 'knowledge_book'
ICONS_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons.json')
ICON_CATALOG_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon_catalog.json')
ICON_DISTINCT_TYPES = ('aura', 'trail', 'sendout', 'victory')
ICON_MIN_MASK_DIFF = 24  # pixels two icons of one effect type must differ by
ICON_FIRST_CMD = 7500001
ICON_MODEL_PARENTS = {'tool_skin': 'origins:item/toolskin/{set}_pickaxe', 'hat': 'origins:cosmetic/{id}',
                      'back': 'origins:cosmetic/{id}', 'front': 'origins:cosmetic/{id}'}
VANILLA_TEXTURES.add('minecraft:item/' + ICON_ITEM)
# server-only items (items.py): the plain look of each base item
VANILLA_TEXTURES |= {'minecraft:item/' + base for _, base, _ in server_items.ITEMS}
RATES = ('minecraft:emitter_rate_instant', 'minecraft:emitter_rate_steady', 'minecraft:emitter_rate_manual')
LIFETIMES = ('minecraft:emitter_lifetime_once', 'minecraft:emitter_lifetime_looping',
             'minecraft:emitter_lifetime_expression')
MATERIALS = {'particles_alpha', 'particles_blend', 'particles_add', 'particles_opaque'}
# v1.1 client-mod cosmetics (catalog.md "v1.1"); the client draws origins:cosmetic/<id> / adds aspect BALL_ASPECT
HATS = ('hat_royal_crown', 'hat_top_hat', 'hat_origins_cap', 'hat_flower_crown', 'hat_golden_halo', 'hat_witch',
        # drop 2 (catalog-v2.md)
        'hat_party_hat', 'hat_propeller_cap', 'hat_cowboy', 'hat_chef', 'hat_viking', 'hat_wizard', 'hat_pirate',
        'hat_bunny_ears', 'hat_cat_ears', 'hat_traffic_cone', 'hat_beanie', 'hat_capsule_helmet')
BACKS = ('back_explorer_pack', 'back_feather_wings', 'back_ball_bandolier', 'back_bat_wings',
         'back_angel_wings', 'back_dragon_wings', 'back_jetpack', 'back_guitar', 'back_capsule_pack',
         'back_sword_sheath')
FRONTS = ('front_trainer_scarf', 'front_champion_medal', 'front_badge_sash', 'front_crystal_amulet',
          'front_ember_scarf', 'front_gold_bow_tie', 'front_pumpkin_pendant',
          'front_gold_chain', 'front_baby_bib', 'front_capsule_pendant', 'front_heart_locket', 'front_star_medal',
          'front_flower_lei')
# front items sit on the chest: the torso's front face is z = 6 (contract), a model may sink into it by 0.5 at most
FRONT_MAX_Z = 6.5
FRONT_BOX = ((2, 14), (-14, 1), (2, FRONT_MAX_Z))  # x, y, z range every (rotated) corner must stay inside
BALL_SKINS = ('ball_galaxy', 'ball_gilded', 'ball_crystal', 'ball_ember', 'ball_sakura', 'ball_pumpkin',
              'ball_neon', 'ball_lava', 'ball_ocean', 'ball_camo', 'ball_checker', 'ball_candy', 'ball_marble',
              'ball_toxic', 'ball_holo', 'ball_watermelon')
BALL_ASPECT = 'origins_ball_{}'
VANILLA_BLOCK_ATLAS_DIRS = ('block/', 'item/')  # directory sources of the 1.21.1 minecraft:blocks atlas we rely on
ANGLES = (-45, -22.5, 0, 22.5, 45)
FACE_NAMES = ('north', 'south', 'west', 'east', 'up', 'down')
COSMETIC_SIZES = {(n, n) for n in (16, 32, 64, 128)}


def _no_constant(name):
    raise ValueError(f'{name} is not valid JSON')


def load(path, pack):
    rel = os.path.relpath(path, pack).replace(os.sep, '/')
    with open(path, 'rb') as f:
        raw = f.read()
    try:
        return json.loads(raw.decode('utf-8'), parse_constant=_no_constant)
    except (UnicodeDecodeError, ValueError) as e:
        raise AssertionError(f'invalid JSON {rel}: {e}') from None


def rid(ref):
    return ref if ':' in ref else 'minecraft:' + ref


def res(pack, ref, kind, ext):
    ns, path = rid(ref).split(':', 1)
    return os.path.join(pack, 'assets', ns, kind, *path.split('/')) + ext


def png(path, pack, size, what):
    """size: (w, h), a set of allowed (w, h), or None for any size."""
    rel = os.path.relpath(path, pack).replace(os.sep, '/')
    assert os.path.isfile(path), f'{what}: missing texture {rel}'
    with open(path, 'rb') as f:
        assert f.read(8) == PNG_SIG, f'{what}: {rel} is not a PNG'
    try:
        with Image.open(path) as im:
            im.load()
            got, alpha = im.size, set(im.convert('RGBA').getchannel('A').tobytes())
    except OSError as e:
        raise AssertionError(f'{what}: {rel} is not a readable PNG: {e}') from None
    allowed = size if isinstance(size, set) else {size}
    assert size is None or got in allowed, (f'{what}: {rel} is {got[0]}x{got[1]}, expected '
                                            + ' or '.join(f'{w}x{h}' for w, h in sorted(allowed)))
    assert alpha <= {0, 255}, f'{what}: {rel} has non-binary alpha'


def particle_texture(texture):
    """Cobblemon 1.8.1 SnowstormParticleReader.loadEffect: drop '.png', remove every 'particles/' and 'textures/',
    lowercase, default namespace cobblemon; the result is a sprite id in the particle atlas (textures/particle/)."""
    t = texture[:-4] if texture.endswith('.png') else texture
    t = t.replace('particles/', '').replace('textures/', '').lower()
    return t if ':' in t else 'cobblemon:' + t


def check_json(pack):
    n = 0
    for d, _, names in os.walk(pack):
        for name in names:
            if name.endswith(('.json', '.mcmeta')):
                load(os.path.join(d, name), pack)
                n += 1
    return n


def collect(pack, folder, suffix):
    """{'<ns>:<path without suffix>': file} for every file under assets/<ns>/<folder> ending in suffix."""
    found = {}
    assets = os.path.join(pack, 'assets')
    for ns in sorted(os.listdir(assets)) if os.path.isdir(assets) else []:
        root = os.path.join(assets, ns, *folder.split('/'))
        for d, _, names in os.walk(root):
            for name in names:
                if name.endswith(suffix):
                    rel = os.path.relpath(os.path.join(d, name), root).replace(os.sep, '/')[:-len(suffix)]
                    found[f'{ns}:{rel}'] = os.path.join(d, name)
    return found


def each(items, fn, *args):
    for key, path in sorted(items.items()):
        try:
            fn(key, path, *args)
        except (KeyError, TypeError, AttributeError, IndexError, ValueError) as e:
            # a structurally wrong file (missing key, wrong type) must fail as cleanly as a wrong value
            raise AssertionError(f'{key}: malformed ({type(e).__name__}: {e})') from None


def particle(eid, path, pack, effects):
    data = load(path, pack)
    assert data.get('format_version') == '1.10.0', f'{eid}: format_version must be "1.10.0"'
    pe = data['particle_effect']
    desc, comps, events = pe['description'], pe['components'], pe.get('events', {})
    assert desc.get('identifier') == eid, f'{eid}: identifier {desc.get("identifier")!r} does not match its path'
    brp = desc['basic_render_parameters']
    assert brp.get('material') in MATERIALS, f'{eid}: unknown material {brp.get("material")!r}'
    assert any(k in comps for k in RATES), f'{eid}: no emitter rate component'
    assert any(k in comps for k in LIFETIMES), f'{eid}: no emitter lifetime component'
    uv = comps.get('minecraft:particle_appearance_billboard', {}).get('uv')
    assert uv, f'{eid}: billboard needs a uv block with texture_width / texture_height'
    tw, th = uv['texture_width'], uv['texture_height']
    cell = uv['flipbook']['size_UV'] if 'flipbook' in uv else uv['uv_size']
    assert tw % cell[0] == 0 and th % cell[1] == 0, f'{eid}: uv cell {cell} does not divide {tw}x{th}'
    sprite = particle_texture(brp['texture'])
    png(res(pack, sprite, 'textures/particle', '.png'), pack, (tw, th), f'{eid} texture {sprite}')
    for name, ev in events.items():
        if 'particle_effect' in ev:
            child = rid(ev['particle_effect']['effect'])
            assert child in effects, f'{eid}: event {name} spawns missing effect {child}'
    for key, name in comps.get('minecraft:emitter_lifetime_events', {}).items():
        if key.endswith('_event'):
            assert name in events, f'{eid}: lifetime event {name!r} is not defined in events'


def atlas_dirs(pack):
    """Directory prefixes the pack's assets/minecraft/atlases/blocks.json adds to minecraft:blocks (atlas files from
    every pack are merged, so these come on top of vanilla's block/ and item/)."""
    dirs = []
    path = os.path.join(pack, 'assets', 'minecraft', 'atlases', 'blocks.json')
    if os.path.isfile(path):
        for src in load(path, pack)['sources']:
            if src.get('type') == 'directory':
                assert src.get('prefix') == src['source'].rstrip('/') + '/', \
                    f'atlases/blocks.json: directory {src["source"]!r} needs prefix {src["source"]}/ so sprite ids ' \
                    f'match texture paths'
                dirs.append(src['prefix'])
    return tuple(dirs)


def model(mid, path, pack, known, textures, atlas):
    data = load(path, pack)
    if 'parent' in data and not data['parent'].startswith('builtin/'):
        assert rid(data['parent']) in known, f'model {mid}: parent {data["parent"]} not found'
    cosmetic = mid.startswith('origins:cosmetic/')
    for key, ref in data.get('textures', {}).items():
        if not ref.startswith('#') and rid(ref) not in VANILLA_TEXTURES:
            png(res(pack, ref, 'textures', '.png'), pack, COSMETIC_SIZES if cosmetic else (16, 16),
                f'model {mid} texture {key}')
            where = atlas if cosmetic else VANILLA_BLOCK_ATLAS_DIRS + atlas
            assert rid(ref).split(':', 1)[1].startswith(where), \
                f'model {mid}: texture {ref} is outside the blocks atlas directories ' \
                f'{", ".join(where) or "(none: no assets/minecraft/atlases/blocks.json directory source)"}' \
                f', it would bake as missing'
            textures.add(rid(ref))
    if cosmetic:
        cosmetic_model(mid, data)
    for o in data.get('overrides', []):
        target = rid(o['model'])
        assert target != mid, f'model {mid}: override points at itself'
        assert target in known, f'model {mid}: override {o["predicate"]} -> missing model {o["model"]}'


def num(v, what):
    assert isinstance(v, (int, float)) and not isinstance(v, bool), f'{what}: {v!r} is not a number'
    return v


def cosmetic_model(mid, data):
    """Hats / back items: a vanilla elements model the client bakes and draws on the head or body bone."""
    assert 'parent' not in data, f'model {mid}: cosmetic models stand alone (no parent)'
    elements = data.get('elements')
    assert isinstance(elements, list) and elements, f'model {mid}: needs a non-empty elements list'
    variables = set(data.get('textures', {}))
    for n, e in enumerate(elements):
        what = f'model {mid} element {n}'
        frm, to = e['from'], e['to']
        assert len(frm) == 3 and len(to) == 3, f'{what}: from / to need 3 coordinates'
        for a, b in zip(frm, to):
            assert -16 <= num(a, what) <= 32 and -16 <= num(b, what) <= 32, \
                f'{what}: cube {frm}..{to} leaves the -16..32 model bounds'
            assert a <= b, f'{what}: from {frm} must not exceed to {to}'
        if 'rotation' in e:
            r = e['rotation']
            assert r.get('axis') in ('x', 'y', 'z'), f'{what}: rotation axis must be x, y or z'
            assert r.get('angle') in ANGLES, f'{what}: rotation angle {r.get("angle")} not one of {ANGLES}'
            assert len(r['origin']) == 3 and all(num(c, what) == c for c in r['origin']), f'{what}: bad origin'
        assert e.get('faces'), f'{what}: no faces'
        for face, f in e['faces'].items():
            assert face in FACE_NAMES, f'{what}: unknown face {face!r}'
            uv = f['uv']
            assert len(uv) == 4 and all(0 <= num(c, what) <= 16 for c in uv), f'{what} {face}: uv {uv} outside 0..16'
            tex = f['texture']
            assert tex.startswith('#') and tex[1:] in variables, f'{what} {face}: texture {tex} is not defined'


def load_cobblemon():
    assert os.path.isfile(COBBLEMON_BALLS), (f'missing {COBBLEMON_BALLS}; run python -I cosmetics/build.py '
                                             f'--refresh-cobblemon <Cobblemon jar>')
    with open(COBBLEMON_BALLS, encoding='utf-8') as f:
        data = json.load(f)
    assert data['balls'] and data['models'] and data['posers'], 'cobblemon_balls.json is incomplete'
    return data


def ball_variations(vid, path, pack, cob, models, posers, covered):
    data = load(path, pack)
    ball = data.get('pokeball', data.get('species', data.get('name')))
    assert ball in cob['balls'], f'ball variation {vid}: {ball!r} is not a Poke Ball Cobblemon ships'
    base = cob['balls'][ball]
    order = data['order']
    assert isinstance(order, int) and not isinstance(order, bool) and order > base['order'], \
        f'ball variation {vid}: order {order!r} must be an int above Cobblemon\'s {base["order"]} for {ball}, or ' \
        f'Cobblemon\'s own texture wins'
    assert isinstance(data['variations'], list) and data['variations'], f'ball variation {vid}: no variations'
    for n, v in enumerate(data['variations']):
        what = f'ball variation {vid} #{n}'
        aspects = v['aspects']
        assert isinstance(aspects, list) and aspects and all(isinstance(a, str) and a for a in aspects), \
            f'{what}: needs at least one aspect, or it reskins {ball} for every player'
        model_id = v.get('model', base['model'])
        assert model_id in models, f'{what}: model {model_id} is neither in Cobblemon nor in the pack'
        poser = v.get('poser', base['poser'])
        assert poser in posers, f'{what}: poser {poser} is neither in Cobblemon nor in the pack'
        tex = v['texture']
        assert isinstance(tex, str) and ':' in tex and tex.split(':', 1)[1].startswith('textures/') and \
            tex.endswith('.png'), f'{what}: texture {tex!r} must be a full <ns>:textures/....png path'
        ns, rel = tex.split(':', 1)
        png(os.path.join(pack, 'assets', ns, *rel.split('/')), pack, models[model_id], f'{what} texture')
        covered.add((ball, tuple(aspects)))


# tool skins: every (custom_model_data, item property) combination the client can see must pick the right texture
PROBE_CMD = [None, 1, TOOL_SETS['crystal'] - 1] + sorted(TOOL_SETS.values()) + [CATCH_ALL, CATCH_ALL + 7]
PROBE_PROPS = {
    'fishing_rod': [{}, {'cast': 1}],
    'bow': [{}, {'pull': 0.95}] + [{'pulling': 1, 'pull': p} for p in (0, 0.3, 0.65, 0.7, 0.9, 0.95, 1)],
    'crossbow': [{}, {'pull': 1}] + [{'pulling': 1, 'pull': p} for p in (0, 0.3, 0.58, 0.6, 0.99, 1)]
    + [{'charged': 1}, {'charged': 1, 'firework': 1}, {'firework': 1}],
}


def matches(predicate, props):
    """ItemOverride.test (1.21.1): every predicate property must be >= its threshold; an unset property is 0."""
    return all(props.get(k, 0) >= v for k, v in predicate.items())


def resolve(overrides, props):
    """ItemOverrides.resolve (1.21.1): the overrides are tested last to first and the first match wins."""
    for o in reversed(overrides):
        if matches(o['predicate'], props):
            return rid(o['model'])
    return None


def layer0(mid, pack, seen=()):
    """The layer0 texture a model ends up with: its own, else its parent's (vanilla models: their own name)."""
    path = res(pack, mid, 'models', '.json')
    if not os.path.isfile(path):
        assert mid in VANILLA_MODELS, f'model {mid} is neither in the pack nor a known vanilla model'
        return mid
    assert mid not in seen, f'model {mid}: parent loop'
    data = load(path, pack)
    if 'layer0' in data.get('textures', {}):
        return rid(data['textures']['layer0'])
    assert 'parent' in data, f'model {mid}: no layer0 texture anywhere in its parents'
    return layer0(rid(data['parent']), pack, seen + (mid,))


def expected_state(item, props):
    base, states = ITEM_STATES[item]
    picked = base
    for predicate, state in states:  # vanilla order, the last match wins
        if matches(predicate, props):
            picked = state
    return picked


def check_toolsets(pack, models):
    """Every set has all its models + 16x16 textures with the right parent; then every item model is resolved for
    every probe custom_model_data x item properties combination and must show the expected set or vanilla texture."""
    for s in TOOL_SETS:
        for state in TOOLSET_TEXTURES:
            mid = f'origins:item/toolskin/{s}_{state}'
            assert mid in models, f'tool set {s}: missing model {mid} (every set needs all {len(TOOLSET_TEXTURES)})'
            data = load(models[mid], pack)
            kind = next((k for k in TOOLSET_PARENT if state.startswith(k)), None)
            want = TOOLSET_PARENT.get(kind, 'minecraft:item/handheld')
            assert rid(data.get('parent', '')) == want, f'model {mid}: parent must be {want} to be held right'
            tex = f'origins:item/toolskin/{s}_{state}'
            assert rid(data.get('textures', {}).get('layer0', '')) == tex, f'model {mid}: layer0 must be {tex}'
            png(res(pack, tex, 'textures', '.png'), pack, (16, 16), f'tool set {s} texture {state}')
    cases = 0
    for item in TOOL_ITEMS + MOD_TOOL_ITEMS:
        ns, name = rid(item).split(':')
        mid = f'{ns}:item/{name}'
        assert mid in models, f'missing item model assets/{ns}/models/item/{name}.json'
        data = load(models[mid], pack)
        overrides = data.get('overrides', [])
        if ':' in item:  # modded: the pinned jar's base model exactly, here and in the catch-all copy
            base = {'parent': 'minecraft:item/handheld',
                    'textures': {'layer0': vanilla_texture(item, ITEM_STATES[item][0])}}
            assert {k: v for k, v in data.items() if k != 'overrides'} == base, \
                f'item model {mid}: must be the jar base model {base} plus overrides'
            copy = f'origins:item/toolskin/vanilla/{ns}/{name}'
            assert copy in models, f'item {item}: missing catch-all copy {copy}'
            assert load(models[copy], pack) == base, f'model {copy}: must be exactly the jar base model {base}'
        for cmd in PROBE_CMD:
            for props in PROBE_PROPS.get(item, [{}]):
                full = dict(props, **({} if cmd is None else {'custom_model_data': cmd}))
                state = expected_state(item, props)
                owner = [k for k, v in TOOL_SETS.items() if cmd is not None and v <= cmd < CATCH_ALL]
                want = (f'origins:item/toolskin/{max(owner, key=TOOL_SETS.get)}_{state}' if owner
                        else vanilla_texture(item, state))
                got_model = resolve(overrides, full) or mid
                got = layer0(got_model, pack)
                assert got == want, (f'item {item} with {full}: overrides pick {got_model} ({got}), expected the '
                                     f'texture {want}')
                cases += 1
    return cases


def front_model(mid, data):
    """Front items: every cube corner (after its rotation) inside FRONT_BOX, i.e. on the chest, at most 0.5 into it."""
    for n, e in enumerate(data['elements']):
        corners = [(x, y, z) for x in (e['from'][0], e['to'][0]) for y in (e['from'][1], e['to'][1])
                   for z in (e['from'][2], e['to'][2])]
        r = e.get('rotation')
        if r:
            a = math.radians(r['angle'])
            c, sn = math.cos(a), math.sin(a)
            o = r['origin']
            out = []
            for p in corners:
                x, y, z = (p[k] - o[k] for k in range(3))
                x, y, z = {'x': (x, y * c - z * sn, y * sn + z * c), 'y': (x * c + z * sn, y, -x * sn + z * c),
                           'z': (x * c - y * sn, x * sn + y * c, z)}[r['axis']]
                out.append((x + o[0], y + o[1], z + o[2]))
            corners = out
        for p in corners:
            for k, axis in enumerate('xyz'):
                lo, hi = FRONT_BOX[k]
                assert lo - 1e-6 <= p[k] <= hi + 1e-6, (
                    f'model {mid} element {n}: corner {axis} = {p[k]:g} leaves the chest box {lo}..{hi} '
                    f'(front items sit on the torso front, z <= {FRONT_MAX_Z})')


def check_icons(pack, models):
    """Menu icons: icons.json numbering (contiguous from ICON_FIRST_CMD, unique, every catalog id present), one model
    per id (flat types: item/generated + a 16x16 binary-alpha texture origins:item/icon/<id>; tool skins: the set's
    pickaxe; hats / back / front items: the wearable model with a display.gui), and the knowledge_book overrides: one
    per id in ascending custom_model_data, then the catch-all to the plain look; every number resolves to its icon."""
    with open(ICONS_JSON, encoding='utf-8') as f:
        icons = json.load(f)
    with open(ICON_CATALOG_JSON, encoding='utf-8') as f:
        catalog = json.load(f)
    missing = sorted(set(catalog) - set(icons))
    assert not missing, f'icons.json: no number for {", ".join(missing)} (run cosmetics/icons.py --refresh-catalog)'
    from cosmetics import icon_art  # lazy: icon_art -> icons -> this module
    orphans = sorted(set(icon_art.ICONS) - set(icons))
    assert not orphans, f'cosmetics/icon_art*.py: templates for ids not in icons.json: {", ".join(orphans)}'
    cmds = sorted(e['cmd'] for e in icons.values())
    assert cmds == list(range(ICON_FIRST_CMD, ICON_FIRST_CMD + len(icons))),         f'icons.json: custom_model_data must be unique and contiguous from {ICON_FIRST_CMD}'
    sets = {v: k for k, v in TOOL_SETS.items()}
    masks = {}
    for cid, e in icons.items():
        mid = f'origins:item/icon/{cid}'
        assert mid in models, f'icon {cid}: missing model {mid}'
        data = load(models[mid], pack)
        kind = e['type']
        assert catalog[cid]['type'] == kind, f'icon {cid}: type {kind} differs from the catalog'
        if kind in ICON_MODEL_PARENTS:
            want = ICON_MODEL_PARENTS[kind].format(id=cid, set=sets.get(catalog[cid].get('custom_model_data')))
            assert data.get('parent') == want and want in models, f'icon {cid}: parent must be {want}'
            if kind != 'tool_skin':
                gui = data['display']['gui']
                assert all(len(gui[k]) == 3 for k in ('rotation', 'translation', 'scale')), f'icon {cid}: bad gui'
                assert all(-80 <= v <= 80 for v in gui['translation']) and all(0 < v <= 4 for v in gui['scale']),                     f'icon {cid}: gui translation / scale outside the client clamp'
        else:
            assert data == {'parent': 'minecraft:item/generated', 'textures': {'layer0': mid}},                 f'icon {cid}: must be item/generated with layer0 {mid}'
            png(res(pack, mid, 'textures', '.png'), pack, (16, 16), f'icon {cid}')
            if kind in ICON_DISTINCT_TYPES:  # hand-drawn effect icons: readable, and no two of a type alike
                with Image.open(res(pack, mid, 'textures', '.png')) as im:
                    alpha = im.convert('RGBA').getchannel('A')
                box = alpha.getbbox()
                assert box and max(box[2] - box[0], box[3] - box[1]) >= 12, f'icon {cid}: art smaller than 12 px'
                masks.setdefault(kind, []).append((cid, {i for i, a in enumerate(alpha.tobytes()) if a}))
    for kind, ms in masks.items():
        for i, (a, ma) in enumerate(ms):
            for b, mb in ms[i + 1:]:
                assert len(ma ^ mb) >= ICON_MIN_MASK_DIFF, f'icons {a} and {b}: shapes too alike (same layout)'
    base = f'minecraft:item/{ICON_ITEM}'
    assert base in models, f'missing assets/minecraft/models/item/{ICON_ITEM}.json'
    data = load(models[base], pack)
    assert data.get('parent') == 'minecraft:item/generated' and data.get('textures') == {'layer0': base},         f'{base}: must keep the vanilla parent and texture'
    order = sorted(icons, key=lambda c: icons[c]['cmd'])
    plain = f'origins:item/icon/plain_{ICON_ITEM}'
    want = [{'predicate': {'custom_model_data': icons[c]['cmd']}, 'model': f'origins:item/icon/{c}'} for c in order]
    want.append({'predicate': {'custom_model_data': cmds[-1] + 1}, 'model': plain})
    assert data.get('overrides') == want, f'{base}: overrides must be one per icon ascending, then the catch-all'
    assert layer0(plain, pack) == base, f'{plain}: must show the vanilla {ICON_ITEM}'
    for c in order:  # replay the client: each number resolves to its own icon, neighbours and the catch-all too
        assert resolve(want, {'custom_model_data': icons[c]['cmd']}) == f'origins:item/icon/{c}', c
    assert resolve(want, {'custom_model_data': ICON_FIRST_CMD - 1}) is None
    assert resolve(want, {'custom_model_data': cmds[-1] + 50}) == plain
    return len(icons)


def check(pack=PACK):
    n_json = check_json(pack)
    effects = collect(pack, 'bedrock/particles', '.particle.json')
    each(effects, particle, pack, effects)
    models, textures = collect(pack, 'models', '.json'), set()
    each(models, model, pack, set(models) | VANILLA_MODELS, textures, atlas_dirs(pack))
    for cid in HATS + BACKS + FRONTS:
        assert f'origins:cosmetic/{cid}' in models, \
            f'cosmetic {cid}: missing model assets/origins/models/cosmetic/{cid}.json'
    for cid in FRONTS:
        front_model(f'origins:cosmetic/{cid}', load(models[f'origins:cosmetic/{cid}'], pack))
    cases = check_toolsets(pack, models)
    cob = load_cobblemon()
    geo = {mid: tuple(m['texture']) for mid, m in cob['models'].items()}
    # a geometry shipped in the pack: its texture size is not checked (no geo parser here)
    geo.update({k: None for k in collect(pack, 'bedrock/poke_balls/models', '.json')})
    posers = set(cob['posers']) | set(collect(pack, 'bedrock/poke_balls/posers', '.json'))
    variations, covered = collect(pack, 'bedrock/poke_balls/variations', '.json'), set()
    each(variations, ball_variations, pack, cob, geo, posers, covered)
    for skin in BALL_SKINS:
        for ball in sorted(cob['balls']):
            assert (ball, (BALL_ASPECT.format(skin),)) in covered, \
                f'ball skin {skin}: no variation for {ball} on aspect {BALL_ASPECT.format(skin)}'
    n_icons = check_icons(pack, models)
    errs = standins.check(pack)
    assert not errs, '; '.join(errs)
    print(f'ok  {n_json} json files, {len(effects)} particle effects, {len(models)} models, '
          f'{len(textures)} model textures, {len(TOOL_SETS)} tool sets ({cases} override cases), '
          f'{len(variations)} ball variation sets ({len(covered)} skin x ball), {n_icons} menu icons')


if __name__ == '__main__':
    try:
        check(sys.argv[1] if len(sys.argv) > 1 else PACK)
    except AssertionError as e:
        sys.exit(f'FAIL: {e}')
