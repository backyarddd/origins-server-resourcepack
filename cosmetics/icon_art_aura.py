"""Aura icons (see icon_art.py for the template rules). The aura alone: no wearer, no object, no body outline (owner
2026-10-27). The hero sprite 7-10 px with 2-4 smaller copies placed the way the particles move."""
from cosmetics import art_fx2 as fx
from cosmetics import build as cb
from cosmetics.icon_art_base import P_LAUGH, P_SKULL, drawn, rainbow, relabel

# FLAME in P_ORANGE (upper case) and P_RED_ORANGE (lower case); it rises (accel +0.8) and shrinks with age, so one big
# flame low down and smaller wisps climbing above it, the smallest at the top
EMBER_WISPS = [
    "................",
    "......W......W..",
    "......LW.....L..",
    ".....MLW...w....",
    ".....OMO...lw...",
    "..........mlw...",
    ".........mlwwl..",
    ".....W...mlwlm..",
    "....LW...omllo..",
    "...MLW....omo...",
    "..MLWWL.........",
    ".MLWWWLM........",
    ".MLWWWLM........",
    ".OMLWLMO........",
    "..OMMMO.........",
    "................",
]

# emote_laugh: one big laughing face (squeezed-shut > < eyes, open grin, tears flying) with small copies popping up
# round it, spread over the body like the effect's box emitter
LAUGHING_FIT = [
    "................",
    "..DE......DDEE..",
    ".FEEF....DFEEFH.",
    ".EIIH....EFFFFH.",
    "..EH.....EFIIFH.",
    "..........EEHH..",
    "....DDEEEE......",
    "...DEEEEEEE.....",
    ".B.DFEEEEFEH.B..",
    ".ABEDFEEFDEHBA..",
    ".A.DFEEEEFEH..A.",
    "...EFFFFFFHH....",
    "...EFGGGGFHH....",
    "....FIIIIFH.....",
    ".....HHHHH......",
    "................",
]

# FLAKE in P_ICE (upper case) and P_ICE2 (lower case): flakes that sink slowly (accel -0.15) and spin, drifting down
# from the big one at the top left to the small ones below and right
FROST_MOTES = [
    "................",
    ".....W......W...",
    "..W..L..M..WWM..",
    "...L.L.M....M...",
    "....LWM.........",
    ".WLLWWWMMO......",
    "....LMM.........",
    "...M.M.O........",
    "..M..M..O..w....",
    ".....O.....l.l..",
    "..........lwm...",
    "...w....wlwwwmo.",
    "..wwm.....mmm...",
    "...m.....m.m.o..",
    "...........o....",
    "................",
]

# ZAP + SPARK in P_YELLOW: crackling in place (drag 3, size flickering, turned in 90 degree steps), so one big bolt with
# sparks of three sizes scattered round it
STATIC_FIELD = [
    "................",
    "........WLM.L.L.",
    ".......WLM...W..",
    "......WLM...L.L.",
    ".....WLM........",
    "....WLLLLLM.....",
    "....OMMWLMO.....",
    "......WLM.......",
    ".....WLM........",
    "....WLM...L...L.",
    "...WLM.....M.M..",
    "..WLM.......W...",
    "..LM..L.L..M.M..",
    "..M....W..L...L.",
    "......L.L.......",
    "................",
]

# PETAL in P_PINK (upper case) and P_PINK2 (lower case): petals that fall (accel -0.35) swaying side to side, so a
# zigzag down from the top right through the big petal (soft, lit at its tip) to the bottom right
PETAL_DRIFT = [
    "................",
    "............llm.",
    "...........lwlm.",
    "...........llmo.",
    "......LWWM.mo...",
    "....LLWLLM......",
    "...LLLLLMM......",
    "...LLLLLMO......",
    "..LLLLMMO.......",
    "..LLLMMOO.......",
    ".LLLMMOO...LLL..",
    ".LLMMO.....LWLM.",
    ".LMO........LMM.",
    ".............MO.",
    "................",
    "................",
]

