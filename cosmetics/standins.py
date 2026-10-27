"""Armor stand-ins for /hidearmor self-view (spec: packdev/server/specs/origins-cosmetics/unit-s3-armor-selfview.md).

The server sends the owner of hidden armor a minecraft:leather_horse_armor stack with custom_model_data
CMD_BASE + index (index = position in ITEMS) in place of the real piece. This module writes the model files that make
that stack look like the real piece in inventories while drawing nothing on the body:
  assets/minecraft/models/item/leather_horse_armor.json   vanilla model + one override group per ITEMS entry
  assets/origins/models/item/standin/<model>.json         parent = the vanilla item (or trim) model, head scale 0

Overrides (1.21.1: every predicate is a >= test, the last matching override wins): ascending cmd, base model before
its trim models, trim_type ascending as vanilla orders them. An item with cmd c and trim t therefore matches its own
base and trims <= t, and later groups (higher cmd) win over earlier ones.

Standalone, stdlib only:
    python -I cosmetics/standins.py build                 write into pack/
    python -I cosmetics/standins.py check                 validate pack/ (offline, against vanilla_armor_models.json)
    python -I cosmetics/standins.py --refresh <1.21.1.jar>  regenerate vanilla_armor_models.json from the client jar
Called by the root build.py / cosmetics checks: build(pack_dir), check(pack_dir) -> [errors].
"""
import json
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(os.path.dirname(HERE), 'pack')
CACHE = os.path.join(HERE, 'vanilla_armor_models.json')

CMD_BASE = 7400001
# order is the wire contract with the server (ArmorStandIns.ITEMS); elytra and leather_boots are deliberately absent
ITEMS = ('leather_helmet', 'leather_chestplate', 'leather_leggings',
         'chainmail_helmet', 'chainmail_chestplate', 'chainmail_leggings', 'chainmail_boots',
         'iron_helmet', 'iron_chestplate', 'iron_leggings', 'iron_boots',
         'golden_helmet', 'golden_chestplate', 'golden_leggings', 'golden_boots',
         'diamond_helmet', 'diamond_chestplate', 'diamond_leggings', 'diamond_boots',
         'netherite_helmet', 'netherite_chestplate', 'netherite_leggings', 'netherite_boots',
         'turtle_helmet')
HORSE = 'leather_horse_armor'
HORSE_REL = f'assets/minecraft/models/item/{HORSE}.json'
STANDIN_DIR = 'assets/origins/models/item/standin'
VANILLA_TEXTURES = {f'minecraft:item/{HORSE}'}  # layer0 of the shipped base model, for the generic model check
HEAD_HIDDEN = {'head': {'rotation': [0, 0, 0], 'translation': [0, 0, 0], 'scale': [0, 0, 0]}}


def load_cache():
    with open(CACHE, encoding='utf-8') as f:
        return json.load(f)


def vanilla_models():
    """minecraft:item/<name> ids the stand-in models use as parents (for cosmetics/check.py VANILLA_MODELS)."""
    c = load_cache()
    return {f'minecraft:item/{n}' for n in used_models(c)}


def used_models(cache):
    """Vanilla model names the stand-ins parent: each item's base model and its trim models."""
    out = []
    for item in ITEMS:
        out.append(item)
        out.extend(o['model'].split('/', 1)[1] for o in cache['items'][item])
    return out


def horse_model(cache):
    """The vanilla leather_horse_armor model plus the override groups; vanilla's own overrides (none in 1.21.1) stay first."""
    model = json.loads(json.dumps(cache[HORSE]))
    overrides = list(model.get('overrides', []))
    for i, item in enumerate(ITEMS):
        cmd = CMD_BASE + i
        overrides.append({'model': f'origins:item/standin/{item}', 'predicate': {'custom_model_data': cmd}})
        for o in cache['items'][item]:
            trimmed = o['model'].split('/', 1)[1]
            overrides.append({'model': f'origins:item/standin/{trimmed}',
                              'predicate': {'custom_model_data': cmd, **o['predicate']}})
    model['overrides'] = overrides
    return model


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=2)
        f.write('\n')


