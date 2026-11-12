"""Hourly observed usage cursor with same-process not-before guard; no quota reset or estimates."""
from pathlib import Path
import datetime,json,subprocess,sys
R=Path.cwd();S=R.parent/'PMO/pgpt-completion-stage-20261102';D=R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106'
load=lambda p:json.loads(p.read_text());a=load(S/'checkpoint.json');prior=a['usageNextPollNotBeforeJST'];now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
if now<datetime.datetime.fromisoformat(prior):
 print(json.dumps(dict(status='NOT_DUE_NO_POLL',now=now.isoformat(),notBefore=prior)));raise SystemExit(0)
name=sys.argv[1];assert '/' not in name and name.endswith('.json');out=D/name;assert not out.exists()
raw=subprocess.check_output(['python3','-B','tools/quality/pmo_usage_increment.py','poll','--thread-id','01a05ae6-b388-7360-ad9b-c97d488d093b','--role','PGPT'],text=True);v=json.loads(raw)
nexttime=datetime.datetime.fromisoformat(v['timeJST'])+datetime.timedelta(hours=1)
report=dict(actualExit=0,actualPoll=v,previousNotBefore=prior,callerClockComparedBeforePoll=now.isoformat(),nextNotBefore=nexttime.isoformat(),N=v['N'],T=v['T'],recordCoverage='OBSERVED_ONLY_NOT_COMPLETE')
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
 p=S/name;a=load(p)
 for k in ['usageLastPollJST','usagePollAtJST','latestUsagePollJST','latestUsagePollAtJST']:a[k]=v['timeJST']
 for k in ['usageNextPollNotBeforeJST','nextUsagePollAtJST','nextUsagePollJST','nextUsagePollNotBefore','nextUsagePollDueJST','usageNextPollNotBefore']:a[k]=nexttime.isoformat()
 for k in ['usageMeasurementId','latestUsageMeasurementId']:a[k]=v['measurementId']
 a['latestExplicitUsageObservation']=v;a['currentUsageCollectorCheckpoint']=dict(path=str(out.relative_to(R)));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
