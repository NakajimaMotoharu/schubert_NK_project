"""Strict metadata binding only; retain the genuine current whole-WBS audit HOLD."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9338-wbs-reference-metadata-post-v1'
HEAD='e14af6f8db69ff877a3af9065d4ad55845c4e1f2'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
PMO='documents/400_PGPT/470_PMO/'
INV=PMO+'485_WBS網羅性・受入対応.json'
SNAP=PMO+'486_WBS現行実績.json'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
def require(value,message):
    if not value:raise ValueError(message)
def unique(pairs):
    result={}
    for key,value in pairs:
        require(key not in result,'duplicate JSON key');result[key]=value
    return result

def validate(inv_bytes,snap_bytes,old_inv,old_snap):
    inventory=json.loads(inv_bytes,object_pairs_hook=unique);snapshot=json.loads(snap_bytes,object_pairs_hook=unique)
    require(snapshot['inventorySha256']==sha(inv_bytes),'snapshot must bind exact full inventory bytes')
    normalized=copy.deepcopy(snapshot);normalized['inventorySha256']=old_snap['inventorySha256']
    require(normalized==old_snap,'all snapshot semantics and acceptance immutable')
    allowed={'currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership'}
    require({k:v for k,v in inventory.items() if k not in allowed}=={k:v for k,v in old_inv.items() if k not in allowed},
            'only explicit current incremental metadata may change')
    require(sha(dump(inventory['artifacts']))=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99','original941 immutable')
    require(sha(dump(inventory['currentPhysicalCandidate']))=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a','historical943 immutable')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    old_inv_raw=subprocess.check_output(['git','show',HEAD+':'+INV],cwd=ROOT)
    old_snap_raw=subprocess.check_output(['git','show',HEAD+':'+SNAP],cwd=ROOT)
    assert sha(old_inv_raw)=='c9baf136ab6766956fb0a82f0293f0a6fe913c960b07b80e4b2fa3e506aec21c'
    assert sha(old_snap_raw)=='6352a4c8b2bd730d3ed07ce7c8c5b726d0e752cb65b2ee05fa1ecfe2a65c0a12'
    old_inv=json.loads(old_inv_raw);old_snap=json.loads(old_snap_raw)
    inv_raw=(ROOT/INV).read_bytes();snap_raw=(ROOT/SNAP).read_bytes()
    validate(inv_raw,snap_raw,old_inv,old_snap)
    inventory=json.loads(inv_raw);snapshot=json.loads(snap_raw);rejected=[]
    for label,change_inventory,change_snapshot in (
      ('stale-inventory-hash',None,lambda v:v.update(inventorySha256=old_snap['inventorySha256'])),
      ('invented-canonical-source',None,lambda v:v.update(source=SOURCE)),
      ('invented-effort',None,lambda v:v.update(wholeEffortCompletionRate=50)),
      ('altered-measurement-count',None,lambda v:v.update(counts={'FORGED':190})),
      ('original-owner-mutated',lambda v:v['artifacts'][0].update(owner='WBS-G13.07'),None),
      ('old-candidate-rebound',lambda v:v['currentPhysicalCandidate'].update(source=SOURCE),None),
      ('unapproved-inventory-field',lambda v:v.update(unapprovedAcceptance=True),None)):
        changed_inv=copy.deepcopy(inventory);changed_snap=copy.deepcopy(snapshot)
        if change_inventory:
            change_inventory(changed_inv);changed_snap['inventorySha256']=sha(dump(changed_inv))
        if change_snapshot:change_snapshot(changed_snap)
        try:validate(dump(changed_inv),dump(changed_snap),old_inv,old_snap)
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged binding or historical semantics accepted')
    require(inv_raw.startswith(b'{'),'ordinary JSON object')
    duplicated=b'{"source":"forged",'+inv_raw[1:]
    duplicate_snap=copy.deepcopy(snapshot);duplicate_snap['inventorySha256']=sha(duplicated)
    try:validate(duplicated,dump(duplicate_snap),old_inv,old_snap)
    except ValueError:rejected.append('duplicate-inventory-key')
    else:raise AssertionError('duplicate key accepted')
    for name in ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json'):
        assert (ROOT/PMO/name).read_bytes()==subprocess.check_output(['git','show',HEAD+':'+PMO+name],cwd=ROOT)
    guard_sources={}
    for path in ('tools/quality/wbs_progress_audit.py','tools/quality/wbs_candidate_trace.py','tools/quality/wbs_component_overlay.py'):
        raw=(ROOT/path).read_bytes();assert raw==subprocess.check_output(['git','show',HEAD+':'+path],cwd=ROOT)
        guard_sources[path]=sha(raw)
    command=[sys.executable,'-B',str(ROOT/'tools/quality/wbs_progress_audit.py')]
    result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    error=result.stderr.decode('utf-8').splitlines()[-1]
    assert result.returncode==1 and error=='ValueError: current physical candidate exact Git/worktree scope'
    assert not result.stdout
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,qualification='LIMITED_METADATA_BINDING_ONLY_FULL_WBS_AUDIT_HOLD',source=SOURCE,
          timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,bug='BUG-1746',ykt='YKT-1497',
          oldInventorySha256=sha(old_inv_raw),oldSnapshotSha256=sha(old_snap_raw),inventorySha256=sha(inv_raw),snapshotSha256=sha(snap_raw),
          snapshotOnlyChangedField='inventorySha256',original941AndHistorical943Preserved=True,originalMasterBudgetAndAcceptancePreserved=True,
          metadataCounterexamples=rejected,unchangedActualAuditSources=guard_sources,
          wholeWbsAudit=dict(command=command,actualExit=result.returncode,lastError=error,passed=False,status='CURRENT_WIP_NOT_SAME_AS_OLD_QUALIFIED_CANDIDATE'),
          qualityGuardRelaxed=False,bugClosed=False,productTestsExecuted=0,coverage=None,formalUpdated=False,
          newAccepted=0,effortPercent=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,metadataNegatives=len(rejected),wholeWbsActualExit=1,wholeWbsAccepted=False,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
