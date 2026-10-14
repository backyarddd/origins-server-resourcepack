// Cobblemon Origins menu kit: pixel-art library shared by kit.js and menus.js (menus/build.py figma prepends it).
// Everything is drawn on a Raster at 1 texel = 1 px and emitted as merged rectangles, like packdev/guipack/figma/*.js.
// Chest geometry (ContainerScreen, 1.21.1): GUI 176 px wide, title strip y 0..16, cell (c, r) = the 18x18 square at
// x = 7 + 18c, y = 17 + 18r (item area 16x16 at +1,+1). A menu background covers 176 x (17 + 18 * rows) from the GUI's
// top-left corner; the vanilla chest texture (navy restyle in the UI pack) keeps drawing the player inventory below,
// so the shell's outline, rim and bevel columns copy generic_54.png exactly and the seam is invisible.
// Palette: packdev/guipack/DESIGN.md. Never use #E5E5E5: the export background is keyed out to transparency.

const hex = h => ({ r: parseInt(h.slice(0, 2), 16) / 255, g: parseInt(h.slice(2, 4), 16) / 255, b: parseInt(h.slice(4, 6), 16) / 255 });
const C = {
  O: '0A1024', rimHi: 'E2B04A', rimLo: 'B07A22', bevHi: '2E4A86', bevLo: '0F1A3D', fill: '1B2E5B',
  slotDark: '070C1E', slotLite: '3A5A9C', slotIn: '101C40', navy: '13214A', navyLite: '22396E', navyDeep: '0E1836',
  gold: 'E2B04A', goldHi: 'F7D27A', goldLo: 'B07A22', cream: 'FFF1D0', glow: '6A92DD', mist: '9AA6C4',
};
const CELL = 18, GX = 7, GY = 17, W = 176;
const menuHeight = rows => GY + CELL * rows;
const cellX = c => GX + CELL * c;
const cellY = r => GY + CELL * r;

class Raster {  // (ox, oy) = menu coordinate of texel (0, 0), so a kit part can be drawn with menu cell coordinates
  constructor(w, h, ox = 0, oy = 0) { this.w = w; this.h = h; this.ox = ox; this.oy = oy; this.p = new Array(w * h).fill(null); }
  set(x, y, c) { x -= this.ox; y -= this.oy; if (x >= 0 && y >= 0 && x < this.w && y < this.h) this.p[y * this.w + x] = c; }
  get(x, y) { x -= this.ox; y -= this.oy; return (x >= 0 && y >= 0 && x < this.w && y < this.h) ? this.p[y * this.w + x] : null; }
  rect(x, y, w, h, c) { for (let j = y; j < y + h; j++) for (let i = x; i < x + w; i++) this.set(i, j, c); }
  emit(parent) {  // horizontal runs, merged vertically when the same run repeats on the next row
    const done = [], open = new Map();
    for (let y = 0; y < this.h; y++) {
      const next = new Map();
      let x = 0;
      while (x < this.w) {
        const c = this.p[y * this.w + x];
        if (c === null) { x++; continue; }
        let e = x; while (e < this.w && this.p[y * this.w + e] === c) e++;
        const key = x + ',' + (e - x) + ',' + c, prev = open.get(key);
        if (prev) { prev.h++; next.set(key, prev); open.delete(key); } else next.set(key, { x, y, w: e - x, h: 1, c });
        x = e;
      }
      for (const r of open.values()) done.push(r);
      open.clear(); for (const [k, v] of next) open.set(k, v);
    }
    for (const r of open.values()) done.push(r);
    for (const r of done) {
      const n = figma.createRectangle();
      n.resize(r.w, r.h); n.x = r.x; n.y = r.y; n.name = '#' + r.c;
      n.fills = [{ type: 'SOLID', color: hex(r.c) }];
      parent.appendChild(n);
    }
    return done.length;
  }
}

