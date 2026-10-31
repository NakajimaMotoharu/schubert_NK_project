"""Fresh whole-source purpose review of 20 generic diagnostics, not dynamic/type/Graph qualification."""
from collections import Counter
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PRIOR=('PG16137-systemd-apiro-saved-reference27-v2','d8225e47447559e38cf7e15d4600757ee9d25af56b07e6f7ffe82ae22c290aa6')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
OUT=data.BASE/'PG16142-readiness-generic20-current-purpose-v1'
API='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/ApiDependencyReadiness.java'
WEB='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebDependencyReadiness.java'
PINS={API:'a9510db3be2c058715da8c4f089d3f49b2e9224447bf6685aeb23f12400d594e',WEB:'bf5f3f6357c91a01dc2d8dfcf8b45687e42a011099d6c286cd54c3a6c8de35ab'}
BODY=('SQLException','RuntimeException','Error')
JMS=('RuntimeException','Error')
CAT_DB=('SQLException','RuntimeException')
CAT_JMS=('RuntimeException',)
SITES={
 API:{60:('BODY',BODY,'failure',None),66:('CLEANUP',BODY,'closing',None),74:('CATALOG',CAT_DB,'failure','API database unavailable'),
      102:('BODY',JMS,'failure',None),108:('CLEANUP',JMS,'closing',None),118:('CATALOG',CAT_JMS,'failure','API Artemis receive queues unavailable')},
 WEB:{34:('BODY',BODY,'failure',None),40:('CLEANUP',BODY,'closing',None),47:('CATALOG',CAT_DB,'failure','Web technical database'),
      58:('BODY',JMS,'failure',None),64:('CLEANUP',JMS,'closing',None),71:('CATALOG',CAT_JMS,'failure','Web Artemis reply Queue')}}
REASONS={
 'BODY':'The owned admission body may fail with RuntimeException or direct Error as well as its declared JDBC failure. Record the same primary and rethrow it through the mandatory close scope; removing unchecked capture skips the explicit primary/cleanup precedence. This is a failed startup path, not a successful fallback or NPE normalization.',
 'CLEANUP':'The already-acquired Connection/JMSContext close site must be attempted after body failure and before normal progress. No primary, or direct close Error versus non-Error primary, selects the closing failure; otherwise retain primary and transient secondary for module-local fatal classification. Removing this boundary or substituting unconditional finally throw changes SSC330. Actual close/graph behavior remains unproved.',
 'CATALOG':'Only ordinary SQLException/RuntimeException reaches the fixed non-success catalog after module-local preserveFatal. Direct Error is not added to this normalizing outer catch. No retry, ready=true or partial success is returned from failure; the source orders DB failure before broker probing. Hidden Error traversal and actual provider admission remain unproved.'}
