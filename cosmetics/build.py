"""Generate the cosmetics assets into pack/: particle sprites + Snowstorm effects, the 12 tool skin sets (17 textures +
models each, art in cosmetics/toolsets.py), the 33 vanilla item models (30 tiered tools, fishing rod, bow, crossbow)
with custom_model_data overrides, hat / back / front item models + textures (and the blocks atlas source they need),
Poke Ball skin textures + one variation set per Cobblemon ball, and the preview sheets in cosmetics/preview/.

Refresh the Cobblemon ball list after a Cobblemon update (writes cosmetics/cobblemon_balls.json):
    python -I cosmetics/build.py --refresh-cobblemon <path to Cobblemon-fabric-*.jar>

Called by the root build.py (build(pack, write_json)); the catalog (ids, colours, looks) is
packdev/server/specs/origins-cosmetics/catalog.md. All art is drawn in cosmetics/art.py.
"""
import hashlib
import json
import math
import os
import shutil
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from cosmetics import art, toolsets  # noqa: E402
from cosmetics.art import CREAM, GOLD, LIGHT_GOLD, NAVY, hexrgb, shades  # noqa: E402
from cosmetics.check import (BACKS, BALL_ASPECT, BALL_SKINS, CATCH_ALL, COBBLEMON_BALLS, FRONTS, HATS,  # noqa: E402
                             ITEM_STATES, TOOL_ITEMS, TOOL_SETS, TOOLSET_PARENT, TOOLSET_TEXTURES, load_cobblemon,
                             vanilla_texture)

PREVIEW = os.path.join(ROOT, 'cosmetics', 'preview')
NS = 'origins'

FADE = '1 - math.pow(v.particle_age / v.particle_lifetime, 2)'
AGE = 'v.particle_age / v.particle_lifetime'


def twinkle(s):
    return f'{s} * math.sin(180 * {AGE})'


def shrink(s):
    return f'{s} * (1 - 0.6 * {AGE})'


def grow(s):
    return f'{s} * (0.7 + 0.6 * {AGE})'


def pal(**roles):
    return {k: hexrgb(v) if isinstance(v, str) else v for k, v in roles.items()}


# palettes (role -> colour); gold accents use the Origins palette
P_GOLD = pal(O='#7A5313', M=GOLD, L=LIGHT_GOLD, W=CREAM, X=NAVY)
P_WHITE_STAR = pal(O='#9AA6C4', M='#DDE6FF', L='#DDE6FF', W='#FFFFFF', X='#FFFFFF')
P_GOLD_STAR = pal(O='#B07A22', M=GOLD, L=LIGHT_GOLD, W=CREAM, X=CREAM)
P_YELLOW = shades('#FFE14D', light='#FFF6B0', dark='#C99A12')
P_ORANGE = shades('#FF7A1A', light='#FFC04D', dark='#B32A0A')
P_RED_ORANGE = shades('#E8401C', light='#FF9A3D', dark='#7A1405')
P_CYAN_FIRE = shades('#3FE0E0', light='#B3FFFF', dark='#0E7C8C')
P_CYAN_FIRE2 = shades('#2BB8D8', light='#8EF2FF', dark='#0A5566')
P_ICE = shades('#9FD8FF', light='#E3F5FF', dark='#4F8FC0')
P_ICE2 = shades('#C6E8FF', light='#FFFFFF', dark='#6FA6CF')
P_SNOW = pal(O='#C9DDF0', M='#F2F8FF', L='#FFFFFF', W='#FFFFFF', X='#FFFFFF')
P_PINK = shades('#FF9CC7', light='#FFD1E6', dark='#C2507F')
P_PINK2 = shades('#F772A8', light='#FFB8D6', dark='#A33A66')
P_SHADOW = shades('#5A2A7A', light='#8A55A8', dark='#24102F')
P_SHADOW2 = shades('#3D1F55', light='#6B3E8C', dark='#1A0B24')
P_VOID = shades('#7A3DB8', light='#B07FE8', dark='#14081F')
P_BAT = pal(O='#1A1420', M='#3A2E48', X='#FF4A3D')
P_BLUE_FIRE = shades('#3D7BFF', light='#9CC2FF', dark='#16337A')
P_GREEN_STAR = pal(O='#2E8B57', M='#4FD67A', L='#4FD67A', W='#C8FFD9', X='#C8FFD9')
P_LEAF = shades('#5DBB4A', light='#9BE07F', dark='#2E6B24')
P_LEAF2 = shades('#3F9A3A', light='#7CCB62', dark='#1F4F1C')
P_BUBBLE = pal(O='#7FD4FF', L='#FFFFFF', W='#FFFFFF')
P_PUMPKIN = pal(O='#7A3500', M='#F07A12', L='#FF9F3D', W='#FFD84D', X='#3E7A1E')
RAINBOW = ['#FF5555', '#FFAA33', '#FFE066', '#7BD88F', '#55E6E6', '#A37BFF']


def frames(*pairs):
    return [art.sprite(t, p) for t, p in pairs]


def box(half, y, direction='outwards'):
    return {'minecraft:emitter_shape_box': {'offset': [0, y, 0], 'half_dimensions': half, 'direction': direction}}


def sphere(radius, y, direction='outwards', surface=False):
    return {'minecraft:emitter_shape_sphere': {'offset': [0, y, 0], 'radius': radius, 'surface_only': surface,
                                               'direction': direction}}


def disc(radius, y, direction, surface=False):
    return {'minecraft:emitter_shape_disc': {'offset': [0, y, 0], 'radius': radius, 'surface_only': surface,
                                             'direction': direction}}


def point(offset, direction=None):
    body = {'offset': offset}
    if direction:
        body['direction'] = direction
    return {'minecraft:emitter_shape_point': body}


SPIN = ('math.random(0, 360)', 'math.random(-90, 90)')

