"""Token annotation/method identity plus required token-rejoined positive control before mutations."""
import f03_lgs_boundary_vectors as original
from f03_literal_batch_sources import tokens

baseline = original.baseline

def methods(values):
    return [values[i+3] for i in range(len(values)-3) if values[i:i+3] == ['@','Test','void']]

def inverse(old,new,_mapping):
    before,after = tokens(old),tokens(new)
    assert methods(before) == methods(after) == original.METHODS
    spans = [(original.location(after,tokens(text)),len(tokens(text))) for text in original.INSERTS]
    first = original.location(after,tokens('void web270Requests() {'))
    third = original.location(after,tokens('void web273MalformedReplies() {'))
    fourth = original.location(after,tokens('void web274CapabilitiesAndNull() {'))
    fifth = original.location(after,tokens('void web275TransportFailures() {'))
    assert spans[0][0] < first and spans[1][0] < first
    assert third < spans[2][0] < fourth < spans[3][0] < fifth
    recovered = list(after)
    for at,length in sorted(spans,reverse=True):
        del recovered[at:at+length]
    assert recovered == before
    return dict(originalTokens=len(before),originalMethodsPreserved=8,addedGoldenVectors=2,wholeOriginalTokensRecovered=True,placementsVerified=True)

def negative(old,new,mapping):
    expected = inverse(old,new,mapping)
    assert inverse(old,' '.join(tokens(new)),mapping) == expected
    assert methods(tokens('@Test void x() {}')) == methods(tokens('@ Test void x ( ) { }')) == ['x']
    original.inverse = inverse
    return original.negative(old,new,mapping)
