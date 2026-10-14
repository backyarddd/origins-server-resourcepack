// Figma (use_figma) script: page "Menu Kit", the template pack. Every part is a component drawn at 1x with the menu
// constructions in lib.js (prepended by `python -I menus/build.py figma`). Cell-based parts (buttons, cards, panels,
// slot grids, tabs) are exactly 18*w x 18*h so instances snap onto a menu's cell grid (cell (c, r) of a menu is at
// x = 7 + 18c, y = 17 + 18r); frames are whole 176 px menu backgrounds. Slot holes are transparent on purpose: in game
// they show the vanilla slot (and its hover highlight) under real items.
// Rerunnable per part: prepend `const PART = 'frames';` (frames | buttons | controls | cards | glyphs) to rebuild one
// section, or run without PART for all of them.
await figma.loadFontAsync({ family: 'Inter', style: 'Bold' });
const page = await usePage('Menu Kit');
const PARTS = { frames: ['Frames', 0], buttons: ['Buttons', 1500], controls: ['Controls', 2400], cards: ['Cards & panels', 3200], glyphs: ['Icons & font', 4500] };
const RUN = typeof PART === 'undefined' ? Object.keys(PARTS) : [PART];
const stats = { components: 0, rects: 0 };

function comp(parent, name, w, h, x, y, draw, ox = 0, oy = 0) {
  const r = new Raster(w, h, ox, oy); draw(r);
  const c = figma.createComponent();
  c.name = name; c.resize(w, h); c.x = x; c.y = y; c.fills = []; c.clipsContent = true;
  parent.appendChild(c);
  stats.rects += r.emit(c); stats.components++;
  return c;
}
// a cell-sized part: drawn with menu coordinates at cell (0, 0), so the raster origin is the cell's top-left corner
const cellComp = (parent, name, cw, ch, x, y, draw) => comp(parent, name, CELL * cw, CELL * ch, x, y, draw, GX, GY);
function section(key) {
  const [title, x] = PARTS[key];
  const s = figma.createSection(); s.name = title; s.x = x; s.y = 0;
  page.appendChild(s);
  s.fills = [{ type: 'SOLID', color: hex('202020') }];
  ftext(s, title, 30, 20, 24, 'FFFFFF');
  return s;
}
function finish(s, items) {
  const right = Math.max(...items.map(n => n.x + n.width)), bottom = Math.max(...items.map(n => n.y + n.height));
  s.resizeWithoutConstraints(right + 40, bottom + 40);
}
const caption = (s, t, x, y) => ftext(s, t, x, y, 12, 'C9D4EC');
const bw = label => { const w = [2, 3, 4].find(n => textWidth(label) <= CELL * n - 8); if (!w) throw new Error('label too long: ' + label); return w; };

// ---------------- frames: shell + layout presets, 1 to 6 rows ----------------
function layouts(R) {
  const f = R - 1;  // footer row
  return {
    plain: [{ type: 'panel', style: 'well', x: 0, y: 0, w: 9, h: R }],
    footer: [{ type: 'panel', style: 'well', x: 0, y: 0, w: 9, h: f },
      { type: 'button', color: 'red', x: 1, y: f, w: 3 }, { type: 'button', color: 'green', x: 5, y: f, w: 3 }],
    paged: [{ type: 'panel', style: 'well', x: 0, y: 0, w: 9, h: f }, { type: 'icon_button', color: 'red', icon: 'return', x: 0, y: f },
      { type: 'icon_button', color: 'navy', icon: 'left', x: 3, y: f }, { type: 'icon_button', color: 'navy', icon: 'right', x: 5, y: f },
      { type: 'icon_button', color: 'navy', icon: 'info', x: 8, y: f }],
    night: [{ type: 'panel', style: 'night', x: 0, y: 0, w: 9, h: f }, { type: 'button', color: 'red', x: 3, y: f, w: 3 }],
    split: [{ type: 'panel', style: 'well', x: 0, y: 0, w: 4, h: f }, { type: 'panel', style: 'night', x: 4, y: 0, w: 5, h: f },
      { type: 'button', color: 'red', x: 0, y: f, w: 3 }, { type: 'button', color: 'green', x: 6, y: f, w: 3 }],
    sidebar: [{ type: 'panel', style: 'well', x: 0, y: 0, w: 6, h: f }, { type: 'panel', style: 'stripes', x: 6, y: 0, w: 3, h: f },
      ...[...Array(f)].map((_, i) => ({ type: 'card', color: ['navy', 'gold', 'green', 'red', 'violet'][i % 5], x: 6, y: i, w: 3, h: 1 })),
      { type: 'icon_button', color: 'red', icon: 'return', x: 0, y: f }],
    grid: [{ type: 'panel', style: 'stripes', x: 0, y: 0, w: 9, h: f }, { type: 'tab', color: 'navy', icon: 'left', x: 0, y: 0, h: f },
      { type: 'tab', color: 'navy', icon: 'right', x: 8, y: 0, h: f }, { type: 'slot', x: 1, y: 0, w: 7, h: f },
      { type: 'icon_button', color: 'red', icon: 'return', x: 0, y: f }, { type: 'button', color: 'red', x: 3, y: f, w: 3 }],
  };
}
function buildFrames() {
  const s = section('frames'), items = [];
  const list = [[1, 'plain'], [2, 'plain']];
  for (const R of [3, 4, 5, 6]) for (const k of Object.keys(layouts(R))) list.push([R, k]);
  list.forEach(([R, k], i) => {
    const col = i % 6, row = Math.floor(i / 6), x = 30 + col * 216, y = 80 + row * 190;
    items.push(comp(s, `Frame/${R} rows/${k}`, W, menuHeight(R), x, y, r => drawMenu(r, { rows: R, elements: layouts(R)[k] })));
    items.push(caption(s, `${R} rows · ${k}`, x, y + menuHeight(R) + 6));
  });
  finish(s, items);
}