# id -> frames + behaviour. kind comes from the id prefix (aura looping on the Pokemon; the rest one-shot bursts).
# rate = particles/s (auras) or burst count; life = (min, max) seconds; size = billboard size (number or MoLang).
EFFECTS = {
    'aura_ember_wisps': dict(frames=frames((art.FLAME, P_ORANGE), (art.FLAME, P_RED_ORANGE)), rate=7,
                             shape=box([0.5, 0.5, 0.5], 0.5, [0, 1, 0]), life=(1.0, 1.4), size=shrink(0.2),
                             speed=0.2, accel=[0, 0.8, 0], drag=0.5),
    'aura_frost_motes': dict(frames=frames((art.FLAKE, P_ICE), (art.FLAKE, P_ICE2)), rate=5,
                             shape=box([0.55, 0.55, 0.55], 0.6), life=(1.6, 2.0), size=0.16, speed=0.15,
                             accel=[0, -0.15, 0], drag=1, spin=SPIN),
    'aura_static_field': dict(frames=frames((art.ZAP, P_YELLOW), (art.SPARK, P_YELLOW)), rate=9,
                              shape=box([0.4, 0.45, 0.4], 0.5), life=(0.8, 1.0),
                              size='0.16 * (0.7 + 0.3 * math.sin(v.particle_age * 2000))', speed=0.3, drag=3,
                              spin=('math.random_integer(0, 3) * 90', 0)),
    'aura_petal_drift': dict(frames=frames((art.PETAL, P_PINK), (art.PETAL, P_PINK2)), rate=5,
                             shape=box([0.6, 0.25, 0.6], 1.0, [0, -1, 0]), life=(1.6, 2.0), size=0.15, speed=0.1,
                             accel=['math.cos(v.particle_age * 180 + v.particle_random_3 * 360) * 0.6', -0.35,
                                    'math.sin(v.particle_age * 180 + v.particle_random_3 * 360) * 0.6'],
                             drag=1, spin=SPIN),
    'aura_shadow_smoke': dict(frames=frames((art.SMOKE, P_SHADOW), (art.SMOKE, P_SHADOW2)), rate=6,
                              shape=box([0.5, 0.45, 0.5], 0.5, [0, 1, 0]), life=(1.2, 1.8), size=grow(0.18),
                              speed=0.1, accel=[0, 0.25, 0], drag=1, spin=('math.random(0, 360)', 0)),
    'aura_starlight': dict(frames=frames((art.STAR, P_WHITE_STAR), (art.STAR, P_GOLD_STAR)), rate=6,
                           shape=box([0.6, 0.6, 0.6], 0.6), life=(1.0, 1.6), size=twinkle(0.2), speed=0.05),
    'aura_ghost_flames': dict(frames=frames((art.FLAME, P_CYAN_FIRE), (art.FLAME, P_CYAN_FIRE2)), rate=7,
                              shape=box([0.5, 0.5, 0.5], 0.5, [0, 1, 0]), life=(1.0, 1.4), size=shrink(0.2),
                              speed=0.2, accel=[0, 0.7, 0], drag=0.5),
    # one lap per emitter loop (active_time 1 s), so the ring keeps turning seamlessly
    'aura_season_halo': dict(frames=frames((art.STAR, P_GOLD_STAR), (art.SPARK, P_GOLD_STAR)), rate=10, max=24,
                             shape=point(['math.sin(v.emitter_age * 360) * 0.6', 1.45,
                                          'math.cos(v.emitter_age * 360) * 0.6']),
                             life=(1.6, 2.0), size=twinkle(0.16), speed=0),

    'sendout_thunderclap': dict(frames=frames((art.ZAP, P_YELLOW), (art.SPARK, P_YELLOW)), rate=28,
                                shape=sphere(0.25, 0.5), life=(0.4, 0.8), size=0.22, speed=5, drag=4,
                                spin=('math.random_integer(0, 3) * 90', 0)),
    'sendout_petal_burst': dict(frames=frames((art.PETAL, P_PINK), (art.PETAL, P_PINK2)), rate=30,
                                shape=sphere(0.3, 0.5), life=(1.0, 1.5), size=0.16, speed=4, accel=[0, -1.5, 0],
                                drag=3, spin=SPIN),
    'sendout_snow_flurry': dict(frames=frames((art.FLAKE, P_SNOW), (art.SMOKE, P_SNOW)), rate=30,
                                shape=sphere(0.3, 0.5), life=(1.0, 1.5), size=0.2, speed=3, accel=[0, -0.6, 0],
                                drag=3, spin=SPIN),
    'sendout_confetti_pop': dict(frames=frames(*[(art.CONFETTI, shades(c)) for c in RAINBOW]), rate=40,
                                 shape=sphere(0.2, 0.4, ['math.random(-1, 1)', 'math.random(0.8, 1.6)',
                                                         'math.random(-1, 1)']),
                                 life=(1.2, 1.8), size=0.12, speed=6, accel=[0, -4, 0], drag=3,
                                 spin=('math.random(0, 360)', 'math.random(-360, 360)')),
    'sendout_void_rift': dict(frames=frames((art.SMOKE, P_VOID), (art.CIRCLE, P_VOID)), rate=32,
                              shape=sphere(1.6, 0.6, 'inwards', surface=True), life=(0.45, 0.5), size=shrink(0.25),
                              speed=3.2, spin=('math.random(0, 360)', 360)),
    'sendout_gold_rush': dict(frames=frames((art.COIN, P_GOLD), (art.STAR, P_GOLD_STAR)), rate=30,
                              shape=sphere(0.3, 0.5), life=(1.0, 1.6), size=0.16, speed=4, accel=[0, -3, 0], drag=3,
                              spin=SPIN),
    'sendout_bat_swarm': dict(frames=frames((art.BAT, P_BAT)), rate=16, shape=sphere(0.3, 0.6), life=(1.2, 1.6),
                              size=['0.25 * (0.7 + 0.3 * math.sin(v.particle_age * 1800))', 0.2], speed=3.5,
                              accel=[0, 1.5, 0], drag=1),

    'victory_fireworks': dict(frames=frames(*[(art.STAR, shades(c, light='#FFFFFF')) for c in RAINBOW[::2]],
                                            (art.STAR, P_GOLD_STAR)),
                              rate=40, shape=sphere(0.2, 2.6), life=(1.0, 1.6), size=shrink(0.16), speed=5,
                              accel=[0, -1.2, 0], drag=3.5),
    'victory_crown_rain': dict(frames=frames((art.CROWN, P_GOLD)), rate=16, shape=disc(1.3, 3.2, [0, -1, 0]),
                               life=(1.2, 1.6), size=0.2, speed=1, accel=[0, -2.5, 0], drag=0.5,
                               spin=('math.random(-20, 20)', 0)),
    'victory_lightning_strike': dict(frames=frames((art.ZAP, P_YELLOW), (art.SPARK, P_YELLOW)), rate=26,
                                     shape=sphere(0.3, 0.2), life=(0.5, 0.9), size=0.18, speed=4,
                                     accel=[0, 2, 0], drag=3, part='bolt'),
    'victory_coin_shower': dict(frames=frames((art.COIN, P_GOLD), (art.COIN, shades(LIGHT_GOLD, dark='#B07A22'))),
                                rate=30, shape=disc(1.2, 3.3, [0, -1, 0]), life=(1.0, 1.3),
                                size=['0.14 * math.abs(math.cos(v.particle_age * 540 + v.particle_random_3 * 360))',
                                      0.14],
                                speed=0.5, accel=[0, -4, 0]),
    'victory_champions_crown': dict(frames=frames((art.STAR, P_GOLD_STAR), (art.SPARK, P_GOLD_STAR),
                                                  (art.STAR, P_WHITE_STAR)),
                                    rate=28, shape=disc(0.8, 0.2, [0, 1, 0], surface=True), life=(1.2, 1.6),
                                    size=twinkle(0.14), speed=2.5, drag=1.5, part='crown'),

    'trail_ember_steps': dict(frames=frames((art.DUST, P_ORANGE), (art.SPARK, P_ORANGE)), rate=2,
                              life=(0.7, 1.0), size=shrink(0.14), speed=0.15, accel=[0, 0.5, 0]),
    'trail_leaf_steps': dict(frames=frames((art.LEAF, P_LEAF), (art.LEAF, P_LEAF2)), rate=2, life=(0.8, 1.2),
                             size=0.15, speed=0.2, accel=[0, -0.2, 0], spin=SPIN),
    'trail_rainbow': dict(frames=frames(*[(art.DUST, shades(c)) for c in RAINBOW]), rate=3, life=(0.6, 1.0),
                          size=0.12, speed=0.1, accel=[0, 0.15, 0]),
    'trail_music_notes': dict(frames=frames((art.NOTE, shades(GOLD)), (art.NOTE, shades('#6A92DD')),
                                            (art.NOTE, shades('#FF7AC8'))),
                              rate=1, life=(0.9, 1.2), size=0.18, speed=0.4, drag=1, direction=[0, 1, 0]),
    'trail_hearts': dict(frames=frames((art.HEART, shades('#FF5577')), (art.HEART, shades('#FF8FB1'))), rate=1,
                         life=(0.8, 1.1), size=0.16, speed=0.35, drag=1, direction=[0, 1, 0]),
    'trail_sparkles': dict(frames=frames((art.STAR, P_WHITE_STAR), (art.STAR, P_GOLD_STAR)), rate=2,
                           life=(0.6, 1.0), size=twinkle(0.16), speed=0.05),
    'trail_snowfall': dict(frames=frames((art.FLAKE, P_SNOW), (art.FLAKE, P_ICE2)), rate=2, life=(0.8, 1.2),
                           size=0.14, speed=0.05, accel=[0, -0.15, 0], spin=SPIN, y=0.35),
    'trail_bubbles': dict(frames=frames((art.BUBBLE, P_BUBBLE)), rate=2, life=(0.8, 1.2), size=0.14, speed=0.3,
                          accel=[0, 0.3, 0], direction=[0, 1, 0]),
    'trail_pumpkin_steps': dict(frames=frames((art.PUMPKIN, P_PUMPKIN), (art.DUST, P_ORANGE)), rate=2,
                                life=(0.7, 1.1), size=0.18, speed=0.15, accel=[0, 0.3, 0]),
    'trail_arena_flame': dict(frames=frames((art.FLAME, P_BLUE_FIRE), (art.FLAME, P_GOLD_STAR)), rate=2,
                              life=(0.6, 0.9), size=shrink(0.16), speed=0.1, accel=[0, 0.6, 0]),
    'trail_supporter_sparkles': dict(frames=frames((art.STAR, P_GREEN_STAR), (art.STAR, P_GOLD_STAR)), rate=2,
                                     life=(0.6, 1.0), size=twinkle(0.16), speed=0.05),
}
assert len(EFFECTS) == 31
# second emitters for looks one particle sheet cannot give (spawned by the parent's creation_event);
# cosmetics/parts/<parent>_<name>, not cosmetic ids
PARTS = {
    'victory_lightning_strike_bolt': dict(
        frames=[art.sprite(art.BOLT, pal(W='#FFFDE8', L='#FFE14D'))], rate=1, shape=point([0, 1.6, 0]),
        life=(0.35, 0.35), size=[0.7, 1.6], speed=0, facing='rotate_y',
        alpha='math.sin(v.particle_age * 3000) > -0.4 ? 1 : 0.25'),
    'victory_champions_crown_crown': dict(
        frames=[art.sprite(art.BIG_CROWN, P_GOLD)], rate=1, shape=point([0, 0.6, 0], [0, 1, 0]), life=(1.8, 1.8),
        size='0.6 * math.min(1, v.particle_age * 4)', speed=3.2, drag=1.6, facing='rotate_y',
        alpha='v.particle_age < 1.3 ? 1 : 1 - (v.particle_age - 1.3) / 0.5'),
}


