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
