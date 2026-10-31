"""Independent exact nine saved judgments, no codec/secret access or false new exemption fields."""
from collections import Counter
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE='f24d1649e170e46aafb59a37b9750c602206364c'
PARENT='PG16148-keylabel-nullable-saved-reference9-v1'
PIN='05e26e5a4ad67629c2c6ca698f6249b8b75321420ce860c306b0e0fb9bd1984a'
OUT=data.BASE/'PG16150-keylabel-nullable-reference-post-v1'
SPECS=[
 ('PG10916-main-null-crypto-resource-context-v1','d41f3747340987cf0a408a71e2224b07b9ec5f08664b79f687b75b240f19492d',
  'PG10918-main-null-crypto-resource-post-v1','e2ea0d2b539dd57e4db7abcf8c95f0fed89727aac0424f24bb7ad3edd97db64d',
  'originalManifestSha256','basis',5,'NULL_KEYLABEL_RESOURCE_BASIS_V1'),
 ('PG10922-main-null-owner-route-context-v1','9360be53ed58a1cf468f0968ca1b91b51fe288a4e217b6576fd342e6c1a88480',
  'PG10924-main-null-owner-route-post-v1','b7c968d373f9d582699ca83b2a7da87f42c878acf333f5e6c7c993523b136002',
  'primaryManifestSha256','reason',4,'NULL_OWNER_REASON_STATEMENT_BINDING_V1')]
RAW_PIN='92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(name,pin):
    return data.read_checked(data.BASE/name/'manifest.json',pin)

