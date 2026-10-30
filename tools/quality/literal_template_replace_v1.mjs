/** BUG2113/YKT1860: exact literal replacement, never replacement-string interpolation. */
export function replaceExactlyOnce(source, needle, replacement) {
  if (typeof source !== "string" || typeof needle !== "string"
      || typeof replacement !== "string" || needle.length === 0) {
    throw new TypeError("three literal strings and a nonempty needle required");
  }
  const first = source.indexOf(needle);
  if (first < 0 || first !== source.lastIndexOf(needle)) {
    throw new RangeError("exactly one literal occurrence required");
  }
  return source.slice(0, first) + replacement + source.slice(first + needle.length);
}
