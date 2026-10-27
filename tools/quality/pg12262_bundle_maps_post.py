"""Independent field/method/caller/owner checks for seven source reasons, no target operation."""
import copy
import json
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11054_api_request_context import original_match
from trace_owner_join import validate as validate_owner_rows

SOURCE='d8a2b7952b321b75fe7fcc1c8d3acb287faca6ec'
PIN='8afbd022d68c9437ef6854aa51c69a705a456d2311f76946f52d0a10011b6a05'
OUT=data.BASE/'PG12262-bundle-maps-post-v1'
BACKUP='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/BackupArtifactVerifier.java'
RELEASE='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/ReleasePayloadVerification.java'
CALLER='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/StartupReleaseManifest.java'
EXPECTED={
 'PMD-02774':(BACKUP,'METHOD','observePending','LOCKED_OPERATION_LOCAL_BUILDER'),
 'PMD-02775':(BACKUP,'METHOD','observePending','LOCKED_OPERATION_LOCAL_BUILDER'),
 'PMD-02776':(BACKUP,'METHOD','verifyAt','LOCKED_OPERATION_LOCAL_BUILDER'),
 'PMD-02777':(BACKUP,'METHOD','verifyAt','LOCKED_OPERATION_LOCAL_BUILDER'),
 'PMD-06190':(RELEASE,'FIELD','jars','REQUEST_SCOPED_PRIVATE_COLLECTOR_FIELD'),
 'PMD-06191':(RELEASE,'FIELD','checksums','REQUEST_SCOPED_PRIVATE_COLLECTOR_FIELD'),
 'PMD-06194':(RELEASE,'METHOD','archive','ARCHIVE_LOCAL_BUILDER_IMMUTABLE_RESULT')}
CONTROLS={BACKUP:['files=Map.copyOf(files);','contents=Map.copyOf(contents);','returnnewPendingDigests(','returnnewBundleSnapshot(','lock.lock();','lock.unlock();'],RELEASE:['finalclassReleasePayloadVerification{','privatefinalMap<String,JarValue>jars=newHashMap<>();','privatefinalMap<String,Integer>checksums=newHashMap<>();','returnnewJarValue(Set.copyOf(classes),Map.copyOf(sql));','java.util.stream.Collectors.toUnmodifiableMap(']}

