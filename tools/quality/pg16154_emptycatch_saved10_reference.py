"""Ten exact-source saved empty-catch reasons; no execution or new applicability claim."""
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD='f24d1649e170e46aafb59a37b9750c602206364c'
REVIEW=('PG10928-main-empty-catch-policy-v1','6e1ed0ff67610462fd6d3e0830dc5bd8ccaad18248a7625f351707de9fad340f')
POST=('PG10930-main-empty-catch-post-v1','25b9ad8efefecbb172faf3bce50e6bc1b3758a7eebf38dc4d55c7e78a5be0897')
PRIOR=('PG16148-keylabel-nullable-saved-reference9-v1','05e26e5a4ad67629c2c6ca698f6249b8b75321420ce860c306b0e0fb9bd1984a')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
RAW='92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966'
OUT=data.BASE/'PG16154-emptycatch-saved10-reference-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def signature(row):
    return json.dumps([row['path'],row['sourceSha256'],row['attributes']],sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,post,prior,obs=[read(v) for v in (REVIEW,POST,PRIOR,OBS)]
    require(old['actualExit']==post['actualExit']==prior['actualExit']==obs['actualExit']==0,'original metadata success')
    require(old['source']==post['source']==OLD and prior['source']==obs['source']==SOURCE
            and post['primaryManifestSha256']==REVIEW[1] and post['metadataNegativeVectors']==11,'exact original post/source')
    require(old['productTestsExecuted']==post['productTestsExecuted']==0 and old['ptExecutionExempt'] is post['ptExecutionExempt'] is False,'source review not PT exemption')
    contexts=data.read_checked(data.BASE/REVIEW[0]/'contexts.json',old['contextsSha256'])
    fields={'attributes','catchBodyTokens','catchHeaderTokens','coverage','currentWholeCaseRefs','id','oldRuntimeReassigned',
            'originalRowSha256','path','policy','productTestsExecuted','ptExecutionExempt','rawWarningRetained','reason',
            'reviewId','reviewStatus','rule','scopeGeneralized','source','sourceSha256','status','technicalDisposition'}
    require(len(contexts)==15 and all(fields==set(v) for v in contexts),'exact actual saved schema before access')
    saved={signature(v):(i,v) for i,v in enumerate(contexts)};require(len(saved)==15,'unique old full signatures')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==468 and prior['combinedSelectedReferences']==907 and prior['combinedPurposeReviewed']==116,'separate prior domains')
    observed=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])
    observed={v['staticObservationId']:v for v in observed}
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',RAW);raw={v['id']:v for v in raw}
    links=[];hashes={}
    for current in queue:
        if signature(current) not in saved:continue
        ordinal,row=saved[signature(current)];actual=observed[current['id']];original=raw[row['id']]
        require(row['rule']=='EmptyCatchBlock' and row['source']==OLD and row['reviewStatus']=='STATIC_LOCAL_FAILURE_POLICY_REVIEW_COMPLETE'
                and row['catchBodyTokens']==[] and row['catchHeaderTokens'] and row['reason'] and row['policy'],'saved finite source policy')
        require(row['productTestsExecuted']==0 and row['coverage'] is None and row['currentWholeCaseRefs']==[]
                and row['oldRuntimeReassigned'] is row['scopeGeneralized'] is row['ptExecutionExempt'] is False
                and row['rawWarningRetained'] is True,'no old runtime transfer/exemption')
        require(original['rowSha256']==row['originalRowSha256'] and original['attributes']==row['attributes']
                and original['path']==row['path'] and original['inputSha256']==row['sourceSha256'],'original raw exact')
        require(actual['currentSource']==SOURCE and actual['attributes']==current['attributes'] and actual['path']==current['path']
                and actual['sourceSha256']==current['sourceSha256'] and actual['message']==original['message'],'whole current diagnostic exact')
        body=(data.ROOT/current['path']).read_text();require(data.sha(body.encode())==row['sourceSha256'],'whole current Source same byte')
        start,stop,token=span(body,current['attributes']);hashes[current['path']]=row['sourceSha256']
        links.append(dict(**current,currentSource=SOURCE,staticReviewSource=OLD,
            savedSchema='EMPTY_CATCH_POLICY_TOKENS_REASON_V1',oldManifestSha256=REVIEW[1],oldPostManifestSha256=POST[1],
            oldRowOrdinal=ordinal,oldRowSha256=data.sha(json.dumps(row,sort_keys=True).encode()),oldFindingId=row['id'],
            oldReviewId=row['reviewId'],oldPolicy=row['policy'],oldReason=row['reason'],oldHeaderTokens=row['catchHeaderTokens'],
            oldBodyTokens=row['catchBodyTokens'],originalDiagnosticRowSha256=row['originalRowSha256'],
            diagnosticMessageSha256=data.sha(actual['message'].encode()),oldMessageFieldAvailable=False,
            oldPtExemptionFieldAvailable=True,currentPtExecutionExempt=False,oldRuntimeTransferred=False,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(token.encode()),
            meaning='EXACT_SOURCE_SAVED_REASON_REFERENCE_NOT_NEW_CURRENT_APPLICABILITY_OR_PT'))
    require(len(links)==len({v['id'] for v in links})==10 and len(hashes)==7,'ten unique and seven Sources only')
    require({v['oldRowOrdinal'] for v in links}=={0,1,2,3,4,10,11,12,13,14},'exclude changed NativeIo and out-of-queue records')
    ids={v['id'] for v in links};remaining=[v for v in queue if v['id'] not in ids]
    for v in (old,post,prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'references.json',links);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,staticReviewSource=OLD,
        oldManifestSha256=REVIEW[1],oldPostManifestSha256=POST[1],oldContextSha256=old['contextsSha256'],
        historicalDesignHashes=old['approvedDesignHashes'],currentDesignApplicabilityReaccepted=False,
        sourceHashes=hashes,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],originalRawJsonSha256=RAW,
        referencesSha256=data.sha((OUT/'references.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),
        newReferenceConnections=10,combinedSelectedReferences=917,combinedPurposeReviewed=116,combinedPurposeOrReferenceRows=1033,
        remainingSelectedUnreferenced=458,policyCounts=dict(Counter(v['oldPolicy'] for v in links)),newManualReviews=0,
        productTestsExecuted=0,oldProductToolsReexecuted=0,actualRollbackOrPurgeOrRetentionCalls=0,oldRuntimeTransferred=False,
        sourceChanged=False,rawSuppressed=0,actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,
        ptExecutionExempt=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
