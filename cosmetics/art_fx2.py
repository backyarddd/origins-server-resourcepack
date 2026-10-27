"""Cosmetics drop 2 particle effects (catalog-v2.md): 20 emotes, 8 auras, 10 send-outs, 8 victory, 12 trails and 7 emoji
effects. EFFECTS2 / PARTS2 are merged into cosmetics/build.py's EFFECTS / PARTS and use the same keys (frames, rate, shape,
life, size, speed, accel, drag, spin, alpha, part, max, facing). Sprites are original 8x8 ASCII templates coloured by
palettes (roles O outline, M mid, L light, W highlight, X accent, see art.py); the emote and emoji sprites are the
16x16 drawings in src/emotes/, read from disk every time this module is imported (i.e. at build time).

The imports are art-only on purpose: build.py imports this module, so it must not import build.py back.
"""
import os

from PIL import Image

from cosmetics.art import (BUBBLE, COIN, CONFETTI, DUST, HEART, LEAF, NOTE, SMOKE, STAR as STAR4, hexrgb,
                           shades, sprite)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMOTES = os.path.join(ROOT, 'src', 'emotes')

# --- the small MoLang / shape helpers build.py uses for EFFECTS (same output, kept here to avoid a circular import) ---
AGE = 'v.particle_age / v.particle_lifetime'


def twinkle(s):
    return f'{s} * math.sin(180 * {AGE})'


def shrink(s):
    return f'{s} * (1 - 0.6 * {AGE})'


def grow(s):
    return f'{s} * (0.7 + 0.6 * {AGE})'


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
RAINBOW = ['#FF5555', '#FFAA33', '#FFE066', '#7BD88F', '#55E6E6', '#A37BFF']


def pal(**roles):
    return {k: hexrgb(v) for k, v in roles.items()}


