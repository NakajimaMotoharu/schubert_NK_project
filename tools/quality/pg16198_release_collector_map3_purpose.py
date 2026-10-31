"""Current manual source-purpose anchors for three maps; never verify a release or invoke Product."""
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pmd_source_span_ascii import span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE='d8a2b7952b321b75fe7fcc1c8d3acb287faca6ec'
PATH='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/ReleasePayloadVerification.java'
CALLER='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/StartupReleaseManifest.java'
MAIN_PIN='01dfe01fe186a9fe8e65098bb2a020cb8f4855e9033043c89696998262dec348'
CALLER_PIN='3f2ae514697c8bac938eb9e0202a4e25346774b8875ce08c63d8117538753937'
PRIOR=('PG16192-local-map-saved16-reference-v1','6890bbcecedfd87b8f0c78a5b337ce119963b7a912bc912b26de6f129dce57b0')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
OUT=data.BASE/'PG16198-release-collector-map3-purpose-v1'
FIELD_PURPOSE='Two private final builder fields belong to each fresh package-private final collector constructed inline per verify or verifyCandidate. No collector/map is returned or cached by current callers; published Contents uses separate unmodifiable inventory values. This is source-use intent, not arbitrary concurrent reuse or execution proof.'
LOCAL_PURPOSE='Archive callback builds a fresh SQL map sequentially, then Map.copyOf isolates it in the private JarValue result. No mutable SQL builder is returned. Actual archive reading and checksum execution remain unperformed by this review.'
RISK='Source inspection and exact anchors are not a type/escape/CFG proof or actual filesystem, callback scheduling, ownership, signature or release-verification acceptance.'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs=[read(v) for v in (PRIOR,OBS)]
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    observations=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])
    old=read(('PG12260-bundle-maps-context-v1','8afbd022d68c9437ef6854aa51c69a705a456d2311f76946f52d0a10011b6a05'))
    payload=data.read_checked(data.BASE/'PG12260-bundle-maps-context-v1/review.json',old['reviewSha256'])
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    body=(data.ROOT/PATH).read_text();caller=(data.ROOT/CALLER).read_text()
    require(data.sha(body.encode())==MAIN_PIN and data.sha(caller.encode())==CALLER_PIN,'whole current two Sources')
    historic=subprocess.check_output(['git','show',OLD_SOURCE+':'+PATH],cwd=data.ROOT).decode()
    before='          String line;\n          while ((line = reader.readLine()) != null) {\n'
    after='          // PG-D804/2476: keep one read, then null termination, before the original body.\n          while (true) {\n            String line = reader.readLine();\n            if (line == null) break;\n'
    require(historic.count(before)==1 and historic.replace(before,after)==body,'entire old/current delta only known checksum loop, not old proof transfer')
    compact=''.join(body.split());caller_compact=''.join(caller.split())
    require(all(v in compact for v in ['finalclassReleasePayloadVerification{','privatefinalMap<String,JarValue>jars=newHashMap<>();',
        'privatefinalMap<String,Integer>checksums=newHashMap<>();','Map<String,String>sql=newHashMap<>();',
        'returnnewJarValue(Set.copyOf(classes),Map.copyOf(sql));','Collectors.toUnmodifiableMap(']),'current field/local/copy controls')
    require(caller_compact.count('newReleasePayloadVerification(this,group,io,security).verify(release,version,approval)')==2,'two inline construction-and-use expressions')
    package=(data.ROOT/PATH).parent;package_hashes={};hits={}
    for file in sorted(package.glob('*.java')):
        require(file.name not in {'RootFailedStartRecovery.java'},'exclude held Source before content')
        text=file.read_text();relative=str(file.relative_to(data.ROOT));package_hashes[relative]=data.sha(text.encode())
        count=text.count('new ReleasePayloadVerification(')
        if count:hits[relative]=count
    require(len(package_hashes)==18 and hits=={CALLER:2},'bounded same-package construction inventory')
    design='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'
    approved=(data.ROOT/design).read_bytes();require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT)
            and data.sha(approved)=='d8be70ce4c170df7939f7803723bb021c99ba40a72819f9b5d861731425332b2','approved SS exact')
    selected=[v for v in queue if v['rule']=='UseConcurrentHashMap'];require(len(queue)==442 and len(selected)==3 and all(v['path']==PATH for v in selected),'all remaining maps only')
    purposes=[]
    for current in selected:
        previous=next(v for v in payload['rows'] if v['path']==PATH and v['attributes']==current['attributes'])
        original=next(v for v in raw if v['id']==previous['id']);actual=next(v for v in observations if v['staticObservationId']==current['id'])
        require(original['rowSha256']==previous['originalRowSha256'] and original['inputSha256']==previous['sourceSha256']
                and previous['sourceSha256']!=MAIN_PIN and actual['sourceSha256']==current['sourceSha256']==MAIN_PIN
                and actual['currentSource']==SOURCE and actual['attributes']==original['attributes']==current['attributes']
                and actual['path']==original['path']==PATH and actual['message']==original['message'],'old raw/current Source distinct, diagnostic exact')
        a=current['attributes'];kind='LOCAL_COPY' if a.get('method')=='archive' else 'FIELD_CONFINED_COLLECTOR'
        require((a['variable'],kind) in [('jars','FIELD_CONFINED_COLLECTOR'),('checksums','FIELD_CONFINED_COLLECTOR'),('sql','LOCAL_COPY')],'explicit three variable roles')
        start,end,token=span(body,a)
        purposes.append(dict(**current,currentSource=SOURCE,reviewStatus='CURRENT_STATIC_MAP_PURPOSE_REVIEW_COMPLETE_NOT_EXECUTED',
            role=kind,manualPurpose=LOCAL_PURPOSE if kind=='LOCAL_COPY' else FIELD_PURPOSE,residualRisk=RISK,
            originalFindingId=original['id'],originalRowSha256=original['rowSha256'],originalInputSha256=original['inputSha256'],
            originalDiagnosticSha256=data.sha(original['message'].encode()),oldWholeSourceMismatchNotReused=True,
            canonicalSpanStart=start,canonicalSpanEndExclusive=end,canonicalSpanSha256=data.sha(token.encode()),
            productTestsExecuted=0,ptExecutionExempt=False,currentWholeCaseRefs=[]))
    ids={v['id'] for v in purposes};remaining=[v for v in queue if v['id'] not in ids]
    for v in (prior,obs,old):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'purposes.json',purposes);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,currentSourceHashes={PATH:MAIN_PIN,CALLER:CALLER_PIN},
        callerPackageSourceHashes=package_hashes,callerConstructionCounts=hits,approvedDesignSha256=data.sha(approved),
        priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],purposesSha256=data.sha((OUT/'purposes.json').read_bytes()),
        queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),newManualReviews=3,newReferenceConnections=0,
        combinedSelectedReferences=933,combinedPurposeReviewed=119,combinedPurposeOrReferenceRows=1052,remainingSelectedUnreferenced=439,
        remainingUseConcurrentHashMap=0,oldWholeSourceQualificationTransferred=False,productTestsExecuted=0,
        actualReleaseVerificationOrSigningOrPublicationCalls=0,externalActions=0,sourceChanged=False,
        actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
