"""Independent full prior-row preservation and WBS metadata only; no formal acceptance."""
import copy
import json
import g07_host_class_provenance_inputs as data
import f03_lgs_boundary_trace as trace
from pg13584_lgs_boundary_trace import PROOF
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit

OUT = data.BASE/'PG13585-lgs-boundary-trace-post-v1'

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    prior, hashes, raw, snap = trace.inputs()
    proof = data.read_checked(data.BASE/PROOF[0]/'manifest.json', PROOF[1])
    value = json.loads((trace.OUT/'manifest.json').read_bytes())
    expected = trace.expected(prior, hashes, proof, PROOF[1])
    actual = copy.deepcopy(value)
    for key in ['invocation', 'wholeWbsAuditBefore']:
        actual.pop(key, None)
    assert actual == expected
    a, b = trace.documents(value, raw, snap)
    assert (data.ROOT/trace.INV).read_bytes() == a and (data.ROOT/trace.SNAP).read_bytes() == b
    trace.validate_docs(a, b, json.loads(raw), json.loads(snap))
    labels = []
    mutations = [
        ('source', lambda x: x.update(source='0'*40)),
        ('owner', lambda x: next(r for r in x['sourceRows'] if r['path'] == trace.cfg.PATH).update(canonicalCostOwner='WBS-F03')),
        ('old-runtime', lambda x: x['sourceRows'][0].update(unprovenRuntime=True)),
        ('raw', lambda x: x.update(sourceDerivedRaw=6246)),
        ('accepted', lambda x: x.update(newAccepted=1)),
        ('JUnit', lambda x: x['currentQualification'].update(productTestsExecuted=10)),
        ('coverage', lambda x: x['currentQualification'].update(coverageGateExit=0)),
        ('old-domain', lambda x: x['priorRegistryReference'].update(oldRuntimeDomainsReassigned=True)),
    ]
    for label, change in mutations:
        bad = copy.deepcopy(actual)
        change(bad)
        assert bad != actual and bad != expected
        labels.append(label)
    observed = audit()
    assert observed['actualExit'] == 1 and not observed['passed']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json', dict(actualExit=0, source=trace.SOURCE, invocation=invocation,
        traceManifestSha256=data.sha((trace.OUT/'manifest.json').read_bytes()), proofManifestSha256=PROOF[1],
        onlyModifiedSourceHashesChanged=[trace.cfg.PATH], all995OwnersCostsAndHistoricalRuntimePreserved=True,
        metadataNegativeVectors=len(labels), negativeLabels=labels,
        inventorySha256=data.sha(a), snapshotSha256=data.sha(b), wholeWbsAudit=observed,
        sourceDerivedRaw=6247, mainRaw=1491, testRaw=4756, totalPriorCorrections=3194,
        measuredPt=8, newJUnitMethods=0, addedSubvectors=2, coverageGateExit=1,
        newAccepted=0, formalUpdated=False, whole451Accepted=False, effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
