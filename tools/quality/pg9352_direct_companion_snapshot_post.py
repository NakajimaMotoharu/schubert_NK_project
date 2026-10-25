"""Reuse unchanged strict binding predicate; full-current WBS audit remains genuinely held."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import pg9338_wbs_reference_metadata_post as binding
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9352-direct-companion-snapshot-post-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
BEFORE='55e8eb10e637380496e96acb2329f25ecabd02b0'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    inv_path='documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    snap_path='documents/400_PGPT/470_PMO/486_WBS現行実績.json'
    old_inv_raw=subprocess.check_output(['git','show',BEFORE+':'+inv_path],cwd=ROOT)
    old_snap_raw=subprocess.check_output(['git','show',BEFORE+':'+snap_path],cwd=ROOT)
    assert sha(old_inv_raw)=='9ecdf89d6c1db9559fef52bbdea98ef9e77834d5238fef4bcb19b38974780c62'
    old_inv=json.loads(old_inv_raw);old_snap=json.loads(old_snap_raw)
    inv_raw=(ROOT/inv_path).read_bytes();snap_raw=(ROOT/snap_path).read_bytes()
    binding.validate(inv_raw,snap_raw,old_inv,old_snap)
    inventory=json.loads(inv_raw);snapshot=json.loads(snap_raw)
    join_path=BASE/'PG9348-direct-companion-owner-join-v1/manifest.json'
    assert sha(join_path.read_bytes())=='fa2817d4f7b37d4d5cf2325edb2e1dd8b0763276fe0477805147606e86660f20'
    joined=json.loads(join_path.read_bytes());assert joined['source']==SOURCE and joined['actualExit']==0
    current=inventory['currentIncrementalHostOwnership'];coverage=inventory['currentJavaPathExplicitRegistryMeasurement']
    assert current['sourceRows']==joined['sourceCount']==569 and current['baselineLogicalReferences']==8
    assert current['newLogicalCandidates']==561 and current['legacyOwnerLabelsDifferingFromCanonical']==sum(row['legacyReportedOwner']!=row['canonicalOwner'] for row in joined['sourceRows'])==335
    assert coverage['registered']==joined['registered']==1394 and coverage['unregistered']==joined['unregisteredTest']==395
    assert coverage['main']==dict(total=965,registered=965,unregistered=0) and coverage['test']==dict(total=824,registered=429,unregistered=395)
    assert current['newAccepted']==coverage['newAccepted']==0 and current['formalAccepted'] is coverage['wholeG13Accepted'] is False
    rejected=[]
    for label,inv_change,snap_change in (
      ('stale-inventory-pointer',None,lambda v:v.update(inventorySha256=old_snap['inventorySha256'])),
      ('snapshot-source-rebound',None,lambda v:v.update(source=SOURCE)),
      ('effort-invented',None,lambda v:v.update(wholeEffortCompletionRate=50)),
      ('original-owner-forged',lambda v:v['artifacts'][0].update(owner='WBS-G13.07'),None),
      ('old-qualified-source-rebound',lambda v:v['currentPhysicalCandidate'].update(source=SOURCE),None)):
        inv=copy.deepcopy(inventory);snap=copy.deepcopy(snapshot)
        if inv_change:inv_change(inv);snap['inventorySha256']=sha(binding.dump(inv))
        if snap_change:snap_change(snap)
        try:binding.validate(binding.dump(inv),binding.dump(snap),old_inv,old_snap)
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged inventory/snapshot semantics accepted')
    duplicate=b'{"source":"forged",'+inv_raw[1:];snap=copy.deepcopy(snapshot);snap['inventorySha256']=sha(duplicate)
    try:binding.validate(duplicate,binding.dump(snap),old_inv,old_snap)
    except ValueError:rejected.append('duplicate-key')
    else:raise AssertionError('duplicate inventory key accepted')
    for name in ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json'):
        relative='documents/400_PGPT/470_PMO/'+name
        assert (ROOT/relative).read_bytes()==subprocess.check_output(['git','show',BEFORE+':'+relative],cwd=ROOT)
    command=[sys.executable,'-B',str(ROOT/'tools/quality/wbs_progress_audit.py')]
    result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    error=result.stderr.decode().splitlines()[-1]
    assert result.returncode==1 and error=='ValueError: current physical candidate exact Git/worktree scope' and not result.stdout
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          inventorySha256=sha(inv_raw),snapshotSha256=sha(snap_raw),oldInventorySha256=sha(old_inv_raw),oldSnapshotSha256=sha(old_snap_raw),
          snapshotOnlyChangedField='inventorySha256',sourceRegistryCountsExact=True,masterBudgetAcceptanceUnchanged=True,
          original941AndHistorical943Unchanged=True,metadataCounterexamples=rejected,
          wholeWbsAudit=dict(command=command,actualExit=result.returncode,lastError=error,passed=False),
          status='METADATA_BINDING_ONLY; FULL_CURRENT_QUALIFICATION_HOLD',qualityGuardRelaxed=False,
          bug1746Closed=False,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,metadataNegatives=len(rejected),wholeWbsActualExit=1,wholeWbsAccepted=False,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
