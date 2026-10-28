"""Send-out icons (see icon_art.py for the template rules): the effect alone, no ball (owner 2026-10-27). Sphere
bursts radiate from the icon centre; bat_swarm scatters, leaf_tornado spirals."""
from cosmetics import art_fx2 as fx
from cosmetics import build as cb
from cosmetics.icon_art_base import P_LAUGH, P_SKULL, drawn, rainbow, relabel

# ZAP + SPARK in P_YELLOW, a sphere burst at speed 5 spun in 90 degree steps: the spark's flash in the centre, a bolt
# flung out along each diagonal
THUNDERCLAP = [
    "................",
    ".L...L.......LM.",
    "..M.M.......LM..",
    "...W.......LM...",
    "..M.M.....LLLLM.",
    ".L...L......LM..",
    "......L....LM...",
    ".......WL.LM....",
    "....LM.LM.......",
    "...LM....M......",
    "..LM......L...L.",
    ".LLLLM.....M.M..",
    "...LM.......W...",
    "..LM.......M.M..",
    ".LM.......L...L.",
    "................",
]

# BAT in P_BAT (near-black wings and body O, membranes M, red eyes X): a sphere burst that rises (accel +1.5) and
# flaps, so two bats scattered up and out, the near one big; kept apart so the shared outline rims each one in RIM on
# its own instead of joining them into one grey lattice on the dark slot
BAT_SWARM = [
    "................",
    ".O..O.O..O......",
    ".OO.OOO.OO......",
    ".OMOXOXOMO......",
    ".OMMOOOMMO......",
    "..O.O.O.O.......",
    "................",
    "................",
    "................",
    "..O....O.O....O.",
    "..OO...OOO...OO.",
    "..OMO.OXOXO.OMO.",
    "..OMMOOOOOOOMMO.",
    "..OMMMMOOOMMMMO.",
    "...O.MO.O.OM.O..",
    "................",
]

# PETAL in P_PINK (upper case) and P_PINK2 (lower case), a sphere burst at speed 4 that sinks (accel -1.5) and spins:
# loose oblong petals blown apart at all angles with gaps between them, the lower ones dropped a little further
PETAL_BURST = [
    "................",
    "....LW..........",
    "...LLM......wl..",
    "..LLMO.....llm..",
    ".LMO......llmo..",
    ".O........mo....",
    "................",
    "......wll.......",
    ".......lmmo.....",
    "................",
    "..WL.........LW.",
    "..LLM.......LLM.",
    "...LMM.....LMO..",
    "....MO....MO....",
    "................",
    "................",
]

# FLAKE and SMOKE in P_SNOW, a sphere burst at speed 3 drifting down (accel -0.6): flakes and snow puffs flung out round
# the centre
SNOW_FLURRY = [
    "................",
    "....W...........",
    "..W.L.W....LLL..",
    "...LWL....LWWLM.",
    ".WLWWWLW..LWLMO.",
    "...LWL.....MOO..",
    "..W.L.W.........",
    "....W...........",
    ".........W.L.W..",
    "..........LWL...",
    ".........LWWWL..",
    "...LLL....LWL...",
    "..LWLMM..W.L.W..",
    "..MMMMO.........",
    "...OOO..........",
    "................",
]

# CONFETTI in the RAINBOW colours (each chip light top-left, mid, dark bottom-right), fired up out of the ball at speed
# 6 then falling back (accel -4): a fountain, chips climbing from the bottom centre, fanning out over the top and
# fluttering down both sides, open at the bottom
CONFETTI_POP = [
    "................",
    ".......rR.......",
    "...aA..R1..yY...",
    "...A2......Y3...",
    "................",
    ".gG..........cC.",
    ".G4....pP....C5.",
    ".......P6.......",
    "................",
    "..cC...yY...rR..",
    "..C5...Y3...R1..",
    "................",
    "...a.........g..",
    "...2...aA....4..",
    ".......A2.......",
    "................",
]

# SMOKE and CIRCLE in P_VOID: the particles start on a 1.6 sphere and fly inwards spinning, shrinking as they go, so a
# dark rift in the centre with four pinwheel arms pulled into it, big at the rim and small near the core
VOID_RIFT = [
    "................",
    ".WL.........WL..",
    ".LMM.LM.....LMM.",
    "..MO....M....MO.",
    "................",
    "......LLMM...L..",
    ".....LOOOOM..M..",
    "...M.LOOOOM.....",
    ".....MOOOOM.M...",
    "..L..MOOOOM.....",
    "..M...MMMM......",
    "................",
    ".WL....M....WL..",
    ".LMM.....LM.LMM.",
    "..MO.........MO.",
    "................",
]

