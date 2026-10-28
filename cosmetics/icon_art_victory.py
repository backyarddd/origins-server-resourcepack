"""Victory icons (see icon_art.py for the template rules). The hero (the PARTS sprite, or the effect's emoji / text, or
with no part its main sprite) large in the centre, its particles round it the way they move; a burst behind it only
where the effect bursts (fireworks, confetti_cannon, rainbow_burst). Rain effects (crown, gg, laugh, hundred) show the
falling copies above or round the hero."""
from cosmetics import art_fx2
from cosmetics import build as cb
from cosmetics.art import LIGHT_GOLD, hexrgb, shades
from cosmetics.icon_art_base import P_LAUGH, drawn, rainbow, relabel

# STAR in the fireworks colours (RAINBOW[::2] red / yellow / cyan, and P_GOLD_STAR): the shell bursts at speed 5 and the
# sparks sag under gravity, so the big gold sparkle in the centre with coloured sparks flung out along the diagonals,
# the lower ones dropped a little further
FIREWORKS = [
    "................",
    "..r....W.....y..",
    ".rsr...L....ytY.",
    "..R....L.....Y..",
    "...s...M...t....",
    "......LWM.......",
    ".....LWWWM......",
    ".WLLMWWWWWMMMMO.",
    ".....LWWWM......",
    "......LMM.......",
    "...u...M...v....",
    ".......M........",
    "..u....M.....v..",
    ".uwU...O....vxV.",
    "..U..........V..",
    "................",
]
P_FIREWORKS = {**cb.P_GOLD_STAR, **rainbow(0, 'Rrs'), **rainbow(2, 'Yyt'), **rainbow(4, 'Vvx'),
               **relabel(cb.P_GOLD_STAR, 'Uuw', 'OMW')}

# CROWN in P_GOLD raining from a disc overhead (straight down, each tipped a little by its spin): three small crowns of
# one size falling in a slant from the top left, none bigger than the others (victory_champions_crown is the one big
# crown)
CROWN_RAIN = [
    "................",
    ".W.W.W..........",
    ".LMLML..........",
    ".MXMXM..........",
    ".OOOOO..........",
    "................",
    "......W.W.W.....",
    "......LMLML.....",
    "......MXMXM.....",
    "......OOOOO.....",
    "................",
    "..........W.W.W.",
    "..........LMLML.",
    "..........MXMXM.",
    "..........OOOOO.",
    "................",
]

# PARTS victory_lightning_strike_bolt (BOLT, white core W / yellow L, shaded with P_YELLOW's O) striking the ground,
# with its SPARK crosses (P_YELLOW) thrown up round the strike point
LIGHTNING = [
    "................",
    "..........WLLy..",
    ".........WLLy...",
    "........WLLy....",
    ".......WLLy.....",
    "......WLLLLLLy..",
    ".........WLLy...",
    "........WLLy....",
    ".......WLLy.....",
    "......WLLy......",
    ".....WLLy.l...l.",
    ".l..WLy....m.m..",
    "...WL.......W...",
    "..W.m......m.m..",
    ".l...l....l...l.",
    "................",
]
P_LIGHTNING = {'W': hexrgb('#FFFDE8'), 'L': hexrgb('#FFE14D'), 'y': cb.P_YELLOW['O'],
               **relabel(cb.P_YELLOW, 'oml', 'OML')}

# COIN in P_GOLD (upper case) and the light-gold coin (lower case) falling straight down, flipping as they fall
# (size x = |cos|): the big coin face-on in the middle, small ones round it face-on, half turned and edge-on
COIN_SHOWER = [
    "................",
    "......ooo....l..",
    ".....olwmo...m..",
    ".....olmmo...m..",
    "......ooo....o..",
    "..l.............",
    ".lm....LLLL.....",
    ".lm..LWWLLLLM...",
    ".mo.LWLMMMMMLO..",
    "..o.LWMMLWMMLO..",
    "....LLMMLWMMLO..",
    "....LLMMLWMLMO..",
    "....LMLMMMMLLO..",
    ".....MMLLLLMO...",
    ".......OOOO.....",
    "................",
]
P_COINS = {**cb.P_GOLD, **relabel(shades(LIGHT_GOLD, dark='#B07A22'), 'omlw')}

# PARTS victory_trophy_cup (TROPHY in P_GOLD_CUP, navy name plate) rising, with its ring of star twinkles (STAR4 in
# P_WHITE_STAR and P_GOLD_STAR) rising beside the stem
TROPHY = [
    "................",
    "...OOOOOOOOOO...",
    "...OWLLLLLLMO...",
    ".OOOWLLLLLLMOOO.",
    ".O.OLLLLLLMMO.O.",
    ".O.OLLLLLMMMO.O.",
    "..OOLLLLLMMMOO..",
    "...OOLLLLMMOO...",
    "....OOLLMMOO....",
    "..w..OOOOOO..s..",
    ".wvw..OLMO..sSs.",
    "..w..OOLMOO..s..",
    "...OOOOOOOOOO...",
    "...OLLXXXXMMO...",
    "...OOOOOOOOOO...",
    "................",
]
P_TROPHY = {**art_fx2.P_GOLD_CUP, **relabel(art_fx2.P_WHITE_STAR, 'wv', 'MW'),
            **relabel(art_fx2.P_GOLD_STAR, 'sS', 'MW')}

