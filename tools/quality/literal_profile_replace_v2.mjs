/** Literal profile substitution only. No code evaluation, filesystem or Product operations. */
export function replaceProfileLiterals(source, entries) {
  if (typeof source !== "string" || !source.isWellFormed()
      || !Array.isArray(entries) || entries.length < 1 || entries.length > 512) {
    throw new TypeError("well-formed source and one to 512 explicit entries required");
  }
  const pairs = [];
  const seen = new Set();
  for (const entry of entries) {
    if (!Array.isArray(entry) || entry.length !== 3) {
      throw new TypeError("needle, replacement, exact original occurrence count required");
    }
    const [needle, replacement, expected] = entry;
    if (typeof needle !== "string" || !needle.length || !needle.isWellFormed()
        || typeof replacement !== "string" || !replacement.isWellFormed()
        || !Number.isSafeInteger(expected) || expected < 1) {
      throw new TypeError("literal strings and positive safe occurrence count required");
    }
    if (seen.has(needle)) throw new RangeError("duplicate original needle");
    if (/^[+-]?[0-9]+(?:\.[0-9]+)?$/.test(needle)
        || (/^[a-fA-F0-9]{6,63}$/.test(needle) && needle.length !== 40)) {
      throw new RangeError("bare numeric or partial digest replacement forbidden");
    }
    seen.add(needle);
    pairs.push([needle, replacement, expected]);
  }
  pairs.sort((a, b) => b[0].length - a[0].length || (a[0] < b[0] ? -1 : 1));
  const escape = value => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(pairs.map(([needle]) => escape(needle)).join("|"), "gu");
  const byNeedle = new Map(pairs.map(([needle, replacement, expected]) =>
    [needle, {replacement, expected, count: 0}]));
  const text = source.replace(regex, needle => {
    const row = byNeedle.get(needle);
    row.count++;
    return row.replacement;
  });
  for (const row of byNeedle.values()) {
    if (row.count !== row.expected) throw new RangeError("exact original occurrence count mismatch");
  }
  return Object.freeze({
    text,
    counts: Object.freeze(Object.fromEntries([...byNeedle].map(([needle, row]) => [needle, row.count]))),
  });
}