RISK='SOURCE PURPOSE ONLY: not Java type resolution, complete CFG proof, actual provider/null/close multiplicity, finite Throwable graph, blocking/deadline, live DB/JMS readiness, ownership, native, or dynamic PT qualification.'
LEX=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|[A-Za-z_$][A-Za-z_$0-9]*|\S')

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def catches(text):
    require(text.isascii() and '\r' not in text and '\\u' not in text,'fixed ordinary ASCII source')
    tokens=[(m.group(),m.start(),m.end()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*','"'))]
    result=[]
    for i,(word,start,end) in enumerate(tokens):
        if word!='catch':continue
        require(tokens[i+1][0]=='(','catch header')
        close=i+2
        while tokens[close][0]!=')':close+=1
        require(tokens[close+1][0]=='{','catch body brace')
        stop=close+2;depth=1
        while depth:
            depth+=(tokens[stop][0]=='{')-(tokens[stop][0]=='}');stop+=1
        header=[t[0] for t in tokens[i+2:close]];parameter=header[-1]
        types=tuple(v for v in header[:-1] if v!='|')
        result.append(dict(line=text.count('\n',0,start)+1,start=start,end=tokens[stop-1][2],
            headerEnd=tokens[close][2],types=types,parameter=parameter,
            bodyTokens=''.join(t[0] for t in tokens[close+2:stop-1]),
            bodyText=text[tokens[close+1][2]:tokens[stop-1][1]]))
    return result

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs=[read(v) for v in (PRIOR,OBS)]
    normal=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    require(prior['actualExit']==obs['actualExit']==normal['actualExit']==normal['testsExecuted']==0
            and prior['source']==obs['source']==normal['source']==SOURCE,'same fixed source/normal, no Product replay')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==497 and prior['combinedSelectedReferences']==898 and prior['combinedPurposeReviewed']==96,'prior current domains')
    observations=data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])
    observations={v['staticObservationId']:v for v in observations}
    selected=[v for v in queue if v['path'] in PINS and v['rule']=='AvoidCatchingGenericException']
    require(len(selected)==20 and Counter(v['path'] for v in selected)==Counter({API:10,WEB:10}),'all20 diagnostics only')
    by_path={};scope_facts=[]
    for path,pin in PINS.items():
        text=(data.ROOT/path).read_text();require(data.sha(text.encode())==pin==normal['begin']['inputHashes'][path],'whole source199 lines fixed')
        found=catches(text);require({v['line'] for v in found}==set(SITES[path]) and len(found)==6,'all six catch headers per Source')
        marker='TemporaryInfrastructureException' if path==API else 'WebStartupException'
        for c in found:
            purpose,types,parameter,literal=SITES[path][c['line']]
            require(c['types']==types and c['parameter']==parameter,'independent manual exact header table')
            if purpose=='BODY':require(c['bodyTokens']=='primary=failure;throwfailure;','same primary retained and rethrown')
            if purpose=='CLEANUP':
                expected='if(primary==null||closinginstanceofError&&!(primaryinstanceofError)){throwclosing;}'+marker+'.attachSecondary(primary,closing);'
                require(c['bodyTokens']==expected,'explicit direct fatal precedence and transient secondary')
            if purpose=='CATALOG':
                cls='IllegalStateException' if path==API else 'WebStartupException'
                require(c['bodyTokens']==marker+'.preserveFatal(failure);thrownew'+cls+'();'
                        and c['bodyText'].count('"'+literal+'"')==1,'fatal classification before exact fixed failure catalog')
            c.update(path=path,purpose=purpose,catalogLiteral=literal,sourceSha256=pin)
            scope_facts.append(c)
        require(text.count('connection.close();')==text.count('context.close();')==1,'one textual close site each, not dynamic proof')
        by_path[path]=(text,found)
    rows=[]
    for current in selected:
        text,found=by_path[current['path']];start,stop,token=span(text,current['attributes'])
        scopes=[v for v in found if v['start']<=start<stop<=v['headerEnd']]
        require(len(scopes)==1 and token in ('RuntimeException','Error'),'one exact diagnostic header operand')
        c=scopes[0];actual=observations[current['id']]
        require(actual['currentSource']==SOURCE and actual['sourceSha256']==PINS[current['path']]
                and actual['attributes']==current['attributes'] and actual['path']==current['path'],'full current observation source/attrs')
        rows.append(dict(**current,currentSource=SOURCE,manualPurposeReviewComplete=True,
            canonicalSpanStart=start,canonicalSpanEndExclusive=stop,canonicalSpanSha256=data.sha(token.encode()),
            typeToken=token,catchLine=c['line'],catchStart=c['start'],catchEnd=c['end'],catchTypes=list(c['types']),
            catchParameter=c['parameter'],catchPurpose=c['purpose'],catchBodyTokenSha256=data.sha(c['bodyTokens'].encode()),
            catalogLiteral=c['catalogLiteral'],reason=REASONS[c['purpose']],residualRisk=RISK,
            diagnosticMessageSha256=data.sha(actual['message'].encode()),status='SOURCE_PURPOSE_REVIEWED_DYNAMIC_AND_WHOLE_STATIC_HOLD',
            rawRetained=True,ptExecutionExempt=False,actualViolation=None,productTestsExecuted=0,coverage=None,
            sourceChanged=False,oldRuntimeTransferred=False))
    require(Counter(v['catchPurpose'] for v in rows)==Counter(BODY=8,CLEANUP=8,CATALOG=4),'20operands/12headers')
    designs=[
      'documents/300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md',
      'documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md',
      'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md',
      'documents/300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md']
    design_hashes={}
    for path in designs:
        body=(data.ROOT/path).read_bytes();require(subprocess.check_output(['git','show','origin/main:'+path],cwd=data.ROOT)==body,'approved origin main')
        design_hashes[path]=data.sha(body)
    require('SSC330' in (data.ROOT/designs[2]).read_text(),'current approved fatal and resource precedence')
    ids={v['id'] for v in rows};remaining=[v for v in queue if v['id'] not in ids]
    for v in (prior,obs):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,sourceHashes=PINS,approvedDesignHashes=design_hashes,
                                    scopeFacts=scope_facts,rows=rows,fullSourceTextReadForReview=True,javaTypeOrCfgProof=False))
    data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,priorManifestSha256=PRIOR[1],
        priorQueueSha256=prior['queueSha256'],reviewSha256=data.sha((OUT/'review.json').read_bytes()),
        queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),
        newManualReviews=20,newReferenceConnections=0,combinedSelectedReferences=898,combinedPurposeReviewed=116,
        combinedPurposeOrReferenceRows=1014,remainingSelectedUnreferenced=477,sourcePrograms=2,catchHeaders=12,operands=20,
        prior5960PurposesTransferred=False,sourceCodeChangeRequiredByThisReview=False,
        rawSuppressed=0,actualViolationCount=None,productTestsExecuted=0,oldProductToolsReexecuted=0,coverage=None,
        sourceChanged=False,externalActions=0,actualGraphCalls=0,javaTypeOrCfgProof=False,
        wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