def wire(v):
    return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=read(PARENT,PIN)
    prior=read('PG16142-readiness-generic20-current-purpose-v1','aa5616879887e35e561778b12b02a6ac21b77fb0243d952fd7e2e8f917a98df8')
    obs=read('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    queue=data.read_checked(data.BASE/'PG16142-readiness-generic20-current-purpose-v1/remaining-selected-review-queue.json',prior['queueSha256'])
    observations=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',obs['observationsSha256'])
    by_id={v['staticObservationId']:v for v in observations}
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',RAW_PIN)
    original={v['id']:v for v in original}
    refs=data.read_checked(data.BASE/PARENT/'references.json',p['referencesSha256'])
    rest=data.read_checked(data.BASE/PARENT/'remaining-selected-review-queue.json',p['queueSha256'])
    inputs=[];all_rows=[]
    for name,pin,post,post_pin,post_key,reason_key,selected,schema in SPECS:
        old,q=read(name,pin),read(post,post_pin)
        require(old['actualExit']==q['actualExit']==0 and old['source']==q['source']==OLD_SOURCE
                and q[post_key]==pin and q['metadataNegativeVectors']==9 and old['productTestsExecuted']==q['productTestsExecuted']==0,'exact old source-purpose proof')
        rows=data.read_checked(data.BASE/name/'contexts.json',old['contextsSha256'])
        require(len(rows)==5 and all(reason_key in r and 'message' not in r and 'ptExecutionExempt' not in r for r in rows),'dedicated schema, no invented common fields')
        all_rows.extend((name,pin,post_pin,reason_key,index,r,schema) for index,r in enumerate(rows));inputs.extend((old,q))
    expected=[];hashes={};counts=Counter()
    for current in queue:
        found=[v for v in all_rows if (v[5]['path'],v[5]['sourceSha256'],v[5]['attributes'])==(current['path'],current['sourceSha256'],current['attributes'])]
        if not found:continue
        require(len(found)==1,'unique exact original Source/attrs')
        name,pin,post_pin,reason_key,index,row,schema=found[0];raw=original[row['id']];actual=by_id[current['id']]
        require(row['source']==OLD_SOURCE and row['rawWarningRetained'] is True and row['priorRuntimeReassigned'] is row['scopeGeneralized'] is False
                and row['newProductExecutions']==0 and row['newCoverage'] is None and row['currentWholeCaseRefs']==[] and row[reason_key],'old judgments, not old PT')
        require(raw['rowSha256']==row['originalRowSha256'] and raw['inputSha256']==row['sourceSha256']
                and raw['path']==row['path'] and raw['attributes']==row['attributes'],'all original row identity')
        require(actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256']
                and actual['attributes']==current['attributes'] and actual['path']==current['path'] and actual['message']==raw['message'],'whole current diagnostics')
        path=current['path'];body=(data.ROOT/path).read_text();require(data.sha(body.encode())==row['sourceSha256'],'current full Source, not statement-only fallback')
        hashes[path]=row['sourceSha256'];a=current['attributes'];lines=body.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
        stop=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])-1
        counts[name]+=1
        expected.append(dict(**current,currentSource=SOURCE,staticReviewSource=OLD_SOURCE,savedSchema=schema,
            oldManifest=name,oldManifestSha256=pin,oldPostManifestSha256=post_pin,oldFindingId=row['id'],
            oldRowOrdinal=index,oldRowSha256=data.sha(wire(row).encode()),oldTechnicalDisposition=row['technicalDisposition'],
            oldReasonOrBasis=row[reason_key],oldDiagnosticBasis='PINNED_ORIGINAL_ROW_SHA_NO_MESSAGE_FIELD',
            originalDiagnosticRowSha256=row['originalRowSha256'],oldMessageFieldInvented=False,
            oldPtExemptionFieldAvailable=False,currentPtExecutionExempt=False,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(body[start:stop].encode()),
            diagnosticMessageSha256=data.sha(raw['message'].encode()),historicalEvidenceReassigned=False,
            meaning='SAVED_SOURCE_REASON_REFERENCE_NOT_NEW_FALSE_POSITIVE_PT_OR_SECRET_SCAN_ACCEPTANCE'))
    ids={v['id'] for v in expected};remaining=[v for v in queue if v['id'] not in ids]
    require(len(expected)==len(ids)==9 and len(hashes)==6 and len(remaining)==468 and counts==Counter({v[0]:v[6] for v in SPECS}),'exact5plus4, excludedSource not rebound')
    require(Counter(v['oldTechnicalDisposition'] for v in expected)==Counter(REQUIRED_CONTRACT=2,
        FALSE_POSITIVE_RUNTIME_INPUT_LABEL_NOT_KEY_MATERIAL=1,
        FALSE_POSITIVE_EXPLICIT_END_FINALLY_NO_SCRATCH_ACQUISITION_GAP=2,EXPLICIT_NECESSARY_SOURCE_CONTRACT=4),'all original judgments unchanged')
    def contract(m,r,t):
        require(type(m['actualExit']) is int and m['actualExit']==0 and m['source']==SOURCE and m['staticReviewSource']==OLD_SOURCE
                and m['sourceHashes']==hashes and m['originalDiagnosticRawJsonSha256']==RAW_PIN,'exact provenance')
        require((m['newReferenceConnections'],m['combinedSelectedReferences'],m['combinedPurposeReviewed'],
                 m['combinedPurposeOrReferenceRows'],m['remainingSelectedUnreferenced'])==(9,907,116,1023,468),'counts, not new purpose')
        require(all(m[k] is False for k in ('oldMessageFieldInvented','oldPtExemptionFieldInvented','oldRuntimeTransferred','sourceChanged',
                'actualKeysOrCredentialsRead','G07Accepted','wholeF03Accepted','whole451Accepted','formalUpdated')),'no key/secret acceptance or old result transfer')
        require(all(type(m[k]) is int and m[k]==0 for k in ('newManualReviews','rawSuppressed','productTestsExecuted',
                'oldProductToolsReexecuted','actualCodecOrCipherOrZipCalls','externalActions','newAccepted'))
                and m['actualViolationCount'] is m['effortPercent'] is None,'no new Product/falsezero')
        require(wire(r)==wire(expected) and wire(t)==wire(remaining),'all oldjudgment/hash/schema and remaining')
    contract(p,refs,rest);labels=[]
    vectors=[('source','source','OLD'),('refs','newReferenceConnections',10),('sum','combinedSelectedReferences',908),
        ('purpose','combinedPurposeReviewed',125),('remaining','remainingSelectedUnreferenced',0),
        ('message','oldMessageFieldInvented',True),('exemption','oldPtExemptionFieldInvented',True),
        ('runtime','oldRuntimeTransferred',True),('G07','G07Accepted',True),('key-read','actualKeysOrCredentialsRead',True),
        ('codec','actualCodecOrCipherOrZipCalls',1),('manual','newManualReviews',9),('raw','rawSuppressed',9),
        ('PT','productTestsExecuted',9),('replay','oldProductToolsReexecuted',1),('formal','formalUpdated',True),
        ('whole','whole451Accepted',True),('accepted','newAccepted',1),('effort','effortPercent',100),('violation','actualViolationCount',0)]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad,refs,rest)
        except ValueError:labels.append(label)
        else:raise ValueError('false keylabel reference '+label)
    for label,key,value in [('basis','oldReasonOrBasis','changed'),('disposition','oldTechnicalDisposition','PASS'),
                            ('row-sha','oldRowSha256','0'*64),('exempt','currentPtExecutionExempt',True),
                            ('history','historicalEvidenceReassigned',True)]:
        bad=copy.deepcopy(refs);bad[0][key]=value
        try:contract(p,bad,rest)
        except ValueError:labels.append('row-'+label)
        else:raise ValueError('false old judgment row '+label)
    try:contract(p,refs,rest[:-1])
    except ValueError:labels.append('remaining-row')
    else:raise ValueError('missing remaining row')
    require(len(labels)==26,'finite26 metadata negatives')
    for v in (*inputs,prior,obs,p):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        referencesSha256=p['referencesSha256'],queueSha256=p['queueSha256'],independentMetadataNegativeVectors=26,negativeLabels=labels,
        occurrences=9,combinedPurposeOrReferenceRows=1023,remainingSelectedUnreferenced=468,
        newManualReviews=0,productTestsExecuted=0,actualCodecOrCipherOrZipCalls=0,G07Accepted=False,
        newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
