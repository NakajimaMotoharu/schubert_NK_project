"""Independent 50 old reason rows and current Source/diagnostic mapping; no monitor/native execution."""
import copy
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PARENT='PG16210-concurrency-saved50-reference-v1'
PIN='ee373a1f88e011a7b94970e0c95f70b7387181d8066508717e888bc86ad99de2'
OUT=data.BASE/'PG16212-concurrency-reference-post-v1'
RECORDS=[
 ('PG13703-current-concurrency-reason-join-recovery-v1','637d3ce581ffc589ea0519e77a1f37a5f1946dcf1070f61ebecb3132b99d98a4',
  'PG13704-current-concurrency-reason-join-post-v1','97d17086b4f150a57c5fde59e1f9f23057860ee6f9f98734ec9847a9b5c5427c',5,14,'PARENT_MONITOR_VISIBILITY_REASON_REUSE_V1'),
 ('PG14066-api-dispatch-observation-monitor-v1','7180480aee83bb1e074355f380d6f55e5dd738a1ee38b4d8d9cf6b6fd0f149e7',
  'PG14068-api-dispatch-observation-monitor-post-v1','991059acda73b03d74d4d740a830671dcb5c85e94ac8532864a8bf09a1cdb7bc',12,18,'EXPLICIT_PRIVATE_MONITOR_SOURCE_CONTEXT_V3'),
 ('PG14077-web-state-local-recording-monitor-v3','17fb76724e4105220c0c68c25baec3856d7d63f4d673000af9e02d9ab9560806',
  'PG14078-web-state-local-recording-monitor-post-v1','a0828fbe888747cdca9365ead01bba3fe2a523402b86a25f9d7bceaca7f8adf5',10,18,'EXPLICIT_PRIVATE_MONITOR_SOURCE_CONTEXT_V3'),
 ('PG14082-batch-retained-scope-monitor-v1','3ecf31a8456d8c44326f38dcbceefd7db115bc30444a79273777a1872b2dc515',
  'PG14084-batch-retained-scope-monitor-post-v1','08228ad53eddd1119bd55b1f60b29fea9a47c58029240120f14bf9887fac3ec0',23,18,'EXPLICIT_PRIVATE_MONITOR_SOURCE_CONTEXT_V3')]

def require(ok,why):
    if not ok:raise ValueError(why)

def read(name,pin):
    return data.read_checked(data.BASE/name/'manifest.json',pin)

