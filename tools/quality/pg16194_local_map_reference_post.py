"""Independent original-row, saved-reason and whole-current-source connection for sixteen maps."""
import copy
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PARENT='PG16192-local-map-saved16-reference-v1'
PIN='6890bbcecedfd87b8f0c78a5b337ce119963b7a912bc912b26de6f129dce57b0'
OUT=data.BASE/'PG16194-local-map-reference-post-v1'
RECORDS=[
 ('PG12246-main-local-maps-context-v1','1481093beb6c7d9642959dcd0b4b956236fda824f2df97379cbaf5ec23d7948e',
  'PG12248-main-local-maps-post-v1','6167dcf7e8671527f16ec20d4c6f0f2fe2b02257a9b404a03719bd588b900fb3',4,14,'LOCAL_METHOD_COPY_V1'),
 ('PG12260-bundle-maps-context-v1','8afbd022d68c9437ef6854aa51c69a705a456d2311f76946f52d0a10011b6a05',
  'PG12262-bundle-maps-post-v1','61523ad29196dabd3f8084ec237515022d661109bdcd00bce24c57b84f495297',4,20,'BUNDLE_SCOPE_COLLECTOR_V1'),
 ('PG12334-remaining-main-maps-context-v1','4227b10cee4cf12fdb0bf19af53bd3f75236625d4470680294fa8d80cb91a17e',
  'PG12336-remaining-main-maps-post-v1','e180597ce36baed2150998a199c08d182ca79f147fd08f8b1ef36abf36b02db0',8,28,'PRIVATE_LOCAL_COPY_STRATEGY_V1')]

def require(ok,why):
    if not ok:raise ValueError(why)

def read(name,pin):
    return data.read_checked(data.BASE/name/'manifest.json',pin)

