"""Explicit JMS-purpose saved schema; join exact diagnostic groups, no Product or graph execution."""
from collections import Counter
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE='db33c6a371d3dbc8e84f70462e0e56351bbb18b4'
OLD=('PG13262-jms-consumer-purpose-review-v1','21035e3b63cb7a03ecbdc3c95496bd8c21d53d73de5cf365fd540ebec10bca46')
OLD_POST=('PG13264-jms-consumer-purpose-post-v1','b0ba0d554deb628cfddd8363a36cb583ffff2a6496a71c25251d02163c8e9736')
PRIOR=('PG16101-resource-compound-saved-reference-v2','8f7e9dcc2e33ceea0358d7b2bd0d3d50106608bf593f72e90b180e7da9bcf0f7')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
OUT=data.BASE/'PG16106-jms-three-saved-purpose-reference-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def key(row):
    return json.dumps([row['path'],row['sourceSha256'],row['attributes']],sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,post,prior,obs=[read(v) for v in (OLD,OLD_POST,PRIOR,OBS)]
    require(all(v['actualExit']==0 for v in (old,post,prior,obs)) and old['source']==post['source']==OLD_SOURCE
            and prior['source']==obs['source']==SOURCE and post['reviewManifestSha256']==OLD[1],'old/current exact provenance')
    require(old['productTestsExecuted']==0 and old['newPurposeReferences']==72 and old['qualityGateExit']==1
            and old['actualViolationCount'] is old['coverage'] is None and old['sourceOrTestChanged'] is False,'historical source-only review, gate remains1')
    review=data.read_checked(data.BASE/OLD[0]/'review.json',old['reviewSha256'])
    rows=review['rows'];required={'purpose','classification','residualRisk','sourceLine','currentPositions','manualPurposeReviewComplete','sourceSha256','path','attributes','message','canonicalOwner','canonicalCostOwner','productTestsExecuted','ptExecutionExempt','actualViolation','measuredProductCounters'}
    require(len(rows)==72 and all(required<=set(r) for r in rows),'explicit JMS-purpose schema before field use')
    require(len(review['sourceFiles'])==3 and all(data.sha((data.ROOT/p).read_bytes())==v['sha256'] for p,v in review['sourceFiles'].items()),'full three sources exact bytes')
    require(Counter(r['classification'] for r in rows)==Counter(LONG_LIVED_OWNER_AND_CONTEXT_CHILD=7,BOUNDARY_FAILURE_RETENTION_NOT_SUCCESS=39,FATAL_PRIORITY_AND_IDENTITY=23,SERIAL_OWNER_CLOSE_STATE=3),'saved purposes full domain')
    require(Counter((r['canonicalOwner'],r['canonicalCostOwner']) for r in rows)==Counter({(v,v):24 for v in ('WBS-P012-01','WBS-P005-03','WBS-P006-05')}),'all original owners/costs preserved')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==739 and prior['combinedSelectedReferences']==656 and prior['combinedPurposeReviewed']==96,'prior domain')
    observed=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])
    require(all({'staticObservationId','currentSource','sourceSha256','path','attributes','message'}<=set(v) for v in observed),'explicit current observation schema')
    by_id={v['staticObservationId']:v for v in observed}
    matches={}
    for ordinal,row in enumerate(rows):matches.setdefault(key(row),[]).append((ordinal,row))
    selected=[r for r in queue if key(r) in matches]
    require(len(matches)==64 and len(selected)==72 and Counter(key(r) for r in selected)==Counter(key(r) for r in rows),'all repeated diagnostic multiplicity')
    links=[]
    for current in selected:
        saved=matches[key(current)];first=saved[0][1];actual=by_id[current['id']]
        require(actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256']
                and actual['path']==current['path'] and actual['attributes']==current['attributes'] and actual['message']==first['message'],'whole current diagnostic and source')
        witnesses=[]
        common=('purpose','classification','residualRisk','sourceLine','canonicalOwner','canonicalCostOwner','message')
        for ordinal,row in saved:
            require(all(row[k]==first[k] for k in common) and row['manualPurposeReviewComplete'] is True
                    and row['ptExecutionExempt'] is False and row['productTestsExecuted']==0
                    and row['actualViolation'] is row['measuredProductCounters'] is None
                    and all(isinstance(row[k],str) and row[k] for k in ('purpose','residualRisk','classification')),'unchanged explicit purpose and residual risks, no product')
            witnesses.append(dict(ordinal=ordinal,id=row['id'],rowSha256=data.sha(json.dumps(row,sort_keys=True).encode())))
        text=(data.ROOT/current['path']).read_text();a=current['attributes']
        require(text.splitlines()[int(a['beginline'])-1]==first['sourceLine'],'whole source line exact old static row')
        start,stop,token=span(text,a)
        links.append(dict(**current,currentSource=SOURCE,staticReviewSource=OLD_SOURCE,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(token.encode()),
            spanBasis='NEW_CANONICAL_COORDINATES_NO_SAVED_LEGACY_SPAN_FIELD_IN_JMS_SCHEMA',
            oldRowWitnesses=witnesses,oldSignatureOccurrences=len(saved),currentSignatureOccurrences=len(saved),
            individualOccurrenceIdentity='SIGNATURE_GROUP_ONLY_NO_ARBITRARY_BIJECTION',
            oldPurpose=first['purpose'],oldClassification=first['classification'],residualRisk=first['residualRisk'],
            canonicalOwner=first['canonicalOwner'],canonicalCostOwner=first['canonicalCostOwner'],
            diagnosticMessageSha256=data.sha(actual['message'].encode()),
            meaning='SAVED_STATIC_PURPOSE_REFERENCE_NOT_NEW_REVIEW_OR_RUNTIME'))
    ids={r['id'] for r in links};remaining=[r for r in queue if r['id'] not in ids]
    require(len(ids)==72 and len(remaining)==667,'complete no duplicate references or lost remaining')
    design='documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md'
    require((data.ROOT/design).is_file(),'exact public design')
    body=(data.ROOT/design).read_bytes()
    require(subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT)==body
            and all(v in body.decode() for v in ('SSC319','SSC332','SSC333','UNKNOWN')),'approved contract unchanged')
    for v in (old,post,prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'references.json',links);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,staticReviewSource=OLD_SOURCE,invocation=invocation,
        oldReviewManifestSha256=OLD[1],oldPostManifestSha256=OLD_POST[1],oldReviewSha256=old['reviewSha256'],
        oldQualityGateExit=1,oldActualViolationCount=None,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],
        referencesSha256=data.sha((OUT/'references.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),
        sourceHashes={p:v['sha256'] for p,v in review['sourceFiles'].items()},approvedDesign=dict(path=design,sha256=data.sha(body)),
        signatureGroups=64,occurrences=72,individualIdentityInvented=False,newReferenceConnections=72,
        combinedSelectedReferences=728,combinedPurposeReviewed=96,combinedPurposeOrReferenceRows=824,
        remainingSelectedUnreferenced=667,newManualReviews=0,rawSuppressed=0,actualViolationCount=None,
        productTestsExecuted=0,oldProductToolsReexecuted=0,oldRuntimeTransferred=False,sourceChanged=False,
        externalActions=0,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