def effect_json(eid, kind, sheet, n, p):
    w, h = sheet.size[0] // n, sheet.size[1]
    life = p['life']
    comps = {}
    if kind == 'aura':
        comps['cobblemon:emitter_space'] = {'scaling': 'entity'}
        # One finite burst per packet: the server resends every 2 s to whoever tracks the Pokemon, so an unequip or a
        # packet the client dropped (Pokemon mid send-out or not yet rendered) heals within one round. The extra 0.5 s
        # overlaps consecutive bursts so tick jitter leaves no gap. A looping emitter with no sleep_time stops after one
        # cycle in Cobblemon 1.8.2, and an endless one could never be cleared.
        comps['minecraft:emitter_lifetime_once'] = {'active_time': 2.5}
        comps['minecraft:emitter_rate_steady'] = {'spawn_rate': p['rate'], 'max_particles': p.get('max', 20)}
    else:
        comps['minecraft:emitter_lifetime_once'] = {'active_time': life[1]}
        comps['minecraft:emitter_rate_instant'] = {'num_particles': p['rate']}
    comps.update(p.get('shape') or box([0.25, 0.02, 0.25], p.get('y', 0.08), p.get('direction', 'outwards')))
    if 'part' in p:
        comps['minecraft:emitter_lifetime_events'] = {'creation_event': p['part']}
    size = p['size'] if isinstance(p['size'], list) else [p['size'], p['size']]
    uv = {'texture_width': w * n, 'texture_height': h, 'uv_size': [w, h],
          'uv': [f'math.floor(v.particle_random_1 * {n}) * {w}' if n > 1 else 0, 0]}
    comps['minecraft:particle_appearance_billboard'] = {'size': size, 'facing_camera_mode': p.get('facing',
                                                                                                    'rotate_xyz'),
                                                        'uv': uv}
    comps['minecraft:particle_appearance_tinting'] = {'color': [1, 1, 1, p.get('alpha', FADE)]}
    comps['minecraft:particle_initial_speed'] = p.get('speed', 0)
    if 'spin' in p:
        comps['minecraft:particle_initial_spin'] = {'rotation': p['spin'][0], 'rotation_rate': p['spin'][1]}
    comps['minecraft:particle_lifetime_expression'] = {
        'max_lifetime': life[0] if life[0] == life[1] else f'math.random({life[0]}, {life[1]})'}
    comps['minecraft:particle_motion_dynamic'] = {'linear_acceleration': p.get('accel', [0, 0, 0]),
                                                  'linear_drag_coefficient': p.get('drag', 0)}
    effect = {'description': {'identifier': f'{NS}:{eid}',
                              'basic_render_parameters': {'material': 'particles_blend',
                                                          'texture': f'{NS}:{eid}'}},
              'components': comps}
    if 'part' in p:
        effect['events'] = {p['part']: {'particle_effect': {'effect': f'{NS}:cosmetics/parts/{eid.split("/")[-1]}_'
                                                                      f'{p["part"]}', 'type': 'emitter'}}}
    return {'format_version': '1.10.0', 'particle_effect': effect}