def wire(v):
    return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=read(PARENT,PIN)
    prior=read('PG16154-emptycatch-saved10-reference-v1','f4bb9c080f06e141564e17ce743821528786476ffe4eef8ef040a4bb93e5a9d2')
    obs=read('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    queue=data.read_checked(data.BASE/'PG16154-emptycatch-saved10-reference-v1/remaining-selected-review-queue.json',prior['queueSha256'])
    observations=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',obs['observationsSha256'])
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    refs=data.read_checked(data.BASE/PARENT/'references.json',p['referencesSha256']);rest=data.read_checked(data.BASE/PARENT/'remaining-selected-review-queue.json',p['queueSha256'])
    expected=[];hashes={};proofs=[];counts=Counter()
    for name,pin,post,post_pin,count,negative,schema in RECORDS:
        old,q=read(name,pin),read(post,post_pin);proofs.extend((old,q))
        require(old['actualExit']==q['actualExit']==0 and old['source']==q['source'] and q['reviewManifestSha256']==pin
                and q['metadataNegativeVectors']==negative and old['productTestsExecuted']==0,'exact old whole review proof')
        payload=data.read_checked(data.BASE/name/'review.json',old['reviewSha256'])
        for ordinal,row in enumerate(payload['rows']):
            matches=[v for v in queue if (v['path'],v['sourceSha256'],v['attributes'])==(row['path'],row['sourceSha256'],row['attributes'])]
            if not matches:continue
            require(len(matches)==1,'one current exact signature');current=matches[0]
            require(row['source']==old['source'] and row['sourceKind']=='MAIN' and row['rule']=='UseConcurrentHashMap'
                    and row['disposition']=='CONTEXT_NOT_APPLICABLE' and row['reason'] and row['controls']
                    and row['currentWholeJoinPending'] is True and row['oldRuntimeReassigned'] is False
                    and row['newAccepted']==row['productTestsExecutedByReview']==0
                    and 'message' not in row and 'ptExecutionExempt' not in row,'historical reasons, not current PT')
            original=next(v for v in raw if v['id']==row['id']);actual=next(v for v in observations if v['staticObservationId']==current['id'])
            require(original['rowSha256']==row['originalRowSha256'] and original['inputSha256']==current['sourceSha256']
                    and original['path']==current['path'] and original['attributes']==current['attributes']
                    and actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256']
                    and actual['path']==current['path'] and actual['attributes']==current['attributes'] and actual['message']==original['message'],'all raw/current diagnostic fields')
            body=(data.ROOT/current['path']).read_text();require(data.sha(body.encode())==current['sourceSha256'],'whole exact byte Source')
            a=current['attributes'];lines=body.splitlines(keepends=True)
            start=sum(len(v) for v in lines[:int(a['beginline'])-1])+int(a['begincolumn'])-1
            end=sum(len(v) for v in lines[:int(a['endline'])-1])+int(a['endcolumn'])-1
            hashes[current['path']]=current['sourceSha256'];counts[name]+=1
            expected.append(dict(**current,currentSource=SOURCE,staticReviewSource=old['source'],savedSchema=schema,
                oldManifest=name,oldManifestSha256=pin,oldPostManifestSha256=post_pin,oldRowOrdinal=ordinal,
                oldRowSha256=data.sha(wire(row).encode()),oldFindingId=row['id'],oldReason=row['reason'],oldKind=row['kind'],
                oldDisposition=row['disposition'],oldControls=row['controls'],oldCanonicalOwner=row['canonicalOwner'],
                oldCanonicalCostOwner=row['canonicalCostOwner'],oldSourceSpanSha256=row['sourceSpanSha256'],
                oldSpanInterpretation='HISTORICAL_SCHEMA_ONLY_NOT_REINTERPRETED_AS_NEW_CANONICAL_SPAN',
                oldCurrentProductQualification=row['currentProductQualification'],oldRuntimeTransferred=False,
                originalDiagnosticRowSha256=row['originalRowSha256'],diagnosticMessageSha256=data.sha(original['message'].encode()),
                oldMessageFieldAvailable=False,oldPtExemptionFieldAvailable=False,currentPtExecutionExempt=False,
                canonicalSpanStart=start,canonicalSpanEndExclusive=end,canonicalSpanSha256=data.sha(body[start:end].encode()),
                meaning='SAVED_MAP_REASON_REFERENCE_NOT_NEW_REVIEW_RUNTIME_OR_APPLICABILITY_ACCEPTANCE'))
    positions={v['id']:i for i,v in enumerate(queue)};expected.sort(key=lambda v:positions[v['id']]);ids={v['id'] for v in expected}
    remaining=[v for v in queue if v['id'] not in ids]
    require(len(expected)==len(ids)==16 and len(hashes)==7 and len(remaining)==442
            and counts==Counter({v[0]:v[4] for v in RECORDS}),'exact16, excluded changedSource never rebound')
    require(sum(v['oldCurrentProductQualification'] is not None for v in expected)==1,'one old Asset runtime kept historical only')
    def contract(m,r,t):
        require(type(m['actualExit']) is int and m['actualExit']==0 and m['source']==SOURCE and m['sourceHashes']==hashes,'same source identity')
        require((m['newReferenceConnections'],m['combinedSelectedReferences'],m['combinedPurposeReviewed'],m['combinedPurposeOrReferenceRows'],m['remainingSelectedUnreferenced'])
                ==(16,933,116,1049,442),'three exact reference domains')
        require(all(m[k] is False for k in ['oldRuntimeTransferred','oldSpanReinterpreted','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated'])
                and m['actualViolationCount'] is m['effortPercent'] is None,'no current runtime or quality upgrade')
        require(all(type(m[k]) is int and m[k]==0 for k in ['newManualReviews','productTestsExecuted','oldProductToolsReexecuted',
                'actualMapOrRetirementOrBackupOperations','externalActions','rawSuppressed','newAccepted']),'no new Product or actual operations')
        require(wire(r)==wire(expected) and wire(t)==wire(remaining),'all saved reasons/hashes/owners/span conventions and remainder')
    contract(p,refs,rest);labels=[]
    for key,value in [('source','OLD'),('newReferenceConnections',17),('combinedSelectedReferences',934),('combinedPurposeReviewed',132),
        ('remainingSelectedUnreferenced',0),('newManualReviews',16),('productTestsExecuted',16),('oldProductToolsReexecuted',1),
        ('actualMapOrRetirementOrBackupOperations',1),('externalActions',1),('rawSuppressed',16),('actualViolationCount',0),
        ('effortPercent',100),('formalUpdated',True),('whole451Accepted',True),('newAccepted',1),('oldRuntimeTransferred',True),
        ('oldSpanReinterpreted',True),('sourceChanged',True),('wholeF03Accepted',True)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad,refs,rest)
        except ValueError:labels.append(key)
        else:raise ValueError('false map metadata '+key)
    for key,value in [('oldReason','changed'),('oldDisposition','PASS'),('oldSourceSpanSha256','0'*64),('currentPtExecutionExempt',True),('oldRuntimeTransferred',True)]:
        bad=copy.deepcopy(refs);bad[0][key]=value
        try:contract(p,bad,rest)
        except ValueError:labels.append('row-'+key)
        else:raise ValueError('false map reason '+key)
    try:contract(p,refs,rest[:-1])
    except ValueError:labels.append('remaining-row')
    else:raise ValueError('missing remaining row')
    require(len(labels)==26,'finite26')
    for v in (*proofs,p,prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        referencesSha256=p['referencesSha256'],queueSha256=p['queueSha256'],occurrences=16,sourceCount=7,
        independentMetadataNegativeVectors=26,negativeLabels=labels,combinedPurposeOrReferenceRows=1049,
        remainingSelectedUnreferenced=442,productTestsExecuted=0,newManualReviews=0,oldRuntimeTransferred=False,
        oldSpanReinterpreted=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
