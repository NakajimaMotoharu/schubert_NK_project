"""One changed Test hash and measured whole-program source scope, historical runtime preserved."""
import copy
import json
import subprocess
import snapshot_program_qualified_v2 as cfg
from f03_jms_owner_six_trace import state_after as previous_state
from pg9954_pure_query_registry_metadata import INV, SNAP, SECTIONS, replaced
from pg9338_wbs_reference_metadata_post import validate as validate_docs

data = cfg.data
SOURCE = cfg.SOURCE
PRIOR = ('PG13776-jms-owner-six-trace-v1','aac5c97bfa530a2bef14fcbf2eda0293e72d95e06751d79960dbf4fe340e9d2a')
PROOF = ('PG13844-snapshot-program-whole-post-v1','1765e226fef6761d6d975a535300e709c09f81e713e83974a567d309f671c113')
OUT = data.BASE/'PG13846-snapshot-program-trace-v1'
PATH = cfg.TEST_ROOT+'InspectorUnitSnapshotTest.java'
RECORD = 'evidence/01_PT/018_NK-OPS-001/2523_Inspector状態解析_全program閉鎖実行結果.md'

def state_after():
    ids,refs,pending = previous_state()
    assert (len(ids),len(refs),len(pending)) == (6247,3394,2533)
    return ids,refs,pending

def inputs():
    prior = data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1])
    proof = data.read_checked(data.BASE/PROOF[0]/'manifest.json',PROOF[1])
    n,_ = cfg.normal();hashes = n['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items())
    assert len(prior['sourceRows']) == 995
    assert {r['path'] for r in prior['sourceRows'] if r['sha256'] != hashes[r['path']]} == {PATH}
    assert proof['source'] == SOURCE and proof['actualExit'] == 0 and proof['tests'] == 23 and proof['suites'] == 3
    assert proof['singleSession'] and proof['crcMismatch'] == 0 and proof['coverageGateExit'] == 0
    assert proof['totals'] == {'LINE':dict(missed=0,covered=222),'METHOD':dict(missed=0,covered=34),'CLASS':dict(missed=0,covered=2),'BRANCH':dict(missed=0,covered=320)}
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+p],cwd=data.ROOT) for p in [INV,SNAP]]
    assert data.sha(raw) == 'e99e601702487de3c55e5ea52abb267fff6af5fca8faf175cbce1683603ef655'
    assert data.sha(snap) == '833b4d1ef0046dd59bd88af4d32413d9bc9a280bfb2bf3b26219f3a868daf137'
    return prior,hashes,proof,raw,snap

def expected(prior,hashes,proof):
    ids,refs,pending = state_after();value = copy.deepcopy(prior)
    for key in ['invocation','wholeWbsAuditBefore']:value.pop(key,None)
    rows = copy.deepcopy(prior['sourceRows'])
    row, = [r for r in rows if r['path'] == PATH]
    assert row['canonicalOwner'] == row['canonicalCostOwner'] == 'WBS-P004-04'
    row['sha256'] = hashes[PATH]
    value.update(source=SOURCE,sourceRows=rows,record=RECORD,modifiedTestPaths=[PATH],modifiedMainPaths=[],newTestPaths=[],
        newMethodIds=['normalExitCodeIsLiteralOnlyAfterNormalMainCode'],newTestIds=['PT-SNAPSHOT-NORMAL-EXIT-001'],
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=prior['source'],oldRuntimeDomainsReassigned=False),
        previousQualificationHistoricalOnly=copy.deepcopy(prior['currentQualification']),
        currentQualification=dict(source=SOURCE,status='WHOLE23_SNAPSHOT_COMPLETE_SOURCE_UNIT_FOUR100_NOT_WHOLE451',proofManifestSha256=PROOF[1],
            productTestsExecuted=23,junitMethodsAdded=1,existingMethodsRevalidated=22,measuredProductCounters=proof['totals'],measuredPhysicalClasses=sorted(proof['physicalClasses']),coverageGateExit=0,
            oldPtQualificationTransferred=False,sourceRowsHistoricalRuntimeUnchanged=True,actualUnitRootNativeQualification=False),
        sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        rawDeltaBasis='Legacy derived catalog unchanged; fresh selected Test static2. No new all-source static measurement or diagnostic correction counted.',
        all995RegistryRowsAndHistoricalRuntimeUnchanged=False,onlyModifiedTestHashChanged=[PATH],all995HistoricalRuntimeFieldsPreserved=True,
        newAccepted=0,formalUpdated=False,effortPercent=None,whole451Accepted=False,wholeF03Accepted=False)
    for old,new in zip(prior['sourceRows'],rows):
        if old['path'] == PATH:
            assert {k:v for k,v in old.items() if k != 'sha256'} == {k:v for k,v in new.items() if k != 'sha256'}
        else:assert old == new
    return value

def documents(value,raw,snap):
    before = json.loads(raw);result = raw
    for name in SECTIONS:
        section = copy.deepcopy(before[name])
        marker = 'beforeSnapshotProgramPG13846Reference'
        assert marker not in section
        section[marker] = {k:copy.deepcopy(section[k]) for k in ['source','manifest','sha256','record']}
        section.update(source=SOURCE,manifest=str((OUT/'manifest.json').relative_to(data.ROOT)),sha256=data.sha((OUT/'manifest.json').read_bytes()),record=RECORD,
            snapshotWholeProgramQualification=value['currentQualification'],currentAddedTestPaths=[])
        result,_,_ = replaced(result,name,section)
    changed_snap,_,_ = replaced(snap,'inventorySha256',data.sha(result))
    validate_docs(result,changed_snap,before,json.loads(snap))
    return result,changed_snap
