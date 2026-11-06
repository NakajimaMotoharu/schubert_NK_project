"""Append complete PGPT stage records; preserve existing collector/PMO state."""
import datetime
import fcntl
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
EVENTS=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
V3=Path('/home/mini/codex/project1/work/PMO/hourly-monitor/wbs-reestimate-v3-PGPT-20261008-PG500.json')
V4=Path('/home/mini/codex/project1/work/PMO/hourly-monitor/wbs-reestimate-v4-PGPT-20261018.json')


def canonical_fields(values,event_type):
    result=dict(values)
    # BUG1576/487: a one-second marker difference is still an unconfirmed interval.
    # Preserve raw quota observations and caller intent; never round or infer a real reset.
    if result.get('sameQuotaWindow') is not None or result.get('observedSharedPp') is not None:
        before=result.get('quotaBefore');after=result.get('quotaAfter')
        first=before.get('resetsAt') if isinstance(before,dict) else None
        last=after.get('resetsAt') if isinstance(after,dict) else None
        if type(first) is not int or type(last) is not int or first!=last:
            result['quotaWindowReportedBeforeGuard']={
                'sameQuotaWindow':result.get('sameQuotaWindow'),
                'observedSharedPp':result.get('observedSharedPp')}
            result['sameQuotaWindow']=None
            result['observedSharedPp']=None
            result['quotaWindowComparisonStatus']='UNDETERMINED_MARKER_INTERVALS_SPLIT_NO_RESET_INFERRED'
    primary=values.get('primaryWbs')
    if primary:
        leaves=list(dict.fromkeys([primary]+list(values.get('componentWbs') or [])))
        if any(not isinstance(item,str) or not item.startswith('WBS-') for item in leaves):
            raise ValueError('explicit WBS ids required')
        if 'wbsLeafIds' in values and values['wbsLeafIds']!=leaves:
            raise ValueError('canonical and extension WBS mapping conflict')
        result['wbsLeafIds']=leaves
        result.setdefault('componentAdditionalBudgetPp',0)
        result.setdefault('componentActualAllocationPp',None)
        result.setdefault('groupBudgetAdditive',False)
    frozen=values.get('groupStartEstimatePp')
    if frozen is not None:
        if set(frozen)!={'low','base','high'} or any(type(v) not in (int,float) or v<0 for v in frozen.values()):
            raise ValueError('explicit nonnegative frozen group estimate, never quota-to-token conversion')
        if not frozen['low']<=frozen['base']<=frozen['high']:
            raise ValueError('ordered original frozen estimate required')
        if 'estimateAtGroupStartPp' in values and values['estimateAtGroupStartPp']!=frozen:
            raise ValueError('canonical and extension frozen estimate conflict')
        result['estimateAtGroupStartPp']=dict(frozen)
    if event_type=='GROUP_END':
        result.setdefault('requestedLegacyEventType',event_type)
        result.setdefault('groupBoundary','END')
        event_type='CHECKPOINT'
    return result,event_type


def estimate_identity(values):
    revision=values.get('costRevision','PMO-remaining-v3-20261010')
    paths={'PMO-remaining-v3-20261010':V3,'PMO-remaining-v4-20261018':V4,
           'WBS-cost-v2-20261007-PMO':ROOT/'documents/400_PGPT/470_PMO/484_WBSコスト枠・細分化.json'}
    if revision not in paths:raise ValueError('known frozen estimate revision required')
    if revision=='WBS-cost-v2-20261007-PMO':
        if json.loads(paths[revision].read_bytes()).get('revision')!=revision:
            raise ValueError('current cost file must declare the selected revision')
    digest=hashlib.sha256(paths[revision].read_bytes()).hexdigest()
    if values.get('estimateRevisionSha256',digest)!=digest:
        raise ValueError('estimate revision and explicit hash mismatch')
    return revision,digest

def append(group,event_type,values):
    if set(values)&{'eventId','previousEventId','timeJST','executionId','groupId','eventType'}:
        raise ValueError('append identity/time are current writer observations, never caller backdates')
    values,event_type=canonical_fields(values,event_type)
    revision,digest=estimate_identity(values)
    specification=json.loads((ROOT/'documents/400_PGPT/470_PMO/487_WBS実行計測規約.json').read_bytes())
    if event_type not in specification['eventTypes']:raise ValueError('registered 487 event type required')
    if values.get('workCategory') is not None and values['workCategory'] not in specification['workCategories']:
        raise ValueError('registered 487 work category required; unknown stays null')
    template=specification['eventTemplate']
    if values.get('wbsLeafIds'):
        nodes={}
        def collect(item):
            if isinstance(item,dict):
                if isinstance(item.get('id'),str):nodes[item['id']]=item
                for child in item.values():collect(child)
            elif isinstance(item,list):
                for child in item:collect(child)
        for name in ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json'):
            collect(json.loads((ROOT/'documents/400_PGPT/470_PMO'/name).read_bytes()))
        if any(leaf not in nodes or nodes[leaf].get('children') or ':' in leaf for leaf in values['wbsLeafIds']):
            raise ValueError('actual 481/484 leaf ids only; split parents cannot add a second cost')
    with EVENTS.open('a+b') as f:
        fcntl.flock(f,fcntl.LOCK_EX);f.seek(0)
        lines=f.read().splitlines();last=json.loads(lines[-1])
        record=dict(template)
        number=int(last['eventId'].rpartition('-')[2])+1
        record.update(eventId=f'PGPT-20261008-{number:04d}',previousEventId=last['eventId'],
          executionId='PGPT-20261008-PG500',groupId=group,eventType=event_type,
          timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
          gitHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          source=None,costRevision=revision,
          estimateRevisionSha256=digest,
          attribution='UNKNOWN_SHARED_ACCOUNT',actualAllocatedPp=None,
          tokenCoverageNote='Explicit numeric response usage not available; no quota-to-token conversion; existing cursor retained',
          modelRequested='gpt-6.1-sol',reasoningRequested='high',modelObserved=None,reasoningObserved=None,
          modelVerificationMethod='Requested configuration; actual app settings unverified')
        record.update(values)
        f.seek(0,os.SEEK_END);f.write((json.dumps(record,ensure_ascii=False)+'\n').encode());f.flush();os.fsync(f.fileno())
    return record['eventId']

if __name__=='__main__':
    # Stage allocation was fixed before command in0259. This checkpoint explicitly
    # records the delayed stage-start event rather than inventing a prior timestamp.
    print(append('V3_COLD_OFFLINE_BOOT','CHECKPOINT',{
      'wbsLeafIds':['WBS-N11'],'stage':'OFFLINE_BOOT_PRESERVATION','run':'PG997-offline-v1',
      'estimateAtGroupStartPp':{'low':.5,'base':1,'high':2},
      'estimateFrozenAt':'PGPT-20261008-0259 stageAllocation.WBS-N11.offlineBoot',
      'measurementDelay':'Dedicated stage event written after job start; estimate existed before start in0259; exact active/model and job wait split unavailable.',
      'attempt':1,'attemptResult':'RUNNING','workCategory':'RECOVERY',
      'actualPaths':['offline stable disk/backing identities and SHA capture; bounded compressed standalone copy running'],
      'unaccepted':['copy logical comparison pending','isolated boot not issued','cold current reauthentication pending'],
      'nextCommand':'Reattach exec session97866; compare must0/source stable, then new-only isolated management boot.'}))
