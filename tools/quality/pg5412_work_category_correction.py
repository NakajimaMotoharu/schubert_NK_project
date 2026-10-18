"""One append-only registered-category correction; original event/source/time/budget unchanged."""
import json
import pg5388_metrics_schema_correction as previous

metrics=previous.metrics
REVISION='PG5412-work-category-v1'
TARGET='PGPT-20261008-1254'


def values(original,line):
    if original['eventId']!=TARGET or original['workCategory']!='SOURCE_REQUALIFICATION':
        raise ValueError('only actual diagnosed category row; never infer another unknown category')
    result=previous.correction(original,line,{original['groupId']:original})
    result.update(canonicalMappingRevision=REVISION,workCategory='FULL_REGRESSION',
        correctedOriginalWorkCategory='FULL_REGRESSION',workCategoryReferenceOnly=True,
        correctionWorkCategory='ADMIN',originalWorkCategory=original['workCategory'],
        bugs=['BUG1449'],ykt=['YKT1213'])
    return result


def main():
    raw=metrics.EVENTS.read_bytes();lines=raw.splitlines(keepends=True)
    if not raw.endswith(b'\n'):raise ValueError('complete original events only')
    rows=[json.loads(line) for line in lines]
    registered=json.loads((metrics.ROOT/'documents/400_PGPT/470_PMO/487_WBS実行計測規約.json').read_bytes())['workCategories']
    bad=[row['eventId'] for row in rows if int(row['eventId'].rpartition('-')[2])>=1230 and
        row.get('workCategory') is not None and row['workCategory'] not in registered]
    if bad!=[TARGET]:raise ValueError('all post1230 category rows reviewed; another unknown requires explicit diagnosis')
    original,line=next((row,line) for row,line in zip(rows,lines) if row['eventId']==TARGET)
    existing=[row for row in rows if row.get('canonicalMappingRevision')==REVISION]
    if len(existing)>1:raise ValueError('unique append-only category correction')
    if existing:
        if existing[0]['correctsEventId']!=TARGET or existing[0]['originalEventLineSha256']!=previous.sha(line):
            raise ValueError('immutable original binding mismatch')
        identifier=existing[0]['eventId']
    else:identifier=metrics.append(original['groupId'],'CHECKPOINT',values(original,line))
    if metrics.EVENTS.read_bytes()[:len(raw)]!=raw:raise ValueError('original prefix changed')
    out=metrics.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5412-work-category-correction-v1'
    out.mkdir(parents=True,exist_ok=True);path=out/'manifest.json'
    receipt={'actualExit':0,'revision':REVISION,'originalEventId':TARGET,'correctionEventId':identifier,
        'originalLineSha256':previous.sha(line),'originalPrefixBytes':len(raw),'originalPrefixSha256':previous.sha(raw),
        'source':original['source'],'originalTimeJST':original['timeJST'],'frozenEstimate':original['groupStartEstimatePp'],
        'scannedFromEvent':1230,'diagnosedCategoryRows':1,'originalEventsRewritten':0,'newBudgetAddedPp':0,
        'newOutcomesAdded':0,'formalAccepted':False,'acceptedLeafDelta':0,'actualAllocatedPp':None,'tokenN':None,'tokenT':None,
        'bugs':['BUG1449'],'ykt':['YKT1213'],'testReplays':0,'vmActions':0}
    if path.exists():
        saved=json.loads(path.read_bytes())
        if saved['correctionEventId']!=identifier or previous.sha(raw[:saved['originalPrefixBytes']])!=saved['originalPrefixSha256']:
            raise ValueError('preserved receipt binding and prefix required')
    else:
        with path.open('x') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'actualExit':0,'correctedRows':1,'correctionEventId':identifier,'sha256':previous.sha(path.read_bytes())}))


if __name__=='__main__':main()
