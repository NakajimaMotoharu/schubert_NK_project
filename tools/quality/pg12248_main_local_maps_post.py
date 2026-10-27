"""Independent source/method/span/owner validation of four local-map reasons and fourteen negative metadata vectors."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11054_api_request_context import original_match

SOURCE='d8a2b7952b321b75fe7fcc1c8d3acb287faca6ec'
PIN='1481093beb6c7d9642959dcd0b4b956236fda824f2df97379cbaf5ec23d7948e'
OUT=data.BASE/'PG12248-main-local-maps-post-v1'
EXPECTED={
 'PMD-00122':('AssetChecksumManifest.java','read','WBS-P009-03',['Map<String,String>hashes=newHashMap<>();','this.hashes=Map.copyOf(hashes);','returnnewAssetChecksumManifest(hashes);','privatestaticvoidaddLine(']),
 'PMD-07323':('MediaRangeService.java','respond','WBS-P009-04',['Map<String,String>headers=newHashMap<>();','response.begin(status,Map.copyOf(headers));','privatestaticvoidrespond(']),
 'PMD-03094':('MaintenanceStopSnapshot.java','parse','WBS-P018-04',['Map<String,String>fields=newHashMap<>();','this.fields=Map.copyOf(fields);','varresult=newMaintenanceStopSnapshot(unit,fields);','returnresult;']),
 'PMD-03111':('MaintenanceUnitStopPolicy.java','parse','WBS-P018-04',['Map<String,String>fields=newHashMap<>();','privatestaticvoidparse(','require(fields.putIfAbsent(','require("no".equals(fields.get("SendSIGKILL")));'])}

def enclosing_method(ts,name,point):
    values=[];tokens=[t for t,_ in ts]
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
        while j<len(tokens) and tokens[j] not in (';','{','}'):j+=1
        if j>=len(tokens) or tokens[j]!='{':continue
        end=j;depth=0
        while end<len(tokens):
            if tokens[end]=='{':depth+=1
            if tokens[end]=='}':
                depth-=1
                if depth==0:break
            end+=1
        if i<=point<=end:values.append((i,end))
    if len(values)!=1:raise ValueError('one explicit enclosing method declaration required')
    return values[0]

def main():
    invocation=capture(__file__);assert not OUT.exists();directory=data.BASE/'PG12246-main-local-maps-context-v1'
    m=data.read_checked(directory/'manifest.json',PIN);rows=data.read_checked(directory/'review.json',m['reviewSha256'])['rows']
    normal=data.read_checked(data.BASE/'PG12224-check-health-six-compile-v1/manifest.json','d65964a4fd58702926206ea8ae5c101ac445b66936e15bda5c9a29c355b129e2')
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');chosen={r['id']:r for r in original if r['id'] in EXPECTED}
    raw=(data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes();assert data.sha(raw)==m['inventorySha256'];artifacts={r['path']:r for r in json.loads(raw)['artifacts']}
    actual=[]
    for r in chosen.values():
        node=ET.Element('violation',r['attributes']);node.text=r['message'];actual.append((r['path'],node))
    runtime=next(r['currentProductQualification'] for r in rows if r['id']=='PMD-00122')
    host=data.read_checked(data.BASE/'PG12226-check-health-host-v1/manifest.json','6e409c526939f7e256aa8c6d17831b9d599e679d44c54744a7f878fb614a9ec4')
    case=next(c for c in host['begin']['cases'] if c['method']=='med044ConcurrentMatchesOwnImmutableInput')
    expected_runtime=dict(source=SOURCE,hostManifestSha256='6e409c526939f7e256aa8c6d17831b9d599e679d44c54744a7f878fb614a9ec4',postManifestSha256='318de790d7d7f2ddae2f9b9fc9091086967d37b8e68d1771d3b03f578769dffa',case=case,existingRunOnly=True,newProductExecutions=0)
    assert runtime==expected_runtime and len(rows)==4 and {r['id'] for r in rows}==set(EXPECTED)
    def validate(row):
        name,method,owner,controls=EXPECTED[row['id']];original_row=chosen[row['id']];path=original_row['path'];text=(data.ROOT/path).read_text();ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))]
        a=original_row['attributes'];lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi=enclosing_method(ts,method,point)
        node=next(n for p,n in actual if p==path);ident=original_match(path,node,original,actual);artifact=artifacts[path];sha=data.sha(text.encode())
        assert path.endswith('/'+name) and sha==original_row['inputSha256']==normal['begin']['inputHashes'][path] and artifact['owner']==artifact['costOwner']==owner
        compact=''.join(t for t,_ in ts);assert compact.count('newHashMap<>();')==1 and all(c in compact for c in controls)
        expected=dict(path=path,sourceKind='MAIN',rule='UseConcurrentHashMap',attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=sha,sourceSpanSha256=data.sha(text[start:end].encode()),method=method,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=controls,disposition='CONTEXT_NOT_APPLICABLE',kind='THREAD_CONFINED_LOCAL_BUILDER',canonicalOwner=owner,canonicalCostOwner=owner,registeredHistoricalSourceSha256=artifact['sha256'],registrationShaMatchesCurrentSource=artifact['sha256']==sha,currentProductQualification=expected_runtime if row['id']=='PMD-00122' else None,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason'):raise ValueError('source/span/control/owner/qualification must match independently')
    for row in rows:validate(row)
    sample=next(r for r in rows if r['id']=='PMD-00122');negatives=0
    for field,value in [('source','0'*40),('sourceKind','TEST'),('reason',''),('sourceSpanSha256','0'*64),('method','foreign'),('controls',[]),('canonicalCostOwner','WBS-F03'),('registeredHistoricalSourceSha256','0'*64),('registrationShaMatchesCurrentSource',True),('currentProductQualification',None),('currentWholeJoinPending',False),('productTestsExecutedByReview',1),('oldRuntimeReassigned',True),('newAccepted',1)]:
        bad=copy.deepcopy(sample);bad[field]=value
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('invalid Main applicability metadata accepted')
    assert negatives==14 and m['source']==SOURCE and m['sourceContexts']==m['rawRetained']==4 and m['productTestsExecuted']==m['sourceCorrections']==0 and m['wholeF03Accepted'] is False
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=4,rawRetained=4,metadataNegativeVectors=negatives,currentExistingRuntimeReferences=1,newProductTestsExecuted=0,newRuntimeQualifiedOtherClasses=0,sourceCorrections=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,externalActions=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