# --- 8x8 templates -------------------------------------------------------------------------------------------------
PAW = [
    "..L..L..",
    "..M..M..",
    "L......L",
    "M.LLLL.M",
    "..LMMM..",
    "..MMMM..",
    "...MM...",
    "........",
]
SOUL = [
    "....L...",
    "...LL...",
    "...LM...",
    "..LWM...",
    "..LWMM..",
    "..LWWM..",
    "...LMM..",
    "...OO...",
]
CHERRY = [
    "........",
    "..OOO...",
    ".OLWLO..",
    ".OLLLMO.",
    ".OLLMMO.",
    "..OMMO..",
    "..O.OO..",
    "........",
]
STAR5 = [
    "...OO...",
    "...LM...",
    "OOLWWMOO",
    ".OLWWMO.",
    "..OLMO..",
    "..LMMM..",
    ".OM..MO.",
    ".O....O.",
]
ZIG = [
    "........",
    "....WL..",
    "...WL...",
    "..WWWL..",
    "....WL..",
    "...WL...",
    "..WL....",
    "........",
]
SPLAT = [
    "........",
    ".O...O..",
    "..OOOMO.",
    ".OMMMMMO",
    ".OMLMMMO",
    "..OMMMO.",
    ".OOOOMO.",
    "O...O...",
]
SPLAT_B = [
    "........",
    "...O....",
    ".O.OMO..",
    "OMOMMMO.",
    ".OMLMMMO",
    ".OMMMMO.",
    "..OOMO.O",
    "......O.",
]
CLOUD = [
    "........",
    "..OOO...",
    ".OWLLOO.",
    "OWLLLLLO",
    "OLLLLLMO",
    "OLLMMMMO",
    ".OOOOOO.",
    "........",
]
BLOB = [
    "........",
    "........",
    "..OOOO..",
    ".OLLMMO.",
    "OLWMMMMO",
    "OLMMMMMO",
    "OMMMMMMO",
    ".OOOOOO.",
]
BLOB_B = [
    "........",
    "..OOO...",
    ".OLLMO..",
    ".OWMMMO.",
    ".OMMMMO.",
    "..OOOO..",
    "........",
    "........",
]
SQUARE = [
    "........",
    "........",
    "..LLLL..",
    "..LMMM..",
    "..LMMM..",
    "..LMMM..",
    "........",
    "........",
]
PLUS = [
    "........",
    "...L....",
    "...M....",
    ".LMWMM..",
    "...M....",
    "...M....",
    "........",
    "........",
]
BIT = [
    "........",
    "........",
    "........",
    "...LL...",
    "...MM...",
    "........",
    "........",
    "........",
]
BAR = [
    "........",
    "........",
    "........",
    ".LLLLLL.",
    ".MMMMMM.",
    "........",
    "........",
    "........",
]
CHUNK = [
    "........",
    ".LL.....",
    ".LM.....",
    ".LMMMM..",
    ".LMMMM..",
    "........",
    "........",
    "........",
]
MAPLE = [
    "...O....",
    "..OLO.O.",
    ".OLMLOLO",
    "OLMMMLMO",
    ".OMMMMO.",
    "..OMMO..",
    "...OM...",
    "...O....",
]
NOTE2 = [
    ".OOOOOO.",
    ".OLLLLO.",
    ".O....O.",
    ".O....O.",
    "OOO..OOO",
    "OMO..OMO",
    "OOO..OOO",
    "........",
]
SHARD = [
    "......LW",
    ".....LWL",
    "....LWLM",
    "...LWLMO",
    "..LWLMO.",
    ".LWLMO..",
    "LMMO....",
    "OO......",
]
SHARD_B = [
    "........",
    "...LW...",
    "..LWLM..",
    "..LWLMO.",
    ".LWLMMO.",
    ".LMMMOO.",
    "..OOOO..",
    "........",
]
DROP = [
    "...M....",
    "...M....",
    "..LMM...",
    "..LMMO..",
    ".LWMMMO.",
    ".LMMMMO.",
    ".OMMMMO.",
    "..OOOO..",
]
STREAK = [
    "........",
    "........",
    "........",
    "OLLLMM..",
    ".MMMO...",
    "........",
    "........",
    "........",
]
GRAIN = [
    "........",
    "........",
    "...LM...",
    "...MO...",
    "........",
    "........",
    "........",
    "........",
]
SPECK = [
    "........",
    "........",
    "...M....",
    "..MLM...",
    "...M....",
    "........",
    "........",
    "........",
]
FILLED_BUBBLE = [
    "..OOOO..",
    ".OLLLMO.",
    "OLWLMMMO",
    "OLWMMMMO",
    "OLMMMMMO",
    "OMMMMMMO",
    ".OMMMMO.",
    "..OOOO..",
]
STREAMER = [
    "........",
    "..LM....",
    "..LM....",
    "...LM...",
    "...LM...",
    "....LM..",
    "....LM..",
    "........",
]
# 16x16 gold cup, the sprite of the victory_trophy part
TROPHY = [
    "................",
    "..OOOOOOOOOOOO..",
    "..OWLLLLLLLLMO..",
    ".OOWLLLLLLLLMOO.",
    "O.OLLLLLLLLMMO.O",
    "O.OLLLLLLLMMMO.O",
    ".OOLLLLLLLMMMOO.",
    "..OOLLLLLMMMOO..",
    "...OOLLLLMMOO...",
    "....OOOOOOOO....",
    "......OLMO......",
    "......OLMO......",
    ".....OOLMOO.....",
    "...OOOOOOOOOO...",
    "...OLLXXXXMMO...",
    "...OOOOOOOOOO...",
]

TEMPLATES_8 = {k: v for k, v in dict(globals()).items()
               if k.isupper() and isinstance(v, list) and v and all(isinstance(r, str) and set(r) <= set('.OMLWX')
                                                                    for r in v) and k != 'TROPHY'}
for _name, _t in TEMPLATES_8.items():
    assert len(_t) == 8 and all(len(r) == 8 for r in _t), f'{_name}: 8x8 template expected'
assert len(TROPHY) == 16 and all(len(r) == 16 for r in TROPHY), 'TROPHY: 16x16 template expected'

