"""Limited metadata binding, retaining true whole-current-source audit HOLD."""
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
OUT=BASE/'PG9378-inherited-companion-snapshot-post-v1'
BEFORE='1964de28d0ec7dd5900c2a6527104a9c2f631ab1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    inv='documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json';snap='documents/400_PGPT/470_PMO/486_WBS現行実績.json'
    old_inv_raw=subprocess.check_output(['git','show',BEFORE+':'+inv],cwd=ROOT)
    old_snap_raw=subprocess.check_output(['git','show',BEFORE+':'+snap],cwd=ROOT)
    assert sha(old_inv_raw)=='8431524614c19c8cd303d17575522576dcfa3037351f7d63b080b62a8730f33a'
    inv_raw=(ROOT/inv).read_bytes();snap_raw=(ROOT/snap).read_bytes()
    binding.validate(inv_raw,snap_raw,json.loads(old_inv_raw),json.loads(old_snap_raw))
    inventory=json.loads(inv_raw);ownership=inventory['currentIncrementalHostOwnership'];measured=inventory['currentJavaPathExplicitRegistryMeasurement']
    paths=[]
    for path,digest in ((ownership['manifest'],ownership['sha256']),(ownership['guardManifest'],ownership['guardSha256'])):
        raw=(ROOT/path).read_bytes();assert sha(raw)==digest;value=json.loads(raw)
        assert value['source']==SOURCE and value['actualExit']==0;paths.append(dict(path=path,sha256=digest))
    join=json.loads((ROOT/ownership['manifest']).read_bytes())
    assert ownership['sourceRows']==len(join['sourceRows'])==626 and ownership['newLogicalCandidates']==618
    assert ownership['legacyOwnerLabelsDifferingFromCanonical']==sum(row['legacyReportedOwner']!=row['canonicalOwner'] for row in join['sourceRows'])==392
    assert measured['registered']==join['registered']==1451 and measured['unregistered']==338
    assert measured['test']==dict(total=824,registered=486,unregistered=338)
    for name in ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json'):
        relative='documents/400_PGPT/470_PMO/'+name
        assert (ROOT/relative).read_bytes()==subprocess.check_output(['git','show',BEFORE+':'+relative],cwd=ROOT)
    result=subprocess.run([sys.executable,'-B',str(ROOT/'tools/quality/wbs_progress_audit.py')],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    error=result.stderr.decode().splitlines()[-1]
    assert result.returncode==1 and error=='ValueError: current physical candidate exact Git/worktree scope' and not result.stdout
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          inventorySha256=sha(inv_raw),snapshotSha256=sha(snap_raw),proofs=paths,snapshotOnlyChangedField='inventorySha256',
          original941Historical943AndBudgetsAcceptanceUnchanged=True,currentSourceRegistryCountsExact=True,
          wholeWbsAudit=dict(actualExit=result.returncode,lastError=error,passed=False),qualityGuardRelaxed=False,bug1746Closed=False,
          productTestsExecuted=0,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,wholeWbsActualExit=1,wholeWbsAccepted=False,manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
