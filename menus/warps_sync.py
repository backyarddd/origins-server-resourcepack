"""Fill the dynamic warps menu from the FTB Essentials warps on the live server.

FTB Essentials keeps warps in `<world>/ftbessentials/data.snbt` (compound `warps`, child key = lowercase warp name,
child compound has string `dim` and ints x/y/z). There is no placeholder for them, so this script reads that file from
the live server, rebuilds the warps menu page(s) from the spec's dynamic menu, uploads them, updates DeluxeMenus'
gui_menus and runs `dm reload`.

Run it after every /setwarp or /delwarp, and after every deploy of menus/deluxemenus/*.yml (the deploy overwrites
warps.yml with the empty base).

Usage:
  python -I menus/warps_sync.py [--dry-run] [--data <local data.snbt>]
  python -I menus/warps_sync.py selftest

  --dry-run  print the generated pages instead of uploading them (the warp list is still read from the server unless
             --data is given).
  --data     read the warps from a local data.snbt instead of the server.

The panel API key is read from ~/Documents/kinetickey at call time and never printed.
"""
import contextlib
import io
import json
import math
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # python -I does not put the script directory on sys.path
from build import CMD, SPEC, dump_yaml, load_spec, yaml_menu  # noqa: E402

API = 'https://kineticpanel.net/api/client/servers/0ec99583'
KEY_PATH = '~/Documents/kinetickey'
REMOTE_DATA = 'AFreshWorld/ftbessentials/data.snbt'
REMOTE_DM = 'plugins/DeluxeMenus'
MATERIALS = {'minecraft:overworld': 'GRASS_BLOCK', 'minecraft:the_nether': 'NETHERRACK',
             'minecraft:the_end': 'END_STONE'}
DIM_NAMES = {'minecraft:overworld': 'Overworld', 'minecraft:the_nether': 'Nether', 'minecraft:the_end': 'The End',
             'origins:spawn': 'Spawn'}
# warp names reach a [player] click command and a YAML file: anything outside this set (%, {, [, ...) is skipped
NAME_RE = re.compile(r"[a-z0-9 _.'-]+")


# --- panel API ---------------------------------------------------------------------------------------------------

def _call(method: str, route: str, body: bytes | None = None, ctype: str | None = None,
          missing_ok: bool = False) -> bytes | None:
    key_path = os.path.expanduser(KEY_PATH)
    try:
        with open(key_path, encoding='utf-8') as f:
            key = f.read().strip()
    except OSError as e:
        raise SystemExit(f'cannot read the panel API key {KEY_PATH}: {e.strerror}')
    headers = {'Authorization': f'Bearer {key}', 'Accept': 'application/json', 'User-Agent': 'curl/8'}
    if ctype:
        headers['Content-Type'] = ctype
    what = f'{method} {route.split("?")[0]}'
    try:
        with urllib.request.urlopen(urllib.request.Request(API + route, data=body, headers=headers, method=method),
                                    timeout=60) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if missing_ok and e.code in (404, 500):  # the panel answers 500 for a missing file
            return None
        raise SystemExit(f'{what}: HTTP {e.code}')
    except OSError as e:
        raise SystemExit(f'{what}: {e}')


def _q(value: str) -> str:
    return urllib.parse.quote(value, safe='')


def get_file(path: str) -> bytes | None:
    return _call('GET', f'/files/contents?file={_q(path)}', missing_ok=True)


def put_file(path: str, data: bytes) -> None:
    _call('POST', f'/files/write?file={_q(path)}', data, 'text/plain')


def list_dir(directory: str) -> list[str]:
    raw = _call('GET', f'/files/list?directory={_q(directory)}')
    try:
        return [e['attributes']['name'] for e in json.loads(raw)['data']]
    except (ValueError, KeyError, TypeError):
        raise SystemExit(f'GET /files/list: unexpected response for {directory}')


def delete_files(root: str, names: list[str]) -> None:
    _call('POST', '/files/delete', json.dumps({'root': root, 'files': names}).encode('utf-8'), 'application/json')


def command(cmd: str) -> None:
    _call('POST', '/command', json.dumps({'command': cmd}).encode('utf-8'), 'application/json')


# --- SNBT --------------------------------------------------------------------------------------------------------

