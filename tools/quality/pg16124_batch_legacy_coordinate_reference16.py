"""Legacy coordinate-only static reasons: preserve missing provenance and old physical hashes."""
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE='b4230118efcc429ee29d6e6f5761c55175f1e85e'
OLD=('PG6286-cleanup-static-review-v1','69276763b5ed88495e10aff8b2d1977aa67823e43beade9e79c5b2057e1593bc')
PRIOR=('PG16118-main-nonempty-saved22-reference-v1','b26367c69ee18954ae61fc1f1cf653499d4500fd915d8f7aed67be55567c8c86')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
OUT=data.BASE/'PG16124-batch-legacy-coordinate-reference16-v1'
COORDS=('beginline','endline','begincolumn','endcolumn','priority')
BASIS='LEGACY_SOURCE_BYTES_RULE_COORDINATES_PRIORITY_DIAGNOSTIC_FRAGMENT_NOT_FULL_ATTRS_OR_RUNTIME'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def legacy_match(current,old):
    return old['sourcePath']==current['path'] and old['sourceSha256']==current['sourceSha256'] and old['rule']==current['rule'] and all(old[k]==current['attributes'][k] for k in COORDS)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,obs=[read(v) for v in (OLD,PRIOR,OBS)]
    require(old['source']==OLD_SOURCE and old['actualExit']==old['testsExecuted']==old['pmdRawRemoved']==old['ptAlternativeCompleted']==0
            and old['reviewed']==32 and old['currentWholeJoinPending'] is True
            and old['F03Accepted'] is old['formalAccepted'] is False and 'invocation' not in old,'explicit saved legacy record, not original run authentication')
    require(prior['actualExit']==obs['actualExit']==0 and prior['source']==obs['source']==SOURCE,'current proof')
    rows=data.read_checked(data.BASE/OLD[0]/'decisions.json',old['decisionsSha256'])
    required={'sourcePath','sourceSha256','rule','priority','beginline','endline','begincolumn','endcolumn',
              'diagnosticFragment','diagnosticTextSha256','reason','findingId','owningPhysicalClassHashes',
              'plannedCurrentWholeCaseClasses','identitySchema','actualRuntimeProven','rawWarningRetained',
              'ptAlternativeCompleted','currentWholeJoinPending','F03Accepted','formalAccepted','status'}
    require(len(rows)==32 and all(required<=set(v) for v in rows),'legacy schema preflight')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==601 and prior['combinedSelectedReferences']==794 and prior['combinedPurposeReviewed']==96,'current domains')
    observed=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])
    require(all({'sourceSha256','currentSource','path','attributes','message','staticObservationId'}<=set(v) for v in observed),'current schema')
    observed={v['staticObservationId']:v for v in observed}
    links=[];source_hashes={}
    for current in queue:
        saved=[(i,v) for i,v in enumerate(rows) if legacy_match(current,v)]
        if not saved:continue
        require(len(saved)==1,'unique coordinate/source/rule match, no arbitrary row inference')
        ordinal,row=saved[0];actual=observed[current['id']]
        require(row['source']==OLD_SOURCE and row['identitySchema']==2 and row['rawWarningRetained'] is True
                and row['currentWholeJoinPending'] is True and row['actualRuntimeProven'] is row['F03Accepted'] is row['formalAccepted'] is False
                and row['ptAlternativeCompleted']==0 and row['status']=='REQUIRED_CONTRACT' and row['reason'],'old purpose only')
        require(actual['sourceSha256']==current['sourceSha256'] and actual['currentSource']==SOURCE
                and actual['path']==current['path'] and actual['attributes']==current['attributes']
                and data.sha(actual['message'].encode())==row['diagnosticTextSha256'],'current exact diagnostic, not invented old attrs')
        path=current['path'];body=(data.ROOT/path).read_text();require(data.sha(body.encode())==row['sourceSha256'],'whole source byte equality')
        source_hashes[path]=row['sourceSha256'];start,stop,token=span(body,current['attributes'])
        require(body[start:stop+1]==row['diagnosticFragment'] and body[stop]==' ' and token in ('RuntimeException','Error'),'exact legacy fragment extra space, not canonical field')
        links.append(dict(**current,currentSource=SOURCE,staticReviewSource=OLD_SOURCE,
            matchingBasis=BASIS,oldFullAttributesAvailable=False,legacyToolInvocationAvailable=False,legacyRunReauthenticated=False,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(token.encode()),
            legacyFragment=row['diagnosticFragment'],legacyFragmentSha256=data.sha(row['diagnosticFragment'].encode()),
            legacyFragmentHashComputedNowNotStoredOldField=True,legacyFragmentIsCanonicalPmdToken=False,
            oldFindingId=row['findingId'],oldRowOrdinal=ordinal,oldRowSha256=data.sha(json.dumps(row,sort_keys=True).encode()),
            oldReason=row['reason'],oldStatus=row['status'],historicalPhysicalClassHashes=row['owningPhysicalClassHashes'],
            historicalPlannedTests=row['plannedCurrentWholeCaseClasses'],historicalPhysicalHashesUsedAsCurrent=False,
            diagnosticMessageSha256=row['diagnosticTextSha256'],
            meaning='LEGACY_SOURCE_PURPOSE_REFERENCE_ONLY_NO_NEW_REVIEW_RUN_OR_RUNTIME_QUALIFICATION'))
    require(len(links)==len({v['id'] for v in links})==16 and len(source_hashes)==2
            and sorted(Counter(v['path'] for v in links).values())==[4,12],'all16 exact current unreferenced occurrences')
    ids={v['id'] for v in links};remaining=[v for v in queue if v['id'] not in ids]
    verify(prior['invocation']);verify(obs['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'references.json',links);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,staticReviewSource=OLD_SOURCE,invocation=invocation,
        oldManifestSha256=OLD[1],oldDecisionsSha256=old['decisionsSha256'],oldReportedExit=0,
        legacyInvocationAvailable=False,legacyRunReauthenticated=False,fullOldAttributesAvailable=False,
        legacyPhysicalHashesTransferred=False,matchingBasis=BASIS,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],
        sourceHashes=source_hashes,referencesSha256=data.sha((OUT/'references.json').read_bytes()),
        queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),
        oldReviewed=32,currentSelected=16,newReferenceConnections=16,combinedSelectedReferences=810,
        combinedPurposeReviewed=96,combinedPurposeOrReferenceRows=906,remainingSelectedUnreferenced=585,
        newManualReviews=0,rawSuppressed=0,actualViolationCount=None,productTestsExecuted=0,
        oldProductToolsReexecuted=0,oldRuntimeTransferred=False,sourceChanged=False,externalActions=0,
        wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