# COIN in P_GOLD (upper case) and STAR in P_GOLD_STAR (lower case), a sphere burst at speed 4 falling (accel -3): a big
# coin face on, one spun edge on, gold sparkles thrown out
GOLD_RUSH = [
    "................",
    "....w...........",
    "...lwm.......L..",
    "..wwwml.....LWM.",
    "...lmm......LWM.",
    "....m.......LWM.",
    "............LWM.",
    "....LLLM....LMO.",
    "...LWWLLM....O..",
    "..LWLLWLMM......",
    "..LWLMWMMO......",
    "..LLMMWMMO..w...",
    "..LMMMWMMO.wwm..",
    "...MMMMMO...m...",
    "....OOOO........",
    "................",
]

# BUBBLE in P_BLUE_BUBBLE (upper case) and P_BLUE_BUBBLE2 (lower case), a sphere burst at speed 3 that swells before it
# pops: hollow bubbles of four sizes spread round the centre
BUBBLE_POP = [
    "................",
    "..OO....OOOOO...",
    ".OW.O..O.....O..",
    ".O..O.O.WW....O.",
    "..OO..O.W.....O.",
    "......O.......O.",
    "......O.......O.",
    "......O......LO.",
    ".......O....LO..",
    "..oooo..OOOOO...",
    ".oww..o.........",
    ".ow...o....oo...",
    ".o....o...ow.o..",
    ".o...lo...o..o..",
    "..oooo.....oo...",
    "................",
]

# LEAF in P_GREEN_LEAF (upper case), P_GREEN_LEAF2 (lower case) and P_GREEN_LEAF3 (e f g h), speed 0 but swirled hard
# and lifted (swirl(55, 5)): leaves on a helix that widens as it climbs, small at the bottom, with leaf bits on the
# front passes
LEAF_TORNADO = [
    "................",
    "............LLW.",
    "...........LWWM.",
    "..........LWLMO.",
    "..........MMMO..",
    ".hg.......O.....",
    ".ghg..gh........",
    "..ffe...........",
    "...e...ff..lw...",
    "..........lwm...",
    ".........lmmo...",
    "...WL.h.o.......",
    "...LMM..........",
    ".....O..hg......",
    ".........f......",
    "................",
]

# DROP in P_LAVA (upper case) and P_LAVA2 (lower case), always upright, a sphere burst at speed 4.5 under heavy gravity
# (accel -9): drops flung out round the centre, the big one on top, the lower ones already falling
LAVA_SPLASH = [
    "................",
    ".......L........",
    "......LLM.......",
    "..L..LWLMO..L...",
    ".WMO.LLMMO.WMO..",
    ".MMO..MOO..MMO..",
    "..O.........O...",
    "................",
    "...l.......l....",
    "..llm.....llm...",
    ".lwlmo...lwlmo..",
    ".llmmo...llmmo..",
    "..moo..l..moo...",
    "......wlo.......",
    ".......o........",
    "................",
]

# SHARD (upper case P_ICE) and SHARD_B (lower case P_ICE2), a sphere burst at speed 5, spinning: long shards and
# chunks flung out in every direction from an empty centre
ICE_SHATTER = [
    "................",
    "..lw...W....lw..",
    ".lwlm..WL..lwm..",
    ".lmmo.LWM..mo...",
    "..oo..LWM.......",
    ".......MO.......",
    "..........LWWW..",
    "..........MMMLW.",
    "..........OOO...",
    ".....LM.........",
    "....LWM....lw...",
    "...LWM....lwlm..",
    "..LWM..l..lmmo..",
    ".WMO...lm..oo...",
    ".O......o.......",
    "................",
]

# HEART in P_RED_HEART (upper case), P_PINK (lower case) and P_PINK2 (e f g h), a sphere burst at speed 3.5 that floats
# up (accel +0.5) and shrinks: a big fresh heart low down, smaller ones rising above it
HEART_BURST = [
    "................",
    "......L.M.gg.ff.",
    "......MMM.ghfff.",
    ".ll.mm.O...ffe..",
    ".lwmmm......e...",
    "..mmo...........",
    "...o............",
    "................",
    "....LLL.MMM.....",
    "...LWWLMMMMM....",
    "...LWLMMMMMO....",
    "....MMMMMMO.....",
    ".....MMMMO......",
    "......MMO.......",
    ".......O........",
    "................",
]