def build(pack_dir):
    cache = load_cache()
    shutil.rmtree(os.path.join(pack_dir, *STANDIN_DIR.split('/')), ignore_errors=True)  # drop stale generated files
    write_json(os.path.join(pack_dir, *HORSE_REL.split('/')), horse_model(cache))
    names = used_models(cache)
    for name in names:
        write_json(os.path.join(pack_dir, *STANDIN_DIR.split('/'), name + '.json'),
                   {'parent': f'minecraft:item/{name}', 'display': HEAD_HIDDEN})
    print(f'standins: {len(ITEMS)} items, {len(names)} stand-in models + {HORSE}.json '
          f'({len(horse_model(cache)["overrides"])} overrides)')
    return len(names) + 1


def _read(path, errors):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        errors.append(f'{path}: {e}')
        return None


def check(pack_dir):
    errors = []
    try:
        cache = load_cache()
    except (OSError, ValueError) as e:
        return [f'{CACHE}: {e} (regenerate: python -I cosmetics/standins.py --refresh <1.21.1.jar>)']
    vanilla = set(cache['models'])
    cmds = [CMD_BASE + i for i in range(len(ITEMS))]
    if len(set(ITEMS)) != 24 or len(ITEMS) != 24 or 'elytra' in ITEMS or 'leather_boots' in ITEMS:
        errors.append('ITEMS must be the spec\'s 24 unique ids without elytra / leather_boots')
    if cmds[0] != 7400001 or cmds[-1] != 7400024:
        errors.append('cmd range must be 7400001..7400024')
    for item in ITEMS:
        if item not in vanilla:
            errors.append(f'vanilla has no models/item/{item}.json (cache {CACHE} stale?)')

    # no other file in the pack may define the vanilla horse armor model (an overlay would shadow ours)
    expected = os.path.normpath(os.path.join(pack_dir, *HORSE_REL.split('/')))
    for d, _, names in os.walk(pack_dir):
        for n in names:
            p = os.path.normpath(os.path.join(d, n))
            if n == f'{HORSE}.json' and p != expected:
                errors.append(f'{p}: second definition of {HORSE}.json')

    path = os.path.join(pack_dir, *HORSE_REL.split('/'))
    model = _read(path, errors)
    if model is None:
        return errors
    base = {k: v for k, v in model.items() if k != 'overrides'}
    van = {k: v for k, v in cache[HORSE].items() if k != 'overrides'}
    if base != van:
        errors.append(f'{HORSE}.json: base (parent / textures / ...) differs from vanilla: {base} vs {van}')
    if base.get('textures', {}).get('layer0') != f'minecraft:item/{HORSE}':
        errors.append(f'{HORSE}.json: layer0 must be minecraft:item/{HORSE}')
    overrides = model.get('overrides')
    van_ov = cache[HORSE].get('overrides', [])
    if not isinstance(overrides, list) or overrides[:len(van_ov)] != van_ov:
        errors.append(f'{HORSE}.json: vanilla overrides {van_ov} must stay first')
        return errors
    ours = overrides[len(van_ov):]
    # walk the groups: base (cmd only) then trims (cmd + ascending trim_type), cmd 7400001+i in ITEMS order
    pos, models_seen = 0, []
    for i, item in enumerate(ITEMS):
        cmd = CMD_BASE + i
        group = [{'model': f'origins:item/standin/{item}', 'predicate': {'custom_model_data': cmd}}]
        trims = []
        for o in cache['items'][item]:
            trims.append({'model': 'origins:item/standin/' + o['model'].split('/', 1)[1],
                          'predicate': {'custom_model_data': cmd, **o['predicate']}})
        tt = [o['predicate'].get('trim_type') for o in trims]
        if any(t is None for t in tt) or tt != sorted(tt) or len(set(tt)) != len(tt):
            errors.append(f'{item}: vanilla trim overrides are not strictly ascending trim_type: {tt}')
        group += trims
        got = ours[pos:pos + len(group)]
        if got != group:
            errors.append(f'{HORSE}.json: overrides for {item} (cmd {cmd}) at #{pos} are not the expected '
                          f'base-then-trims group ({len(group)} entries)')
        pos += len(group)
        models_seen += [g['model'] for g in group]
    if pos != len(ours):
        errors.append(f'{HORSE}.json: {len(ours) - pos} unexpected extra overrides after the {len(ITEMS)} groups')
    cmd_seq = [o['predicate'].get('custom_model_data') for o in ours]
    if cmd_seq != sorted(cmd_seq):
        errors.append(f'{HORSE}.json: custom_model_data not ascending')

    # every referenced stand-in model exists with the right parent + hidden head transform; no strays
    root = os.path.join(pack_dir, *STANDIN_DIR.split('/'))
    on_disk = {f[:-5] for f in os.listdir(root) if f.endswith('.json')} if os.path.isdir(root) else set()
    want = {m.rsplit('/', 1)[1] for m in models_seen}
    for name in sorted(want - on_disk):
        errors.append(f'missing {STANDIN_DIR}/{name}.json')
    for name in sorted(on_disk - want):
        errors.append(f'stray {STANDIN_DIR}/{name}.json (not referenced by {HORSE}.json)')
    for name in sorted(want & on_disk):
        m = _read(os.path.join(root, name + '.json'), errors)
        if m is None:
            continue
        if m != {'parent': f'minecraft:item/{name}', 'display': HEAD_HIDDEN}:
            errors.append(f'{STANDIN_DIR}/{name}.json: expected parent minecraft:item/{name} + head scale 0, got {m}')
        if name not in vanilla:
            errors.append(f'{STANDIN_DIR}/{name}.json: parent minecraft:item/{name} does not exist in vanilla 1.21.1')
    return errors


