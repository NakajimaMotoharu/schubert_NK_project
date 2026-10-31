"""Sixteen byte-exact saved map reasons, with each old schema and runtime kept historical."""
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pmd_source_span_ascii import span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
SPECS=[
 ('PG12246-main-local-maps-context-v1','1481093beb6c7d9642959dcd0b4b956236fda824f2df97379cbaf5ec23d7948e',
  'PG12248-main-local-maps-post-v1','6167dcf7e8671527f16ec20d4c6f0f2fe2b02257a9b404a03719bd588b900fb3',4,4,14,'LOCAL_METHOD_COPY_V1'),
 ('PG12260-bundle-maps-context-v1','8afbd022d68c9437ef6854aa51c69a705a456d2311f76946f52d0a10011b6a05',
  'PG12262-bundle-maps-post-v1','61523ad29196dabd3f8084ec237515022d661109bdcd00bce24c57b84f495297',7,4,20,'BUNDLE_SCOPE_COLLECTOR_V1'),
 ('PG12334-remaining-main-maps-context-v1','4227b10cee4cf12fdb0bf19af53bd3f75236625d4470680294fa8d80cb91a17e',
  'PG12336-remaining-main-maps-post-v1','e180597ce36baed2150998a199c08d182ca79f147fd08f8b1ef36abf36b02db0',8,8,28,'PRIVATE_LOCAL_COPY_STRATEGY_V1')]
PRIOR=('PG16154-emptycatch-saved10-reference-v1','f4bb9c080f06e141564e17ce743821528786476ffe4eef8ef040a4bb93e5a9d2')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
RAW='92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966'
OUT=data.BASE/'PG16192-local-map-saved16-reference-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(name,pin):
    return data.read_checked(data.BASE/name/'manifest.json',pin)

def signature(v):
    return json.dumps([v['path'],v['sourceSha256'],v['attributes']],sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs=[read(*v) for v in (PRIOR,OBS)];saved={};inputs=[prior,obs]
    common={'attributes','canonicalCostOwner','canonicalOwner','controls','currentProductQualification','currentWholeJoinPending',
            'disposition','id','kind','newAccepted','oldRuntimeReassigned','originalRowSha256','path',
            'productTestsExecutedByReview','reason','rule','source','sourceKind','sourceSha256','sourceSpanSha256'}
    for name,pin,post,post_pin,total,selected,negatives,schema in SPECS:
        old,p=read(name,pin),read(post,post_pin)
        require(old['actualExit']==p['actualExit']==0 and p['reviewManifestSha256']==pin and p['source']==old['source']
                and p['metadataNegativeVectors']==negatives and old['productTestsExecuted']==0,'qualified old review only')
        payload=data.read_checked(data.BASE/name/'review.json',old['reviewSha256']);rows=payload['rows']
        require(len(rows)==total and payload['source']==old['source'] and all(common<=set(v) for v in rows),'actual schema before field access')
        for ordinal,v in enumerate(rows):
            require(v['source']==old['source'] and v['sourceKind']=='MAIN' and v['rule']=='UseConcurrentHashMap'
                    and v['disposition']=='CONTEXT_NOT_APPLICABLE' and v['reason'] and v['controls']
                    and v['currentWholeJoinPending'] is True and v['oldRuntimeReassigned'] is False
                    and v['productTestsExecutedByReview']==v['newAccepted']==0
                    and 'message' not in v and 'ptExecutionExempt' not in v,'old purposes not transferred runtime')
            require(signature(v) not in saved,'no overlapping old signatures')
            saved[signature(v)]=(name,pin,post_pin,old['source'],schema,ordinal,v)
        inputs.extend((old,p))
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==458 and prior['combinedSelectedReferences']==917 and prior['combinedPurposeReviewed']==116,'actual prior counts')
    observed=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256']);observed={v['staticObservationId']:v for v in observed}
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',RAW);raw={v['id']:v for v in raw}
    links=[];counts=Counter();hashes={}
    for current in queue:
        if signature(current) not in saved:continue
        name,pin,post_pin,old_source,schema,ordinal,v=saved[signature(current)];original=raw[v['id']];actual=observed[current['id']]
        require(original['rowSha256']==v['originalRowSha256'] and original['inputSha256']==v['sourceSha256']
                and original['attributes']==v['attributes'] and original['path']==v['path'],'all original diagnostic identity')
        require(actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256'] and actual['path']==current['path']
                and actual['attributes']==current['attributes'] and actual['message']==original['message'],'all current diagnostic fields')
        body=(data.ROOT/current['path']).read_text();require(data.sha(body.encode())==v['sourceSha256'],'whole byte-exact Source, no source fallback')
        start,stop,token=span(body,current['attributes']);hashes[current['path']]=v['sourceSha256'];counts[name]+=1
        links.append(dict(**current,currentSource=SOURCE,staticReviewSource=old_source,savedSchema=schema,
            oldManifest=name,oldManifestSha256=pin,oldPostManifestSha256=post_pin,oldRowOrdinal=ordinal,
            oldRowSha256=data.sha(json.dumps(v,sort_keys=True).encode()),oldFindingId=v['id'],oldReason=v['reason'],
            oldKind=v['kind'],oldDisposition=v['disposition'],oldControls=v['controls'],oldCanonicalOwner=v['canonicalOwner'],
            oldCanonicalCostOwner=v['canonicalCostOwner'],oldSourceSpanSha256=v['sourceSpanSha256'],
            oldSpanInterpretation='HISTORICAL_SCHEMA_ONLY_NOT_REINTERPRETED_AS_NEW_CANONICAL_SPAN',
            oldCurrentProductQualification=v['currentProductQualification'],oldRuntimeTransferred=False,
            originalDiagnosticRowSha256=v['originalRowSha256'],diagnosticMessageSha256=data.sha(actual['message'].encode()),
            oldMessageFieldAvailable=False,oldPtExemptionFieldAvailable=False,currentPtExecutionExempt=False,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(token.encode()),
            meaning='SAVED_MAP_REASON_REFERENCE_NOT_NEW_REVIEW_RUNTIME_OR_APPLICABILITY_ACCEPTANCE'))
    require(len(links)==len({v['id'] for v in links})==16 and len(hashes)==7
            and counts==Counter({v[0]:v[5] for v in SPECS}),'four plus four plus eight exact')
    ids={v['id'] for v in links};remaining=[v for v in queue if v['id'] not in ids]
    for v in inputs:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'references.json',links);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,oldReviewSpecs=SPECS,sourceHashes=hashes,
        priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],referencesSha256=data.sha((OUT/'references.json').read_bytes()),
        queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),newReferenceConnections=16,
        combinedSelectedReferences=933,combinedPurposeReviewed=116,combinedPurposeOrReferenceRows=1049,remainingSelectedUnreferenced=442,
        oldRuntimeTransferred=False,oldSpanReinterpreted=False,sourceChanged=False,newManualReviews=0,productTestsExecuted=0,
        oldProductToolsReexecuted=0,actualMapOrRetirementOrBackupOperations=0,externalActions=0,rawSuppressed=0,
        actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
