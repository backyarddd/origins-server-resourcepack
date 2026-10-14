// Figma (use_figma) script: compose the menus of SPEC on page "Menus". `python -I menus/build.py figma` prepends lib.js
// and SPEC = {width: preview section width, menus: the menus of this script, each with its fixed page place fy and px}.
// A big spec is split over several scripts; each one replaces only its own menus, so they can run alone or in any order.
// Frames of other menus are never touched (other branches draw on this page too): delete a dropped menu's frames by
// hand. The page-level 1x frames menu_<id> are the export sources (download_assets, png, scale 1 ->
// menus/export/menu_<id>.png); they sit over the page background #E5E5E5, which
// build.py keys out, so slot holes and the chamfer corners export transparent. Section "Menus preview" shows each menu
// at 4x above an approximate player inventory, with the title where the game draws it (Inter stands in for the
// Minecraft font there).
await figma.loadFontAsync({ family: 'Inter', style: 'Bold' });
const page = await usePage('Menus');
const mine = new Set(SPEC.menus.map(m => m.id));
for (const old of page.children.filter(n => n.name.startsWith('menu_') && mine.has(n.name.slice(5)))) old.remove();
let sec = page.children.find(n => n.type === 'SECTION' && n.name === 'Menus preview');
if (!sec) { sec = figma.createSection(); sec.name = 'Menus preview'; sec.x = 0; sec.y = 0; }
// preview frames are named "<id> preview 4x", captions start with "<id>  ("
for (const old of sec.children.filter(n => mine.has(n.name.split(' ')[0]))) old.remove();
const exports = [], rects = {};
for (const m of SPEC.menus) {
  const h = menuHeight(m.rows), r = new Raster(W, h);
  drawMenu(r, m);
  const f = fframe(page, 'menu_' + m.id, -400, m.fy, W, h, null);
  rects[m.id] = r.emit(f);
  exports.push({ id: f.id, name: f.name, w: f.width, h: f.height });
}
for (const m of SPEC.menus) {
  const h = menuHeight(m.rows), r = new Raster(W, h + 96);
  drawMenu(r, m); inventoryMock(r, h);
  const f = fframe(sec, m.id + ' preview 4x', m.px, 90, W, h + 96, null);
  r.emit(f);
  ftext(f, m.title, 8, 5, 8, C.cream);
  ftext(f, 'Inventory', 8, h + 2, 8, C.cream);
  f.rescale(4);
  ftext(sec, m.id + '  (' + m.rows + ' rows, ' + (m.open_command ? '/' + m.open_command[0] : 'opened from another menu') + ')', m.px, 40, 22, 'FFFFFF');
}
sec.resizeWithoutConstraints(Math.max(sec.width, SPEC.width), 90 + (menuHeight(6) + 96) * 4 + 60);
sec.fills = [{ type: 'SOLID', color: hex('202020') }];
return { pageId: page.id, sectionId: sec.id, exports, rects };
