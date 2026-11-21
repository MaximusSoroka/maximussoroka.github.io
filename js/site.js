/* Desire Agency — motion & interactivity. Vanilla JS, no dependencies, no network requests.
   Numbers are never invented: count-ups animate towards the value already written in the HTML. */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var lang = (root.getAttribute("lang") || "en").slice(0, 2);
  var T = lang === "de"
    ? { copied: "Link kopiert", copyFail: "Kopieren nicht möglich", shown: "{n} von {t} Tools", light: "Helles Design", dark: "Dunkles Design" }
    : { copied: "Link copied", copyFail: "Could not copy", shown: "{n} of {t} tools", light: "Light theme", dark: "Dark theme" };
  function $all(sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); }

  /* ---------- Theme toggle (stored locally only, no cookies) ---------- */
  function currentTheme() {
    var t = root.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  $all(".theme-toggle").forEach(function (btn) {
    function label() { btn.setAttribute("aria-label", currentTheme() === "dark" ? T.light : T.dark); btn.title = btn.getAttribute("aria-label"); }
    label();
    btn.addEventListener("click", function (ev) {
      var next = currentTheme() === "dark" ? "light" : "dark";
      function apply() {
        root.setAttribute("data-theme", next);
        try { localStorage.setItem("theme", next); } catch (e) {}
        label();
      }
      if (!reduce && doc.startViewTransition) {
        var r = btn.getBoundingClientRect();
        var x = r.left + r.width / 2, y = r.top + r.height / 2;
        var end = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
        var vt = doc.startViewTransition(apply);
        vt.ready.then(function () {
          root.animate({ clipPath: ["circle(0px at " + x + "px " + y + "px)", "circle(" + end + "px at " + x + "px " + y + "px)"] },
            { duration: 550, easing: "cubic-bezier(.4,0,.2,1)", pseudoElement: "::view-transition-new(root)" });
        }).catch(function () {});
      } else if (!reduce) {
        root.classList.add("theme-anim"); apply();
        setTimeout(function () { root.classList.remove("theme-anim"); }, 500);
      } else { apply(); }
    });
  });

  /* ---------- Header shadow + reading progress ---------- */
  var header = doc.querySelector(".site-header");
  var bar = doc.querySelector(".progress");
  var ticking = false;
  function onScroll() {
    ticking = false;
    var y = window.scrollY || 0;
    if (header) header.classList.toggle("is-scrolled", y > 8);
    if (bar) {
      var h = doc.documentElement.scrollHeight - innerHeight;
      bar.style.transform = "scaleX(" + (h > 0 ? Math.min(1, y / h) : 0) + ")";
    }
  }
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* ---------- Count-up for existing numbers ---------- */
  var NUM = /([0-9]+(?:[.,][0-9]+)?)/;
  function zeroed(el) {
    var final = el.textContent, m = final.match(NUM);
    if (!m) return;
    var raw = m[1];
    if (parseFloat(raw.replace(",", ".")) === 0) return;
    el.dataset.final = final;
    el.textContent = final.slice(0, m.index) + raw.replace(/[0-9]/g, "0") .replace(/^0+(?=0)/, "") + final.slice(m.index + raw.length);
  }
  function countUp(el) {
    var final = el.dataset.final || el.textContent;
    var m = final.match(NUM);
    if (!m) return;
    var raw = m[1], sep = raw.indexOf(",") !== -1 ? "," : ".";
    var dec = raw.indexOf(sep) !== -1 && /[.,]/.test(raw) ? raw.split(/[.,]/)[1].length : 0;
    var target = parseFloat(raw.replace(",", "."));
    if (!isFinite(target) || target === 0) return; /* zeros stay zeros */
    var pre = final.slice(0, m.index), post = final.slice(m.index + raw.length);
    var row = el.closest(".ledger-row");
    var t0 = null, dur = 1100 + Math.min(700, target * 8);
    if (row) row.classList.add("is-counting");
    function frame(ts) {
      if (t0 === null) t0 = ts;
      var p = Math.min(1, (ts - t0) / dur);
      var e = 1 - Math.pow(1 - p, 3);
      var v = (target * e).toFixed(dec);
      el.textContent = pre + (sep === "," ? v.replace(".", ",") : v) + post;
      if (p < 1) requestAnimationFrame(frame);
      else { el.textContent = final; if (row) row.classList.remove("is-counting"); }
    }
    requestAnimationFrame(frame);
  }
  var counters = $all("[data-count]");

  /* ---------- Scroll reveal (staggered) ---------- */
  var revealSel = [".section-head", ".stats", ".panel", ".product", ".fact", ".team", ".faq details", ".cta-band",
    ".card", ".tpl-card", ".step", ".stack-item", ".case", "article > h2", ".table-wrap", ".placeholder-box"].join(",");
  var revealEls = $all(revealSel).filter(function (el) { return !el.closest(".home-hero"); });
  if (!reduce && "IntersectionObserver" in window) {
    var groups = new Map();
    revealEls.forEach(function (el) {
      var parent = el.parentElement;
      var i = groups.get(parent) || 0;
      groups.set(parent, i + 1);
      el.style.setProperty("--d", Math.min(i, 6) * 70 + "ms");
      el.classList.add("reveal");
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add("is-in");
        io.unobserve(en.target);
        setTimeout(function () { en.target.style.removeProperty("--d"); }, 1200);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { countUp(en.target); cio.unobserve(en.target); } });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { zeroed(el); cio.observe(el); });
  }

  /* ---------- Cursor-follow spotlight + hero glow ---------- */
  var fine = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (fine && !reduce) {
    $all(".product, .card, .fact, .panel, .stat, .tpl-card").forEach(function (el) {
      el.classList.add("spot");
      el.addEventListener("pointermove", function (e) {
        var r = el.getBoundingClientRect();
        el.style.setProperty("--mx", (e.clientX - r.left) + "px");
        el.style.setProperty("--my", (e.clientY - r.top) + "px");
      });
    });
    var hero = doc.querySelector(".home-hero");
    if (hero) {
      var glow = doc.createElement("div");
      glow.className = "hero-glow"; glow.setAttribute("aria-hidden", "true");
      hero.appendChild(glow);
      hero.addEventListener("pointermove", function (e) {
        var r = hero.getBoundingClientRect();
        glow.style.setProperty("--gx", (e.clientX - r.left) + "px");
        glow.style.setProperty("--gy", (e.clientY - r.top) + "px");
      });
    }
  }

  /* ---------- Team diagram ---------- */
  var team = doc.querySelector(".team");
  if (team) {
    var agents = $all(".agent", team);
    var detail = team.querySelector(".team-detail");
    var svg = team.querySelector(".team-lines");
    var lead = team.querySelector(".agent.is-lead:not(.is-human)");
    var human = team.querySelector(".agent.is-human");
    var paths = [];
    function draw() {
      if (!svg || !lead || getComputedStyle(svg).display === "none") return;
      var tr = team.getBoundingClientRect();
      svg.setAttribute("viewBox", "0 0 " + tr.width + " " + tr.height);
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      paths = [];
      var lr = lead.getBoundingClientRect();
      var cx = lr.left + lr.width / 2 - tr.left, cy = lr.top + lr.height / 2 - tr.top;
      agents.forEach(function (a) {
        if (a === lead || a.classList.contains("is-human")) return;
        var r = a.getBoundingClientRect();
        var left = r.left + r.width / 2 - tr.left < cx;
        var x = left ? r.right - tr.left : r.left - tr.left, y = r.top + r.height / 2 - tr.top;
        var sx = left ? lr.left - tr.left : lr.right - tr.left;
        var mx = (x + sx) / 2;
        var p = doc.createElementNS("http://www.w3.org/2000/svg", "path");
        p.setAttribute("d", "M" + sx + " " + cy + " C" + mx + " " + cy + " " + mx + " " + y + " " + x + " " + y);
        p.dataset.id = a.dataset.id;
        svg.appendChild(p);
        paths.push(p);
      });
      if (human) {
        var hr = human.getBoundingClientRect();
        var hp = doc.createElementNS("http://www.w3.org/2000/svg", "path");
        var hx = hr.left + hr.width / 2 - tr.left;
        hp.setAttribute("d", "M" + hx + " " + (hr.bottom - tr.top) + " L" + hx + " " + (lr.top - tr.top));
        hp.dataset.id = human.dataset.id;
        svg.appendChild(hp); paths.push(hp);
      }
      mark(team.querySelector('.agent[aria-pressed="true"]'));
    }
    function mark(a) {
      paths.forEach(function (p) { p.classList.toggle("is-on", !!a && (p.dataset.id === a.dataset.id || a === lead)); });
    }
    var home = detail ? detail.parentNode : null, homeNext = detail ? detail.nextSibling : null;
    var narrow = window.matchMedia("(max-width: 980px)");
    function place(a) {
      if (!detail) return;
      if (narrow.matches && a && !a.classList.contains("is-lead")) { a.insertAdjacentElement("afterend", detail); }
      else if (detail.parentNode !== home) { home.insertBefore(detail, homeNext); }
    }
    function select(a, focus) {
      place(a);
      agents.forEach(function (x) { x.setAttribute("aria-pressed", x === a ? "true" : "false"); });
      if (detail) {
        detail.innerHTML = "";
        var g = doc.createElement("div"); g.className = "grp"; g.textContent = a.dataset.group || "";
        var w = doc.createElement("div"); w.className = "who"; w.textContent = a.dataset.name || "";
        var p = doc.createElement("p"); p.textContent = a.dataset.role || "";
        detail.appendChild(g); detail.appendChild(w); detail.appendChild(p);
        if (!reduce) { detail.classList.remove("flash"); void detail.offsetWidth; detail.classList.add("flash"); }
      }
      mark(a);
    }
    agents.forEach(function (a) {
      a.addEventListener("click", function () { select(a); });
      if (fine) a.addEventListener("mouseenter", function () { select(a); });
      a.addEventListener("focus", function () { select(a); });
    });
    if (lead) select(lead);
    draw();
    var rt; window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(function () { place(team.querySelector('.agent[aria-pressed="true"]')); draw(); }, 120); });
    if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(draw);
    setTimeout(draw, 900);
  }

  /* ---------- FAQ: smooth open/close ---------- */
  $all(".faq details").forEach(function (d) {
    var s = d.querySelector("summary"), body = d.querySelector(".faq-a");
    if (!s || !body || reduce || !d.animate) return;
    s.addEventListener("click", function (e) {
      e.preventDefault();
      if (d.classList.contains("is-animating")) return;
      d.classList.add("is-animating");
      var start = d.offsetHeight;
      if (d.open) {
        var endH = s.offsetHeight + 2;
        var a = d.animate({ height: [start + "px", endH + "px"] }, { duration: 260, easing: "ease" });
        a.onfinish = function () { d.open = false; d.classList.remove("is-animating"); };
      } else {
        d.open = true;
        var end = d.offsetHeight;
        var b = d.animate({ height: [start + "px", end + "px"] }, { duration: 300, easing: "ease" });
        b.onfinish = function () { d.classList.remove("is-animating"); };
      }
    });
  });

  /* ---------- Copy to clipboard ---------- */
  var toast;
  function say(msg) {
    if (!toast) { toast = doc.createElement("div"); toast.className = "toast"; toast.setAttribute("role", "status"); doc.body.appendChild(toast); }
    toast.textContent = msg; toast.classList.add("show");
    clearTimeout(toast._t); toast._t = setTimeout(function () { toast.classList.remove("show"); }, 1800);
  }
  $all("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = new URL(btn.getAttribute("data-copy"), location.href).href;
      var done = function () { btn.classList.add("is-done"); say(T.copied); setTimeout(function () { btn.classList.remove("is-done"); }, 1600); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { say(T.copyFail); });
      } else {
        var ta = doc.createElement("textarea"); ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
        doc.body.appendChild(ta); ta.select();
        try { doc.execCommand("copy"); done(); } catch (e) { say(T.copyFail); }
        doc.body.removeChild(ta);
      }
    });
  });

  /* ---------- Directory: live count, "/" shortcut, pop-in ---------- */
  var grid = doc.getElementById("tool-grid"), search = doc.getElementById("tool-search");
  if (grid && search) {
    var cards = $all(".card", grid), out = doc.createElement("p");
    out.className = "result-count"; out.setAttribute("aria-live", "polite");
    grid.parentNode.insertBefore(out, grid);
    function count() {
      var n = cards.filter(function (c) { return !c.hidden; }).length;
      out.textContent = T.shown.replace("{n}", n).replace("{t}", cards.length);
    }
    function refresh() {
      setTimeout(function () {
        count();
        if (!reduce) cards.forEach(function (c) { if (!c.hidden) { c.classList.remove("pop"); void c.offsetWidth; c.classList.add("pop", "is-in"); } });
      }, 0);
    }
    search.addEventListener("input", refresh);
    $all(".chip").forEach(function (c) { c.addEventListener("click", refresh); });
    doc.addEventListener("keydown", function (e) {
      if (e.key === "/" && doc.activeElement !== search && !/input|textarea/i.test(doc.activeElement.tagName)) { e.preventDefault(); search.focus(); }
      if (e.key === "Escape" && doc.activeElement === search) { search.value = ""; search.dispatchEvent(new Event("input")); }
    });
    count();
  }
})();
