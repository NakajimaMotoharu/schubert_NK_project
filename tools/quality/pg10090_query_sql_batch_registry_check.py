"""Independent two-path trace/cost and different-source runtime contracts; metadata only."""
import copy
import json
from pathlib import Path
import pg10088_query_sql_batch_trace as registry
from host_tool_invocation import capture, verify


def contract(value, prior, hashes):
    if len(value['sourceRows']) != 976 or value['sourceRows'][:-2] != prior['sourceRows']:
        raise ValueError('all prior974 fields immutable')
    expected = {
        'log/LogSqlContractTest.java':('WBS-P018-09','LOG','6cd6ae7efc495f17e1ebb79291f26c7a90f99dc7',
            'f909af4a8703b53aeef2903f23968393a88cfbff0efb713e231d90338f7ba8b2'),
        'question/QuestionSqlContractTest.java':('WBS-P013-01','QRY','9eac6bffd8462aea5d0d0759cb14fdef5b1a1a3e',
            'c3c001763eb2794795447ea287333eea752b0fa1162d967a26ec9e54137eb907')}
    rows = {r['path'].removeprefix(registry.TEST_PREFIX):r for r in value['sourceRows'][-2:]}
    if set(rows) != set(expected):
        raise ValueError('two exact new Test paths')
    for path,(owner,tag,source,sha) in expected.items():
        row = rows[path]
        if row['sha256'] != hashes[row['path']] or [row[k] for k in ('owner','canonicalOwner','canonicalCostOwner')] != [owner]*3:
            raise ValueError('original owner/cost and current hash')
        if row['methodTestIds'] != [f'PT-{tag}-SQL{i:03d}' for i in range(1,9)]:
            raise ValueError('eight independent IDs per program')
        runtime = row['sourceSpecificRuntimeProof']
        if (runtime['source'],runtime['tests'],runtime['suites'],runtime['newTestIds'],runtime['programMethodCount'],runtime['sha256']) != (source,16,2,8,8,sha):
            raise ValueError('Log6cd and Question9eac, not all same-source qualified')
        if not runtime['sharedRunReferenceNotAdditive'] or runtime['reassignedToCurrentSource']:
            raise ValueError('new8 plus regression8 nonadditive, no reassignment')
    if (value['registered'],value['javaPaths'],value['registeredTest'],value['totalTest']) != (1801,1803,836,838):
        raise ValueError('literal current measurements')
    for key in ('unregisteredJavaPaths','unregisteredCurrentSourceBindings','changedTestBindings',
                'previousChangedTestBindings','currentModifiedLogicalBindings'):
        if value[key] != prior[key]:
            raise ValueError('unknown/history immutable')
    if value['newAccepted'] or value['formalUpdated'] or value['effortPercent'] is not None or value['productTestsExecuted']:
        raise ValueError('metadata not product execution or acceptance')


def main():
    invocation = capture(Path(__file__))
    assert not registry.CHECK.exists()
    prior,hashes,_,_ = registry.inputs()
    value = json.loads((registry.OUT/'manifest.json').read_bytes())
    contract(value,prior,hashes)
    negatives = []
    for label,edit in (
        ('old-owner',lambda v:v['sourceRows'][0].update(canonicalOwner='WBS-G13.07')),
        ('new-cost',lambda v:v['sourceRows'][-1].update(canonicalCostOwner='WBS-G13.07')),
        ('log-cost',lambda v:v['sourceRows'][-2].update(canonicalCostOwner='WBS-P010-04')),
        ('hash',lambda v:v['sourceRows'][-1].update(sha256='0'*64)),
        ('ids',lambda v:v['sourceRows'][-1].update(methodTestIds=[])),
        ('new-count',lambda v:v['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(newTestIds=16)),
        ('log-source-reassigned',lambda v:v['sourceRows'][-2]['sourceSpecificRuntimeProof'].update(source=registry.SOURCE)),
        ('unknown',lambda v:v.update(unregisteredJavaPaths=[])),
        ('history',lambda v:v.update(changedTestBindings=[])),
        ('accepted',lambda v:v.update(newAccepted=1))):
        changed = copy.deepcopy(value)
        edit(changed)
        try:
            contract(changed,prior,hashes)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('invalid registry accepted')
    verify(invocation)
    registry.CHECK.mkdir()
    registry.data.write(registry.CHECK/'manifest.json',dict(actualExit=0,source=registry.SOURCE,invocation=invocation,
        registryManifestSha256=registry.data.sha((registry.OUT/'manifest.json').read_bytes()),
        metadataNegativeVectors=negatives,registered=1801,total=1803,unknown=2,
        original974AllFieldsPreserved=True,productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,metadataNegatives=len(negatives),
        manifestSha256=registry.data.sha((registry.CHECK/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
