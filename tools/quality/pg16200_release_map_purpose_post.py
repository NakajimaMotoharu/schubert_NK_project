"""Independent byte-prefix/caller anchors; manual purposes are not dynamic semantic verdicts."""
import copy
import json
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PARENT='PG16199-release-collector-map3-purpose-v2'
PIN='1e1efedd74db655a592a0e3f83f24bc92a5467a0e4329c8919f5cbfb99e10ecd'
PATH='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/ReleasePayloadVerification.java'
CALLER='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/StartupReleaseManifest.java'
HASHES={PATH:'01dfe01fe186a9fe8e65098bb2a020cb8f4855e9033043c89696998262dec348',CALLER:'3f2ae514697c8bac938eb9e0202a4e25346774b8875ce08c63d8117538753937'}
OUT=data.BASE/'PG16200-release-map-purpose-post-v1'
FIELD='Two private final builder fields belong to each fresh package-private final collector constructed inline per verify or verifyCandidate. No collector/map is returned or cached by current callers; published Contents uses separate unmodifiable inventory values. This is source-use intent, not arbitrary concurrent reuse or execution proof.'
LOCAL='Archive callback builds a fresh SQL map sequentially, then Map.copyOf isolates it in the private JarValue result. No mutable SQL builder is returned. Actual archive reading and checksum execution remain unperformed by this review.'
RISK='Source inspection and exact anchors are not a type/escape/CFG proof or actual filesystem, callback scheduling, ownership, signature or release-verification acceptance.'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(name,pin):
    return data.read_checked(data.BASE/name/'manifest.json',pin)

