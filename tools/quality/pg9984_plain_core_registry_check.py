"""Independent prior-row and one new logical Test trace contract; no product execution."""
import copy
import json
from pathlib import Path
import pg9982_plain_core_trace as registry
from host_tool_invocation import capture, verify


def contract(value, prior, hashes):
    if value['sourceRows'][:-1] != prior['sourceRows'] or len(value['sourceRows']) != 971:
        raise ValueError('all prior970 rows/owners/costs/runtime evidence unchanged')
    row = value['sourceRows'][-1]
    if row['path'] != registry.NEW or row['sha256'] != hashes[registry.NEW]:
        raise ValueError('literal new path and current source bytes')
    if [row[k] for k in ('owner','canonicalOwner','canonicalCostOwner')] != ['WBS-P010-01']*3:
        raise ValueError('original Main canonical owner and cost, not change owner')
    if row['methodTestIds'] != ['PT-ADM-CORE001','PT-ADM-CORE002','PT-ADM-CORE003','PT-ADM-CORE004']:
        raise ValueError('exact four new Test IDs')
    if (value['registered'],value['javaPaths'],value['registeredTest'],value['totalTest']) != (1796,1798,831,833):
        raise ValueError('literal measured current dimensions')
    if value['unregisteredJavaPaths'] != prior['unregisteredJavaPaths']:
        raise ValueError('unknown two preserved')
    runtime = row['sourceSpecificRuntimeProof']
    if (runtime['source'],runtime['tests'],runtime['suites'],runtime['newTestIds'],runtime['relatedRegressionMethods']) != (registry.SOURCE,8,2,4,4):
        raise ValueError('eight current executions are only four new IDs')
    if runtime['sha256'] != '7e37b3f71ef9716661798c908ec231c45a2883cbe0e97df55dbbee13c1a7fe5b':
        raise ValueError('actual independent current runtime proof')
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
        ('runtime-newids',lambda v:v['sourceRows'][-1]['sourceSpecificRuntimeProof'].update(newTestIds=8)),
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
        metadataNegativeVectors=negatives,registered=1796,total=1798,unknown=2,
        original970AllFieldsPreserved=True,productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,metadataNegatives=len(negatives),
        manifestSha256=registry.data.sha((registry.CHECK/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
