"""Seven locked-operation/request-collector map contexts, source/caller only; no verifier invocation."""
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
from trace_owner_join import join_rows

SOURCE='d8a2b7952b321b75fe7fcc1c8d3acb287faca6ec'
OUT=data.BASE/'PG12260-bundle-maps-context-v1'
INV='documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
IDS={'PMD-02774','PMD-02775','PMD-02776','PMD-02777','PMD-06190','PMD-06191','PMD-06194'}
CALLER='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/StartupReleaseManifest.java'
BACKUP='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/BackupArtifactVerifier.java'
RELEASE='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/ReleasePayloadVerification.java'
CONTROLS={BACKUP:['files=Map.copyOf(files);','contents=Map.copyOf(contents);','returnnewPendingDigests(','returnnewBundleSnapshot(','lock.lock();','lock.unlock();'],RELEASE:['finalclassReleasePayloadVerification{','privatefinalMap<String,JarValue>jars=newHashMap<>();','privatefinalMap<String,Integer>checksums=newHashMap<>();','returnnewJarValue(Set.copyOf(classes),Map.copyOf(sql));','java.util.stream.Collectors.toUnmodifiableMap(']}

def lex(text):return [(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def main():
    invocation=capture(__file__);assert not OUT.exists()
    normal=data.read_checked(data.BASE/'PG12224-check-health-six-compile-v1/manifest.json','d65964a4fd58702926206ea8ae5c101ac445b66936e15bda5c9a29c355b129e2');hashes=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');chosen={r['id']:r for r in original if r['id'] in IDS};assert set(chosen)==IDS
    raw=(data.ROOT/INV).read_bytes();inventory=json.loads(raw);logical={r['path']:r for r in inventory['artifacts']}
    ownership_inputs=[dict(path=p,sha256=hashes[p],owner=logical[p]['owner']) for p in (BACKUP,RELEASE,CALLER)];ownership=join_rows(ownership_inputs,logical,hashes,'WBS-F03');owners={r['path']:r for r in ownership}
    assert owners[BACKUP]['canonicalOwner']==owners[BACKUP]['canonicalCostOwner']=='WBS-P017-05' and all(owners[p]['canonicalOwner']==owners[p]['canonicalCostOwner']=='WBS-P018-02' for p in (RELEASE,CALLER))
    calls={}
    for path in hashes:
        if '/src/main/java/' not in path or not path.endswith('.java'):continue
        ts=lex((data.ROOT/path).read_text());tokens=[t for t,_ in ts];points=[i for i in range(len(tokens)-2) if tokens[i:i+3]==['new','ReleasePayloadVerification','(']]
        if points:calls[path]=points
    assert set(calls)=={CALLER} and len(calls[CALLER])==2
    caller=(data.ROOT/CALLER).read_text();ct=lex(caller);caller_scopes={}
    for method in ('verify','verifyCandidate'):
        spans=[v for v in functions(ct) if v[2]==method];assert len(spans)==1;lo,hi,_=spans[0];body=''.join(t for t,_ in ct[lo:hi+1])
        assert body.count('newReleasePayloadVerification(this,group,io,security).verify(release,version,approval)')==1
        caller_scopes[method]=data.sha('\0'.join(t for t,_ in ct[lo:hi+1]).encode())
    caller_fact=dict(path=CALLER,sourceSha256=hashes[CALLER],newCollectorSites=2,onlyCurrentMainConstructionCaller=True,entrypointTokenHashes=caller_scopes,publicCollectorReturned=False,verificationExecuted=False)
    actual=[]
    for r in chosen.values():
        node=ET.Element('violation',r['attributes']);node.text=r['message'];actual.append((r['path'],node))
    rows=[]
    for path,node in actual:
        ident=original_match(path,node,original,actual);text=(data.ROOT/path).read_text();ts=lex(text);compact=''.join(t for t,_ in ts)
        assert path in CONTROLS and data.sha(text.encode())==hashes[path]==chosen[ident['id']]['inputSha256'] and all(c in compact for c in CONTROLS[path])
        assert compact.count('newHashMap<>();')=={BACKUP:4,RELEASE:3}[path] and not any(t in ('Executors','ThreadPoolExecutor','parallelStream') for t,_ in ts)
        a=dict(node.attrib);lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        method=a.get('method');variable=a['variable'];point=next(i for i,(_,p) in enumerate(ts) if p==start)
        if method:
            lo,hi,_=min((v for v in functions(ts) if v[2]==method and v[0]<=point<=v[1]),key=lambda v:v[1]-v[0]);scope_tokens=[t for t,_ in ts[lo:hi+1]];scope='METHOD'
        else:
            assert path==RELEASE and variable in ('jars','checksums');scope_tokens=[t for t,_ in lex(lines[int(a['beginline'])-1])];scope='FIELD'
        if path==BACKUP:
            kind='LOCKED_OPERATION_LOCAL_BUILDER';reason='Each observed/snapshot map belongs to the current operation callback under the verifier private lock. observePending returns digest values only, never either map. verifyAt returns BundleSnapshot whose compact constructor copies files and contents. I/O callbacks receive paths/claims, not these mutable maps. Actual backup/read/force/removal/lock acquisition is not executed or qualified.'
        elif scope=='FIELD':
            kind='REQUEST_SCOPED_PRIVATE_COLLECTOR_FIELD';reason='Not assumed local: these are private final mutable maps of a package-private final collector. The complete current Main construction search finds only two inline new-collector-and-immediate-verify callbacks, one per public verify/verifyCandidate invocation. No collector/map is returned or cached; recursive walk/agreement use the same lexical collector. This is current-source call-graph confinement, not a general concurrent reuse permission or real release verification.'
        else:
            kind='ARCHIVE_LOCAL_BUILDER_IMMUTABLE_RESULT';reason='The archive callback allocates a distinct local SQL map, fills it sequentially and copies it through Map.copyOf into private JarValue. The mutable builder does not escape. Contents are separately collected as an unmodifiable map from inventory, not the collector fields. No archive/release/native operation is executed or qualified.'
        owner=owners[path];artifact=logical[path]
        rows.append(dict(id=ident['id'],path=path,sourceKind='MAIN',rule='UseConcurrentHashMap',attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=hashes[path],sourceSpanSha256=data.sha(text[start:end].encode()),scope=scope,scopeName=method or variable,scopeTokenSha256=data.sha('\0'.join(scope_tokens).encode()),kind=kind,controls=CONTROLS[path],reason=reason,disposition='CONTEXT_NOT_APPLICABLE',canonicalOwner=owner['canonicalOwner'],canonicalCostOwner=owner['canonicalCostOwner'],registeredHistoricalSourceSha256=artifact['sha256'],registrationShaMatchesCurrentSource=artifact['sha256']==hashes[path],collectorCaller=caller_fact if path==RELEASE else None,currentProductQualification=None,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0))
    assert len(rows)==7 and sum(r['scope']=='FIELD' for r in rows)==2 and all(r['currentProductQualification'] is None for r in rows)
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows,ownershipInputs=ownership_inputs,ownership=ownership,collectorCaller=caller_fact))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),inventorySha256=data.sha(raw),normalManifestSha256='d65964a4fd58702926206ea8ae5c101ac445b66936e15bda5c9a29c355b129e2',sourceContexts=7,reviewedMainSources=2,callerSources=1,fieldContexts=2,methodContexts=5,rawRetained=7,sourceCorrections=0,normalBuildsExecuted=0,staticAnalyzerRuns=0,productTestsExecuted=0,nativeOperationsExecuted=0,currentSourceRuntimeReferences=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,externalActions=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
