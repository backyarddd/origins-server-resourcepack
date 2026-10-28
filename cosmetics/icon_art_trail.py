"""Trail icons (see icon_art.py for the template rules). The effect's sprites laid along a ground path that recedes from
the bottom-left (large, near) to the top-right (small, far)."""
from cosmetics import art_fx2
from cosmetics import build as cb
from cosmetics.art import GOLD, shades
from cosmetics.icon_art_base import P_LAUGH, P_SKULL, drawn, rainbow, relabel

# HEART in the two trail_hearts palettes (build.py EFFECTS: shades('#FF5577'), shades('#FF8FB1')) upper / lower case.
# Each step pops a heart that floats up a little, so they hang just above the path, the nearest one biggest.
HEARTS = [
    "................",
    "............L.M.",
    "............MMM.",
    ".............M..",
    "..........L.M...",
    ".........LWMMM..",
    "..........MMO...",
    "...........O....",
    "..LLL.MMM.......",
    ".LWWLMMMMM......",
    ".LWLMMMMMO......",
    "..MMMMMMO.......",
    "...MMMMO........",
    "....MMO.........",
    ".....O..........",
    "................",
]

# PAW in P_BROWN (upper case) and P_BROWN2 (lower case), flat on the ground (speed 0): left / right prints in turn,
# smaller the further up the path
PAW_PRINTS = [
    "................",
    ".....L.L........",
    "....L...L.......",
    ".....LLM........",
    ".....MMM..l.l...",
    ".........l...l..",
    "..........llm...",
    ".........lllll..",
    "...LM.LM..lml...",
    "...MM.MM........",
    ".LM.....LM......",
    ".MM.LLM.MM......",
    "...LWLLM........",
    "..LLMMMMM.......",
    "...MMMMM........",
    "................",
]

# DUST embers in P_ORANGE that rise (accel +0.5) and shrink: a big ember on the path, smaller ones up it, a
# SPARK above each of the nearer two
EMBER_STEPS = [
    "................",
    ".......L.L......",
    "........W...L...",
    ".......L.L.LWM..",
    "..L.L.......MO..",
    "...W.....LM.....",
    "..L.L...LWMM....",
    "........MMMO....",
    "...LM....MO.....",
    "..LWWM..........",
    ".LWWMMM.........",
    ".LWMMMO.........",
    "..MMMO..........",
    "...MO...........",
    "................",
    "................",
]

# LEAF in P_LEAF (upper case) and P_LEAF2 (lower case), sinking (accel -0.2) and spun: a big leaf lying on the path,
# a smaller one turned the other way further up, one still falling
LEAF_STEPS = [
    "................",
    "................",
    "......LW........",
    ".....LWM..wl....",
    "....OMO...lwll..",
    "..........lmwmm.",
    "...........mmwo.",
    "..............o.",
    ".........LW.....",
    ".......LLWM.....",
    ".....LLLWMM.....",
    "....LLLWMMO.....",
    "...LLLWMMO......",
    "...LLWMOO.......",
    "..O.............",
    "................",
]

# DUST puffs in RAINBOW order (red '1Rr' .. violet '6Vv' as O / M / L), each step one colour: a ribbon of
# overlapping puffs, red nearest and biggest, violet far and smallest, a few loose specks drifting up off it
RAINBOW = [
    "................",
    "............vV..",
    "..........ccV6..",
    "......G...cCC...",
    "........gg.C5...",
    "......yygGG.....",
    "..y..yyYYG4.....",
    "....aaYY3...V...",
    "...aaAA3........",
    "..rrRA2.........",
    ".rwrRR..C.......",
    ".rrRRR..........",
    ".RRRR1..........",
    "..RR1...........",
    "................",
    "................",
]

