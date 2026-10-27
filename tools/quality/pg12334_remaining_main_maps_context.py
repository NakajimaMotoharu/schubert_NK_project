"""Eight unchanged private Main map builders; source-only applicability evidence, no target invocation."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
from trace_owner_join import join_rows,validate

SOURCE='442441c83f73935eb2bd33cd40a7b9884eb7dfe3'
OUT=data.BASE/'PG12334-remaining-main-maps-context-v1'
INV='documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
M='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MaintenanceRunFiles.java'
I='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot.java'
CASES={
 'PMD-02847':(M,'retirementScan','runs','INVENTORY','WBS-P004-03'),
 'PMD-02848':(M,'retirementScan','begins','INVENTORY','WBS-P004-03'),
 'PMD-02849':(M,'retirementScan','done','INVENTORY','WBS-P004-03'),
 'PMD-02850':(M,'retirementScan','plans','INVENTORY','WBS-P004-03'),
 'PMD-02853':(M,'scan','runs','GRAPH','WBS-P004-03'),
 'PMD-02854':(M,'scan','begins','GRAPH','WBS-P004-03'),
 'PMD-02855':(M,'scan','done','GRAPH','WBS-P004-03'),
 'PMD-03093':(I,'parse','fields','SNAPSHOT','WBS-P004-04')}
CONTROLS={
 'INVENTORY':['returnnewInventory(runs,begins,done,active,plans,marker);','Inventory{runs=Map.copyOf(runs);begins=Map.copyOf(begins);done=Map.copyOf(done);plans=Map.copyOf(plans);}','synchronized(stateLock){'],
 'GRAPH':['returngraph(runs,begins,done,active);','returnnewGraph(Map.copyOf(runs),Map.copyOf(begins),Map.copyOf(done),active,pending.stream().findFirst());','privatestaticGraphgraph(','synchronized(stateLock){'],
 'SNAPSHOT':['this.values=Map.copyOf(values);','privatefinalMap<String,String>values;','varresult=newInspectorUnitSnapshot(fields,target);','returnresult;']}
REASONS={
 'INVENTORY':'retirementScan allocates four new maps on each private invocation; decoded immutable value records alone are inserted, no mutable builder crosses an IO/decoder/callback boundary. The only map return is the private Inventory compact constructor which defensively copies all four maps. Session.perform serialization is supplemental, not a substitute for this local-to-copy non-escape argument. No retirement or original-file operation executed.',
 'GRAPH':'scan allocates three fresh maps per private invocation. After synchronous local graph validation, graph copies all three into the private Graph record before returning. All map values are immutable BatchRun/Activation/Completion records. No builder is a field or concurrent callback argument; no real scan, filesystem or lifecycle action executed.',
 'SNAPSHOT':'parse allocates its own fields map and private construction copies it into a final immutable values field before publication. Keys/values are immutable Strings, observations return no mutable map alias; input bytes are cloned/wiped. This source review is neither real Unit observation nor process/startup/stop ownership proof.'}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    normal=data.read_checked(data.BASE/'PG12312-readiness-dependency-six-compile-v1/manifest.json','96605de485f83a38656ca3d0f479f679f708193d263671784582acb088d4b88b')
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    chosen={r['id']:r for r in original if r['id'] in CASES};assert set(chosen)==set(CASES)
    raw=(data.ROOT/INV).read_bytes();logical={r['path']:r for r in json.loads(raw)['artifacts']}
    hashes=normal['begin']['inputHashes'];support={}
    for stem in ('BatchRun','MaintenanceActivation','MaintenanceCompletion'):
        path='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/'+stem+'.java'
        text=(data.ROOT/path).read_text();assert data.sha(text.encode())==hashes[path] and 'public record '+stem+'(' in text
        support[path]=hashes[path]
    actual=[]
    for r in chosen.values():
        node=ET.Element('violation',r['attributes']);node.text=r['message'];actual.append((r['path'],node))
    ownership_inputs=[dict(path=p,sha256=hashes[p],owner=logical[p]['owner']) for p in sorted({M,I})]
    ownership=join_rows(ownership_inputs,logical,hashes,'WBS-F03');validate(ownership,ownership_inputs,logical,hashes,'WBS-F03')
    rows=[]
    for path,node in actual:
        ident=original_match(path,node,original,actual);expected_path,method,variable,strategy,owner=CASES[ident['id']]
        text=(data.ROOT/path).read_text();sha=data.sha(text.encode());a=dict(node.attrib)
        assert path==expected_path and Path(path).suffix=='.java' and sha==hashes[path]==chosen[ident['id']]['inputSha256']
        assert node.get('rule')=='UseConcurrentHashMap' and a['method']==method and a['variable']==variable
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))]
        compact=''.join(t for t,_ in ts);assert all(c in compact for c in CONTROLS[strategy])
        lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi,name=min((v for v in functions(ts) if v[0]<=point<=v[1]),key=lambda v:v[1]-v[0]);assert name==method
        body=''.join(t for t,_ in ts[lo:hi+1]);assert body.count('newHashMap<>();')=={'INVENTORY':4,'GRAPH':3,'SNAPSHOT':1}[strategy]
        artifact=logical[path];assert artifact['owner']==artifact['costOwner']==owner
        rows.append(dict(id=ident['id'],path=path,sourceKind='MAIN',rule='UseConcurrentHashMap',attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=sha,sourceSpanSha256=data.sha(text[start:end].encode()),method=method,variable=variable,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=CONTROLS[strategy],copyStrategy=strategy,reason=REASONS[strategy],disposition='CONTEXT_NOT_APPLICABLE',kind='LOCAL_MAP_TO_PRIVATE_IMMUTABLE_COPY',canonicalOwner=owner,canonicalCostOwner=owner,registeredHistoricalSourceSha256=artifact['sha256'],registrationShaMatchesCurrentSource=artifact['sha256']==sha,currentProductQualification=None,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0))
    count=len({r['id'] for r in rows});assert count==len(rows)==8
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows,supportValueSourceHashes=support,canonicalOwnership=ownership))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),inventorySha256=data.sha(raw),sourceContexts=count,rawRetained=count,rawRetainedMeaning='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholeStaticScopeRaw=None,reviewedMainSourceCount=len(ownership),supportValueSourceCount=len(support),sourceCorrections=0,productTestsExecuted=0,normalBuildsExecuted=0,staticAnalyzerRuns=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,externalActions=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
