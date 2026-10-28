"""Token-granular independent invalid rewrites; never treat ++ as a single lexer token."""
import f03_main_assignment_sources as original
from f03_literal_batch_sources import tokens

inverse = original.inverse
baseline = original.baseline

def negative(old,new,mapping):
    kind = mapping[0]['kind']
    after = tokens(new)
    pattern = tokens(original.NEW[kind])
    locations = [i for i in range(len(after)) if after[i:i+len(pattern)] == pattern]
    assert len(locations) == len(mapping)
    at = locations[0]
    if kind == 'INDEX':
        wrong = ['int ownedPosition=count;count--;descriptors[ownedPosition]=descriptor;',
                 'int ownedPosition=count;count++;descriptors[count]=descriptor;',
                 'int ownedPosition=count;descriptors[ownedPosition]=descriptor;count++;',
                 'int ownedPosition=count;descriptors[ownedPosition]=descriptor;']
    else:
        wrong = ['count--;if(count>MAXIMUM_SOCKET_DIRECTORY_ENTRIES)',
                 'count++;if(count>=MAXIMUM_SOCKET_DIRECTORY_ENTRIES)',
                 'if(count>MAXIMUM_SOCKET_DIRECTORY_ENTRIES)count++;',
                 'if(count>MAXIMUM_SOCKET_DIRECTORY_ENTRIES)']
    variants = [after[:at]+tokens(part)+after[at+len(pattern):] for part in wrong]+[after+[';']]
    assert len({tuple(value) for value in variants}) == len(variants) == 5
    for value in variants:
        assert value != after
        try:
            inverse(old,' '.join(value),mapping)
        except AssertionError:
            pass
        else:
            raise AssertionError('non-equivalent count/index/order/guard accepted')
    return len(variants)

def originals(cfg):
    original.negative = negative
    original.originals(cfg)
