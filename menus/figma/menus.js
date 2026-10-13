// Figma (use_figma) script: compose every menu of SPEC (menus/spec.json, prepended with lib.js by
// `python -I menus/build.py figma`) on page "Menus". The page-level 1x frames menu_<id> are the export sources
// (download_assets, png, scale 1 -> menus/export/menu_<id>.png); they sit over the page background #E5E5E5, which
// build.py keys out, so slot holes and the chamfer corners export transparent. Section "Menus preview" shows each menu
// at 4x above an approximate player inventory, with the title where the game draws it (Inter stands in for the
// Minecraft font there).
await figma.loadFontAsync({ family: 'Inter', style: 'Bold' });
const page = await usePage('Menus');
for (const old of page.children.filter(n => n.name.startsWith('menu_') || (n.type === 'SECTION' && n.name === 'Menus preview'))) old.remove();
const exports = [], rects = {};
let y = 0;
for (const m of SPEC.menus) {
  const h = menuHeight(m.rows), r = new Raster(W, h);
  drawMenu(r, m);
  const f = fframe(page, 'menu_' + m.id, -400, y, W, h, null);
  rects[m.id] = r.emit(f);
  exports.push({ id: f.id, name: f.name, w: f.width, h: f.height });
  y += h + 40;
}
const sec = figma.createSection(); sec.name = 'Menus preview'; sec.x = 0; sec.y = 0;
let px = 40;
for (const m of SPEC.menus) {
  const h = menuHeight(m.rows), r = new Raster(W, h + 96);
  drawMenu(r, m); inventoryMock(r, h);
  const f = fframe(sec, m.id + ' preview 4x', px, 90, W, h + 96, null);
  r.emit(f);
  ftext(f, m.title, 8, 5, 8, C.cream);
  ftext(f, 'Inventory', 8, h + 2, 8, C.cream);
  f.rescale(4);
  ftext(sec, m.id + '  (' + m.rows + ' rows, ' + (m.open_command ? '/' + m.open_command[0] : 'opened from another menu') + ')', px, 40, 22, 'FFFFFF');
  px += W * 4 + 80;
}
sec.resizeWithoutConstraints(px, 90 + (menuHeight(6) + 96) * 4 + 60);
sec.fills = [{ type: 'SOLID', color: hex('202020') }];
return { pageId: page.id, sectionId: sec.id, exports, rects };
