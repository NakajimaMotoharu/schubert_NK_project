"""Exact saved nullable/key-label references only, no key/codec/constructor invocation."""
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE='f24d1649e170e46aafb59a37b9750c602206364c'
RECORDS=[
 dict(name='PG10916-main-null-crypto-resource-context-v1',pin='d41f3747340987cf0a408a71e2224b07b9ec5f08664b79f687b75b240f19492d',
      post='PG10918-main-null-crypto-resource-post-v1',postPin='e2ea0d2b539dd57e4db7abcf8c95f0fed89727aac0424f24bb7ad3edd97db64d',postKey='originalManifestSha256',reasonKey='basis',total=5,selected=5,schema='NULL_KEYLABEL_RESOURCE_BASIS_V1'),
 dict(name='PG10922-main-null-owner-route-context-v1',pin='9360be53ed58a1cf468f0968ca1b91b51fe288a4e217b6576fd342e6c1a88480',
      post='PG10924-main-null-owner-route-post-v1',postPin='b7c968d373f9d582699ca83b2a7da87f42c878acf333f5e6c7c993523b136002',postKey='primaryManifestSha256',reasonKey='reason',total=5,selected=4,schema='NULL_OWNER_REASON_STATEMENT_BINDING_V1')]
PRIOR=('PG16142-readiness-generic20-current-purpose-v1','aa5616879887e35e561778b12b02a6ac21b77fb0243d952fd7e2e8f917a98df8')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
RAW_PIN='92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966'
OUT=data.BASE/'PG16148-keylabel-nullable-saved-reference9-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def signature(v):
    return json.dumps([v['path'],v['sourceSha256'],v['attributes']],sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs=[read(v) for v in (PRIOR,OBS)]
    require(prior['actualExit']==obs['actualExit']==0 and prior['source']==obs['source']==SOURCE,'current metadata')
    saved={};inputs=[]
    for cfg in RECORDS:
        old,post=[read(v) for v in ((cfg['name'],cfg['pin']),(cfg['post'],cfg['postPin']))]
        require(old['actualExit']==post['actualExit']==0 and old['source']==post['source']==OLD_SOURCE
                and post[cfg['postKey']]==cfg['pin'] and post['metadataNegativeVectors']==9
                and old['productTestsExecuted']==post['productTestsExecuted']==0,'independent old source-purpose only')
        rows=data.read_checked(data.BASE/cfg['name']/'contexts.json',old['contextsSha256'])
        required={'path','sourceSha256','attributes','id','source','originalRowSha256','technicalDisposition',
                  'rawWarningRetained','priorRuntimeReassigned','scopeGeneralized','newCoverage','newProductExecutions','currentWholeCaseRefs'}
        require(len(rows)==cfg['total'] and all(required<=set(v) and cfg['reasonKey'] in v for v in rows),'explicit saved schema before field use')
        for index,row in enumerate(rows):
            require(row['source']==OLD_SOURCE and row['rawWarningRetained'] is True and row['priorRuntimeReassigned'] is row['scopeGeneralized'] is False
                    and row['newCoverage'] is None and row['newProductExecutions']==0 and row['currentWholeCaseRefs']==[]
                    and 'message' not in row and 'ptExecutionExempt' not in row and row[cfg['reasonKey']],'no invented old fields or runtime')
            if cfg['reasonKey']=='basis':require('evidence' in row,'basis/evidence schema')
            else:require({'priorProof','statementBinding','sourceRebindMode'}<=set(row),'reason/statement-binding schema')
            require(signature(row) not in saved,'unique old exact signature')
            saved[signature(row)]=(cfg,index,row)
        inputs.extend((old,post))
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==477 and prior['combinedSelectedReferences']==898 and prior['combinedPurposeReviewed']==116,'prior reference/purpose domains')
    observed=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])
    observed={v['staticObservationId']:v for v in observed}
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',RAW_PIN)
    original={v['id']:v for v in original}
    links=[];counts=Counter();source_hashes={}
    for current in queue:
        if signature(current) not in saved:continue
        cfg,index,row=saved[signature(current)];raw=original[row['id']];actual=observed[current['id']]
        require(raw['rowSha256']==row['originalRowSha256'] and raw['inputSha256']==row['sourceSha256']
                and raw['path']==row['path'] and raw['attributes']==row['attributes'],'original diagnostic relation exact')
        require(actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256']
                and actual['path']==current['path'] and actual['attributes']==current['attributes'] and actual['message']==raw['message'],'whole current diagnostic')
        text=(data.ROOT/current['path']).read_text();require(data.sha(text.encode())==row['sourceSha256'],'whole exact Source; no excluded Source fallback')
        start,stop,token=span(text,current['attributes']);source_hashes[current['path']]=row['sourceSha256'];counts[cfg['name']]+=1
        links.append(dict(**current,currentSource=SOURCE,staticReviewSource=OLD_SOURCE,savedSchema=cfg['schema'],
            oldManifest=cfg['name'],oldManifestSha256=cfg['pin'],oldPostManifestSha256=cfg['postPin'],
            oldFindingId=row['id'],oldRowOrdinal=index,oldRowSha256=data.sha(json.dumps(row,sort_keys=True).encode()),
            oldTechnicalDisposition=row['technicalDisposition'],oldReasonOrBasis=row[cfg['reasonKey']],
            oldDiagnosticBasis='PINNED_ORIGINAL_ROW_SHA_NO_MESSAGE_FIELD',originalDiagnosticRowSha256=row['originalRowSha256'],
            oldMessageFieldInvented=False,oldPtExemptionFieldAvailable=False,currentPtExecutionExempt=False,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(token.encode()),
            diagnosticMessageSha256=data.sha(actual['message'].encode()),historicalEvidenceReassigned=False,
            meaning='SAVED_SOURCE_REASON_REFERENCE_NOT_NEW_FALSE_POSITIVE_PT_OR_SECRET_SCAN_ACCEPTANCE'))
    require(len(links)==len({v['id'] for v in links})==9 and len(source_hashes)==6
            and counts==Counter({v['name']:v['selected'] for v in RECORDS})
            and sum(v['rule']=='HardCodedCryptoKey' for v in links)==1,'all9 only, six Sources, exact HCK label')
    ids={v['id'] for v in links};remaining=[v for v in queue if v['id'] not in ids]
    for v in (*inputs,prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'references.json',links);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,oldRecords=RECORDS,staticReviewSource=OLD_SOURCE,
        priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],originalDiagnosticRawJsonSha256=RAW_PIN,
        sourceHashes=source_hashes,referencesSha256=data.sha((OUT/'references.json').read_bytes()),
        queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),
        newReferenceConnections=9,combinedSelectedReferences=907,combinedPurposeReviewed=116,
        combinedPurposeOrReferenceRows=1023,remainingSelectedUnreferenced=468,newManualReviews=0,
        oldMessageFieldInvented=False,oldPtExemptionFieldInvented=False,rawSuppressed=0,actualViolationCount=None,
        productTestsExecuted=0,oldProductToolsReexecuted=0,oldRuntimeTransferred=False,sourceChanged=False,
        actualCodecOrCipherOrZipCalls=0,actualKeysOrCredentialsRead=False,externalActions=0,G07Accepted=False,
        wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
