"""One-shot WBS65 resume reconciliation; public metadata only, no job/VM or product action."""
from pathlib import Path
import datetime as dt, hashlib, json, subprocess, sys

R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'
P=R.parent/'PMO/hourly-monitor/execution-plan-20261110/65-前回の実績と初週の未達で予算を見直す条件'
S=R.parent/'PMO/pgpt-completion-stage-20261102'
O=B/'evidence/PG26010-wbs65-resume-v1'
sys.path[:0]=[str(R/'tools/quality'),str(R/'tools/quality/vm/050_s1')]
import pg998_metrics as metrics
from pmo_quota_binding import append_start,digest
from pmo_group_context import build_context

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert not O.exists()
saved=json.loads((P/'保存記録.json').read_text())
names=['00_最初に開く管理用実行計画.txt','管理基準.json','全領域で週20件のときの625行WBS.tsv','全領域で週20件のときの実行計画.tsv','管理用の初回20ppの判断表.tsv']
pins={n:sha(P/n) for n in names}
assert all(pins[n]==saved['sha256'][n] for n in names)
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert head=='b713991f750eefe0982f94564480a378f06d3ff6'
restart=B/'evidence/PG26004-quota-preservation-restart-v1/next-restart.json'
prior=json.loads(restart.read_text()); assert prior['ownedRunningJobs']==[]
for p,h in prior['nextCandidate']['sourceHashes'].items():assert sha(R/p)==h
# The protected paths are names only. No stat, read or hash of them is performed.
dirty=subprocess.check_output(['git','status','--short','--branch'],text=True)
assert subprocess.check_output(['git','diff','--name-only','--','src/*/src/main/*'],text=True)==''
quota=json.loads(Path(sys.argv[1]).read_text())
group='PGPT-WBS65-K03-FIRST-WINDOW-20261111'
context=build_context(group_id=group,category='ADMIN',kind='ORIGINAL_PLAN',scope='K03.01/01 0.385 plus K03.02/01 0.615; resume/window/source/plan binding only. No original success replay or external operations.',oracle_refs=[dict(path=str(restart.relative_to(R)),sha256=sha(restart))])
values=dict(context,costRevision='WBS-cost-v2-20261007-PMO',wbsLeafIds=['WBS-K03.01','WBS-K03.02'],source=prior['productionCoreMain'],run='PG26010',estimateAtGroupStartPp=dict(low=1,base=1,high=1),groupCapPp=1,managementPlan='WBS65-20261110',managementPlanRemainingAtResumePp=dict(low=424.30,base=904.85,high=1778.40),originalEstimatesRetained=True,productTestsExecuted=0,actualAllocatedPp=None,tokenTotals=None,pgptAllComplete=False,nextCommand='Close K03 measurement then start A4-01 BUG2623 original4; all HOLD retained.')
start=append_start(group,values,sys.argv[1],digest(quota),dt.datetime.now(dt.timezone.utc).isoformat())
now=dt.datetime.now(dt.timezone(dt.timedelta(hours=9)))
v=dict(actualExit=0,atJST=now.isoformat(),startEvent=start,head=head,headDifferenceFromSaved=None,productionCoreMain=prior['productionCoreMain'],planRoot=str(P),planPins=pins,remainingBudgetAtResumePp=dict(low=424.30,base=904.85,high=1778.40),scheduleOriginalStartJST='2026-11-11T20:14:00+09:00',observedStartJST=now.isoformat(),scheduleStartDifferenceSeconds=(now-dt.datetime.fromisoformat('2026-11-11T20:14:00+09:00')).total_seconds(),quota=quota,worktree=dirty,stashCount=7,ownedRunningJobs=[],originalJobs='All own previous terminal receipts retained; external18474 and VM UNKNOWN_NOT_QUERIED_HOLD; no reattachment or restart.',diskAvailableGiB=round(__import__('shutil').disk_usage(R).free/1024**3,3),capacityLargeJobGateGiB=30,capacityReserveR3AlreadyIncludedPp=4,newAcceptance=0,formalTests=1964,formalScopes=53,effortRate=None,productTestsExecuted=0,N=None,T=None,usageMeasurementId='36758e07cb21457dc4e5bb8209bf07bef637897ee3f6093f8d759eda4c649c1a',missingUsageNotZero=True,existingHoldsRetained=True,toolSha256=sha(Path(__file__)))
O.mkdir();write(O/'manifest.json',v)
for n in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
 d=json.loads((S/n).read_text());d.update(phase='WBS65_EXPLICIT_RESUME_K03_ACTIVE',head=head,executionAllowed=True,newImplementationAllowed=True,explicitUserResumeRequired=False,stoppedForQuota=False,mayFinishTurn=False,stopReason=None,ordinaryActiveGroup=group,ordinaryGroupNotYetClosed=True,currentQuota=quota,lastEventId=start,latestWbs65Resume=dict(path=str((O/'manifest.json').relative_to(R)),sha256=sha(O/'manifest.json')),managementPlan65=dict(root=str(P),initialRemainingPp=v['remainingBudgetAtResumePp'],baselineImmutable=True),nextCommand=values['nextCommand']);write(S/n,d)
print(json.dumps(dict(actualExit=0,startEvent=start,manifestSha256=sha(O/'manifest.json'),remaining=100-quota['primary']['usedPercent'])))
