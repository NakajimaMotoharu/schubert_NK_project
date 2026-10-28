"""Exact Main source overlay, preserving all original owner/cost/acceptance and historical Test domains."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
import pg13530_main_assignment_final_config as cfg
from f03_literal_batch_sources import original_value
from host_tool_invocation import capture, verify
from trace_owner_join import canonical
from pg9954_pure_query_registry_metadata import INV, SNAP, replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs
from pg9880_snapshot_nonce_trace import audit

SOURCE = 'a90e303fc59938d413c2d777380bdffbe3e7f9e7'
OUT = data.BASE/'PG13542-main-assignment-final-four-v1'
KEY = 'mainAssignmentFinalFourPG13542Overlay'
PRIOR = ('PG13512-main-assignment-seven-v1','cf1a2cfb1b7b1033e29afafba51587fde59a05622077cd23dd466c7097423e0d')

def state_after():
    ids,refs,pending = cfg.previous_state()
    original = original_value(cfg)
    removed = {row['id'] for item in original['sources'] for row in item['mapping']}
    retained = {row['id'] for item in original['sources'] for row in item['findings']}-removed
    assert len(removed) == 4 and removed <= ids-refs and len(ids) == 6251
    return ids-removed,refs,pending|(retained&refs)

def inputs():
    prior = data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1])
    normal = data.read_checked(data.BASE/'PG13536-main-assignment-final-four-v1/manifest.json','12e04040d67762a748e6d7f9898604ee38717c75eb6a15fb92a762391d963a48')
    proof = data.read_checked(data.BASE/'PG13540-main-assignment-final-four-v1/manifest.json','fb6cdd2125378a0027eff333a1a6c180235a9cb5e685608e3dee6d0225e8f804')
    assert normal['source'] == proof['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == proof['actualExit'] == proof['productTestsExecuted'] == 0
    assert proof['allTestPhysicalBytesUnchanged'] and proof['changedMainPhysical'] == 6 and proof['allClosureMembersUnchanged']
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/path).read_bytes()) == pin for path,pin in hashes.items())
    assert len(prior['sourceRows']) == 995 and all(hashes[row['path']] == row['sha256'] for row in prior['sourceRows'])
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+path],cwd=data.ROOT) for path in [INV,SNAP]]
    return prior,hashes,raw,snap

def expected(prior,hashes,raw):
    logical = {row['path']:row for row in json.loads(raw)['artifacts']}
    bindings = []
    for path,(_,ids,owner,_) in cfg.PATHS.items():
        ownership = canonical(path,logical)
        assert ownership['canonicalOwner'] == ownership['canonicalCostOwner'] == owner
        bindings.append(dict(path=path,sha256=hashes[path],originalDiagnosticIds=ids,**ownership))
    value = copy.deepcopy(prior)
    for key in ['invocation','wholeWbsAuditBefore','futureLiteralTraceMustPreserveMainRaw1495']:
        value.pop(key,None)
    ids,refs,pending = state_after()
    value.update(source=SOURCE,modifiedTestPaths=[],modifiedMainPaths=sorted(cfg.PATHS),modifiedMainBindings=bindings,
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=prior['source'],oldRuntimeDomainsReassigned=False),
        currentQualification=dict(source=SOURCE,status='PG_STATIC_MAIN_STATEMENT_CHANGE_NOT_PT_QUALIFIED',
            proofManifestSha256='fb6cdd2125378a0027eff333a1a6c180235a9cb5e685608e3dee6d0225e8f804',
            productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',measuredProductCounters=None,
            changedMainPhysical=6,unchangedMainPhysical=1837,allMainPhysical=1843,currentTestPhysical=1978,
            allTestPhysicalBytesUnchanged=True,oldPtQualificationTransferred=False),
        sourceDerivedRaw=len(ids),mainRaw=1491,testRaw=4756,totalPriorCorrections=3194,
        joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        rawDeltaBasis='Exact4 original Main assignment diagnostics removed; other current diagnostics retained; no global replay',
        record=cfg.RECORD,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False,
        futureLiteralTraceMustPreserveMainRaw1491=True,all995RegistryRowsAndOldRuntimePreserved=True)
    assert value['sourceRows'] == prior['sourceRows'] and len(ids) == 6247 and len(pending) == 2488
    return value

def documents(value,raw,snap):
    current = json.loads(raw)
    overlay = dict(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),
        record=cfg.RECORD,currentMainBindings=value['modifiedMainBindings'],qualification=value['currentQualification'],
        sourceDerivedRaw=6247,mainRaw=1491,testRaw=4756,totalPriorCorrections=3194,sourceReboundCurrentWholePending=2488,
        all995OldRegistryRowsPreserved=True,newAccepted=0,formalUpdated=False)
    result = raw
    for name in ['currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership']:
        section = current[name]
        assert KEY not in section
        section[KEY] = copy.deepcopy(overlay)
        result,_,_ = replaced(result,name,section)
    new_snap,_,_ = replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,new_snap,json.loads(raw),json.loads(snap))
    return result,new_snap

def main():
    invocation = capture(__file__)
    assert not OUT.exists() and (data.ROOT/cfg.RECORD).is_file()
    prior,hashes,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    value = expected(prior,hashes,raw)
    observed = audit()
    assert observed['actualExit'] == 1 and not observed['passed']
    value.update(invocation=invocation,wholeWbsAuditBefore=observed)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',value)
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
