/**
 * Admin inline: ລວມແຖວ = ຈຳນວນ × ຕົ້ນທຶນ/ໜ່ວຍ
 * ຍອດລວມ = ຜົນລວມທຸກແຖວ (ນັບແຕ່ຊ່ອງ subtotal ທີ່ບໍ່ຊ້ຳ)
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

  function pairFor(subInput) {
    var name = subInput.name;
    if (!name || name.indexOf("-subtotal") === -1) return null;
    var prefix = name.slice(0, -"-subtotal".length);
    return {
      qty: document.querySelector('input[name="' + prefix + '-quantity"]'),
      cost: document.querySelector('input[name="' + prefix + '-cost_price"]'),
      sub: subInput,
    };
  }

  function uniqueSubtotalInputs() {
    var seen = {};
    var list = [];
    document.querySelectorAll('input[name$="-subtotal"]').forEach(function (el) {
      if (!el.name || seen[el.name]) return;
      if (isTemplateOrDeleted(el)) return;
      seen[el.name] = true;
      list.push(el);
    });
    return list;
  }

  function recalcAll() {
    var sum = 0;
    uniqueSubtotalInputs().forEach(function (sub) {
      var f = pairFor(sub);
      if (!f || !f.qty || !f.cost) return;
      f.sub.value = money(parseNum(f.qty.value) * parseNum(f.cost.value));
      f.sub.readOnly = true;
      f.sub.classList.add("mz-auto-calc");
      sum += parseNum(f.sub.value);
    });
    var total = document.getElementById("id_total_amount");
    if (total) {
      total.value = money(sum);
      total.readOnly = true;
      total.classList.add("mz-auto-calc");
      total.title = "ຄິດໄລ່ອັດຕະໂນມັດຈາກລາຍການ";
    }
  }

  function onChange(e) {
    var t = e.target;
    if (!t || !t.name) return;
    if (
      t.name.indexOf("-quantity") === -1 &&
      t.name.indexOf("-cost_price") === -1 &&
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
