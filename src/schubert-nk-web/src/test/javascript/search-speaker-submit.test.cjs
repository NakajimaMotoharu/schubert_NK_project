"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const script = path.resolve(__dirname, "../../main/resources/static/js/search-speaker-submit.js");
const source = fs.readFileSync(script, "utf8");
function setup(missing = "", absent = false) {
  const controls = {};
  for (const name of ["q", "speaker", "chapter", "game"]) {
    controls[name] = { value: "", validity: "", events: {},
      setCustomValidity(message) { this.validity = message; },
      addEventListener(type, action) { this.events[type] = action; } };
  }
  if (missing) delete controls[missing];
  const form = { events: {}, reports: 0, requested: 0, submitted: 0, prevented: 0,
    elements: { namedItem(name) { return controls[name] || null; } },
    addEventListener(type, action) { this.events[type] = action; },
    reportValidity() { this.reports++; },
    requestSubmit() { this.requested++; this.submit(); },
    submit() {
      let prevented = false;
      this.events.submit({ preventDefault: () => { prevented = true; this.prevented++; } });
      if (!prevented) this.submitted++;
    }
  };
  const sandbox = { TextEncoder, TextDecoder, document: {
    querySelector(selector) { assert.equal(selector, "form.filters"); return absent ? null : form; }
  }};
  const keys = Object.keys(sandbox);
  vm.runInNewContext(source, sandbox, { filename: script });
  assert.deepEqual(Object.keys(sandbox), keys);
  return { form, controls };
}
test("PT-SCR025-A absent form and registration", () => {
  const absent = setup("", true);
  assert.deepEqual(absent.form.events, {}); assert.equal(absent.form.submitted, 0);
  const { form, controls } = setup();
  assert.deepEqual(Object.keys(form.events), ["submit"]);
  for (const name of ["q", "speaker", "chapter"]) {
    assert.deepEqual(Object.keys(controls[name].events), ["input"]);
    assert.equal(controls[name].value, ""); assert.equal(controls[name].validity, "");
  }
  assert.deepEqual(Object.keys(controls.game.events), ["change"]);
});
test("PT-SCR025-B missing template controls", () => {
  for (const name of ["q", "speaker", "chapter", "game"])
    assert.throws(() => setup(name), { message: "invalid search form structure" });
});
test("PT-SCR025-C independent ASCII byte boundaries", () => {
  const { controls } = setup();
  for (const [name, limit, message] of [
    ["q", 256, "本文はUTF-8で256 byte以内にしてください。"],
    ["speaker", 128, "話者はUTF-8で128 byte以内にしてください。"],
    ["chapter", 256, "章タイトルはUTF-8で256 byte以内にしてください。"]]) {
    for (const size of [limit - 1, limit, limit + 1]) {
      controls[name].value = "a".repeat(size); controls[name].events.input();
      assert.equal(controls[name].validity, size > limit ? message : "");
      assert.equal(controls[name].value, "a".repeat(size));
    }
  }
});
test("PT-SCR025-D Unicode and forbidden controls", () => {
  const { controls } = setup(); const q = controls.q;
  for (const raw of ["\r", "\n", "\t", "\u0000", "x\n", "\uD800", "\uD800x", "\uDC00", "\uD800\n"]) {
    q.value = raw; q.events.input();
    assert.equal(q.validity, "使用できない文字が含まれています。"); assert.equal(q.value, raw);
  }
  q.value = "😀".repeat(64); q.events.input(); assert.equal(q.validity, "");
  q.value += "x"; q.events.input(); assert.equal(q.validity, "本文はUTF-8で256 byte以内にしてください。");
});
test("PT-SCR025-E NFC and Java ASCII trim compatibility", () => {
  const { controls } = setup(); const q = controls.q;
  for (const raw of ["e\u0301".repeat(128), "  " + "a".repeat(256) + " ",
      "\u00A0" + "a".repeat(252) + "\u00A0", "\uFEFF" + "a".repeat(253)]) {
    q.value = raw; q.events.input(); assert.equal(q.validity, ""); assert.equal(q.value, raw);
  }
  for (const raw of ["e\u0301".repeat(129), "\u00A0" + "a".repeat(254) + "\u00A0",
      "\uFEFF" + "a".repeat(254)]) {
    q.value = raw; q.events.input(); assert.equal(q.validity, "本文はUTF-8で256 byte以内にしてください。");
    assert.equal(q.value, raw);
  }
});
test("PT-SCR025-F all invalid fields stop submit", () => {
  const { controls, form } = setup();
  controls.q.value = "\n"; controls.speaker.value = "s".repeat(129); controls.chapter.value = "c".repeat(257);
  form.submit();
  assert.equal(controls.q.validity, "使用できない文字が含まれています。");
  assert.equal(controls.speaker.validity, "話者はUTF-8で128 byte以内にしてください。");
  assert.equal(controls.chapter.validity, "章タイトルはUTF-8で256 byte以内にしてください。");
  assert.equal(form.prevented, 1); assert.equal(form.reports, 1); assert.equal(form.submitted, 0);
});
test("PT-SCR025-G input clears errors and permits valid submit", () => {
  const { controls, form } = setup();
  controls.q.value = "\n"; form.submit(); assert.equal(form.prevented, 1);
  controls.q.value = "本文"; controls.q.events.input(); assert.equal(controls.q.validity, "");
  form.submit(); assert.equal(form.submitted, 1); assert.equal(form.reports, 1);
});
test("PT-SCR025-H game change uses native submission", () => {
  const { controls, form } = setup();
  controls.game.value = "NUKITASHI2"; controls.game.events.change();
  assert.equal(form.requested, 1); assert.equal(form.submitted, 1); assert.equal(form.prevented, 0);
  controls.q.value = "\t"; controls.game.events.change();
  assert.equal(form.requested, 2); assert.equal(form.submitted, 1); assert.equal(form.prevented, 1);
});