# --- palettes ------------------------------------------------------------------------------------------------------
P_BROWN = shades('#8A5A2B', light='#B98350', dark='#4A2C12')
P_BROWN2 = shades('#6E4520', light='#A06A38', dark='#3A220C')
P_SOUL = shades('#35D6D0', light='#C8FFFB', dark='#0E6E78')
P_CHERRY = pal(O='#E58AB0', M='#FFB6D0', L='#FFD6E6', W='#FFFFFF', X='#FFFFFF')
P_CHERRY2 = pal(O='#D87AA2', M='#FFA3C4', L='#FFC9DD', W='#FFF0F5', X='#FFFFFF')
P_YEL_STAR = pal(O='#C98A12', M='#FFD93D', L='#FFE98A', W='#FFFBD6', X='#FFFFFF')
P_WHITE_STAR = pal(O='#9AA6C4', M='#DDE6FF', L='#F4F8FF', W='#FFFFFF', X='#FFFFFF')
P_GOLD_STAR = pal(O='#B07A22', M='#E2B04A', L='#F7D27A', W='#FFF1D0', X='#FFF1D0')
P_SPARK = pal(O='#B88A00', M='#FFE14D', L='#FFF6B0', W='#FFFFFF', X='#FFFFFF')
P_INK = pal(O='#05040A', M='#15121C', L='#2E2A3A', W='#4A4458', X='#4A4458')
P_CLOUD = pal(O='#B8C6DC', M='#E2EBF7', L='#FFFFFF', W='#FFFFFF', X='#FFFFFF')
P_SLIME = shades('#6FD43A', light='#B5F27A', dark='#2F7A14')
P_SLIME2 = shades('#58C02E', light='#9BE86A', dark='#276610')
P_LIME_BUBBLE = pal(O='#2F8A1A', M='#7FE04A', L='#B5F27A', W='#F0FFD6', X='#F0FFD6')
P_LIME_BUBBLE2 = pal(O='#3A9A22', M='#93EA5C', L='#C4F78D', W='#F5FFE0', X='#F5FFE0')
P_FUME = shades('#8A3FC8', light='#C08FF0', dark='#3A1458')
P_FUME2 = shades('#6A2FA0', light='#A070D8', dark='#2A0E42')
P_BLUE_BUBBLE = pal(O='#5BC0F0', M='#9ADFFF', L='#D6F3FF', W='#FFFFFF', X='#FFFFFF')
P_BLUE_BUBBLE2 = pal(O='#3FA6E0', M='#7CCBF5', L='#C2EBFF', W='#FFFFFF', X='#FFFFFF')
P_MAPLE_ORANGE = shades('#F08A1A', light='#FFC060', dark='#8A3A06')
P_MAPLE_RED = shades('#D2381C', light='#F07A52', dark='#6A1408')
P_MAPLE_BROWN = shades('#9A5A2A', light='#C88A52', dark='#4A2610')
P_PINK = shades('#FF9CC7', light='#FFD1E6', dark='#C2507F')
P_PINK2 = shades('#F772A8', light='#FFB8D6', dark='#A33A66')
P_RED_HEART = shades('#E8284A', light='#FF7A92', dark='#7A0F26')
P_SPECK_PURPLE = shades('#5A2DA0', light='#9A6AE0', dark='#241048')
P_SPECK_BLUE = shades('#2D4FC8', light='#7A9CFF', dark='#101E6A')
P_SAND = shades('#D9B877', light='#F0D9A0', dark='#8E6A32')
P_SAND2 = shades('#C4A060', light='#E2C88C', dark='#7A5826')
P_LAVA = shades('#FF5A1F', light='#FFC04D', dark='#7A1405')
P_LAVA2 = shades('#E8401C', light='#FF9A3D', dark='#5A0E04')
P_ICE = shades('#9FD8FF', light='#E3F5FF', dark='#4F8FC0')
P_ICE2 = shades('#C6E8FF', light='#FFFFFF', dark='#6FA6CF')
P_SMOKE = pal(O='#5A5F6A', M='#A4AAB4', L='#D4D8DE', W='#EEF0F2', X='#EEF0F2')
P_SMOKE2 = pal(O='#4A4F5A', M='#8E949E', L='#C0C5CC', W='#E2E5E9', X='#E2E5E9')
P_DARK_SPECK = pal(O='#0A0A12', M='#262A36', L='#4A5060', W='#6A7080', X='#6A7080')
P_MAGENTA = shades('#FF2BD6', light='#FF8AEA', dark='#8A0F78')
P_CYAN = shades('#2BFFF0', light='#9CFFF8', dark='#0A7A74')
P_BLACK = pal(O='#000000', M='#0A0A12', L='#22222E', W='#3A3A4A', X='#3A3A4A')
P_GOLD_NOTE = shades('#E2B04A', light='#F7D27A', dark='#7A5313')
P_BLUE_NOTE = shades('#6A92DD', light='#A8C4F5', dark='#2A4A8A')
P_PINK_NOTE = shades('#FF7AC8', light='#FFB8E2', dark='#A33A7A')
P_GREEN_NOTE = shades('#4FD67A', light='#A0F0B8', dark='#1F7A3A')
P_WHITE_NOTE = pal(O='#9AA6C4', M='#E8EEFF', L='#FFFFFF', W='#FFFFFF', X='#FFFFFF')
P_GREEN_LEAF = shades('#5DBB4A', light='#9BE07F', dark='#2E6B24')
P_GREEN_LEAF2 = shades('#3F9A3A', light='#7CCB62', dark='#1F4F1C')
P_GREEN_LEAF3 = shades('#7ACB4A', light='#B5EE86', dark='#3A7A24')
P_GOLD_CUP = pal(O='#7A5313', M='#E2B04A', L='#F7D27A', W='#FFF1D0', X='#1B2E5B')
P_GOLD_COIN = pal(O='#7A5313', M='#E2B04A', L='#F7D27A', W='#FFF1D0', X='#FFF1D0')
P_GOLD_COIN2 = pal(O='#B07A22', M='#F7D27A', L='#FFF1D0', W='#FFFFFF', X='#FFFFFF')


