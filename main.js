(function () {
  "use strict";

  /* Demian Soria Vicente — main.js · vanilla, sin dependencias */

  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (sel, scope) => (scope || document).querySelector(sel);
  const $$ = (sel, scope) => Array.from((scope || document).querySelectorAll(sel));

  function safe(fn, name) {
    try { fn(); } catch (e) { console.warn("[" + name + "]", e); }
  }

  /* ----------------------------------------------------------
     1. Tema claro / oscuro (se recuerda en localStorage)
     ---------------------------------------------------------- */
  function initTheme() {
    const btn = $("[data-theme-toggle]");
    if (!btn) return;
    const root = document.documentElement;
    const meta = $('meta[name="theme-color"]');
    const apply = (theme) => {
      root.dataset.theme = theme;
      if (meta) meta.setAttribute("content", theme === "light" ? "#f6f8fb" : "#0a0e14");
      btn.setAttribute("aria-pressed", String(theme === "light"));
    };
    apply(root.dataset.theme === "light" ? "light" : "dark");
    btn.addEventListener("click", () => {
      const next = root.dataset.theme === "light" ? "dark" : "light";
      apply(next);
      try { localStorage.setItem("theme", next); } catch (e) { /* sin almacenamiento */ }
    });
  }

  /* ----------------------------------------------------------
     2. Línea mecanografiada del hero
     ---------------------------------------------------------- */
  function initTyped() {
    const el = $("[data-typed]");
    if (!el || reduced) return;
    let words;
    try { words = JSON.parse(el.dataset.words || "[]"); } catch (e) { return; }
    if (!Array.isArray(words) || words.length < 2) return;

    let w = 0;
    let i = words[0].length;
    let deleting = false;
    el.setAttribute("aria-hidden", "true");
    const line = el.parentElement;
    if (line) line.setAttribute("aria-label", words.join(", "));

    function tick() {
      const word = words[w];
      el.textContent = word.slice(0, i);
      let delay = deleting ? 35 : 70;
      if (!deleting && i === word.length) {
        deleting = true;
        delay = 1700;
      } else if (deleting && i === 0) {
        deleting = false;
        w = (w + 1) % words.length;
        delay = 350;
      } else {
        i += deleting ? -1 : 1;
      }
      setTimeout(tick, delay);
    }
    setTimeout(tick, 1800);
  }

  /* ----------------------------------------------------------
     3. Revelado al hacer scroll
     ---------------------------------------------------------- */
  function initReveal() {
    const els = $$(".reveal");
    if (!els.length) return;
    if (reduced || typeof IntersectionObserver === "undefined") {
      els.forEach((el) => el.classList.add("in"));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -4% 0px" });
    els.forEach((el) => io.observe(el));
    /* Red de seguridad: si el observer no dispara, se muestra todo */
    setTimeout(() => els.forEach((el) => el.classList.add("in")), 5000);
  }

  /* ----------------------------------------------------------
     4. Sección activa en la navegación
     ---------------------------------------------------------- */
  function initNavSpy() {
    if (typeof IntersectionObserver === "undefined") return;
    const links = $$('.nav-links a[href^="#"]');
    const map = new Map();
    links.forEach((a) => {
      const sec = $(a.getAttribute("href"));
      if (sec) map.set(sec, a);
    });
    if (!map.size) return;
    const hero = $(".hero");
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        const a = map.get(e.target);
        if (!a && e.target !== hero) return;
        links.forEach((l) => l.removeAttribute("aria-current"));
        if (a) a.setAttribute("aria-current", "true");
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    map.forEach((_, sec) => io.observe(sec));
    if (hero) io.observe(hero);
  }

  /* ----------------------------------------------------------
     5. Copiar correo
     ---------------------------------------------------------- */
  function initCopy() {
    $$("[data-copy]").forEach((btn) => {
      const label = btn.textContent;
      btn.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(btn.dataset.copy);
          btn.textContent = btn.dataset.copied || "OK";
          setTimeout(() => { btn.textContent = label; }, 1800);
        } catch (e) {
          btn.style.display = "none";
        }
      });
    });
  }

  /* ----------------------------------------------------------
     6. Formulario de contacto (mailto, sin servicios externos)
     ---------------------------------------------------------- */
  function initForm() {
    const form = $("#contact-form");
    if (!form) return;
    const d = form.dataset;
    const status = $("[data-status]", form);
    const fields = {
      name: $("#f-name", form),
      email: $("#f-email", form),
      msg: $("#f-msg", form),
    };
    const trap = $("#f-web", form);

    const setErr = (key, text) => {
      const out = $('[data-err="' + key + '"]', form);
      if (out) out.textContent = text || "";
      if (text) fields[key].setAttribute("aria-invalid", "true");
      else fields[key].removeAttribute("aria-invalid");
    };

    const validate = () => {
      let first = null;
      const name = fields.name.value.trim();
      const email = fields.email.value.trim();
      const msg = fields.msg.value.trim();
      const okEmail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email);

      setErr("name", name ? "" : d.eName);
      setErr("email", okEmail ? "" : d.eEmail);
      setErr("msg", msg.length >= 10 ? "" : d.eMsg);
      if (!name) first = fields.name;
      else if (!okEmail) first = fields.email;
      else if (msg.length < 10) first = fields.msg;
      return first ? { first } : { name, email, msg };
    };

    Object.keys(fields).forEach((key) => {
      fields[key].addEventListener("input", () => setErr(key, ""));
    });

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (trap && trap.value) return; /* antispam: campo trampa relleno */
      const res = validate();
      if (res.first) {
        res.first.focus();
        if (status) status.textContent = "";
        return;
      }
      const body =
        d.labelName + ": " + res.name + "\r\n" +
        d.labelEmail + ": " + res.email + "\r\n\r\n" +
        res.msg;
      const href = "mailto:" + d.to +
        "?subject=" + encodeURIComponent(d.subject + " — " + res.name) +
        "&body=" + encodeURIComponent(body);
      if (status) {
        status.textContent = d.ok + " " + d.copyHint + " " + d.to + ".";
      }
      window.location.href = href;
    });
  }

  /* ----------------------------------------------------------
     Boot
     ---------------------------------------------------------- */
  function boot() {
    safe(initTheme, "initTheme");
    safe(initTyped, "initTyped");
    safe(initReveal, "initReveal");
    safe(initNavSpy, "initNavSpy");
    safe(initCopy, "initCopy");
    safe(initForm, "initForm");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