# SMOKE in P_SHADOW (upper case) and P_SHADOW2 (lower case): puffs that rise (accel +0.25) and grow with age, so a small
# puff low down, a bigger one above it and the biggest at the top
SHADOW_SMOKE = [
    "................",
    "....LLL.........",
    "...LWWLM.LLM....",
    "..LWWLLMLWLMM...",
    ".LWLLLMMMLMMMM..",
    ".LLLMMMMMMMMMO..",
    "..MMMMMMMMMOO...",
    "...OOMMMOOO.....",
    ".....OOO........",
    "................",
    ".........lll....",
    "........lwllmm..",
    "...LM...lmmmmo..",
    "..LWMM...mooo...",
    "...MO...........",
    "................",
]

# STAR in P_WHITE_STAR (upper case) and P_GOLD_STAR (lower case), twinkling in place (speed 0.05): a big white star, a
# gold one and two small ones scattered
STARLIGHT = [
    "................",
    "......W.....W...",
    "......W....WWM..",
    "......L.....M...",
    ".....LWL........",
    "....LWWWM.......",
    ".WWLWWWWWMMO....",
    "....LWWMM.......",
    ".....LMM...w....",
    "......M....l....",
    "......M...lwm...",
    "..w...O.wlwwwmo.",
    ".wwm......mmm...",
    "..m........m....",
    "...........o....",
    "................",
]

# FLAME in P_CYAN_FIRE (upper case) and P_CYAN_FIRE2 (lower case): rises (accel +0.7) and shrinks like ember_wisps, the
# column leaning the other way: the big flame low on the right, smaller ones climbing up the left and top
GHOST_FLAMES = [
    "................",
    "............W...",
    "...w.......LW...",
    "...lw......OMO..",
    "....lw..........",
    ".w.mlw.....W....",
    ".l.mlwl...WL....",
    ".mlwwlm..WL.....",
    ".omllmo.MLW..W..",
    "..omo...MLWLML..",
    ".......MLWWWLM..",
    "......MLWWWWLM..",
    "......MLWWWWLM..",
    "......OMLWWLMO..",
    ".......OMMMMO...",
    "................",
]

# STAR + SPARK in P_GOLD_STAR, twinkling in place all over the body (box emitter, speed 0.05; owner 2026-10-27: no
# ring): an even field of gold stars and X-sparks of three sizes, no hero, all gold (aura_starlight is a big white star)
SEASON_HALO = [
    "................",
    "....W.....L...L.",
    "....L......M.M..",
    "...LWM......W...",
    ".WLWWWMO...M.M..",
    "...MWM....L...L.",
    "....M...........",
    "....O...W.......",
    ".......LWM.W....",
    "........M..L....",
    ".L...L....LWM...",
    "..M.M...WLWWWMO.",
    "...W......MWM...",
    "..M.M......M....",
    ".L...L.....O....",
    "................",
]

# STAR (P_NEUTRAL_STAR, rainbow-tinted per particle in game) twinkling all over the body (box emitter; owner
# 2026-10-27: no ring): six 4-point stars of three sizes scattered, each one RAINBOW colour (upper case its light,
# lower case its mid, digit its dark tone), red at the top left, clockwise round to violet, yellow in the middle
RAINBOW_HALO = [
    "................",
    "..R........A....",
    ".Rr1.......A....",
    "..1......AAAa2..",
    "......Y....a....",
    "......Y....2....",
    ".....YYy........",
    "...YYYYyy3......",
    ".....yyy.....G..",
    "......y.....Gg4.",
    "...V..3...C..4..",
    "...V......C.....",
    ".VVVv6..CCCc5...",
    "...v......c.....",
    "...6......5.....",
    "................",
]
P_RAINBOW_HALO = {k: v for i, ch in enumerate(('Rr1', 'Aa2', 'Yy3', 'Gg4', 'Cc5', 'Vv6'))
                  for k, v in rainbow(i, ch, 'LMO').items()}