def build_effects(pack, write_json):
    out = []
    jobs = [(f'cosmetics/{eid}', eid.split('_')[0], p) for eid, p in EFFECTS.items()]
    jobs += [(f'cosmetics/parts/{eid}', 'part', p) for eid, p in PARTS.items()]
    for path, kind, p in jobs:
        sheet = art.strip(p['frames'])
        png = os.path.join(pack, 'assets', NS, 'textures', 'particle', *path.split('/')) + '.png'
        os.makedirs(os.path.dirname(png), exist_ok=True)
        sheet.save(png, optimize=True)
        write_json(os.path.join(pack, 'assets', NS, 'bedrock', 'particles', *path.split('/')) + '.particle.json',
                   effect_json(path, kind, sheet, len(p['frames']), p))
        out.append((path.split('/')[-1], sheet))
    return out


# vanilla 1.21.1 item models (client jar assets/minecraft/models/item/<item>.json) minus their overrides, which
# ITEM_STATES in check.py holds; our files replace these, so parent, textures and display must stay exactly as vanilla
VANILLA_BASE = {
    'fishing_rod': {'parent': 'item/handheld_rod', 'textures': {'layer0': 'item/fishing_rod'}},
    'bow': {'parent': 'item/generated', 'textures': {'layer0': 'item/bow'}, 'display': {
        'thirdperson_righthand': {'rotation': [-80, 260, -40], 'translation': [-1, -2, 2.5], 'scale': [0.9, 0.9, 0.9]},
        'thirdperson_lefthand': {'rotation': [-80, -280, 40], 'translation': [-1, -2, 2.5], 'scale': [0.9, 0.9, 0.9]},
        'firstperson_righthand': {'rotation': [0, -90, 25], 'translation': [1.13, 3.2, 1.13],
                                  'scale': [0.68, 0.68, 0.68]},
        'firstperson_lefthand': {'rotation': [0, 90, -25], 'translation': [1.13, 3.2, 1.13],
                                 'scale': [0.68, 0.68, 0.68]}}},
    'crossbow': {'parent': 'item/generated', 'textures': {'layer0': 'item/crossbow_standby'}, 'display': {
        'thirdperson_righthand': {'rotation': [-90, 0, -60], 'translation': [2, 0.1, -3], 'scale': [0.9, 0.9, 0.9]},
        'thirdperson_lefthand': {'rotation': [-90, 0, 30], 'translation': [2, 0.1, -3], 'scale': [0.9, 0.9, 0.9]},
        'firstperson_righthand': {'rotation': [-90, 0, -55], 'translation': [1.13, 3.2, 1.13],
                                  'scale': [0.68, 0.68, 0.68]},
        'firstperson_lefthand': {'rotation': [-90, 0, 35], 'translation': [1.13, 3.2, 1.13],
                                 'scale': [0.68, 0.68, 0.68]}}},
}