def rgb(c):
    """Palette of one flat-ish colour for the retro pixel / glitch squares."""
    return shades(c)


def fr(*pairs):
    return [sprite(t, p) for t, p in pairs]


def emote(eid):
    """The 16x16 sprite src/emotes/<eid>.png as it is on disk right now (never cached between builds)."""
    path = os.path.join(EMOTES, eid + '.png')
    with Image.open(path) as im:
        im = im.convert('RGBA')
    assert im.size == (16, 16), f'{path}: expected 16x16, got {im.size}'
    return im


# Emote effect: one particle at the emitter (0.5 blocks above the head), pops in over 0.15 s with a small overshoot,
# rises 0.6 blocks with an ease-out (speed 1.25 b/s decaying at drag 2: 1.25 / 2 * (1 - e^-3.2) = 0.6), fades out over
# the last 0.3 s. size is Cobblemon's half-size input: the quad is 2 * size / 1.5 wide (SnowstormParticle.render), so
# 0.45 gives a 0.6 block wide sprite.
EMOTE_LIFE = 1.6
EMOTE_SIZE = ('0.45 * ((0.6 + 0.4 * math.min(1, v.particle_age / 0.15)) '
              '+ 0.12 * math.sin(180 * math.min(1, v.particle_age / 0.3)))')
EMOTE_ALPHA = f'math.clamp(({EMOTE_LIFE} - v.particle_age) / 0.3, 0, 1)'


def emote_fx(eid):
    return dict(frames=[emote(eid)], rate=1, shape=point([0, 0, 0], [0, 1, 0]), life=(EMOTE_LIFE, EMOTE_LIFE),
                size=EMOTE_SIZE, speed=1.25, drag=2, alpha=EMOTE_ALPHA)


EMOTE_IDS = ['emote_laugh', 'emote_skull', 'emote_cry', 'emote_heart_eyes', 'emote_cool', 'emote_angry', 'emote_clown',
             'emote_thinking', 'emote_shock', 'emote_sleep', 'emote_fire', 'emote_hundred', 'emote_gg', 'emote_w',
             'emote_l', 'emote_question', 'emote_exclaim', 'emote_thumbs_up', 'emote_sweat', 'emote_party']

# rain from above the player: the same shape the existing victory_crown_rain uses
RAIN = disc(1.3, 3.2, [0, -1, 0])
SWAY = ['math.cos(v.particle_age * 180 + v.particle_random_3 * 360) * 0.6', -0.35,
        'math.sin(v.particle_age * 180 + v.particle_random_3 * 360) * 0.6']
# a pop: the bubble swells and vanishes in the last part of its life
POP_ALPHA = f'1 - math.pow({AGE}, 6)'


def pop(s):
    return f'{s} * (1 + 0.5 * math.pow({AGE}, 6))'


FLICKER = 'math.sin(v.particle_age * 3000) > -0.4 ? 1 : 0.25'


def spin_wobble(period_deg):
    """Sideways accel that makes a particle swirl; phase differs per particle."""
    return [f'math.cos(v.particle_age * {period_deg} + v.particle_random_3 * 360)',
            f'math.sin(v.particle_age * {period_deg} + v.particle_random_3 * 360)']


