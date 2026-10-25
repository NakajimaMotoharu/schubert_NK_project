"""Strict current trace-pointer postconditions; never qualify whole current WBS by metadata."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import pg9338_wbs_reference_metadata_post as binding
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
PMO='documents/400_PGPT/470_PMO/'
INV=PMO+'485_WBS網羅性・受入対応.json'
SNAP=PMO+'486_WBS現行実績.json'

def sha(raw):return hashlib.sha256(raw).hexdigest()

def run(library,out,before,source,join_manifest,join_sha,expected_registered,expected_rows):
    invocation=capture(library);assert not out.exists()
    old_inv_raw=subprocess.check_output(['git','show',before+':'+INV],cwd=ROOT)
    old_snap_raw=subprocess.check_output(['git','show',before+':'+SNAP],cwd=ROOT)
    old_inv=json.loads(old_inv_raw);old_snap=json.loads(old_snap_raw)
    inv_raw=(ROOT/INV).read_bytes();snap_raw=(ROOT/SNAP).read_bytes()
    binding.validate(inv_raw,snap_raw,old_inv,old_snap)
    inv=json.loads(inv_raw);snap=json.loads(snap_raw);current=inv['currentIncrementalHostOwnership'];measured=inv['currentJavaPathExplicitRegistryMeasurement']
    raw=(BASE/join_manifest).read_bytes();assert sha(raw)==join_sha;joined=json.loads(raw)
    assert joined['source']==source and joined['actualExit']==0
    assert current['manifest']==measured['manifest']==str((BASE/join_manifest).relative_to(ROOT))
    assert current['sha256']==measured['sha256']==join_sha
    rows=joined['sourceRows'];assert len(rows)==len({row['path'] for row in rows})==current['sourceRows']==expected_rows
    assert current['newLogicalCandidates']==expected_rows-current['baselineLogicalReferences']
    assert current['legacyOwnerLabelsDifferingFromCanonical']==sum(row['legacyReportedOwner']!=row['canonicalOwner'] for row in rows)
    normal_path=BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json'
    assert sha(normal_path.read_bytes())=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    normal=json.loads(normal_path.read_bytes());assert normal['source']==source
    universe={p for p in normal['begin']['inputHashes'] if p.startswith('src/schubert-nk-') and p.endswith('.java') and '/java/' in p}
    main={p for p in universe if '/src/main/java/' in p};tests=universe-main
    registered=universe & ({row['path'] for row in inv['artifacts']}|{row['path'] for row in rows})
    assert len(universe)==1789 and len(main)==965 and len(tests)==824 and len(registered)==expected_registered
    assert measured['registered']==joined['registered']==expected_registered and measured['unregistered']==1789-expected_registered
    assert measured['main']==dict(total=965,registered=len(registered & main),unregistered=len(main-registered))
    assert measured['test']==dict(total=824,registered=len(registered & tests),unregistered=len(tests-registered))
    post=(ROOT/current['guardManifest']).read_bytes();assert sha(post)==current['guardSha256']==measured['independentPostSha256']
    assert json.loads(post)['source']==source and json.loads(post)['actualExit']==0
    rejected=[]
    for label,edit_inv,edit_snap in (
      ('stale-pointer',None,lambda v:v.update(inventorySha256=old_snap['inventorySha256'])),
      ('source-rebound',None,lambda v:v.update(source=source)),('effort-invented',None,lambda v:v.update(wholeEffortCompletionRate=50)),
      ('original-owner',lambda v:v['artifacts'][0].update(owner='WBS-G13.07'),None),
      ('old-candidate-source',lambda v:v['currentPhysicalCandidate'].update(source=source),None)):
        a=copy.deepcopy(inv);b=copy.deepcopy(snap)
        if edit_inv:edit_inv(a);b['inventorySha256']=sha(binding.dump(a))
        if edit_snap:edit_snap(b)
        try:binding.validate(binding.dump(a),binding.dump(b),old_inv,old_snap)
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged snapshot accepted')
    duplicate=b'{"source":"FORGED",'+inv_raw[1:];b=copy.deepcopy(snap);b['inventorySha256']=sha(duplicate)
    try:binding.validate(duplicate,binding.dump(b),old_inv,old_snap)
    except ValueError:rejected.append('duplicate-key')
    else:raise AssertionError('duplicate key accepted')
    for name in ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json'):
        assert (ROOT/PMO/name).read_bytes()==subprocess.check_output(['git','show',before+':'+PMO+name],cwd=ROOT)
    result=subprocess.run([sys.executable,'-B',str(ROOT/'tools/quality/wbs_progress_audit.py')],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    error=result.stderr.decode().splitlines()[-1]
    assert result.returncode==1 and not result.stdout and error=='ValueError: current physical candidate exact Git/worktree scope'
    verify(invocation);out.mkdir()
    with (out/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=source,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          inventorySha256=sha(inv_raw),snapshotSha256=sha(snap_raw),oldInventorySha256=sha(old_inv_raw),oldSnapshotSha256=sha(old_snap_raw),
          sourceRows=expected_rows,registered=expected_registered,metadataCounterexamples=rejected,snapshotOnlyChangedField='inventorySha256',
          original941Historical943BudgetsAcceptanceUnchanged=True,wholeWbsAudit=dict(actualExit=result.returncode,lastError=error,passed=False),
          bug1746Closed=False,qualityGuardRelaxed=False,productTestsExecuted=0,newAccepted=0,coverage=None,formalUpdated=False,effortPercent=None),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,registered=expected_registered,metadataNegatives=len(rejected),wholeWbsActualExit=1,manifestSha256=sha((out/'manifest.json').read_bytes()))))
