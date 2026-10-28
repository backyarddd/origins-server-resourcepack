"""Animated gradient nicknames: writes the text shaders' style table and proves the marker colours are unambiguous.

The server (origins_cosmetics NicknameStyles.styled) gives every char of a gradient nickname a marker colour; the core
text shaders (pack/assets/minecraft/shaders/core/rendertype_text*) decode it and paint a gradient that flows along the
name. Spec: packdev/server/specs/origins-cosmetics/animated-nicks.md. Kotlin twin: AppliedLogic.nickMarkers.

Marker channel byte (R, G and B alike): (base << 4) | (payload << 2) | TAG
  base     the style's cosmetics.jsonc `marker` ("#RGB", one hex digit per channel), default: the mean of its stops
           >> 4 per channel. Identifies the style in the shader, and is roughly the colour a client without the pack
           sees (#E96 -> every letter in #E0..#EF, #90..#9F, #60..#6F). Set `marker` only when check() finds the
           default cell shared with a real text colour; it prints the nearest free cell.
  payload  2 bits per channel of code(i, n) = n(n-1)/2 + i (R high, B low): char i of a name n chars long, where
           n = min(length, CYCLE) and i = index mod n, so a long name repeats the cycle every CYCLE chars, seamlessly
  TAG      fixed low bits. Text shadows are drawn in floor(c / 4) per channel, which drops exactly these bits:
           shadow = (base << 2) | payload, every channel < 64.

Run:  python -I nicks.py --scan <dir> [<dir> ...]
      Collects every hex colour in the text files there (configs, lang, menus, chat formats, mod sources) into
      nick_scan.json, which check() (run by build.py) holds every marker against. Rerun after adding a gradient
      nickname or a new coloured config, e.g. from packdev:  python -I server/resourcepack-icons/nicks.py --scan server mods
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(HERE, 'cosmetics', 'icon_catalog.json')
SCAN = os.path.join(HERE, 'nick_scan.json')
INCLUDE = ('assets', 'minecraft', 'shaders', 'include', 'origins_nick.glsl')
CYCLE = 10  # code(i, n) for n <= 10 fills 0..54 of the 6 payload bits
TAG = (1, 2, 1)  # low 2 bits of R, G, B on marker text; no colour --scan found shares it with a marker base
PERIOD_TICKS = 60  # one loop = 3 s; must divide 24000 (GameTime wraps every 24000 ticks)
SPREAD = 1.0  # colour cycles along the whole name (n chars); 0.5 = half the cycle is visible at once
# Vanilla chat formatting colours (ChatFormatting) and the vanilla GUI text greys, always on screen somewhere.
VANILLA = [0x000000, 0x0000AA, 0x00AA00, 0x00AAAA, 0xAA0000, 0xAA00AA, 0xFFAA00, 0xAAAAAA, 0x555555, 0x5555FF,
           0x55FF55, 0x55FFFF, 0xFF5555, 0xFF55FF, 0xFFFF55, 0xFFFFFF, 0x404040, 0x808080, 0xA0A0A0, 0xE0E0E0,
           0x3F3F3F, 0x707070, 0xFFFFA0]


def rgb(hex_colour):
    return int(hex_colour.lstrip('#'), 16)


def channels(c):
    return (c >> 16) & 255, (c >> 8) & 255, c & 255


def pack3(r, g, b):
    return (r << 16) | (g << 8) | b


def styles(catalog_path=CATALOG):
    """Gradient nickname styles in catalog order: [(id, [stop rgb ints], (base r, g, b))]."""
    with open(catalog_path, encoding='utf-8') as f:
        catalog = json.load(f)
    out = []
    for cid, entry in catalog.items():
        if entry.get('type') != 'nickname' or len(entry.get('colors', [])) < 2:
            continue
        stops = [rgb(c) for c in entry['colors']]
        if 'marker' in entry:
            base = tuple(int(d, 16) for d in entry['marker'][1:])
        else:
            base = tuple(sum(channels(s)[k] for s in stops) // len(stops) >> 4 for k in range(3))
        out.append((cid, stops, base))
    return out


def code(i, n):
    return n * (n - 1) // 2 + i


def marker(base, index, length):
    """The colour of char [index] of a [length]-char name in the style with [base]."""
    n = min(length, CYCLE)
    c = code(index % n, n)
    payload = ((c >> 4) & 3, (c >> 2) & 3, c & 3)
    return pack3(*((base[k] << 4) | (payload[k] << 2) | TAG[k] for k in range(3)))


def decode(colour, bases):
    """What the vertex shader sees in [colour]: (style index, i, n, shadow) or None. Mirrors origins_nick.glsl."""
    ch = channels(colour)
    found, shadow, payload = -1, False, None
    if tuple(c & 3 for c in ch) == TAG:
        key = tuple(c >> 4 for c in ch)
        if key in bases:
            found, payload = bases.index(key), tuple((c >> 2) & 3 for c in ch)
    if found < 0 and all(c < 64 for c in ch):
        key = tuple((c >> 2) & 15 for c in ch)
        if key in bases:
            found, shadow, payload = bases.index(key), True, tuple(c & 3 for c in ch)
    if found < 0:
        return None
    c = payload[0] * 16 + payload[1] * 4 + payload[2]
    for n in range(1, CYCLE + 1):
        if c < n * (n + 1) // 2:
            return found, c - n * (n - 1) // 2, n, shadow
    return None


def shadow(colour):
    """Vanilla Font: channel / 255 * 0.25 * 255 in float, truncated, which is exactly floor(channel / 4)."""
    return pack3(*(c >> 2 for c in channels(colour)))


def static_gradient(stops, length):
    """AppliedLogic.gradient: the per-char colours of a static gradient nickname (pre-animation names keep these)."""
    if length <= 1:
        return [stops[0]] * length
    seg = len(stops) - 1
    out = []
    for i in range(length):
        pos = i / (length - 1) * seg
        s = min(int(pos), seg - 1)
        f = pos - s
        a, b = channels(stops[s]), channels(stops[s + 1])
        out.append(pack3(*(math.floor(a[k] + (b[k] - a[k]) * f + 0.5) for k in range(3))))  # Kotlin roundToInt
    return out


def glsl(table):
    """The include the text vertex shaders import. Everything happens per vertex, so the fragment shaders stay whatever
    the client has (the modpack's "Cobblemon Origins UI" pack replaces rendertype_text.fsh and wins over this pack)."""
    stops, starts, counts, bases = [], [], [], []
    for _, s, base in table:
        starts.append(len(stops))
        counts.append(len(s))
        bases.append(base)
        stops.extend(s)
    vec3s = ',\n    '.join('vec3(%d.0, %d.0, %d.0)' % channels(s) for s in stops)
    ivec3s = ', '.join('ivec3(%d, %d, %d)' % b for b in bases)
    ints = lambda xs: ', '.join(str(x) for x in xs)  # noqa: E731
    ids = ', '.join(cid for cid, _, _ in table)
    return f'''// GENERATED by nicks.py from cosmetics/icon_catalog.json, do not edit. Spec: specs/origins-cosmetics/animated-nicks.md
// Styles: {ids}
#define NICK_STYLES {len(table)}
#define NICK_CYCLE {CYCLE}
// One loop of the moving gradient, in ticks (20 per second). Must divide 24000: GameTime wraps every 24000 ticks.
#define NICK_PERIOD_TICKS {PERIOD_TICKS}.0
// How much of the colour cycle one name shows at once (1.0 = the whole cycle from the first to the last char).
#define NICK_SPREAD {SPREAD}

const ivec3 NICK_TAG = ivec3({TAG[0]}, {TAG[1]}, {TAG[2]});
const ivec3 NICK_BASE[NICK_STYLES] = ivec3[NICK_STYLES]({ivec3s});
const int NICK_START[NICK_STYLES] = int[NICK_STYLES]({ints(starts)});
const int NICK_COUNT[NICK_STYLES] = int[NICK_STYLES]({ints(counts)});
const vec3 NICK_STOPS[{len(stops)}] = vec3[{len(stops)}](
    {vec3s}
);

int nick_style(ivec3 base) {{
    for (int s = 0; s < NICK_STYLES; s++) {{
        if (base == NICK_BASE[s]) return s;
    }}
    return -1;
}}

// The cyclic gradient through the style's stops at u (0..1 along the name), moving toward the end of the name.
// Neighbouring stops are blended in squared (roughly linear-light) RGB so the in-between colours stay bright.
vec3 nick_color(int style, float u, float gameTime) {{
    float phase = fract(u * NICK_SPREAD - gameTime * (24000.0 / NICK_PERIOD_TICKS));
    int n = NICK_COUNT[style];
    float x = phase * float(n);
    int k = min(int(x), n - 1);
    vec3 a = NICK_STOPS[NICK_START[style] + k] / 255.0;
    vec3 b = NICK_STOPS[NICK_START[style] + (k + 1) % n] / 255.0;
    return sqrt(mix(a * a, b * b, x - float(k)));
}}

// [color] is the vertex colour. A nickname marker becomes its animated colour at this vertex: the left corners of a
// glyph quad sit at u = i / n, the right ones at (i + 1) / n (BakedGlyph emits top-left, bottom-left, bottom-right,
// top-right), and the rasteriser blends the two across the glyph. A marker's shadow becomes the same colour dimmed
// like vanilla dims shadows, floor(c / 4). Every other colour comes back untouched.
vec4 nick_vertex(vec4 color, int vertexId, float gameTime) {{
    ivec3 c = ivec3(round(color.rgb * 255.0));
    int style = -1;
    ivec3 payload = ivec3(0);
    bool shadow = false;
    if ((c & 3) == NICK_TAG) {{
        style = nick_style(c >> 4);
        payload = (c >> 2) & 3;
    }}
    if (style < 0 && all(lessThan(c, ivec3(64)))) {{
        style = nick_style((c >> 2) & 15);
        payload = c & 3;
        shadow = true;
    }}
    if (style < 0) return color;
    int code = payload.r * 16 + payload.g * 4 + payload.b;
    for (int n = 1; n <= NICK_CYCLE; n++) {{
        if (code < n * (n + 1) / 2) {{
            float u = (float(code - n * (n - 1) / 2) + (vertexId % 4 >= 2 ? 1.0 : 0.0)) / float(n);
            vec3 rgb = nick_color(style, u, gameTime);
            if (shadow) rgb = floor(rgb * 255.0 / 4.0) / 255.0;
            return vec4(rgb, color.a);
        }}
    }}
    return color;
}}
'''

HEX = re.compile(r'(?<![0-9A-Za-z])(?:#|&#|0x|0X)([0-9A-Fa-f]{6})(?![0-9A-Fa-f])')
LEGACY = re.compile(r'[&§]x((?:[&§][0-9A-Fa-f]){6})')
# Files whose colours can reach the client's text renderer: configs, lang, menus, chat formats, mod sources.
TEXT = ('.json', '.jsonc', '.json5', '.yml', '.yaml', '.toml', '.txt', '.properties', '.conf', '.cfg', '.mcfunction',
        '.snbt', '.lang', '.kt', '.java')
GRADIENT = re.compile(r'<gradient|<#[0-9A-Fa-f]{6}>[^<]*</#|\{#[0-9A-Fa-f]{6}>', re.IGNORECASE)
SKIP_DIRS = {'.git', 'node_modules', 'build', '.gradle', 'region', 'entities', 'poi', 'DIM-1', 'DIM1', 'libraries',
             'versions', 'logs', 'crash-reports', 'cache', '__pycache__', 'playerdata', 'stats', 'advancements'}


def scan(roots):
    """{colour: first file it was seen in} for every hex colour in the text files under [roots]; a line with gradient
    syntax (MiniMessage <gradient:..>, TAB <#a>..</#b>, {#a>}..{#b<}) adds every blend of neighbouring colours."""
    seen = {}
    for root in roots:
        for d, dirs, names in os.walk(root):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for name in names:
                path = os.path.join(d, name)
                # block_map.txt: FTB Chunks map tile colours, never text
                if not name.lower().endswith(TEXT) or os.path.getsize(path) > 8_000_000 or name == 'block_map.txt':
                    continue
                with open(path, encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                for line in text.splitlines():
                    found = [rgb(m) for m in HEX.findall(line)]
                    found += [rgb(re.sub(r'[&§]', '', m)) for m in LEGACY.findall(line)]
                    for c in found:
                        seen.setdefault(c, path)
                    if not GRADIENT.search(line):
                        continue
                    for a, b in zip(found, found[1:]):
                        for step in range(1, 64):
                            ca, cb = channels(a), channels(b)
                            seen.setdefault(pack3(*(round(ca[k] + (cb[k] - ca[k]) * step / 64) for k in range(3))),
                                            path + ' (blend)')
    return seen


def collisions(colours, table):
    """Real colours (and their shadows) the shader would take for a marker, each with the nearest marker cell to that
    style's mean colour that holds no real colour."""
    bases = [b for _, _, b in table]
    used = {(c >> 20 & 15, c >> 12 & 15, c >> 4 & 15) for c in colours}
    bad = []
    for c, where in sorted(colours.items()):
        for what, v in (('text', c), ('shadow', shadow(c))):
            hit = decode(v, bases)
            if hit is None:
                continue
            cid, stops, _ = table[hit[0]]
            mean = [sum(channels(s)[k] for s in stops) / len(stops) for k in range(3)]
            free = min((cell for cell in ((r, g, b) for r in range(16) for g in range(16) for b in range(16))
                        if cell not in used and cell not in bases),
                       key=lambda cell: sum((cell[k] * 16 + 8 - mean[k]) ** 2 for k in range(3)))
            bad.append(f'#{c:06X} {what} decodes as {cid} ({where}); free marker: "#%X%X%X"' % free)
    return bad


def known_colours(table, catalog_path=CATALOG):
    """Colours the pack and the catalog always put on screen: vanilla, every catalog colour, and the static gradient of
    every gradient nickname at 1..24 chars (Pokemon traded away before the animation keep their static names)."""
    colours = {c: 'vanilla' for c in VANILLA}
    with open(catalog_path, encoding='utf-8') as f:
        for cid, entry in json.load(f).items():
            for c in entry.get('colors', []):
                colours.setdefault(rgb(c), cid)
    for cid, stops, _ in table:
        for n in range(1, 25):
            for c in static_gradient(stops, n):
                colours.setdefault(c, f'{cid} static gradient')
    return colours


def build(pack, catalog_path=CATALOG):
    table = styles(catalog_path)
    path = os.path.join(pack, *INCLUDE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(glsl(table))
    return table


def check(pack, catalog_path=CATALOG):
    table = styles(catalog_path)
    bases = [b for _, _, b in table]
    assert len(set(bases)) == len(bases), f'two gradient nicknames share a marker base: {table}'
    assert 24000 % PERIOD_TICKS == 0, 'PERIOD_TICKS must divide 24000 or the loop jumps when GameTime wraps'
    with open(os.path.join(pack, *INCLUDE), encoding='utf-8') as f:
        assert f.read() == glsl(table), 'origins_nick.glsl is stale (run build.py)'
    # Every marker and every marker shadow decodes to exactly itself.
    for s, (_, _, base) in enumerate(table):
        for n in range(1, CYCLE + 1):
            for i in range(n):
                m = marker(base, i, n)
                assert decode(m, bases) == (s, i, n, False), f'style {s} ({i}, {n}) marker #{m:06X}'
                assert decode(shadow(m), bases) == (s, i, n, True), f'style {s} ({i}, {n}) shadow #{shadow(m):06X}'
    with open(SCAN, encoding='utf-8') as f:
        scanned = {rgb(c): where for c, where in json.load(f).items()}
    bad = collisions({**known_colours(table, catalog_path), **scanned, **scan([os.path.join(HERE, 'menus')])}, table)
    assert not bad, 'real colours read as nickname markers (set `marker` in cosmetics.jsonc):\n  ' + '\n  '.join(bad)
    for name in ('rendertype_text', 'rendertype_text_see_through', 'rendertype_text_intensity',
                 'rendertype_text_intensity_see_through'):
        core = os.path.join(pack, 'assets', 'minecraft', 'shaders', 'core', name)
        with open(core + '.vsh', encoding='utf-8') as f:
            assert '#moj_import <origins_nick.glsl>' in f.read(), f'{name}.vsh does not import origins_nick.glsl'
        # The fragment shader stays the client's own (the modpack's UI pack replaces rendertype_text.fsh and wins).
        assert not os.path.exists(core + '.fsh'), f'{name}.fsh must not be shipped: the animation is per vertex'
        with open(core + '.json', encoding='utf-8') as f:
            assert any(u['name'] == 'GameTime' for u in json.load(f)['uniforms']), f'{name}.json lacks GameTime'
    print(f'ok  {len(table)} animated nickname styles, {CYCLE * (CYCLE + 1) // 2} positions each')


if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] != '--scan':
        sys.exit(__doc__)
    table = styles()
    found = scan(sys.argv[2:])
    with open(SCAN, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'#%06X' % c: os.path.relpath(found[c]).replace(os.sep, '/') for c in sorted(found)}, f, indent=0)
        f.write('\n')
    bad = collisions({**known_colours(table), **found}, table)
    print(f'{len(found)} colours scanned into {SCAN}, {len(bad)} collisions')
    for line in bad:
        print('  ' + line)
    sys.exit(1 if bad else 0)