def swirl(amp, lift):
    c, s = spin_wobble(540)
    return [f'{c} * {amp}', lift, f'{s} * {amp}']


COIN_W = '0.11 * math.abs(math.cos(v.particle_age * 540 + v.particle_random_3 * 360))'

EFFECTS2 = {eid: emote_fx(eid) for eid in EMOTE_IDS}

EFFECTS2.update({
    # ---- auras (rate = particles/s over a 2.5 s emission, tuned on a Pikachu; build.py scales them to the Pokemon) ----
    'aura_bubble_ring': dict(
        frames=fr((BUBBLE, P_BLUE_BUBBLE), (BUBBLE, P_BLUE_BUBBLE2)), rate=6, max=14,
        shape=point(['math.sin(v.emitter_age * 300) * 0.55', '0.45 + 0.25 * math.sin(v.emitter_age * 540)',
                     'math.cos(v.emitter_age * 300) * 0.55']),
        life=(1.4, 1.8), size=pop(0.17), speed=0.05, accel=[0, 0.3, 0], alpha=POP_ALPHA),
    'aura_rainbow_halo': dict(
        frames=fr(*[(STAR4, shades(c, light='#FFFFFF')) for c in RAINBOW]), rate=10, max=24,
        shape=point(['math.sin(v.emitter_age * 360) * 0.6', 1.45, 'math.cos(v.emitter_age * 360) * 0.6']),
        life=(1.6, 2.0), size=twinkle(0.16), speed=0),
    'aura_melody': dict(
        frames=fr((NOTE, P_GOLD_NOTE), (NOTE2, P_BLUE_NOTE), (NOTE, P_PINK_NOTE), (NOTE2, P_GREEN_NOTE)), rate=4,
        shape=box([0.5, 0.3, 0.5], 0.3, [0, 1, 0]), life=(1.4, 1.8), size=0.18, speed=0.3, drag=0.5,
        accel=['math.sin(v.particle_age * 300 + v.particle_random_3 * 360) * 0.8', 0.6, 0]),
    'aura_toxic_fumes': dict(
        frames=fr((FILLED_BUBBLE, P_LIME_BUBBLE), (SMOKE, P_FUME), (FILLED_BUBBLE, P_LIME_BUBBLE2),
                  (SMOKE, P_FUME2)), rate=7, shape=box([0.5, 0.3, 0.5], 0.3, [0, 1, 0]), life=(1.2, 1.8),
        size=grow(0.17), speed=0.1, accel=[0, 0.5, 0], drag=1, spin=('math.random(0, 360)', 0)),
    'aura_autumn_leaves': dict(
        frames=fr((MAPLE, P_MAPLE_ORANGE), (MAPLE, P_MAPLE_RED), (MAPLE, P_MAPLE_BROWN)), rate=5,
        shape=box([0.6, 0.25, 0.6], 1.0, [0, -1, 0]), life=(1.6, 2.0), size=0.16, speed=0.1, accel=SWAY, drag=1,
        spin=SPIN),
    'aura_lovestruck': dict(
        frames=fr((HEART, P_PINK), (HEART, P_PINK2)), rate=4, shape=box([0.5, 0.3, 0.5], 0.3, [0, 1, 0]),
        life=(1.4, 1.8), size=0.12, speed=0.2, drag=0.8,
        accel=['math.sin(v.particle_age * 240 + v.particle_random_3 * 360) * 0.4', 0.45, 0]),
    'aura_galaxy_dust': dict(
        frames=fr((SPECK, P_SPECK_PURPLE), (SPECK, P_SPECK_BLUE), (SPECK, P_SPECK_PURPLE), (STAR4, P_WHITE_STAR)),
        rate=9, max=24, shape=box([0.6, 0.6, 0.6], 0.6), life=(1.2, 1.8), size=twinkle(0.17), speed=0.04),
    'aura_sandstorm': dict(
        frames=fr((GRAIN, P_SAND), (GRAIN, P_SAND2), (STREAK, P_SAND)), rate=9, max=24,
        shape=box([0.55, 0.45, 0.55], 0.5), life=(0.8, 1.1), size=0.2, speed=0.1, drag=1.5,
        accel=swirl(2.2, 0.15)),

    # ---- send-outs (one burst, about 1 s) ----
    'sendout_bubble_pop': dict(
        frames=fr((BUBBLE, P_BLUE_BUBBLE), (BUBBLE, P_BLUE_BUBBLE2)), rate=22, shape=sphere(0.25, 0.5),
        life=(0.7, 1.1), size=pop(0.26), speed=3, drag=3, alpha=POP_ALPHA),
    'sendout_leaf_tornado': dict(
        frames=fr((LEAF, P_GREEN_LEAF), (LEAF, P_GREEN_LEAF2), (LEAF, P_GREEN_LEAF3)), rate=30,
        shape=sphere(0.15, 0.2), life=(1.0, 1.4), size=0.17, speed=0, accel=swirl(55, 5), drag=3, spin=SPIN),
    'sendout_lava_splash': dict(
        frames=fr((DROP, P_LAVA), (DROP, P_LAVA2)), rate=30, shape=sphere(0.2, 0.4), life=(0.7, 1.1), size=0.15,
        speed=4.5, accel=[0, -9, 0], drag=1),
    'sendout_ice_shatter': dict(
        frames=fr((SHARD, P_ICE), (SHARD_B, P_ICE2), (SHARD, P_ICE2)), rate=26, shape=sphere(0.2, 0.5),
        life=(0.6, 1.0), size=0.2, speed=5, accel=[0, -4, 0], drag=2, spin=SPIN),
    'sendout_heart_burst': dict(
        frames=fr((HEART, P_PINK), (HEART, P_RED_HEART), (HEART, P_PINK2)), rate=24, shape=sphere(0.25, 0.5),
        life=(0.9, 1.3), size=shrink(0.19), speed=3.5, accel=[0, 0.5, 0], drag=2.5),
    'sendout_star_burst': dict(
        frames=fr((STAR5, P_GOLD_STAR), (STAR5, P_WHITE_STAR), (STAR5, P_YEL_STAR)), rate=30,
        shape=sphere(0.2, 0.5), life=(0.8, 1.2), size=shrink(0.2), speed=5.5, drag=3.5, spin=SPIN),
    'sendout_smoke_bomb': dict(
        frames=fr((SMOKE, P_SMOKE), (SMOKE, P_SMOKE2), (SMOKE, P_SMOKE), (DUST, P_DARK_SPECK)), rate=26,
        shape=sphere(0.3, 0.5), life=(0.9, 1.4), size=grow(0.3), speed=2.5, accel=[0, 0.3, 0], drag=3,
        spin=('math.random(0, 360)', 0)),
    'sendout_rainbow_arc': dict(
        frames=fr(*[(DUST, shades(c)) for c in RAINBOW]), rate=40,
        shape=sphere(0.2, 0.4, ['math.random(-0.7, 0.7)', 'math.random(1.2, 1.8)', 'math.random(-0.7, 0.7)']),
        life=(0.9, 1.3), size=0.2, speed=5.5, accel=[0, -6, 0], drag=0.8),
    'sendout_glitch': dict(
        frames=fr((SQUARE, P_MAGENTA), (SQUARE, P_CYAN), (SQUARE, P_BLACK), (BAR, P_MAGENTA), (BAR, P_CYAN),
                  (CHUNK, P_BLACK)), rate=30, shape=sphere(0.3, 0.5), life=(0.5, 0.9), size=0.2, speed=3.5,
        drag=2.5, alpha=FLICKER),
    'sendout_emoji_party': dict(
        frames=[emote('emote_laugh')], rate=16, shape=sphere(0.25, 0.5), life=(1.0, 1.4), size=0.28, speed=4,
        accel=[0, -1.5, 0], drag=3),

    # ---- victory (about 2 s, around the player) ----
    'victory_trophy': dict(
        frames=fr((STAR5, P_GOLD_STAR), (STAR4, P_WHITE_STAR), (STAR4, P_GOLD_STAR)), rate=24,
        shape=disc(0.5, 0.6, [0, 1, 0], surface=True), life=(1.2, 1.6), size=twinkle(0.14), speed=1.5, drag=1.5,
        part='cup'),
    'victory_confetti_cannon': dict(
        frames=fr(*[(CONFETTI, shades(c)) for c in RAINBOW], (STREAMER, shades('#FF5555')),
                  (STREAMER, shades('#55E6E6'))), rate=50,
        shape=sphere(0.15, 0.3, ['math.random(-0.5, 0.5)', 'math.random(2, 3)', 'math.random(-0.5, 0.5)']),
        life=(1.4, 2.0), size=0.13, speed=7, accel=[0, -3, 0], drag=1.5,
        spin=('math.random(0, 360)', 'math.random(-360, 360)')),
    'victory_laugh_rain': dict(
        frames=[emote('emote_laugh')], rate=12, shape=RAIN, life=(1.2, 1.6), size=0.27, speed=1,
        accel=[0, -2.5, 0], drag=0.5),
    'victory_gg_rain': dict(
        frames=[emote('emote_gg')], rate=12, shape=RAIN, life=(1.2, 1.6), size=0.3, speed=1, accel=[0, -2.5, 0],
        drag=0.5),
    'victory_fanfare': dict(
        frames=fr((NOTE, P_GOLD_NOTE), (NOTE2, P_WHITE_NOTE), (NOTE, P_WHITE_NOTE), (NOTE2, P_GOLD_NOTE)), rate=28,
        shape=sphere(0.3, 0.3, ['math.random(-0.8, 0.8)', 'math.random(1, 2)', 'math.random(-0.8, 0.8)']),
        life=(1.3, 1.8), size=0.2, speed=4.5, accel=[0, 0.4, 0], drag=2.5),
    'victory_heart_rain': dict(
        frames=fr((HEART, P_PINK), (HEART, P_PINK2)), rate=18, shape=RAIN, life=(1.2, 1.6), size=0.17, speed=0.8,
        accel=['math.sin(v.particle_age * 200 + v.particle_random_3 * 360) * 0.5', -2, 0], drag=0.5),
    'victory_star_shower': dict(
        frames=fr((STAR5, P_YEL_STAR), (STAR5, P_WHITE_STAR)), rate=26, shape=disc(1.4, 3.3, [0, -1, 0]),
        life=(1.1, 1.5), size=twinkle(0.17), speed=0.6, accel=[0, -3.5, 0], drag=0.5, spin=SPIN),
    'victory_rainbow_burst': dict(
        frames=fr(*[(DUST, shades(c)) for c in RAINBOW]), rate=48, shape=disc(0.25, 0.5, 'outwards', surface=True),
        life=(1.0, 1.4), size=0.2, speed=4.5, drag=2.5),

    # ---- trails (small, short-lived) ----
    'trail_paw_prints': dict(
        frames=fr((PAW, P_BROWN), (PAW, P_BROWN2)), rate=1, life=(1.2, 1.5), size=0.14, speed=0, y=0.1),
    'trail_soul_steps': dict(
        frames=fr((SOUL, P_SOUL)), rate=2, life=(0.7, 1.0), size=shrink(0.16), speed=0.1, accel=[0, 0.5, 0]),
    'trail_cherry_petals': dict(
        frames=fr((CHERRY, P_CHERRY), (CHERRY, P_CHERRY2)), rate=2, life=(0.9, 1.3), size=0.13, speed=0.1,
        accel=['math.sin(v.particle_age * 240 + v.particle_random_3 * 360) * 0.4', -0.25, 0], drag=1, spin=SPIN,
        y=0.4),
    'trail_stars': dict(
        frames=fr((STAR5, P_YEL_STAR)), rate=2, life=(0.7, 1.0), size=twinkle(0.12), speed=0.05,
        accel=[0, 0.2, 0], y=0.2),
    'trail_coins': dict(
        frames=fr((COIN, P_GOLD_COIN), (COIN, P_GOLD_COIN2)), rate=2, life=(0.7, 1.0), size=[COIN_W, 0.11],
        speed=1.2, accel=[0, -4, 0], direction=[0, 1, 0]),
    'trail_sparks': dict(
        frames=fr((ZIG, P_SPARK), (BIT, P_SPARK)), rate=2, life=(0.4, 0.7), size=0.15, speed=0.6, drag=3,
        alpha=FLICKER, y=0.2),
    'trail_ink_drops': dict(
        frames=fr((SPLAT, P_INK), (SPLAT_B, P_INK)), rate=2, life=(1.0, 1.4), size=0.13, speed=0, y=0.1),
    'trail_clouds': dict(
        frames=fr((CLOUD, P_CLOUD)), rate=2, life=(0.8, 1.2), size=grow(0.17), speed=0.05, accel=[0, 0.1, 0], y=0.15),
    'trail_slime': dict(
        frames=fr((BLOB, P_SLIME), (BLOB_B, P_SLIME2)), rate=2, life=(1.0, 1.4), size=shrink(0.16), speed=0, y=0.1),
    'trail_laugh': dict(
        frames=[emote('emote_laugh')], rate=1, life=(0.8, 1.1), size=0.15, speed=0.5, drag=1, direction=[0, 1, 0]),
    'trail_pixel_dust': dict(
        frames=fr(*[(s, rgb(c)) for c in ('#FF3B3B', '#3BFF6B', '#3B7BFF') for s in (SQUARE, PLUS)]), rate=3,
        life=(0.5, 0.8), size=0.1, speed=0.2, alpha=FLICKER, y=0.2),
    'trail_toxic': dict(
        frames=fr((FILLED_BUBBLE, P_LIME_BUBBLE), (FILLED_BUBBLE, P_LIME_BUBBLE2)), rate=2, life=(0.8, 1.2),
        size=0.13, speed=0.2, accel=[0, 0.4, 0], direction=[0, 1, 0]),

    # ---- emoji effects (16x16 emote sprites) ----
    # laughing faces circle the Pokemon: the emitter walks a ring (0.8 laps/s), each face stays where it spawned
    'aura_laughing_fit': dict(
        frames=[emote('emote_laugh')], rate=5, max=12,
        shape=point(['math.sin(v.emitter_age * 290) * 0.6', 0.55, 'math.cos(v.emitter_age * 290) * 0.6']),
        life=(1.3, 1.6), size=0.27, speed=0),
    # skulls rise slowly and fade out
    'aura_dead_inside': dict(
        frames=[emote('emote_skull')], rate=2.5, max=8, shape=box([0.5, 0.2, 0.5], 0.2, [0, 1, 0]),
        life=(1.8, 2.2), size=0.26, speed=0.1, accel=[0, 0.25, 0]),
    # heart-eyes faces drift sideways around the body and bob
    'aura_smitten': dict(
        frames=[emote('emote_heart_eyes')], rate=2.5, max=8, shape=box([0.55, 0.35, 0.55], 0.5),
        life=(1.8, 2.2), size=0.27, speed=0.05, drag=0.8,
        accel=['math.cos(v.particle_age * 200 + v.particle_random_3 * 360) * 0.5',
               'math.sin(v.particle_age * 420 + v.particle_random_3 * 360) * 0.7',
               'math.sin(v.particle_age * 200 + v.particle_random_3 * 360) * 0.5']),
    # flames shoot up from the body and flicker
    'aura_on_fire': dict(
        frames=[emote('emote_fire')], rate=5, max=12, shape=box([0.4, 0.2, 0.4], 0.3, [0, 1, 0]),
        life=(0.7, 1.0), size=f'0.27 * (0.85 + 0.15 * math.sin(v.particle_age * 1800)) * (1 - 0.5 * {AGE})',
        speed=0.6, accel=[0, 1.4, 0], drag=0.5),
    'sendout_skull_pop': dict(
        frames=[emote('emote_skull')], rate=16, shape=sphere(0.25, 0.5), life=(0.9, 1.3), size=0.26, speed=4.5,
        accel=[0, -2, 0], drag=3),
    'victory_hundred_rain': dict(
        frames=[emote('emote_hundred')], rate=12, shape=RAIN, life=(1.2, 1.6), size=0.3, speed=1,
        accel=[0, -2.5, 0], drag=0.5),
    'trail_skulls': dict(
        frames=[emote('emote_skull')], rate=1, life=(0.8, 1.1), size=0.12, speed=0.4, drag=1, direction=[0, 1, 0]),
})
assert len(EFFECTS2) == 65, len(EFFECTS2)

# second emitters (see build.py PARTS): the trophy that rises over the winner
PARTS2 = {
    'victory_trophy_cup': dict(
        frames=[sprite(TROPHY, P_GOLD_CUP)], rate=1, shape=point([0, 0.6, 0], [0, 1, 0]), life=(1.8, 1.8),
        size='0.55 * math.min(1, v.particle_age * 4)', speed=3.2, drag=1.6, facing='rotate_y',
        alpha='v.particle_age < 1.3 ? 1 : 1 - (v.particle_age - 1.3) / 0.5'),
}
