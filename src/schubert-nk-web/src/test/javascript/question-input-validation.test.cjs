"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const script = path.resolve(__dirname, "../../main/resources/static/js/question-input-validation.js");
const source = fs.readFileSync(script, "utf8");
const invalid = "入力項目を確認してください。";

function setup(value = "", missing = "", absent = false) {
  const question = {
    value, validity: "", events: {},
    setCustomValidity(message) { this.validity = message; },
    addEventListener(type, callback) { this.events[type] = callback; }
  };
  const remaining = { textContent: "not-yet-counted" };
  const button = { disabled: false };
  const form = {
    events: {}, prevented: 0, reported: 0, submitted: 0,
    elements: { namedItem(name) {
      assert.equal(name, "question");
      return missing === "question" ? null : question;
    } },
    querySelector(selector) {
      if (selector === "button[type=submit]") return missing === "button" ? null : button;
      assert.equal(selector, "[data-question-remaining]");
      return missing === "remaining" ? null : remaining;
    },
    addEventListener(type, callback) { this.events[type] = callback; },
    reportValidity() { this.reported++; },
    submit() {
      let prevented = false;
      this.events.submit({ preventDefault: () => { this.prevented++; prevented = true; } });
      if (!prevented) this.submitted++;
    }
  };
  const sandbox = { TextEncoder, TextDecoder, document: {
    querySelector(selector) {
      assert.equal(selector, "form.question-input");
      return absent ? null : form;
    }
  }};
  const keys = Object.keys(sandbox);
  vm.runInNewContext(source, sandbox, { filename: script });
  assert.deepEqual(Object.keys(sandbox), keys);
  return { question, remaining, button, form };
}

test("PT-QST-JS001-A absent form is inert", () => {
  const { question, remaining, form } = setup("x", "", true);
  assert.deepEqual(form.events, {});
  assert.deepEqual(question.events, {});
  assert.equal(remaining.textContent, "not-yet-counted");
});
test("PT-QST-JS001-B closed required structure", () => {
  for (const missing of ["question", "remaining", "button"])
    assert.throws(() => setup("", missing), { message: "invalid question form structure" });
  const { question, form } = setup("x");
  assert.deepEqual(Object.keys(question.events), ["input"]);
  assert.deepEqual(Object.keys(form.events), ["submit"]);
});
test("PT-QST-JS001-C initial count and required validation", () => {
  const empty = setup();
  assert.equal(empty.remaining.textContent, "4096");
  assert.equal(empty.question.validity, invalid);
  const existing = setup("質問");
  assert.equal(existing.remaining.textContent, "4090");
  assert.equal(existing.question.validity, "");
  assert.equal(existing.question.value, "質問");
});
test("PT-QST-JS001-D ASCII byte boundary", () => {
  const { question, remaining } = setup("x");
  for (const [size, count, validity] of [[4095, "1", ""], [4096, "0", ""], [4097, "-1", invalid]]) {
    question.value = "a".repeat(size);
    question.events.input();
    assert.equal(remaining.textContent, count);
    assert.equal(question.validity, validity);
    assert.equal(question.value.length, size);
  }
});
test("PT-QST-JS001-E independent NFC and Unicode byte vectors", () => {
  const { question, remaining } = setup("x");
  for (const [raw, count, validity] of [
    ["e\u0301", "4094", ""], ["e\u0301".repeat(2048), "0", ""],
    ["e\u0301".repeat(2049), "-2", invalid], ["界".repeat(1365) + "a", "0", ""],
    ["界".repeat(1366), "-2", invalid], ["😀".repeat(1024), "0", ""],
    ["😀".repeat(1025), "-4", invalid], ["\ufeffx", "4092", ""]]) {
    question.value = raw;
    question.events.input();
    assert.equal(remaining.textContent, count);
    assert.equal(question.validity, validity);
    assert.equal(question.value, raw);
  }
});
test("PT-QST-JS001-F controls and malformed pairs", () => {
  const { question } = setup("x");
  for (const raw of ["\r", "\n", "\t", "\0", "\u001f", "\u007f", "\u0085", "\u009f", "\ud800", "\udfff", "x\ud800", "\udfffy"]) {
    question.value = raw;
    question.events.input();
    assert.equal(question.validity, invalid);
    assert.equal(question.value, raw);
  }
  question.value = "😀";
  question.events.input();
  assert.equal(question.validity, "");
});
test("PT-QST-JS001-G no trimming and trailing ASCII only", () => {
  const { question, remaining } = setup("x");
  for (const [raw, count, validity] of [[" x", "4094", ""], ["x ", "4094", invalid], [" ", "4095", invalid], ["x\u00a0", "4093", ""], ["x\u3000", "4092", ""]]) {
    question.value = raw;
    question.events.input();
    assert.equal(remaining.textContent, count);
    assert.equal(question.validity, validity);
    assert.equal(question.value, raw);
  }
});
test("PT-QST-JS001-H fresh input/submit never auto resends", () => {
  const { question, remaining, button, form } = setup("x");
  form.submit();
  assert.equal(form.submitted, 1);
  assert.equal(form.prevented, 0);
  assert.equal(form.reported, 0);
  assert.equal(button.disabled, true); // UI222 section 8: valid operation POST shows disabled.
  question.value = "";
  form.submit();
  assert.equal(remaining.textContent, "4096");
  assert.equal(form.submitted, 1);
  assert.equal(form.prevented, 1);
  assert.equal(form.reported, 1);
  question.value = "new";
  question.events.input();
  assert.equal(remaining.textContent, "4093");
  assert.equal(form.submitted, 1);
  form.submit();
  assert.equal(form.submitted, 2);
  assert.equal(form.prevented, 1);
  assert.equal(form.reported, 1);
  const correction = setup("");
  correction.form.submit();
  assert.equal(correction.button.disabled, false);
  assert.equal(correction.form.prevented, 1);
  correction.question.value = "x";
  correction.form.submit(); // Submit must revalidate even without a preceding input event.
  assert.equal(correction.button.disabled, true);
  assert.equal(correction.remaining.textContent, "4095");
  assert.equal(correction.form.submitted, 1);
  assert.equal(correction.form.reported, 1);
});
