// 首页轮播头图：自动轮播、左右按钮、圆点、触屏滑动、键盘左右键。
// 鼠标悬停或键盘焦点在轮播上时暂停；系统开启「减少动态效果」时不自动轮播。
(function () {
  "use strict";

  window.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".carousel").forEach(setup);
  });

  function setup(root) {
    const slides = [...root.querySelectorAll(".carousel-slide")];
    const dots = [...root.querySelectorAll(".carousel-dot")];
    if (slides.length < 2) return;

    const interval = parseInt(root.dataset.interval, 10) || 5000;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let index = 0;
    let timer = null;

    function show(i) {
      index = (i + slides.length) % slides.length;
      slides.forEach((s, k) => {
        const active = k === index;
        s.classList.toggle("is-active", active);
        s.setAttribute("aria-hidden", active ? "false" : "true");
        const link = s.querySelector("a");
        if (link) link.tabIndex = active ? 0 : -1;
        // 懒加载的图片提前开始加载下一张
        if (k === (index + 1) % slides.length) {
          const img = s.querySelector("img[loading=lazy]");
          if (img) img.loading = "eager";
        }
      });
      dots.forEach((d, k) => {
        d.classList.toggle("is-active", k === index);
        d.setAttribute("aria-selected", k === index ? "true" : "false");
      });
    }

    function start() {
      if (reduceMotion || timer) return;
      timer = setInterval(() => show(index + 1), interval);
    }
    function stop() {
      clearInterval(timer);
      timer = null;
    }
    // 手动切换后重新计时，避免刚点完就自动跳走
    function go(i) {
      stop();
      show(i);
      if (!root.matches(":hover") && !root.contains(document.activeElement)) start();
    }

    root.querySelector(".carousel-prev").addEventListener("click", () => go(index - 1));
    root.querySelector(".carousel-next").addEventListener("click", () => go(index + 1));
    dots.forEach((d, k) => d.addEventListener("click", () => go(k)));

    root.addEventListener("mouseenter", stop);
    root.addEventListener("mouseleave", start);
    root.addEventListener("focusin", stop);
    root.addEventListener("focusout", (e) => {
      if (!root.contains(e.relatedTarget)) start();
    });
    root.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") go(index - 1);
      if (e.key === "ArrowRight") go(index + 1);
    });

    // 触屏左右滑动
    let x0 = null;
    root.addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; stop(); }, { passive: true });
    root.addEventListener("touchend", (e) => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0;
      x0 = null;
      if (Math.abs(dx) > 40) go(dx < 0 ? index + 1 : index - 1);
      else start();
    });

    // 页面切到后台时暂停
    document.addEventListener("visibilitychange", () => (document.hidden ? stop() : start()));

    start();
  }
})();