// ---------------- 7 px caps font (1 px strokes, 1 px letter spacing) ----------------
const FONT = {
  A: ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'], B: ['####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'],
  C: ['.###.', '#...#', '#....', '#....', '#....', '#...#', '.###.'], D: ['####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'],
  E: ['#####', '#....', '#....', '####.', '#....', '#....', '#####'], F: ['#####', '#....', '#....', '####.', '#....', '#....', '#....'],
  G: ['.####', '#....', '#....', '#..##', '#...#', '#...#', '.###.'], H: ['#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
  I: ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '###'], J: ['....#', '....#', '....#', '....#', '#...#', '#...#', '.###.'],
  K: ['#...#', '#..#.', '#.#..', '##...', '#.#..', '#..#.', '#...#'], L: ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
  M: ['#...#', '##.##', '#.#.#', '#...#', '#...#', '#...#', '#...#'], N: ['#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#', '#...#'],
  O: ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'], P: ['####.', '#...#', '#...#', '####.', '#....', '#....', '#....'],
  Q: ['.###.', '#...#', '#...#', '#...#', '#.#.#', '#..#.', '.##.#'], R: ['####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'],
  S: ['.####', '#....', '#....', '.###.', '....#', '....#', '####.'], T: ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
  U: ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'], V: ['#...#', '#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..'],
  W: ['#...#', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'], X: ['#...#', '#...#', '.#.#.', '..#..', '.#.#.', '#...#', '#...#'],
  Y: ['#...#', '#...#', '.#.#.', '..#..', '..#..', '..#..', '..#..'], Z: ['#####', '....#', '...#.', '..#..', '.#...', '#....', '#####'],
  0: ['.###.', '#...#', '#..##', '#.#.#', '##..#', '#...#', '.###.'], 1: ['.#.', '##.', '.#.', '.#.', '.#.', '.#.', '###'],
  2: ['.###.', '#...#', '....#', '..##.', '.#...', '#....', '#####'], 3: ['.###.', '#...#', '....#', '..##.', '....#', '#...#', '.###.'],
  4: ['...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'], 5: ['#####', '#....', '####.', '....#', '....#', '#...#', '.###.'],
  6: ['..##.', '.#...', '#....', '####.', '#...#', '#...#', '.###.'], 7: ['#####', '....#', '...#.', '..#..', '..#..', '..#..', '..#..'],
  8: ['.###.', '#...#', '#...#', '.###.', '#...#', '#...#', '.###.'], 9: ['.###.', '#...#', '#...#', '.####', '....#', '...#.', '.##..'],
  ' ': ['...', '...', '...', '...', '...', '...', '...'], '!': ['#', '#', '#', '#', '#', '.', '#'],
  '?': ['.###.', '#...#', '....#', '...#.', '..#..', '.....', '..#..'], '.': ['.', '.', '.', '.', '.', '.', '#'],
  ':': ['.', '.', '#', '.', '.', '#', '.'], '-': ['....', '....', '....', '####', '....', '....', '....'],
  '+': ['.....', '..#..', '..#..', '#####', '..#..', '..#..', '.....'], '/': ['....#', '...#.', '...#.', '..#..', '.#...', '.#...', '#....'],
  "'": ['#', '#', '.', '.', '.', '.', '.'],
};
function glyph(ch) { const g = FONT[ch]; if (!g) throw new Error('font has no glyph for ' + JSON.stringify(ch)); return g; }
function textWidth(s) { return [...s].reduce((w, ch) => w + glyph(ch)[0].length, 0) + Math.max(0, s.length - 1); }
function drawText(r, s, x, y, color, shadow) {
  for (const pass of shadow ? [1, 0] : [0]) {
    let cx = x;
    for (const ch of s) {
      const g = glyph(ch);
      g.forEach((row, j) => [...row].forEach((p, i) => { if (p === '#') r.set(cx + i + pass, y + j + pass, pass ? shadow : color); }));
      cx += g[0].length + 1;
    }
  }
}
function drawMask(r, rows, x, y, color, shadow) {  // '#' rows, optional 1 px drop shadow
  for (const pass of shadow ? [1, 0] : [0]) rows.forEach((row, j) => [...row].forEach((p, i) => {
    if (p === '#') r.set(x + i + pass, y + j + pass, pass ? shadow : color);
  }));
}

// ---------------- small glyphs for icon buttons and tabs ----------------
const SMALL = {
  left: ['...#...', '..##...', '.######', '#######', '.######', '..##...', '...#...'],
  right: ['...#...', '...##..', '######.', '#######', '######.', '...##..', '...#...'],
  up: ['...#...', '..###..', '.#####.', '#######', '..###..', '..###..', '..###..'],
  down: ['..###..', '..###..', '..###..', '#######', '.#####.', '..###..', '...#...'],
  close: ['##...##', '###.###', '.#####.', '..###..', '.#####.', '###.###', '##...##'],
  check: ['.....##', '....###', '##.###.', '#####..', '.###...', '..#....'],
  info: ['.##.', '.##.', '....', '###.', '.##.', '.##.', '####'],
  return: ['..#......', '.##......', '########.', '#########', '.##....##', '..#....##', '...######', '...#####.'],
  plus: ['..##..', '..##..', '######', '######', '..##..', '..##..'],
  minus: ['######', '######'],
};
const TRI = {
  left: ['...#', '..##', '.###', '####', '.###', '..##', '...#'], right: ['#...', '##..', '###.', '####', '###.', '##..', '#...'],
  up: ['...#...', '..###..', '.#####.', '#######'], down: ['#######', '.#####.', '..###..', '...#...'],
};

// ---------------- 16x16 icons ----------------
function strIcon(rows, pal) {
  if (rows.length !== 16 || rows.some(row => row.length !== 16)) throw new Error('icon rows must be 16x16: ' + rows.join('|'));
  return rows.map(row => [...row].map(ch => ch === '.' ? null : pal[ch]));
}
function maskIcon(inside, shade) {  // inside(x, y) -> bool; shade(x, y, top, bottom) -> colour; outline added outside
  const m = [...Array(16)].map((_, y) => [...Array(16)].map((_, x) => inside(x, y)));
  const has = (x, y) => x >= 0 && y >= 0 && x < 16 && y < 16 && m[y][x];
  return m.map((row, y) => row.map((v, x) => {
    if (v) return shade(x, y, !has(x, y - 1), !has(x, y + 1));
    return [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([a, b]) => has(x + a, y + b)) ? C.O : null;
  }));
}
const goldShade = (x, y, top, bottom) => top ? C.goldHi : bottom ? C.goldLo : C.gold;
const ICONS = {
  pokeball: strIcon([
    '.....OOOOOO.....', '...OORRRRRROO...', '..ORRRRRRRRRRO..', '.ORhhRRRRRRRRrO.', '.ORhRRRRRRRRRrO.', 'ORRRRROOOORRRrrO',
    'ORRRROWWWWORRrrO', 'OOOOOOWWWWOOOOOO', 'OOOOOOWWWWOOOOOO', 'OWWWWOWWWWOWWwwO', 'OWWWWWOOOOWWWwwO', '.OWWWWWWWWWWwwO.',
    '.OWWWWWWWWWwwwO.', '..OwWWWWWWwwwO..', '...OOwwwwwwOO...', '.....OOOOOO.....',
  ], { O: C.O, R: 'E8343F', r: 'A61E2A', h: 'FF9A9A', W: 'F4F4F4', w: 'C3C9D9' }),
  compass: strIcon([
    '.....OOOOOO.....', '...OOGGGGGGOO...', '..OGGFFFFFFggO..', '.OGFFFFtFFFFFgO.', '.OGFFFFFFFFNNgO.', 'OGFFFFFFFFNNNFgO',
    'OGFFFFFFFNNNFFgO', 'OGtFFFFFcNNFFtgO', 'OGFFFFFncFFFFFgO', 'OGFFFFnnnFFFFFgO', 'OGFFFnnnFFFFFfgO', '.OGFFnnFFFFFffO.',
    '.OgFFFFFtFFfffO.', '..OggfffffffgO..', '...OOggggggOO...', '.....OOOOOO.....',
  ], { O: C.O, G: C.gold, g: C.goldLo, F: C.cream, f: 'EADBB8', t: C.mist, N: 'E8343F', n: C.navyLite, c: C.O }),
  house: strIcon([
    '.......OO.......', '......ORRO......', '.....ORRRRO.....', '....ORhRRRRO....', '...ORhRRRRRRO...', '..ORhRRRRRRRRO..',
    '.ORRRRRRRRRRRRO.', 'OrrrrrrrrrrrrrrO', '.OWWWWWWWWWWWwO.', '.OWKKWWddWWKKwO.', '.OWKKWWDDWWKKwO.', '.OWWWWWDDWWWWwO.',
    '.OWWWWWDkWWWWwO.', '.OWWWWWDDWWWWwO.', '.OwwwwwDDwwwwwO.', '.OOOOOOOOOOOOOO.',
  ], { O: C.O, R: 'C8283C', r: '8E1A2A', h: 'F06A78', W: C.cream, w: 'EADBB8', K: C.glow, D: C.navyLite, d: C.navy, k: C.goldHi }),
  trophy: strIcon([
    '...OOOOOOOOOO...', '.OOOGGGGGGgdOOO.', 'OO.OGWGGGGgdO.OO', 'O..OGGGGGGgdO..O', 'OO.OGGGGGGgdO.OO', '.OOOgGGGGGgdOOO.',
    '...OgGGGGggdO...', '....OggggddO....', '.....OgggdO.....', '......OgdO......', '......OgdO......', '.....OOgdOO.....',
    '....OBBBBBBO....', '...OBBBBBBBbO...', '...ObbbbbbbbO...', '...OOOOOOOOOO...',
  ], { O: C.O, G: C.goldHi, g: C.gold, d: C.goldLo, W: C.cream, B: C.navyLite, b: C.navy }),
  back: maskIcon((x, y) =>
    (x >= 1 && x <= 5 && Math.abs(y - 6) <= x - 1) ||          // arrow head, tip at (1, 6)
    (x >= 6 && x <= 12 && y >= 5 && y <= 7) ||                  // top shaft
    (x >= 11 && x <= 13 && y >= 5 && y <= 12 && !(x === 13 && (y === 5 || y === 12))) ||  // bend
    (x >= 6 && x <= 12 && y >= 10 && y <= 12), goldShade),     // bottom shaft
  star: maskIcon((x, y) => {
    const pts = [...Array(10)].map((_, i) => { const a = -Math.PI / 2 + i * Math.PI / 5, rad = i % 2 ? 3.1 : 7.4; return [7.5 + rad * Math.cos(a), 8 + rad * Math.sin(a)]; });
    let inside = false;
    for (let i = 0, j = 9; i < 10; j = i++) {
      const [xi, yi] = pts[i], [xj, yj] = pts[j], px = x + 0.5, py = y + 0.5;
      if ((yi > py) !== (yj > py) && px < (xj - xi) * (py - yi) / (yj - yi) + xi) inside = !inside;
    }
    return inside;
  }, goldShade),
  coin: maskIcon((x, y) => Math.hypot(x - 7.5, y - 7.5) <= 6.6, (x, y, top, bottom) => {
    const d = Math.hypot(x - 7.5, y - 7.5);
    if (d > 4.2 && d <= 5.2) return C.goldLo;                  // engraved inner ring
    if (top || (x + y < 9 && d > 5.2)) return C.goldHi;
    if (bottom || (x + y > 21 && d > 5.2)) return C.goldLo;
    return (x === 6 && y >= 5 && y <= 10) || (y === 5 && x >= 7 && x <= 9) || (y === 10 && x >= 7 && x <= 9) ? C.cream : C.gold;
  }),
};
// warp: a violet swirl portal (spiral bands by angle + radius, bright core)
ICONS.warp = maskIcon((x, y) => ((x - 7.5) / 6.6) ** 2 + ((y - 7.5) / 7.4) ** 2 <= 1, (x, y) => {
  const dx = (x - 7.5) / 6.6, dy = (y - 7.5) / 7.4, r = Math.hypot(dx, dy), a = Math.atan2(dy, dx);
  if (r < 0.22) return C.cream;
  if (r < 0.42) return 'D6C2FF';
  return Math.floor(a / (2 * Math.PI) * 5 + r * 3.2 + 10) % 2 ? 'A98BEA' : '5A3DA6';
});
// leave: a wooden door with a green exit arrow over it (each part outlined on its own)
ICONS.leave = (() => {
  const door = maskIcon((x, y) => x >= 2 && x <= 8 && y >= 1 && y <= 14, (x, y) => x === 7 && y === 8 ? C.goldHi : x <= 3 ? 'A0662C' : '7A4A1E');
  const arrow = maskIcon((x, y) => (x >= 6 && x <= 11 && y >= 6 && y <= 8) || (x >= 12 && x <= 15 && Math.abs(y - 7) <= 15 - x),
    (x, y, top, bottom) => top ? '78DB98' : bottom ? '26874D' : '33A35F');
  return door.map((row, y) => row.map((c, x) => arrow[y][x] || c));
})();
const inPoly = (pts, x, y) => {  // even-odd test of the texel centre
  let inside = false;
  for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
    const [xi, yi] = pts[i], [xj, yj] = pts[j], px = x + 0.5, py = y + 0.5;
    if ((yi > py) !== (yj > py) && px < (xj - xi) * (py - yi) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
};
// crown: three points over a band set with red and blue stones
ICONS.crown = maskIcon((x, y) => x >= 2 && x <= 13 && y <= 13 && y >= Math.min(...[2, 7.5, 13].map(p => 3 + 1.3 * Math.abs(x - p))),
  (x, y, top, bottom) => y === 11 && (x === 4 || x === 11) ? 'E8343F' : y === 11 && (x === 7 || x === 8) ? C.glow : y === 9 ? C.goldLo : goldShade(x, y, top, bottom));
// bolt: a gold lightning bolt
ICONS.bolt = maskIcon((x, y) => inPoly([[9.5, 0.5], [2.5, 9], [7, 9], [5, 15.5], [13.5, 6], [8.8, 6], [11.5, 0.5]], x, y),
  (x, y, top, bottom) => top || x + y < 9 ? C.cream : bottom ? C.goldLo : x > 9 ? C.gold : C.goldHi);
// gem: a cut blue token, light crown facets over darker pavilion facets
ICONS.gem = maskIcon((x, y) => inPoly([[4, 1.5], [12, 1.5], [15, 6], [8, 15], [1, 6]], x, y),
  (x, y) => (x === 4 || x === 5) && y === 3 ? C.cream : y <= 5 ? (x < 8 ? 'BFD3FF' : '8FB0F0') : x < 6 ? C.glow : x < 10 ? '4A74C8' : C.slotLite);
// crate: a wooden loot crate with gold corner bands and a latch
ICONS.crate = maskIcon((x, y) => x >= 1 && x <= 14 && y >= 3 && y <= 14 && !(y === 3 && (x === 1 || x === 14)), (x, y) => {
  if ((x === 7 || x === 8) && y >= 7 && y <= 10) return y === 7 ? C.goldHi : y === 10 ? C.goldLo : C.gold;
  if (x <= 2 || x >= 13) return x === 1 ? C.goldHi : x === 14 ? C.goldLo : C.gold;
  if (y === 8) return '4A2A10';
  if (y < 8) return y === 3 ? 'C8904E' : 'B5793A';
  return y === 11 || y === 14 ? '6A3E18' : '8A5626';
});
// globe: a blue world with cream latitude and meridian lines
ICONS.globe = maskIcon((x, y) => Math.hypot(x - 7.5, y - 7.5) <= 6.6, (x, y) => {
  const dx = x - 7.5, dy = y - 7.5, e = (dx / 3.4) ** 2 + (dy / 6.6) ** 2;
  if (Math.abs(dy) < 0.6 || Math.abs(dx) < 0.6 || (e > 0.7 && e < 1.25) || y === 3 || y === 12) return 'D6E2FA';
  return dx + dy < -4 ? '8FB0F0' : dx + dy > 5 ? '2E5DC0' : '4A86F0';
});
// pointer arrows for a reel: a short gold shaft and a wide head (arrow_down points at the cell below)
ICONS.arrow_down = maskIcon((x, y) => (x >= 6 && x <= 9 && y >= 2 && y <= 6) || (y >= 7 && y <= 12 && Math.abs(x - 7.5) <= 12.5 - y), goldShade);
// flipped, with highlight and shade swapped so the light still falls from the top
ICONS.arrow_up = [...ICONS.arrow_down].reverse().map(row => row.map(c => c === C.goldHi ? C.goldLo : c === C.goldLo ? C.goldHi : c));
function drawIcon(r, name, x, y) {
  const ic = ICONS[name]; if (!ic) throw new Error('no icon ' + name);
  ic.forEach((row, j) => row.forEach((c, i) => { if (c) r.set(x + i, y + j, c); }));
}

// ---------------- constructions ----------------
// Chamfered button (DESIGN.md framed()): outline, bevelled rim, bevelled inner line, two-tone fill; 1 px chamfer.
function framed(r, x0, y0, w, h, p) {
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    if ((x === 0 || x === w - 1) && (y === 0 || y === h - 1)) continue;
    const edge = Math.min(x, y, w - 1 - x, h - 1 - y), tl = (y === edge || x === edge) && !(y === h - 1 - edge || x === w - 1 - edge);
    r.set(x0 + x, y0 + y, edge === 0 ? C.O : edge === 1 ? (tl ? p.rimHi : p.rimLo) : edge === 2 ? (tl ? p.inHi : p.inLo) : (y < h / 2 ? p.top : p.bottom));
  }
}
// Plate (DESIGN.md new panels): 2 px chamfer, outline, rim, bevel, flat fill.
function plate(r, x0, y0, w, h, p) {
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const dx = Math.min(x, w - 1 - x), dy = Math.min(y, h - 1 - y), edge = Math.min(dx, dy), corner = dx + dy;
    if (corner < 2) continue;
    const tl = (y <= edge || x <= edge) && !(y >= h - 1 - edge || x >= w - 1 - edge);
    r.set(x0 + x, y0 + y, edge === 0 || corner === 2 ? C.O : edge === 1 ? (tl ? p.rimHi : p.rimLo) : edge === 2 ? (tl ? p.bevHi : p.bevLo) : p.fill);
  }
}
// Recessed well: dark top/left, light bottom/right, the two off corners take the interior colour (vanilla slot rule).
function well(r, x, y, w, h, inner) {
  if (inner !== undefined) r.rect(x + 1, y + 1, w - 2, h - 2, inner);
  r.rect(x, y, w - 1, 1, C.slotDark); r.rect(x, y, 1, h - 1, C.slotDark);
  r.rect(x + 1, y + h - 1, w - 1, 1, C.slotLite); r.rect(x + w - 1, y + 1, 1, h - 1, C.slotLite);
  r.set(x + w - 1, y, C.slotIn); r.set(x, y + h - 1, C.slotIn);
}

