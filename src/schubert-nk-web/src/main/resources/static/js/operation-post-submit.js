"use strict";
// UI222§8/BUG1222/YKT988/PT-WEB-OPSJS2646. Tokens and server idempotence remain unchanged.
(() => {
  for (const form of document.querySelectorAll("form[data-operation-submit]")) {
    const token = form.querySelector("input[type=hidden][name=operation_token]");
    const buttons = form.querySelectorAll("button[type=submit]");
    if (!token || buttons.length === 0) throw new Error("invalid operation form structure");
    let submitted = false;
    form.addEventListener("submit", (event) => {
      if (submitted) {
        event.preventDefault();
        return;
      }
      if (!form.checkValidity()) {
        event.preventDefault();
        form.reportValidity();
        return;
      }
      submitted = true;
      for (const button of buttons) button.disabled = true;
    });
  }
})();