def item_overrides(item):
    """Vanilla's own overrides first, then per set (ascending custom_model_data) its base state followed by its
    states in vanilla order, then the same block at CATCH_ALL pointing back at vanilla. Overrides are tested last to
    first, so for any value the highest set threshold <= value wins and, inside it, the most specific state."""
    base, states = ITEM_STATES[item]
    out = [{'predicate': p, 'model': f'item/{st}'} for p, st in states]
    for s, cmd in sorted(TOOL_SETS.items(), key=lambda kv: kv[1]):
        out.append({'predicate': {'custom_model_data': cmd}, 'model': f'{NS}:item/toolskin/{s}_{base}'})
        out += [{'predicate': {'custom_model_data': cmd, **p}, 'model': f'{NS}:item/toolskin/{s}_{st}'}
                for p, st in states]
    # a copy of the vanilla model: an override may not point at the item model itself (the baker would recurse)
    out.append({'predicate': {'custom_model_data': CATCH_ALL}, 'model': f'{NS}:item/toolskin/vanilla/{item}'})
    out += [{'predicate': {'custom_model_data': CATCH_ALL, **p}, 'model': f'item/{st}'} for p, st in states]
    return out


def build_tools(pack, write_json):
    models = os.path.join(pack, 'assets', NS, 'models', 'item', 'toolskin')
    textures = os.path.join(pack, 'assets', NS, 'textures', 'item', 'toolskin')
    os.makedirs(textures, exist_ok=True)
    out = {}
    for s in TOOL_SETS:
        images = toolsets.textures(toolsets.SETS[s])
        assert set(images) == set(TOOLSET_TEXTURES), f'tool set {s}: textures {sorted(images)}'
        for state in TOOLSET_TEXTURES:
            name = f'{s}_{state}'
            images[state].save(os.path.join(textures, name + '.png'), optimize=True)
            kind = next((k for k in TOOLSET_PARENT if state.startswith(k)), None)
            write_json(os.path.join(models, name + '.json'),
                       {'parent': TOOLSET_PARENT.get(kind, 'minecraft:item/handheld'),
                        'textures': {'layer0': f'{NS}:item/toolskin/{name}'}})
        out[s] = images
    for item in TOOL_ITEMS:
        base = VANILLA_BASE.get(item) or {'parent': 'minecraft:item/handheld',
                                          'textures': {'layer0': vanilla_texture(item, ITEM_STATES[item][0])}}
        write_json(os.path.join(models, 'vanilla', item + '.json'), base)
        write_json(os.path.join(pack, 'assets', 'minecraft', 'models', 'item', item + '.json'),
                   {**base, 'overrides': item_overrides(item)})
    return out


def toolsets_preview(sets, path, scale=6):
    """12 rows x 17 textures (TOOLSET_TEXTURES order), set ids down the left, state names across the top."""
    font = ImageFont.load_default()
    pad, label_w, head_h = 8, 64, 30
    cell = 16 * scale + pad
    sheet = Image.new('RGBA', (label_w + len(TOOLSET_TEXTURES) * cell + pad, head_h + len(sets) * cell + pad),
                      (0x1E, 0x22, 0x2C, 255))
    draw = ImageDraw.Draw(sheet)
    for k, state in enumerate(TOOLSET_TEXTURES):
        x = label_w + k * cell
        words = state.replace('crossbow_', 'xbow_').replace('fishing_rod', 'rod').split('_')
        draw.text((x, 4), words[0], fill=CREAM + (255,), font=font)
        if len(words) > 1:
            draw.text((x, 16), '_'.join(words[1:]), fill=CREAM + (255,), font=font)
    for r, (s, images) in enumerate(sets.items()):
        y = head_h + r * cell
        draw.text((pad, y + 16 * scale // 2 - 6), s, fill=CREAM + (255,), font=font)
        for k, state in enumerate(TOOLSET_TEXTURES):
            im = images[state]
            sheet.alpha_composite(im.resize((16 * scale, 16 * scale), Image.NEAREST), (label_w + k * cell, y))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path, optimize=True)


def toolsets_closeup(sets, path, states=('sword', 'pickaxe', 'bow'), scale=10):
    """Sword / pickaxe / bow of every set at x10, two sets per row, plus each at x2 on an inventory-slot grey."""
    font = ImageFont.load_default()
    pad, label_h = 10, 14
    block = len(states) * (16 * scale + pad)
    cols, rows = 2, (len(sets) + 1) // 2
    row_h = label_h + 16 * scale + pad + 36 + pad
    sheet = Image.new('RGBA', (pad + cols * (block + 2 * pad), pad + rows * row_h), (0x1E, 0x22, 0x2C, 255))
    draw = ImageDraw.Draw(sheet)
    for n, (s, images) in enumerate(sets.items()):
        x0, y0 = pad + (n % cols) * (block + 2 * pad), pad + (n // cols) * row_h
        draw.text((x0, y0), f'{s} ({TOOL_SETS[s]})', fill=CREAM + (255,), font=font)
        for k, state in enumerate(states):
            x = x0 + k * (16 * scale + pad)
            sheet.alpha_composite(images[state].resize((16 * scale, 16 * scale), Image.NEAREST), (x, y0 + label_h))
            slot = Image.new('RGBA', (36, 36), (0x8B, 0x8B, 0x8B, 255))
            slot.alpha_composite(images[state].resize((32, 32), Image.NEAREST), (2, 2))
            sheet.alpha_composite(slot, (x, y0 + label_h + 16 * scale + pad))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path, optimize=True)


def sheet_preview(rows, path, cols=1):
    """rows: [(label, image)] scaled x8 nearest-neighbour, laid out in a grid with the label above each image."""
    font = ImageFont.load_default()
    scale, pad, label_h = 8, 12, 14
    cw = max(im.width for _, im in rows) * scale + pad
    ch = max(im.height for _, im in rows) * scale + label_h + pad
    lines = (len(rows) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * cw + pad, lines * ch + pad), (0x2B, 0x2F, 0x3A, 255))
    draw = ImageDraw.Draw(sheet)
    for i, (label, im) in enumerate(rows):
        x, y = pad + (i % cols) * cw, pad + (i // cols) * ch
        draw.text((x, y), label, fill=CREAM + (255,), font=font)
        sheet.alpha_composite(im.resize((im.width * scale, im.height * scale), Image.NEAREST), (x, y + label_h))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path, optimize=True)