# NOTE in gold (upper case), blue (lower case) and pink ('1234' = O / M / L / W), launched straight up (direction
# up, speed 0.4): one note per step, each further one smaller and floating higher
MUSIC_NOTES = [
    "................",
    "........34......",
    "........3.......",
    ".......32...lw..",
    ".......2....lm..",
    ".....LW.....l...",
    ".....LMW....l...",
    ".....L.M..lll...",
    ".....L...lwmm...",
    ".....L....mo....",
    ".....L..........",
    "..LLLL..........",
    ".LWMMM..........",
    ".LMMMO..........",
    "..MMO...........",
    "................",
]

# STAR in P_WHITE_STAR (upper case) and P_GOLD_STAR (lower case), twinkling in place (speed 0.05): a scattered
# field along the path, a big white star near, gold and white ones smaller further up, two pin-point glints
SPARKLES = [
    "................",
    ".............W..",
    "......W.....WWM.",
    ".............M..",
    "................",
    "..........w.....",
    ".....W....l.....",
    ".....W..wlwmo...",
    ".....L....m.....",
    "....LWL...o.....",
    ".WWLWWWMMO......",
    "....LWM.....w...",
    ".....M..........",
    ".....M..........",
    ".....O..........",
    "................",
]

# FLAKE in P_SNOW (upper case) and P_ICE2 (lower case), drifting down slowly (accel -0.15) from waist height
# (y 0.35): flakes hanging over the path, one sinking below the line, specks under them
SNOWFALL = [
    "................",
    ".............w..",
    "........l.l.l...",
    ".........lwl....",
    "........lwwwm...",
    ".M..W..M.lwm....",
    "..W.W.W.l.m.o...",
    "...WWW..........",
    ".WWWWWWW........",
    "...WWW......W...",
    "..W.W.M....WWW..",
    ".M..W..O....W...",
    "................",
    "....W...........",
    "................",
    "................",
]

# BUBBLE rings in P_BUBBLE (hollow, highlight inside top-left) rising straight up (direction up, accel +0.3): a big
# ring near, a smaller one further up, and a small one climbing above each
BUBBLES = [
    "................",
    "............O...",
    "...........O.O..",
    ".....O......O...",
    "....O.O.........",
    ".....O....OOO...",
    ".........OW..O..",
    ".........OW..O..",
    "...OOO...O..LO..",
    "..O...O...OOO...",
    ".O.W...O........",
    ".O.W...O........",
    ".O.....O........",
    "..O..LO.........",
    "...OOO..........",
    "................",
]

# PUMPKIN (jack-o'-lantern, glowing W face, X stem) in P_PUMPKIN and DUST in P_ORANGE (lower case), drifting up
# (accel +0.3): a big lantern near, a small one further up, orange dust bits rising
PUMPKIN_STEPS = [
    "................",
    ".............l..",
    ".......l........",
    "......lwm..X....",
    ".......mo.LMM...",
    ".........LWMWM..",
    ".........LWWWO..",
    ".....XX...MOO...",
    "...LLMXMM.......",
    "..LLWMMLMM......",
    ".LLWWMLWWM......",
    ".LLLLMMMMO......",
    ".LWMWMWMWO......",
    "..LWWWWWO.......",
    "...OOOOO........",
    "................",
]

# FLAME in P_BLUE_FIRE (upper case) and P_GOLD_STAR (lower case) in turn, rising (accel +0.6) and shrinking: a
# big blue flame near, a gold one further up, a small blue tip far off
ARENA_FLAME = [
    "................",
    ".............W..",
    "............LW..",
    "...........MLWM.",
    "............OMO.",
    "..........w.....",
    "...L......lw.l..",
    "...LW..L..lwlm..",
    "..MLW.LM.mlwwm..",
    "..MLWLWM.mlwwm..",
    ".MLWWWLM.omllo..",
    ".MLWWWLM..omo...",
    ".MLWWWLM........",
    ".OMLWLMO........",
    "..OMMMO.........",
    "................",
]

# STAR in P_GREEN_STAR (upper case) and P_GOLD_STAR (lower case), twinkling in place: a big green star near,
# a gold one high up the path, a small green one sunk lower right, a gold glint
SUPPORTER_SPARKLES = [
    "................",
    "..........w.....",
    "..........l.....",
    "...w.....lwl....",
    ".......wlwwwmo..",
    ".........lwm....",
    "..........m.....",
    "....W.....o.....",
    "....L...........",
    "...LWL.....W....",
    ".WLWWWMO..WWM...",
    "...LWM.....M....",
    "....M...........",
    "....O...........",
    "................",
    "................",
]

