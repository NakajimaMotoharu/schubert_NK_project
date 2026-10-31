"""Independent legacy coordinates/fragment and provenance-limit checks, no original run authentication."""
from collections import Counter
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE='b4230118efcc429ee29d6e6f5761c55175f1e85e'
PARENT='PG16124-batch-legacy-coordinate-reference16-v1'
PIN='12ff7d62c5f540be5b2ebbcd3799e59e6240c1d4f4f05aa7b9c19e989a51ee38'
OUT=data.BASE/'PG16126-batch-legacy-coordinate-post-v1'
BASIS='LEGACY_SOURCE_BYTES_RULE_COORDINATES_PRIORITY_DIAGNOSTIC_FRAGMENT_NOT_FULL_ATTRS_OR_RUNTIME'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(name,pin):
    return data.read_checked(data.BASE/name/'manifest.json',pin)

def wire(v):
    return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=read(PARENT,PIN)
    old=read('PG6286-cleanup-static-review-v1','69276763b5ed88495e10aff8b2d1977aa67823e43beade9e79c5b2057e1593bc')
    prior=read('PG16118-main-nonempty-saved22-reference-v1','b26367c69ee18954ae61fc1f1cf653499d4500fd915d8f7aed67be55567c8c86')
    obs=read('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    rows=data.read_checked(data.BASE/'PG6286-cleanup-static-review-v1/decisions.json',old['decisionsSha256'])
    queue=data.read_checked(data.BASE/'PG16118-main-nonempty-saved22-reference-v1/remaining-selected-review-queue.json',prior['queueSha256'])
    observations=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',obs['observationsSha256'])
    by_id={v['staticObservationId']:v for v in observations}
    refs=data.read_checked(data.BASE/PARENT/'references.json',p['referencesSha256'])
    rest=data.read_checked(data.BASE/PARENT/'remaining-selected-review-queue.json',p['queueSha256'])
    require(old['source']==OLD_SOURCE and old['actualExit']==0 and 'invocation' not in old
            and all('attributes' not in v and v['identitySchema']==2 for v in rows),'explicit legacy limits, no original run attestation')
    require(prior['actualExit']==obs['actualExit']==p['actualExit']==0 and prior['source']==obs['source']==SOURCE,'genuine current metadata runs')
    expected=[];hashes={}
    for current in queue:
        a=current['attributes'];found=[]
        for index,row in enumerate(rows):
            if row['sourcePath']!=current['path'] or row['sourceSha256']!=current['sourceSha256'] or row['rule']!=current['rule']:continue
            if tuple(row[k] for k in ('beginline','endline','begincolumn','endcolumn','priority'))!=tuple(a[k] for k in ('beginline','endline','begincolumn','endcolumn','priority')):continue
            found.append((index,row))
        if not found:continue
        require(len(found)==1,'unambiguous legacy match without inventing full attributes')
        ordinal,row=found[0];actual=by_id[current['id']]
        require(row['source']==OLD_SOURCE and row['rawWarningRetained'] is row['currentWholeJoinPending'] is True
                and row['actualRuntimeProven'] is row['F03Accepted'] is row['formalAccepted'] is False
                and row['ptAlternativeCompleted']==0 and row['status']=='REQUIRED_CONTRACT' and row['reason'],'old static purpose only')
        require(actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256']
                and actual['attributes']==a and actual['path']==current['path']
                and data.sha(actual['message'].encode())==row['diagnosticTextSha256'],'current whole diagnostic')
        path=current['path'];body=(data.ROOT/path).read_text();require(data.sha(body.encode())==row['sourceSha256'],'full source same bytes')
        hashes[path]=row['sourceSha256'];lines=body.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
        stop=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])-1
        require(body[start:stop+1]==row['diagnosticFragment'] and body[stop]==' '
                and body[start:stop] in ('RuntimeException','Error'),'independent exact span and legacy fragment')
        expected.append(dict(**current,currentSource=SOURCE,staticReviewSource=OLD_SOURCE,
            matchingBasis=BASIS,oldFullAttributesAvailable=False,legacyToolInvocationAvailable=False,legacyRunReauthenticated=False,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(body[start:stop].encode()),
            legacyFragment=row['diagnosticFragment'],legacyFragmentSha256=data.sha(row['diagnosticFragment'].encode()),
            legacyFragmentHashComputedNowNotStoredOldField=True,legacyFragmentIsCanonicalPmdToken=False,
            oldFindingId=row['findingId'],oldRowOrdinal=ordinal,oldRowSha256=data.sha(wire(row).encode()),
            oldReason=row['reason'],oldStatus=row['status'],historicalPhysicalClassHashes=row['owningPhysicalClassHashes'],
            historicalPlannedTests=row['plannedCurrentWholeCaseClasses'],historicalPhysicalHashesUsedAsCurrent=False,
            diagnosticMessageSha256=row['diagnosticTextSha256'],
            meaning='LEGACY_SOURCE_PURPOSE_REFERENCE_ONLY_NO_NEW_REVIEW_RUN_OR_RUNTIME_QUALIFICATION'))
    ids={v['id'] for v in expected};remaining=[v for v in queue if v['id'] not in ids]
    require(len(expected)==len(ids)==16 and len(remaining)==585 and len(hashes)==2
            and sorted(Counter(v['path'] for v in expected).values())==[4,12],'all16 subset and remaining')
    def contract(m,r,t):
        require(type(m['actualExit']) is int and m['actualExit']==0 and m['source']==SOURCE and m['staticReviewSource']==OLD_SOURCE,'source/exit')
        require((m['oldReportedExit'],m['oldReviewed'],m['currentSelected'],m['newReferenceConnections'],
                 m['combinedSelectedReferences'],m['combinedPurposeReviewed'],m['combinedPurposeOrReferenceRows'],
                 m['remainingSelectedUnreferenced'])==(0,32,16,16,810,96,906,585),'no old32 double count or current inference')
        require(m['matchingBasis']==BASIS and m['sourceHashes']==hashes,'explicit limited matching schema')
        require(all(m[k] is False for k in ('legacyInvocationAvailable','legacyRunReauthenticated','fullOldAttributesAvailable',
                'legacyPhysicalHashesTransferred','oldRuntimeTransferred','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated')),'preserve missing provenance and historical bytes')
        require(all(type(m[k]) is int and m[k]==0 for k in ('newManualReviews','rawSuppressed','productTestsExecuted','oldProductToolsReexecuted','externalActions','newAccepted'))
                and m['actualViolationCount'] is m['effortPercent'] is None,'no quality/PT/effort inference')
        require(wire(r)==wire(expected) and wire(t)==wire(remaining),'all original row/physical histories and remaining metadata')
    contract(p,refs,rest);labels=[]
    vectors=[('source','source',OLD_SOURCE),('old-source','staticReviewSource',SOURCE),('old-size','oldReviewed',16),
        ('new-size','newReferenceConnections',32),('total','combinedSelectedReferences',826),
        ('purpose','combinedPurposeReviewed',112),('remaining','remainingSelectedUnreferenced',0),
        ('invocation','legacyInvocationAvailable',True),('run','legacyRunReauthenticated',True),
        ('attrs','fullOldAttributesAvailable',True),('physical','legacyPhysicalHashesTransferred',True),
        ('basis','matchingBasis','FULL_ATTRS_AND_RUNTIME'),('manual','newManualReviews',16),
        ('suppress','rawSuppressed',16),('product','productTestsExecuted',1),('replay','oldProductToolsReexecuted',1),
        ('formal','formalUpdated',True),('accepted','newAccepted',1),('effort','effortPercent',100),('violation','actualViolationCount',0)]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad,refs,rest)
        except ValueError:labels.append(label)
        else:raise ValueError('false legacy claim '+label)
    for label,key,value in [('reason','oldReason','changed'),('physical','historicalPhysicalHashesUsedAsCurrent',True),
                            ('attrs','oldFullAttributesAvailable',True),('span','canonicalSpanSha256','0'*64),
                            ('old-row','oldRowSha256','0'*64)]:
        bad=copy.deepcopy(refs);bad[0][key]=value
        try:contract(p,bad,rest)
        except ValueError:labels.append('row-'+label)
        else:raise ValueError('false legacy row '+label)
    try:contract(p,refs,rest[:-1])
    except ValueError:labels.append('remaining-row')
    else:raise ValueError('missing current remaining row')
    require(len(labels)==26,'finite26 metadata negatives')
    for v in (prior,obs,p):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        referencesSha256=p['referencesSha256'],queueSha256=p['queueSha256'],
        independentMetadataNegativeVectors=26,negativeLabels=labels,occurrences=16,
        combinedPurposeOrReferenceRows=906,remainingSelectedUnreferenced=585,
        legacyRunReauthenticated=False,oldFullAttributesAvailable=False,oldPhysicalHashesTransferred=False,
        newManualReviews=0,productTestsExecuted=0,newAccepted=0,formalUpdated=False,
        wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