# ---------------------------------------------------------------------------------------------------------------------
# v1.1 client-mod cosmetics: hats / back items (vanilla JSON models) and ball skins (Cobblemon ball variations)

TEX_SIZES = (16, 32, 64, 128)
BALL_ORDER = 100  # above every Cobblemon base set (order 0): sets are sorted by order and the last fitting one wins
POKE_BALLS = 'assets/cobblemon/bedrock/poke_balls/'
REPO_CLASS = 'com/cobblemon/mod/common/client/render/models/blockbench/repository/VaryingModelRepository.class'


def num(v):
    return int(v) if v == int(v) else v


def shelf(sizes, size):
    """Place (w, h) rects left to right in rows, tallest first; {index: (x, y)} or None if they do not fit."""
    spots, x, y, row = {}, 0, 0, 0
    for k in sorted(range(len(sizes)), key=lambda k: (-sizes[k][1], -sizes[k][0], k)):
        w, h = sizes[k]
        if x + w > size:
            x, y, row = 0, y + row, 0
        if w > size or y + h > size:
            return None
        spots[k] = (x, y)
        x, row = x + w, max(row, h)
    return spots


def wearable_model(cid, spec):
    """Paint every face, pack the faces into the smallest square texture that holds them, return (model, texture)."""
    density, palette = spec.get('density', 2), spec['palette']
    faces = [(n, face, im) for n, e in enumerate(spec['elements']) for face in art.FACES
             if face not in e['skip'] for im in [art.paint_face(e, face, density, palette)] if im]
    sizes = [im.size for _, _, im in faces]
    for size in TEX_SIZES:
        spots = shelf(sizes, size)
        if spots:
            break
    else:
        raise SystemExit(f'{cid}: faces do not fit a {TEX_SIZES[-1]}px texture; lower its density')
    tex = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    ref = f'{NS}:cosmetic/{cid}'
    elements = []
    for k, (n, face, im) in enumerate(faces):
        x, y = spots[k]
        tex.paste(im, (x, y))
        if not elements or elements[-1][0] != n:
            e = spec['elements'][n]
            body = {'from': [num(c) for c in e['frm']], 'to': [num(c) for c in e['to']]}
            if e['rot']:
                axis, angle, origin = e['rot']
                body['rotation'] = {'origin': [num(c) for c in origin], 'axis': axis, 'angle': num(angle)}
            body['faces'] = {}
            elements.append((n, body))
        s = 16 / size
        elements[-1][1]['faces'][face] = {'uv': [num(x * s), num(y * s), num((x + im.width) * s),
                                                 num((y + im.height) * s)], 'texture': '#skin'}
    return {'textures': {'particle': ref, 'skin': ref}, 'elements': [b for _, b in elements]}, tex


def build_wearables(pack, write_json):
    out = {}
    for cid in HATS + BACKS + FRONTS:
        model, tex = wearable_model(cid, art.WEARABLES[cid] if cid in art.WEARABLES else art.FRONTS[cid])
        path = os.path.join(pack, 'assets', NS, 'textures', 'cosmetic', cid + '.png')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tex.save(path, optimize=True)
        write_json(os.path.join(pack, 'assets', NS, 'models', 'cosmetic', cid + '.json'), model)
        out[cid] = (model, tex)
    # textures/cosmetic/ is not in the vanilla blocks atlas: without this source the baked models render as missing
    atlas = os.path.join(pack, 'assets', 'minecraft', 'atlases', 'blocks.json')
    data = {'sources': []}
    if os.path.exists(atlas):
        with open(atlas, encoding='utf-8') as f:
            data = json.load(f)
    src = {'type': 'directory', 'source': 'cosmetic', 'prefix': 'cosmetic/'}
    if src not in data['sources']:
        data['sources'].append(src)
    write_json(atlas, data)
    return out


