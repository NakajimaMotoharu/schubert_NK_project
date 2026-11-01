import assert from "node:assert/strict";
import { replaceProfileLiterals } from "./literal_profile_replace_v2.mjs";
assert.equal(process.version, "v24.19.0");

// Fixed independent literals, not derived with the helper.
const positives = [
  ["abc", [["b", "x", 1]], "axc"],
  ["BODY OWNER", [["BODY", "OWNER", 1], ["OWNER", "END", 1]], "OWNER END"],
  ["PG18238 PG18258", [["PG18238", "PG18258", 1], ["PG18258", "PG18278", 1]], "PG18258 PG18278"],
  ["AB A", [["A", "SHORT", 1], ["AB", "LONG", 1]], "LONG SHORT"],
  ["A A", [["A", "", 2]], " "],
  ["BODY", [["BODY", "$' $& $` $$ $1", 1]], "$' $& $` $$ $1"],
  ["A\nBODY\nC", [["BODY", "one\ntwo", 1]], "A\none\ntwo\nC"],
  ["日本語 😀", [["日本語", "表示", 1], ["😀", "🧪", 1]], "表示 🧪"],
  ["a.b [x] (y) $^", [["a.b", "DOT", 1], ["[x]", "SQUARE", 1], ["(y)", "PAREN", 1], ["$^", "CASH", 1]], "DOT SQUARE PAREN CASH"],
  ["aa", [["aa", "b", 1]], "b"],
  ["a".repeat(40), [["a".repeat(40), "c".repeat(40), 1]], "c".repeat(40)],
  ["b".repeat(64), [["b".repeat(64), "d".repeat(64), 1]], "d".repeat(64)],
  ["COUNT=6 hash=123456", [["COUNT=6", "COUNT=8", 1]], "COUNT=8 hash=123456"],
  ["__proto__ constructor", [["__proto__", "PROTO", 1], ["constructor", "CTOR", 1]], "PROTO CTOR"],
  ["same", [["same", "same", 1]], "same"],
];
function independentScan(source, entries) {
  let offset = 0;
  let text = "";
  const counts = Object.fromEntries(entries.map(([needle]) => [needle, 0]));
  while (offset < source.length) {
    let selected;
    for (const row of entries) {
      if (source.startsWith(row[0], offset) && (!selected || row[0].length > selected[0].length)) {
        selected = row;
      }
    }
    if (selected) {
      text += selected[1];
      counts[selected[0]]++;
      offset += selected[0].length;
    } else {
      text += source[offset++];
    }
  }
  return {text, counts};
}
for (const [source, entries, expected] of positives) {
  const before = JSON.stringify(entries);
  const actual = replaceProfileLiterals(source, entries);
  assert.equal(actual.text, expected);
  assert.deepEqual(actual, independentScan(source, entries));
  assert.equal(JSON.stringify(entries), before);
  assert.equal(Object.isFrozen(actual), true);
  assert.equal(Object.isFrozen(actual.counts), true);
}
const negatives = [
  [null, [["A", "B", 1]]], [[], [["A", "B", 1]]], [1, [["A", "B", 1]]],
  ["A", null], ["A", {}], ["A", []],
  ["A", [["", "B", 1]]], ["A", [[null, "B", 1]]],
  ["A", [["A", null, 1]]], ["A", [["A", false, 1]]],
  ["A", [["A", "B"]]], ["A", ["A"]], ["A", [null]],
  ["A", [["A", "B", 0]]], ["A", [["A", "B", -1]]],
  ["A", [["A", "B", 1.5]]], ["A", [["A", "B", NaN]]],
  ["A", [["A", "B", true]]], ["A", [["A", "B", Number.MAX_SAFE_INTEGER + 1]]],
  ["A", [["A", "B", 2]]], ["A", [["Z", "B", 1]]],
  ["A", [["A", "B", 1], ["A", "C", 1]]],
  ["COUNT=6", [["6", "8", 1]]], ["12.5", [["12.5", "13", 1]]],
  ["abcdef", [["abcdef", "OTHER", 1]]], ["a".repeat(63), [["a".repeat(63), "X", 1]]],
  ["AB", [["A", "X", 1], ["AB", "Y", 1]]],
  ["\uD800", [["A", "B", 1]]], ["A", [["\uD800", "B", 1]]], ["A", [["A", "\uD800", 1]]],
  ["A", Array.from({length: 513}, (_, i) => ["KEY" + i, "V", 1])],
];
for (const values of negatives) assert.throws(() => replaceProfileLiterals(...values));

// Boundary512 and immutable snapshots are separate checks, not Product tests.
const boundary = Array.from({length: 512}, (_, i) => ["KEY_" + i + ";", "VALUE_" + i + ";", 1]);
const joined = boundary.map(row => row[0]).join("");
assert.equal(replaceProfileLiterals(joined, boundary).text, boundary.map(row => row[1]).join(""));
const frozen = replaceProfileLiterals("A", [["A", "B", 1]]);
assert.throws(() => { frozen.text = "CHANGED"; });
assert.throws(() => { frozen.counts.A = 99; });
const input = [["A", "B", 1]];
const snapshot = replaceProfileLiterals("A", input);
input[0][1] = "C";
assert.equal(snapshot.text, "B");
process.stdout.write(JSON.stringify({
  actualExit: 0, toolPositiveVectors: positives.length, toolNegativeVectors: negatives.length,
  independentScanVectors: positives.length, boundaryAndSnapshotChecks: 4,
  productTestsExecuted: 0, externalActions: 0, formalUpdated: false,
}) + "\n");