# BUBBLE in P_BLUE_BUBBLE (upper case) and P_BLUE_BUBBLE2 (lower case): bubbles that float up (accel +0.3) and swell
# before they pop, so small ones low down and the big one at the top
BUBBLE_RING = [
    "................",
    ".........OOO....",
    ".......OO...OO..",
    ".......O.WW..O..",
    "......O.W.....O.",
    "......O.W.....O.",
    "......O......LO.",
    ".......O....LO..",
    ".......OO...OO..",
    "..oooo...OOO....",
    ".o.w..o.........",
    ".ow...o..OO.....",
    ".o...lo.OW.O....",
    ".o..llo.O..O....",
    "..oooo...OO.....",
    "................",
]

# NOTE (P_GOLD_NOTE upper case, P_PINK_NOTE p/q/r/s) and NOTE2 (P_BLUE_NOTE lower case): notes that float up (accel
# +0.6) and sway, the beamed pair low on the right, the others climbing up the left and the top
MELODY = [
    "................",
    "...........r....",
    "...........qr...",
    "...........q.q..",
    "...L......rq....",
    "...ML.....qp....",
    "...M.L..........",
    "...M..M.lllllll.",
    "...M....mmmmmmo.",
    "..LM....m.....m.",
    ".LWMM...m.....m.",
    ".MMMO.llm...llm.",
    "..OO.lwmm..lwmm.",
    ".....mmmo..mmmo.",
    "......oo....oo..",
    "................",
]

# FILLED_BUBBLE in P_LIME_BUBBLE (upper case) and SMOKE in P_FUME (lower case): bubbles and fumes rising (accel +0.5)
# and growing, so a small bubble at the bottom, a bigger one and a puff above, the biggest fume at the top
TOXIC_FUMES = [
    "................",
    ".......lll.lm...",
    "......lwwllwlm..",
    ".....lwllmmlmmm.",
    ".....llmmmmmmmo.",
    "......mmmmmmoo..",
    ".......ooooo....",
    "...LLM..........",
    "..WWLMM.........",
    ".LWWLMMO..ll....",
    ".LLLLMMO.lwlmm..",
    ".MMMMMMO.lmmmo..",
    "..MMMMO...ooo...",
    "...OOO.LLM......",
    ".......MMO......",
    "................",
]

# MAPLE in P_MAPLE_ORANGE (upper case), P_MAPLE_RED (lower case) and P_MAPLE_BROWN (a-d): leaves that fall swaying and
# spinning, the big orange one at the top (its body the effect's #F08A1A, lit top left, light veins) and two small
# ones tumbling below it
AUTUMN_LEAVES = [
    "................",
    "......L.........",
    ".....LML........",
    "..L..LLM..M.....",
    "..LM.MLM.MO.....",
    ".LLMMMLMMMLO....",
    "..MMLMLMLMO.....",
    "...MMLLLMO......",
    "..LMMMLMMOO.....",
    "...M..L..O......",
    "......O.....l...",
    ".c.c.b....l.l.m.",
    ".ccdbb....llwmm.",
    "..cbb......lmm..",
    "...a........o...",
    "................",
]

# HEART in P_PINK (upper case) and P_PINK2 (lower case): hearts that float up (accel +0.45) swaying side to side, the
# big one low on the right, smaller ones zigzagging up
LOVESTRUCK = [
    "................",
    "........L.M.....",
    "........MMO.....",
    ".........O......",
    ".ll.mm..........",
    ".lwmmm..........",
    ".lmmmo..........",
    "..mmo...........",
    "...o...LLL.MMM..",
    "......LWWLMMMMM.",
    "......LWLMMMMMO.",
    "......MMMMMMMMO.",
    ".......MMMMMMO..",
    "........MMMMO...",
    ".........MMO....",
    "................",
]

# SPECK in P_SPECK_PURPLE (p/q/r) and P_SPECK_BLUE (b/c/d) with STAR in P_WHITE_STAR (upper case): a twinkling field
# (speed 0.04) of specks of several sizes round one white star
GALAXY_DUST = [
    "................",
    "..........W.....",
    "...p......W.....",
    "..pqp.....L.....",
    ".pqrqp...LWM....",
    "..pqp.WWLWWWMMO.",
    "...p.....LMM....",
    "..........M.....",
    "..b.......M.....",
    ".bcb..b...O.....",
    "..b..bcb........",
    "....bcdcb...p...",
    ".....bcb...pqp..",
    "......b.....p...",
    "................",
    "................",
]