def lex(text):return [(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def method_tokens(ts,name,point=None):
    tokens=[t for t,_ in ts];ranges=[]
    for i,t in enumerate(tokens[:-1]):
        if t!=name or tokens[i+1]!='(':continue
        j=i+1;depth=0
        while j<len(tokens):
            if tokens[j]=='(':depth+=1
            if tokens[j]==')':
                depth-=1
                if depth==0:break
            j+=1
        j+=1
        if j>=len(tokens) or tokens[j] not in ('{','throws'):continue
        while j<len(tokens) and tokens[j] not in ('{',';','}'):j+=1
        if j>=len(tokens) or tokens[j]!='{':continue
        end=j;depth=0
        while end<len(tokens):
            if tokens[end]=='{':depth+=1
            if tokens[end]=='}':
                depth-=1
                if depth==0:break
            end+=1
        if point is None or i<=point<=end:ranges.append((i,end))
    if len(ranges)!=1:raise ValueError('one enclosing method declaration, not an archive callback invocation')
    lo,hi=ranges[0];return tokens[lo:hi+1]

def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG12260-bundle-maps-context-v1';m=data.read_checked(p/'manifest.json',PIN);v=data.read_checked(p/'review.json',m['reviewSha256']);rows=v['rows']
    normal=data.read_checked(data.BASE/'PG12224-check-health-six-compile-v1/manifest.json','d65964a4fd58702926206ea8ae5c101ac445b66936e15bda5c9a29c355b129e2');hashes=normal['begin']['inputHashes'];assert normal['source']==SOURCE
    raw=(data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes();assert data.sha(raw)==m['inventorySha256'];logical={r['path']:r for r in json.loads(raw)['artifacts']}
    owners=validate_owner_rows(v['ownership'],v['ownershipInputs'],logical,hashes,'WBS-F03');assert {r['path'] for r in owners}=={BACKUP,RELEASE,CALLER}
    assert all(r['canonicalOwner']==r['canonicalCostOwner']==('WBS-P017-05' if r['path']==BACKUP else 'WBS-P018-02') and not r['currentSourcePtQualificationInferred'] and not r['historicalRunReassigned'] and r['additionalSharedCostPp']==0 for r in owners)
    construction={}
    for path in hashes:
        if '/src/main/java/' not in path or not path.endswith('.java'):continue
        tape='\0'.join(t for t,_ in lex((data.ROOT/path).read_text()));count=len(re.findall('new\0ReleasePayloadVerification\0\\(',tape))
        if count:construction[path]=count
    assert construction=={CALLER:2};ct=lex((data.ROOT/CALLER).read_text());entrypoints={}
    for method in ('verify','verifyCandidate'):
        tokens=method_tokens(ct,method);assert ''.join(tokens).count('newReleasePayloadVerification(this,group,io,security).verify(release,version,approval)')==1;entrypoints[method]=data.sha('\0'.join(tokens).encode())
    caller=dict(path=CALLER,sourceSha256=hashes[CALLER],newCollectorSites=2,onlyCurrentMainConstructionCaller=True,entrypointTokenHashes=entrypoints,publicCollectorReturned=False,verificationExecuted=False);assert caller==v['collectorCaller']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');selected={r['id']:r for r in original if r['id'] in EXPECTED};actual=[]
    for r in selected.values():
        node=ET.Element('violation',r['attributes']);node.text=r['message'];actual.append((r['path'],node))
    def validate(row):
        path,scope,name,kind=EXPECTED[row['id']];orig=selected[row['id']];a=orig['attributes'];text=(data.ROOT/path).read_text();ts=lex(text);compact=''.join(t for t,_ in ts)
        assert data.sha(text.encode())==orig['inputSha256']==hashes[path] and all(c in compact for c in CONTROLS[path]) and compact.count('newHashMap<>();')=={BACKUP:4,RELEASE:3}[path]
        lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);point=next(i for i,(_,p) in enumerate(ts) if p==start)
        if scope=='FIELD':assert 'method' not in a and name==a['variable'];tokens=[t for t,_ in lex(lines[int(a['beginline'])-1])]
        else:assert a['method']==name;tokens=method_tokens(ts,name,point)
        node=next(n for p,n in actual if p==path and n.attrib==a);ident=original_match(path,node,original,actual);owner='WBS-P017-05' if path==BACKUP else 'WBS-P018-02';artifact=logical[path]
        expected=dict(path=path,sourceKind='MAIN',rule='UseConcurrentHashMap',attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=hashes[path],sourceSpanSha256=data.sha(text[start:end].encode()),scope=scope,scopeName=name,scopeTokenSha256=data.sha('\0'.join(tokens).encode()),kind=kind,controls=CONTROLS[path],disposition='CONTEXT_NOT_APPLICABLE',canonicalOwner=owner,canonicalCostOwner=owner,registeredHistoricalSourceSha256=artifact['sha256'],registrationShaMatchesCurrentSource=artifact['sha256']==hashes[path],collectorCaller=caller if path==RELEASE else None,currentProductQualification=None,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0)
        if any(row.get(k)!=value for k,value in expected.items()) or not row.get('reason'):raise ValueError('independent field/method/caller/owner and no-runtime contract required')
    assert len(rows)==7 and {r['id'] for r in rows}==set(EXPECTED)
    for row in rows:validate(row)
    sample=next(r for r in rows if r['id']=='PMD-06190');bad_caller=copy.deepcopy(caller);bad_caller['newCollectorSites']=1
    bad_graph=copy.deepcopy(caller);bad_graph['onlyCurrentMainConstructionCaller']=False
    bad_entries=copy.deepcopy(caller);bad_entries['entrypointTokenHashes']={}
    bad_run=copy.deepcopy(caller);bad_run['verificationExecuted']=True
    negatives=0
    for field,value in [('source','0'*40),('scope','METHOD'),('scopeName','verify'),('scopeTokenSha256','0'*64),('attributes',{**sample['attributes'],'method':'verify'}),('collectorCaller',None),('collectorCaller',bad_caller),('collectorCaller',bad_graph),('collectorCaller',bad_entries),('collectorCaller',bad_run),('currentProductQualification',{'pass':True}),('registeredHistoricalSourceSha256','0'*64),('canonicalCostOwner','WBS-F03'),('controls',[]),('reason',''),('currentWholeJoinPending',False),('productTestsExecutedByReview',1),('oldRuntimeReassigned',True),('newAccepted',1),('kind','THREAD_CONFINED_LOCAL_BUILDER')]:
        bad=copy.deepcopy(sample);bad[field]=value
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('invalid source/caller metadata accepted')
    ownership_negatives=0
    for field,value in [('canonicalOwner','WBS-F03'),('canonicalCostOwner','WBS-F03'),('historicalRunReassigned',True),('currentSourcePtQualificationInferred',True)]:
        bad=copy.deepcopy(owners);bad[0][field]=value
        try:validate_owner_rows(bad,v['ownershipInputs'],logical,hashes,'WBS-F03')
        except ValueError:ownership_negatives+=1
        else:raise AssertionError('owner/cost/runtime reassignment accepted')
    assert negatives==20 and ownership_negatives==4 and m['source']==SOURCE and m['productTestsExecuted']==m['sourceCorrections']==0 and m['fieldContexts']==2
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=7,rawRetained=7,fieldContexts=2,methodContexts=5,metadataNegativeVectors=negatives,ownershipNegativeVectors=ownership_negatives,currentMainCollectorCallers=1,currentMainNewCollectorSites=2,sourceCorrections=0,productTestsExecuted=0,nativeOperationsExecuted=0,newRuntimeQualifiedClasses=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,externalActions=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
