"""Check the server pack's fonts: follow every reference from assets/minecraft/font/default.json, and for each bitmap
provider assert the PNG exists, is `height` px tall, has binary alpha; every char must be unique across all providers.

Run:  python -I packdev/server/resourcepack/check.py
"""
import json
import os
import sys

from PIL import Image

PACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pack')


def res(pack, rid, kind, ext):
    ns, path = rid.split(':', 1) if ':' in rid else ('minecraft', rid)
    return os.path.join(pack, 'assets', ns, kind, *path.split('/')) + ext


def check(pack=PACK):
    seen, todo, done, glyphs = {}, ['minecraft:default'], set(), 0
    while todo:
        fid = todo.pop()
        if fid in done:
            continue
        done.add(fid)
        path = res(pack, fid, 'font', '.json')
        assert os.path.isfile(path), f'font {fid}: missing {path}'
        with open(path, encoding='utf-8') as f:
            providers = json.load(f)['providers']
        for p in providers:
            if p['type'] == 'reference':
                todo.append(p['id'])
                continue
            assert p['type'] == 'bitmap', f'{fid}: unexpected provider type {p["type"]}'
            png = res(pack, p['file'], 'textures', '')
            assert os.path.isfile(png), f'{fid}: missing {png}'
            im = Image.open(png).convert('RGBA')
            assert im.height == p['height'] == 9, f'{png}: height {im.height}, provider height {p["height"]}'
            alphas = set(im.getchannel('A').tobytes())
            assert alphas <= {0, 255}, f'{png}: non-binary alpha {sorted(alphas - {0, 255})}'
            for row in p['chars']:
                for ch in row:
                    assert ch not in seen, f'U+{ord(ch):04X} in {p["file"]} already used by {seen[ch]}'
                    seen[ch] = p['file']
            glyphs += 1
            print(f'ok  U+{ord(p["chars"][0][0]):04X}  {im.width:>2}x{im.height}  {p["file"]}')
    print(f'{glyphs} glyphs, {len(seen)} unique chars, fonts: {", ".join(sorted(done))}')


if __name__ == '__main__':
    try:
        check()
    except AssertionError as e:
        sys.exit(f'FAIL: {e}')
