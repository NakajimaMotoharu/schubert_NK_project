"""Independent two-schema modern reference proof, including external original-diagnostic row lookup."""
from collections import Counter
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PARENT='PG16137-systemd-apiro-saved-reference27-v2'
PIN='d8225e47447559e38cf7e15d4600757ee9d25af56b07e6f7ffe82ae22c290aa6'
OUT=data.BASE/'PG16138-systemd-apiro-reference-post-v1'
SPECS=[
 ('PG13148-systemd-source-context-v1','4c4d139f02de58aa29294e4022ba8c710f3d0117349c86778841183dfd8ac7f2',
  'PG13149-systemd-source-context-post-v1','b2d7947bd08f97f58b0872261d429793afaad836b21d188ef6af2dd607e7b25c',
  'reviewedManifestSha256','44afb0a1ecddabfebe577b2037aabdc6fb31d1e3','review.json','reviewSha256',14,'SYSTEMD_SOURCE_PURPOSE_FULL_ATTRIBUTES_V1'),
 ('PG10934-api-ro-prior-context13-v1','69b5240316368ec534dd837ca1b95b9b8f2cd36af1a87775b165e1e6a780350f',
  'PG10936-api-ro-prior-context-post-v1','e5143c2f99ecab9185dee9068c14233e2f2eae2de075a423faf13c3e628b4f12',
  'primaryManifestSha256','f24d1649e170e46aafb59a37b9750c602206364c','contexts.json','contextsSha256',13,'API_RO_CONTEXT_FULL_ATTRIBUTES_V1')]
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
    prior=read('PG16131-startup-archive-legacy-reference61-v2','ba83ddaeeeb86f302fe1c274bd0406ee3fa2e88c89a3de2e42bb1a08020eb56a')
    obs=read('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    queue=data.read_checked(data.BASE/'PG16131-startup-archive-legacy-reference61-v2/remaining-selected-review-queue.json',prior['queueSha256'])
    observed=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',obs['observationsSha256'])
    by_id={v['staticObservationId']:v for v in observed}
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',RAW_PIN)
    original={v['id']:v for v in original}
    refs=data.read_checked(data.BASE/PARENT/'references.json',p['referencesSha256'])
    rest=data.read_checked(data.BASE/PARENT/'remaining-selected-review-queue.json',p['queueSha256'])
    input_manifests=[];old_rows=[]
    for name,pin,post,post_pin,post_key,source,payload,hash_key,count,schema in SPECS:
        old,q=read(name,pin),read(post,post_pin)
        require(old['actualExit']==q['actualExit']==0 and old['source']==q['source']==source and q[post_key]==pin
                and old['productTestsExecuted']==q['productTestsExecuted']==0,'saved independent static proof')
        body=data.read_checked(data.BASE/name/payload,old[hash_key]);rows=body['rows'] if isinstance(body,dict) else body
        require(len(rows)==count,'exact old rows')
        old_rows.extend((name,pin,post_pin,source,index,v,schema) for index,v in enumerate(rows))
        input_manifests.extend((old,q))
    expected=[];hashes={};counts=Counter()
    for current in queue:
        found=[v for v in old_rows if (v[5]['path'],v[5]['sourceSha256'],v[5]['attributes'])==(current['path'],current['sourceSha256'],current['attributes'])]
        if not found:continue
        require(len(found)==1,'one old exact Source/attributes signature')
        name,pin,post_pin,source,index,row,schema=found[0];actual=by_id[current['id']]
        require(row['source']==source and row['ptExecutionExempt'] is False and row['reason'],'unchanged old reason')
        if schema.startswith('SYSTEMD'):
            require(row['manualPurposeReviewComplete'] is True and row['dynamicExecutionQualificationInferred'] is False
                    and row['actualViolation'] is None and 'message' in row,'Systemd schema')
            message=row['message'];basis='SAVED_ROW_MESSAGE_LITERAL';raw_sha=None
        else:
            require('message' not in row and row['rawWarningRetained'] is True and row['oldRuntimeReassigned'] is row['scopeGeneralized'] is False
                    and row['productTestsExecuted']==0 and row['coverage'] is None and row['currentWholeCaseRefs']==[],'API schema without message field')
            raw=original[row['id']]
            require(raw['rowSha256']==row['originalRowSha256'] and raw['inputSha256']==row['sourceSha256']
                    and raw['path']==row['path'] and raw['attributes']==row['attributes'],'all13 original diagnostic row identities')
            message=raw['message'];basis='PINNED_ORIGINAL_ROW_SHA_LOOKUP_NO_MESSAGE_IN_CONTEXT_SCHEMA';raw_sha=row['originalRowSha256']
        require(actual['currentSource']==SOURCE and actual['sourceSha256']==current['sourceSha256']
                and actual['path']==current['path'] and actual['attributes']==current['attributes'] and actual['message']==message,'whole current diagnostic')
        body=(data.ROOT/current['path']).read_text();require(data.sha(body.encode())==row['sourceSha256'],'full Source byte equality')
        hashes[current['path']]=row['sourceSha256'];a=current['attributes'];lines=body.splitlines(keepends=True)
        start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
        stop=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])-1
        available='canonicalOwner' in row and 'canonicalCostOwner' in row;counts[name]+=1
        expected.append(dict(**current,currentSource=SOURCE,staticReviewSource=source,savedSchema=schema,
            oldManifest=name,oldManifestSha256=pin,oldPostManifestSha256=post_pin,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(body[start:stop].encode()),
            spanBasis='NEW_CANONICAL_SOURCE_COORDINATES_NOT_OLD_RUNTIME_OR_COVERAGE',
            oldFindingId=row['id'],oldRowOrdinal=index,oldRowSha256=data.sha(wire(row).encode()),
            oldReason=row['reason'],oldDiagnosticBasis=basis,oldDiagnosticRawRowSha256=raw_sha,oldMessageFieldInvented=False,
            historicalOwnerFieldsAvailable=available,historicalCanonicalOwner=row['canonicalOwner'] if available else None,
            historicalCanonicalCostOwner=row['canonicalCostOwner'] if available else None,currentOwnershipReassigned=False,
            diagnosticMessageSha256=data.sha(message.encode()),
            meaning='SAVED_SOURCE_PURPOSE_REFERENCE_ONLY_NO_NEW_MANUAL_REVIEW_OR_RUNTIME'))
    ids={v['id'] for v in expected};remaining=[v for v in queue if v['id'] not in ids]
    require(len(expected)==len(ids)==27 and len(hashes)==2 and len(remaining)==497 and counts==Counter({v[0]:v[8] for v in SPECS})
            and Counter(v['historicalOwnerFieldsAvailable'] for v in expected)==Counter({True:14,False:13}),'complete27/2 Sources and explicit owner absence')
    def contract(m,r,t):
        require(type(m['actualExit']) is int and m['actualExit']==0 and m['source']==SOURCE and m['sourceHashes']==hashes,'source and exact bytes')
        require((m['newReferenceConnections'],m['combinedSelectedReferences'],m['combinedPurposeReviewed'],
                 m['combinedPurposeOrReferenceRows'],m['remainingSelectedUnreferenced'])==(27,898,96,994,497),'reference domains')
        require(m['originalDiagnosticRawJsonSha256']==RAW_PIN and m['oldMessageFieldInvented'] is False,'explicit pinned original diagnostic relation')
        require(all(type(m[k]) is int and m[k]==0 for k in ('newManualReviews','rawSuppressed','productTestsExecuted',
                'oldProductToolsReexecuted','externalActions','actualSystemdOrFfmCalls','actualDatabaseActions','newAccepted'))
                and all(m[k] is False for k in ('oldRuntimeTransferred','currentOwnershipReassigned','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated'))
                and m['actualViolationCount'] is m['effortPercent'] is None,'no runtime/ownership/quality inference')
        require(wire(r)==wire(expected) and wire(t)==wire(remaining),'every original row/diagnostic/source and tail')
    contract(p,refs,rest);labels=[]
    vectors=[('source','source','OLD'),('refs','newReferenceConnections',26),('sum','combinedSelectedReferences',897),
        ('purpose','combinedPurposeReviewed',123),('remaining','remainingSelectedUnreferenced',0),
        ('message','oldMessageFieldInvented',True),('raw','originalDiagnosticRawJsonSha256','0'*64),
        ('manual','newManualReviews',27),('suppressed','rawSuppressed',27),('PT','productTestsExecuted',1),
        ('old-replay','oldProductToolsReexecuted',1),('native','actualSystemdOrFfmCalls',1),('DB','actualDatabaseActions',1),
        ('runtime','oldRuntimeTransferred',True),('ownership','currentOwnershipReassigned',True),('formal','formalUpdated',True),
        ('accepted','newAccepted',1),('effort','effortPercent',100),('violation','actualViolationCount',0),('whole','whole451Accepted',True)]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad,refs,rest)
        except ValueError:labels.append(label)
        else:raise ValueError('false modern27 claim '+label)
    for label,key,value in [('reason','oldReason','changed'),('schema','savedSchema','GENERIC'),
                            ('basis','oldDiagnosticBasis','INVENTED_MESSAGE'),('raw-sha','oldDiagnosticRawRowSha256','0'*64),
                            ('owner','currentOwnershipReassigned',True)]:
        bad=copy.deepcopy(refs);bad[0][key]=value
        try:contract(p,bad,rest)
        except ValueError:labels.append('row-'+label)
        else:raise ValueError('false modern row '+label)
    try:contract(p,refs,rest[:-1])
    except ValueError:labels.append('remaining-row')
    else:raise ValueError('missing remaining row')
    require(len(labels)==26,'finite26 metadata negatives')
    for v in (*input_manifests,prior,obs,p):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        referencesSha256=p['referencesSha256'],queueSha256=p['queueSha256'],independentMetadataNegativeVectors=26,
        negativeLabels=labels,occurrences=27,combinedPurposeOrReferenceRows=994,remainingSelectedUnreferenced=497,
        originalDiagnosticRawJsonSha256=RAW_PIN,oldMessageFieldInvented=False,currentOwnershipReassigned=False,
        newManualReviews=0,productTestsExecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
