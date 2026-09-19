/* SCR003/FUN003; UI222/223; SS313/352; PG201/PT-SCR025-A..H. */
"use strict";
(() => {
  const form = document.querySelector("form.filters");
  if (!form) return;
  const game = form.elements.namedItem("game");
  const definitions = [["q", 256, "本文"], ["speaker", 128, "話者"], ["chapter", 256, "章タイトル"]];
  const controls = definitions.map(([name, maximum, label]) => [form.elements.namedItem(name), maximum, label]);
  if (!game || controls.some(([control]) => !control)) throw new Error("invalid search form structure");
  const encoder = new TextEncoder();
  const decoder = new TextDecoder("utf-8", { ignoreBOM: true });
  function validate(control, maximum, label) {
    const raw = control.value;
    let message = "";
    if (decoder.decode(encoder.encode(raw)) !== raw || /[\r\n\t\x00]/.test(raw)) {
      message = "使用できない文字が含まれています。";
    } else {
      const normalized = raw.normalize("NFC").replace(/^[\x00-\x20]+|[\x00-\x20]+$/g, "");
      if (encoder.encode(normalized).length > maximum) {
        message = label + "はUTF-8で" + maximum + " byte以内にしてください。";
      }
    }
    control.setCustomValidity(message);
    return message === "";
  }
  for (const [control, maximum, label] of controls) {
    control.addEventListener("input", () => validate(control, maximum, label));
  }
  form.addEventListener("submit", (event) => {
    let valid = true;
    for (const [control, maximum, label] of controls) {
      if (!validate(control, maximum, label)) valid = false;
    }
    if (!valid) {
      event.preventDefault();
      form.reportValidity();
    }
  });
  game.addEventListener("change", () => form.requestSubmit());
})();