def refresh(jar):
    """Regenerate the offline vanilla cache: the horse armor model, each ITEMS model's overrides, the item model listing."""
    pre = 'assets/minecraft/models/item/'
    with zipfile.ZipFile(jar) as z:
        names = sorted(n[len(pre):-5] for n in z.namelist() if n.startswith(pre) and n.endswith('.json')
                       and '/' not in n[len(pre):])
        read = lambda n: json.loads(z.read(f'{pre}{n}.json'))  # noqa: E731
        cache = {'source': 'minecraft 1.21.1 client jar', 'models': names, HORSE: read(HORSE), 'items': {}}
        for item in ITEMS:
            cache['items'][item] = read(item).get('overrides', [])
    for item, ovs in cache['items'].items():
        for o in ovs:
            assert list(o['predicate']) == ['trim_type'] and o['model'].startswith('minecraft:item/'), (item, o)
            assert o['model'].split('/', 1)[1] in names, (item, o)
    with open(CACHE, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(cache, f, indent=1)
        f.write('\n')
    print(f'wrote {CACHE}: {len(names)} item models, {sum(len(v) for v in cache["items"].values())} trim overrides, '
          f'vanilla {HORSE} overrides: {len(cache[HORSE].get("overrides", []))}')


if __name__ == '__main__':
    args = sys.argv[1:]
    if args == ['build']:
        build(PACK)
    elif args == ['check']:
        errs = check(PACK)
        if errs:
            sys.exit('FAIL:\n  ' + '\n  '.join(errs))
        print(f'ok  standins: {len(ITEMS)} items, cmd {CMD_BASE}..{CMD_BASE + len(ITEMS) - 1}')
    elif len(args) == 2 and args[0] == '--refresh':
        refresh(args[1])
    else:
        sys.exit(__doc__)
