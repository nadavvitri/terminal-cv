/*
  matrix.js — draws the falling "digital rain" on the <canvas id="matrix">.
  This is the only real algorithm on the page, and it's short. Read top-down.

  How it works, in plain English:
    1. Make the canvas fill the window.
    2. Split the screen into vertical columns, each one character wide.
    3. Each column has a "drop" = the Y position of the leading character.
    4. ~30 times per second: paint a translucent black rectangle over the whole
       canvas (this fades old characters), then draw one new green character at
       the bottom of every column and move each drop down by one.
    5. When a drop goes off the bottom, randomly reset it to the top so the
       streams have varied lengths.
*/

(function () {
  const canvas = document.getElementById('matrix');
  const ctx = canvas.getContext('2d'); // the 2D drawing API

  // Characters to rain down (katakana + digits gives the classic Matrix look).
  const glyphs = 'ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄ0123456789'.split('');
  const fontSize = 16;
  let columns, drops;

  // Recompute grid whenever the window size changes.
  function setup() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    columns = Math.floor(canvas.width / fontSize);
    // Start every column at a random height so they don't fall in sync.
    drops = new Array(columns).fill(0).map(() => Math.random() * -100);
  }

  function draw() {
    // Translucent black overlay: fades the previous frame instead of clearing it,
    // which creates the glowing trailing-tail effect.
    ctx.fillStyle = 'rgba(13, 17, 23, 0.08)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#00ff41';        // matrix green
    ctx.font = fontSize + 'px monospace';

    for (let i = 0; i < drops.length; i++) {
      const char = glyphs[Math.floor(Math.random() * glyphs.length)];
      const x = i * fontSize;
      const y = drops[i] * fontSize;
      ctx.fillText(char, x, y);

      // Once a drop passes the bottom, randomly send it back to the top.
      if (y > canvas.height && Math.random() > 0.975) {
        drops[i] = 0;
      }
      drops[i]++;
    }
  }

  setup();
  window.addEventListener('resize', setup);

  // ~30 fps is plenty and keeps CPU/battery use low.
  setInterval(draw, 33);
})();
