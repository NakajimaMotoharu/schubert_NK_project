"""Independent full-row owner/hash comparison for two changed Test bindings, not dynamic qualification."""
import copy
from pathlib import Path
import json

import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9916_user_query_changed_test_trace as registry

ROOT = data.ROOT
OUT = data.BASE/'PG9918-user-query-trace-post-v1'
REGISTRY_SHA = '42899a03f8ddd657805f55c053cfb0f64616356c2ff889a912c8d77505303b0b'


def contract(value, prior, hashes):
    expected = copy.deepcopy(prior['sourceRows'])
    for row in expected:
        if row['path'] in registry.SUBJECTS:
            row['sha256'] = hashes[row['path']]
    if value['source'] != registry.SOURCE or value['sourceRows'] != expected:
        raise ValueError('exact prior rows with only two current hashes changed')
    if value['currentModifiedLogicalBindings'] != prior['currentModifiedLogicalBindings']:
        raise ValueError('historical Main binding loss or reassignment')
    if value['unregisteredJavaPaths'] != prior['unregisteredJavaPaths']:
        raise ValueError('two unknown files must remain unknown')
    if (value['registered'],value['javaPaths'],value['sourceCount'],value['registeredMain'],value['registeredTest']) != (1794,1796,969,965,829):
        raise ValueError('exact current physical registration dimensions')
    if value['productTestsExecuted'] != 0 or value['dynamicQualificationInferred'] or value['newAccepted'] or value['formalUpdated'] or value['effortPercent'] is not None:
        raise ValueError('metadata cannot promote dynamic/formal/effort')
    if len(value['changedTestBindings']) != 2 or {r['path'] for r in value['changedTestBindings']} != registry.SUBJECTS:
        raise ValueError('two existing Test paths only')
    old_rows = {r['path']:r for r in prior['sourceRows']}
    for row in value['changedTestBindings']:
        if (row['currentSha256'] != hashes[row['path']] or row['previousSha256'] != old_rows[row['path']]['sha256'] or
            row['canonicalOwner'] != 'WBS-P010-01' or row['canonicalCostOwner'] != 'WBS-P010-01' or
            row['staticProofSha256'] != registry.PROOF_SHA or row['previousRegistrySha256'] != registry.PRIOR_SHA or
            row['source'] != registry.SOURCE or row['dynamicQualificationStatus'] != 'NOT_EXECUTED_DB_DEPENDENCY_HOLD' or
            row['oldDynamicSuccessTransferred'] or row['additionalAllocatedCostPp'] != 0):
            raise ValueError('exact original owner/cost/history and current static-only evidence')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG9916-user-query-changed-test-trace-v1/manifest.json'
    value = data.read_checked(path,REGISTRY_SHA)
    prior = data.read_checked(data.BASE/'PG9880-snapshot-nonce-trace-v1/manifest.json',registry.PRIOR_SHA)
    normal = data.read_checked(data.BASE/'PG9908-user-query-fixture-six-compile-v1/manifest.json',
        '82fa21a02cbd438e29d63a5260e206d71bf7c9df864448146866af5d73c91e34')
    assert value['actualExit'] == prior['actualExit'] == normal['actualExit'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    contract(value,prior,hashes)
    negatives = []
    for label,edit in (
        ('owner',lambda d:d['changedTestBindings'][0].update(canonicalOwner='WBS-G13.07')),
        ('cost',lambda d:d['changedTestBindings'][0].update(canonicalCostOwner='WBS-G13.07')),
        ('hash',lambda d:d['changedTestBindings'][0].update(currentSha256='0'*64)),
        ('history',lambda d:d['changedTestBindings'][0].update(previousSha256='0'*64)),
        ('proof',lambda d:d['changedTestBindings'][0].update(staticProofSha256='0'*64)),
        ('row-corruption',lambda d:d['sourceRows'][0].update(owner='WBS-G13.07')),
        ('unknown-lost',lambda d:d.update(unregisteredJavaPaths=[])),
        ('old-binding-lost',lambda d:d['currentModifiedLogicalBindings'].pop()),
        ('dynamic-promotion',lambda d:d.update(dynamicQualificationInferred=True)),
        ('acceptance',lambda d:d.update(newAccepted=1))):
        changed = copy.deepcopy(value)
        edit(changed)
        try:
            contract(changed,prior,hashes)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('invalid trace metadata accepted: '+label)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=registry.SOURCE,invocation=invocation,registryManifestSha256=REGISTRY_SHA,
        previousRegistrySha256=registry.PRIOR_SHA,sourceRows=969,registered=1794,javaPaths=1796,unknown=2,
        auditSourceHashes=hashes,wholeWbsAuditBefore=value['wholeWbsAuditBefore'],negativeMetadataVectors=negatives,
        changedTestBindings=value['changedTestBindings'],currentModifiedLogicalBindings=value['currentModifiedLogicalBindings'],
        productTestsExecuted=0,dynamicQualificationInferred=False,canonicalOwnersAndCostsPreserved=True,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,metadataNegatives=len(negatives),registered=1794,unknown=2,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