const BUTTON = {  // framed() palettes; text + shadow drawn on the fill
  navy: { rimHi: 'F7D27A', rimLo: 'B07A22', inHi: '3A5A9C', inLo: '142246', top: '22396E', bottom: '1B2E5B', text: C.cream, shadow: C.O },
  red: { rimHi: 'F7D27A', rimLo: 'B07A22', inHi: 'F0707E', inLo: '6E0F1F', top: 'CC3245', bottom: 'AE2236', text: C.cream, shadow: '4A0B14' },
  green: { rimHi: 'F7D27A', rimLo: 'B07A22', inHi: '78DB98', inLo: '135A2E', top: '33A35F', bottom: '26874D', text: C.cream, shadow: '0C3519' },
  gold: { rimHi: 'FFF1D0', rimLo: '8A5A12', inHi: 'FFE9A8', inLo: 'B07A22', top: 'F2C462', bottom: 'E2B04A', text: C.navy, shadow: null },
  done: { rimHi: '9AA6C4', rimLo: '4A5576', inHi: '6B7799', inLo: '1E2640', top: '3A4566', bottom: '323C5A', text: '9AA6C4', shadow: C.O },
};
const CARD = {  // plate() palettes
  navy: { rimHi: C.rimHi, rimLo: C.rimLo, bevHi: '3A5A9C', bevLo: '142246', fill: C.navyLite, text: C.cream, shadow: C.O },
  red: { rimHi: C.rimHi, rimLo: C.rimLo, bevHi: 'F0707E', bevLo: '6E0F1F', fill: 'B8293D', text: C.cream, shadow: '4A0B14' },
  green: { rimHi: C.rimHi, rimLo: C.rimLo, bevHi: '78DB98', bevLo: '135A2E', fill: '2B9152', text: C.cream, shadow: '0C3519' },
  gold: { rimHi: 'FFF1D0', rimLo: '8A5A12', bevHi: 'FFE9A8', bevLo: 'B07A22', fill: C.gold, text: C.navy, shadow: null },
  violet: { rimHi: C.rimHi, rimLo: C.rimLo, bevHi: 'A98BEA', bevLo: '2A1857', fill: '5A3DA6', text: C.cream, shadow: '1C0F3A' },
};
const SKY = ['0B1433', '0D1839', '101C40', '132147', '16264F', '1A2C58'];