_BARE = re.compile(r'[\w+.\-\u221e]+')  # keys and unquoted values: numbers with b/s/L/f/d suffix, true/false, words
_TYPED = re.compile(r'[BIL]\s*;')  # [B; ..] [I; ..] [L; ..]
_ESC = {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', 'f': '\f'}
_HEX4 = re.compile(r'[0-9A-Fa-f]{4}')


class _Snbt:
    def __init__(self, text: str) -> None:
        self.t, self.i = text, 0

    def fail(self, msg: str) -> None:
        line = self.t.count('\n', 0, self.i) + 1
        raise SystemExit(f'data.snbt: {msg} (line {line}, offset {self.i})')

    def peek(self) -> str:
        """Skip whitespace, return the next character ('' at the end)."""
        while self.i < len(self.t) and self.t[self.i].isspace():
            self.i += 1
        return self.t[self.i] if self.i < len(self.t) else ''

    def comma(self) -> None:
        if self.peek() == ',':
            self.i += 1

    def bare(self, what: str) -> str:
        m = _BARE.match(self.t, self.i)
        if not m:
            found = repr(self.t[self.i]) if self.i < len(self.t) else 'end of input'
            self.fail(f'expected a {what}, found {found}')
        self.i = m.end()
        return m.group()

    def string(self) -> str:
        self.i += 1  # opening quote
        buf = []
        while self.i < len(self.t):
            c = self.t[self.i]
            self.i += 1
            if c == '"':
                return ''.join(buf)
            if c != '\\':
                buf.append(c)
                continue
            if self.i >= len(self.t):
                break
            e = self.t[self.i]
            self.i += 1
            if e == 'u':
                if not _HEX4.fullmatch(self.t[self.i:self.i + 4]):
                    self.fail('bad \\u escape')
                buf.append(chr(int(self.t[self.i:self.i + 4], 16)))
                self.i += 4
            else:
                buf.append(_ESC.get(e, e))
        self.fail('unterminated string')

    def value(self):
        c = self.peek()
        if c == '{':
            return self.compound()
        if c == '[':
            return self.array()
        if c == '"':
            return self.string()
        return self.bare('value')

    def array(self) -> list:
        self.i += 1  # '['
        self.peek()
        m = _TYPED.match(self.t, self.i)
        if m:
            self.i = m.end()
        out = []
        while True:
            c = self.peek()
            if c == ']':
                self.i += 1
                return out
            if c == '':
                self.fail('unterminated list')
            out.append(self.value())
            self.comma()

    def compound(self) -> dict:
        self.i += 1  # '{'
        out = {}
        while True:
            c = self.peek()
            if c == '}':
                self.i += 1
                return out
            if c == '':
                self.fail('unterminated compound')
            key = self.string() if c == '"' else self.bare('key')
            if self.peek() != ':':
                self.fail(f'expected ":" after key {key!r}')
            self.i += 1
            out[key] = self.value()
            self.comma()


def parse_warps(text: str) -> list[tuple[str, str]]:
    """Sorted (name, dim) of every child of the root compound's `warps` compound; [] when there is no `warps`."""
    p = _Snbt(text)
    if p.peek() != '{':
        p.fail('expected "{" at the start')
    try:
        root = p.compound()
    except RecursionError:
        raise SystemExit('data.snbt: nested too deeply')
    if p.peek() != '':
        p.fail('unexpected data after the root compound')
    warps = root.get('warps')
    if warps is None:
        return []
    if not isinstance(warps, dict):
        raise SystemExit('data.snbt: "warps" is not a compound')
    out = []
    for name, w in warps.items():
        if not isinstance(w, dict):
            raise SystemExit(f'data.snbt: warp {name!r} is not a compound')
        dim = w.get('dim', '')
        out.append((name, dim if isinstance(dim, str) else ''))
    return sorted(out)


# --- pages -------------------------------------------------------------------------------------------------------

def pretty(name: str) -> str:
    return ' '.join(w.capitalize() for w in re.split(r'[ _-]+', name) if w)


def build_pages(menu: dict, warps: list[tuple[str, str]]) -> dict[str, dict]:
    """One menu document per page of the dynamic menu, keyed by page id, in page order."""
    dyn = menu['dynamic']
    g = dyn['grid']
    grid = [(g['y'] + r) * 9 + g['x'] + c for r in range(g['h']) for c in range(g['w'])]
    good = []
    for name, dim in warps:
        if NAME_RE.fullmatch(name):
            good.append((name, dim))
        else:
            print(f'warning: skipping warp {name!r}: name must match {NAME_RE.pattern}', file=sys.stderr)
    total = max(1, math.ceil(len(good) / len(grid)))
    mid, title = menu['id'], menu['title']

    def page_id(n: int) -> str:
        return mid if n == 1 else f'{mid}_{n}'

    def arrow(label: str, cell: dict, target: str) -> dict:
        return {'material': 'PAPER', 'model_data': CMD, 'slots': [cell['y'] * 9 + cell['x']],
                'display_name': f'&#f7d27a{label}', 'click_commands': ['[openguimenu] ' + target]}

    pages = {}
    for n in range(1, total + 1):
        doc = yaml_menu(menu)
        if total > 1:  # menu_title ends with the menu title
            doc['menu_title'] = doc['menu_title'][:-len(title)] + f'{title} {n}/{total}'
        items = doc['items']
        for i, (name, dim) in enumerate(good[(n - 1) * len(grid):n * len(grid)], 1):
            items[f'warp_{i}'] = {'material': MATERIALS.get(dim, 'COMPASS'), 'slots': [grid[i - 1]],
                                  'display_name': '&#f7d27a' + pretty(name),
                                  'lore': ['&#c9d4ec' + DIM_NAMES.get(dim, dim), '&#9aa6c4Click to travel'],
                                  'click_commands': ['[close]', f'[player] warp {name}']}
        if n > 1:
            items['prev_page'] = arrow('Previous page', dyn['prev'], page_id(n - 1))
        if n < total:
            items['next_page'] = arrow('Next page', dyn['next'], page_id(n + 1))
        pages[page_id(n)] = doc
    return pages


# --- sync --------------------------------------------------------------------------------------------------------

def sync(dry_run: bool, data_path: str | None) -> None:
    spec = load_spec(SPEC)
    menus = [m for m in spec['menus'] if m.get('dynamic', {}).get('source') == 'ftb_warps']
    if len(menus) != 1:
        raise SystemExit(f'spec: expected exactly one menu with dynamic.source "ftb_warps", found {len(menus)}')
    menu = menus[0]
    mid = menu['id']
    if data_path:
        try:
            with open(data_path, encoding='utf-8') as f:
                text = f.read()
        except (OSError, ValueError) as e:
            raise SystemExit(f'cannot read {data_path}: {e}')
    else:
        raw = get_file(REMOTE_DATA)
        # the panel answers 500 both for a missing file and for daemon errors: only an absent file means "no warps"
        if raw is None and os.path.basename(REMOTE_DATA) in list_dir(os.path.dirname(REMOTE_DATA)):
            raise SystemExit(f'{REMOTE_DATA}: exists but could not be read; nothing changed')
        try:
            text = raw.decode('utf-8') if raw is not None else None
        except ValueError as e:
            raise SystemExit(f'{REMOTE_DATA}: not valid UTF-8: {e}')
    warps = parse_warps(text) if text is not None else []
    pages = build_pages(menu, warps)
    if dry_run:
        for pid, doc in pages.items():
            print(f'== {pid} ==')
            print(dump_yaml(doc))
        return

    folder = f'{REMOTE_DM}/gui_menus'
    uploaded = 0
    # read and check config.yml before any upload, so a bad config leaves the server untouched
    cfg_path = f'{REMOTE_DM}/config.yml'
    raw = get_file(cfg_path)
    if raw is None:
        raise SystemExit(f'{cfg_path}: not found on the server')
    try:
        before, cfg = yaml.safe_load(raw), yaml.safe_load(raw)
    except yaml.YAMLError as e:
        raise SystemExit(f'{cfg_path}: invalid YAML: {e}')
    if not isinstance(cfg, dict) or not isinstance(cfg.get('gui_menus'), dict):
        raise SystemExit(f'{cfg_path}: no gui_menus section')
    gui = cfg['gui_menus']
    page_re = re.compile(re.escape(mid) + r'_\d+')
    for k in [k for k in gui if isinstance(k, str) and page_re.fullmatch(k) and k not in pages]:
        del gui[k]
    for pid in pages:
        gui[pid] = {'file': f'{pid}.yml'}
    for pid, doc in pages.items():
        put_file(f'{folder}/{pid}.yml', dump_yaml(doc).encode('utf-8'))
        uploaded += 1
    if cfg != before:  # safe_dump drops the file's comments, so only rewrite it when something changed
        put_file(cfg_path, yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True).encode('utf-8'))
        uploaded += 1

    file_re = re.compile(re.escape(mid) + r'_\d+\.yml')
    stale = [n for n in list_dir(folder) if file_re.fullmatch(n) and n[:-len('.yml')] not in pages]
    if stale:
        delete_files(folder, stale)
    command('dm reload')
    shown = sum(1 for name, _ in warps if NAME_RE.fullmatch(name))
    print(f'warps={shown} pages={len(pages)} uploaded={uploaded} stale_removed={len(stale)}')