def wire(v):
    return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=read(PARENT,PIN)
    prior=read('PG16192-local-map-saved16-reference-v1','6890bbcecedfd87b8f0c78a5b337ce119963b7a912bc912b26de6f129dce57b0')
    obs=read('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    queue=data.read_checked(data.BASE/'PG16192-local-map-saved16-reference-v1/remaining-selected-review-queue.json',prior['queueSha256'])
    observations=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',obs['observationsSha256'])
    old=read('PG12260-bundle-maps-context-v1','8afbd022d68c9437ef6854aa51c69a705a456d2311f76946f52d0a10011b6a05')
    old_rows=data.read_checked(data.BASE/'PG12260-bundle-maps-context-v1/review.json',old['reviewSha256'])['rows']
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    purposes=data.read_checked(data.BASE/PARENT/'purposes.json',p['purposesSha256']);rest=data.read_checked(data.BASE/PARENT/'remaining-selected-review-queue.json',p['queueSha256'])
    texts={path:(data.ROOT/path).read_text() for path in HASHES};require(all(data.sha(v.encode())==HASHES[k] for k,v in texts.items()),'whole Source byte pins')
    body=texts[PATH];caller=texts[CALLER]
    require('final class ReleasePayloadVerification {' in body and all(v in body for v in
            ['private final Map<String, JarValue> jars = new HashMap<>();','private final Map<String, Integer> checksums = new HashMap<>();',
             'Map<String, String> sql = new HashMap<>();','return new JarValue(Set.copyOf(classes), Map.copyOf(sql));']),'independent declarations and result-copy anchors')
    require(len(re.findall(r'new\s+ReleasePayloadVerification\(this,\s*group,\s*io,\s*security\)\s*\.verify\(release,\s*version,\s*approval\)',caller))==2
            and 'public Contents verify(' in caller and 'public Contents verifyCandidate(' in caller,'two current construction paths, not reflection proof')
    package_hashes={};hits={}
    for file in sorted((data.ROOT/PATH).parent.glob('*.java')):
        relative=str(file.relative_to(data.ROOT));blob=file.read_bytes();package_hashes[relative]=data.sha(blob)
        count=len(re.findall(rb'new\s+ReleasePayloadVerification\(',blob))
        if count:hits[relative]=count
    require(len(package_hashes)==18 and hits=={CALLER:2},'same-package bounded inventory')
    selected=[v for v in queue if v['rule']=='UseConcurrentHashMap'];expected=[]
    for current in selected:
        a=current['attributes'];variable=a['variable'];local=variable=='sql'
        require(current['path']==PATH and (variable,int(a['beginline'])) in [('jars',49),('checksums',50),('sql',297)],'three actual variable coordinates')
        original_context=next(v for v in old_rows if v['path']==PATH and v['attributes']==a);original=next(v for v in raw if v['id']==original_context['id'])
        actual=next(v for v in observations if v['staticObservationId']==current['id'])
        require(original_context['sourceSha256']==original['inputSha256']!=HASHES[PATH]
                and original_context['originalRowSha256']==original['rowSha256'] and original['attributes']==a
                and actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256']==HASHES[PATH]
                and actual['attributes']==a and actual['path']==original['path']==PATH and actual['message']==original['message'],'old/new Source separated with whole diagnostic identity')
        lines=body.encode().splitlines(keepends=True);last=int(a['endline']);prefix=b''.join(lines[:last])
        require(prefix.isascii() and all(v not in prefix for v in [b'\\u',b'\r',b'\0',b'\t',b'\v',b'\f'])
                and body.index('\\u')>len(prefix),'target prefix precedes every Java Unicode escape')
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
        end=sum(map(len,lines[:last-1]))+int(a['endcolumn'])-1
        require(body.encode()[start:end].decode()==variable+' = new HashMap<>()','independent exact byte columns/token')
        expected.append(dict(**current,currentSource=SOURCE,reviewStatus='CURRENT_STATIC_MAP_PURPOSE_REVIEW_COMPLETE_NOT_EXECUTED',
            role='LOCAL_COPY' if local else 'FIELD_CONFINED_COLLECTOR',manualPurpose=LOCAL if local else FIELD,residualRisk=RISK,
            originalFindingId=original['id'],originalRowSha256=original['rowSha256'],originalInputSha256=original['inputSha256'],
            originalDiagnosticSha256=data.sha(original['message'].encode()),oldWholeSourceMismatchNotReused=True,
            canonicalSpanStart=start,canonicalSpanEndExclusive=end,canonicalSpanSha256=data.sha(body.encode()[start:end]),
            spanBasis='RAW_ASCII_PREFIX_FROM_FILE_START_BEFORE_LATER_UNICODE_ESCAPE',productTestsExecuted=0,ptExecutionExempt=False,currentWholeCaseRefs=[]))
    ids={v['id'] for v in expected};remaining=[v for v in queue if v['id'] not in ids]
    require(len(expected)==3 and len(remaining)==439 and not any(v['rule']=='UseConcurrentHashMap' for v in remaining),'all three purposes, no raw suppression')
    def contract(m,r,t):
        require(type(m['actualExit']) is int and m['actualExit']==0 and m['source']==SOURCE and m['currentSourceHashes']==HASHES
                and m['callerPackageSourceHashes']==package_hashes and m['callerConstructionCounts']==hits,'full current source/caller binding')
        require((m['combinedSelectedReferences'],m['combinedPurposeReviewed'],m['combinedPurposeOrReferenceRows'],m['remainingSelectedUnreferenced'],
                 m['remainingUseConcurrentHashMap'],m['newManualReviews'],m['newReferenceConnections'])==(933,119,1052,439,0,3,0),'purpose/reference domains distinct')
        require(m['boundedAsciiPrefixSpans'] is True and m['prefixMetadataNegativeVectors']==6 and m['prefixMetadataPositiveVectors']==1,'bounded prefix not global reader relaxation')
        require(all(type(m[k]) is int and m[k]==0 for k in ['productTestsExecuted','actualReleaseVerificationOrSigningOrPublicationCalls','externalActions','newAccepted'])
                and all(m[k] is False for k in ['oldWholeSourceQualificationTransferred','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated'])
                and m['actualViolationCount'] is m['effortPercent'] is None,'source purpose not dynamic qualification')
        require(wire(r)==wire(expected) and wire(t)==wire(remaining),'manual anchors/risk and independent byte reconstruction')
    contract(p,purposes,rest);labels=[]
    for key,value in [('source','OLD'),('currentSourceHashes',{}),('callerPackageSourceHashes',{}),('callerConstructionCounts',{}),
        ('combinedSelectedReferences',936),('combinedPurposeReviewed',116),('combinedPurposeOrReferenceRows',1049),('remainingSelectedUnreferenced',0),
        ('remainingUseConcurrentHashMap',3),('newManualReviews',0),('newReferenceConnections',3),('productTestsExecuted',3),
        ('actualReleaseVerificationOrSigningOrPublicationCalls',1),('externalActions',1),('sourceChanged',True),('oldWholeSourceQualificationTransferred',True),
        ('wholeF03Accepted',True),('whole451Accepted',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('actualViolationCount',0)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad,purposes,rest)
        except ValueError:labels.append(key)
        else:raise ValueError('false map-purpose metadata '+key)
    for key,value in [('role','UNKNOWN'),('manualPurpose','changed'),('canonicalSpanStart',0)]:
        bad=copy.deepcopy(purposes);bad[0][key]=value
        try:contract(p,bad,rest)
        except ValueError:labels.append('row-'+key)
        else:raise ValueError('false purpose row')
    try:contract(p,purposes,rest[:-1])
    except ValueError:labels.append('remaining-row')
    else:raise ValueError('missing remaining row')
    require(len(labels)==26,'finite26')
    for v in (p,prior,obs,old):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        purposesSha256=p['purposesSha256'],queueSha256=p['queueSha256'],independentMetadataNegativeVectors=26,negativeLabels=labels,
        reviewedPurposes=3,independentlyReconstructedByteSpans=3,sourceCallerPackageSize=18,
        combinedPurposeOrReferenceRows=1052,remainingSelectedUnreferenced=439,remainingUseConcurrentHashMap=0,
        purposeMeaning='MANUAL_PURPOSE_RISK_ANCHORS_PLUS_SOURCE_GUARDS_NOT_DYNAMIC_TYPE_ESCAPE_OR_SEMANTIC_VERDICT',
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
