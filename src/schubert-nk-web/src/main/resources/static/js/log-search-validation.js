/* SCR014/FUN008/AUT002; UI222/225/235; SS313/352; PG217/PT-SCR092. */
"use strict";
(() => {
  const form = document.querySelector("form.log-filters");
  if (!form) return;
  const definitions = [["q", 256, "メッセージ"], ["action", 64, "アクション"], ["path", 256, "パス"]];
  const controls = definitions.map(([name, maximum, label]) => [form.elements.namedItem(name), maximum, label]);
  if (controls.some(([control]) => !control)) throw new Error("invalid log form structure");
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
})();
