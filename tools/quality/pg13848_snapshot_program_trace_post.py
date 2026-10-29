"""Independently verify exact one-hash WBS overlay and retained global audit HOLD."""
import copy
import json
import f03_snapshot_program_trace as trace
from host_tool_invocation import capture, verify
from pg9880_snapshot_nonce_trace import audit

data = trace.data
OUT = data.BASE/'PG13848-snapshot-program-trace-post-v1'

def strict(a,b):
    assert json.dumps(a,sort_keys=True) == json.dumps(b,sort_keys=True)

def main():
    invocation = capture(__file__);assert not OUT.exists()
    prior,hashes,proof,raw,snap = trace.inputs()
    value = json.loads((trace.OUT/'manifest.json').read_bytes());actual = copy.deepcopy(value)
    for key in ['invocation','wholeWbsAuditBefore']:actual.pop(key,None)
    expected = trace.expected(prior,hashes,proof);strict(actual,expected)
    a,b = trace.documents(value,raw,snap)
    assert (data.ROOT/trace.INV).read_bytes() == a and (data.ROOT/trace.SNAP).read_bytes() == b
    trace.validate_docs(a,b,json.loads(raw),json.loads(snap));labels = []
    for label,change in [('source',lambda x:x.update(source='0'*40)),('owner',lambda x:next(r for r in x['sourceRows'] if r['path'] == trace.PATH).update(canonicalCostOwner='WBS-F03')),
        ('old-runtime',lambda x:x['sourceRows'][0].update(unprovenRuntime=True)),('raw',lambda x:x.update(sourceDerivedRaw=6246)),('accepted',lambda x:x.update(newAccepted=1)),
        ('new-test',lambda x:x['currentQualification'].update(junitMethodsAdded=23)),('coverage',lambda x:x['currentQualification'].update(coverageGateExit=1)),
        ('old-domain',lambda x:x['priorRegistryReference'].update(oldRuntimeDomainsReassigned=True))]:
        bad = copy.deepcopy(actual);change(bad)
        try:strict(bad,expected)
        except AssertionError:labels.append(label)
        else:raise AssertionError('incorrect trace qualification accepted')
    observed = audit();assert observed['actualExit'] == 1 and not observed['passed']
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=trace.SOURCE,invocation=invocation,traceManifestSha256=data.sha((trace.OUT/'manifest.json').read_bytes()),
        proofManifestSha256=trace.PROOF[1],onlyModifiedSourceHashesChanged=[trace.PATH],all995OwnersCostsAndHistoricalRuntimePreserved=True,
        metadataNegativeVectors=len(labels),negativeLabels=labels,inventorySha256=data.sha(a),snapshotSha256=data.sha(b),wholeWbsAudit=observed,
        sourceDerivedRaw=6247,mainRaw=1491,testRaw=4756,totalPriorCorrections=3194,measuredPt=23,newJUnitMethods=1,coverageGateExit=0,
        newAccepted=0,formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