# --- selftest ----------------------------------------------------------------------------------------------------

def _snbt(names: list[str], dim: str = 'minecraft:overworld') -> str:
    body = ''.join(f'\t\t{n}: {{\n\t\t\tdim: "{dim}"\n\t\t\tx: 1\n\t\t\ty: 64\n\t\t\tz: 1\n\t\t}}\n' for n in names)
    return '{\n\twarps: {\n' + body + '\t}\n}\n'


def _rejects(fn, word: str) -> None:
    try:
        fn()
    except SystemExit as e:
        assert word in str(e.code), f'expected {word!r} in {e.code!r}'
        return
    raise AssertionError(f'expected SystemExit containing {word!r}')


def selftest() -> None:
    sample = '''{
\tmaintenance: 1b
\twarps: {
\t\tspawn: {
\t\t\tdim: "origins:spawn"
\t\t\tx: 0
\t\t\ty: 64
\t\t\tz: 0
\t\t}
\t\t"my warp": {
\t\t\tdim: "minecraft:the_nether"
\t\t\tx: -5, y: 70, z: 12
\t\t\tnote: "say \\"hi\\" \\u0041"
\t\t}
\t\tarena: {
\t\t\tdim: "minecraft:overworld"
\t\t\tx: 1 y: 2 z: 3
\t\t\tyaw: 90.5f
\t\t\tflag: true
\t\t\tids: [I; 1, 2, 3]
\t\t\ttags: [ "a", "b", { k: 1L } ]
\t\t}
\t\tnodim: { x: 1 }
\t}
\tother: { n: 1L, s: 2s, d: 3.0d }
}
'''
    assert parse_warps(sample) == [('arena', 'minecraft:overworld'), ('my warp', 'minecraft:the_nether'),
                                   ('nodim', ''), ('spawn', 'origins:spawn')], parse_warps(sample)
    assert parse_warps('{ other: 1 }') == [] and parse_warps('{ warps: {} }') == []
    for bad in ('', '[1]', '{ warps: {', '{ warps: { a: } }', '{ warps: { a { } } }', '{ a: 1 } x', '{ "a: 1 }',
                '{ warps: 5 }', '{ warps: { a: 1 } }', '{ a: 1,, }', '{ a: [1 }', '{ a: "\\u00zz" }', '{ a: @ }'):
        _rejects(lambda bad=bad: parse_warps(bad), 'data.snbt')
    assert pretty("my_warp-x  y") == 'My Warp X Y' and pretty('spawn') == 'Spawn'

    menu = next(m for m in load_spec(SPEC)['menus'] if m.get('dynamic'))
    base = yaml_menu(menu)
    static = {s for it in base['items'].values() for s in it['slots']}
    prev_slot, next_slot = (menu['dynamic'][k]['y'] * 9 + menu['dynamic'][k]['x'] for k in ('prev', 'next'))

    warps = [(f'w{i:02d}', 'minecraft:overworld') for i in range(1, 24)]
    pages = build_pages(menu, warps)
    assert list(pages) == ['warps', 'warps_2'], list(pages)
    p1, p2 = pages['warps']['items'], pages['warps_2']['items']
    keys1 = [k for k in p1 if k.startswith('warp_')]
    assert keys1 == [f'warp_{i}' for i in range(1, 22)] and len(p1) == len(base['items']) + 21 + 1
    assert [p1[k]['slots'][0] for k in keys1] == [10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25,
                                                   28, 29, 30, 31, 32, 33, 34]
    assert 'prev_page' not in p1 and p1['next_page']['slots'] == [next_slot]
    assert p1['next_page']['click_commands'] == ['[openguimenu] warps_2']
    assert p1['next_page']['material'] == 'PAPER' and p1['next_page']['model_data'] == CMD
    assert [k for k in p2 if k.startswith('warp_')] == ['warp_1', 'warp_2']
    assert p2['warp_1']['slots'] == [10] and p2['warp_2']['slots'] == [11]
    assert 'next_page' not in p2 and p2['prev_page']['slots'] == [prev_slot]
    assert p2['prev_page']['click_commands'] == ['[openguimenu] warps']
    assert pages['warps']['menu_title'].endswith('Warps 1/2') and pages['warps_2']['menu_title'].endswith('Warps 2/2')
    assert p1['warp_1']['display_name'] == '&#f7d27aW01' and p1['warp_1']['material'] == 'GRASS_BLOCK'
    assert p1['warp_1']['lore'] == ['&#c9d4ecOverworld', '&#9aa6c4Click to travel']
    assert p1['warp_1']['click_commands'] == ['[close]', '[player] warp w01']
    for doc in pages.values():
        slots_used = [s for k, it in doc['items'].items() if k.startswith('warp_') for s in it['slots']]
        assert not set(slots_used) & static and len(slots_used) == len(set(slots_used))
        assert prev_slot not in slots_used and next_slot not in slots_used
        assert yaml.safe_load(dump_yaml(doc)) == doc
    for k, it in base['items'].items():  # the static items survive on every page
        assert all(d['items'][k] == it for d in pages.values())

    mixed = build_pages(menu, [('a b', 'minecraft:the_nether'), ('c', 'minecraft:the_end'), ('d', 'x:y'), ('e', '')])
    mi = mixed['warps']['items']
    assert [mi[f'warp_{i}']['material'] for i in range(1, 5)] == ['NETHERRACK', 'END_STONE', 'COMPASS', 'COMPASS']
    assert mi['warp_1']['display_name'] == '&#f7d27aA B' and mi['warp_1']['lore'][0] == '&#c9d4ecNether'
    assert mi['warp_3']['lore'][0] == '&#c9d4ecx:y'
    assert list(mixed) == ['warps'] and mixed['warps']['menu_title'] == base['menu_title']

    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        skipped = build_pages(menu, [('bad%name', 'minecraft:overworld'), ('ok', 'minecraft:overworld')])
    assert 'bad%name' in err.getvalue()
    assert [k for k in skipped['warps']['items'] if k.startswith('warp_')] == ['warp_1']
    assert skipped['warps']['items']['warp_1']['click_commands'] == ['[close]', '[player] warp ok']

    empty = build_pages(menu, [])
    assert list(empty) == ['warps'] and empty['warps'] == base
    assert len(build_pages(menu, warps[:21])) == 1 and len(build_pages(menu, warps[:22])) == 2

    # FTB writes non-ASCII names unquoted: they must parse (and are then skipped by NAME_RE, not crash the sync)
    accented = '{\n\twarps: {\n\t\tpok\u00e9center: {\n\t\t\tdim: "minecraft:overworld"\n\t\t\tx: 1\n\t\t}\n\t}\n}\n'
    assert parse_warps(accented) == [('pok\u00e9center', 'minecraft:overworld')]
    with contextlib.redirect_stderr(io.StringIO()):
        assert not [k for k in build_pages(menu, parse_warps(accented))['warps']['items'] if k.startswith('warp_')]

    # sync against an in-memory server: no network
    files = {REMOTE_DATA: _snbt([w[0] for w in warps]).encode(),
             f'{REMOTE_DM}/config.yml': yaml.safe_dump({'check_updates': True, 'gui_menus': {
                 'menu': {'file': 'menu.yml'}, 'warps': {'file': 'warps.yml'}, 'warps_3': {'file': 'warps_3.yml'}}}
             ).encode(),
             f'{REMOTE_DM}/gui_menus/menu.yml': b'menu', f'{REMOTE_DM}/gui_menus/warps.yml': b'empty base',
             f'{REMOTE_DM}/gui_menus/warps_3.yml': b'stale'}
    puts, cmds = [], []

    def fake_list(d):
        return [p[len(d) + 1:] for p in files if p.startswith(d + '/') and '/' not in p[len(d) + 1:]]

    def fake_put(p, data):
        puts.append(p)
        files[p] = data

    def fake_delete(root, names):
        for n in names:
            del files[f'{root}/{n}']

    fakes = {'get_file': files.get, 'put_file': fake_put, 'list_dir': fake_list, 'delete_files': fake_delete,
             'command': cmds.append}
    g = globals()
    saved = {k: g[k] for k in fakes}
    g.update(fakes)
    try:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sync(False, None)
        assert out.getvalue().strip() == 'warps=23 pages=2 uploaded=3 stale_removed=1', out.getvalue()
        cfg = yaml.safe_load(files[f'{REMOTE_DM}/config.yml'])
        assert cfg == {'check_updates': True, 'gui_menus': {'menu': {'file': 'menu.yml'},
                                                            'warps': {'file': 'warps.yml'},
                                                            'warps_2': {'file': 'warps_2.yml'}}}, cfg
        assert f'{REMOTE_DM}/gui_menus/warps_3.yml' not in files and files[f'{REMOTE_DM}/gui_menus/menu.yml'] == b'menu'
        assert yaml.safe_load(files[f'{REMOTE_DM}/gui_menus/warps_2.yml']) == pages['warps_2']
        assert yaml.safe_load(files[f'{REMOTE_DM}/gui_menus/warps.yml']) == pages['warps'] and cmds == ['dm reload']

        puts.clear()
        with contextlib.redirect_stdout(io.StringIO()):
            sync(False, None)
        assert puts == [f'{REMOTE_DM}/gui_menus/warps.yml', f'{REMOTE_DM}/gui_menus/warps_2.yml'], puts  # config as is

        del files[REMOTE_DATA]  # no data.snbt yet: the empty base page, and the old second page goes away
        with contextlib.redirect_stdout(io.StringIO()):
            sync(False, None)
        assert yaml.safe_load(files[f'{REMOTE_DM}/config.yml'])['gui_menus'] == {'menu': {'file': 'menu.yml'},
                                                                                'warps': {'file': 'warps.yml'}}
        assert f'{REMOTE_DM}/gui_menus/warps_2.yml' not in files and yaml.safe_load(
            files[f'{REMOTE_DM}/gui_menus/warps.yml']) == base and len(cmds) == 3

        puts.clear()
        with tempfile.TemporaryDirectory() as tmp:
            data = os.path.join(tmp, 'data.snbt')
            with open(data, 'w', encoding='utf-8', newline='\n') as f:
                f.write(_snbt(['alpha', 'beta']))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                sync(True, data)
            assert not puts and len(cmds) == 3 and '== warps ==' in out.getvalue() and 'Alpha' in out.getvalue()
            _rejects(lambda: sync(True, os.path.join(tmp, 'nope.snbt')), 'cannot read')

        # data.snbt listed but unreadable (daemon 500): stop before touching anything
        files[REMOTE_DATA] = _snbt(['alpha']).encode()
        g['get_file'] = lambda path: None if path == REMOTE_DATA else files.get(path)
        before = dict(files)
        _rejects(lambda: sync(False, None), 'could not be read')
        assert files == before and len(cmds) == 3
        g['get_file'] = files.get

        # broken config.yml: no page is uploaded
        files[f'{REMOTE_DM}/config.yml'] = b'gui_menus: [not, a, dict]'
        puts.clear()
        _rejects(lambda: sync(False, None), 'no gui_menus section')
        assert not puts and len(cmds) == 3
    finally:
        g.update(saved)
    print('warps_sync selftest ok')


def main(argv: list[str]) -> None:
    if argv == ['selftest']:
        selftest()
        return
    dry, data, i = False, None, 0
    while i < len(argv):
        if argv[i] == '--dry-run':
            dry = True
        elif argv[i] == '--data' and i + 1 < len(argv):
            i += 1
            data = argv[i]
        else:
            print('usage: python -I menus/warps_sync.py [--dry-run] [--data <local data.snbt>] | selftest',
                  file=sys.stderr)
            sys.exit(2)
        i += 1
    sync(dry, data)


if __name__ == '__main__':
    main(sys.argv[1:])
