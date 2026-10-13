"""Check the server pack's fonts: follow every reference from assets/minecraft/font/default.json, and for each bitmap
provider assert the PNG exists, its cell height (PNG height / number of `chars` rows) equals `height`, ascent <= height
and alpha is binary; `space` providers are allowed (their advance chars count too). Every char must be unique across
all providers.

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
            if p['type'] == 'space':
                for key in p['advances']:
                    assert len(key) == 1, f'{fid}: space advance key {key!r} must be one character'
                    assert key not in seen, f'U+{ord(key):04X} in {fid} already used by {seen[key]}'
                    seen[key] = fid
                    print(f'ok  U+{ord(key):04X}  space {p["advances"][key]:>4}  {fid}')
                continue
            assert p['type'] == 'bitmap', f'{fid}: unexpected provider type {p["type"]}'
            png = res(pack, p['file'], 'textures', '')
            assert os.path.isfile(png), f'{fid}: missing {png}'
            im = Image.open(png).convert('RGBA')
            rows = p['chars']
            assert rows and rows[0] and all(len(r) == len(rows[0]) for r in rows), f'{png}: chars rows must be equal length'
            assert im.height % len(rows) == 0 and im.width % len(rows[0]) == 0, \
                f'{png}: {im.width}x{im.height} does not divide into {len(rows[0])}x{len(rows)} cells'
            cell_h = im.height // len(rows)
            assert cell_h == p['height'], f'{png}: cell height {cell_h}, provider height {p["height"]}'
            assert p['ascent'] <= p['height'], f'{png}: ascent {p["ascent"]} > height {p["height"]}'
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
