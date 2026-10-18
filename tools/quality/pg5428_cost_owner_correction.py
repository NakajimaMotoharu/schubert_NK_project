"""Append-only K01.01 whole/freeze owner with joint readonly trigger reference, no cost allocation."""
import json
import pg5388_metrics_schema_correction as previous

metrics=previous.metrics
REVISION='PG5428-K01-joint-owner-v1'
TARGETS=('PGPT-20261008-1254','PGPT-20261008-1256')


def values(original,line,start):
    if original['eventId'] not in TARGETS or original['groupId']!='V4_FACTORY_WHOLE_READONLY' or original['primaryWbs']!='WBS-P018-04.03':
        raise ValueError('only diagnosed same joint-group original records')
    if start['eventId']!=TARGETS[0] or original['source']!=start['source'] or original['groupStartEstimatePp']!={'low':1,'base':3,'high':8}:
        raise ValueError('same source and one exact frozen start budget')
    result=previous.correction(original,line,{original['groupId']:start})
    result.update(canonicalMappingRevision=REVISION,primaryWbs='WBS-K01.01',componentWbs=['WBS-P018-04.03'],
        correctedCostPrimaryWbs='WBS-K01.01',componentReferenceOnly=True,componentAdditionalBudgetPp=0,
        componentActualAllocationPp=None,actualSpentPp=None,actualAllocatedPp=None,newBudgetAddedPp=0,
        newOutcomesAdded=0,sourceEvidenceRefs=original['sourceEvidenceRefs'],run=original.get('run'),
        costBoundaryEvidence=['PGPT-20261008-1182','PGPT-20261008-1183','documents/400_PGPT/470_PMO/484_WBSコスト枠・細分化.json'],
        jointGroupCostAttribution='Whole/freeze K01.01; source-specific readonly P018 reference only. Exclusive costs unseparated; no proportional allocation or shared1pp attribution.',
        groupBudgetCount=1,groupBudgetIdentityEventId=TARGETS[0],parentResidualRevised=False,
        bugs=['BUG1451'],ykt=['YKT1215'])
    return result


def main():
    raw=metrics.EVENTS.read_bytes();lines=raw.splitlines(keepends=True)
    if not raw.endswith(b'\n'):raise ValueError('complete original event prefix only')
    rows=[json.loads(line) for line in lines];start=next(row for row in rows if row['eventId']==TARGETS[0])
    existing={row['correctsEventId']:row for row in rows if row.get('canonicalMappingRevision')==REVISION}
    bindings=[]
    for original,line in zip(rows,lines,strict=True):
        if original['eventId'] not in TARGETS:continue
        expected=values(original,line,start)
        if original['eventId'] in existing:
            old=existing[original['eventId']]
            if old['originalEventLineSha256']!=previous.sha(line):raise ValueError('immutable original binding')
            identifier=old['eventId']
        else:identifier=metrics.append(original['groupId'],'CHECKPOINT',expected)
        bindings.append({'originalEventId':original['eventId'],'correctionEventId':identifier,'originalLineSha256':previous.sha(line),
            'source':original['source'],'run':original.get('run'),'originalTimeJST':original['timeJST']})
    if len(bindings)!=2 or metrics.EVENTS.read_bytes()[:len(raw)]!=raw:raise ValueError('exact two original records and unchanged byte prefix')
    out=metrics.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5428-cost-owner-correction-v1'
    out.mkdir(parents=True,exist_ok=True);path=out/'manifest.json'
    receipt={'actualExit':0,'revision':REVISION,'bindings':bindings,'primaryWbs':'WBS-K01.01','componentReferenceWbs':'WBS-P018-04.03',
        'originalPrefixBytes':len(raw),'originalPrefixSha256':previous.sha(raw),'frozenStartEstimatePp':start['groupStartEstimatePp'],
        'groupBudgetCount':1,'newBudgetAddedPp':0,'actualSpentPp':None,'actualAllocatedPp':None,'newOutcomesAdded':0,
        'formalAccepted':False,'parentResidualRevised':False,'sharedObservedPpIsNotExclusive':True,'testReplays':0,'vmActions':0,
        'bugs':['BUG1451'],'ykt':['YKT1215']}
    if path.exists():
        old=json.loads(path.read_bytes())
        if old['bindings']!=bindings or previous.sha(raw[:old['originalPrefixBytes']])!=old['originalPrefixSha256']:
            raise ValueError('immutable receipt and original prefix required')
    else:
        with path.open('x') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'actualExit':0,'bindings':bindings,'sha256':previous.sha(path.read_bytes()),'newBudgetAddedPp':0}))


if __name__=='__main__':main()