# GRAIN + STREAK in P_SAND (upper case) and P_SAND2 (lower case): sand swirling round and round (sideways accel 2.2,
# small lift), so streaks circling in a funnel with grains thrown out of it
SANDSTORM = [
    "................",
    "................",
    "..OLLLLLWWWM....",
    "...OMMMMMMO..LM.",
    ".............MO.",
    ".....mwwlllllo..",
    ".lm...ommmmmo...",
    ".mo.............",
    "......OLLWWWM...",
    ".......OMMMO.lm.",
    ".............mo.",
    ".....mwwllo.....",
    "......ommo......",
    "........LWM.....",
    ".........O......",
    "................",
]

# emote_skull (P_SKULL as B / C / D): skulls that rise slowly (accel +0.25) and fade, the big one on the right, two
# small ones rising up the left
DEAD_INSIDE = [
    "................",
    "..BBB...........",
    ".BBBBC..........",
    ".BDBDC..........",
    ".CBBBC..BBBBB...",
    "..CDC..BBBBBBBC.",
    "......BBBBBBBBC.",
    "......BBBBBBBBC.",
    "......BDDBBBDDC.",
    "......BDDBBBDDC.",
    "......BBBBDBBBC.",
    "..BBB.CBBBBBBBC.",
    ".BDBDC.CBBBBBC..",
    ".CBBBC.CDBBBDC..",
    "..CDC...CCCCC...",
    "................",
]

# emote_heart_eyes' own colours: heart-eyed faces that drift sideways round the body and bob, the big one at the top
# with small ones bobbing below either side
P_SMITTEN = {'B': (0xFF, 0xE0, 0x7A), 'C': (0xFF, 0xC8, 0x3D), 'D': (0xFF, 0x8A, 0x8C), 'E': (0xE5, 0x38, 0x3B),
             'F': (0xE0, 0x9A, 0x1F), 'G': (0x3B, 0x24, 0x12)}
SMITTEN = [
    "................",
    "......BBCCCC....",
    ".....BBCCCCCC...",
    "....BDCECCDCEF..",
    "....CEEECCEEEF..",
    "....CCECCCCECF..",
    "....CCCCCCCCCF..",
    "....CCGGGGGGFF..",
    "....CCGEEEEGFF..",
    ".....CCGGGGFF...",
    ".......FFFF.....",
    "..BCC.....BCC...",
    ".BECEC...BECEC..",
    ".CGGGF...CGGGF..",
    "..FFF.....FFF...",
    "................",
]

# emote_fire's own colours: flames that shoot up (accel +1.4), flicker and shrink, the big one low down, smaller ones
# above it, the smallest at the top
P_FIRE = {'B': (0xFF, 0x8A, 0x1F), 'C': (0xFF, 0xC8, 0x3D), 'D': (0xFF, 0xFF, 0xFF)}
ON_FIRE = [
    "................",
    "............B...",
    "......B....BBB..",
    "......BB..BBCBB.",
    ".....BCBB.BCDCB.",
    ".....BBB...BBB..",
    ".B..BBB..B......",
    ".BB.BBB.BB......",
    ".BBBBBBBBB......",
    ".BBBBBBBBB......",
    ".BBBBCBBBB......",
    ".BBBCCCBBB......",
    ".BBCCDCCBB......",
    "..BBCDCBB.......",
    "...BBBBB........",
    "................",
]

