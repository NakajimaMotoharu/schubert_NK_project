"""Independent line/brace/guard reconstruction for the twenty current source purposes; no Product."""
from collections import Counter
import copy
import json
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PARENT='PG16142-readiness-generic20-current-purpose-v1'
PIN='aa5616879887e35e561778b12b02a6ac21b77fb0243d952fd7e2e8f917a98df8'
OUT=data.BASE/'PG16144-readiness-generic20-purpose-post-v1'
API='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/ApiDependencyReadiness.java'
WEB='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebDependencyReadiness.java'
PINS={API:'a9510db3be2c058715da8c4f089d3f49b2e9224447bf6685aeb23f12400d594e',WEB:'bf5f3f6357c91a01dc2d8dfcf8b45687e42a011099d6c286cd54c3a6c8de35ab'}
TABLE={
 API:[(60,'BODY',None),(66,'CLEANUP',None),(74,'CATALOG','API database unavailable'),
      (102,'BODY',None),(108,'CLEANUP',None),(118,'CATALOG','API Artemis receive queues unavailable')],
 WEB:[(34,'BODY',None),(40,'CLEANUP',None),(47,'CATALOG','Web technical database'),
      (58,'BODY',None),(64,'CLEANUP',None),(71,'CATALOG','Web Artemis reply Queue')]}
TOKENS={'BODY':['same primary','mandatory close','not a successful fallback'],
        'CLEANUP':['Connection/JMSContext','direct close Error','transient secondary','Actual close/graph behavior remains unproved'],
        'CATALOG':['preserveFatal','Direct Error is not','fixed non-success','unproved']}

def require(ok,why):
    if not ok:raise ValueError(why)

def read(name,pin):
    return data.read_checked(data.BASE/name/'manifest.json',pin)

