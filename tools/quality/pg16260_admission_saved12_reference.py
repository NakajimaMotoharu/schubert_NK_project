"""Two exact-source saved Admission policies; historical facts never become current DB evidence."""
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
REVIEW=('PG11590-admission-handoff-source-reauth-v1','03129d291d10ee8eeb444fae0c4ea2cd50e4b0a8176cf6e5891aadac5d729560')
POST=('PG11592-admission-handoff-source-reauth-post-v1','bf4f08d125e43861c9cc34c52496e56bff366aa37cb15b1fc24e6b928be7d62a')
PRIOR=('PG16254-monitor-saved15-reference-v1','11de0e98f6d03ac9bf4e6f7bf9871f956f4a987371c8279e3f0657bc301ed7f3')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
RAW='92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966'
OUT=data.BASE/'PG16260-admission-saved12-reference-v1'
FIELDS={'attributes','coverage','currentSourceFacts','currentSpanSha256','diagnosticTextSha256','disposition',
    'historicalFindingId','historicalManifest','historicalReasonRowSha256','historicalReasonWasBlank','id','oldRuntimeReassigned',
    'originalRowSha256','path','productTestsExecuted','ptExecutionExempt','rawWarningRetained','reason','reasonOrigin','source','sourceSha256','status'}

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def signature(row):
    return json.dumps([row['path'],row['sourceSha256'],row['attributes']],sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,post,prior,obs=[read(v) for v in (REVIEW,POST,PRIOR,OBS)]
    require(old['actualExit']==post['actualExit']==prior['actualExit']==obs['actualExit']==0 and old['source']==post['source']==OLD_SOURCE
            and prior['source']==obs['source']==SOURCE and post['primaryManifestSha256']==REVIEW[1] and post['metadataNegativeVectors']==14,'qualified old and current chain')
    require(old['productTestsExecuted']==post['productTestsExecuted']==old['newIndividualDispositions']==post['newIndividualDispositions']==0
            and old['reviewed']==post['reviewed']==19 and old['historicalRuntimeImportedAsCurrent'] is post['historicalRuntimeImportedAsCurrent'] is False,'old source review not execution')
    review=data.read_checked(data.BASE/REVIEW[0]/'review.json',old['reviewSha256']);rows=review['rows']
    require(review['source']==OLD_SOURCE and len(rows)==19 and all(set(v)==FIELDS for v in rows),'actual old schema lacks standalone rule')
    saved={signature(v):(i,v) for i,v in enumerate(rows)};require(len(saved)==19,'unique old full signatures')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==213 and prior['combinedSelectedReferences']==1159 and prior['combinedPurposeReviewed']==119,'fixed prior domains')
    observed=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256']);observed={v['staticObservationId']:v for v in observed}
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',RAW);raw={v['id']:v for v in raw}
    links=[];hashes={}
    for current in queue:
        if signature(current) not in saved:continue
        ordinal,row=saved[signature(current)];original=raw[row['id']];actual=observed[current['id']]
        require(row['source']==OLD_SOURCE and row['reasonOrigin']=='PG6048' and row['historicalReasonWasBlank'] is False
                and row['reason'] and row['currentSourceFacts'] and row['status']=='SOURCE_REBOUND_CURRENT_WHOLE_PENDING'
                and row['oldRuntimeReassigned'] is row['ptExecutionExempt'] is False and row['coverage'] is None
                and row['productTestsExecuted']==0 and row['rawWarningRetained'] is True,'original nonblank reason and pending state')
        require(original['rowSha256']==row['originalRowSha256'] and original['path']==row['path']
                and original['inputSha256']==row['sourceSha256'] and original['attributes']==row['attributes'],'entire original raw record')
        require(actual['currentSource']==SOURCE and actual['path']==current['path'] and actual['sourceSha256']==current['sourceSha256']
                and actual['attributes']==current['attributes'] and actual['message']==original['message']
                and data.sha(actual['message'].encode())==row['diagnosticTextSha256'],'current full diagnostic')
        blob=(data.ROOT/current['path']).read_bytes();require(data.sha(blob)==row['sourceSha256'],'whole Source same bytes')
        hashes[current['path']]=row['sourceSha256']
        links.append(dict(**current,currentSource=SOURCE,staticReviewSource=OLD_SOURCE,oldManifestSha256=REVIEW[1],oldPostManifestSha256=POST[1],
            oldReviewSha256=old['reviewSha256'],oldRowOrdinal=ordinal,oldRowSha256=data.sha(json.dumps(row,sort_keys=True).encode()),savedReviewRow=row,
            originalDiagnosticRowSha256=row['originalRowSha256'],diagnosticMessageSha256=row['diagnosticTextSha256'],oldStandaloneRuleFieldAvailable=False,
            oldScopeFingerprintsReparsed=False,historicalDesignsReaccepted=False,currentRuntimeQualification=False,
            meaning='EXACT_SOURCE_SAVED_ADMISSION_POLICY_REFERENCE_NOT_NEW_CLASSIFICATION_OR_DATABASE_PROOF'))
    require(len(links)==len({v['id'] for v in links})==12 and len(hashes)==2 and Counter(v['rule'] for v in links)=={'AvoidCatchingGenericException':8,'DoNotThrowExceptionInFinally':4},'twelve of nineteen only')
    ids={v['id'] for v in links};remaining=[v for v in queue if v['id'] not in ids]
    require(len(remaining)==201 and not any(v['rule']=='DoNotThrowExceptionInFinally' for v in remaining),'selected finally now empty not whole gate')
    for v in (old,post,prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'references.json',links);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,staticReviewSource=OLD_SOURCE,invocation=invocation,
        oldManifestSha256=REVIEW[1],oldPostManifestSha256=POST[1],oldReviewSha256=old['reviewSha256'],historicalApprovedDesigns=review['approvedDesigns'],
        historicalCurrentSourceReviewFacts=review['currentSourceReviewFacts'],priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],
        originalRawJsonSha256=RAW,sourceHashes=hashes,referencesSha256=data.sha((OUT/'references.json').read_bytes()),
        queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),oldReviewed=19,oldOtherRowsOutsideCurrentQueue=7,
        newReferenceConnections=12,combinedSelectedReferences=1171,combinedPurposeReviewed=119,combinedPurposeOrReferenceRows=1290,remainingSelectedUnreferenced=201,
        oldStandaloneRuleFieldAvailable=False,oldScopeFingerprintsReparsed=False,historicalDesignsReaccepted=False,currentRuntimeQualification=False,
        newManualReviews=0,productTestsExecuted=0,oldProductToolsReexecuted=0,oldRuntimeTransferred=False,sourceChanged=False,
        rawSuppressed=0,actualViolationCount=None,ptExecutionExempt=False,wholeF03Accepted=False,whole451Accepted=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
