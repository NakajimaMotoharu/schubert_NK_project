"""Four unchanged Main local-map applicability reviews; no target invocation or new product qualification."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='d8a2b7952b321b75fe7fcc1c8d3acb287faca6ec'
OUT=data.BASE/'PG12246-main-local-maps-context-v1'
INV='documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
CASES={
 'PMD-00122':('AssetChecksumManifest.java','read','WBS-P009-03',['Map<String,String>hashes=newHashMap<>();','this.hashes=Map.copyOf(hashes);','returnnewAssetChecksumManifest(hashes);','privatestaticvoidaddLine('],'Invocation-local checksum builder; private addLine only populates it and the private constructor copies it to a final immutable field before publication. The builder never escapes. Public requireMatches/entryCount only read the immutable field. Same-source med044 already verifies100 concurrent immutable lookups; no new run.'),
 'PMD-07323':('MediaRangeService.java','respond','WBS-P009-04',['Map<String,String>headers=newHashMap<>();','response.begin(status,Map.copyOf(headers));','privatestaticvoidrespond('],'Each response callback invocation constructs its own header builder; only Map.copyOf(headers) crosses the Response boundary. FileSource/Response may be external ports but the mutable map is neither a field nor an argument to those ports. The shared semaphore does not make this per-call builder shared. Source review only; no delivery/FileSource invocation.'),
 'PMD-03094':('MaintenanceStopSnapshot.java','parse','WBS-P018-04',['Map<String,String>fields=newHashMap<>();','this.fields=Map.copyOf(fields);','varresult=newMaintenanceStopSnapshot(unit,fields);','returnresult;'],'Each parse invocation allocates a distinct local map and private construction copies it to a final immutable field. It is exposed only through immutable String/enum/list observations and equality. Input is cloned and wiped; this reasoning does not establish real Unit state, stop authority or kernel ownership. Source review only.'),
 'PMD-03111':('MaintenanceUnitStopPolicy.java','parse','WBS-P018-04',['Map<String,String>fields=newHashMap<>();','privatestaticvoidparse(','require(fields.putIfAbsent(','require("no".equals(fields.get("SendSIGKILL")));'],'Private parse owns a fresh local map for four-key validation and returns void; no map is retained, returned or passed to a concurrent callback. Source/native reader ownership is separate. create/NativeSource/systemctl/requireSafe are not invoked by this review; no real stop or policy receipt is qualified.')}

def tokens(text):return [(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def main():
    invocation=capture(__file__);assert not OUT.exists()
    normal=data.read_checked(data.BASE/'PG12224-check-health-six-compile-v1/manifest.json','d65964a4fd58702926206ea8ae5c101ac445b66936e15bda5c9a29c355b129e2')
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    chosen={r['id']:r for r in original if r['id'] in CASES};assert set(chosen)==set(CASES)
    actual=[]
    for r in chosen.values():
        node=ET.Element('violation',r['attributes']);node.text=r['message'];actual.append((r['path'],node))
    inventory_raw=(data.ROOT/INV).read_bytes();inventory=json.loads(inventory_raw);artifacts={r['path']:r for r in inventory['artifacts']}
    host=data.read_checked(data.BASE/'PG12226-check-health-host-v1/manifest.json','6e409c526939f7e256aa8c6d17831b9d599e679d44c54744a7f878fb614a9ec4')
    post=data.read_checked(data.BASE/'PG12230-check-health-post-v1/manifest.json','318de790d7d7f2ddae2f9b9fc9091086967d37b8e68d1771d3b03f578769dffa')
    assert host['source']==post['source']==SOURCE and host['actualExit']==post['actualExit']==0 and host['observedTestExecutions']==8
    rows=[]
    for path,node in actual:
        ident=original_match(path,node,original,actual);name,method,owner,controls,reason=CASES[ident['id']];source=(data.ROOT/path).read_text();sha=data.sha(source.encode())
        assert Path(path).name==name and sha==normal['begin']['inputHashes'][path]==chosen[ident['id']]['inputSha256'] and node.get('rule')=='UseConcurrentHashMap'
        ts=tokens(source);compact=''.join(t for t,_ in ts);assert all(c in compact for c in controls) and compact.count('newHashMap<>();')==1
        a=dict(node.attrib);lines=source.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        i=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi,actual_method=min((v for v in functions(ts) if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);assert actual_method==method==node.get('method')
        artifact=artifacts[path];assert artifact['owner']==artifact['costOwner']==owner and artifact['kind']=='JAVA'
        qualification=None
        if ident['id']=='PMD-00122':
            case=next(c for c in host['begin']['cases'] if c['method']=='med044ConcurrentMatchesOwnImmutableInput');assert any(c['classname']==case['className'] and c['name']==case['method'] and not c['nonPass'] for c in host['cases'])
            assert post['artifactMeasurements']['api']['selectedValueFourCounters100']
            qualification=dict(source=SOURCE,hostManifestSha256='6e409c526939f7e256aa8c6d17831b9d599e679d44c54744a7f878fb614a9ec4',postManifestSha256='318de790d7d7f2ddae2f9b9fc9091086967d37b8e68d1771d3b03f578769dffa',case=case,existingRunOnly=True,newProductExecutions=0)
        rows.append(dict(id=ident['id'],path=path,sourceKind='MAIN',rule=a['rule'],attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=sha,sourceSpanSha256=data.sha(source[start:end].encode()),method=method,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=controls,reason=reason,disposition='CONTEXT_NOT_APPLICABLE',kind='THREAD_CONFINED_LOCAL_BUILDER',canonicalOwner=owner,canonicalCostOwner=owner,registeredHistoricalSourceSha256=artifact['sha256'],registrationShaMatchesCurrentSource=artifact['sha256']==sha,currentProductQualification=qualification,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0))
    assert len(rows)==4 and sum(r['currentProductQualification'] is not None for r in rows)==1 and sum(not r['registrationShaMatchesCurrentSource'] for r in rows)==1
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),originalFindingsSha256='92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966',inventorySha256=data.sha(inventory_raw),sourceContexts=4,rawRetained=4,newSourceReasons=4,sourceCorrections=0,normalBuildsExecuted=0,staticAnalyzerRuns=0,productTestsExecuted=0,currentSourceExistingRuntimeReferences=1,newRuntimeQualifiedOtherClasses=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,externalActions=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
