// 展馆页（layouts/_default/museum.html）的分类 / 年份筛选。
// 筛选状态写在网址 # 后面：#book、#2025、#book-2025，可以直接分享。
(function () {
  "use strict";

  window.addEventListener("DOMContentLoaded", () => {
    const root = document.querySelector("[data-museum]");
    if (!root) return;
    const catBtns = root.querySelectorAll(".museum-cats button");
    const yearBtns = root.querySelectorAll(".museum-years button");
    const sections = root.querySelectorAll(".museum-year");
    const empty = root.querySelector(".museum-empty");
    let cat = "all";
    let year = "all";

    function readHash() {
      cat = "all";
      year = "all";
      decodeURIComponent(location.hash.slice(1)).split("-").forEach((part) => {
        if (/^\d{4}$/.test(part) && root.querySelector(`button[data-year="${part}"]`)) year = part;
        else if (part && root.querySelector(`button[data-cat="${part}"]`)) cat = part;
      });
    }

    function apply() {
      catBtns.forEach((b) => {
        const on = b.dataset.cat === cat;
        b.classList.toggle("active", on);
        b.setAttribute("aria-pressed", on);
      });
      yearBtns.forEach((b) => {
        const on = b.dataset.year === year;
        b.classList.toggle("active", on);
        b.setAttribute("aria-pressed", on);
      });
      let shown = 0;
      sections.forEach((sec) => {
        let n = 0;
        if (year === "all" || sec.dataset.year === year) {
          sec.querySelectorAll(".museum-item").forEach((it) => {
            const ok = cat === "all" || it.dataset.cat === cat;
            it.hidden = !ok;
            if (ok) n++;
          });
        }
        sec.hidden = n === 0;
        sec.querySelector(".museum-year-count").textContent = n;
        shown += n;
      });
      if (empty) empty.hidden = shown > 0;
    }

    function update() {
      const parts = [cat, year].filter((v) => v !== "all");
      history.replaceState(null, "", parts.length ? "#" + parts.join("-") : location.pathname);
      apply();
    }

    catBtns.forEach((b) => b.addEventListener("click", () => { cat = b.dataset.cat; update(); }));
    yearBtns.forEach((b) => b.addEventListener("click", () => { year = b.dataset.year; update(); }));
    window.addEventListener("hashchange", () => { readHash(); apply(); });
    readHash();
    apply();
  });
})();
