"""Build the Cobblemon Origins server resource pack (rank prefix glyphs for chat).

Run:  python -I packdev/server/resourcepack/build.py

Source art: Figma file thHX6Yp5pMOLrryrsSaITZ, page "Prefixes", script packdev/guipack/figma/04_prefixes.js. Export each
page-level frame prefix_<group> (download_assets, png, scale 1) to src/<group>.png. The export draws the frame over the
page background (#E5E5E5, never used in a badge), which is keyed out to transparency here (in src/, idempotent).

Writes into pack/: the cosmetics assets (cosmetics/build.py, see README "Cosmetics"), the prefix textures,
assets/origins/font/prefixes.json (one bitmap provider per rank) and a reference to it in
assets/minecraft/font/default.json (other providers already there are kept). Also writes prefixes.json (the group ->
glyph table for LuckPerms), runs check.py and cosmetics/check.py, then zips pack/ deterministically into
dist/origins-server-pack.zip and prints its SHA-1 for server.properties (resource-pack-sha1).
"""
import hashlib
import json
import os
import shutil
import sys
import zipfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check  # noqa: E402
from cosmetics import build as cosmetics_build, check as cosmetics_check  # noqa: E402

SRC = os.path.join(HERE, 'src')
PACK = os.path.join(HERE, 'pack')
DIST = os.path.join(HERE, 'dist', 'origins-server-pack.zip')
KEY = (229, 229, 229)
REF = 'origins:prefixes'
# rank order (highest first): LuckPerms group, label drawn in the badge, private-use codepoint
BADGES = [
    ('owner', 'OWNER', 0xE200), ('admin', 'ADMIN', 0xE201), ('moderator', 'MOD', 0xE202),
    ('helper', 'HELPER', 0xE203), ('builder', 'BUILDER', 0xE204), ('gymleader', 'GYM LEADER', 0xE205), ('league_champion', 'LEAGUE CHAMPION', 0xE211),
    # tiered ranks (numerals drawn as 1 px strokes)
    ('master', 'MASTER', 0xE221),
    ('champion_iii', 'CHAMPION III', 0xE220), ('champion_ii', 'CHAMPION II', 0xE21F), ('champion_i', 'CHAMPION I', 0xE21E),
    ('elite_iii', 'ELITE III', 0xE21D), ('elite_ii', 'ELITE II', 0xE21C), ('elite_i', 'ELITE I', 0xE21B),
    ('veteran_iii', 'VETERAN III', 0xE21A), ('veteran_ii', 'VETERAN II', 0xE219), ('veteran_i', 'VETERAN I', 0xE218),
    ('challenger_iii', 'CHALLENGER III', 0xE217), ('challenger_ii', 'CHALLENGER II', 0xE216),
    ('challenger_i', 'CHALLENGER I', 0xE215),
    ('ace_iii', 'ACE III', 0xE214), ('ace_ii', 'ACE II', 0xE213), ('ace_i', 'ACE I', 0xE212),
    # legacy single-tier badges
    ('champion', 'CHAMPION', 0xE206), ('elite', 'ELITE', 0xE207), ('veteran', 'VETERAN', 0xE208),
    ('ace', 'ACE', 0xE209), ('challenger', 'CHALLENGER', 0xE20A), ('default', 'TRAINER', 0xE20B),
    # paid ranks, shown before the role badge
    ('vip', 'VIP', 0xE20C), ('vip_plus', 'VIP+', 0xE20D), ('mvp', 'MVP', 0xE20E), ('mvp_plus', 'MVP+', 0xE20F),
    ('legend', 'LEGEND', 0xE210),
]


def keyed(path):
    """Load src PNG with the export background keyed out; rewrite src if it changed."""
    im = Image.open(path).convert('RGBA')
    px = im.load()
    changed = False
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][:3] == KEY and px[x, y][3]:
                px[x, y] = (0, 0, 0, 0)
                changed = True
    if changed:
        im.save(path)
    return im


def colours(im):
    """fill = padding pixel left of the text; text = the one other colour in the text band (rows 2-6)."""
    px = im.load()
    fill = px[1, 2][:3]
    band = {px[x, y][:3] for y in range(2, 7) for x in range(1, im.width - 1)} - {fill}
    if len(band) != 1:
        raise SystemExit(f'text band must hold fill + one text colour, got {sorted(band)}')
    return '%02X%02X%02X' % fill, '%02X%02X%02X' % band.pop()


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=2)  # ensure_ascii default: chars stay as \uE2xx escapes
        f.write('\n')


def build():
    tex = os.path.join(PACK, 'assets', 'origins', 'textures', 'font', 'prefix')
    os.makedirs(tex, exist_ok=True)
    write_json(os.path.join(PACK, 'pack.mcmeta'),
               {'pack': {'pack_format': 34, 'description': 'Cobblemon Origins server pack'}})
    providers, table = [], []
    for group, label, cp in BADGES:
        im = keyed(os.path.join(SRC, group + '.png'))
        shutil.copyfile(os.path.join(SRC, group + '.png'), os.path.join(tex, group + '.png'))
        fill, text = colours(im)
        providers.append({'type': 'bitmap', 'file': f'origins:font/prefix/{group}.png', 'ascent': 8, 'height': 9,
                          'chars': [chr(cp)]})
        table.append({'group': group, 'label': label, 'char': chr(cp), 'codepoint': '%04X' % cp, 'width': im.width,
                      'hex': {'fill': fill, 'text': text}})
    write_json(os.path.join(PACK, 'assets', 'origins', 'font', 'prefixes.json'), {'providers': providers})
    default = os.path.join(PACK, 'assets', 'minecraft', 'font', 'default.json')
    data = {'providers': []}
    if os.path.exists(default):
        with open(default, encoding='utf-8') as f:
            data = json.load(f)
    if not any(p.get('type') == 'reference' and p.get('id') == REF for p in data['providers']):
        data['providers'].insert(0, {'type': 'reference', 'id': REF})
    write_json(default, data)
    write_json(os.path.join(HERE, 'prefixes.json'), table)


def zip_pack():
    files = sorted(os.path.relpath(os.path.join(d, n), PACK).replace(os.sep, '/')
                   for d, _, names in os.walk(PACK) for n in names)
    os.makedirs(os.path.dirname(DIST), exist_ok=True)
    with zipfile.ZipFile(DIST, 'w', zipfile.ZIP_DEFLATED) as z:
        for rel in files:
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(os.path.join(PACK, rel), 'rb') as f:
                z.writestr(info, f.read())
    with open(DIST, 'rb') as f:
        blob = f.read()
    return hashlib.sha1(blob).hexdigest(), len(blob), len(files)


if __name__ == '__main__':
    build()
    cosmetics_build.build(PACK, write_json)
    try:
        check.check(PACK)
        cosmetics_check.check(PACK)
    except AssertionError as e:
        sys.exit(f'FAIL: {e}')
    sha1, size, n = zip_pack()
    print(f'{DIST}\n{n} files, {size} bytes\nsha1 {sha1}')
