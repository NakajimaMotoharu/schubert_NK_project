"""Independent two-legacy-set limited-reference proof; old pending flags never become new qualification."""
from collections import Counter
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PARENT='PG16131-startup-archive-legacy-reference61-v2'
PIN='ba83ddaeeeb86f302fe1c274bd0406ee3fa2e88c89a3de2e42bb1a08020eb56a'
OUT=data.BASE/'PG16132-startup-archive-legacy-post-v1'
OLDS=[
 ('PG6460-normal-publication-static-review-v1','edbca132babc30692228491bd45fbff6abea406702782418377182fb88ceb7b4','bbbc3f7f13b6858535515dc495ad53839683fb24',56,39),
 ('PG6358-backup-archive-static-review-v1','7ef99f90b7192abf4c570705b43fa83eae72aa951abd99c71d1a504477bc5250','aed19c6dca368e9717309d6f744d7917c6b7b32c',35,22)]
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
    prior=read('PG16124-batch-legacy-coordinate-reference16-v1','12ff7d62c5f540be5b2ebbcd3799e59e6240c1d4f4f05aa7b9c19e989a51ee38')
    obs=read('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    queue=data.read_checked(data.BASE/'PG16124-batch-legacy-coordinate-reference16-v1/remaining-selected-review-queue.json',prior['queueSha256'])
    observations=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',obs['observationsSha256'])
    by_id={v['staticObservationId']:v for v in observations};old_rows=[]
    for name,pin,source,total,count in OLDS:
        old=read(name,pin)
        require(old['source']==source and old['reviewed']==total and old['actualExit']==0 and 'invocation' not in old,'legacy saved record only, no old run attestation')
        rows=data.read_checked(data.BASE/name/'decisions.json',old['decisionsSha256'])
        require(len(rows)==total and all('attributes' not in v and v['identitySchema']==2 for v in rows),'legacy partial identity schema')
        old_rows.extend((name,pin,source,index,v) for index,v in enumerate(rows))
    refs=data.read_checked(data.BASE/PARENT/'references.json',p['referencesSha256'])
    rest=data.read_checked(data.BASE/PARENT/'remaining-selected-review-queue.json',p['queueSha256'])
    require(prior['actualExit']==obs['actualExit']==p['actualExit']==0 and prior['source']==obs['source']==SOURCE,'current metadata outcomes')
    allowed=set(p['sourceHashes'])
    require(len(allowed)==5 and all('RootFailedStartRecovery' not in v for v in allowed),'no excluded Root target')
    expected=[];hashes={};counts=Counter();extra=Counter()
    for current in queue:
        if current['path'] not in allowed:continue
        a=current['attributes'];found=[]
        for name,pin,source,index,row in old_rows:
            if (row['sourcePath'],row['sourceSha256'],row['rule'])!=(current['path'],current['sourceSha256'],current['rule']):continue
            if tuple(row[k] for k in ('beginline','endline','begincolumn','endcolumn','priority'))!=tuple(a[k] for k in ('beginline','endline','begincolumn','endcolumn','priority')):continue
            found.append((name,pin,source,index,row))
        if not found:continue
        require(len(found)==1,'unambiguous old-source coordinate match')
        name,pin,source,index,row=found[0];actual=by_id[current['id']]
        require(row['source']==source and row['rawWarningRetained'] is True and type(row['currentWholeJoinPending']) is bool
                and row['actualRuntimeProven'] is row['F03Accepted'] is row['formalAccepted'] is False
                and row['ptAlternativeCompleted']==0 and row['status']=='REQUIRED_CONTRACT' and row['reason'],'explicit old booleans, not shared pending value')
        require(actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256']
                and actual['attributes']==a and actual['path']==current['path']
                and data.sha(actual['message'].encode())==row['diagnosticTextSha256'],'all current diagnostic fields')
        path=current['path'];body=(data.ROOT/path).read_text();require(data.sha(body.encode())==row['sourceSha256'],'full source byte equality')
        hashes[path]=row['sourceSha256'];lines=body.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
        stop=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])-1
        require(body[start:stop+1]==row['diagnosticFragment'] and body[stop] in ' \n','exact legacy fragment extent')
        counts[name]+=1;extra[repr(body[stop])]+=1
        expected.append(dict(**current,currentSource=SOURCE,staticReviewSource=source,oldManifest=name,oldManifestSha256=pin,
            matchingBasis=BASIS,oldFullAttributesAvailable=False,legacyToolInvocationAvailable=False,legacyRunReauthenticated=False,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(body[start:stop].encode()),
            legacyFragment=row['diagnosticFragment'],legacyFragmentSha256=data.sha(row['diagnosticFragment'].encode()),
            legacyFragmentHashComputedNowNotStoredOldField=True,legacyFragmentIsCanonicalPmdToken=False,
            oldFindingId=row['findingId'],oldRowOrdinal=index,oldRowSha256=data.sha(wire(row).encode()),
            oldReason=row['reason'],oldStatus=row['status'],historicalWholeJoinPending=row['currentWholeJoinPending'],
            currentWholeJoinPending=True,currentWholeSourceQualification=False,historicalPhysicalClassHashes=row['owningPhysicalClassHashes'],
            historicalPlannedTests=row.get('plannedCurrentWholeCaseClasses'),
            historicalPlannedTestsAvailable='plannedCurrentWholeCaseClasses' in row,historicalPhysicalHashesUsedAsCurrent=False,
            diagnosticMessageSha256=row['diagnosticTextSha256'],
            meaning='LEGACY_SOURCE_PURPOSE_REFERENCE_ONLY_NO_NEW_REVIEW_RUN_OR_RUNTIME_QUALIFICATION'))
    ids={v['id'] for v in expected};remaining=[v for v in queue if v['id'] not in ids]
    require(len(expected)==len(ids)==61 and len(remaining)==524 and len(hashes)==5
            and counts==Counter({v[0]:v[4] for v in OLDS}) and extra==Counter({"' '":58,"'\\n'":3})
            and Counter(v['historicalWholeJoinPending'] for v in expected)==Counter({True:39,False:22})
            and Counter(v['historicalPlannedTestsAvailable'] for v in expected)==Counter({True:39,False:22}),'complete61 with preserved historical state domains')
    old_manifest_expected=[dict(name=n,sha256=h,source=s,reviewed=t,currentSelected=c) for n,h,s,t,c in OLDS]
    def contract(m,r,t):
        require(type(m['actualExit']) is int and m['actualExit']==0 and m['source']==SOURCE,'current source/exit')
        require(m['oldManifests']==old_manifest_expected and m['sourceHashes']==hashes and m['matchingBasis']==BASIS,'exact two legacy source sets')
        require((m['newReferenceConnections'],m['combinedSelectedReferences'],m['combinedPurposeReviewed'],
                 m['combinedPurposeOrReferenceRows'],m['remainingSelectedUnreferenced'])==(61,871,96,967,524),'finite domain counts')
        require(m['historicalWholeJoinPendingCounts']=={'TRUE':39,'FALSE':22} and m['currentWholeSourceQualification'] is False
                and m['legacyFragmentExtras']=={'SPACE':58,'LF':3},'old pending flags distinct from new qualification')
        require(all(m[k] is False for k in ('legacyInvocationAvailable','legacyRunReauthenticated','fullOldAttributesAvailable',
                'legacyPhysicalHashesTransferred','oldRuntimeTransferred','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated','rootFailedRecoveryTargetIncluded')),'no false provenance, Root target or acceptance')
        require(all(type(m[k]) is int and m[k]==0 for k in ('newManualReviews','rawSuppressed','productTestsExecuted','oldProductToolsReexecuted',
                'externalActions','actualIntentPermitOrCohortOperations','newAccepted')) and m['actualViolationCount'] is m['effortPercent'] is None,'no Product or external acts inferred')
        require(wire(r)==wire(expected) and wire(t)==wire(remaining),'every source/coordinate/reason/history and tail')
    contract(p,refs,rest);labels=[]
    vectors=[('source','source','OLD'),('old-set','oldManifests',[]),('refs','newReferenceConnections',91),
        ('total','combinedSelectedReferences',901),('purpose','combinedPurposeReviewed',157),('pending','remainingSelectedUnreferenced',0),
        ('old-state','historicalWholeJoinPendingCounts',{'TRUE':61,'FALSE':0}),('current-state','currentWholeSourceQualification',True),
        ('invocation','legacyInvocationAvailable',True),('run','legacyRunReauthenticated',True),('attrs','fullOldAttributesAvailable',True),
        ('physical','legacyPhysicalHashesTransferred',True),('root','rootFailedRecoveryTargetIncluded',True),
        ('operation','actualIntentPermitOrCohortOperations',1),('manual','newManualReviews',61),('product','productTestsExecuted',1),
        ('formal','formalUpdated',True),('accepted','newAccepted',1),('effort','effortPercent',100),('violation','actualViolationCount',0)]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad,refs,rest)
        except ValueError:labels.append(label)
        else:raise ValueError('false legacy61 claim '+label)
    for label,key,value in [('reason','oldReason','changed'),('old-state','historicalWholeJoinPending','UNKNOWN'),
                            ('current-state','currentWholeSourceQualification',True),('planned','historicalPlannedTestsAvailable','UNKNOWN'),
                            ('physical','historicalPhysicalHashesUsedAsCurrent',True)]:
        bad=copy.deepcopy(refs);bad[0][key]=value
        try:contract(p,bad,rest)
        except ValueError:labels.append('row-'+label)
        else:raise ValueError('false historical/current row '+label)
    try:contract(p,refs,rest[:-1])
    except ValueError:labels.append('remaining-row')
    else:raise ValueError('missing remaining row')
    require(len(labels)==26,'finite26 metadata negatives')
    for v in (prior,obs,p):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        referencesSha256=p['referencesSha256'],queueSha256=p['queueSha256'],independentMetadataNegativeVectors=26,
        negativeLabels=labels,occurrences=61,combinedPurposeOrReferenceRows=967,remainingSelectedUnreferenced=524,
        historicalWholeJoinPendingCounts={'TRUE':39,'FALSE':22},currentWholeSourceQualification=False,
        legacyRunReauthenticated=False,oldPhysicalHashesTransferred=False,newManualReviews=0,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
