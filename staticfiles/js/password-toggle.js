(function () {
  document.querySelectorAll(".mz-password-wrap").forEach(function (wrap) {
    var input = wrap.querySelector("input");
    var btn = wrap.querySelector(".mz-password-toggle-btn");
    if (!input || !btn) return;

    var showIcon = btn.querySelector(".mz-password-icon-show");
    var hideIcon = btn.querySelector(".mz-password-icon-hide");

    btn.addEventListener("click", function () {
      var visible = input.type === "text";
      input.type = visible ? "password" : "text";
      btn.setAttribute("aria-pressed", visible ? "false" : "true");
      btn.setAttribute("aria-label", visible ? "Show password" : "Hide password");
      if (showIcon) showIcon.classList.toggle("d-none", !visible);
      if (hideIcon) hideIcon.classList.toggle("d-none", visible);
    });
  });
})();