def refresh_cobblemon(jar):
    """Read the Poke Ball list, base variations, geometries (texture size + box UV) and poser ids from the Cobblemon
    jar into cosmetics/cobblemon_balls.json, which the build and the checker use (the jar is not needed after)."""
    with open(jar, 'rb') as f:
        sha1 = hashlib.sha1(f.read()).hexdigest()
    with zipfile.ZipFile(jar) as z:
        names = set(z.namelist())
        balls = {}
        for n in sorted(names):
            if n.startswith(POKE_BALLS + 'variations/') and n.endswith('.json'):
                d = json.loads(z.read(n).decode('utf-8'))
                ball = d.get('pokeball', d.get('species', d.get('name')))
                base = [v for v in d['variations'] if not v.get('aspects')]
                assert ball not in balls and len(base) == 1, f'{n}: expected one aspect-less base set per ball'
                balls[ball] = {'order': d.get('order', 0), 'model': base[0]['model'], 'poser': base[0]['poser']}
        models = {}
        for mid in sorted({b['model'] for b in balls.values()}):
            ns, path = mid.split(':')
            src = f'assets/{ns}/bedrock/poke_balls/models/{path}.json'  # id = file name without .json
            assert src in names, f'{mid}: no {src} in the jar'
            (geo,) = json.loads(z.read(src).decode('utf-8'))['minecraft:geometry']
            cubes = [{'bone': b['name'], 'uv': c['uv'], 'size': c['size'],
                      **({'inflate': c['inflate']} if c.get('inflate') else {})}
                     for b in geo['bones'] for c in b.get('cubes', [])]
            assert all(isinstance(c['uv'], list) for c in cubes), f'{mid}: per-face UV is not supported'
            models[mid] = {'texture': [geo['description']['texture_width'], geo['description']['texture_height']],
                           'cubes': cubes}
        repo = z.read(REPO_CLASS)
        posers = {}
        for pid in sorted({b['poser'] for b in balls.values()}):
            ns, path = pid.split(':')
            if f'assets/{ns}/bedrock/poke_balls/posers/{path}.json' in names:
                posers[pid] = 'json'
                continue
            # in-built posers are registered in code: inbuilt("<path>", ...) -> cobblemon:<path>
            lit = path.encode('utf-8')
            assert ns == 'cobblemon' and b'\x01' + len(lit).to_bytes(2, 'big') + lit in repo, \
                f'{pid}: neither a poser file nor an in-built poser in {REPO_CLASS}'
            posers[pid] = 'inbuilt'
    data = {'source': {'jar': os.path.basename(jar), 'sha1': sha1}, 'balls': balls, 'models': models,
            'posers': posers}
    with open(COBBLEMON_BALLS, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=1, sort_keys=True)
        f.write('\n')
    print(f'{COBBLEMON_BALLS}: {len(balls)} balls, {len(models)} geometries, {len(posers)} posers from {jar}')


def build_balls(pack, write_json):
    cob = load_cobblemon()
    textures, out = {}, []
    for skin in BALL_SKINS:
        for mid, geo in sorted(cob['models'].items()):
            name = mid.split(':', 1)[1].removesuffix('.geo')
            rel = f'textures/poke_balls/cosmetic/{skin}/{name}.png'
            im = art.ball_texture(art.BALL_SKINS_ART[skin], geo)
            path = os.path.join(pack, 'assets', NS, *rel.split('/'))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            im.save(path, optimize=True)
            textures[skin, mid] = f'{NS}:{rel}'
            out.append((f'{skin} on {name}', im))
    for ball, base in sorted(cob['balls'].items()):
        # model and poser pinned to the ball's own base ones: the texture is drawn for exactly that UV layout
        variations = [{'aspects': [BALL_ASPECT.format(skin)], 'layers': [], 'model': base['model'],
                       'poser': base['poser'], 'texture': textures[skin, base['model']]} for skin in BALL_SKINS]
        write_json(os.path.join(pack, 'assets', NS, 'bedrock', 'poke_balls', 'variations',
                                ball.split(':', 1)[1] + '.json'),
                   {'pokeball': ball, 'order': BALL_ORDER, 'variations': variations})
    return out, len(cob['balls'])


# preview: orthographic texel-quad renderer of the shipped model JSON + texture, in contract model space

VIEWS = {  # name: (screen x, screen y, nearness) of a point, direction toward the viewer; +x = wearer's right
    'front': (lambda p: (-p[0], p[1], -p[2]), (0, 0, -1)),
    'side': (lambda p: (-p[2], p[1], p[0]), (1, 0, 0)),  # from the wearer's right, facing to the viewer's right
    'back': (lambda p: (p[0], p[1], p[2]), (0, 0, 1)),
}


def rotate(p, axis, angle, origin):
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)
    x, y, z = (p[k] - origin[k] for k in range(3))
    if axis == 'x':
        x, y, z = x, y * c - z * s, y * s + z * c
    elif axis == 'y':
        x, y, z = x * c + z * s, y, -x * s + z * c
    else:
        x, y, z = x * c - y * s, x * s + y * c, z
    return x + origin[0], y + origin[1], z + origin[2]


def model_quads(model, tex):
    """[(4 corners, rgb, normal)] for every opaque texel of every face."""
    size, px, quads = tex.width, tex.load(), []
    for e in model['elements']:
        r = e.get('rotation')
        for face, fd in e['faces'].items():
            corners = art.face_corners(face, e['from'], e['to'])
            normal = art.NORMALS[face]
            if r:
                corners = [rotate(c, r['axis'], r['angle'], r['origin']) for c in corners]
                normal = rotate(normal, r['axis'], r['angle'], (0, 0, 0))
            tl, tr, br, bl = corners
            u1, v1, u2, v2 = (c * size / 16 for c in fd['uv'])
            w, h = round(u2 - u1), round(v2 - v1)
            for j in range(h):
                for i in range(w):
                    c = px[round(u1) + i, round(v1) + j]
                    if c[3]:
                        pt = [art.lerp3(art.lerp3(tl, tr, a), art.lerp3(bl, br, a), b)
                              for a, b in ((i / w, j / h), ((i + 1) / w, j / h), ((i + 1) / w, (j + 1) / h),
                                           (i / w, (j + 1) / h))]
                        quads.append((pt, c[:3], normal))
    return quads


def body_quads(frm, to):
    """The reference head / torso: a grey box drawn as a 1 px grid."""
    quads = []
    for face in art.FACES:
        tl, tr, br, bl = art.face_corners(face, frm, to)
        fw, fh = art.face_size(face, frm, to)
        for j in range(int(fh)):
            for i in range(int(fw)):
                pt = [art.lerp3(art.lerp3(tl, tr, a), art.lerp3(bl, br, a), b)
                      for a, b in ((i / fw, j / fh), ((i + 1) / fw, j / fh), ((i + 1) / fw, (j + 1) / fh),
                                   (i / fw, (j + 1) / fh))]
                quads.append((pt, (0x9A, 0x9E, 0xA8) if (i + j) % 2 else (0x8C, 0x90, 0x9A), art.NORMALS[face],
                              'grid'))
    return quads