// ---------------- buttons: labelled, by colour; blank ones for custom layouts ----------------
const LABELS = {
  red: ['CANCEL', 'DECLINE', 'CLOSE', 'BACK', 'REMOVE', 'SELL', 'NO', 'EXIT', 'STOP', 'DELETE'],
  green: ['CONFIRM', 'ACCEPT', 'BUY', 'ADD', 'YES', 'START', 'SELECT', 'CLAIM', 'SAVE', 'JOIN'],
  gold: ['MENU', 'SPAWN', 'RTP', 'HOMES', 'WARPS', 'KITS', 'SHOP', 'QUESTS', 'REWARDS', 'VOTE', 'TOWN', 'PARTY', 'PC', 'TRADE',
    'BATTLE', 'EVENTS', 'RANKS', 'STORE', 'RULES', 'INFO', 'SETTINGS', 'NEXT', 'PREV', 'PAGE'],
};
LABELS.navy = LABELS.gold;
function buildButtons() {
  const s = section('buttons'), items = [];
  ['red', 'green', 'gold', 'navy'].forEach((color, ci) => {
    const x = 30 + ci * 190;
    items.push(caption(s, color, x, 70));
    [...LABELS[color], '', '', ''].forEach((label, i) => {
      const w = label ? bw(label) : [2, 3, 4][i - LABELS[color].length], y = 100 + i * 26;
      items.push(cellComp(s, `Button/${color}/${label || 'blank ' + w}`, w, 1, x, y, r => button(r, color, label, 0, 0, w)));
    });
  });
  finish(s, items);
}