def wire(v):
    return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=read(PARENT,PIN)
    prior=read('PG16137-systemd-apiro-saved-reference27-v2','d8225e47447559e38cf7e15d4600757ee9d25af56b07e6f7ffe82ae22c290aa6')
    obs=read('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
    review=data.read_checked(data.BASE/PARENT/'review.json',p['reviewSha256'])
    queue=data.read_checked(data.BASE/'PG16137-systemd-apiro-saved-reference27-v2/remaining-selected-review-queue.json',prior['queueSha256'])
    observations=data.read_checked(data.BASE/'PG15930-f03-current-main-review-join-v2/current-main-observations.json',obs['observationsSha256'])
    by_id={v['staticObservationId']:v for v in observations}
    rest=data.read_checked(data.BASE/PARENT/'remaining-selected-review-queue.json',p['queueSha256'])
    require(p['actualExit']==prior['actualExit']==obs['actualExit']==0 and p['source']==prior['source']==obs['source']==SOURCE,'same source current metadata')
    require(review['sourceHashes']==PINS and review['fullSourceTextReadForReview'] is True and review['javaTypeOrCfgProof'] is False,'two whole Sources, no stronger parser claim')
    scopes=[];by_path={}
    for path,pin in PINS.items():
        body=(data.ROOT/path).read_text();require(data.sha(body.encode())==pin and body.isascii() and '\\u' not in body,'exact ordinary source')
        cleaned=re.sub(r'"(?:\\.|[^"\\])*"|/\*[\s\S]*?\*/|//[^\n]*',lambda m:' '*(m.end()-m.start()),body)
        lines=body.splitlines(keepends=True);offsets=[0]
        for line in lines:offsets.append(offsets[-1]+len(line))
        marker='TemporaryInfrastructureException' if path==API else 'WebStartupException'
        local=[]
        for ordinal,(line_number,purpose,literal) in enumerate(TABLE[path]):
            line=lines[line_number-1];header=re.search(r'\bcatch\s*\(([^()]*)\)\s*\{',line)
            require(header is not None,'manual fixed line/header')
            name_types,parameter=header.group(1).strip().rsplit(' ',1)
            types=[v.strip() for v in name_types.split('|')]
            expected_types=[['SQLException','RuntimeException','Error'],['SQLException','RuntimeException','Error'],['SQLException','RuntimeException'],
                            ['RuntimeException','Error'],['RuntimeException','Error'],['RuntimeException']][ordinal]
            require(types==expected_types and parameter==('closing' if purpose=='CLEANUP' else 'failure'),'complete independent type/parameter table')
            start=offsets[line_number-1]+header.start()
            opening=offsets[line_number-1]+header.end()-1
            header_end=offsets[line_number-1]+line.index(')',header.start())+1
            cursor=opening+1;depth=1
            while depth:
                depth+=(cleaned[cursor]=='{')-(cleaned[cursor]=='}');cursor+=1
            normalized=re.sub(r'\s+','',cleaned[opening+1:cursor-1])
            if purpose=='BODY':require(normalized=='primary=failure;throwfailure;','body exact same-primary rethrow')
            elif purpose=='CLEANUP':require(normalized=='if(primary==null||closinginstanceofError&&!(primaryinstanceofError)){throwclosing;}'+marker+'.attachSecondary(primary,closing);','close exact direct fatal selection and secondary retention')
            else:
                cls='IllegalStateException' if path==API else 'WebStartupException'
                require(normalized==marker+'.preserveFatal(failure);thrownew'+cls+'();' and body[opening+1:cursor-1].count('"'+literal+'"')==1,'outer catalog after fatal classification only')
            fact=dict(line=line_number,start=start,end=cursor,headerEnd=header_end,types=types,parameter=parameter,
                      bodyTokens=normalized,bodyText=body[opening+1:cursor-1],path=path,purpose=purpose,catalogLiteral=literal,sourceSha256=pin)
            scopes.append(fact);local.append(fact)
        require(body.count('connection.close();')==body.count('context.close();')==1,'one textual close each, not actual resource count')
        by_path[path]=(body,offsets,local)
    require(wire(scopes)==wire(review['scopeFacts']) and len(scopes)==12,'all12 source scopes independently reconstructed')
    actual_rows={v['id']:v for v in review['rows']};expected=[]
    for current in queue:
        if current['path'] not in PINS or current['rule']!='AvoidCatchingGenericException':continue
        body,offsets,local=by_path[current['path']];a=current['attributes']
        start=offsets[int(a['beginline'])-1]+int(a['begincolumn'])-1
        stop=offsets[int(a['endline'])-1]+int(a['endcolumn'])-1
        found=[v for v in local if v['start']<=start<stop<=v['headerEnd']]
        require(len(found)==1 and body[start:stop] in ('RuntimeException','Error'),'all exact header operands')
        c=found[0];actual=by_id[current['id']];row=actual_rows[current['id']]
        require(actual['currentSource']==SOURCE and actual['sourceSha256']==PINS[current['path']]
                and actual['attributes']==a and actual['path']==current['path'],'current whole observation')
        require(all(anchor in row['reason'] for anchor in TOKENS[c['purpose']])
                and row['residualRisk'].startswith('SOURCE PURPOSE ONLY:')
                and all(v in row['residualRisk'] for v in ('Java type resolution','Throwable graph','actual provider','dynamic PT qualification')),'independent purpose/risk anchors, not semantic runtime proof')
        expected.append(dict(**current,currentSource=SOURCE,manualPurposeReviewComplete=True,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(body[start:stop].encode()),
            typeToken=body[start:stop],catchLine=c['line'],catchStart=c['start'],catchEnd=c['end'],catchTypes=c['types'],
            catchParameter=c['parameter'],catchPurpose=c['purpose'],catchBodyTokenSha256=data.sha(c['bodyTokens'].encode()),
            catalogLiteral=c['catalogLiteral'],reason=row['reason'],residualRisk=row['residualRisk'],
            diagnosticMessageSha256=data.sha(actual['message'].encode()),status='SOURCE_PURPOSE_REVIEWED_DYNAMIC_AND_WHOLE_STATIC_HOLD',
            rawRetained=True,ptExecutionExempt=False,actualViolation=None,productTestsExecuted=0,coverage=None,
            sourceChanged=False,oldRuntimeTransferred=False))
    ids={v['id'] for v in expected};remaining=[v for v in queue if v['id'] not in ids]
    require(len(expected)==len(ids)==20 and len(remaining)==477 and Counter(v['catchPurpose'] for v in expected)==Counter(BODY=8,CLEANUP=8,CATALOG=4),'complete20/12headers/477remain')
    require(all(data.sha((data.ROOT/path).read_bytes())==pin for path,pin in review['approvedDesignHashes'].items()),'all current approved designs unchanged')
    def contract(m,r,t,s):
        require(type(m['actualExit']) is int and m['actualExit']==0 and m['source']==SOURCE,'source/exit')
        require((m['newManualReviews'],m['newReferenceConnections'],m['combinedSelectedReferences'],m['combinedPurposeReviewed'],
                 m['combinedPurposeOrReferenceRows'],m['remainingSelectedUnreferenced'],m['sourcePrograms'],m['catchHeaders'],m['operands'])==
                 (20,0,898,116,1014,477,2,12,20),'newmanual separate from savedreferences and Product tests')
        require(all(m[k] is False for k in ('prior5960PurposesTransferred','sourceCodeChangeRequiredByThisReview','sourceChanged',
                'javaTypeOrCfgProof','wholeF03Accepted','whole451Accepted','formalUpdated')),'no stale source or stronger qualification')
        require(all(type(m[k]) is int and m[k]==0 for k in ('rawSuppressed','productTestsExecuted','oldProductToolsReexecuted',
                'externalActions','actualGraphCalls','newAccepted')) and m['actualViolationCount'] is m['coverage'] is m['effortPercent'] is None,'not execution/static zero/coverage')
        require(wire(r)==wire(expected) and wire(t)==wire(remaining) and wire(s)==wire(scopes),'every raw row/catch guard/risk and remaining')
    contract(p,review['rows'],rest,review['scopeFacts']);labels=[]
    vectors=[('source','source','OLD'),('manual','newManualReviews',0),('saved','newReferenceConnections',20),
        ('purpose','combinedPurposeReviewed',96),('remaining','remainingSelectedUnreferenced',0),
        ('source-size','sourcePrograms',1),('headers','catchHeaders',6),('operands','operands',12),
        ('old-source','prior5960PurposesTransferred',True),('type-proof','javaTypeOrCfgProof',True),
        ('raw-erased','rawSuppressed',20),('PT','productTestsExecuted',20),('replay','oldProductToolsReexecuted',1),
        ('Graph','actualGraphCalls',1),('source-change','sourceChanged',True),('whole','whole451Accepted',True),
        ('formal','formalUpdated',True),('accepted','newAccepted',1),('effort','effortPercent',100),('violation','actualViolationCount',0)]
    for label,key,value in vectors:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad,review['rows'],rest,review['scopeFacts'])
        except ValueError:labels.append(label)
        else:raise ValueError('false purpose metadata '+label)
    for label,key,value in [('reason','reason','changed'),('risk','residualRisk','none'),
                            ('types','catchTypes',['RuntimeException']),('guard','catchBodyTokenSha256','0'*64),
                            ('PT-exempt','ptExecutionExempt',True)]:
        bad=copy.deepcopy(review['rows']);bad[0][key]=value
        try:contract(p,bad,rest,review['scopeFacts'])
        except ValueError:labels.append('row-'+label)
        else:raise ValueError('false purpose row '+label)
    try:contract(p,review['rows'],rest[:-1],review['scopeFacts'])
    except ValueError:labels.append('remaining-row')
    else:raise ValueError('missing remaining row')
    require(len(labels)==26,'finite26 source/metadata negatives')
    for v in (prior,obs,p):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,parentManifestSha256=PIN,
        reviewSha256=p['reviewSha256'],queueSha256=p['queueSha256'],independentMetadataNegativeVectors=26,negativeLabels=labels,
        independentScopeReconstruction=12,purposeReasonCheck='INDEPENDENT_SOURCE_GUARDS_AND_MANUAL_PURPOSE_RISK_ANCHORS_NOT_DYNAMIC_VERDICT',
        newManualReviews=20,productTestsExecuted=0,combinedPurposeOrReferenceRows=1014,remainingSelectedUnreferenced=477,
        javaTypeOrCfgProof=False,actualGraphCalls=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