def render(quads, view, window, scale=7, pad=6):
    project, toward = VIEWS[view]
    corners = [project((x, y, z)) for x in window[0] for y in window[1] for z in window[2]]
    x0, x1 = min(c[0] for c in corners), max(c[0] for c in corners)
    y0, y1 = min(c[1] for c in corners), max(c[1] for c in corners)
    im = Image.new('RGBA', (round((x1 - x0) * scale) + 2 * pad, round((y1 - y0) * scale) + 2 * pad),
                   (0x2B, 0x2F, 0x3A, 255))
    draw = ImageDraw.Draw(im)
    visible = []
    for k, q in enumerate(quads):
        n = q[2]
        if n[0] * toward[0] + n[1] * toward[1] + n[2] * toward[2] <= 1e-6:
            continue
        pts = [project(p) for p in q[0]]
        visible.append((sum(p[2] for p in pts) / 4, k, pts, q))
    for _, _, pts, q in sorted(visible, key=lambda v: (v[0], v[1])):
        n = q[2]
        f = 0.8 + 0.2 * n[1] - 0.1 * abs(n[0])
        rgb = tuple(min(255, round(c * f)) for c in q[1])
        poly = [(pad + (p[0] - x0) * scale, pad + (y1 - p[1]) * scale) for p in pts]
        draw.polygon(poly, fill=rgb + (255,), outline=(0x6E, 0x72, 0x7C, 255) if len(q) > 3 else None)
    return im


HEAD, TORSO = ((4, 0, 4), (12, 8, 12)), ((4, -12, 6), (12, 0, 10))
WINDOWS = {'hat': ((-1.5, 17.5), (-1, 21), (-1.5, 17.5)), 'back': ((-1, 17), (-14, 2), (2, 17)),
           'front': ((-1, 17), (-14, 2), (1, 13))}


def wearables_preview(models, balls, path):
    font = ImageFont.load_default()
    pad, label_h = 12, 14
    rows = []
    for cid, (model, tex) in models.items():
        kind = 'hat' if cid.startswith('hat_') else 'front' if cid.startswith('front_') else 'back'
        quads = body_quads(*(HEAD if kind == 'hat' else TORSO)) + model_quads(model, tex)
        rows.append((cid, [(v, render(quads, v, WINDOWS[kind])) for v in VIEWS]))
    ball_rows = [(label, im.resize((im.width * 4, im.height * 4), Image.NEAREST)) for label, im in balls]
    width = max(sum(im.width + pad for _, im in views) for _, views in rows) + pad
    height = pad + sum(label_h + max(im.height for _, im in views) + pad for _, views in rows)
    bh = 0
    if ball_rows:
        width = max(width, 3 * (ball_rows[0][1].width + pad) + pad)
        bh = label_h + ball_rows[0][1].height + pad
        height += ((len(ball_rows) + 2) // 3) * bh + pad
    sheet = Image.new('RGBA', (width, height), (0x1E, 0x22, 0x2C, 255))
    draw = ImageDraw.Draw(sheet)
    y = pad
    for cid, views in rows:
        x = pad
        for v, im in views:
            draw.text((x, y), f'{cid} - {v}', fill=CREAM + (255,), font=font)
            sheet.alpha_composite(im, (x, y + label_h))
            x += im.width + pad
        y += label_h + max(im.height for _, im in views) + pad
    for k, (label, im) in enumerate(ball_rows):
        x = pad + (k % 3) * (im.width + pad)
        yy = y + (k // 3) * bh
        draw.text((x, yy), label, fill=CREAM + (255,), font=font)
        sheet.alpha_composite(im, (x, yy + label_h))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path, optimize=True)


def build(pack, write_json):
    for d in (('origins', 'bedrock', 'particles', 'cosmetics'), ('origins', 'textures', 'particle', 'cosmetics'),
              ('origins', 'models', 'item', 'toolskin'), ('origins', 'textures', 'item', 'toolskin'),
              ('origins', 'models', 'cosmetic'), ('origins', 'textures', 'cosmetic'),
              ('origins', 'bedrock', 'poke_balls'), ('origins', 'textures', 'poke_balls')):
        shutil.rmtree(os.path.join(pack, 'assets', *d), ignore_errors=True)  # drop stale generated files
    effects = build_effects(pack, write_json)
    tools = build_tools(pack, write_json)
    sheet_preview(effects, os.path.join(PREVIEW, 'particles.png'), cols=3)
    toolsets_preview(tools, os.path.join(PREVIEW, 'toolsets.png'))
    toolsets_closeup(tools, os.path.join(PREVIEW, 'toolsets_x10.png'))
    wearables = build_wearables(pack, write_json)
    balls, n_balls = build_balls(pack, write_json)
    wearables_preview({k: v for k, v in wearables.items() if k in HATS + BACKS}, balls,
                      os.path.join(PREVIEW, 'wearables.png'))
    wearables_preview({k: v for k, v in wearables.items() if k in FRONTS}, [], os.path.join(PREVIEW, 'fronts.png'))
    print(f'cosmetics: {len(EFFECTS)} effects + {len(PARTS)} parts, {len(tools)} tool sets x '
          f'{len(TOOLSET_TEXTURES)} textures, {len(TOOL_ITEMS)} item models with overrides')
    print(f'cosmetics: {len(HATS)} hats + {len(BACKS)} back items + {len(FRONTS)} front items, {len(BALL_SKINS)} '
          f'ball skins x {n_balls} balls')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--refresh-cobblemon':
        refresh_cobblemon(sys.argv[2])
    else:
        sys.exit('usage: python -I cosmetics/build.py --refresh-cobblemon <Cobblemon jar>  (the pack is built by '
                 'python -I build.py)')
