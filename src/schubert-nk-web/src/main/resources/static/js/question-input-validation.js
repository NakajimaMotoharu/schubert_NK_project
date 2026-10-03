/* SCR018/QST001; UI224; SS313/352; PG-D352/PT-QST-JS001-A..H. */
"use strict";
(() => {
  const form = document.querySelector("form.question-input");
  if (!form) return;
  const question = form.elements.namedItem("question");
  const remaining = form.querySelector("[data-question-remaining]");
  if (!question || !remaining) throw new Error("invalid question form structure");
  const encoder = new TextEncoder();
  const decoder = new TextDecoder("utf-8", { ignoreBOM: true });
  function validate() {
    const raw = question.value;
    const length = encoder.encode(raw.normalize("NFC")).length;
    remaining.textContent = String(4096 - length);
    let message = "";
    if (decoder.decode(encoder.encode(raw)) !== raw || /[\x00-\x1f\x7f-\x9f]/.test(raw) || raw.endsWith(" ")) {
      message = "入力項目を確認してください。";
    } else if (length < 1 || length > 4096) {
      message = "入力項目を確認してください。";
    }
    question.setCustomValidity(message);
    return message === "";
  }
  validate();
  question.addEventListener("input", () => validate());
  form.addEventListener("submit", (event) => {
    if (!validate()) {
      event.preventDefault();
      form.reportValidity();
    }
  });
})();
