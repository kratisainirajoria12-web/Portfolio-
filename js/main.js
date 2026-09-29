/* Krati — portfolio interactions
   Everything here is progressive enhancement: without JS the page is fully
   readable, and with `prefers-reduced-motion` the scenes stay still. */
(() => {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const ramp = (p, start, end) => clamp((p - start) / (end - start));
  const ease = (t) => 1 - Math.pow(1 - t, 3);

  document.querySelectorAll("[data-year]").forEach((el) => (el.textContent = new Date().getFullYear()));

  /* ---------- Nav state ---------- */
  const nav = document.getElementById("nav");
  const onNavScroll = () => nav && nav.classList.toggle("is-scrolled", window.scrollY > 24);
  onNavScroll();
  window.addEventListener("scroll", onNavScroll, { passive: true });

  const navLinks = [...document.querySelectorAll('.nav-links a[href^="#"], .toc a[href^="#"]')];
  const sections = navLinks.map((a) => document.querySelector(a.getAttribute("href"))).filter(Boolean);
  if ("IntersectionObserver" in window && sections.length) {
    const spy = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (!e.isIntersecting) return;
          navLinks.forEach((a) =>
            a.getAttribute("href") === "#" + e.target.id ? a.setAttribute("aria-current", "true") : a.removeAttribute("aria-current")
          );
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    sections.forEach((s) => spy.observe(s));
  }

  /* ---------- Reveal on scroll ---------- */
  const reveals = document.querySelectorAll(".reveal");
  if (reduceMotion || !("IntersectionObserver" in window)) {
    reveals.forEach((el) => el.classList.add("is-in"));
  } else {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("is-in");
            io.unobserve(e.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );
    reveals.forEach((el) => io.observe(el));
  }

  /* ---------- Hero: scroll camera + gentle pointer parallax ---------- */
  const hero = document.querySelector(".hero");
  const camera = document.querySelector("[data-camera]");
  if (hero && camera && !reduceMotion) {
    const layers = [...camera.querySelectorAll("[data-depth]")].map((el) => ({ el, d: parseFloat(el.dataset.depth) }));
    const finePointer = window.matchMedia("(pointer: fine)").matches;
    let tx = 0, ty = 0, cx = 0, cy = 0, heroVisible = true, raf = 0;

    if (finePointer) {
      window.addEventListener("pointermove", (e) => {
        tx = (e.clientX / window.innerWidth) * 2 - 1;
        ty = (e.clientY / window.innerHeight) * 2 - 1;
      }, { passive: true });
    }

    const frame = () => {
      raf = 0;
      cx += (tx - cx) * 0.06;
      cy += (ty - cy) * 0.06;
      const p = clamp(window.scrollY / hero.offsetHeight);
      camera.style.transform = `translate3d(0, ${p * 60}px, 0) scale(${1 + p * 0.08})`;
      layers.forEach(({ el, d }) => {
        el.style.transform = `translate3d(${cx * d * -14}px, ${cy * d * -10 - p * d * 90}px, 0)`;
      });
      if (heroVisible && (Math.abs(tx - cx) > 0.001 || Math.abs(ty - cy) > 0.001)) tick();
    };
    const tick = () => { if (!raf) raf = requestAnimationFrame(frame); };

    new IntersectionObserver(([e]) => { heroVisible = e.isIntersecting; if (heroVisible) tick(); }).observe(hero);
    window.addEventListener("scroll", () => heroVisible && tick(), { passive: true });
    window.addEventListener("pointermove", () => heroVisible && tick(), { passive: true });
    tick();
  }

  /* ---------- About: desk list <-> studio objects ---------- */
  document.querySelectorAll(".desk-list button").forEach((btn) => {
    const target = document.querySelector(`[data-obj="${btn.dataset.target}"]`);
    if (!target) return;
    const on = () => target.classList.add("is-lit");
    const off = () => target.classList.remove("is-lit");
    btn.addEventListener("mouseenter", on);
    btn.addEventListener("mouseleave", off);
    btn.addEventListener("focus", on);
    btn.addEventListener("blur", off);
  });

  /* ---------- Approach: steps drive the clay lump ---------- */
  const lump = document.querySelector(".scene--lump");
  const steps = document.querySelectorAll(".step");
  if (lump && steps.length && "IntersectionObserver" in window) {
    const setStep = (n) => {
      lump.dataset.step = n;
      steps.forEach((s) => s.classList.toggle("is-active", s.dataset.step === n));
    };
    setStep("1");
    const so = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && setStep(e.target.dataset.step)),
      { rootMargin: "-48% 0px -48% 0px" }
    );
    steps.forEach((s) => so.observe(s));
  } else {
    steps.forEach((s) => s.classList.add("is-active"));
  }

  /* ---------- Contact: the closing scene ---------- */
  const closing = document.querySelector("[data-closing]");
  if (closing) {
    const cinematic = window.matchMedia("(min-width: 881px)");
    const caps = [...closing.querySelectorAll("[data-cap]")];
    let raf = 0;

    const render = () => {
      raf = 0;
      const rect = closing.getBoundingClientRect();
      const span = closing.offsetHeight - window.innerHeight;
      const p = clamp(-rect.top / span);

      const lid = ease(ramp(p, 0.04, 0.24));
      const dark = ease(ramp(p, 0.2, 0.45));
      const walk = ease(ramp(p, 0.4, 0.78));
      const pan = ease(ramp(p, 0.42, 0.72));
      const cta = ease(ramp(p, 0.72, 0.9));
      const moving = walk > 0 && walk < 1;
      const bob = moving ? Math.sin(walk * Math.PI * 7) * -0.8 : 0;

      const s = closing.style;
      s.setProperty("--lid", lid.toFixed(3));
      s.setProperty("--dark", dark.toFixed(3));
      s.setProperty("--walk", walk.toFixed(3));
      s.setProperty("--pan", pan.toFixed(3));
      s.setProperty("--cta", cta.toFixed(3));
      s.setProperty("--bob", bob.toFixed(3));
      closing.classList.toggle("is-dark", dark > 0.5);
      if (nav) nav.classList.toggle("is-dark", dark > 0.5 && rect.top < 60);

      const active = p < 0.02 ? -1 : p < 0.22 ? 0 : p < 0.42 ? 1 : p < 0.72 ? 2 : -1;
      caps.forEach((c, i) => c.classList.toggle("is-on", i === active));
    };
    const tick = () => { if (!raf) raf = requestAnimationFrame(render); };

    const setup = () => {
      const staticMode = reduceMotion || !cinematic.matches;
      closing.classList.toggle("is-static", staticMode);
      if (staticMode) {
        ["--lid", "--dark", "--walk", "--pan", "--cta", "--bob"].forEach((v) => closing.style.removeProperty(v));
        window.removeEventListener("scroll", tick);
      } else {
        window.addEventListener("scroll", tick, { passive: true });
        tick();
      }
    };
    cinematic.addEventListener("change", setup);
    window.addEventListener("resize", tick);
    setup();
  }
})();
