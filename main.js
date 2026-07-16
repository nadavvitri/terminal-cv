/*
  main.js — a tiny typing animation for any element marked data-typed.
  In index.html the <h1 class="name" data-typed>Nadav Vitri</h1> uses this:
  the text is "typed out" one character at a time when the page loads.
*/

(function () {
  // Find every element that opted in with the data-typed attribute.
  const targets = document.querySelectorAll('[data-typed]');

  targets.forEach((el) => {
    const fullText = el.textContent;   // remember the final text
    el.textContent = '';               // clear it so we can type it back in
    let i = 0;

    // Add one character every 90ms until the whole string is shown.
    const timer = setInterval(() => {
      el.textContent += fullText[i];
      i++;
      if (i >= fullText.length) {
        clearInterval(timer);          // stop when done
      }
    }, 90);
  });
})();
