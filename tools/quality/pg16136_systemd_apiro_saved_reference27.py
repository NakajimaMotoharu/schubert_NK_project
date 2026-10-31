"""Two explicit modern source-purpose schemas; no original Product/FFM/DB actions."""
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
RECORDS=[
 dict(name='PG13148-systemd-source-context-v1',pin='4c4d139f02de58aa29294e4022ba8c710f3d0117349c86778841183dfd8ac7f2',
      post='PG13149-systemd-source-context-post-v1',postPin='b2d7947bd08f97f58b0872261d429793afaad836b21d188ef6af2dd607e7b25c',postKey='reviewedManifestSha256',
      source='44afb0a1ecddabfebe577b2037aabdc6fb31d1e3',payload='review.json',hashKey='reviewSha256',nested=True,count=14,schema='SYSTEMD_SOURCE_PURPOSE_FULL_ATTRIBUTES_V1'),
 dict(name='PG10934-api-ro-prior-context13-v1',pin='69b5240316368ec534dd837ca1b95b9b8f2cd36af1a87775b165e1e6a780350f',
      post='PG10936-api-ro-prior-context-post-v1',postPin='e5143c2f99ecab9185dee9068c14233e2f2eae2de075a423faf13c3e628b4f12',postKey='primaryManifestSha256',
      source='f24d1649e170e46aafb59a37b9750c602206364c',payload='contexts.json',hashKey='contextsSha256',nested=False,count=13,schema='API_RO_CONTEXT_FULL_ATTRIBUTES_V1')]
PRIOR=('PG16131-startup-archive-legacy-reference61-v2','ba83ddaeeeb86f302fe1c274bd0406ee3fa2e88c89a3de2e42bb1a08020eb56a')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
OUT=data.BASE/'PG16136-systemd-apiro-saved-reference27-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def signature(v):
    return json.dumps([v['path'],v['sourceSha256'],v['attributes']],sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs=[read(v) for v in (PRIOR,OBS)]
    require(prior['actualExit']==obs['actualExit']==0 and prior['source']==obs['source']==SOURCE,'current metadata')
    inputs=[];source_rows={}
    for cfg in RECORDS:
        old,post=[read(v) for v in ((cfg['name'],cfg['pin']),(cfg['post'],cfg['postPin']))]
        require(old['actualExit']==post['actualExit']==0 and old['source']==post['source']==cfg['source']
                and post[cfg['postKey']]==cfg['pin'] and old['productTestsExecuted']==post['productTestsExecuted']==0,'exact old independent source-purpose witnesses')
        payload=data.read_checked(data.BASE/cfg['name']/cfg['payload'],old[cfg['hashKey']])
        rows=payload['rows'] if cfg['nested'] else payload
        require(len(rows)==cfg['count'] and all({'path','sourceSha256','attributes','message','reason','id','source','ptExecutionExempt'}<=set(r) for r in rows),'explicit common row keys')
        for ordinal,row in enumerate(rows):
            require(row['source']==cfg['source'] and row['ptExecutionExempt'] is False and row['reason'],'old reason only')
            if cfg['nested']:
                require({'manualPurposeReviewComplete','dynamicExecutionQualificationInferred','actualViolation'}<=set(row)
                        and row['manualPurposeReviewComplete'] is True and row['dynamicExecutionQualificationInferred'] is False
                        and row['actualViolation'] is None,'Systemd dedicated schema')
            else:
                require({'rawWarningRetained','oldRuntimeReassigned','scopeGeneralized','productTestsExecuted','coverage','currentWholeCaseRefs'}<=set(row)
                        and row['rawWarningRetained'] is True and row['oldRuntimeReassigned'] is row['scopeGeneralized'] is False
                        and row['productTestsExecuted']==0 and row['coverage'] is None and row['currentWholeCaseRefs']==[],'API RO dedicated schema')
            k=signature(row);require(k not in source_rows,'all distinct original signatures')
            source_rows[k]=(cfg,ordinal,row)
        inputs.extend((old,post))
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==524 and prior['combinedSelectedReferences']==871 and prior['combinedPurposeReviewed']==96,'prior current domains')
    observed=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])
    require(all({'staticObservationId','currentSource','sourceSha256','path','attributes','message'}<=set(v) for v in observed),'current schema')
    observed={v['staticObservationId']:v for v in observed}
    links=[];source_hashes={};counts=Counter()
    for current in queue:
        if signature(current) not in source_rows:continue
        cfg,index,row=source_rows[signature(current)];actual=observed[current['id']]
        require(actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256'] and actual['path']==current['path']
                and actual['attributes']==current['attributes'] and actual['message']==row['message'],'full current source/attributes/diagnostic')
        text=(data.ROOT/current['path']).read_text();require(data.sha(text.encode())==row['sourceSha256'],'whole Source bytes match')
        source_hashes[current['path']]=row['sourceSha256'];start,stop,token=span(text,current['attributes']);counts[cfg['name']]+=1
        owner_available='canonicalOwner' in row and 'canonicalCostOwner' in row
        links.append(dict(**current,currentSource=SOURCE,staticReviewSource=cfg['source'],savedSchema=cfg['schema'],
            oldManifest=cfg['name'],oldManifestSha256=cfg['pin'],oldPostManifestSha256=cfg['postPin'],
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(token.encode()),
            spanBasis='NEW_CANONICAL_SOURCE_COORDINATES_NOT_OLD_RUNTIME_OR_COVERAGE',
            oldFindingId=row['id'],oldRowOrdinal=index,oldRowSha256=data.sha(json.dumps(row,sort_keys=True).encode()),
            oldReason=row['reason'],historicalOwnerFieldsAvailable=owner_available,
            historicalCanonicalOwner=row['canonicalOwner'] if owner_available else None,
            historicalCanonicalCostOwner=row['canonicalCostOwner'] if owner_available else None,
            currentOwnershipReassigned=False,diagnosticMessageSha256=data.sha(actual['message'].encode()),
            meaning='SAVED_SOURCE_PURPOSE_REFERENCE_ONLY_NO_NEW_MANUAL_REVIEW_OR_RUNTIME'))
    require(len(links)==len({v['id'] for v in links})==27 and len(source_hashes)==2 and counts==Counter({v['name']:v['count'] for v in RECORDS}),'complete27/2 Sources')
    ids={v['id'] for v in links};remaining=[v for v in queue if v['id'] not in ids]
    for v in (*inputs,prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'references.json',links);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,oldRecords=RECORDS,
        priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],sourceHashes=source_hashes,
        referencesSha256=data.sha((OUT/'references.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),
        newReferenceConnections=27,combinedSelectedReferences=898,combinedPurposeReviewed=96,
        combinedPurposeOrReferenceRows=994,remainingSelectedUnreferenced=497,newManualReviews=0,
        rawSuppressed=0,actualViolationCount=None,productTestsExecuted=0,oldProductToolsReexecuted=0,
        oldRuntimeTransferred=False,currentOwnershipReassigned=False,sourceChanged=False,externalActions=0,
        actualSystemdOrFfmCalls=0,actualDatabaseActions=0,wholeF03Accepted=False,whole451Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
