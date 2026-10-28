"""Exact add-only independent boundary source contract; no Product invocation in this helper."""
import re
import g07_host_class_provenance_inputs as data
from f03_literal_batch_sources import tokens,out,prior_normal
from f03_positioned_ascii_literals import baseline
from host_tool_invocation import capture,verify

INSERTS = [
 'import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerRecord;',
 'import dev.codex.schubert.nk.protocol.layout.semantic.SpeakerId;',
 "b -> Arrays.fill(b, 113, 177, (byte) ' '),",
 'rejected(Reason.INVALID_INPUT, () -> f.client.exchange(new TypedPayloadValues(new LayoutId(FIXTURE_LGSREQ01_A99ED320), input().data(), List.of(new SpeakerRecord(new SpeakerId(1), FIXTURE_SYNTHETIC_85DA8434, 1))), CONTEXT));',
]
METHODS = ['web270Requests','web271SuccessProfiles','web272ErrorProfiles','web273MalformedReplies',
           'web274CapabilitiesAndNull','web275TransportFailures','web276ConcurrentRequests','web277OwnershipAndDiagnostics']

def location(values,pattern):
    matches = [i for i in range(len(values)) if values[i:i+len(pattern)] == pattern]
    assert len(matches) == 1
    return matches[0]

def inverse(old,new,_mapping):
    before,after = tokens(old),tokens(new)
    assert re.findall(r'@Test\s+void\s+(\w+)\s*\(',old) == re.findall(r'@Test\s+void\s+(\w+)\s*\(',new) == METHODS
    spans = [(location(after,tokens(text)),len(tokens(text))) for text in INSERTS]
    first = location(after,tokens('void web270Requests() {'))
    third = location(after,tokens('void web273MalformedReplies() {'))
    fourth = location(after,tokens('void web274CapabilitiesAndNull() {'))
    fifth = location(after,tokens('void web275TransportFailures() {'))
    assert spans[0][0] < first and spans[1][0] < first
    assert third < spans[2][0] < fourth < spans[3][0] < fifth
    recovered = list(after)
    for at,length in sorted(spans,reverse=True):
        del recovered[at:at+length]
    assert recovered == before
    return dict(originalTokens=len(before),originalMethodsPreserved=8,addedGoldenVectors=2,wholeOriginalTokensRecovered=True,placementsVerified=True)

def negative(old,new,mapping):
    values = tokens(new)
    at,length = location(values,tokens(INSERTS[2])),len(tokens(INSERTS[2]))
    first = tokens(INSERTS[2])
    mutations = [first[:],first[:],first[:]]
    mutations[0][mutations[0].index('113')] = '112'
    mutations[1][mutations[1].index('177')] = '176'
    mutations[2][mutations[2].index("' '")] = "'x'"
    variants = [values[:at]+part+values[at+length:] for part in mutations]
    variants.append(values[:at]+values[at+length:])
    at,length = location(values,tokens(INSERTS[3])),len(tokens(INSERTS[3]))
    record = tokens(INSERTS[3]);wrong = list(record)
    wrong[wrong.index('INVALID_INPUT')] = 'INVALID_RESPONSE'
    variants += [values[:at]+wrong+values[at+length:],values[:at]+values[at+length:]]
    variants.append(values+[';'])
    changed = list(values);changed[changed.index('assertArrayEquals')] = 'assertNotEquals';variants.append(changed)
    assert len({tuple(value) for value in variants}) == 8
    for value in variants:
        try:
            inverse(old,' '.join(value),mapping)
        except AssertionError:
            pass
        else:
            raise AssertionError('altered golden vector/original assertion accepted')
    return len(variants)

def originals(cfg):
    invocation = capture(__file__)
    target = out(cfg,cfg.ORIGINAL_NUMBER)
    assert not target.exists()
    normal = prior_normal(cfg)
    path = cfg.PATH
    text = (data.ROOT/path).read_text()
    assert data.sha(text.encode()) == cfg.PATHS[path][0] == normal['begin']['inputHashes'][path]
    row = dict(path=path,sha256=data.sha(text.encode()),text=text,mapping=[])
    measured,binding = baseline(cfg,row)
    assert len(measured) == 2 and re.findall(r'@Test\s+void\s+(\w+)\s*\(',text) == METHODS
    row.update(findings=measured,canonicalOwner='WBS-P016-14',canonicalCostOwner='WBS-P016-14',addedVectorIds=cfg.VECTOR_IDS)
    verify(invocation)
    target.mkdir()
    data.write(target/'originals.json',dict(source=cfg.BASE_SOURCE,sources=[row]))
    data.write(target/'manifest.json',dict(actualExit=0,source=cfg.BASE_SOURCE,invocation=invocation,
        originalsSha256=data.sha((target/'originals.json').read_bytes()),sourcePath=path,currentBaseline=binding,
        expectedUnchangedDiagnosticCount=2,originalJUnitMethods=8,plannedAddedSubvectorIds=cfg.VECTOR_IDS,
        productTestsExecuted=0,newAccepted=0,externalActions=0))
    print(data.sha((target/'manifest.json').read_bytes()))