# SOUL wisps in P_SOUL, rising (accel +0.5) and shrinking: teal flames whose tips curl, the near one big, the far
# one smaller and higher, a spark of soul still climbing
SOUL_STEPS = [
    "................",
    "................",
    ".............M..",
    "...........M....",
    "..........M.....",
    ".........MLM....",
    ".....M...LWM.M..",
    "....M....LWWMM..",
    "...MLM...MLWMO..",
    "..MLWM.M..OMO...",
    "..MLWLMM........",
    ".MLWWWLM........",
    ".MLWWWLM........",
    ".MLWWLMO........",
    "..OMMMO.........",
    "................",
]

# CHERRY petals (notched end) in P_CHERRY (upper case) and P_CHERRY2 (lower case), drifting down and swaying
# from y 0.4: petals at different turns hanging over the path, one sunk below it
CHERRY_PETALS = [
    "................",
    "................",
    ".........ll.....",
    "........lwll....",
    "....ll..llmmm...",
    "...lm....mmo.m..",
    "................",
    "................",
    "..LL............",
    ".LWWL...........",
    ".LWLLM.....LL...",
    "..LLMMM...LMM...",
    "...LMMMMM..M....",
    "....MMO.M.......",
    "................",
    "................",
]

# STAR5 in P_YEL_STAR, twinkling as it rises a little (accel +0.2): a big five-point star near, two smaller ones
# further up and to the side
STARS = [
    "................",
    "................",
    "...........L....",
    "..........LWM...",
    "........LLLWMMO.",
    ".........LWWMO..",
    ".....L...LMOMO..",
    "....LWM..O...O..",
    ".LLLLWMMMO......",
    "..LWWWWMO.......",
    "...LWWMO....L...",
    "...LWMMO..LLWMO.",
    "..LMO.MMO..LMO..",
    "..MO...MO..M.O..",
    "................",
    "................",
]

# COIN in P_GOLD_COIN (upper case) and P_GOLD_COIN2 (lower case), hopped up (speed 1.2, accel -4) while it spins
# (width = |cos|): a coin face-on on the path, one edge-on at the top of its hop, two smaller landing further on
COINS = [
    "................",
    "............lm..",
    "........l...mo..",
    ".......lwm......",
    ".......lwm......",
    ".......lwm......",
    "........m...LM..",
    "...........LWLM.",
    "...LLM.....LLMO.",
    "..LWWLM.....MO..",
    ".LWMMMLM........",
    ".LWMLMLO........",
    ".LLMMMMO........",
    "..LMMMO.........",
    "...MOO..........",
    "................",
]

# ZIG bolts and BIT chips in P_SPARK, flung a short way (speed 0.6, drag 3) and flickering: a big bolt near,
# smaller bolts further up, chips scattered round them
SPARKS = [
    "................",
    "..............W.",
    "....LL.......WL.",
    "....MM....WL..L.",
    ".........WL.....",
    "........WWWL....",
    ".....WL...L.....",
    "....WL...L..LL..",
    "...WL.......MM..",
    "..WWWWL.........",
    "....WL..........",
    "...WL...LL......",
    "..WL....MM......",
    "..L.............",
    "................",
    "................",
]

# SPLAT and SPLAT_B in P_INK, flat on the ground (speed 0): the big round splat near, stubby spikes and a flung drop
# round it and a wet gloss top left, a smaller splat up the path; the shared outline rims them in RIM so they read on
# the dark slot
INK_DROPS = [
    "................",
    "...........O....",
    "..........OMMO..",
    "..........MWMO..",
    "...........MO...",
    "................",
    "....O...O.......",
    "...OMMMMMO......",
    ".OOMWLMMMMO.....",
    "...MLLMMMMO.....",
    "...MLMMMMMMOO...",
    "...OMMMMMMO.....",
    "..OOMMMMMO......",
    "....O..O....OO..",
    "................",
    "................",
]

