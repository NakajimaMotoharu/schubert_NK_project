"use strict";
// UI222§8/BUG1222/YKT988/PT-WEB-OPSJS2646-A..F. Independent DOM-event fixture.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const script = path.resolve(__dirname, "../../main/resources/static/js/operation-post-submit.js");
const source = fs.readFileSync(script, "utf8");

function setup(definitions) {
  const forms = definitions.map(([valid, missing]) => {
    const buttons = [{ disabled: false }, { disabled: false }];
    const token = { value: "PUBLIC_TEST_ONLY", name: "operation_token" };
    const form = { valid, buttons, token, handlers: {}, prevented: 0, reports: 0,
      querySelector(selector) {
        assert.equal(selector, "input[type=hidden][name=operation_token]");
        return missing === "token" ? null : token;
      },
      querySelectorAll(selector) {
        assert.equal(selector, "button[type=submit]");
        return missing === "button" ? [] : buttons;
      },
      checkValidity() { return this.valid; },
      reportValidity() { this.reports++; },
      addEventListener(name, handler) { assert.equal(name, "submit"); this.handlers[name] = handler; },
      submit() { this.handlers.submit({ preventDefault: () => this.prevented++ }); }
    };
    return form;
  });
  const sandbox = { document: { querySelectorAll(selector) {
    assert.equal(selector, "form[data-operation-submit]"); return forms;
  } } };
  const keys = Object.keys(sandbox);
  vm.runInNewContext(source, sandbox, { filename: script });
  assert.deepEqual(Object.keys(sandbox), keys);
  return forms;
}

test("PT-WEB-OPSJS2646-A no update form leaves document inert", () => {
  assert.deepEqual(setup([]), []);
});
test("PT-WEB-OPSJS2646-B token/button structure is closed", () => {
  for (const missing of ["token", "button"])
    assert.throws(() => setup([[true, missing]]), { message: "invalid operation form structure" });
});
test("PT-WEB-OPSJS2646-C valid keyboard submit disables every submit button and preserves token", () => {
  const [form] = setup([[true, ""]]);
  assert.deepEqual(form.buttons.map(b => b.disabled), [false, false]);
  form.submit();
  assert.deepEqual(form.buttons.map(b => b.disabled), [true, true]);
  assert.equal(form.prevented, 0); assert.equal(form.reports, 0);
  assert.equal(form.token.value, "PUBLIC_TEST_ONLY");
});
test("PT-WEB-OPSJS2646-D invalid then corrected submit never locks invalid form", () => {
  const [form] = setup([[false, ""]]);
  form.submit();
  assert.deepEqual(form.buttons.map(b => b.disabled), [false, false]);
  assert.equal(form.prevented, 1); assert.equal(form.reports, 1);
  form.valid = true; form.submit();
  assert.deepEqual(form.buttons.map(b => b.disabled), [true, true]);
  assert.equal(form.prevented, 1); assert.equal(form.reports, 1);
});
test("PT-WEB-OPSJS2646-E second submit is suppressed without reissuing operation", () => {
  const [form] = setup([[true, ""]]); form.submit(); form.submit();
  assert.equal(form.prevented, 1); assert.equal(form.reports, 0);
  assert.deepEqual(form.buttons.map(b => b.disabled), [true, true]);
});
test("PT-WEB-OPSJS2646-F independent forms retain independent submission state", () => {
  const [first, second] = setup([[true, ""], [true, ""]]); first.submit();
  assert.deepEqual(second.buttons.map(b => b.disabled), [false, false]);
  second.submit(); assert.equal(second.prevented, 0);
  assert.equal(first.token.value, second.token.value);
});