# CONFETTI (RAINBOW) and the red / cyan STREAMER shot up out of one point (speed 7, aimed up in a narrow cone) before they
# rain back down: a fan of pieces spreading from the bottom centre, the streamers curling up its two edges
CONFETTI_CANNON = [
    "................",
    ".11......33.....",
    ".1rr.....3yy.66.",
    "..rR......yY.6p.",
    "......2o.....pP.",
    ".1r...oO....5c..",
    ".1r.........5c..",
    "..1r.......5c...",
    "..1r..4g...5c...",
    "...1r.gG..5c....",
    "...1r....5c.....",
    "....1r..........",
    "......3y.2o.....",
    "......yY.oO.....",
    "................",
    "................",
]
P_CONFETTI = {**rainbow(0, 'Rr1'), **rainbow(1, 'Oo2'), **rainbow(2, 'Yy3'), **rainbow(3, 'Gg4'), **rainbow(4, 'Cc5'),
              **rainbow(5, 'Pp6')}

# emote_laugh raining from a disc overhead: three faces of one size falling in a zigzag, the emote's own tears
# streaming up off the falling ones (aura_laughing_fit is one big face with small ones popping round it)
LAUGH_RAIN = [
    "................",
    ".........DDEE...",
    "........DFDEFE..",
    ".B....B.DEEEEH..",
    ".A....A.EFGGFH..",
    "........EFIIFH..",
    "..DDEE...HFFH...",
    ".DFDEFE.........",
    ".DEEEEH.B....B..",
    ".EFGGFH.A....A..",
    ".EFIIFH..DDEE...",
    "..HFFH..DFDEFE..",
    "........DEEEEH..",
    "........EFGGFH..",
    "........EFIIFH..",
    ".........HFFH...",
]

# NOTE / NOTE2 in P_GOLD_NOTE (upper case) and P_WHITE_NOTE (lower case) flung up and out (speed 4.5, aimed up, then
# rising): the big gold beamed pair in the middle, single notes flying off above and beside it
FANFARE = [
    "................",
    "..wl.........LL.",
    "..w.l........LM.",
    "..w..........L..",
    ".ww.........LL..",
    ".wm.........MO..",
    "....LLLLLLLL....",
    "....LMMMMMMO....",
    "....L......M....",
    "....L......M....",
    "....L......M....",
    "..LLL....LLM....",
    ".LWMM...LWMM....",
    ".MMMO...MMMO....",
    "..OO.....OO.....",
    "................",
]

# HEART in P_PINK (upper case) and P_PINK2 (lower case) raining down and swaying side to side: the big heart in the
# middle, small ones above it drifting off to either side
HEART_RAIN = [
    "................",
    ".ll.mm..........",
    ".lwmmo......l.m.",
    "..mmo.......mmo.",
    "...o.........o..",
    "................",
    "...LLL...MMM....",
    "..LWWWL.MMMMM...",
    "..LWWLMMMMMMO...",
    "..LWLMMMMMMMO...",
    "..LMMMMMMMMMO...",
    "...MMMMMMMMO....",
    "....MMMMMMO.....",
    ".....MMMMO......",
    "......MOO.......",
    "................",
]

# STAR5 in P_YEL_STAR (upper case) and P_WHITE_STAR (lower case) falling fast, spinning and twinkling: the big star in
# the middle, small ones falling round it at different sizes (the smallest, mid-twinkle, is just a glint)
STAR_SHOWER = [
    "................",
    "...w............",
    ".wwwwm......L...",
    "..wwm.....LLWMO.",
    "..w.m......LMO..",
    "...........L.O..",
    "......W.........",
    ".....LWM........",
    ".LLLLLWMMMMO....",
    "..LWWWWMMMO.....",
    "...LWWMMMO......",
    "...LWMMMMO...w..",
    "..LWMMOMMMO.wwm.",
    "..LMO...OMO..m..",
    "..OO.....OO.....",
    "................",
]

# DUST in RAINBOW pushed out flat in a ring (disc surface, speed 4.5): the six colours in order round an expanding ring,
# each with a smaller puff behind it on the same ray
RAINBOW_BURST = [
    "................",
    "................",
    ".....1r....2o...",
    "....1rr...2oo...",
    "....rrR...ooO...",
    "................",
    ".......r.o......",
    "...6p........3y.",
    "..6pp.p...y.3yy.",
    "..ppP.......yyY.",
    ".......c.g......",
    "................",
    ".....5c....4g...",
    "....5cc...4gg...",
    "....ccC...ggG...",
    "................",
]

