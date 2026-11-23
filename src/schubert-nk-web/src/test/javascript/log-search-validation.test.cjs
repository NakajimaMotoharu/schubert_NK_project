"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const script = path.resolve(__dirname, "../../main/resources/static/js/log-search-validation.js");
const source = fs.readFileSync(script, "utf8");

function setup(missing = "", absent = false) {
  const controls = {};
  for (const name of ["q", "action", "path"]) {
    controls[name] = {
      value: "", validity: "", events: {},
      setCustomValidity(message) { this.validity = message; },
      addEventListener(type, action) { this.events[type] = action; }
    };
  }
  if (missing) delete controls[missing];
  const form = {
    events: {}, prevented: 0, reported: 0, submitted: 0,
    elements: { namedItem(name) { return controls[name] || null; } },
    addEventListener(type, action) { this.events[type] = action; },
    reportValidity() { this.reported++; },
    submit() {
      let prevented = false;
      this.events.submit({ preventDefault: () => { this.prevented++; prevented = true; } });
      if (!prevented) this.submitted++;
    }
  };
  const sandbox = { TextEncoder, TextDecoder, document: {
    querySelector(selector) { assert.equal(selector, "form.log-filters"); return absent ? null : form; }
  }};
  const keys = Object.keys(sandbox);
  vm.runInNewContext(source, sandbox, { filename: script });
  assert.deepEqual(Object.keys(sandbox), keys);
  return { form, controls };
}

test("PT-SCR092-A missing page stays inert", () => {
  const { form } = setup("", true);
  assert.deepEqual(form.events, {});
});
test("PT-SCR092-B fixed form structure", () => {
  for (const name of ["q", "action", "path"])
    assert.throws(() => setup(name), { message: "invalid log form structure" });
  const { controls, form } = setup();
  assert.deepEqual(Object.keys(form.events), ["submit"]);
  for (const control of Object.values(controls)) assert.deepEqual(Object.keys(control.events), ["input"]);
});
test("PT-SCR092-C ASCII boundary from UI225", () => {
  const { controls } = setup();
  for (const [name, limit, label] of [["q", 256, "メッセージ"], ["action", 64, "アクション"], ["path", 256, "パス"]]) {
    for (const n of [limit - 1, limit, limit + 1]) {
      controls[name].value = "a".repeat(n);
      controls[name].events.input();
      assert.equal(controls[name].validity, n > limit ? label + "はUTF-8で" + limit + " byte以内にしてください。" : "");
      assert.equal(controls[name].value.length, n);
    }
  }
});
test("PT-SCR092-D Unicode controls and malformed pairs", () => {
  const { controls } = setup();
  for (const raw of ["\r", "\n", "\t", "\u0000", "\uD800", "\uD800x", "\uDC00", "x\n", " \uD800 "]) {
    controls.q.value = raw;
    controls.q.events.input();
    assert.equal(controls.q.validity, "使用できない文字が含まれています。");
    assert.equal(controls.q.value, raw);
  }
});
test("PT-SCR092-E NFC and ASCII trim byte vectors", () => {
  const { controls } = setup();
  for (const [raw, expected] of [
    ["e\u0301".repeat(128), ""], ["  " + "a".repeat(256) + " ", ""],
    ["\u00A0" + "a".repeat(252) + "\u00A0", ""],
    ["\uFEFF" + "a".repeat(253), ""],
    ["e\u0301".repeat(129), "メッセージはUTF-8で256 byte以内にしてください。"],
    ["\uFEFF" + "a".repeat(254), "メッセージはUTF-8で256 byte以内にしてください。"],
    ["\u00A0" + "a".repeat(254) + "\u00A0", "メッセージはUTF-8で256 byte以内にしてください。"]]) {
    controls.q.value = raw;
    controls.q.events.input();
    assert.equal(controls.q.validity, expected);
    assert.equal(controls.q.value, raw);
  }
});
test("PT-SCR092-F all invalid fields block native GET", () => {
  const { controls, form } = setup();
  controls.q.value = "\n";
  controls.action.value = "x".repeat(65);
  controls.path.value = "😀".repeat(65);
  form.submit();
  assert.equal(controls.q.validity, "使用できない文字が含まれています。");
  assert.equal(controls.action.validity, "アクションはUTF-8で64 byte以内にしてください。");
  assert.equal(controls.path.validity, "パスはUTF-8で256 byte以内にしてください。");
  assert.equal(form.prevented, 1);
  assert.equal(form.reported, 1);
  assert.equal(form.submitted, 0);
});
test("PT-SCR092-G fixed Unicode byte edges", () => {
  const { controls } = setup();
  for (const [name, atLimit, over] of [["q", "😀".repeat(64), "😀".repeat(64) + "a"],
    ["action", "あ".repeat(21) + "x", "あ".repeat(22)],
    ["path", "あ".repeat(85) + "x", "あ".repeat(86)]]) {
    controls[name].value = atLimit;
    controls[name].events.input();
    assert.equal(controls[name].validity, "");
    controls[name].value = over;
    controls[name].events.input();
    assert.notEqual(controls[name].validity, "");
  }
});
test("PT-SCR092-H corrected input permits submit", () => {
  const { controls, form } = setup();
  controls.q.value = "\t";
  form.submit();
  assert.equal(form.prevented, 1);
  controls.q.value = "本文";
  controls.q.events.input();
  assert.equal(controls.q.validity, "");
  form.submit();
  assert.equal(form.reported, 1);
  assert.equal(form.submitted, 1);
});
