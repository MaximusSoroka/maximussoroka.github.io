(function () {
  var grid = document.getElementById("tool-grid");
  var empty = document.getElementById("no-results");
  var search = document.getElementById("tool-search");
  if (!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll(".card"));
  var chips = Array.prototype.slice.call(document.querySelectorAll(".chip"));
  var group = "all";

  function norm(s) {
    return (s || "").toLowerCase();
  }

  function apply() {
    var q = search ? norm(search.value) : "";
    var shown = 0;
    cards.forEach(function (card) {
      var g = card.getAttribute("data-group") || "all";
      var text = norm(card.getAttribute("data-search"));
      var ok = (group === "all" || g === group) && (!q || text.indexOf(q) !== -1);
      card.hidden = !ok;
      if (ok) shown += 1;
    });
    if (empty) empty.classList.toggle("show", shown === 0);
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      group = chip.getAttribute("data-group") || "all";
      chips.forEach(function (c) {
        c.setAttribute("aria-pressed", c === chip ? "true" : "false");
      });
      apply();
    });
  });
  if (search) search.addEventListener("input", apply);
})();
