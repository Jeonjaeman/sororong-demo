// 영상 프레임 스크롤 (이미지 시퀀스 → canvas, cover 맞춤)
// 사용: new FrameScrub(canvas, { dir, count, ext:'webp', pad:3 }) 뒤 scrub.seek(0~1)
class FrameScrub {
  constructor(canvas, opt) {
    this.c = canvas; this.ctx = canvas.getContext('2d', { alpha: false });
    this.dir = opt.dir; this.count = opt.count; this.ext = opt.ext || 'webp'; this.pad = opt.pad || 3;
    this.frames = new Array(this.count); this.loaded = 0; this.cur = -1; this.pos = 0;
    this.onProgress = opt.onProgress || function () {};
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.resize(); addEventListener('resize', () => { this.resize(); this.draw(true); });
    this.load();
  }
  src(i) { return this.dir + '/' + String(i + 1).padStart(this.pad, '0') + '.' + this.ext; }
  load() {
    // 첫 프레임 먼저, 이어서 띄엄띄엄 → 나머지 (초기 표시 빠르게)
    var order = [0]; var step = 8;
    for (var s = step; s >= 1; s = s >> 1) for (var i = 0; i < this.count; i += s) if (order.indexOf(i) < 0) order.push(i);
    var self = this, k = 0, par = 6;
    function next() {
      if (k >= order.length) return;
      var i = order[k++]; var im = new Image();
      im.onload = im.onerror = function () { self.frames[i] = im; self.loaded++; self.onProgress(self.loaded / self.count); if (i === 0 || Math.abs(i - self.cur) < 2) self.draw(true); next(); };
      im.src = self.src(i);
    }
    for (var p = 0; p < par; p++) next();
  }
  resize() {
    var r = this.c.getBoundingClientRect();
    this.w = Math.max(1, Math.round(r.width * this.dpr)); this.h = Math.max(1, Math.round(r.height * this.dpr));
    this.c.width = this.w; this.c.height = this.h;
  }
  nearest(i) { // 아직 안 온 프레임이면 가까운 로드된 프레임
    if (this.frames[i]) return this.frames[i];
    for (var d = 1; d < this.count; d++) { if (this.frames[i - d]) return this.frames[i - d]; if (this.frames[i + d]) return this.frames[i + d]; }
    return null;
  }
  seek(t) { this.pos = Math.min(1, Math.max(0, t)); this.draw(); }
  draw(force) {
    var i = Math.round(this.pos * (this.count - 1));
    if (!force && i === this.cur) return;
    var im = this.nearest(i); if (!im || !im.naturalWidth) return;
    this.cur = i;
    var cw = this.w, ch = this.h, iw = im.naturalWidth, ih = im.naturalHeight;
    var s = Math.max(cw / iw, ch / ih), dw = iw * s, dh = ih * s;
    this.ctx.drawImage(im, (cw - dw) / 2, (ch - dh) / 2, dw, dh);
  }
}
window.FrameScrub = FrameScrub;