# emote_wet (fx.P_WET, its outline left to the shared INK outline) + WET_DROP: the splash itself large, drawn as in
# src/emotes/emote_wet.png, with two single drops hopping up below it (the effect pops both up all over the body)
SOAKED = [
    "................",
    "..WLM.....LLM...",
    ".LWLMM...LWLMM..",
    ".LLMMM...LWLMMM.",
    ".LMMMX...LLMMMM.",
    "..MMMX...LMMMMX.",
    "...MX...LMMMLXX.",
    "...M....LMMMXX..",
    ".......LMMXX....",
    "..L...LMX.......",
    "..LM............",
    ".LWMM..L...LWM..",
    ".LMMX.LWM.LMMX..",
    "..XX..MMX..MXX..",
    ".......X........",
    "................",
]

ICONS = {
    'aura_ember_wisps': drawn(EMBER_WISPS, {**relabel(cb.P_ORANGE, 'OMLW'), **relabel(cb.P_RED_ORANGE, 'omlw')}),
    'aura_laughing_fit': drawn(LAUGHING_FIT, P_LAUGH),
    'aura_frost_motes': drawn(FROST_MOTES, {**relabel(cb.P_ICE, 'OMLW'), **relabel(cb.P_ICE2, 'omlw')}),
    'aura_static_field': drawn(STATIC_FIELD, cb.P_YELLOW),
    'aura_petal_drift': drawn(PETAL_DRIFT, {**relabel(cb.P_PINK, 'OMLW'), **relabel(cb.P_PINK2, 'omlw')}),
    'aura_shadow_smoke': drawn(SHADOW_SMOKE, {**relabel(cb.P_SHADOW, 'OMLW'), **relabel(cb.P_SHADOW2, 'omlw')}),
    'aura_starlight': drawn(STARLIGHT, {**relabel(cb.P_WHITE_STAR, 'OMLW'), **relabel(cb.P_GOLD_STAR, 'omlw')}),
    'aura_ghost_flames': drawn(GHOST_FLAMES, {**relabel(cb.P_CYAN_FIRE, 'OMLW'),
                                              **relabel(cb.P_CYAN_FIRE2, 'omlw')}),
    'aura_season_halo': drawn(SEASON_HALO, cb.P_GOLD_STAR),
    'aura_bubble_ring': drawn(BUBBLE_RING, {**relabel(fx.P_BLUE_BUBBLE, 'OMLW'),
                                            **relabel(fx.P_BLUE_BUBBLE2, 'omlw')}),
    'aura_rainbow_halo': drawn(RAINBOW_HALO, P_RAINBOW_HALO),
    'aura_melody': drawn(MELODY, {**relabel(fx.P_GOLD_NOTE, 'OMLW'), **relabel(fx.P_BLUE_NOTE, 'omlw'),
                                  **relabel(fx.P_PINK_NOTE, 'pqrs')}),
    'aura_toxic_fumes': drawn(TOXIC_FUMES, {**relabel(fx.P_LIME_BUBBLE, 'OMLW'), **relabel(fx.P_FUME, 'omlw')}),
    'aura_autumn_leaves': drawn(AUTUMN_LEAVES, {**relabel(fx.P_MAPLE_ORANGE, 'OMLW'),
                                                **relabel(fx.P_MAPLE_RED, 'omlw'),
                                                **relabel(fx.P_MAPLE_BROWN, 'abcd')}),
    'aura_lovestruck': drawn(LOVESTRUCK, {**relabel(fx.P_PINK, 'OMLW'), **relabel(fx.P_PINK2, 'omlw')}),
    'aura_galaxy_dust': drawn(GALAXY_DUST, {**relabel(fx.P_WHITE_STAR, 'OMLW'),
                                            **relabel(fx.P_SPECK_PURPLE, 'pqr', 'MLW'),
                                            **relabel(fx.P_SPECK_BLUE, 'bcd', 'MLW')}),
    'aura_sandstorm': drawn(SANDSTORM, {**relabel(fx.P_SAND, 'OMLW'), **relabel(fx.P_SAND2, 'omlw')}),
    'aura_dead_inside': drawn(DEAD_INSIDE, relabel(P_SKULL, 'BCD', 'WGD')),
    'aura_smitten': drawn(SMITTEN, P_SMITTEN),
    'aura_on_fire': drawn(ON_FIRE, P_FIRE),
    'aura_soaked': drawn(SOAKED, fx.P_WET),
}
