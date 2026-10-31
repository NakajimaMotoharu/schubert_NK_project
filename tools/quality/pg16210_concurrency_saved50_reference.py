"""Saved monitor/visibility reasons only; no locks, native resources, keys or lifecycle actions."""
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
SPECS=[
 ('PG13703-current-concurrency-reason-join-recovery-v1','637d3ce581ffc589ea0519e77a1f37a5f1946dcf1070f61ebecb3132b99d98a4',
  'PG13704-current-concurrency-reason-join-post-v1','97d17086b4f150a57c5fde59e1f9f23057860ee6f9f98734ec9847a9b5c5427c',5,5,14,'PARENT_MONITOR_VISIBILITY_REASON_REUSE_V1'),
 ('PG14066-api-dispatch-observation-monitor-v1','7180480aee83bb1e074355f380d6f55e5dd738a1ee38b4d8d9cf6b6fd0f149e7',
  'PG14068-api-dispatch-observation-monitor-post-v1','991059acda73b03d74d4d740a830671dcb5c85e94ac8532864a8bf09a1cdb7bc',12,12,18,'EXPLICIT_PRIVATE_MONITOR_SOURCE_CONTEXT_V3'),
 ('PG14077-web-state-local-recording-monitor-v3','17fb76724e4105220c0c68c25baec3856d7d63f4d673000af9e02d9ab9560806',
  'PG14078-web-state-local-recording-monitor-post-v1','a0828fbe888747cdca9365ead01bba3fe2a523402b86a25f9d7bceaca7f8adf5',10,10,18,'EXPLICIT_PRIVATE_MONITOR_SOURCE_CONTEXT_V3'),
 ('PG14082-batch-retained-scope-monitor-v1','3ecf31a8456d8c44326f38dcbceefd7db115bc30444a79273777a1872b2dc515',
  'PG14084-batch-retained-scope-monitor-post-v1','08228ad53eddd1119bd55b1f60b29fea9a47c58029240120f14bf9887fac3ec0',37,23,18,'EXPLICIT_PRIVATE_MONITOR_SOURCE_CONTEXT_V3')]
PRIOR=('PG16204-throwable-identity-saved28-reference-v1','d67c8d46ee9aaa80f187bf97e76813f7949333cee54e8693b4c858095963b488')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
OUT=data.BASE/'PG16210-concurrency-saved50-reference-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(name,pin):
    return data.read_checked(data.BASE/name/'manifest.json',pin)

