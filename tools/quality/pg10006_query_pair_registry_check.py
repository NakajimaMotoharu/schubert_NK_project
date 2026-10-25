"""Independent prior-row and one new logical Test trace contract; no product execution."""
import copy
import json
from pathlib import Path
import pg10004_query_pair_trace as registry
from host_tool_invocation import capture, verify


def contract(value, prior, hashes):
    if value['sourceRows'][:-2] != prior['sourceRows'] or len(value['sourceRows']) != 973:
        raise ValueError('all prior971 rows/owners/costs/runtime evidence unchanged')
    expected = {
        'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionQueryPlainContractTest.java':('WBS-P013-01','QRY'),
        'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/log/LogPlainContractTest.java':('WBS-P018-09','LOG')}
    rows = {r['path']:r for r in value['sourceRows'][-2:]}
    if set(rows) != set(expected):
        raise ValueError('two literal new source paths only')
    for path,(owner,tag) in expected.items():
        row = rows[path]
        if row['sha256'] != hashes[path] or [row[k] for k in ('owner','canonicalOwner','canonicalCostOwner')] != [owner]*3:
            raise ValueError('original Main canonical owner/cost and current bytes')
        if row['methodTestIds'] != [f'PT-{tag}-PLAIN{i:03d}' for i in range(1,9)]:
            raise ValueError('eight Test IDs per program')
        runtime = row['sourceSpecificRuntimeProof']
        if (runtime['source'],runtime['tests'],runtime['suites'],runtime['newTestIds'],runtime['programMethodCount']) != (registry.SOURCE,16,2,16,8):
            raise ValueError('shared16 executions, eight per program, never32')
        if not runtime['sharedRunReferenceNotAdditive'] or runtime['sha256'] != '9cc448696e53581d68239ac67cb22ae25a019c2a41d04ebaf2ec9b0f15bfa9d8':
            raise ValueError('actual independent shared runtime proof')
    if (value['registered'],value['javaPaths'],value['registeredTest'],value['totalTest']) != (1798,1800,833,835):
        raise ValueError('literal measured current dimensions')
    if value['unregisteredJavaPaths'] != prior['unregisteredJavaPaths']:
        raise ValueError('unknown two preserved')
    if any(value[k] != prior[k] for k in ('changedTestBindings','previousChangedTestBindings','currentModifiedLogicalBindings')):
        raise ValueError('history binding preserved')
    if value['newAccepted'] or value['formalUpdated'] or value['effortPercent'] is not None or value['productTestsExecuted']:
        raise ValueError('metadata is not runtime or acceptance')


def main():
    invocation = capture(Path(__file__))
    assert not registry.CHECK.exists()
    prior,hashes,_,_ = registry.inputs()
    value = json.loads((registry.OUT/'manifest.json').read_bytes())
    contract(value,prior,hashes)
    negatives = []
    for label,edit in (
        ('prior-owner',lambda v:v['sourceRows'][0].update(canonicalOwner='WBS-G13.07')),
        ('new-cost',lambda v:v['sourceRows'][-1].update(canonicalCostOwner='WBS-G13.07')),
        ('hash',lambda v:v['sourceRows'][-1].update(sha256='0'*64)),
        ('unknown',lambda v:v.update(unregisteredJavaPaths=[])),
        ('runtime-newids',lambda v:v['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(newTestIds=32)),
        ('question-cost',lambda v:v['sourceRows'][-2].update(canonicalCostOwner='WBS-P018-09')),
        ('shared-run-count',lambda v:v['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(sharedRunReferenceNotAdditive=False)),
        ('runtime-source',lambda v:v['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(source='0'*40)),
        ('accepted',lambda v:v.update(newAccepted=1))):
        altered = copy.deepcopy(value)
        edit(altered)
        try:
            contract(altered,prior,hashes)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('invalid registry accepted')
    verify(invocation)
    registry.CHECK.mkdir()
    registry.data.write(registry.CHECK/'manifest.json',dict(actualExit=0,source=registry.SOURCE,invocation=invocation,
        registryManifestSha256=registry.data.sha((registry.OUT/'manifest.json').read_bytes()),
        metadataNegativeVectors=negatives,registered=1798,total=1800,unknown=2,
        original971AllFieldsPreserved=True,productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,metadataNegatives=len(negatives),
        manifestSha256=registry.data.sha((registry.CHECK/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