# STAR5 in P_GOLD_STAR (upper case), P_WHITE_STAR (lower case) and P_YEL_STAR (e f g h), a sphere burst at speed 5.5
# that shrinks with age: the big gold star in the centre, small ones flung to the corners
STAR_BURST = [
    "................",
    "..w..........h..",
    ".wwl........hhg.",
    "..m....L.....f..",
    "......LWM.......",
    "......LWM.......",
    "...LLLWWWMMO....",
    "....LWWWMMO.....",
    ".....LWWMO......",
    ".....LMMMO......",
    "....LMO.LMO.....",
    "....MO...OO.....",
    "..h..........w..",
    ".hhg........wwl.",
    "..f..........m..",
    "................",
]

# SMOKE in P_SMOKE (upper case) and P_SMOKE2 (lower case) growing as it spreads (speed 2.5, grow), plus DUST in
# P_DARK_SPECK (p q k): one billowing cloud of overlapping puffs with dark grit thrown clear
SMOKE_BOMB = [
    "................",
    ".pq.............",
    ".qk.............",
    ".....LLL..mm....",
    "...LLWWLL.mllm..",
    "..LWWLLLLMlmmo..",
    ".LWLLLLMMMMmmo..",
    ".LLLLMMMMMMMmo..",
    ".MLWLMMMMMMOmo..",
    "..LLMMMMMMOOoo..",
    "..MMMMMMMOOOmo..",
    "...MMOOO.MOOo...",
    "....OOO...ooo...",
    ".............pq.",
    ".............qk.",
    "................",
]

# DUST in the RAINBOW colours in order, fired up in a narrow cone (speed 5.5) and falling back (accel -6): the arc it
# draws, one band per colour, and the dust dropping from its ends
RAINBOW_ARC = [
    "................",
    "................",
    "................",
    "....RRRRRRRR....",
    "..RRAAAAAAAARR..",
    ".RAAYYYYYYYYAAR.",
    ".RAYYGGGGGGYYAR.",
    ".RAYGGCCCCGGYAR.",
    ".RAYGCCPPCCGYAR.",
    ".RAYGCP..PCGYAR.",
    "................",
    ".rR..........pP.",
    ".R1.aA....cC.P6.",
    "....A2....C5....",
    "................",
    "................",
]

# SQUARE, BAR and CHUNK in P_MAGENTA (a b c), P_CYAN (d e f) and P_BLACK (k j i), a flickering sphere burst at speed
# 3.5: torn, offset bars in the middle and squares thrown to the corners; the black chunks get the RIM outline
GLITCH = [
    "................",
    ".ccc........fff.",
    ".cbb........fee.",
    ".cbb........fee.",
    "................",
    "...cccccc.......",
    "...bbbbbb.ii....",
    "..........ij....",
    "....ffffff......",
    "....eeeeee......",
    ".ii.....cccccc..",
    ".ij.....bbbbbb..",
    "................",
    ".....ccc...fff..",
    ".....cbb...fee..",
    "................",
]

# emote_laugh burst out at speed 4 from the centre and falling (accel -1.5): four faces flung apart into the corners,
# the centre left empty like the other sphere bursts (victory_laugh_rain is three faces falling in a zigzag)
EMOJI_PARTY = [
    "................",
    "..DDEE....DDEE..",
    ".DFDEFE..DFDEFE.",
    ".DEEEEH..DEEEEH.",
    ".EFGGFH..EFGGFH.",
    ".EFIIFH..EFIIFH.",
    "..HFFH....HFFH..",
    "................",
    "................",
    "..DDEE....DDEE..",
    ".DFDEFE..DFDEFE.",
    ".DEEEEH..DEEEEH.",
    ".EFGGFH..EFGGFH.",
    ".EFIIFH..EFIIFH.",
    "..HFFH....HFFH..",
    "................",
]

