"""Literal three-row delta and new-vs-historical runtime proof contract; no product execution."""
import copy
import json
from pathlib import Path
import pg10112_query_projection_trace as registry
from host_tool_invocation import capture, verify

SUBJECTS = {
    'admin/UserQuerySqlContractTest.java':('WBS-P010-01','ADM',9,17),
    'log/LogSqlContractTest.java':('WBS-P018-09','LOG',9,17),
    'question/QuestionSqlContractTest.java':('WBS-P013-01','QRY',10,18)}


def contract(value, prior, hashes):
    rows = {r['path']:r for r in value['sourceRows']}
    old = {r['path']:r for r in prior['sourceRows']}
    if set(rows) != set(old) or len(rows) != 976:
        raise ValueError('same976 source paths')
    changes = {r['path']:r for r in value['changedTestBindings']}
    expected_paths = {registry.TEST_PREFIX+p for p in SUBJECTS}
    if set(changes) != expected_paths:
        raise ValueError('only three changed bindings')
    for path,row in rows.items():
        if path not in expected_paths:
            if row != old[path]: raise ValueError('other973 rows immutable')
            continue
        owner,tag,count,program = SUBJECTS[path.removeprefix(registry.TEST_PREFIX)]
        if row['sha256'] != hashes[path] or row['methodTestIds'] != [f'PT-{tag}-SQL{i:03d}' for i in range(1,count+1)]:
            raise ValueError('current hash plus appended IDs')
        current = row['currentSourceRuntimeProof']
        if (current['source'],current['tests'],current['suites'],current['groupNewTestIds'],
            current['newProgramTestIds'],current['programSqlMethodCount'],current['programAllMethodCount']) != (registry.SOURCE,52,7,4,count-8,count,program):
            raise ValueError('explicit current52 proof, four new total')
        if current['sha256'] != 'b83f269bd2f8573e5e9f10341ad4fc96d6b0a93589e98d0c11e66467c00f0b2d' or current['historicalProofReassigned'] or not current['sharedRunReferenceNotAdditive']:
            raise ValueError('genuine run, no historical reassignment')
        restored = copy.deepcopy(row)
        del restored['currentSourceRuntimeProof'],restored['currentIndependentSpec']
        restored['sha256'] = old[path]['sha256']
        restored['methodTestIds'] = restored['methodTestIds'][:8]
        if restored != old[path] or row['canonicalOwner'] != owner or row['canonicalCostOwner'] != owner:
            raise ValueError('all other fields/owners/costs/historical proof immutable')
    if value['previousCurrentChangedTestBindingsReference'] != dict(
        manifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG10088-query-sql-batch-trace-v1/manifest.json',
        sha256='3b6d5b8d2d4ac20a54d89faeddea478ae2bfedcd749eb5166859dd536bb45ffe',
        arrayPath='changedTestBindings',count=639):
        raise ValueError('previous639 retained by immutable full manifest reference')
    if any(value[k] != prior[k] for k in ('unregisteredJavaPaths','unregisteredCurrentSourceBindings',
        'previousChangedTestBindings','currentModifiedLogicalBindings')):
        raise ValueError('unknown two/history bindings unchanged')
    if (value['registered'],value['javaPaths'],value['registeredTest'],value['totalTest'],value['newPathsAdded'],value['newMethodIds']) != (1801,1803,836,838,0,4):
        raise ValueError('current dimensions unchanged, four methods not paths')
    if value['newAccepted'] or value['formalUpdated'] or value['effortPercent'] is not None or value['productTestsExecuted']:
        raise ValueError('metadata not runtime/acceptance')


def main():
    invocation = capture(Path(__file__))
    assert not registry.CHECK.exists()
    prior,hashes,_,_ = registry.inputs()
    value = json.loads((registry.OUT/'manifest.json').read_bytes())
    contract(value,prior,hashes)
    indices = [i for i,r in enumerate(value['sourceRows']) if r['path'].endswith('/QuestionSqlContractTest.java')]
    assert len(indices) == 1
    index = indices[0]
    negatives = []
    for label,edit in (
        ('other-owner',lambda v:v['sourceRows'][0].update(canonicalOwner='WBS-G13.07')),
        ('cost',lambda v:v['sourceRows'][index].update(canonicalCostOwner='WBS-G13.07')),
        ('hash',lambda v:v['sourceRows'][index].update(sha256='0'*64)),
        ('ids',lambda v:v['sourceRows'][index].update(methodTestIds=[])),
        ('current-source',lambda v:v['sourceRows'][index]['currentSourceRuntimeProof'].update(source='0'*40)),
        ('current-count',lambda v:v['sourceRows'][index]['currentSourceRuntimeProof'].update(groupNewTestIds=52)),
        ('historical-source',lambda v:v['sourceRows'][index]['sourceSpecificRuntimeProof'].update(source=registry.SOURCE)),
        ('old639',lambda v:v['previousCurrentChangedTestBindingsReference'].update(count=0)),
        ('unknown',lambda v:v.update(unregisteredJavaPaths=[])),
        ('paths',lambda v:v.update(newPathsAdded=4)),
        ('accepted',lambda v:v.update(newAccepted=1))):
        changed = copy.deepcopy(value)
        edit(changed)
        try: contract(changed,prior,hashes)
        except ValueError: negatives.append(label)
        else: raise AssertionError('invalid registry accepted')
    verify(invocation)
    registry.CHECK.mkdir()
    registry.data.write(registry.CHECK/'manifest.json',dict(actualExit=0,source=registry.SOURCE,invocation=invocation,
        registryManifestSha256=registry.data.sha((registry.OUT/'manifest.json').read_bytes()),
        metadataNegativeVectors=negatives,registered=1801,total=1803,unknown=2,
        other973RowsUnchanged=True,originalHistoricalRuntimeProofsUnchanged=True,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,metadataNegatives=len(negatives),
        manifestSha256=registry.data.sha((registry.CHECK/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
