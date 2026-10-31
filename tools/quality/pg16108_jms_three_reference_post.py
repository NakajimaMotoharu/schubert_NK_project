"""Independent full JMS purpose/diagnostic/source/owner and remaining-queue proof."""
from collections import Counter
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE='db33c6a371d3dbc8e84f70462e0e56351bbb18b4'
PARENT='PG16106-jms-three-saved-purpose-reference-v1'
PIN='4dccb138c4c39be4fd57e1f14b07d08fe0ab5f228a5894adb9b0f6b121c6ee0b'
OUT=data.BASE/'PG16108-jms-three-reference-post-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(name,pin):
    return data.read_checked(data.BASE/name/'manifest.json',pin)

def wire(v):
    return json.dumps(v,sort_keys=True)

def matches(a,b):
    return a['path']==b['path'] and a['sourceSha256']==b['sourceSha256'] and a['attributes']==b['attributes']

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=read(PARENT,PIN)
    old=read('PG13262-jms-consumer-purpose-review-v1','21035e3b63cb7a03ecbdc3c95496bd8c21d53d73de5cf365fd540ebec10bca46')
    old_post=read('PG13264-jms-consumer-purpose-post-v1','b0ba0d554deb628cfddd8363a36cb583ffff2a6496a71c25251d02163c8e9736')
    prior=read('PG16101-resource-compound-saved-reference-v2','8f7e9dcc2e33ceea0358d7b2bd0d3d50106608bf593f72e90b180e7da9bcf0f7')
    obs=read('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    review=data.read_checked(data.BASE/'PG13262-jms-consumer-purpose-review-v1/review.json',old['reviewSha256'])
    queue=data.read_checked(data.BASE/'PG16101-resource-compound-saved-reference-v2/remaining-selected-review-queue.json',prior['queueSha256'])
    observed=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',obs['observationsSha256'])
    actual_by_id={r['staticObservationId']:r for r in observed}
    refs=data.read_checked(data.BASE/PARENT/'references.json',p['referencesSha256'])
    remaining=data.read_checked(data.BASE/PARENT/'remaining-selected-review-queue.json',p['queueSha256'])
    require(old['source']==old_post['source']==OLD_SOURCE and prior['source']==SOURCE
            and all(v['actualExit']==0 for v in (old,old_post,prior,obs,p))
            and old_post['reviewManifestSha256']==p['oldReviewManifestSha256']=='21035e3b63cb7a03ecbdc3c95496bd8c21d53d73de5cf365fd540ebec10bca46','full exact old static provenance')
    require(p['sourceHashes']=={path:v['sha256'] for path,v in review['sourceFiles'].items()}
            and all(data.sha((data.ROOT/f).read_bytes())==h for f,h in p['sourceHashes'].items()),'full three unchanged sources')
    expected=[];groups=set()
    for current in queue:
        saved=[(i,r) for i,r in enumerate(review['rows']) if matches(current,r)]
        if not saved:continue
        old_count=len(saved);new_count=sum(matches(current,r) for r in queue)
        require(old_count==new_count,'every indistinguishable occurrence retained')
        first=saved[0][1];actual=actual_by_id[current['id']]
        require(actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256']
                and actual['attributes']==current['attributes'] and actual['path']==current['path']
                and actual['message']==first['message'],'current-source diagnostic, not old hash field')
        source=(data.ROOT/current['path']).read_text();lines=source.splitlines(keepends=True);a=current['attributes']
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
        stop=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])-1
        require(lines[int(a['beginline'])-1].removesuffix('\n')==first['sourceLine'],'whole source line')
        witnesses=[]
        for index,row in saved:
            require(row['manualPurposeReviewComplete'] is True and row['productTestsExecuted']==0
                    and row['ptExecutionExempt'] is False and row['measuredProductCounters'] is row['actualViolation'] is None
                    and row['purpose']==first['purpose'] and row['classification']==first['classification']
                    and row['residualRisk']==first['residualRisk'] and row['canonicalOwner']==row['canonicalCostOwner']==first['canonicalOwner'],'same old purposes/risk/fee, no product')
            witnesses.append(dict(ordinal=index,id=row['id'],rowSha256=data.sha(wire(row).encode())))
        expected.append(dict(**current,currentSource=SOURCE,staticReviewSource=OLD_SOURCE,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(source[start:stop].encode()),
            spanBasis='NEW_CANONICAL_COORDINATES_NO_SAVED_LEGACY_SPAN_FIELD_IN_JMS_SCHEMA',
            oldRowWitnesses=witnesses,oldSignatureOccurrences=old_count,currentSignatureOccurrences=new_count,
            individualOccurrenceIdentity='SIGNATURE_GROUP_ONLY_NO_ARBITRARY_BIJECTION',
            oldPurpose=first['purpose'],oldClassification=first['classification'],residualRisk=first['residualRisk'],
            canonicalOwner=first['canonicalOwner'],canonicalCostOwner=first['canonicalCostOwner'],
            diagnosticMessageSha256=data.sha(actual['message'].encode()),
            meaning='SAVED_STATIC_PURPOSE_REFERENCE_NOT_NEW_REVIEW_OR_RUNTIME'))
        groups.add(wire([current['path'],current['sourceSha256'],a]))
    ids={r['id'] for r in expected};rest=[r for r in queue if r['id'] not in ids]
    require(len(expected)==len(ids)==72 and len(groups)==64 and len(rest)==667,'complete72/64/667')
    require(Counter(r['oldClassification'] for r in expected)==Counter(LONG_LIVED_OWNER_AND_CONTEXT_CHILD=7,BOUNDARY_FAILURE_RETENTION_NOT_SUCCESS=39,FATAL_PRIORITY_AND_IDENTITY=23,SERIAL_OWNER_CLOSE_STATE=3),'all four explicit purpose classes')
    def contract(m,rows,tail):
        require(type(m['actualExit']) is int and m['actualExit']==0 and m['source']==SOURCE and m['staticReviewSource']==OLD_SOURCE,'actual source/exit')
        require((m['oldQualityGateExit'],m['signatureGroups'],m['occurrences'],m['newReferenceConnections'],
                 m['combinedSelectedReferences'],m['combinedPurposeReviewed'],m['combinedPurposeOrReferenceRows'],
                 m['remainingSelectedUnreferenced'])==(1,64,72,72,728,96,824,667),'exact scopes and gate1 retained')
        require(m['oldActualViolationCount'] is m['actualViolationCount'] is m['effortPercent'] is None,'unknown notzero')
        require(all(type(m[k]) is int and m[k]==0 for k in ('newManualReviews','rawSuppressed','productTestsExecuted','oldProductToolsReexecuted','externalActions','newAccepted'))
                and all(m[k] is False for k in ('individualIdentityInvented','oldRuntimeTransferred','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated')),'not execution/newpurpose/quality exemption')
        require(wire(rows)==wire(expected) and wire(tail)==wire(rest),'every bound row/span/risk/owner and remaining old row unchanged')
    contract(p,refs,remaining);labels=[]
    vectors=[('source','source',OLD_SOURCE),('old-source','staticReviewSource',SOURCE),('gate','oldQualityGateExit',0),
        ('groups','signatureGroups',72),('occurrences','occurrences',64),('refs','newReferenceConnections',71),
        ('sum','combinedSelectedReferences',800),('purpose','combinedPurposeReviewed',168),
        ('remaining','remainingSelectedUnreferenced',0),('identity','individualIdentityInvented',True),
        ('manual','newManualReviews',72),('suppress','rawSuppressed',72),('product','productTestsExecuted',1),
        ('replay','oldProductToolsReexecuted',1),('runtime','oldRuntimeTransferred',True),
        ('formal','formalUpdated',True),('accepted','newAccepted',1),('effort','effortPercent',100),
        ('violation','actualViolationCount',0)]
    for label,k,v in vectors:
        bad=copy.deepcopy(p);bad[k]=v
        try:contract(bad,refs,remaining)
        except ValueError:labels.append(label)
        else:raise ValueError('false JMS reference scope '+label)
    for label,k,v in [('witness','oldRowWitnesses',[]),('purpose','oldPurpose','changed'),('risk','residualRisk',''),
                       ('owner','canonicalOwner','WBS-F03'),('cost','canonicalCostOwner','WBS-F03'),
                       ('span','canonicalSpanSha256','0'*64),('identity','individualOccurrenceIdentity','UNIQUE')]:
        bad=copy.deepcopy(refs);bad[0][k]=v
        try:contract(p,bad,remaining)
        except ValueError:labels.append('row-'+label)
        else:raise ValueError('false JMS individual reference '+label)
    try:contract(p,refs,remaining[:-1])
    except ValueError:labels.append('remaining-row')
    else:raise ValueError('missing remaining row')
    require(len(labels)==27,'finite27 metadata checks')
    for v in (old,old_post,prior,obs,p):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        referencesSha256=p['referencesSha256'],queueSha256=p['queueSha256'],
        independentMetadataNegativeVectors=27,negativeLabels=labels,signatureGroups=64,occurrences=72,
        combinedPurposeOrReferenceRows=824,remainingSelectedUnreferenced=667,oldQualityGateExitRetained=1,
        newManualReviews=0,productTestsExecuted=0,oldRuntimeTransferred=False,newAccepted=0,
        wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