// Shell: the chest's top part, outline/rim/bevel identical to generic_54 (2 px chamfer top-left, 3 px top-right),
// open at the bottom where the vanilla texture continues.
function shell(r, rows) {
  const h = menuHeight(rows);
  r.rect(0, 0, W, h, C.fill);
  r.rect(0, 0, 2, 1, null); r.set(0, 1, null); r.rect(173, 0, 3, 1, null); r.rect(174, 1, 2, 1, null); r.set(175, 2, null);
  r.rect(2, 0, 171, 1, C.O); r.set(1, 1, C.O); r.set(173, 1, C.O); r.set(174, 2, C.O);
  r.rect(0, 2, 1, h - 2, C.O); r.rect(175, 3, 1, h - 3, C.O);
  r.rect(2, 1, 171, 1, C.rimHi); r.rect(1, 2, 1, h - 2, C.rimHi); r.set(173, 2, C.rimHi); r.rect(174, 3, 1, h - 3, C.rimLo);
  r.rect(2, 2, 171, 1, C.bevHi); r.rect(2, 3, 1, h - 3, C.bevHi); r.rect(173, 3, 1, h - 3, C.bevLo);
}

function panel(r, style, cx, cy, cw, ch) {
  const x = cellX(cx), y = cellY(cy), w = CELL * cw, h = CELL * ch;
  if (style === 'well') well(r, x, y, w, h, C.navy);
  else if (style === 'night') {
    for (let j = 1; j < h - 1; j++) r.rect(x + 1, y + j, w - 2, 1, SKY[Math.min(SKY.length - 1, Math.floor((j - 1) / (h - 2) * SKY.length))]);
    for (let j = 3; j < h - 3; j++) for (let i = 3; i < w - 3; i++) {
      const n = (((x + i) * 73856093) ^ ((y + j) * 19349663)) >>> 0;
      if (n % 61 === 0) { const c = n % 3 === 0 ? C.cream : n % 3 === 1 ? C.glow : C.slotLite; r.set(x + i, y + j, c); (r.stars = r.stars || new Map()).set((x + i) + ',' + (y + j), c); }
    }
    well(r, x, y, w, h);
  } else if (style === 'stripes') {
    for (let j = 1; j < h - 1; j++) for (let i = 1; i < w - 1; i++) r.set(x + i, y + j, Math.floor((x + i + y + j) / 6) % 2 ? '182A54' : '213768');
    well(r, x, y, w, h);
  } else throw new Error('panel style ' + style);
}
function card(r, color, icon, label, cx, cy, cw, ch) {
  const p = CARD[color]; if (!p) throw new Error('card colour ' + color);
  const x = cellX(cx) + 1, y = cellY(cy) + 1, w = CELL * cw - 2, h = CELL * ch - 2;
  plate(r, x, y, w, h, p);
  if (icon && label && ch === 1) {  // one row: icon left of the label, the pair centred
    const gw = 18 + textWidth(label), gx = x + Math.floor((w - gw) / 2);
    if (gw > w - 4) throw new Error('icon + label too wide for ' + cw + ' cells: ' + label);
    drawIcon(r, icon, gx, y);
    drawText(r, label, gx + 18, y + 4, p.text, p.shadow);
  } else if (icon && label) {
    drawIcon(r, icon, x + Math.floor((w - 16) / 2), y + Math.floor((h - 28) / 2));
    drawText(r, label, x + Math.floor((w - textWidth(label)) / 2), y + Math.floor((h - 28) / 2) + 20, p.text, p.shadow);
  } else if (icon) drawIcon(r, icon, x + Math.floor((w - 16) / 2), y + Math.floor((h - 16) / 2));
  else if (label) drawText(r, label, x + Math.floor((w - textWidth(label)) / 2), y + Math.floor((h - 7) / 2), p.text, p.shadow);
}
function button(r, color, label, cx, cy, cw) {
  const p = BUTTON[color]; if (!p) throw new Error('button colour ' + color);
  const x = cellX(cx) + 1, y = cellY(cy) + 1, w = CELL * cw - 2;
  framed(r, x, y, w, 16, p);
  if (label) {
    if (textWidth(label) > w - 6) throw new Error('label too wide for ' + cw + ' cells: ' + label);
    drawText(r, label, x + Math.floor((w - textWidth(label)) / 2), y + 4, p.text, p.shadow);
  }
}
function iconButton(r, color, icon, cx, cy) {
  const p = BUTTON[color], g = SMALL[icon]; if (!p || !g) throw new Error('icon button ' + color + '/' + icon);
  const x = cellX(cx) + 1, y = cellY(cy) + 1;
  framed(r, x, y, 16, 16, p);
  drawMask(r, g, x + Math.floor((16 - g[0].length) / 2), y + Math.floor((16 - g.length) / 2), p.text, p.shadow);
}
function tab(r, color, dir, cx, cy, ch) {
  const p = BUTTON[color], g = TRI[dir]; if (!p || !g) throw new Error('tab ' + color + '/' + dir);
  const x = cellX(cx) + 1, y = cellY(cy) + 1, h = CELL * ch - 2;
  framed(r, x, y, 16, h, p);
  drawMask(r, g, x + Math.floor((16 - g[0].length) / 2), y + Math.floor((h - g.length) / 2), p.text, p.shadow);
}
function ring(r, x, y, w, h, tl, br) {  // 1 px frame, light top/left, dark bottom/right
  r.rect(x, y, w, 1, tl); r.rect(x, y, 1, h, tl); r.rect(x + 1, y + h - 1, w - 1, 1, br); r.rect(x + w - 1, y + 1, 1, h - 1, br);
}
// Pedestal: a gold-rimmed well standing on a two-step gold plinth that is wider than the cell. It only grows sideways
// (the rows above and below may hold pedestals too) and casts a shadow to its right.
function pedestal(r, X, Y) {
  for (const [y, h, e] of [[Y + 11, 4, 2], [Y + 14, 4, 4]]) {  // steps: top row, height, overhang per side
    r.rect(X - 1 - e, y, CELL + 2 + 2 * e, h, C.O);
    r.rect(X - e, y + 1, CELL + 2 * e, 1, C.goldHi); r.rect(X - e, y + 2, CELL + 2 * e, h - 3, C.gold);
    r.rect(X - e, y + h - 2, CELL + 2 * e, 1, C.goldLo);
    r.rect(X + CELL + 1 + e, y + 1, 1, h - 1, C.navyDeep);
  }
  r.rect(X - 1, Y, 1, 11, C.O); r.rect(X + CELL, Y, 1, 11, C.O); r.rect(X + CELL + 1, Y + 1, 1, 10, C.navyDeep);
  ring(r, X, Y, CELL, CELL, C.goldHi, C.goldLo);
}
// Reel row: dim navy frames, the middle cell picked out with a bright gold double frame and a blue glow halo.
function reel(r, cx, cy, cw) {
  const mid = Math.floor(cw / 2);
  for (let i = 0; i < cw; i++) if (i !== mid) ring(r, cellX(cx + i), cellY(cy), CELL, CELL, C.navyDeep, C.navyLite);
  const X = cellX(cx + mid), Y = cellY(cy);
  ring(r, X - 2, Y - 2, CELL + 4, CELL + 4, C.glow, C.glow);
  ring(r, X - 1, Y - 1, CELL + 2, CELL + 2, C.gold, C.goldLo);
  ring(r, X, Y, CELL, CELL, C.goldHi, C.gold);
}
function slotRings(r, cx, cy, cw, ch, style) {  // slot borders; the 16x16 interiors are cleared by holes()
  if (style === 'reel') return reel(r, cx, cy, cw);
  for (let j = 0; j < ch; j++) for (let i = 0; i < cw; i++) {
    if (style === 'pedestal') pedestal(r, cellX(cx + i), cellY(cy + j));
    else well(r, cellX(cx + i), cellY(cy + j), CELL, CELL, C.slotIn);
  }
}
function arrow(r, dir, cx, cy) { drawIcon(r, 'arrow_' + dir, cellX(cx) + 1, cellY(cy) + 1); }
function holes(r, cx, cy, cw, ch) {
  for (let j = 0; j < ch; j++) for (let i = 0; i < cw; i++) r.rect(cellX(cx + i) + 1, cellY(cy + j) + 1, 16, 16, null);
}
const STARS = new Set([C.cream, C.glow, C.slotLite]);
function text(r, label, color, cx, cy, cw) {
  const tc = color === 'gold' ? C.goldHi : C.cream, x = cellX(cx) + Math.floor((CELL * cw - textWidth(label)) / 2), y = cellY(cy) + 5;
  // night-panel stars next to letters read as punctuation: clear them around the text (take the sky colour to the left)
  for (let j = y - 2; j <= y + 9; j++) for (let i = x - 3; i <= x + textWidth(label) + 3; i++) {
    if (!STARS.has(r.get(i, j))) continue;
    let k = i - 1; while (STARS.has(r.get(k, j))) k--;
    r.set(i, j, r.get(k, j));
  }
  drawText(r, label, x, y, tc, C.O);
}

