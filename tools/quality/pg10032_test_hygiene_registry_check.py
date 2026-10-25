"""Independent639-hash-only rebind; preserve canonical ownership, old runtime and unknown two."""
import copy
import json
from pathlib import Path
import pg10030_test_hygiene_current_trace as registry
from host_tool_invocation import capture, verify


def contract(value,prior,hashes,proof):
    rows = copy.deepcopy(prior['sourceRows'])
    for row in rows:
        row['sha256'] = hashes[row['path']]
    if value['sourceRows'] != rows or len(rows) != 973:
        raise ValueError('all973 prior fields/cost/owner/runtime unchanged except current SHA')
    if value['source'] != '5012c53265d8d8d789ea2a3edf0b63fa45853a6a':
        raise ValueError('actual committed normal source')
    if value['newTestPaths'] or value['newPathsAdded'] or value['newAccepted'] or value['formalUpdated'] or value['productTestsExecuted']:
        raise ValueError('style trace creates no paths/acceptance/product PT')
    if value['effortPercent'] is not None or value['unregisteredJavaPaths'] != prior['unregisteredJavaPaths']:
        raise ValueError('unknown source ownership and effort remain unresolved')
    if any(value[k] != prior[k] for k in ('currentModifiedLogicalBindings','previousChangedTestBindings')):
        raise ValueError('prior Main and Test history immutable')
    if value['previousTestHygieneChangedTestBindings'] != prior['changedTestBindings']:
        raise ValueError('previous current hash bindings retained in history')
    if (value['registered'],value['javaPaths'],value['registeredTest'],value['totalTest'],value['sourceCount'],value['newLogicalCandidates']) != (1798,1800,833,835,973,965):
        raise ValueError('same measured registration dimensions')
    old = {r['path']:r for r in prior['sourceRows']}
    expected_known = {p for p in proof['changedSourceHashes'] if p in old}
    bounds = value['changedTestBindings']
    if len(bounds) != len(expected_known) != 0 or len(bounds) != 639 or {r['path'] for r in bounds} != expected_known:
        raise ValueError('all639 known changed paths exactly once')
    for row in bounds:
        previous = old[row['path']]
        if (row['previousSha256'],row['currentSha256'],row['canonicalOwner'],row['canonicalCostOwner']) != (
                previous['sha256'],hashes[row['path']],previous['canonicalOwner'],previous['canonicalCostOwner']):
            raise ValueError('canonical cost/owner and before/current hash exact')
        if row['source'] != value['source'] or row['proofSha256'] != '6094f2b3027cdb314f951668c2656fbcb9b2f34c2f59a2dd9779fc146fc701c2' or row['currentSourceRuntimeQualificationInferred'] or row['additionalAllocatedCostPp'] != 0:
            raise ValueError('static source binding cannot infer runtime or allocate a second cost')
    unknown = value['unregisteredCurrentSourceBindings']
    if len(unknown) != 2 or {r['path'] for r in unknown} != set(prior['unregisteredJavaPaths']):
        raise ValueError('two current unknown hashes, not new owned registrations')
    if any(r['canonicalOwner'] != 'UNKNOWN' or r['canonicalCostOwner'] != 'UNKNOWN' or r['currentSha256'] != hashes[r['path']] for r in unknown):
        raise ValueError('no unknown ownership fabrication')


def main():
    invocation = capture(Path(__file__))
    assert not registry.CHECK.exists()
    prior,hashes,_,_ = registry.inputs()
    value = json.loads((registry.OUT/'manifest.json').read_bytes())
    proof = registry.data.read_checked(registry.data.BASE/'PG10026-test-hygiene-normal-post-v1/manifest.json',
        '6094f2b3027cdb314f951668c2656fbcb9b2f34c2f59a2dd9779fc146fc701c2')
    contract(value,prior,hashes,proof)
    negatives = []
    for label,edit in (
        ('prior-owner',lambda v:v['sourceRows'][0].update(canonicalOwner='WBS-G13.07')),
        ('prior-cost',lambda v:v['sourceRows'][0].update(canonicalCostOwner='WBS-G13.07')),
        ('changed-hash',lambda v:v['changedTestBindings'][0].update(currentSha256='0'*64)),
        ('changed-cost',lambda v:v['changedTestBindings'][0].update(canonicalCostOwner='WBS-G13.07')),
        ('unknown-assigned',lambda v:v['unregisteredCurrentSourceBindings'][0].update(canonicalOwner='WBS-G13.07')),
        ('unknown-lost',lambda v:v.update(unregisteredJavaPaths=[])),
        ('runtime-reassigned',lambda v:next(r for r in v['sourceRows'] if 'sourceSpecificRuntimeProof' in r)['sourceSpecificRuntimeProof'].update(source=registry.SOURCE)),
        ('old-bindings-lost',lambda v:v.update(previousTestHygieneChangedTestBindings=[])),
        ('new-path',lambda v:v.update(newPathsAdded=1)),
        ('accepted',lambda v:v.update(newAccepted=1))):
        altered = copy.deepcopy(value)
        edit(altered)
        try:
            contract(altered,prior,hashes,proof)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('invalid current hash binding accepted')
    verify(invocation)
    registry.CHECK.mkdir()
    registry.data.write(registry.CHECK/'manifest.json',dict(actualExit=0,source=registry.SOURCE,invocation=invocation,
        registryManifestSha256=registry.data.sha((registry.OUT/'manifest.json').read_bytes()),
        knownChangedTestHashes=639,unknownChangedTestHashes=2,original973PreservedExceptSha=True,
        negativeMetadataVectors=negatives,registered=1798,total=1800,unknown=2,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,metadataNegatives=len(negatives),
        manifestSha256=registry.data.sha((registry.CHECK/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
