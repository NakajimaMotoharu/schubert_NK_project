"""Saved compiler-type/purpose references only; never rerun typing, load Product or qualify Graph."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE='2f4290e7e511ea30224d087f78d44964d3488919'
REVIEW=('PG13038-throwable-identity-post-v1','2db97b5ef8db4f2c84b69c3096a3ec966d89a42529db5c7c9c3bc9956b241f4d')
TYPED=('PG13036-throwable-identity-types-v3','da05a736e3d76741d04e8de8b14188a5428c0ba24ecd856e242fc6b9f8c60a4d')
PRIOR=('PG16199-release-collector-map3-purpose-v2','1e1efedd74db655a592a0e3f83f24bc92a5467a0e4329c8919f5cbfb99e10ecd')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
OUT=data.BASE/'PG16204-throwable-identity-saved28-reference-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    review,typed,prior,obs=[read(v) for v in (REVIEW,TYPED,PRIOR,OBS)]
    require(review['actualExit']==typed['actualExit']==prior['actualExit']==obs['actualExit']==0
            and review['source']==typed['source']==OLD_SOURCE and prior['source']==obs['source']==SOURCE
            and review['typedManifestSha256']==TYPED[1] and review['metadataNegativeVectors']==9,'qualified saved static chain')
    require(review['productClassesLoaded']==typed['productClassesLoaded']==review['productTestsExecuted']==typed['productTestsExecuted']==0
            and typed['observedRows']==56 and typed['bothThrowableTypeCandidates']==28 and typed['unresolvedRows']==0,'old static type analysis only')
    payload=data.read_checked(data.BASE/REVIEW[0]/'review.json',review['reviewSha256'])
    require(payload['source']==OLD_SOURCE and len(payload['reviewedRows'])==28 and len(payload['typedNonThrowableUnclassified'])==28,'keep old two distinct domains')
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');original={v['id']:v for v in original}
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==439 and prior['combinedSelectedReferences']==933 and prior['combinedPurposeReviewed']==119,'actual prior reference/purpose counts')
    observed=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256']);observed={v['staticObservationId']:v for v in observed}
    old_rows={row['id']:row for row in payload['reviewedRows']};links=[];hashes={}
    for current in queue:
        if current['rule']!='CompareObjectsWithEquals':continue
        rows=[(row,original[row['id']]) for row in old_rows.values() if row['path']==current['path'] and row['sourceSha256']==current['sourceSha256']
              and original[row['id']]['attributes']==current['attributes']]
        require(len(rows)==1,'one exact saved identity context for every remaining identity')
        row,raw=rows[0];actual=observed[current['id']];a=current['attributes']
        require(row['typeEvidence']=='BOTH_THROWABLE_REFERENCE_TYPES' and row['leftThrowable']==row['rightThrowable']=='YES'
                and row['manualPurposeReviewComplete'] is True and row['dynamicExecutionQualificationInferred'] is False
                and row['status']=='STATIC_DIAGNOSTIC_CONTEXT_REVIEWED_DYNAMIC_HOLD' and row['reason']
                and row['actualViolation'] is row['actualAllocatedPp'] is None and row['additionalSharedCostPp']==0,'saved type/purpose/risk never dynamic')
        require((row['originalLine'],row['originalColumn'])==(int(a['beginline']),int(a['begincolumn']))
                and raw['inputSha256']==row['sourceSha256'] and raw['path']==row['path'] and actual['currentSource']==SOURCE
                and actual['sourceSha256']==current['sourceSha256'] and actual['path']==current['path']
                and actual['attributes']==a and actual['message']==raw['message'],'whole raw/current diagnostic and original coordinates')
        body=(data.ROOT/current['path']).read_text();require(data.sha(body.encode())==row['sourceSha256']
                and body.splitlines()[row['astLine']-1].strip()==row['sourceSnippet'],'full current byte Source plus exact old AST line')
        hashes[current['path']]=row['sourceSha256']
        links.append(dict(**current,currentSource=SOURCE,staticReviewSource=OLD_SOURCE,
            savedSchema='JAVAC_TYPED_THROWABLE_REFERENCE_PURPOSE_WITH_DYNAMIC_HOLD_V1',oldPostManifestSha256=REVIEW[1],oldTypedManifestSha256=TYPED[1],
            oldReviewId=row['id'],oldReviewRowSha256=data.sha(json.dumps(row,sort_keys=True).encode()),oldReview=row,
            originalDiagnosticRowSha256=raw['rowSha256'],diagnosticMessageSha256=data.sha(actual['message'].encode()),
            oldTypeClasspathReassigned=False,newCurrentTypeAnalysisClaimed=False,oldRuntimeTransferred=False,ptExecutionExempt=False,
            meaning='SAVED_EXACT_SOURCE_TYPE_PURPOSE_REFERENCE_NOT_NEW_CURRENT_TYPE_OR_DYNAMIC_QUALIFICATION'))
    require(len(links)==len({v['id'] for v in links})==28 and len(hashes)==18,'all28/eighteen exact Source references')
    ids={v['id'] for v in links};remaining=[v for v in queue if v['id'] not in ids]
    for v in (review,prior,obs):verify(v['invocation'])
    verify(typed['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'references.json',links);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,staticReviewSource=OLD_SOURCE,
        oldPostManifestSha256=REVIEW[1],oldTypedManifestSha256=TYPED[1],sourceHashes=hashes,
        priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],referencesSha256=data.sha((OUT/'references.json').read_bytes()),
        queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),newReferenceConnections=28,newManualReviews=0,
        combinedSelectedReferences=961,combinedPurposeReviewed=119,combinedPurposeOrReferenceRows=1080,remainingSelectedUnreferenced=411,
        remainingCompareObjectsWithEquals=0,newCurrentTypeAnalysisClaimed=False,oldTypeClasspathReassigned=False,oldRuntimeTransferred=False,
        productTestsExecuted=0,oldTypeCheckerReexecuted=0,actualProductClassFilesReadOrLoaded=0,actualGraphOrCleanupInvocations=0,
        externalActions=0,sourceChanged=False,actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