# emote_hundred raining down: the big red 100 with its two underline bars in the middle, a smaller one falling above it
# (the dark plate between the strokes is left to the shared INK outline)
HUNDRED_RAIN = [
    "................",
    "......b.bbb.bbb.",
    ".....cc.c.c.c.c.",
    "......c.c.c.c.c.",
    "......d.ddd.ddd.",
    "................",
    "..b..bbbb.bbbb..",
    ".cc..c..c.c..c..",
    "..c..c..c.c..c..",
    "..c..c..c.c..c..",
    ".ddd.dddd.dddd..",
    "................",
    ".ccccccccccccc..",
    "................",
    ".ddddddddddddd..",
    "................",
]
# d: emote_hundred's #A8191C lifted to #C42A2E (luminance >= 80), else icons.dark_patch reads the strokes as dark art
# and rims them in RIM
P_HUNDRED = {'b': hexrgb('#FF8A8C'), 'c': hexrgb('#E5383B'), 'd': hexrgb('#C42A2E')}

# PARTS victory_champions_crown_crown (BIG_CROWN in P_GOLD, navy jewels) rising in the centre, and the ring of
# STAR / SPARK / STAR particles it throws (P_GOLD_STAR o g S c, P_WHITE_STAR u w v) arching over it: one big crown
CHAMPIONS_CROWN = [
    "................",
    ".......S.S......",
    "...c....c...v...",
    "...S...S.g..w...",
    ".cScgo.....vvvwu",
    "...g........w...",
    "...o........u...",
    "................",
    "..W....WW....W..",
    "..L....LW....M..",
    "..LM..LLMM..MM..",
    "..LWLLLWWLLLWM..",
    "..LXLLLXXLLLXM..",
    "..MMMMMMMMMMMM..",
    "..OOOOOOOOOOOO..",
    "................",
]

# emote_gg raining down: the big GG in the centre, a smaller one still falling above it (a second small copy merges
# with the first into one blob at 16 px)
GG_RAIN = [
    "................",
    "........BBB.BBB.",
    "........C...C...",
    "........C.C.C.C.",
    "........DDD.DDD.",
    "................",
    "................",
    "..BBBB...BBBB...",
    ".BB..BB.BB..BB..",
    ".CC.....CC......",
    ".CC.CCC.CC.CCC..",
    ".CC..CC.CC..CC..",
    ".DD..DD.DD..DD..",
    "..DDDD...DDDD...",
    "................",
    "................",
]

# src/emotes/emote_gg.png's own golds (its dark outline is left to the shared INK outline)
P_GG = {'B': (0xFF, 0xE0, 0x7A), 'C': (0xFF, 0xC8, 0x3D), 'D': (0xE0, 0x9A, 0x1F)}

ICONS = {
    'victory_fireworks': drawn(FIREWORKS, P_FIREWORKS),
    'victory_crown_rain': drawn(CROWN_RAIN, cb.P_GOLD),
    'victory_lightning_strike': drawn(LIGHTNING, P_LIGHTNING),
    'victory_coin_shower': drawn(COIN_SHOWER, P_COINS),
    'victory_trophy': drawn(TROPHY, P_TROPHY),
    'victory_confetti_cannon': drawn(CONFETTI_CANNON, P_CONFETTI),
    'victory_laugh_rain': drawn(LAUGH_RAIN, P_LAUGH),
    'victory_fanfare': drawn(FANFARE, {**art_fx2.P_GOLD_NOTE, **relabel(art_fx2.P_WHITE_NOTE, 'omlw')}),
    'victory_heart_rain': drawn(HEART_RAIN, {**art_fx2.P_PINK, **relabel(art_fx2.P_PINK2, 'omlw')}),
    'victory_star_shower': drawn(STAR_SHOWER, {**art_fx2.P_YEL_STAR, **relabel(art_fx2.P_WHITE_STAR, 'omlw')}),
    'victory_rainbow_burst': drawn(RAINBOW_BURST, {**rainbow(0, 'Rr1'), **rainbow(1, 'Oo2'), **rainbow(2, 'Yy3'),
                                                   **rainbow(3, 'Gg4'), **rainbow(4, 'Cc5'), **rainbow(5, 'Pp6')}),
    'victory_hundred_rain': drawn(HUNDRED_RAIN, P_HUNDRED),
    'victory_champions_crown': drawn(CHAMPIONS_CROWN, {**cb.P_GOLD, **relabel(cb.P_GOLD_STAR, 'ogSc'),
                                                       **relabel(cb.P_WHITE_STAR, 'uwv', 'OMW')}),
    'victory_gg_rain': drawn(GG_RAIN, P_GG),
}
