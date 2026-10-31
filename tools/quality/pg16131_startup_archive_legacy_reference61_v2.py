"""Two legacy static-reference sets; preserve each source and every provenance limitation."""
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLDS=[
 ('PG6460-normal-publication-static-review-v1','edbca132babc30692228491bd45fbff6abea406702782418377182fb88ceb7b4','bbbc3f7f13b6858535515dc495ad53839683fb24',56,39),
 ('PG6358-backup-archive-static-review-v1','7ef99f90b7192abf4c570705b43fa83eae72aa951abd99c71d1a504477bc5250','aed19c6dca368e9717309d6f744d7917c6b7b32c',35,22)]
PRIOR=('PG16124-batch-legacy-coordinate-reference16-v1','12ff7d62c5f540be5b2ebbcd3799e59e6240c1d4f4f05aa7b9c19e989a51ee38')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
OUT=data.BASE/'PG16131-startup-archive-legacy-reference61-v2'
COORDS=('beginline','endline','begincolumn','endcolumn','priority')
BASIS='LEGACY_SOURCE_BYTES_RULE_COORDINATES_PRIORITY_DIAGNOSTIC_FRAGMENT_NOT_FULL_ATTRS_OR_RUNTIME'
PREFIX='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/'
ALLOWED={PREFIX+'file/'+n+'.java' for n in ('BackupStartIntentFiles','MorningStartupLaunchOwner','StartupPermitFiles')}
ALLOWED.update({PREFIX+'backup/BackupCommitService.java',PREFIX+'platform/BackupArchiveProcess.java'})

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    require(data.sha((data.ROOT/'tools/quality/pg16130_startup_archive_legacy_reference61.py').read_bytes())=='87748810d22506fbb4bd390488a45fb0c5995837e40bcea0dc78e37ccaa77974','old failed consumer frozen')
    prior,obs=[read(v) for v in (PRIOR,OBS)]
    require(prior['actualExit']==obs['actualExit']==0 and prior['source']==obs['source']==SOURCE,'current metadata')
    saved=[]
    for name,pin,source,total,expected in OLDS:
        old=read((name,pin))
        require(old['source']==source and old['actualExit']==old['testsExecuted']==old['pmdRawRemoved']==old['ptAlternativeCompleted']==0
                and old['reviewed']==total and old['F03Accepted'] is old['formalAccepted'] is False and 'invocation' not in old,'legacy record, original runtime not authenticated')
        rows=data.read_checked(data.BASE/name/'decisions.json',old['decisionsSha256'])
        required={'sourcePath','sourceSha256','rule','priority','beginline','endline','begincolumn','endcolumn',
                  'diagnosticFragment','diagnosticTextSha256','reason','findingId','owningPhysicalClassHashes',
                  'identitySchema','actualRuntimeProven','rawWarningRetained','ptAlternativeCompleted',
                  'currentWholeJoinPending','F03Accepted','formalAccepted','status'}
        require(len(rows)==total and all(required<=set(v) for v in rows),'explicit legacy schema, planned tests optional not invented')
        saved.append((name,pin,source,expected,rows,old['decisionsSha256']))
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==585 and prior['combinedSelectedReferences']==810 and prior['combinedPurposeReviewed']==96,'current domains')
    observations=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])
    observations={v['staticObservationId']:v for v in observations}
    links=[];source_hashes={};counts=Counter();extras=Counter()
    for current in queue:
        if current['path'] not in ALLOWED:continue
        found=[]
        for name,pin,source,expected,rows,decision_pin in saved:
            for index,row in enumerate(rows):
                if row['sourcePath']==current['path'] and row['sourceSha256']==current['sourceSha256'] and row['rule']==current['rule'] and all(row[k]==current['attributes'][k] for k in COORDS):
                    found.append((name,pin,source,index,row))
        if not found:continue
        require(len(found)==1,'one distinct old-source coordinate match')
        name,pin,source,index,row=found[0];actual=observations[current['id']]
        require(row['source']==source and row['identitySchema']==2 and row['rawWarningRetained'] is True and type(row['currentWholeJoinPending']) is bool
                and row['actualRuntimeProven'] is row['F03Accepted'] is row['formalAccepted'] is False
                and row['ptAlternativeCompleted']==0 and row['status']=='REQUIRED_CONTRACT' and row['reason'],'original source-only purpose')
        require(actual['sourceSha256']==current['sourceSha256'] and actual['currentSource']==SOURCE
                and actual['path']==current['path'] and actual['attributes']==current['attributes']
                and data.sha(actual['message'].encode())==row['diagnosticTextSha256'],'whole current diagnostic')
        path=current['path'];text=(data.ROOT/path).read_text();require(data.sha(text.encode())==row['sourceSha256'],'whole source bytes')
        source_hashes[path]=row['sourceSha256'];start,stop,token=span(text,current['attributes'])
        require(stop<len(text) and text[stop] in ' \n' and text[start:stop+1]==row['diagnosticFragment'],'exact preserved legacy fragment')
        counts[name]+=1;extras[repr(text[stop])]+=1
        links.append(dict(**current,currentSource=SOURCE,staticReviewSource=source,oldManifest=name,oldManifestSha256=pin,
            matchingBasis=BASIS,oldFullAttributesAvailable=False,legacyToolInvocationAvailable=False,legacyRunReauthenticated=False,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(token.encode()),
            legacyFragment=row['diagnosticFragment'],legacyFragmentSha256=data.sha(row['diagnosticFragment'].encode()),
            legacyFragmentHashComputedNowNotStoredOldField=True,legacyFragmentIsCanonicalPmdToken=False,
            oldFindingId=row['findingId'],oldRowOrdinal=index,oldRowSha256=data.sha(json.dumps(row,sort_keys=True).encode()),
            oldReason=row['reason'],oldStatus=row['status'],historicalWholeJoinPending=row['currentWholeJoinPending'],
            currentWholeJoinPending=True,currentWholeSourceQualification=False,historicalPhysicalClassHashes=row['owningPhysicalClassHashes'],
            historicalPlannedTests=row.get('plannedCurrentWholeCaseClasses'),
            historicalPlannedTestsAvailable='plannedCurrentWholeCaseClasses' in row,historicalPhysicalHashesUsedAsCurrent=False,
            diagnosticMessageSha256=row['diagnosticTextSha256'],
            meaning='LEGACY_SOURCE_PURPOSE_REFERENCE_ONLY_NO_NEW_REVIEW_RUN_OR_RUNTIME_QUALIFICATION'))
    require(len(links)==len({v['id'] for v in links})==61 and set(source_hashes)==ALLOWED
            and counts==Counter({v[0]:v[4] for v in OLDS}) and extras==Counter({"' '":58,"'\\n'":3}),'all61/5 sources/58space3LF')
    require(Counter(v['historicalWholeJoinPending'] for v in links)==Counter({True:39,False:22}),'exact old pending states preserved separately from current')
    ids={v['id'] for v in links};remaining=[v for v in queue if v['id'] not in ids]
    verify(prior['invocation']);verify(obs['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'references.json',links);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        oldManifests=[dict(name=name,sha256=pin,source=source,reviewed=total,currentSelected=count) for name,pin,source,total,count in OLDS],
        legacyInvocationAvailable=False,legacyRunReauthenticated=False,fullOldAttributesAvailable=False,legacyPhysicalHashesTransferred=False,
        matchingBasis=BASIS,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],sourceHashes=source_hashes,
        referencesSha256=data.sha((OUT/'references.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),
        historicalWholeJoinPendingCounts={'TRUE':39,'FALSE':22},currentWholeSourceQualification=False,
        legacyFragmentExtras={'SPACE':58,'LF':3},newReferenceConnections=61,combinedSelectedReferences=871,
        combinedPurposeReviewed=96,combinedPurposeOrReferenceRows=967,remainingSelectedUnreferenced=524,
        newManualReviews=0,rawSuppressed=0,actualViolationCount=None,productTestsExecuted=0,
        oldProductToolsReexecuted=0,oldRuntimeTransferred=False,sourceChanged=False,externalActions=0,
        actualIntentPermitOrCohortOperations=0,rootFailedRecoveryTargetIncluded=False,
        wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
