"use strict";
// UI222 section8 independent literal; DB-free review only, not browser or JS coverage acceptance.
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const source = fs.readFileSync(process.argv[2], "utf8");
function fixture(value) {
  const handlers = {};
  const button = { disabled: false };
  const question = { value, setCustomValidity(v) { this.error = v; }, addEventListener() {} };
  const remaining = { textContent: "" };
  const form = {
    elements: { namedItem(name) { assert.equal(name, "question"); return question; } },
    querySelector(selector) {
      if (selector === "[data-question-remaining]") return remaining;
      assert.equal(selector, "button[type=submit]"); return button;
    },
    addEventListener(name, fn) { handlers[name] = fn; },
    reportValidity() { this.reported = true; }
  };
  vm.runInNewContext(source, { document: { querySelector(selector) { assert.equal(selector, "form.question-input"); return form; } }, TextEncoder, TextDecoder });
  const event = { prevented: false, preventDefault() { this.prevented = true; } };
  handlers.submit(event);
  return { button, event, form, question };
}
const invalid = fixture("");
assert.equal(invalid.event.prevented, true);
assert.equal(invalid.button.disabled, false);
assert.equal(invalid.form.reported, true);
const valid = fixture("独立した公開fixture質問");
assert.equal(valid.event.prevented, false);
assert.equal(valid.button.disabled, true, "UI222 valid submit must disable the submit button");
console.log("independentInvalidAndValidDisabled=true;browserAndDbAccepted=false");