def signature(v):
    return json.dumps([v['path'],v['sourceSha256'],v['attributes']],sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs=[read(*v) for v in (PRIOR,OBS)];inputs=[prior,obs];saved={}
    common={'id','path','source','sourceSha256','rule','attributes','originalRowSha256','reason','rawRetained','currentWholeJoinPending','productTestsExecuted','canonicalOwner','canonicalCostOwner'}
    for name,pin,post,post_pin,total,selected,negative,schema in SPECS:
        old,p=read(name,pin),read(post,post_pin)
        require(old['actualExit']==p['actualExit']==0 and old['source']==p['source'] and p['reviewManifestSha256']==pin
                and p['metadataNegativeVectors']==negative and old['productTestsExecuted']==0,'qualified saved source review only')
        payload=data.read_checked(data.BASE/name/'review.json',old['reviewSha256']);rows=payload['rows']
        require(len(rows)==total and payload['source']==old['source'] and all(common<=set(v) for v in rows),'actual common schema before access')
        for ordinal,v in enumerate(rows):
            require(v['source']==old['source'] and v['reason'] and v['rawRetained'] is v['currentWholeJoinPending'] is True
                    and v['productTestsExecuted']==0,'saved individual reason retained, no Product execution')
            if schema.startswith('PARENT_'):
                require(v['reasonReused'] is True and v['newReason'] is v['historicalRuntimeTransferred'] is v['currentRuntimeQualification'] is False,'explicit five old reasons only')
            else:
                require(v['sourceChanged'] is v['qualityGatePass'] is v['nativeRuntimeProven'] is False
                        and v['occurrenceOrdinal']==0 and v['rawDiagnosticMultiplicity']==1
                        and v['monitor'] and isinstance(v['coordinateScope'],dict),'private monitor reason not universal or native acceptance')
            require(signature(v) not in saved,'unambiguous whole signature')
            saved[signature(v)]=(name,pin,post_pin,schema,ordinal,v)
        inputs.extend((old,p))
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==411 and prior['combinedSelectedReferences']==961 and prior['combinedPurposeReviewed']==119,'prior count domains')
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');raw={v['id']:v for v in raw}
    actual=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256']);actual={v['staticObservationId']:v for v in actual}
    refs=[];hashes={};counts=Counter()
    for current in queue:
        if signature(current) not in saved:continue
        name,pin,post_pin,schema,ordinal,v=saved[signature(current)];o=raw[v['id']];a=actual[current['id']]
        require(o['rowSha256']==v['originalRowSha256'] and o['inputSha256']==v['sourceSha256'] and o['path']==v['path']
                and o['attributes']==v['attributes'] and a['currentSource']==SOURCE and a['sourceSha256']==current['sourceSha256']
                and a['path']==current['path'] and a['attributes']==current['attributes'] and a['message']==o['message'],'full original/current diagnostic')
        require('RootFailedStartRecovery.java' not in current['path'],'exclude held recovery Source before content')
        body=(data.ROOT/current['path']).read_bytes();require(data.sha(body)==v['sourceSha256'],'whole byte-exact current Source')
        hashes[current['path']]=v['sourceSha256'];counts[name]+=1
        refs.append(dict(**current,currentSource=SOURCE,staticReviewSource=v['source'],savedSchema=schema,
            oldManifest=name,oldManifestSha256=pin,oldPostManifestSha256=post_pin,oldRowOrdinal=ordinal,
            oldReviewRowSha256=data.sha(json.dumps(v,sort_keys=True).encode()),oldReview=v,
            originalDiagnosticRowSha256=o['rowSha256'],diagnosticMessageSha256=data.sha(a['message'].encode()),
            oldSpanOrCoordinateScopeReinterpreted=False,oldRuntimeTransferred=False,newNativeOrConcurrencyQualificationClaimed=False,
            ptExecutionExempt=False,meaning='SAVED_MONITOR_VISIBILITY_REASON_REFERENCE_NOT_NEW_REVIEW_OR_RUNTIME_QUALIFICATION'))
    require(len(refs)==len({v['id'] for v in refs})==50 and len(hashes)==19
            and counts==Counter({v[0]:v[5] for v in SPECS}),'five plus12 plus10 plus23 exact')
    ids={v['id'] for v in refs};remaining=[v for v in queue if v['id'] not in ids]
    require(Counter(v['rule'] for v in refs)==Counter(AvoidSynchronizedStatement=45,AvoidSynchronizedAtMethodLevel=4,AvoidUsingVolatile=1),'correct rule domains')
    for v in inputs:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'references.json',refs);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,oldReviewSpecs=SPECS,sourceHashes=hashes,
        priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],referencesSha256=data.sha((OUT/'references.json').read_bytes()),
        queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),newReferenceConnections=50,
        combinedSelectedReferences=1011,combinedPurposeReviewed=119,combinedPurposeOrReferenceRows=1130,remainingSelectedUnreferenced=361,
        remainingStatementMonitors=11,remainingMethodMonitors=0,remainingVolatile=0,newManualReviews=0,
        oldRuntimeTransferred=False,oldSpanOrCoordinateScopeReinterpreted=False,newNativeOrConcurrencyQualificationClaimed=False,
        productTestsExecuted=0,oldToolsReexecuted=0,actualMonitorsOrLifecycleOrJcaOperations=0,externalActions=0,sourceChanged=False,
        actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
