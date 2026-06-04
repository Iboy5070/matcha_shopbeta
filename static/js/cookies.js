(function () {
  var KEY = "mz_cookie_consent";
  var banner = document.getElementById("mz-cookie-banner");
  if (!banner) return;
  if (localStorage.getItem(KEY)) return;
  banner.classList.add("show");
  document.getElementById("mz-cookie-accept")?.addEventListener("click", function () {
    localStorage.setItem(KEY, "1");
    banner.classList.remove("show");
  });
  document.getElementById("mz-cookie-decline")?.addEventListener("click", function () {
    localStorage.setItem(KEY, "0");
    banner.classList.remove("show");
  });
})();
