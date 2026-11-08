"""Persist a declared explicit selected-Test activity before execution using a fresh saved quota receipt."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
from pmo_quota_binding import append_start,digest
from pmo_group_context import build_context
R=Path.cwd();S=R.parent/'PMO/pgpt-completion-stage-20261102'
load=lambda p:json.loads(p.read_bytes());write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
c=load(Path(sys.argv[1]));assert c['category']=='SELECTED_TEST' and c['productTestsExecuted']==0
spec=R/c['specPath'];assert spec.is_relative_to(R/'evidence/01_PT/018_NK-OPS-001') and spec.suffix=='.md'
out=R/c['resultPath'];assert not out.exists() and out.is_relative_to(R/'documents/400_PGPT/470_PMO')
q=load(S/c['quotaFile']);now=datetime.datetime.now().astimezone().isoformat()
fields=build_context(group_id=c['groupId'],category=c['category'],kind=c['kind'],scope=c['scope'],oracle_refs=[dict(path=str(spec.relative_to(R)),sha256=hashlib.sha256(spec.read_bytes()).hexdigest())])
fields.update(wbsRevision='WBS-v2-20261007-PMO',costRevision='WBS-cost-v2-20261007-PMO',wbsLeafIds=c['wbsLeafIds'],primaryWbs=c['primaryWbs'],componentWbs=c.get('componentWbs',[]),componentAdditionalBudgetPp=0,groupBudgetAdditive=False,source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),run=c['run'],estimateAtGroupStartPp=c['estimate'],capPp=c['capPp'],acceptedDelta=dict(closedIds=[],reopenedIds=[],criteriaSatisfied=[],evidenceRefs=[]),technicalMeasurementDelta={},attemptResult='START',pgptAllComplete=False)
for name in ('checkpoint','cost-ledger','continuation-gate'):
 v=load(S/(name+'.json'));assert not v.get('ordinaryGroupNotYetClosed') and v.get('ordinaryActiveGroup') is None
event=append_start(c['groupId'],fields,S/c['quotaFile'],digest(q),now)
write(out,dict(groupId=c['groupId'],startEvent=event,scope=c['scope'],estimate=c['estimate'],capPp=c['capPp'],configSha256=hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()))
for name in ('checkpoint','cost-ledger','continuation-gate'):
 p=S/(name+'.json');v=load(p);v.update(atJST=now,ordinaryActiveGroup=c['groupId'],ordinaryGroupNotYetClosed=True,lastEventId=event,mayFinishTurn=False,nextCommand=c['nextCommand']);write(p,v)
print(json.dumps(dict(startEvent=event,remaining=q['primary']['remainingPercent'],estimate=c['estimate'])))
