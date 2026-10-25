"""Current trace pointer integrity is distinct from the held whole-source WBS acceptance."""
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
OUT=BASE/'PG9368-static-companion-snapshot-post-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
BEFORE='767b5396ab7802864358617e029b7988dc2fcbfa'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    inv='documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json';snap='documents/400_PGPT/470_PMO/486_WBS現行実績.json'
    old_inv_raw=subprocess.check_output(['git','show',BEFORE+':'+inv],cwd=ROOT)
    old_snap_raw=subprocess.check_output(['git','show',BEFORE+':'+snap],cwd=ROOT)
    assert sha(old_inv_raw)=='1e8ace7e1844a34478315981f5e299dd72863e7c70a090b2faf5933f933d1b02'
    old_inv=json.loads(old_inv_raw);old_snap=json.loads(old_snap_raw)
    inv_raw=(ROOT/inv).read_bytes();snap_raw=(ROOT/snap).read_bytes()
    binding.validate(inv_raw,snap_raw,old_inv,old_snap)
    inventory=json.loads(inv_raw);snapshot=json.loads(snap_raw)
    join_path=BASE/'PG9364-static-companion-owner-join-v1/manifest.json'
    assert sha(join_path.read_bytes())=='5f7b552fb08fb96e388232952ab88ac61d70a581176c1e63400b405da864cbbb'
    joined=json.loads(join_path.read_bytes());assert joined['source']==SOURCE and joined['actualExit']==0
    current=inventory['currentIncrementalHostOwnership'];measured=inventory['currentJavaPathExplicitRegistryMeasurement']
    assert current['sourceRows']==joined['sourceCount']==624 and current['baselineLogicalReferences']==8 and current['newLogicalCandidates']==616
    assert current['legacyOwnerLabelsDifferingFromCanonical']==sum(row['legacyReportedOwner']!=row['canonicalOwner'] for row in joined['sourceRows'])==390
    assert measured['registered']==joined['registered']==1449 and measured['unregistered']==joined['unregisteredTest']==340
    assert measured['main']==dict(total=965,registered=965,unregistered=0) and measured['test']==dict(total=824,registered=484,unregistered=340)
    rejected=[]
    for label,change_inv,change_snap in (
      ('stale-pointer',None,lambda v:v.update(inventorySha256=old_snap['inventorySha256'])),
      ('source-rebound',None,lambda v:v.update(source=SOURCE)),
      ('effort-invented',None,lambda v:v.update(wholeEffortCompletionRate=50)),
      ('owner-forged',lambda v:v['artifacts'][0].update(owner='WBS-G13.07'),None),
      ('old-quality-source-rebound',lambda v:v['currentPhysicalCandidate'].update(source=SOURCE),None)):
        changed_inv=copy.deepcopy(inventory);changed_snap=copy.deepcopy(snapshot)
        if change_inv:change_inv(changed_inv);changed_snap['inventorySha256']=sha(binding.dump(changed_inv))
        if change_snap:change_snap(changed_snap)
        try:binding.validate(binding.dump(changed_inv),binding.dump(changed_snap),old_inv,old_snap)
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged binding accepted')
    duplicate=b'{"source":"forged",'+inv_raw[1:];changed=copy.deepcopy(snapshot);changed['inventorySha256']=sha(duplicate)
    try:binding.validate(duplicate,binding.dump(changed),old_inv,old_snap)
    except ValueError:rejected.append('duplicate-key')
    else:raise AssertionError('duplicate metadata key accepted')
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
          status='LIMITED_METADATA_BINDING; FULL_CURRENT_WBS_QUALIFICATION_HOLD',qualityGuardRelaxed=False,
          bug1746Closed=False,productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,metadataNegatives=len(rejected),wholeWbsActualExit=1,wholeWbsAccepted=False,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