def wire(value):
    return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=read(PARENT,PIN)
    prior=read('PG16204-throwable-identity-saved28-reference-v1','d67c8d46ee9aaa80f187bf97e76813f7949333cee54e8693b4c858095963b488')
    obs=read('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    queue=data.read_checked(data.BASE/'PG16204-throwable-identity-saved28-reference-v1/remaining-selected-review-queue.json',prior['queueSha256'])
    observations=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',obs['observationsSha256'])
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    refs=data.read_checked(data.BASE/PARENT/'references.json',p['referencesSha256']);rest=data.read_checked(data.BASE/PARENT/'remaining-selected-review-queue.json',p['queueSha256'])
    expected=[];hashes={};counts=Counter();proofs=[]
    for name,pin,post,post_pin,count,negative,schema in RECORDS:
        old,q=read(name,pin),read(post,post_pin);proofs.extend((old,q))
        require(old['actualExit']==q['actualExit']==0 and old['source']==q['source'] and q['reviewManifestSha256']==pin
                and q['metadataNegativeVectors']==negative and old['productTestsExecuted']==0,'original qualified static review')
        payload=data.read_checked(data.BASE/name/'review.json',old['reviewSha256'])
        for ordinal,row in enumerate(payload['rows']):
            matching=[v for v in queue if (v['path'],v['sourceSha256'],v['attributes'])==(row['path'],row['sourceSha256'],row['attributes'])]
            if not matching:continue
            require(len(matching)==1,'no occurrence inference');current=matching[0]
            require(row['source']==old['source'] and row['reason'] and row['rawRetained'] is row['currentWholeJoinPending'] is True
                    and row['productTestsExecuted']==0,'old reason/pending state')
            if name.startswith('PG13703'):
                require(row['reasonReused'] is True and row['newReason'] is row['historicalRuntimeTransferred'] is row['currentRuntimeQualification'] is False,'parent monitor/visibility dedicated schema')
            else:
                require(row['nativeRuntimeProven'] is row['qualityGatePass'] is row['sourceChanged'] is False
                        and row['rawDiagnosticMultiplicity']==1 and row['occurrenceOrdinal']==0 and row['monitor']
                        and isinstance(row['coordinateScope'],dict),'explicit monitor schema, no runtime or global exemption')
            raw=next(v for v in original if v['id']==row['id']);actual=next(v for v in observations if v['staticObservationId']==current['id'])
            require(raw['rowSha256']==row['originalRowSha256'] and raw['inputSha256']==current['sourceSha256'] and raw['path']==current['path']
                    and raw['attributes']==current['attributes'] and actual['currentSource']==SOURCE
                    and actual['sourceSha256']==current['sourceSha256'] and actual['path']==current['path']
                    and actual['attributes']==current['attributes'] and actual['message']==raw['message'],'all original/current diagnostic metadata')
            require('RootFailedStartRecovery.java' not in current['path'],'excluded recovery Source before content')
            body=(data.ROOT/current['path']).read_bytes();require(data.sha(body)==row['sourceSha256'],'whole Source same bytes')
            hashes[current['path']]=row['sourceSha256'];counts[name]+=1
            expected.append(dict(**current,currentSource=SOURCE,staticReviewSource=row['source'],savedSchema=schema,
                oldManifest=name,oldManifestSha256=pin,oldPostManifestSha256=post_pin,oldRowOrdinal=ordinal,
                oldReviewRowSha256=data.sha(wire(row).encode()),oldReview=row,originalDiagnosticRowSha256=raw['rowSha256'],
                diagnosticMessageSha256=data.sha(raw['message'].encode()),oldSpanOrCoordinateScopeReinterpreted=False,
                oldRuntimeTransferred=False,newNativeOrConcurrencyQualificationClaimed=False,ptExecutionExempt=False,
                meaning='SAVED_MONITOR_VISIBILITY_REASON_REFERENCE_NOT_NEW_REVIEW_OR_RUNTIME_QUALIFICATION'))
    positions={v['id']:i for i,v in enumerate(queue)};expected.sort(key=lambda v:positions[v['id']]);ids={v['id'] for v in expected}
    remaining=[v for v in queue if v['id'] not in ids]
    require(len(expected)==len(ids)==50 and len(hashes)==19 and len(remaining)==361
            and counts==Counter({v[0]:v[4] for v in RECORDS}),'all exact5+12+10+23')
    require(Counter(v['rule'] for v in expected)==Counter(AvoidSynchronizedStatement=45,AvoidSynchronizedAtMethodLevel=4,AvoidUsingVolatile=1)
            and sum(v['rule']=='AvoidSynchronizedStatement' for v in remaining)==11,'correct distinct rule domains')
    def contract(m,r,t):
        require(type(m['actualExit']) is int and m['actualExit']==0 and m['source']==SOURCE and m['sourceHashes']==hashes,'current Source binding')
        require((m['newReferenceConnections'],m['combinedSelectedReferences'],m['combinedPurposeReviewed'],m['combinedPurposeOrReferenceRows'],
                 m['remainingSelectedUnreferenced'],m['remainingStatementMonitors'],m['remainingMethodMonitors'],m['remainingVolatile'])==(50,1011,119,1130,361,11,0,0),'actual reference and rule counts')
        require(all(m[k] is False for k in ['oldRuntimeTransferred','oldSpanOrCoordinateScopeReinterpreted','newNativeOrConcurrencyQualificationClaimed',
                'sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated']) and m['actualViolationCount'] is m['effortPercent'] is None,'no native or quality promotion')
        require(all(type(m[k]) is int and m[k]==0 for k in ['newManualReviews','productTestsExecuted','oldToolsReexecuted',
                'actualMonitorsOrLifecycleOrJcaOperations','externalActions','newAccepted']),'no hidden execution or new purpose')
        require(wire(r)==wire(expected) and wire(t)==wire(remaining),'complete old reason/risk/span/multiplicity and remainder')
    contract(p,refs,rest);labels=[]
    for key,value in [('source','OLD'),('newReferenceConnections',51),('combinedSelectedReferences',1012),('combinedPurposeReviewed',169),
        ('combinedPurposeOrReferenceRows',1131),('remainingSelectedUnreferenced',0),('remainingStatementMonitors',0),('remainingMethodMonitors',4),
        ('remainingVolatile',1),('newManualReviews',50),('productTestsExecuted',50),('oldToolsReexecuted',1),('actualMonitorsOrLifecycleOrJcaOperations',1),
        ('externalActions',1),('oldRuntimeTransferred',True),('oldSpanOrCoordinateScopeReinterpreted',True),('newNativeOrConcurrencyQualificationClaimed',True),
        ('wholeF03Accepted',True),('whole451Accepted',True),('formalUpdated',True),('actualViolationCount',0),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad,refs,rest)
        except ValueError:labels.append(key)
        else:raise ValueError('false concurrency reference '+key)
    for key,value in [('oldReviewRowSha256','0'*64),('oldRuntimeTransferred',True),('ptExecutionExempt',True)]:
        bad=copy.deepcopy(refs);bad[0][key]=value
        try:contract(p,bad,rest)
        except ValueError:labels.append('row-'+key)
        else:raise ValueError('false saved monitor row')
    try:contract(p,refs,rest[:-1])
    except ValueError:labels.append('remaining-row')
    else:raise ValueError('missing remaining row')
    require(len(labels)==26,'finite26')
    for v in (*proofs,p,prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        referencesSha256=p['referencesSha256'],queueSha256=p['queueSha256'],occurrences=50,sourceCount=19,
        independentMetadataNegativeVectors=26,negativeLabels=labels,combinedPurposeOrReferenceRows=1130,
        remainingSelectedUnreferenced=361,remainingStatementMonitors=11,remainingMethodMonitors=0,remainingVolatile=0,
        productTestsExecuted=0,newManualReviews=0,oldRuntimeTransferred=False,newNativeOrConcurrencyQualificationClaimed=False,
        newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
