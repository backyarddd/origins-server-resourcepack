"""Nickname icons (see icon_art.py for the template rules): a bold pixel "Aa" in the style's own name colours (the
catalog `colors`; several make a left-to-right gradient across both letters, in order) with chat's drop shadow, on a
small dark plate. That is the coloured name the player gets.

To add a style: put its id in NICK_IDS; the colours come from cosmetics/icon_catalog.json."""
from cosmetics import icons

# A = letter, P = plate, R = its frame: RIM, what the shared outline puts round near-black art, drawn here so letters
# near the edge don't turn it INK there (outline leaves RIM art alone). Every plate pixel down-right of a letter pixel
# becomes the letter's drop shadow (its colour at 1/4, as chat draws it).
AA = [
    "................",
    ".RRRRRRRRRRRRRR.",
    "RPPPPPPPPPPPPPPR",
    "RPPPAAPPPPPPPPPR",
    "RPPAAAAPPPPPPPPR",
    "RPAAPPAAPPPPPPPR",
    "RPAAPPAAPPAAAPPR",
    "RPAAAAAAPPPPAAPR",
    "RPAAPPAAPPAAAAPR",
    "RPAAPPAAPAAPAAPR",
    "RPAAPPAAPPAAAAPR",
    "RPPPPPPPPPPPPPPR",
    "RPPPPPPPPPPPPPPR",
    ".RRRRRRRRRRRRRR.",
    "................",
    "................",
]
PLATE = (0x0C, 0x0F, 0x19)  # near-black like the chat background, so dark stops (galaxy) still read
LIT = 0.28  # the top pixel of each stroke, toward white (light from the top-left)
LIT_GRADIENT = 0.14  # gentler on gradients, so the highlight row doesn't wash the bands into one tint
LIT_DARK = 0.3  # a stop this dark (galaxy's #3A1C71) all but vanishes on the plate: its top and left edges get lit
DARK = 70  # luminance under which a letter colour counts as dark
NICK_IDS = ('nick_red', 'nick_orange', 'nick_yellow', 'nick_green', 'nick_aqua', 'nick_blue', 'nick_purple',
            'nick_pink', 'nick_sunset', 'nick_ocean', 'nick_aurora', 'nick_champion_gold', 'nick_lime', 'nick_gold',
            'nick_crimson', 'nick_lavender', 'nick_fire', 'nick_toxic', 'nick_candy', 'nick_galaxy')
LETTER_COLS = [x for x in range(16) if any(row[x] == 'A' for row in AA)]  # the 11 lit columns, the gap left out


def bands(colors, n):
    """n column colours for a left-to-right gradient that reads at 1x: every stop is a solid band of its exact colour,
    with one half-way column between neighbours (a smooth ramp over 11 columns looks flat at real size). One colour ->
    n of it."""
    cs = [icons.hexrgb(c) for c in colors]
    w = max(1, (n - len(cs) + 1) // len(cs))
    levels = []
    for j, c in enumerate(cs):
        levels += [c] * w
        if j < len(cs) - 1:
            levels.append(icons.mix(c, cs[j + 1], 0.5))
    return [levels[round(i * (len(levels) - 1) / (n - 1))] for i in range(n)]


def nick_icon(colors):
    """The "Aa" plate in these colours: each letter column takes its band (bands); the top pixel of each stroke is
    lit a little, and a dark colour's left edge too, so its letter keeps its shape."""
    col = dict(zip(LETTER_COLS, bands(colors, len(LETTER_COLS))))
    lit = LIT if len(colors) == 1 else LIT_GRADIENT
    cv = icons.canvas()
    px = cv.load()
    for y, row in enumerate(AA):
        for x, ch in enumerate(row):
            if ch == '.':
                continue
            if ch == 'A':
                c = col[x]
                dark = icons.lum(c) < DARK
                if AA[y - 1][x] != 'A':
                    c = icons.mix(c, (255, 255, 255), LIT_DARK if dark else lit)
                elif dark and AA[y][x - 1] != 'A':
                    c = icons.mix(c, (255, 255, 255), LIT_DARK * 0.6)
            elif AA[y - 1][x - 1] == 'A':
                c = tuple(v // 4 for v in col[x - 1])
            else:
                c = icons.RIM if ch == 'R' else PLATE
            px[x, y] = c + (255,)
    return icons.outline(cv)


_catalog = icons.load_json(icons.CATALOG_JSON, {})
ICONS = {cid: (lambda c=tuple(_catalog[cid]['colors']): nick_icon(c)) for cid in NICK_IDS}
