"""Independent old typed rows and current diagnostic/source line binding, without new type execution."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD='2f4290e7e511ea30224d087f78d44964d3488919'
PARENT='PG16204-throwable-identity-saved28-reference-v1'
PIN='d67c8d46ee9aaa80f187bf97e76813f7949333cee54e8693b4c858095963b488'
POST_PIN='2db97b5ef8db4f2c84b69c3096a3ec966d89a42529db5c7c9c3bc9956b241f4d'
TYPED_PIN='da05a736e3d76741d04e8de8b14188a5428c0ba24ecd856e242fc6b9f8c60a4d'
OUT=data.BASE/'PG16206-throwable-identity-reference-post-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(name,pin):
    return data.read_checked(data.BASE/name/'manifest.json',pin)

def wire(value):
    return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=read(PARENT,PIN)
    post=read('PG13038-throwable-identity-post-v1',POST_PIN);typed=read('PG13036-throwable-identity-types-v3',TYPED_PIN)
    prior=read('PG16199-release-collector-map3-purpose-v2','1e1efedd74db655a592a0e3f83f24bc92a5467a0e4329c8919f5cbfb99e10ecd')
    obs=read('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    require(post['actualExit']==typed['actualExit']==0 and post['source']==typed['source']==OLD and post['typedManifestSha256']==TYPED_PIN
            and post['metadataNegativeVectors']==9 and post['productClassesLoaded']==typed['productClassesLoaded']==post['productTestsExecuted']==typed['productTestsExecuted']==0,'old compiler/independent post only')
    payload=data.read_checked(data.BASE/'PG13038-throwable-identity-post-v1/review.json',post['reviewSha256'])
    queue=data.read_checked(data.BASE/'PG16199-release-collector-map3-purpose-v2/remaining-selected-review-queue.json',prior['queueSha256'])
    observations=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',obs['observationsSha256'])
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    references=data.read_checked(data.BASE/PARENT/'references.json',p['referencesSha256']);rest=data.read_checked(data.BASE/PARENT/'remaining-selected-review-queue.json',p['queueSha256'])
    expected=[];hashes={}
    for row in payload['reviewedRows']:
        original=next(v for v in raw if v['id']==row['id'])
        matches=[v for v in queue if (v['path'],v['sourceSha256'],v['attributes'])==(row['path'],row['sourceSha256'],original['attributes'])]
        require(len(matches)==1,'exact saved full Source/complete diagnostic attributes');current=matches[0]
        actual=next(v for v in observations if v['staticObservationId']==current['id'])
        require(row['typeEvidence']=='BOTH_THROWABLE_REFERENCE_TYPES' and row['leftThrowable']==row['rightThrowable']=='YES'
                and row['manualPurposeReviewComplete'] is True and row['dynamicExecutionQualificationInferred'] is False
                and row['status']=='STATIC_DIAGNOSTIC_CONTEXT_REVIEWED_DYNAMIC_HOLD' and row['reason'] and row['sourceContext']
                and row['actualViolation'] is row['actualAllocatedPp'] is None and row['additionalSharedCostPp']==0,'historical complete purpose/risk/typed information')
        require((row['originalLine'],row['originalColumn'])==(int(original['attributes']['beginline']),int(original['attributes']['begincolumn']))
                and original['inputSha256']==row['sourceSha256'] and original['path']==row['path'] and current['rule']=='CompareObjectsWithEquals'
                and actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256'] and actual['path']==current['path']
                and actual['attributes']==current['attributes'] and actual['message']==original['message'],'all raw/current identity')
        body=(data.ROOT/row['path']).read_bytes();require(data.sha(body)==row['sourceSha256']
                and body.decode().splitlines()[row['astLine']-1].strip()==row['sourceSnippet'],'whole byte Source and saved AST-line expression')
        hashes[row['path']]=row['sourceSha256']
        expected.append(dict(**current,currentSource=SOURCE,staticReviewSource=OLD,
            savedSchema='JAVAC_TYPED_THROWABLE_REFERENCE_PURPOSE_WITH_DYNAMIC_HOLD_V1',oldPostManifestSha256=POST_PIN,oldTypedManifestSha256=TYPED_PIN,
            oldReviewId=row['id'],oldReviewRowSha256=data.sha(wire(row).encode()),oldReview=row,
            originalDiagnosticRowSha256=original['rowSha256'],diagnosticMessageSha256=data.sha(original['message'].encode()),
            oldTypeClasspathReassigned=False,newCurrentTypeAnalysisClaimed=False,oldRuntimeTransferred=False,ptExecutionExempt=False,
            meaning='SAVED_EXACT_SOURCE_TYPE_PURPOSE_REFERENCE_NOT_NEW_CURRENT_TYPE_OR_DYNAMIC_QUALIFICATION'))
    positions={v['id']:i for i,v in enumerate(queue)};expected.sort(key=lambda v:positions[v['id']]);ids={v['id'] for v in expected}
    remaining=[v for v in queue if v['id'] not in ids]
    require(len(expected)==len(ids)==28 and len(hashes)==18 and len(remaining)==411
            and len(payload['typedNonThrowableUnclassified'])==28 and not any(v['rule']=='CompareObjectsWithEquals' for v in remaining),'all saved28, untouched nonThrowable domain and remaining')
    def contract(m,r,t):
        require(type(m['actualExit']) is int and m['actualExit']==0 and m['source']==SOURCE and m['staticReviewSource']==OLD and m['sourceHashes']==hashes,'full source binding')
        require((m['newReferenceConnections'],m['combinedSelectedReferences'],m['combinedPurposeReviewed'],m['combinedPurposeOrReferenceRows'],
                 m['remainingSelectedUnreferenced'],m['remainingCompareObjectsWithEquals'])==(28,961,119,1080,411,0),'exact reference/purpose domains')
        require(all(m[k] is False for k in ['newCurrentTypeAnalysisClaimed','oldTypeClasspathReassigned','oldRuntimeTransferred','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated'])
                and m['actualViolationCount'] is m['effortPercent'] is None,'no current type/whole/runtime promotion')
        require(all(type(m[k]) is int and m[k]==0 for k in ['newManualReviews','productTestsExecuted','oldTypeCheckerReexecuted',
                'actualProductClassFilesReadOrLoaded','actualGraphOrCleanupInvocations','externalActions','newAccepted']),'no actual hidden operation')
        require(wire(r)==wire(expected) and wire(t)==wire(remaining),'every original type/purpose/hash/coordinate and remainder preserved')
    contract(p,references,rest);labels=[]
    vectors=[('source','OLD'),('newReferenceConnections',29),('combinedSelectedReferences',962),('combinedPurposeReviewed',147),
        ('combinedPurposeOrReferenceRows',1081),('remainingSelectedUnreferenced',0),('remainingCompareObjectsWithEquals',28),
        ('newManualReviews',28),('productTestsExecuted',28),('oldTypeCheckerReexecuted',1),('actualProductClassFilesReadOrLoaded',1),
        ('actualGraphOrCleanupInvocations',1),('newCurrentTypeAnalysisClaimed',True),('oldTypeClasspathReassigned',True),('oldRuntimeTransferred',True),
        ('sourceChanged',True),('wholeF03Accepted',True),('whole451Accepted',True),('formalUpdated',True),('newAccepted',1),('actualViolationCount',0),('effortPercent',100)]
    for key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad,references,rest)
        except ValueError:labels.append(key)
        else:raise ValueError('false old typing reference '+key)
    for key,value in [('oldReviewRowSha256','0'*64),('ptExecutionExempt',True),('oldTypeClasspathReassigned',True)]:
        bad=copy.deepcopy(references);bad[0][key]=value
        try:contract(p,bad,rest)
        except ValueError:labels.append('row-'+key)
        else:raise ValueError('false old review qualification')
    try:contract(p,references,rest[:-1])
    except ValueError:labels.append('remaining-row')
    else:raise ValueError('missing remaining row')
    require(len(labels)==26,'finite26')
    for v in (p,post,prior,obs):verify(v['invocation'])
    verify(typed['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        referencesSha256=p['referencesSha256'],queueSha256=p['queueSha256'],occurrences=28,sourceCount=18,
        independentMetadataNegativeVectors=26,negativeLabels=labels,combinedPurposeOrReferenceRows=1080,
        remainingSelectedUnreferenced=411,remainingCompareObjectsWithEquals=0,newManualReviews=0,productTestsExecuted=0,
        oldTypeClasspathReassigned=False,newCurrentTypeAnalysisClaimed=False,oldRuntimeTransferred=False,
        newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
