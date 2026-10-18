"""Append-only original event to canonical487 correspondence; no new result, budget or fee."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('pg5388_metrics',ROOT/'tools/quality/vm/050_s1/pg998_metrics.py')
metrics=importlib.util.module_from_spec(spec);spec.loader.exec_module(metrics)
EVENTS=metrics.EVENTS
REVISION='PG5388-canonical487-v1'
BASE='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'
RESULTS={
    1231:('pg5322-cgroup-owner-green-v1-metadata-v2','PG5324-cgroup-owner-bytecode-v1','PG5328-scope-classification-cgroup-owner-v1'),
    1233:('pg5340-service-resources-green-v2-metadata-v2','PG5342-service-resources-bytecode-v1','PG5346-scope-classification-service-resources-v1'),
    1235:('pg5348-manager-session-green-v1-metadata-v2','PG5350-manager-session-bytecode-v1','PG5354-scope-classification-manager-session-v1'),
    1237:('pg5372-ffm-progress-green-v1-metadata-v2','PG5374-ffm-progress-bytecode-v1','PG5378-scope-classification-ffm-progress-v1'),
    1239:('pg5380-nss-root-query-green-v1-metadata-v2','PG5382-nss-root-query-bytecode-v1','PG5386-scope-classification-nss-root-query-v1')}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def correction(original,line,starts,root=ROOT):
    primary=original['primaryWbs'];components=starts[original['groupId']].get('componentWbs') or []
    frozen=original['groupStartEstimatePp']
    start=starts[original['groupId']]
    if frozen!=start.get('groupStartEstimatePp',start.get('estimateAtGroupStartPp')):
        raise ValueError('original start frozen estimate mismatch; no budget replacement')
    values={'costRevision':original['costRevision'],'estimateRevisionSha256':original['estimateRevisionSha256'],
        'source':original['source'],'primaryWbs':primary,'componentWbs':components,
        'groupStartEstimatePp':frozen,'correctsEventId':original['eventId'],
        'originalEventLineSha256':sha(line),'originalTimeJST':original['timeJST'],
        'originalEventType':original['eventType'],'frozenEstimateFromEventId':start['eventId'],
        'canonicalMappingRevision':REVISION,'correctionOnly':True,'newOutcomesAdded':0,
        'newBudgetAddedPp':0,'actualAllocatedPp':None,'tokenTotals':None,'attempt':None,
        'workCategory':'ADMIN','formalRunDelta':None,'formalAccepted':False,
        'sourceReferenceRole':'ORIGINAL_EVENT_BINDING_NOT_CURRENT_DEPLOYMENT',
        'estimateChangeReason':'COLUMN_MAPPING_ONLY_ORIGINAL_FROZEN_VALUE_NO_NEW_ESTIMATE',
        'timeOverlapNote':'Correction recorded now; original time retained separately; no backdated execution claim',
        'sourceEvidenceRefs':['documents/400_PGPT/470_PMO/487_WBS実行計測規約.json'],
        'acceptedDelta':{'closedIds':[],'reopenedIds':[],'criteriaSatisfied':[],'evidenceRefs':[]},
        'technicalMeasurementDelta':{'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],
            'scopeRemovedIds':[],'coverageBySource':[]}}
    number=int(original['eventId'].rpartition('-')[2])
    if number in RESULTS:
        public_name,proof_name,class_name=RESULTS[number]
        refs=[BASE+name+'/manifest.json' for name in (public_name,proof_name,class_name)]
        public,proof,classified=[json.loads((root/ref).read_bytes()) for ref in refs]
        if (public['productionCandidateSource'],proof['source'],classified['source'])!=(original['source'],)*3 or (
            type(public['actualExit']) is not int or public['actualExit']!=0 or
            type(proof['actualExit']) is not int or proof['actualExit']!=0):
            raise ValueError('original source/result binding mismatch')
        if classified['qualificationSha256']!=sha((root/refs[0]).read_bytes()) or sha((root/refs[1]).read_bytes()) not in (
            value for key,value in public.items() if key.endswith('BytecodeProofSha256')):
            raise ValueError('original qualification/proof hash chain mismatch')
        run=public_name.removesuffix('-metadata-v2')
        values.update(run=run,sourceEvidenceRefs=refs,
            actualPaths=[{'path':ref,'sha256':sha((root/ref).read_bytes())} for ref in refs],
            technicalMeasurementDelta={'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],
                'scopeRemovedIds':[],'coverageBySource':[{'source':original['source'],'run':run,
                    'tests':public['tests'],'suites':public['suites'],'classCounters':proof['targetClassCounters'],
                    'original237Partition':classified['classificationCounts'],'evidenceRefs':refs,
                    'measurementReferenceOnly':True,'formalAccepted':False}]})
    quota={'fetchedAtJST':None,'limitId':None,'windowDurationMins':None,'resetsAt':None,
        'usedPercent':original.get('quotaUsedPercent'),'remainingPercent':original.get('quotaRemainingPercent'),
        'source':'Original extension values only; fetch time/window identity not captured here'}
    values['quotaBefore' if original['eventType']=='GROUP_START' else 'quotaAfter']=quota
    return values


def main():
    raw=EVENTS.read_bytes();lines=raw.splitlines(keepends=True)
    if not raw.endswith(b'\n'):raise ValueError('incomplete original line; preserve and stop before append')
    receipt_path=ROOT/(BASE+'PG5388-event-schema-corrections-v1/manifest.json')
    if receipt_path.exists():
        saved=json.loads(receipt_path.read_bytes())
        if sha(raw[:saved['originalPrefixBytes']])!=saved['originalPrefixSha256']:
            raise ValueError('saved original prefix changed; no append permitted')
    rows=[json.loads(line) for line in lines]
    starts={r['groupId']:r for r in rows if r['eventType']=='GROUP_START' and not r.get('correctionOnly')}
    already={r.get('correctsEventId'):r for r in rows if r.get('canonicalMappingRevision')==REVISION}
    targets=[(r,line) for r,line in zip(rows,lines) if 1231<=int(r['eventId'].rpartition('-')[2])<=1240]
    if len(targets)!=10:raise ValueError('exact ten original rows, no inferred historical replay')
    recorded=[]
    for original,line in targets:
        old=already.get(original['eventId'])
        if old:
            if old['originalEventLineSha256']!=sha(line):raise ValueError('existing correction refers to changed original bytes')
            identifier=old['eventId']
        else:identifier=metrics.append(original['groupId'],'CHECKPOINT',correction(original,line,starts))
        recorded.append({'originalEventId':original['eventId'],'originalLineSha256':sha(line),
            'correctionEventId':identifier,'source':original['source'],'originalTimeJST':original['timeJST']})
    if EVENTS.read_bytes()[:len(raw)]!=raw:raise ValueError('original byte prefix changed; never rewrite')
    out=ROOT/(BASE+'PG5388-event-schema-corrections-v1');out.mkdir(parents=True,exist_ok=True)
    receipt={'revision':REVISION,'actualExit':0,'bindings':recorded,'originalPrefixSha256':sha(raw),
        'originalPrefixBytes':len(raw),'originalEventsRewritten':0,'newOutcomesAdded':0,'newBudgetAddedPp':0,
        'actualAllocatedPp':None,'tokenN':None,'tokenT':None,'formalAccepted':False,
        'acceptedLeafDelta':0,'vmActions':0,'testReplays':0,'bugs':['BUG1446'],'ykt':['YKT1210']}
    path=out/'manifest.json'
    if not path.exists():
        with path.open('x') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
    else:
        old=json.loads(path.read_bytes())
        if old['bindings']!=recorded:raise ValueError('existing immutable receipt differs')
    print(json.dumps({'actualExit':0,'bindings':len(recorded),'manifestSha256':sha(path.read_bytes()),
        'originalPrefixUnchanged':True,'newOutcomesAdded':0}))


if __name__=='__main__':main()
