"""Strict single add-only block and positive controls before ten distinct token mutations."""
from f03_literal_batch_sources import tokens
from f03_lgs_boundary_vectors import location, METHODS
from f03_lgs_boundary_vectors_v2 import methods
from f03_positioned_ascii_literals import baseline as measured_baseline

baseline = measured_baseline

INSERT = '''
    for (boolean wrongLayout : List.of(true, false)) {
      var f = new Fixture();
      f.reply =
          (id, b) ->
              wrongLayout
                  ? header("MCTRSP01", 8, 72, 1, FIXTURE_0000_876EEFE0, id, CONTEXT.wireValue())
                  : Arrays.copyOf(
                      response(0, false, FIXTURE_0000_876EEFE0, id, CONTEXT.wireValue()), 305);
      rejected(Reason.INVALID_RESPONSE, () -> f.client.exchange(input(), CONTEXT));
      f.erased();
    }
'''

def inverse(old, new, mapping):
    assert mapping == []
    before, after = tokens(old), tokens(new)
    assert methods(before) == methods(after) == METHODS
    pattern = tokens(INSERT)
    at = location(after, pattern)
    assert location(after, tokens('void web273MalformedReplies() {')) < at < location(after, tokens('void web274CapabilitiesAndNull() {'))
    assert after[:at] + after[at+len(pattern):] == before
    return dict(originalTokens=len(before), originalMethodsPreserved=8, addedGoldenVectors=2, wholeOriginalTokensRecovered=True, placementsVerified=True)

def negative(old, new, mapping):
    expected = inverse(old, new, mapping)
    assert inverse(old, ' '.join(tokens(new)), mapping) == expected
    values = tokens(new)
    pattern = tokens(INSERT)
    at = location(values, pattern)
    substitutions = [('"MCTRSP01"', '"LGSRSP01"'), (', 8, 72,', ', 7, 72,'), (', 8, 72,', ', 8, 71,'),
        (', 72, 1,', ', 72, 0,'), (', 305)', ', 304)'), (', 305)', ', 306)'),
        ('Reason.INVALID_RESPONSE', 'Reason.INVALID_INPUT'), ('f.erased();', '')]
    variants = []
    for old_part, new_part in substitutions:
        assert INSERT.count(old_part) == 1
        block = tokens(INSERT.replace(old_part, new_part, 1))
        variants.append(values[:at] + block + values[at+len(pattern):])
    variants.append(values + [';'])
    changed = list(values)
    changed[changed.index('assertArrayEquals')] = 'assertNotEquals'
    variants.append(changed)
    assert len({tuple(v) for v in variants}) == 10 and all(v != values for v in variants)
    for variant in variants:
        try:
            inverse(old, ' '.join(variant), mapping)
        except AssertionError:
            pass
        else:
            raise AssertionError('changed header boundary/original assertion accepted')
    return len(variants)
