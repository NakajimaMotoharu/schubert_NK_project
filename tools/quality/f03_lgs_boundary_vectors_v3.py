"""Mutate exact frozen snippets before lexical splitting; positive controls precede all ten negatives."""
import f03_lgs_boundary_vectors as original
from f03_lgs_boundary_vectors_v2 import inverse
from f03_literal_batch_sources import tokens

baseline = original.baseline

def negative(old,new,mapping):
    expected = inverse(old,new,mapping)
    assert inverse(old,' '.join(tokens(new)),mapping) == expected
    assert tokens("' '") != tokens("'\t'") and tokens("' '") != tokens("'\\t'")
    values = tokens(new)
    pattern = tokens(original.INSERTS[2])
    at = original.location(values,pattern)
    snippets = [original.INSERTS[2].replace('113','112',1),original.INSERTS[2].replace('177','176',1),
                original.INSERTS[2].replace("' '","'x'",1),original.INSERTS[2].replace("' '","'\t'",1)]
    variants = [values[:at]+tokens(text)+values[at+len(pattern):] for text in snippets]
    variants.append(values[:at]+values[at+len(pattern):])
    pattern = tokens(original.INSERTS[3])
    at = original.location(values,pattern)
    wrong = tokens(original.INSERTS[3].replace('Reason.INVALID_INPUT','Reason.INVALID_RESPONSE',1))
    variants += [values[:at]+wrong+values[at+len(pattern):],values[:at]+values[at+len(pattern):],values+[';']]
    changed = list(values);changed[changed.index('assertArrayEquals')] = 'assertNotEquals';variants.append(changed)
    changed = list(values);last = max(i for i,value in enumerate(changed) if value == "' '");changed[last] = "'\t'";variants.append(changed)
    assert len({tuple(value) for value in variants}) == len(variants) == 10
    for value in variants:
        assert value != values
        try:
            inverse(old,' '.join(value),mapping)
        except AssertionError:
            pass
        else:
            raise AssertionError('changed boundary/oracle char accepted')
    return len(variants)
