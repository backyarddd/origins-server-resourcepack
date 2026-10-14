# origins-server-resourcepack

Server resource pack for the Cobblemon Origins server (Minecraft 1.21.1).

- `pack/` is the resource pack root. Rank prefix glyphs live in `assets/origins/font/prefixes.json` (U+E200..U+E2FF);
  `assets/minecraft/font/default.json` only holds `reference` providers so each feature keeps its own font file.
- `src/` holds the 1x PNG exports from Figma (`packdev/guipack/figma/04_prefixes.js`); `prefixes.json` maps each
  LuckPerms group to its glyph.
- `python -I build.py` rebuilds `pack/`, runs `check.py` and writes `dist/origins-server-pack.zip` plus its SHA-1.

Each release attaches `origins-server-pack.zip`. The server's `resource-pack` points at
`https://github.com/backyarddd/origins-server-resourcepack/releases/latest/download/origins-server-pack.zip` and
`resource-pack-sha1` must match the release.

## Menus (DeluxeMenus)

Chest-menu backgrounds for DeluxeMenus, drawn in the navy/gold Origins theme.

- `menus/spec.json` is the source of truth: each menu's rows, title, glyph and elements in chest cells (9 columns,
  cell (x, y) = slot y*9+x), plus the DeluxeMenus item (name, lore, click actions) for each clickable element.
- Backgrounds are font glyphs U+E300..U+E3EF in `assets/origins/font/menus.json`; U+E3F0 (-8) and U+E3F1 (-169) shift
  the title so the glyph covers the chest from its top-left corner and the real title text lands at the vanilla x=8.
  Menu titles are `&f<U+E3F0><glyph><U+E3F1>&#fff1d0<Title>`.
- Drawn buttons are invisible `PAPER` items with custom_model_data 7300 (`assets/minecraft/models/item/paper.json` →
  `origins:item/menu_blank`); `slot` elements are transparent holes that show the vanilla slot and real items.
- Figma file `thHX6Yp5pMOLrryrsSaITZ`: page "Menu Kit" (all parts, script `menus/figma/kit.js`) and page "Menus"
  (composed menus, script `menus/figma/menus.js`).

Workflow:
1. Edit `menus/spec.json`, run `python -I menus/build.py validate`.
2. `python -I menus/build.py figma [menu ids]`, then run `menus/figma/out/menus.run.js` with the Figma MCP `use_figma` tool.
   A spec too big for one script is split into `menus.1.run.js`, `menus.2.run.js`, ...; each script redraws only its own
   menus at fixed places, so pass the ids of the menus you changed to get one small script. Other menus' frames on the
   page are never touched (delete a dropped menu's frames by hand).
3. Export each page-level frame `menu_<id>` (download_assets, png, scale 1) to `menus/export/menu_<id>.png`.
4. `python -I menus/build.py build` (validates every export pixel-exactly, writes the glyphs, fonts, item model and
   `menus/deluxemenus/*.yml`), then `python -I build.py` for the zip and SHA-1.
5. Server: copy `menus/deluxemenus/<id>.yml` to `plugins/DeluxeMenus/gui_menus/`, merge `menus/deluxemenus/gui_menus.yml`
   into `plugins/DeluxeMenus/config.yml`, `/dm reload`; publish the pack release and update `resource-pack-sha1`.

### Mod menus

A menu with `"renderer": "mod"` is drawn by the server-side Fabric mod `origins_server` instead of DeluxeMenus. It gets the
same background texture and font glyph, but no `menus/deluxemenus/<id>.yml`, no `gui_menus` entry and no `open_command`;
`[openguimenu]` actions in DeluxeMenus menus and commands cannot target it. Each element `item` is only `{"key": "<key>"}`
(the mod supplies names, lore, materials and clicks) and `dynamic` is not allowed.

`python -I menus/build.py layouts` (also run by `build`) writes `menus/mod/<id>.json` for each mod menu, which the mod reads:
`{"id", "rows", "glyph", "slots": {"<key>": [slot indexes]}}`. Stale files in `menus/mod/` are removed. It needs no exports.

### Warps menu

FTB Essentials has no placeholders for warps, so the warps menu is filled from the server's warp list by
`python -I menus/warps_sync.py` (reads `AFreshWorld/ftbessentials/data.snbt`, writes one page per 21 warps, updates
DeluxeMenus' `gui_menus`, runs `dm reload`; needs the panel API key in `~/Documents/kinetickey`). Run it after every
`/setwarp` or `/delwarp`, and after uploading `menus/deluxemenus/*.yml` (that upload resets `warps.yml` to the empty
base). `--dry-run` prints the pages instead.

### Commands

`commands` in spec.json are command-only DeluxeMenus menus (`/spawn`, `/rules`): an always-false open requirement
runs their actions instead of opening a menu. `register_command` is on, so a new command needs a server restart.
