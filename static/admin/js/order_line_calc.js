/**
 * Admin OrderItem inline: ລວມແຖວ = ຈຳນວນ × ລາຄາ/ໜ່ວຍ
 */
(function () {
  function parseNum(value) {
    if (value == null || value === "") return 0;
    var n = parseFloat(String(value).replace(/,/g, "").trim());
    return Number.isFinite(n) ? n : 0;
  }

  function money(n) {
    return (Math.round(n * 100) / 100).toFixed(2);
  }

  function isTemplateOrDeleted(el) {
    var name = el.name || "";
    if (name.indexOf("__prefix__") !== -1) return true;
    var row = el.closest("tr, .inline-related");
    if (!row) return false;
    if (row.classList.contains("empty-form") || row.classList.contains("deleted")) return true;
    var del = row.querySelector('input[name$="-DELETE"]');
    return !!(del && del.checked);
  }

  function recalcAll() {
    document.querySelectorAll('input[name$="-subtotal"]').forEach(function (sub) {
      if (!sub.name || isTemplateOrDeleted(sub)) return;
      var prefix = sub.name.slice(0, -"-subtotal".length);
      var qty = document.querySelector('input[name="' + prefix + '-quantity"]');
      var price = document.querySelector('input[name="' + prefix + '-price"]');
      if (!qty || !price) return;
      sub.value = money(parseNum(qty.value) * parseNum(price.value));
      sub.readOnly = true;
    });
  }

  function onChange(e) {
    var t = e.target;
    if (!t || !t.name) return;
    if (
      t.name.indexOf("-quantity") === -1 &&
      t.name.indexOf("-price") === -1 &&
      t.name.indexOf("-DELETE") === -1
    ) {
      return;
    }
    recalcAll();
  }

  function init() {
    recalcAll();
    document.body.addEventListener("input", onChange);
    document.body.addEventListener("change", onChange);
    document.body.addEventListener("formset:added", recalcAll);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
