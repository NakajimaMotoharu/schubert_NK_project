"""Independent literal one-Test ownership/runtime registry checks; no product invocation."""
import copy
import json
from pathlib import Path
import pg10052_user_sql_trace as registry
from host_tool_invocation import capture, verify


def contract(value, prior, hashes):
    if len(value['sourceRows']) != 974 or value['sourceRows'][:-1] != prior['sourceRows']:
        raise ValueError('all prior973 fields and historical runtime proofs unchanged')
    row = value['sourceRows'][-1]
    path = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/UserQuerySqlContractTest.java'
    if row['path'] != path or row['sha256'] != hashes[path]:
        raise ValueError('one exact source hash')
    if [row[k] for k in ('owner','canonicalOwner','canonicalCostOwner')] != ['WBS-P010-01']*3:
        raise ValueError('original User owner/cost')
    if row['methodTestIds'] != [f'PT-ADM-SQL{i:03d}' for i in range(1,9)]:
        raise ValueError('eight independent new Test IDs')
    runtime = row['sourceSpecificRuntimeProof']
    if (runtime['source'],runtime['tests'],runtime['suites'],runtime['newTestIds'],runtime['programMethodCount']) != (registry.SOURCE,16,3,8,8):
        raise ValueError('new8 plus related8 not sixteen new')
    if not runtime['sharedRunReferenceNotAdditive'] or runtime['reassignedToCurrentSource']:
        raise ValueError('one measured source/run, no reassignment')
    if runtime['sha256'] != 'a7d6c23e71cc2da5463bba8d88a64a9188ad47c859badfb098aab287882daf4c':
        raise ValueError('genuine same-source XML/CRC measurement')
    if (value['registered'],value['javaPaths'],value['registeredTest'],value['totalTest']) != (1799,1801,834,836):
        raise ValueError('current dimensions')
    for key in ('unregisteredJavaPaths','unregisteredCurrentSourceBindings','changedTestBindings',
                'previousChangedTestBindings','currentModifiedLogicalBindings'):
        if value[key] != prior[key]:
            raise ValueError('unknown/history preserved')
    if value['newAccepted'] or value['formalUpdated'] or value['effortPercent'] is not None or value['productTestsExecuted']:
        raise ValueError('metadata not acceptance or runtime')


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
        ('source-hash',lambda v:v['sourceRows'][-1].update(sha256='0'*64)),
        ('ids',lambda v:v['sourceRows'][-1].update(methodTestIds=[])),
        ('new-count',lambda v:v['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(newTestIds=16)),
        ('source',lambda v:v['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(source='0'*40)),
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
        metadataNegativeVectors=negatives,registered=1799,total=1801,unknown=2,
        original973AllFieldsPreserved=True,productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,metadataNegatives=len(negatives),
        manifestSha256=registry.data.sha((registry.CHECK/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