// A star the night panel placed and nothing has painted over since. Colour alone cannot tell it from the slot rings
// (slotLite) or button text, so clearStarsAround only touches the stars panel() recorded.
function liveStar(r, x, y) { return !!r.stars && r.stars.get(x + ',' + y) === r.get(x, y); }
// Stars left in the 2px gaps around a drawn button/card/icon button (rect {x, y, w, h}): take the nearest colour to
// the left that is neither a star nor part of the element itself.
function clearStarsAround(r, x, y, w, h) {
  const inEx = (i, j) => i >= x && i < x + w && j >= y && j < y + h;
  for (let j = y - 2; j <= y + h + 1; j++) for (let i = x - 2; i <= x + w + 1; i++) {
    if (inEx(i, j) || !liveStar(r, i, j)) continue;
    let k = i - 1; while (liveStar(r, k, j) || inEx(k, j)) k--;
    r.set(i, j, r.get(k, j)); r.stars.delete(i + ',' + j);
  }
}

// One spec element (menus/spec.json) onto a raster; slot holes are punched after every element is drawn.
function drawElement(r, e) {
  const w = e.w || 1, h = e.h || 1;
  if (e.type === 'panel') panel(r, e.style, e.x, e.y, w, h);
  else if (e.type === 'card') { card(r, e.color, e.icon, e.label, e.x, e.y, w, h); clearStarsAround(r, cellX(e.x) + 1, cellY(e.y) + 1, CELL * w - 2, CELL * h - 2); }
  else if (e.type === 'button') { button(r, e.color, e.label, e.x, e.y, w); clearStarsAround(r, cellX(e.x) + 1, cellY(e.y) + 1, CELL * w - 2, 16); }
  else if (e.type === 'icon_button') { iconButton(r, e.color, e.icon, e.x, e.y); clearStarsAround(r, cellX(e.x) + 1, cellY(e.y) + 1, 16, 16); }
  else if (e.type === 'tab') tab(r, e.color, e.icon, e.x, e.y, h);
  else if (e.type === 'slot') slotRings(r, e.x, e.y, w, h, e.style);
  else if (e.type === 'arrow') { arrow(r, e.icon, e.x, e.y); clearStarsAround(r, cellX(e.x) + 1, cellY(e.y) + 1, 16, 16); }
  else if (e.type === 'text') text(r, e.label, e.color, e.x, e.y, w);
  else throw new Error('element type ' + e.type);
}
function drawMenu(r, menu) {
  shell(r, menu.rows);
  for (const e of menu.elements) drawElement(r, e);
  for (const e of menu.elements) if (e.type === 'slot') holes(r, e.x, e.y, e.w || 1, e.h || 1);
}
// Approximate vanilla bottom part (player inventory) for previews only; the game draws the real one.
function inventoryMock(r, y0) {
  r.rect(0, y0, W, 96, C.fill);
  r.rect(0, y0, 1, 94, C.O); r.rect(1, y0, 1, 93, C.rimHi); r.rect(2, y0, 1, 92, C.bevHi);
  r.rect(175, y0, 1, 94, C.O); r.rect(174, y0, 1, 94, C.rimLo); r.rect(173, y0, 1, 93, C.bevLo);
  r.rect(2, y0 + 95, 172, 1, C.O); r.rect(1, y0 + 94, 1, 1, C.O); r.rect(2, y0 + 94, 172, 1, C.rimLo); r.rect(3, y0 + 93, 170, 1, C.bevLo);
  r.set(0, y0 + 94, null); r.set(0, y0 + 95, null); r.set(1, y0 + 95, null); r.set(175, y0 + 94, null); r.set(175, y0 + 95, null); r.set(174, y0 + 95, null);
  r.set(174, y0 + 94, C.O);
  for (let row = 0; row < 3; row++) for (let c = 0; c < 9; c++) well(r, cellX(c), y0 + 13 + row * CELL, CELL, CELL, C.slotIn);
  for (let c = 0; c < 9; c++) well(r, cellX(c), y0 + 71, CELL, CELL, C.slotIn);
}

// ---------------- Figma helpers ----------------
function fframe(parent, name, x, y, w, h, fill) {
  const f = figma.createFrame();
  f.name = name; f.resize(w, h); f.x = x; f.y = y; f.clipsContent = true;
  f.fills = fill ? [{ type: 'SOLID', color: hex(fill) }] : [];
  parent.appendChild(f); return f;
}
function ftext(parent, s, x, y, size, color) {
  const t = figma.createText();
  t.fontName = { family: 'Inter', style: 'Bold' }; t.characters = s; t.fontSize = size;
  t.fills = [{ type: 'SOLID', color: hex(color) }]; t.x = x; t.y = y; parent.appendChild(t); return t;
}
async function usePage(name) {
  let page = figma.root.children.find(p => p.name === name);
  if (!page) { page = figma.createPage(); page.name = name; }
  await figma.setCurrentPageAsync(page);
  page.backgrounds = [{ type: 'SOLID', color: hex('E5E5E5') }];
  return page;
}
