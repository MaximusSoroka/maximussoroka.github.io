(function () {
  var cfg = window.SITE_CONFIG || {};
  var n8n = (cfg.N8N_AFFILIATE_URL || "").trim();
  var make = (cfg.MAKE_AFFILIATE_URL || "").trim();
  var n8nOfficial = cfg.N8N_OFFICIAL_URL || "https://n8n.io/";
  var makeOfficial = cfg.MAKE_OFFICIAL_URL || "https://www.make.com/";

  if (cfg.NOINDEX !== false) {
    var robots = document.querySelector('meta[name="robots"]');
    if (!robots) {
      robots = document.createElement("meta");
      robots.setAttribute("name", "robots");
      document.head.appendChild(robots);
    }
    robots.setAttribute("content", "noindex, nofollow");
  }

  function setAdMark(el, on) {
    var mark = el.querySelector(".ad-mark");
    if (on) {
      if (!mark) {
        mark = document.createElement("span");
        mark.className = "ad-mark";
        mark.textContent = "#ad";
        el.appendChild(document.createTextNode(" "));
        el.appendChild(mark);
      }
    } else if (mark) {
      mark.remove();
    }
  }

  function apply(key, url, official, isAff) {
    document.querySelectorAll('[data-aff="' + key + '"]').forEach(function (el) {
      if (el.tagName === "A") {
        el.setAttribute("href", url);
        el.setAttribute("target", "_blank");
        if (isAff) {
          el.setAttribute("rel", "sponsored nofollow noopener noreferrer");
          el.classList.add("is-affiliate");
          el.classList.remove("is-official");
        } else {
          el.setAttribute("rel", "noopener noreferrer");
          el.classList.add("is-official");
          el.classList.remove("is-affiliate");
        }
        setAdMark(el, isAff);
      }
    });
    document.querySelectorAll('[data-aff-state="' + key + '"]').forEach(function (el) {
      var lang = document.documentElement.lang || "en";
      if (isAff) {
        el.innerHTML =
          lang === "de"
            ? "Affiliate-Link aktiv, gekennzeichnet als <strong>#ad / Anzeige</strong>."
            : "Affiliate link active, labelled <strong>#ad / Anzeige</strong>.";
        el.classList.add("is-live");
      } else {
        el.innerHTML =
          lang === "de"
            ? "Kein Affiliate-Link aktiv — dieser Verweis führt auf die offizielle Anbieterseite. Diese Seite kann in Zukunft Affiliate-Links enthalten."
            : "No affiliate link is active — this points to the official site. This page may contain affiliate links in the future.";
        el.classList.remove("is-live");
      }
    });
  }

  apply("n8n", n8n || n8nOfficial, n8nOfficial, !!n8n);
  apply("make", make || makeOfficial, makeOfficial, !!make);

  /* Discreet footer line only on pages that actually have live affiliate links. */
  if (document.querySelector("a.is-affiliate")) {
    var bottom = document.querySelector(".footer-bottom");
    if (bottom && !bottom.querySelector(".aff-foot")) {
      var lang = (document.documentElement.lang || "en").toLowerCase();
      var p = document.createElement("p");
      p.className = "aff-foot";
      p.textContent =
        lang.indexOf("de") === 0
          ? "Einige Links auf dieser Seite sind Affiliate-Links und als #ad / Anzeige gekennzeichnet."
          : lang.indexOf("pt") === 0
            ? "Alguns links nesta página são de afiliados e estão identificados como #ad / Anzeige."
            : "Some links on this page are affiliate links and are labelled #ad / Anzeige.";
      bottom.insertBefore(p, bottom.firstChild);
    }
  }
})();