# CLOUD puffs in P_CLOUD, rising very slowly just off the ground (y 0.15): a big cloud near, smaller ones further
# up the path
CLOUDS = [
    "................",
    "............WL..",
    "...........WLLM.",
    "............MO..",
    "................",
    ".........WL.....",
    "........WLLM....",
    ".......WLLLMM...",
    "........MMMO....",
    "....WWL.........",
    "..WWLLLM........",
    ".WLLLLLLMM......",
    ".LLLLLLLLM......",
    "..MMMMMMO.......",
    "................",
    "................",
]

# BLOB in P_SLIME (upper case) and P_SLIME2 (lower case), flat on the ground (speed 0): glossy domes squatting on
# the path, smaller further up
SLIME = [
    "................",
    "................",
    "................",
    ".............L..",
    "............LWM.",
    "............OOO.",
    "................",
    ".........llm....",
    "........lwwmm...",
    "........lmmmo...",
    "...LLMM..ooo....",
    "..LWWMMM........",
    ".LWWMMMMM.......",
    ".LMMMMMMO.......",
    "..OOOOOO........",
    "................",
]

# emote_laugh launched straight up (direction up, speed 0.5): a big laughing face near with its tears flying, a
# smaller one floating higher up the path
LAUGH = [
    "................",
    "..........DDEE..",
    ".........DFEEFH.",
    ".........EFFFFH.",
    ".........EFIIFH.",
    "..........EEHH..",
    "..DDEEEE........",
    ".DEEEEEEE.......",
    ".DFEEEEFEHB.....",
    ".EDFEEFDEH.A....",
    ".DFEEEEFEH.A....",
    ".EFFFFFFHH......",
    ".EFGGGGFHH......",
    "..FIIIIFH.......",
    "...HHHHH........",
    "................",
]

# SQUARE and PLUS chips in red / green / blue ('Rrq' / 'Ggh' / 'Bbn' = M / L / W), flickering (alpha
# FLICKER): mixed chips scattered along the path, smaller further up
PIXEL_DUST = [
    "................",
    ".............b..",
    ".........r..bnB.",
    "........rqR..B..",
    ".........R......",
    ".............gg.",
    ".......g.....gG.",
    ".......G........",
    ".....gGhGGbbb...",
    ".......G..bBB...",
    ".rrrr..G..bBB...",
    ".rRRR...........",
    ".rRRR...........",
    ".rRRR...........",
    "................",
    "................",
]

# FILLED_BUBBLE in P_LIME_BUBBLE (upper case) and P_LIME_BUBBLE2 (lower case), rising (direction up, accel
# +0.4): a big bubble near, a second further on, small ones bubbling up off both
TOXIC = [
    "................",
    "................",
    "...........lm...",
    "......L....mo...",
    ".....LWM........",
    "......MO........",
    "................",
    "..........llm...",
    "...LLM...lwlmm..",
    "..LWLMM..llmmm..",
    ".LWWLMMM.lmmmo..",
    ".LWLMMMM..moo...",
    ".LMMMMMO........",
    "..MMMMO.........",
    "...MOO..........",
    "................",
]

# emote_skull launched straight up (direction up, speed 0.4): a big skull near, a smaller one floating higher up
# the path, a third sunk lower right
SKULLS = [
    "................",
    "................",
    ".........bbbbb..",
    "........bbbbbbc.",
    "........bddbddc.",
    "........bbbdbbc.",
    "...bbbbb.cbbbc..",
    "..bbbbbbbcbdb...",
    ".bbbbbbbbc......",
    ".bddbbbddc......",
    ".bddbbbddc.bbb..",
    ".bbbbdbbbcbdbdc.",
    "..cbbbbbc.bbbbc.",
    "...bdbdbc..b.c..",
    "....ccc.........",
    "................",
]

