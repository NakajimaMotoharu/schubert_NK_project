"""Three qualified saved context families, exact full attributes and Source, no new applicability."""
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PRIOR=('PG16248-legacy-fourteen-133-reference-v1','013bfd3e905d613397592e307aa45b4d5014862b32da1bf484a10d953762fa4b')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
RAW='92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966'
OUT=data.BASE/'PG16254-monitor-saved15-reference-v1'
FAMILIES=[
 ('PG12824-exact-registry-context-v1','c96c20868b97aaf236ac1209719c68d5bbfe88b8a12c8babb35204b7c5806774','PG12826-exact-registry-context-post-v1','1ef6be7fa63772894cc8f8a540922e5a4d68805825a57145e4074649fc426bbd',9,2,22),
 ('PG12854-monitor-sequence-context-v1','3273a1622d8a8121316e31c28821651d27b5f81db7944f4e62998d7cba75403e','PG12856-monitor-sequence-context-post-v1','aa4e7a66e1b83f630c11c08c2db119f54ef84e3d27853b83ffcbedea8c3ba3e7',17,8,24),
 ('PG12878-pure-health-lifecycle-context-v1','75365584df3268405f71f92cfd55ef22bb9c03352699882ddbe542286fe7eb69','PG12880-pure-health-lifecycle-context-post-v1','bafd82a00b8366ece46209969ea91baa01f9b443f0b77e70cd61db85e888b251',22,5,25)]
FIELDS={'attributes','controls','currentCases','currentWholeJoinPending','disposition','id','kind','newAccepted','oldRuntimeReassigned','originalRowSha256','path','productTestsExecutedByReview','reason','rule','scopeKind','scopeName','scopeTokenSha256','source','sourceSha256','sourceSpanSha256'}

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def signature(row):
    return json.dumps([row['path'],row['sourceSha256'],row['attributes']],sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs=[read(v) for v in (PRIOR,OBS)]
    require(prior['actualExit']==obs['actualExit']==0 and prior['source']==obs['source']==SOURCE,'current metadata source')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==228 and prior['combinedSelectedReferences']==1144 and prior['combinedPurposeReviewed']==119,'separate current domains')
    observed=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256']);observed={v['staticObservationId']:v for v in observed}
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',RAW);raw={v['id']:v for v in raw}
    links=[];hashes={};families=[]
    for name,pin,post_name,post_pin,count,selected,negatives in FAMILIES:
        old,post=[read(v) for v in [(name,pin),(post_name,post_pin)]]
        require(old['actualExit']==post['actualExit']==old['productTestsExecuted']==post['productTestsExecuted']==0
                and old['source']==post['source'] and post['reviewManifestSha256']==pin
                and old['sourceContexts']==post['sourceContexts']==count and post['metadataNegativeVectors']==negatives
                and old['wholeF03Accepted'] is post['wholeF03Accepted'] is old['whole451Accepted'] is post['whole451Accepted'] is False,'original qualified source-context scope')
        review=data.read_checked(data.BASE/name/'review.json',old['reviewSha256']);rows=review['rows']
        require(review['source']==old['source'] and len(rows)==count and all(set(v)==FIELDS for v in rows),'exact three actual saved schemas')
        saved={signature(v):(i,v) for i,v in enumerate(rows)};require(len(saved)==count,'unique full saved signatures')
        local=[]
        for current in queue:
            if signature(current) not in saved:continue
            ordinal,row=saved[signature(current)];actual=observed[current['id']];original=raw[row['id']]
            require(row['source']==old['source'] and row['scopeKind']=='METHOD' and row['scopeName'] and row['reason'] and row['controls']
                    and row['disposition']=='CONTEXT_NOT_APPLICABLE' and row['currentWholeJoinPending'] is True
                    and row['oldRuntimeReassigned'] is False and row['productTestsExecutedByReview']==row['newAccepted']==0,'old limited source-purpose record')
            require(original['rowSha256']==row['originalRowSha256'] and original['path']==row['path']
                    and original['attributes']==row['attributes'] and original['inputSha256']==row['sourceSha256'],'full original raw exact')
            require(actual['currentSource']==SOURCE and actual['attributes']==current['attributes'] and actual['path']==current['path']
                    and actual['sourceSha256']==current['sourceSha256'] and actual['message']==original['message'],'whole current diagnostic exact')
            blob=(data.ROOT/current['path']).read_bytes();require(data.sha(blob)==row['sourceSha256'],'whole Source byte equality')
            hashes[current['path']]=row['sourceSha256']
            local.append(dict(**current,currentSource=SOURCE,staticReviewSource=old['source'],oldManifestName=name,
                oldManifestSha256=pin,oldPostManifestSha256=post_pin,oldReviewSha256=old['reviewSha256'],oldRowOrdinal=ordinal,
                oldRowSha256=data.sha(json.dumps(row,sort_keys=True).encode()),savedReviewRow=row,
                originalDiagnosticRowSha256=row['originalRowSha256'],diagnosticMessageSha256=data.sha(actual['message'].encode()),
                oldFullAttributesAvailable=True,oldDiagnosticMessageFieldAvailable=False,oldScopeFingerprintsReparsed=False,
                currentRuntimeQualification=False,currentDesignApplicabilityReaccepted=False,scopeGeneralized=False,
                meaning='EXACT_FULL_SOURCE_ATTRIBUTES_SAVED_PURPOSE_REFERENCE_NOT_NEW_CLASSIFICATION_OR_RUNTIME'))
        require(len(local)==selected,'fixed per-family current Main selection');links.extend(local)
        families.append(dict(name=name,manifestSha256=pin,postName=post_name,postSha256=post_pin,reviewSha256=old['reviewSha256'],oldSource=old['source'],oldRows=count,currentRows=selected))
        verify(old['invocation']);verify(post['invocation'])
    require(len(links)==len({v['id'] for v in links})==15 and len(hashes)==6
            and Counter(v['rule'] for v in links)=={'AvoidSynchronizedStatement':11,'AvoidCatchingGenericException':4},'all15/sixSource/methods')
    ids={v['id'] for v in links};remaining=[v for v in queue if v['id'] not in ids]
    require(len(remaining)==213 and not any(v['rule']=='AvoidSynchronizedStatement' for v in remaining),'selected monitor queue now empty, not whole gate')
    verify(prior['invocation']);verify(obs['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'references.json',links);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,oldFamilies=families,
        priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],originalRawJsonSha256=RAW,sourceHashes=hashes,
        referencesSha256=data.sha((OUT/'references.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),
        newReferenceConnections=15,combinedSelectedReferences=1159,combinedPurposeReviewed=119,combinedPurposeOrReferenceRows=1278,remainingSelectedUnreferenced=213,
        oldReviewed=48,oldOtherRowsOutsideCurrentQueue=33,oldFullAttributesAvailable=True,oldScopeFingerprintsReparsed=False,
        newManualReviews=0,currentRuntimeQualification=False,currentDesignApplicabilityReaccepted=False,scopeGeneralized=False,
        productTestsExecuted=0,oldProductToolsReexecuted=0,oldRuntimeTransferred=False,sourceChanged=False,
        rawSuppressed=0,actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
