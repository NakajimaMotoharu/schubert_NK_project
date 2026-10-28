"""Independent exact Main overlay/old domains/two documents/record source and digest binding."""
import copy
import json
import re
import g07_host_class_provenance_inputs as data
import pg13512_main_assignment_trace as stage
from host_tool_invocation import capture, verify
from pg9954_pure_query_registry_metadata import INV,SNAP
from pg9338_wbs_reference_metadata_post import validate as validate_docs
from pg9880_snapshot_nonce_trace import audit

OUT = data.BASE/'PG13513-main-assignment-trace-post-v1'

def validate(value,expected):
    actual = copy.deepcopy(value)
    for key in ['invocation','wholeWbsAuditBefore']:
        actual.pop(key,None)
    assert actual == expected

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    prior,hashes,raw,snap = stage.inputs()
    trace = data.read_checked(stage.OUT/'manifest.json','cf1a2cfb1b7b1033e29afafba51587fde59a05622077cd23dd466c7097423e0d')
    expected = stage.expected(prior,hashes,raw)
    validate(trace,expected)
    actual_raw,actual_snap = (data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    want_raw,want_snap = stage.documents(trace,raw,snap)
    assert actual_raw == want_raw and actual_snap == want_snap
    validate_docs(actual_raw,actual_snap,json.loads(raw),json.loads(snap))
    negatives = []
    for label,change in [
        ('source',lambda v:v.update(source=stage.cfg.BASE_SOURCE)),
        ('main-owner',lambda v:v['modifiedMainBindings'][0].update(canonicalOwner='WBS-G13')),
        ('main-cost',lambda v:v['modifiedMainBindings'][0].update(canonicalCostOwner='WBS-G13')),
        ('old-registry',lambda v:v['sourceRows'][0].update(sha256='0'*64)),
        ('raw',lambda v:v.update(sourceDerivedRaw=6258)),
        ('pending',lambda v:v.update(sourceReboundCurrentWholePending=2481)),
        ('qualification',lambda v:v['currentQualification'].update(productTestsExecuted=1)),
        ('accepted',lambda v:v.update(newAccepted=1))]:
        value = copy.deepcopy(trace)
        change(value)
        try:
            validate(value,expected)
        except AssertionError:
            negatives.append(label)
        else:
            raise AssertionError('fabricated Main ownership or qualification accepted')
    record = data.ROOT/stage.cfg.RECORD
    assert record.is_file() and stage.SOURCE in record.read_text()
    rows = re.findall(r'\| (PG\S+) \| ([a-f0-9]{64}) \|',record.read_text())
    assert len(rows) == len({name for name,_ in rows}) == 7
    for name,pin in rows:
        value = data.read_checked(data.BASE/name/'manifest.json',pin)
        assert value['actualExit'] == 0
    observed = audit()
    assert observed['actualExit'] == 1 and not observed['passed']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=stage.SOURCE,invocation=invocation,
        traceManifestSha256='cf1a2cfb1b7b1033e29afafba51587fde59a05622077cd23dd466c7097423e0d',
        inventorySha256=data.sha(actual_raw),snapshotSha256=data.sha(actual_snap),record=stage.cfg.RECORD,
        recordSha256=data.sha(record.read_bytes()),recordLinkedManifests=7,metadataNegativeVectors=len(negatives),negativeLabels=negatives,
        mainSources=4,all995OldRegistryRowsAndRuntimeUnchanged=True,original941And943AndBudgetAndAcceptanceUnchanged=True,
        sourceDerivedRaw=6251,mainRaw=1495,testRaw=4756,corrections=3190,currentWholePending=2483,
        productTestsExecuted=0,newAccepted=0,wholeWbsAudit=observed,whole451Accepted=False,formalUpdated=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