# RAINBOW's six DUST palettes as O / M / L ('1Rr' .. '6Vv'), plus the red puff's highlight 'w'
P_RAINBOW = {k: v for i, ch in enumerate(('1Rr', '2Aa', '3Yy', '4Gg', '5Cc', '6Vv'))
             for k, v in rainbow(i, ch, 'OML').items()} | rainbow(0, 'w', 'W')
# trail_pixel_dust's three chip colours (art_fx2.EFFECTS2) as M / L / W
P_PIXEL = {k: v for c, ch in zip(('#FF3B3B', '#3BFF6B', '#3B7BFF'), ('Rrq', 'Ggh', 'Bbn'))
           for k, v in relabel(art_fx2.rgb(c), ch, 'MLW').items()}

ICONS = {
    'trail_hearts': drawn(HEARTS, {**relabel(shades('#FF5577'), 'OMLW'), **relabel(shades('#FF8FB1'), 'omlw')}),
    'trail_paw_prints': drawn(PAW_PRINTS, {**relabel(art_fx2.P_BROWN, 'OMLW'), **relabel(art_fx2.P_BROWN2, 'omlw')}),
    'trail_ember_steps': drawn(EMBER_STEPS, cb.P_ORANGE),
    'trail_leaf_steps': drawn(LEAF_STEPS, {**cb.P_LEAF, **relabel(cb.P_LEAF2, 'omlw')}),
    'trail_rainbow': drawn(RAINBOW, P_RAINBOW),
    'trail_music_notes': drawn(MUSIC_NOTES, {**relabel(shades(GOLD), 'OMLW'), **relabel(shades('#6A92DD'), 'omlw'),
                                             **relabel(shades('#FF7AC8'), '1234')}),
    'trail_sparkles': drawn(SPARKLES, {**cb.P_WHITE_STAR, **relabel(cb.P_GOLD_STAR, 'omlw')}),
    'trail_snowfall': drawn(SNOWFALL, {**cb.P_SNOW, **relabel(cb.P_ICE2, 'omlw')}),
    'trail_bubbles': drawn(BUBBLES, cb.P_BUBBLE),
    'trail_pumpkin_steps': drawn(PUMPKIN_STEPS, {**cb.P_PUMPKIN, **relabel(cb.P_ORANGE, 'omlw')}),
    'trail_arena_flame': drawn(ARENA_FLAME, {**cb.P_BLUE_FIRE, **relabel(cb.P_GOLD_STAR, 'omlw')}),
    'trail_supporter_sparkles': drawn(SUPPORTER_SPARKLES, {**cb.P_GREEN_STAR, **relabel(cb.P_GOLD_STAR, 'omlw')}),
    'trail_soul_steps': drawn(SOUL_STEPS, art_fx2.P_SOUL),
    'trail_cherry_petals': drawn(CHERRY_PETALS, {**art_fx2.P_CHERRY, **relabel(art_fx2.P_CHERRY2, 'omlw')}),
    'trail_stars': drawn(STARS, art_fx2.P_YEL_STAR),
    'trail_coins': drawn(COINS, {**art_fx2.P_GOLD_COIN, **relabel(art_fx2.P_GOLD_COIN2, 'omlw')}),
    'trail_sparks': drawn(SPARKS, art_fx2.P_SPARK),
    'trail_ink_drops': drawn(INK_DROPS, art_fx2.P_INK),
    'trail_clouds': drawn(CLOUDS, art_fx2.P_CLOUD),
    'trail_slime': drawn(SLIME, {**art_fx2.P_SLIME, **relabel(art_fx2.P_SLIME2, 'omlw')}),
    'trail_laugh': drawn(LAUGH, P_LAUGH),
    'trail_pixel_dust': drawn(PIXEL_DUST, P_PIXEL),
    'trail_toxic': drawn(TOXIC, {**art_fx2.P_LIME_BUBBLE, **relabel(art_fx2.P_LIME_BUBBLE2, 'omlw')}),
    'trail_skulls': drawn(SKULLS, relabel(P_SKULL, 'bcd', 'WGD')),
}