// ---------------- controls: icon buttons, side tabs, slot grids ----------------
function buildControls() {
  const s = section('controls'), items = [];
  const icons = Object.keys(SMALL);
  ['red', 'green', 'gold', 'navy'].forEach((color, ci) => {
    items.push(caption(s, color, 30, 100 + ci * 30));
    icons.forEach((icon, i) => items.push(cellComp(s, `Icon Button/${color}/${icon}`, 1, 1, 90 + i * 26, 96 + ci * 30, r => iconButton(r, color, icon, 0, 0))));
  });
  items.push(caption(s, 'side tabs (1 x 2-4 cells)', 30, 240));
  let x = 30;
  for (const color of ['navy', 'gold', 'red', 'green']) for (const dir of ['left', 'right']) for (const h of [2, 3, 4]) {
    items.push(cellComp(s, `Tab/${color}/${dir}/${h}`, 1, h, x, 270, r => tab(r, color, dir, 0, 0, h)));
    x += 24;
  }
  items.push(caption(s, 'slot grids (holes show the vanilla slot in game)', 30, 380));
  let gx = 30, gy = 410;
  for (const [w, h] of [[1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [7, 1], [9, 1], [3, 2], [5, 2], [7, 2], [9, 2], [3, 3], [5, 3], [7, 3], [9, 3], [4, 4], [9, 4]]) {
    if (gx + CELL * w > 700) { gx = 30; gy += 90; }
    items.push(cellComp(s, `Slots/${w}x${h}`, w, h, gx, gy, r => { slotRings(r, 0, 0, w, h); holes(r, 0, 0, w, h); }));
    gx += CELL * w + 20;
  }
  // slot styles and reel arrows; pedestal and reel draw outside their cells, so their rasters get a margin
  const sy = gy + 100;
  items.push(caption(s, 'slot styles: pedestal (1 x 2 shown stacked), reel (middle cell picked); reel arrows', 30, sy));
  items.push(comp(s, 'Slots/pedestal', CELL + 12, CELL * 2, 30, sy + 30, r => { slotRings(r, 0, 0, 1, 2, 'pedestal'); holes(r, 0, 0, 1, 2); }, GX - 6, GY));
  items.push(comp(s, 'Slots/reel 9x1', CELL * 9, CELL + 4, 80, sy + 30, r => { slotRings(r, 0, 0, 9, 1, 'reel'); holes(r, 0, 0, 9, 1); }, GX, GY - 2));
  ['down', 'up'].forEach((dir, i) => items.push(cellComp(s, `Arrow/${dir}`, 1, 1, 260 + i * 26, sy + 30, r => arrow(r, dir, 0, 0))));
  finish(s, items);
}

// ---------------- cards and panels ----------------
function buildCards() {
  const s = section('cards'), items = [];
  const colors = Object.keys(CARD);
  colors.forEach((color, ci) => {
    const y = 80 + ci * 60;
    items.push(caption(s, color, 30, y + 10));
    let x = 90;
    for (const [w, h] of [[1, 1], [2, 1], [3, 1], [2, 2], [3, 2], [4, 2], [3, 3], [9, 1]]) {
      items.push(cellComp(s, `Card/${color}/${w}x${h}`, w, h, x, y, r => card(r, color, null, null, 0, 0, w, h)));
      x += CELL * w + 16;
    }
  });
  const sy = 80 + colors.length * 60 + 20;
  items.push(caption(s, 'example cards (icon + label, as menus.json draws them)', 30, sy));
  [['navy', 'pokeball', 'SPAWN'], ['navy', 'compass', 'RTP'], ['navy', 'house', 'HOMES'], ['red', 'back', 'BACK'], ['green', 'leave', 'LEAVE'],
    ['gold', 'trophy', 'REWARDS'], ['violet', 'star', 'EVENTS'], ['gold', 'coin', 'SHOP']].forEach(([color, icon, label], i) =>
    items.push(cellComp(s, `Card/example/${label}`, 3, 2, 30 + i * 70, sy + 30, r => card(r, color, icon, label, 0, 0, 3, 2))));
  [['gold', 'coin', 'FUNDS'], ['violet', 'star', 'SALE']].forEach(([color, icon, label], i) =>  // one row: icon beside the label
    items.push(cellComp(s, `Card/example/${label} 3x1`, 3, 1, 590 + i * 70, sy + 30, r => card(r, color, icon, label, 0, 0, 3, 1))));
  const py = sy + 110;
  items.push(caption(s, 'panels (backgrounds behind cards, slots and text)', 30, py));
  let x = 30;
  for (const style of ['well', 'night', 'stripes']) for (const [w, h] of [[9, 2], [9, 3], [4, 3], [5, 3]]) {
    items.push(cellComp(s, `Panel/${style}/${w}x${h}`, w, h, x, py + 30 + ['well', 'night', 'stripes'].indexOf(style) * 80, r => panel(r, style, 0, 0, w, h)));
    x += CELL * w + 20;
    if (h === 3 && w === 5) x = 30;
  }
  finish(s, items);
}

// ---------------- icons and the font (for hand-made labels: place glyph instances 1 px apart) ----------------
function buildGlyphs() {
  const s = section('glyphs'), items = [];
  items.push(caption(s, 'icons 16x16 (place at +1,+1 inside a cell)', 30, 70));
  Object.keys(ICONS).forEach((name, i) => items.push(comp(s, `Icon/${name}`, 16, 16, 30 + i * 30, 100, r => drawIcon(r, name, 0, 0))));
  items.push(caption(s, 'font 7 px (cream + shadow, 1 px letter spacing)', 30, 150));
  Object.keys(FONT).filter(ch => ch !== ' ').forEach((ch, i) => {
    const g = glyph(ch);
    items.push(comp(s, `Font/${ch}`, g[0].length + 1, 8, 30 + (i % 15) * 18, 180 + Math.floor(i / 15) * 22, r => drawText(r, ch, 0, 0, C.cream, C.O)));
  });
  finish(s, items);
}

const BUILD = { frames: buildFrames, buttons: buildButtons, controls: buildControls, cards: buildCards, glyphs: buildGlyphs };
for (const key of RUN) {
  for (const old of page.children.filter(n => n.type === 'SECTION' && n.name === PARTS[key][0])) old.remove();
  BUILD[key]();
}
return { pageId: page.id, parts: RUN, sections: page.children.filter(n => n.type === 'SECTION').map(n => ({ id: n.id, name: n.name, w: n.width, h: n.height })), ...stats };
