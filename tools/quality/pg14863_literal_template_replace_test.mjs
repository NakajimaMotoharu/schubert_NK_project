import assert from "node:assert/strict";
import { replaceExactlyOnce } from "./literal_template_replace_v1.mjs";

// PT-TOOL-LIT001: independent expected literals, no Product/VM/files/network operations.
assert.equal(process.version, "v24.19.0");
const positives = [
  ["abc", "b", "x", "axc"],
  ["abc", "b", "$'", "a$'c"],
  ["abc", "b", "$&", "a$&c"],
  ["abc", "b", "$`", "a$`c"],
  ["abc", "b", "$$", "a$$c"],
  ["abc", "b", "$1", "a$1c"],
  ["abc", "b", "", "ac"],
  ["A\nB\nC", "B", "line1\nline2", "A\nline1\nline2\nC"],
  ["A😀B", "😀", "🧪", "A🧪B"],
  ["a\\bc", "\\b", "\\x", "a\\xc"],
  ["BODY\nOWNER", "BODY", "name.split('$',1)", "name.split('$',1)\nOWNER"],
];
for (const [source, needle, replacement, expected] of positives) {
  assert.equal(replaceExactlyOnce(source, needle, replacement), expected);
}
const negatives = [
  [null, "b", "x"], [[], "b", "x"], [1, "b", "x"],
  ["abc", null, "x"], ["abc", {}, "x"], ["abc", "", "x"],
  ["abc", "b", null], ["abc", "b", false],
  ["abc", "z", "x"], ["BODY BODY", "BODY", "x"], ["aaa", "aa", "x"],
];
for (const values of negatives) assert.throws(() => replaceExactlyOnce(...values));
// Preserve the actual native API failure; this is tool metadata reproduction, not a retry of PT.
const faulty = "BODY\nOWNER".replace("BODY", "name.split('$',1)");
assert.equal(faulty.split("OWNER").length - 1, 2);
assert.equal(replaceExactlyOnce("BODY\nOWNER", "BODY", "name.split('$',1)").split("OWNER").length - 1, 1);
process.stdout.write(JSON.stringify({
  actualExit: 0, toolPositiveVectors: positives.length, toolNegativeVectors: negatives.length,
  nativeFailureOwnerOccurrences: 2, correctedOwnerOccurrences: 1,
  productTestsExecuted: 0, externalActions: 0, formalUpdated: false,
}) + "\n");
