"""Independent saved-policy/source/diagnostic check, never invoke a catch or native path."""
import copy
import hashlib
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PARENT='PG16154-emptycatch-saved10-reference-v1'
PIN='f4bb9c080f06e141564e17ce743821528786476ffe4eef8ef040a4bb93e5a9d2'
OUT=data.BASE/'PG16156-emptycatch-reference-post-v1'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(name,pin):
    return data.read_checked(data.BASE/name/'manifest.json',pin)

def canonical(value):
    return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=read(PARENT,PIN)
    old=read('PG10928-main-empty-catch-policy-v1','6e1ed0ff67610462fd6d3e0830dc5bd8ccaad18248a7625f351707de9fad340f')
    post=read('PG10930-main-empty-catch-post-v1','25b9ad8efefecbb172faf3bce50e6bc1b3758a7eebf38dc4d55c7e78a5be0897')
    prior=read('PG16148-keylabel-nullable-saved-reference9-v1','05e26e5a4ad67629c2c6ca698f6249b8b75321420ce860c306b0e0fb9bd1984a')
    obs=read('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    require(old['actualExit']==post['actualExit']==prior['actualExit']==obs['actualExit']==0 and post['metadataNegativeVectors']==11
            and post['primaryManifestSha256']=='6e1ed0ff67610462fd6d3e0830dc5bd8ccaad18248a7625f351707de9fad340f','original finite review/post')
    contexts=data.read_checked(data.BASE/'PG10928-main-empty-catch-policy-v1/contexts.json',old['contextsSha256'])
    queue=data.read_checked(data.BASE/'PG16148-keylabel-nullable-saved-reference9-v1/remaining-selected-review-queue.json',prior['queueSha256'])
    current=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',obs['observationsSha256'])
    raw=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    refs=data.read_checked(data.BASE/PARENT/'references.json',p['referencesSha256'])
    rest=data.read_checked(data.BASE/PARENT/'remaining-selected-review-queue.json',p['queueSha256'])
    expected=[];hashes={};policies={}
    for ordinal in (0,1,2,3,4,10,11,12,13,14):
        row=contexts[ordinal];found=[v for v in queue if (v['path'],v['attributes'],v['sourceSha256'])==(row['path'],row['attributes'],row['sourceSha256'])]
        require(len(found)==1 and row['rule']=='EmptyCatchBlock' and 'message' not in row and row['ptExecutionExempt'] is False,'exact saved schema/signature')
        require(row['oldRuntimeReassigned'] is row['scopeGeneralized'] is False and row['coverage'] is None
                and row['currentWholeCaseRefs']==[] and row['productTestsExecuted']==0 and row['rawWarningRetained'] is True,'old policy no PT/exemption')
        require(row['catchBodyTokens']==[] and row['catchHeaderTokens'] and row['reason']
                and row['reviewStatus']=='STATIC_LOCAL_FAILURE_POLICY_REVIEW_COMPLETE','old finite policy review only')
        q=found[0];o=[v for v in current if v['staticObservationId']==q['id']];a=[v for v in raw if v['id']==row['id']]
        require(len(o)==len(a)==1,'independent exact current/original identity');o,a=o[0],a[0]
        require(a['rowSha256']==row['originalRowSha256'] and a['path']==q['path'] and a['inputSha256']==q['sourceSha256']
                and a['attributes']==q['attributes'] and o['message']==a['message'] and o['currentSource']==SOURCE
                and o['path']==q['path'] and o['sourceSha256']==q['sourceSha256'] and o['attributes']==q['attributes'],'full raw/current diagnostic relation')
        body=(data.ROOT/q['path']).read_bytes();require(hashlib.sha256(body).hexdigest()==row['sourceSha256'],'entire byte-exact Source')
        text=body.decode();lines=text.splitlines(keepends=True);attrs=q['attributes']
        start=sum(len(v) for v in lines[:int(attrs['beginline'])-1])+int(attrs['begincolumn'])-1
        end=sum(len(v) for v in lines[:int(attrs['endline'])-1])+int(attrs['endcolumn'])-1
        hashes[q['path']]=row['sourceSha256'];policies[row['policy']]=policies.get(row['policy'],0)+1
        expected.append(dict(**q,currentSource=SOURCE,staticReviewSource='f24d1649e170e46aafb59a37b9750c602206364c',
            savedSchema='EMPTY_CATCH_POLICY_TOKENS_REASON_V1',oldManifestSha256=post['primaryManifestSha256'],
            oldPostManifestSha256='25b9ad8efefecbb172faf3bce50e6bc1b3758a7eebf38dc4d55c7e78a5be0897',
            oldRowOrdinal=ordinal,oldRowSha256=hashlib.sha256(canonical(row).encode()).hexdigest(),oldFindingId=row['id'],
            oldReviewId=row['reviewId'],oldPolicy=row['policy'],oldReason=row['reason'],oldHeaderTokens=row['catchHeaderTokens'],
            oldBodyTokens=[],originalDiagnosticRowSha256=row['originalRowSha256'],
            diagnosticMessageSha256=hashlib.sha256(a['message'].encode()).hexdigest(),oldMessageFieldAvailable=False,
            oldPtExemptionFieldAvailable=True,currentPtExecutionExempt=False,oldRuntimeTransferred=False,
            canonicalSpanStart=start,canonicalSpanEndExclusive=end,canonicalSpanSha256=hashlib.sha256(text[start:end].encode()).hexdigest(),
            meaning='EXACT_SOURCE_SAVED_REASON_REFERENCE_NOT_NEW_CURRENT_APPLICABILITY_OR_PT'))
    expected.sort(key=lambda v:next(i for i,q in enumerate(queue) if q['id']==v['id']))
    ids={v['id'] for v in expected};remaining=[v for v in queue if v['id'] not in ids]
    require(len(ids)==10 and len(hashes)==7 and len(remaining)==458 and len(contexts)==15,'allten and unchanged remaining/source domain')
    def contract(m,r,t):
        require(type(m['actualExit']) is int and m['actualExit']==0 and m['source']==SOURCE and m['sourceHashes']==hashes
                and m['historicalDesignHashes']==old['approvedDesignHashes'] and m['oldContextSha256']==old['contextsSha256'],'source/history exact')
        require((m['newReferenceConnections'],m['combinedSelectedReferences'],m['combinedPurposeReviewed'],m['combinedPurposeOrReferenceRows'],m['remainingSelectedUnreferenced'])
                ==(10,917,116,1033,458) and m['policyCounts']==policies,'exact counts, no inferred purpose/PT')
        require(all(m[k] is False for k in ('currentDesignApplicabilityReaccepted','oldRuntimeTransferred','sourceChanged',
                'wholeF03Accepted','whole451Accepted','ptExecutionExempt','formalUpdated')),'no current qualification/exemption')
        require(all(type(m[k]) is int and m[k]==0 for k in ('newManualReviews','productTestsExecuted','oldProductToolsReexecuted',
                'actualRollbackOrPurgeOrRetentionCalls','rawSuppressed','externalActions','newAccepted'))
                and m['actualViolationCount'] is m['effortPercent'] is None,'finite static reference only')
        require(canonical(r)==canonical(expected) and canonical(t)==canonical(remaining),'all reasons/header/raw coordinates and remainder')
    contract(p,refs,rest);labels=[]
    for label,key,value in [('source','source','OLD'),('refs','newReferenceConnections',11),('sum','combinedSelectedReferences',918),
        ('purpose','combinedPurposeReviewed',126),('remaining','remainingSelectedUnreferenced',0),('design','currentDesignApplicabilityReaccepted',True),
        ('runtime','oldRuntimeTransferred',True),('changed','sourceChanged',True),('F03','wholeF03Accepted',True),('451','whole451Accepted',True),
        ('exemption','ptExecutionExempt',True),('formal','formalUpdated',True),('manual','newManualReviews',10),('PT','productTestsExecuted',10),
        ('replay','oldProductToolsReexecuted',1),('calls','actualRollbackOrPurgeOrRetentionCalls',1),('raw','rawSuppressed',10),
        ('external','externalActions',1),('accepted','newAccepted',1),('effort','effortPercent',100),('violation','actualViolationCount',0)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad,refs,rest)
        except ValueError:labels.append(label)
        else:raise ValueError('false contract '+label)
    for key,value in [('oldPolicy','PASS'),('oldReason','changed'),('oldHeaderTokens',[]),('currentPtExecutionExempt',True)]:
        bad=copy.deepcopy(refs);bad[0][key]=value
        try:contract(p,bad,rest)
        except ValueError:labels.append(key)
        else:raise ValueError('false policy row '+key)
    try:contract(p,refs,rest[:-1])
    except ValueError:labels.append('remaining-row')
    else:raise ValueError('lost remaining row')
    require(len(labels)==26,'finite26')
    for v in (p,old,post,prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        referencesSha256=p['referencesSha256'],queueSha256=p['queueSha256'],occurrences=10,sourceCount=7,
        independentMetadataNegativeVectors=26,negativeLabels=labels,combinedPurposeOrReferenceRows=1033,
        remainingSelectedUnreferenced=458,productTestsExecuted=0,newManualReviews=0,formalUpdated=False,
        wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
