"""Independent direct-column and complete signature-multiplicity reference proof, no Product."""
from collections import Counter
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD_SOURCE='1be156b6ebb139713db31a561b8b024972975471'
PIN='8f7e9dcc2e33ceea0358d7b2bd0d3d50106608bf593f72e90b180e7da9bcf0f7'
OUT=data.BASE/'PG16102-resource-compound-reference-post-v1'
PARENT='PG16101-resource-compound-saved-reference-v2'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(name,pin):
    return data.read_checked(data.BASE/name/'manifest.json',pin)

def wire(v):
    return json.dumps(v,sort_keys=True)

def same(a,b):
    return (a['path'],a['sourceSha256'],a['attributes'])==(b['path'],b['sourceSha256'],b['attributes'])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=read(PARENT,PIN)
    old=read('PG12432-resource-compound-context-v1','20cd6d45c1b336ce6f5320a2844e7ca4bd455a8103beb179bb7e19bd252035de')
    post=read('PG12434-resource-compound-context-post-v1','7457fb8e17f085e7022cca8aad1953eb61c5f3ae128d137cde2be6ba03f30ce3')
    prior=read('PG16075-four-repository-saved-reference-join-v2','44b10dd7416d940b650c77325dd48e195fdf2dacc749fa98e75b063464bc874d')
    review=data.read_checked(data.BASE/'PG12432-resource-compound-context-v1/review.json',old['reviewSha256'])['rows']
    queue=data.read_checked(data.BASE/'PG16075-four-repository-saved-reference-join-v2/remaining-selected-review-queue.json',prior['queueSha256'])
    links=data.read_checked(data.BASE/PARENT/'references.json',p['referencesSha256'])
    remaining=data.read_checked(data.BASE/PARENT/'remaining-selected-review-queue.json',p['queueSha256'])
    require(old['source']==post['source']==OLD_SOURCE and prior['source']==SOURCE
            and all(v['actualExit']==0 for v in (old,post,prior,p))
            and post['reviewManifestSha256']==p['oldReviewManifestSha256']=='20cd6d45c1b336ce6f5320a2844e7ca4bd455a8103beb179bb7e19bd252035de','old source stays historical')
    require(p['sourceHashes']==old['closureSourceHashes'] and len(p['sourceHashes'])==5
            and all(data.sha((data.ROOT/f).read_bytes())==h for f,h in p['sourceHashes'].items()),'full five source/helper same bytes')
    source_observations=read('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    observed=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',source_observations['observationsSha256'])
    observations={v['staticObservationId']:v for v in observed}
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    raws={v['id']:v for v in original}
    expected=[];extra=Counter();groups=set()
    for row in queue:
        matches=[(i,s) for i,s in enumerate(review) if same(row,s)]
        if not matches:continue
        duplicate_current=[s for s in queue if same(row,s)]
        require(len(matches)==len(duplicate_current),'full raw/current multiplicity')
        path=row['path'];body=(data.ROOT/path).read_text();lines=body.splitlines(keepends=True);a=row['attributes']
        start=sum(len(v) for v in lines[:int(a['beginline'])-1])+int(a['begincolumn'])-1
        stop=sum(len(v) for v in lines[:int(a['endline'])-1])+int(a['endcolumn'])-1
        token=body[start:stop];legacy=body[start:stop+1];first=matches[0][1]
        require(start<stop<len(body) and data.sha(legacy.encode())==first['sourceSpanSha256'],'independent old endcolumn extent')
        suffix=repr(body[stop]);extra[suffix]+=1;groups.add(wire([path,row['sourceSha256'],a]))
        witnesses=[]
        for index,saved in matches:
            raw=raws[saved['id']]
            require(raw['inputSha256']==row['sourceSha256'] and raw['rowSha256']==saved['originalRowSha256']
                    and raw['attributes']==a and raw['path']==path,'all exact original row identities')
            require(saved['source']==OLD_SOURCE and saved['oldRuntimeReassigned'] is False and saved['productTestsExecutedByReview']==saved['newAccepted']==0
                    and saved['dynamicPtStatus']=='NOT_EXECUTED' and saved['reason']==first['reason'],'no runtime or arbitrary duplicate identity')
            witnesses.append(dict(ordinal=index,id=saved['id'],rowSha256=data.sha(wire(saved).encode()),originalRawRowSha256=saved['originalRowSha256']))
        actual=observations[row['id']]
        require({'sourceSha256','currentSource','path','message','attributes'}<=set(actual)
                and actual['sourceSha256']==row['sourceSha256'] and actual['currentSource']==SOURCE
                and actual['path']==path and actual['attributes']==a and actual['message']==raws[first['id']]['message'],'current schema explicitly differs from old inputSha256')
        expected.append(dict(**row,currentSource=SOURCE,staticReviewSource=OLD_SOURCE,
            canonicalStart=start,canonicalEndExclusive=stop,canonicalSpanSha256=data.sha(token.encode()),
            legacyExtentSha256=first['sourceSpanSha256'],legacyExtraCharacter=suffix,
            legacyExtentIsCanonicalPmdToken=False,spanSchema='CANONICAL_EXCLUSIVE_AND_FIXED_EXPORTER_PLUS_ONE_CHARACTER',
            individualOccurrenceIdentity='SIGNATURE_GROUP_ONLY_NO_ARBITRARY_BIJECTION',
            oldSignatureOccurrences=len(matches),currentSignatureOccurrences=len(duplicate_current),
            oldRowWitnesses=witnesses,oldReason=first['reason'],oldKind=first['kind'],
            diagnosticMessageSha256=data.sha(actual['message'].encode()),
            meaning='EXISTING_STATIC_REFERENCE_ONLY_NOT_NEW_REVIEW_OR_RUNTIME'))
    ids={v['id'] for v in expected}
    expected_remaining=[v for v in queue if v['id'] not in ids]
    require(len(expected)==len(ids)==46 and len(groups)==32 and len(expected_remaining)==739
            and extra==Counter({"' '":22,"'\\n'":8,"')'":16}),'all46 including duplicates and suffixes')
    def contract(m,refs,rest):
        require(m['actualExit']==0 and type(m['actualExit']) is int and m['source']==SOURCE and m['staticReviewSource']==OLD_SOURCE,'exact source/exit')
        require((m['newReferenceConnections'],m['combinedSelectedReferences'],m['combinedPurposeReviewed'],m['combinedPurposeOrReferenceRows'],m['remainingSelectedUnreferenced'])==(46,656,96,752,739),'finite reference domains')
        require(m['signatureGroups']==32 and m['occurrences']==46 and m['individualIdentityInvented'] is False
                and m['legacyExtentIsCanonicalPmdToken'] is False and m['extraCharacters']=={'SPACE':22,'LF':8,'RIGHT_PAREN':16},'multiplicity and explicit old convention')
        require(all(type(m[k]) is int and m[k]==0 for k in ('newManualReviews','rawSuppressed','productTestsExecuted','oldProductToolsReexecuted','externalActions','newAccepted'))
                and all(m[k] is False for k in ('exporterReexecuted','oldRuntimeTransferred','sourceChanged','wholeF03Accepted','whole451Accepted','formalUpdated'))
                and m['effortPercent'] is m['actualViolationCount'] is None,'not new product or false quality')
        require(m['exporterSha256']=='7707736ffe8dd37399377797faf20fe233c8ce258d336367f8d90b610768b147'
                and data.sha((data.ROOT/'tools/quality/pg12432_resource_compound_context.py').read_bytes())==m['exporterSha256'],'frozen exporter')
        require(wire(refs)==wire(expected) and wire(rest)==wire(expected_remaining),'all rows and remaining immutable')
    contract(p,links,remaining)
    labels=[]
    vectors=[('source','source','OLD'),('old-source','staticReviewSource',SOURCE),('refs','newReferenceConnections',45),
        ('sum','combinedSelectedReferences',655),('purpose','combinedPurposeReviewed',142),('remaining','remainingSelectedUnreferenced',0),
        ('multiplicity','signatureGroups',46),('identity','individualIdentityInvented',True),('canonical','legacyExtentIsCanonicalPmdToken',True),
        ('manual','newManualReviews',46),('suppression','rawSuppressed',46),('PT','productTestsExecuted',1),
        ('replay','oldProductToolsReexecuted',1),('export','exporterReexecuted',True),('runtime','oldRuntimeTransferred',True),
        ('formal','formalUpdated',True),('acceptance','newAccepted',1),('effort','effortPercent',100),('violation','actualViolationCount',0)]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad,links,remaining)
        except ValueError:labels.append(label)
        else:raise ValueError('false scope accepted '+label)
    for label,key,value in [('old-witness','oldRowWitnesses',[]),('span','canonicalSpanSha256','0'*64),('reason','oldReason','changed'),('raw-id','id','OLD'),('old-extent','legacyExtentSha256','0'*64),('individual','individualOccurrenceIdentity','UNIQUE')]:
        bad=copy.deepcopy(links);bad[0][key]=value
        try:contract(p,bad,remaining)
        except ValueError:labels.append(label)
        else:raise ValueError('false individual reference accepted '+label)
    try:contract(p,links,remaining[:-1])
    except ValueError:labels.append('remaining-row')
    else:raise ValueError('missing remaining row accepted')
    require(len(labels)==26,'finite26 metadata negatives')
    for v in (old,post,prior,p):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        oldReviewManifestSha256=p['oldReviewManifestSha256'],referencesSha256=p['referencesSha256'],queueSha256=p['queueSha256'],
        independentMetadataNegativeVectors=26,negativeLabels=labels,signatureGroups=32,occurrences=46,
        combinedPurposeOrReferenceRows=752,remainingSelectedUnreferenced=739,oldRuntimeTransferred=False,
        newManualReviews=0,productTestsExecuted=0,newAccepted=0,formalUpdated=False,
        wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