# emote_skull burst out at speed 4.5 and falling (accel -2): one big skull with two small ones popped up beside it
SKULL_POP = [
    "................",
    "..WWW......WWW..",
    ".WWWWG....WWWWG.",
    ".WDWDG....WDWDG.",
    "..GWG......GWG..",
    "................",
    ".....WWWWWW.....",
    "....WWWWWWWG....",
    "...WWWWWWWWWG...",
    "...WWDDWWDDWG...",
    "...WWDDWWDDWG...",
    "...GWWWDDWWWG...",
    "....GWWWWWWG....",
    ".....WDWWDG.....",
    ".....GGGGGG.....",
    "................",
]

# emote_wet + WET_DROP in fx.P_WET, flung up and out at speed 4.5 and raining back down (accel -7): emote_wet's
# three-drop splash opened into a full crown, every drop's tail pointing back at the burst under the centre
SPLASH = [
    "................",
    ".......LM.......",
    "......LWMM......",
    "......LMMX......",
    "..LLM..MX..LLM..",
    ".LWMMM....LWLMM.",
    ".LMMMX....LMMMX.",
    "..MMMMX..LMMMX..",
    "...XMMX..MMXX...",
    ".....MX..MX.....",
    "......X..X......",
    ".LLM........LLM.",
    ".LWMMX....LMWMX.",
    "..XX........XX..",
    "................",
    "................",
]

# RAINBOW in order, each colour's mid / light / dark under its own letter, lower case, digit
P_RAINBOW = {k: v for i in range(6) for k, v in rainbow(i, 'RAYGCP'[i] + 'raygcp'[i] + '123456'[i], 'MLO').items()}

ICONS = {
    'sendout_thunderclap': drawn(THUNDERCLAP, cb.P_YELLOW),
    'sendout_bat_swarm': drawn(BAT_SWARM, cb.P_BAT),
    'sendout_petal_burst': drawn(PETAL_BURST, {**cb.P_PINK, **relabel(fx.P_PINK2, 'omlw')}),
    'sendout_snow_flurry': drawn(SNOW_FLURRY, cb.P_SNOW),
    'sendout_confetti_pop': drawn(CONFETTI_POP, P_RAINBOW),
    'sendout_void_rift': drawn(VOID_RIFT, cb.P_VOID),
    'sendout_gold_rush': drawn(GOLD_RUSH, {**cb.P_GOLD, **relabel(cb.P_GOLD_STAR, 'omlw')}),
    'sendout_bubble_pop': drawn(BUBBLE_POP, {**fx.P_BLUE_BUBBLE, **relabel(fx.P_BLUE_BUBBLE2, 'omlw')}),
    'sendout_leaf_tornado': drawn(LEAF_TORNADO, {**fx.P_GREEN_LEAF, **relabel(fx.P_GREEN_LEAF2, 'omlw'),
                                                 **relabel(fx.P_GREEN_LEAF3, 'efgh')}),
    'sendout_lava_splash': drawn(LAVA_SPLASH, {**fx.P_LAVA, **relabel(fx.P_LAVA2, 'omlw')}),
    'sendout_ice_shatter': drawn(ICE_SHATTER, {**fx.P_ICE, **relabel(fx.P_ICE2, 'omlw')}),
    'sendout_heart_burst': drawn(HEART_BURST, {**fx.P_RED_HEART, **relabel(fx.P_PINK, 'omlw'),
                                               **relabel(fx.P_PINK2, 'efgh')}),
    'sendout_star_burst': drawn(STAR_BURST, {**fx.P_GOLD_STAR, **relabel(fx.P_WHITE_STAR, 'omlw'),
                                             **relabel(fx.P_YEL_STAR, 'efgh')}),
    'sendout_smoke_bomb': drawn(SMOKE_BOMB, {**fx.P_SMOKE, **relabel(fx.P_SMOKE2, 'omlw'),
                                             **relabel(fx.P_DARK_SPECK, 'kqp', 'OML')}),
    'sendout_rainbow_arc': drawn(RAINBOW_ARC, P_RAINBOW),
    'sendout_glitch': drawn(GLITCH, {**relabel(fx.P_MAGENTA, 'abc'), **relabel(fx.P_CYAN, 'def'),
                                     **relabel(fx.P_BLACK, 'kji')}),
    'sendout_emoji_party': drawn(EMOJI_PARTY, P_LAUGH),
    'sendout_skull_pop': drawn(SKULL_POP, P_SKULL),
    'sendout_splash': drawn(SPLASH, fx.P_WET),
}
