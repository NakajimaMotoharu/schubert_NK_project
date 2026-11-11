"""Append WBS65 bounded group records using existing quota/487 guards; no product operations."""
from pathlib import Path
import datetime as dt,hashlib,json,sys,re,subprocess
def bind_current_identity(state,head,main):
    assert isinstance(head,str) and re.fullmatch('[0-9a-f]{40}',head)
    assert isinstance(main,str) and re.fullmatch('[0-9a-f]{40}',main)
    result=dict(state)
    previous={k:state.get(k) for k in ['head','productionCoreMain']}
    current=dict(head=head,productionCoreMain=main)
    if previous!=current:
        result['identityBindingHistory']=list(state.get('identityBindingHistory',[]))+[dict(previous=previous,current=current,reason='CURRENT_GIT_AND_FIXED_PRODUCTION_MAIN_BINDING_NOT_SOURCE_ROLLBACK')]
    result.update(current)
    return result
def resolve_end_main_identity(start_source, config, manifest):
    after = config.get('sourceAfter', start_source)
    assert isinstance(after, str) and re.fullmatch('[0-9a-f]{40}', after)
    if 'sourceAfter' in config:
        assert manifest.get('source') == manifest.get('productionCoreMain') == after
    return after
R=Path.cwd(); S=R.parent/'PMO/pgpt-completion-stage-20261102'
sys.path[:0]=[str(R/'tools/quality'),str(R/'tools/quality/vm/050_s1')]
import pg998_metrics as metrics
from pmo_quota_binding import append_start,digest,end_fields
from pmo_group_context import build_context
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
mode,cfgpath,quotapath=sys.argv[1:];c=load(cfgpath);q=load(quotapath)
group=c['groupId'];out=R/c['recordPath'];assert not out.exists()
forecastRef=c.get('forecastRef');forecast=None
if forecastRef is not None:
 p=R/forecastRef['path'];assert forecastRef['path'].startswith('documents/400_PGPT/470_PMO/600_通常PGPT_20261106/') and p.suffix=='.json' and sha(p)==forecastRef['sha256']
 forecast=load(p);points=forecast['revisedRemainingPp'];assert set(points)=={'low','base','high'} and 0<=points['low']<=points['base']<=points['high']
now=dt.datetime.now(dt.timezone.utc).isoformat()
rows=[json.loads(v) for v in metrics.EVENTS.read_bytes().splitlines()]
if mode=='start':
 assert not any(v['groupId']==group for v in rows)
 values=dict(build_context(group_id=group,category=c['category'],kind=c['kind'],scope=c['scope'],oracle_refs=c['oracleRefs']),costRevision='WBS-cost-v2-20261007-PMO',wbsLeafIds=c['wbsLeafIds'],source=c['source'],run=c['run'],estimateAtGroupStartPp=c['estimate'],groupCapPp=c['capPp'],managementPlan='WBS65-20261110',managementWorkIds=c['workIds'],originalEstimatesRetained=True,actualAllocatedPp=None,tokenTotals=None,nextCommand=c['nextCommand'])
 event=append_start(group,values,quotapath,digest(q),now)
 record=dict(actualExit=0,eventId=event,groupId=group,estimate=c['estimate'],quota=q,configSha256=sha(Path(cfgpath)),productTestsExecuted=0,newAcceptance=0)
else:
 assert mode=='end'
 starts=[v for v in rows if v['groupId']==group and v['eventType']=='GROUP_START'];assert len(starts)==1
 assert not any(v['groupId']==group and v.get('groupBoundary')=='END' for v in rows)
 first=starts[0];p=R/c['manifestPath'];assert sha(p)==c['manifestSha256'];m=load(p)
 assert type(m['actualExit']) is int and m['actualExit']==0
 endMain=resolve_end_main_identity(first['source'],c,m)
 bound=end_fields(first['quotaReceipt']['observation'],q,digest(q),now,c['terminalAtUTC'],first['groupCapPp'])
 bound['quotaAfter']=q['primary'];bound['quotaBefore']=first['quotaReceipt']['observation']['primary']
 values=dict(bound,wbsLeafIds=first['wbsLeafIds'],workCategory=first['workCategory'],workAttributionKind=first['workAttributionKind'],source=endMain,sourceAtGroupStart=first['source'],run=c['run'],estimateAtGroupStartPp=first['estimateAtGroupStartPp'],groupCapPp=first['groupCapPp'],managementPlan='WBS65-20261110',managementWorkIds=c['workIds'],managementOutcome=c['outcome'],technicalMeasurementDelta=c['technical'],acceptedDelta=dict(closedIds=[],reopenedIds=[],criteriaSatisfied=[],evidenceRefs=[]),sourceEvidenceRefs=[dict(path=c['manifestPath'],sha256=c['manifestSha256'])],newAcceptance=0,effortCompletionRate=None,nextCommand=c['nextCommand'],groupBoundary='END')
 if forecast is not None:values.update(remainingEstimatePp=forecast['revisedRemainingPp'],remainingForecastRef=forecastRef,forecastNotActualCost=True)
 event=metrics.append(group,'CHECKPOINT',values)
 record=dict(actualExit=0,eventId=event,groupId=group,startEvent=first['eventId'],sourceAtGroupStart=first['source'],productionCoreMain=endMain,estimate=first['estimateAtGroupStartPp'],quota=q,observedSharedPp=bound['observedSharedPp'],actualAllocatedPp=None,N=None,T=None,manifest=dict(path=c['manifestPath'],sha256=c['manifestSha256']),outcome=c['outcome'],technical=c['technical'],newAcceptance=0,formalTests=1964,formalScopes=53,effortRate=None,nextCommand=c['nextCommand'])
if forecast is not None:record.update(remainingEstimatePp=forecast['revisedRemainingPp'],remainingForecastRef=forecastRef,forecastNotActualCost=True)
out.parent.mkdir(parents=True,exist_ok=True);write(out,record)
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
 d=bind_current_identity(load(S/name),metrics.subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),endMain if mode=='end' else c['source']);d.update(lastEventId=event,currentQuota=q,mayFinishTurn=False,executionAllowed=True,newImplementationAllowed=True,pgptAllComplete=False,ordinaryActiveGroup=group if mode=='start' else None,ordinaryGroupNotYetClosed=mode=='start',phase='WBS65_'+mode.upper(),nextCommand=c['nextCommand'],latestWbs65Record=dict(path=str(out.relative_to(R)),sha256=sha(out)))
 if mode=='end':
  d.setdefault('wbs65Results',[]).append(record)
  d['newImplementationAllowed']=bound['newImplementationAllowedByQuota']
 if forecast is not None:d.update(currentWbs65Forecast=forecastRef,currentWbs65RemainingEstimatePp=forecast['revisedRemainingPp'])
 write(S/name,d)
if mode=='end':
 when=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat()
 text='\n## 最新checkpoint（'+when+'、WBS65 '+','.join(c['workIds'])+'）\n\n'+c['checkpointText']+' event '+event+'。次: '+c['nextCommand']+'\n\n'
 for n in ['456_領域別進捗・利用枠・中断再開管理.md','460_基盤残件・再開優先順.md']:
  p=R/'documents/400_PGPT/450_品質'/n;t=p.read_text();a,b=t.split('\n',1);p.write_text(a+'\n'+text+b)
print(json.dumps(dict(actualExit=0,event=event,mode=mode,remaining=q['primary']['remainingPercent'],recordSha256=sha(out))))
