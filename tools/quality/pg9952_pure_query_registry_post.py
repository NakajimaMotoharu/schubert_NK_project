"""Independent old-row preservation, new Test ownership and source-specific PT proof checks."""
import copy
import json
from pathlib import Path

import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9950_pure_query_test_registry as registry

ROOT = data.ROOT
OUT = data.BASE/'PG9952-pure-query-registry-post-v1'
REGISTRY_SHA = '6f3437117368244ae1dca486f4187e750015f90f42ca9ab07556292e2dc59986'


def contract(value,prior,hashes):
    expected = copy.deepcopy(prior['sourceRows'])
    for row in expected:
        if row['path'] in registry.SUBJECT_OWNERS:
            row['sha256'] = hashes[row['path']]
    if value['sourceRows'][:-1] != expected or value['source'] != registry.SOURCE:
        raise ValueError('all prior969 fields/cost preserved except explicit two current hashes')
    if value['currentModifiedLogicalBindings'] != prior['currentModifiedLogicalBindings'] or value['previousChangedTestBindings'] != prior['changedTestBindings']:
        raise ValueError('prior logical/current Test binding history preserved')
    if value['unregisteredJavaPaths'] != prior['unregisteredJavaPaths']:
        raise ValueError('two unknown source files cannot be silently assigned')
    if (value['registered'],value['javaPaths'],value['sourceCount'],value['registeredMain'],value['registeredTest'],value['newLogicalCandidates']) != (1795,1797,970,965,830,962):
        raise ValueError('exact current registration dimensions')
    if value['productTestsExecuted'] != 0 or value['dynamicQualificationInferred'] or value['newAccepted'] or value['formalUpdated'] or value['effortPercent'] is not None:
        raise ValueError('metadata cannot promote PT/formal/effort')
    row = value['sourceRows'][-1]
    if (row['path'] != registry.NEW or row['sha256'] != hashes[registry.NEW] or
        row['owner'] != 'WBS-P010-01' or row['canonicalOwner'] != 'WBS-P010-01' or row['canonicalCostOwner'] != 'WBS-P010-01' or
        row['mainSourceSubjects'] != [registry.MAIN] or row['methodTestIds'] != ['PT-ADM-VAL001','PT-ADM-VAL002','PT-ADM-VAL003','PT-ADM-VAL004'] or
        row['ownerProofSha256'] != registry.PROOF_SHA or row['ownershipStatus'] != 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' or
        row['currentSourcePtQualificationInferred'] or row['historicalRunReassigned'] or row['historicalCostsReallocated']):
        raise ValueError('new explicitly reviewed candidate, not an acceptance or cost change')
    runtime = row['sourceSpecificRuntimeProof']
    if (runtime['source'],runtime['tests'],runtime['suites'],runtime['sha256'],runtime['reassignedToCurrentSource']) != (
        '7cdcf0029cf111d63498ba4de383bbbf494f91a1',4,1,'bfc77cc75a8f7764ad4c64a7955481f3e1cd7f10031c508b6f3e1902271062c3',False):
        raise ValueError('recorded source-specific fourPT is not current execution')
    if len(value['changedTestBindings']) != 2 or {r['path'] for r in value['changedTestBindings']} != set(registry.SUBJECT_OWNERS):
        raise ValueError('two existing hash bindings only')
    old = {r['path']:r for r in prior['sourceRows']}
    for bound in value['changedTestBindings']:
        if (bound['canonicalOwner'] != registry.SUBJECT_OWNERS[bound['path']] or
            bound['canonicalCostOwner'] != registry.SUBJECT_OWNERS[bound['path']] or
            bound['previousSha256'] != old[bound['path']]['sha256'] or bound['currentSha256'] != hashes[bound['path']] or
            bound['staticProofSha256'] != registry.PROOF_SHA or bound['currentSourceRuntimeQualificationInferred']):
            raise ValueError('existing canonical User/Log owner and static-only current hash binding')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG9950-pure-query-test-registry-v1/manifest.json'
    value = data.read_checked(path,REGISTRY_SHA)
    prior = data.read_checked(data.BASE/'PG9916-user-query-changed-test-trace-v1/manifest.json',registry.PRIOR_SHA)
    normal = data.read_checked(data.BASE/'PG9944-log-style-six-compile-v1/manifest.json',
        '9bd924d4baa1720b896451c96eee53c42f885afa213b8bca618ea4c4f9cd262d')
    assert value['actualExit'] == prior['actualExit'] == normal['actualExit'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    contract(value,prior,hashes)
    negatives = []
    for label,edit in (
        ('new-owner',lambda d:d['sourceRows'][-1].update(canonicalOwner='WBS-G13.07')),
        ('new-cost',lambda d:d['sourceRows'][-1].update(canonicalCostOwner='WBS-G13.07')),
        ('new-hash',lambda d:d['sourceRows'][-1].update(sha256='0'*64)),
        ('log-owner-redirect',lambda d:next(r for r in d['sourceRows'] if r['path'].endswith('/LogRequestTest.java')).update(canonicalOwner='WBS-P010-04')),
        ('unknown-lost',lambda d:d.update(unregisteredJavaPaths=[])),
        ('runtime-source-reassigned',lambda d:d['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(source=registry.SOURCE)),
        ('runtime-duplicated-eight',lambda d:d['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(tests=8)),
        ('original-fields-lost',lambda d:d['sourceRows'][0].pop('basis')),
        ('binding-history-lost',lambda d:d['previousChangedTestBindings'].clear()),
        ('accepted',lambda d:d.update(newAccepted=1))):
        changed = copy.deepcopy(value)
        edit(changed)
        try:
            contract(changed,prior,hashes)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('invalid source trace accepted: '+label)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=registry.SOURCE,invocation=invocation,
        registryManifestSha256=REGISTRY_SHA,priorRegistrySha256=registry.PRIOR_SHA,sourceRows=970,newLogicalCandidates=962,
        registered=1795,javaPaths=1797,unknown=2,changedTestBindings=value['changedTestBindings'],
        currentModifiedLogicalBindings=value['currentModifiedLogicalBindings'],newTestPaths=[registry.NEW],
        auditSourceHashes=hashes,wholeWbsAuditBefore=value['wholeWbsAuditBefore'],negativeMetadataVectors=negatives,
        allOriginal969RowsPreservedExceptTwoSha=True,original941AndCostsPreserved=True,
        productTestsExecuted=0,dynamicQualificationInferred=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,metadataNegatives=len(negatives),registered=1795,unknown=2,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
