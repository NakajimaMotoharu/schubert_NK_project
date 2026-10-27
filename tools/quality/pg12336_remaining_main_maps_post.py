"""Independent original-node/method/owner/copy checks and malformed metadata vectors; no Product calls."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11054_api_request_context import original_match
from pg12248_main_local_maps_post import enclosing_method
from trace_owner_join import validate as validate_join

SOURCE='442441c83f73935eb2bd33cd40a7b9884eb7dfe3'
PIN='4227b10cee4cf12fdb0bf19af53bd3f75236625d4470680294fa8d80cb91a17e'
OUT=data.BASE/'PG12336-remaining-main-maps-post-v1'
EXPECTED={
 'PMD-02847':('retirementScan','runs','INVENTORY','WBS-P004-03'),
 'PMD-02848':('retirementScan','begins','INVENTORY','WBS-P004-03'),
 'PMD-02849':('retirementScan','done','INVENTORY','WBS-P004-03'),
 'PMD-02850':('retirementScan','plans','INVENTORY','WBS-P004-03'),
 'PMD-02853':('scan','runs','GRAPH','WBS-P004-03'),
 'PMD-02854':('scan','begins','GRAPH','WBS-P004-03'),
 'PMD-02855':('scan','done','GRAPH','WBS-P004-03'),
 'PMD-03093':('parse','fields','SNAPSHOT','WBS-P004-04')}
CONTROLS={
 'INVENTORY':['returnnewInventory(runs,begins,done,active,plans,marker);','Inventory{runs=Map.copyOf(runs);begins=Map.copyOf(begins);done=Map.copyOf(done);plans=Map.copyOf(plans);}','synchronized(stateLock){'],
 'GRAPH':['returngraph(runs,begins,done,active);','returnnewGraph(Map.copyOf(runs),Map.copyOf(begins),Map.copyOf(done),active,pending.stream().findFirst());','privatestaticGraphgraph(','synchronized(stateLock){'],
 'SNAPSHOT':['this.values=Map.copyOf(values);','privatefinalMap<String,String>values;','varresult=newInspectorUnitSnapshot(fields,target);','returnresult;']}

def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG12334-remaining-main-maps-context-v1'
    m=data.read_checked(p/'manifest.json',PIN);review=data.read_checked(p/'review.json',m['reviewSha256']);rows=review['rows']
    normal=data.read_checked(data.BASE/'PG12312-readiness-dependency-six-compile-v1/manifest.json','96605de485f83a38656ca3d0f479f679f708193d263671784582acb088d4b88b');hashes=normal['begin']['inputHashes']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');chosen={r['id']:r for r in original if r['id'] in EXPECTED}
    raw=(data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes();assert data.sha(raw)==m['inventorySha256'];logical={r['path']:r for r in json.loads(raw)['artifacts']}
    actual=[]
    for r in chosen.values():
        node=ET.Element('violation',r['attributes']);node.text=r['message'];actual.append((r['path'],node))
    assert len(rows)==len({r['id'] for r in rows})==8 and set(chosen)==set(EXPECTED)=={r['id'] for r in rows}
    def validate(row):
        if row.get('id') not in EXPECTED:raise ValueError('known original finding ID required')
        method,variable,strategy,owner=EXPECTED[row['id']];r=chosen[row['id']];path=r['path'];a=r['attributes'];text=(data.ROOT/path).read_text();sha=data.sha(text.encode())
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];compact=''.join(t for t,_ in ts)
        assert sha==hashes[path]==r['inputSha256'] and all(c in compact for c in CONTROLS[strategy])
        lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi=enclosing_method(ts,method,point)
        assert ''.join(t for t,_ in ts[lo:hi+1]).count('newHashMap<>();')=={'INVENTORY':4,'GRAPH':3,'SNAPSHOT':1}[strategy]
        nodes=[n for p,n in actual if p==path and dict(n.attrib)==a];assert len(nodes)==1
        ident=original_match(path,nodes[0],original,actual);artifact=logical[path];assert artifact['owner']==artifact['costOwner']==owner
        expected=dict(path=path,sourceKind='MAIN',rule='UseConcurrentHashMap',attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=sha,sourceSpanSha256=data.sha(text[start:end].encode()),method=method,variable=variable,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=CONTROLS[strategy],copyStrategy=strategy,disposition='CONTEXT_NOT_APPLICABLE',kind='LOCAL_MAP_TO_PRIVATE_IMMUTABLE_COPY',canonicalOwner=owner,canonicalCostOwner=owner,registeredHistoricalSourceSha256=artifact['sha256'],registrationShaMatchesCurrentSource=artifact['sha256']==sha,currentProductQualification=None,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason'):raise ValueError('exact independent node/span/copy/canonical owner and no dynamic qualification required')
    for row in rows:validate(row)
    sample=next(r for r in rows if r['id']=='PMD-02847');labels=[]
    for field,value in [('id','foreign'),('source','0'*40),('sourceKind','TEST'),('path','src/foreign.java'),('reason',''),('sourceSha256','0'*64),('sourceSpanSha256','0'*64),('method','scan'),('variable','foreign'),('controls',[]),('copyStrategy','SHARED_MUTABLE_FIELD'),('canonicalOwner','WBS-F03'),('canonicalCostOwner','WBS-F03'),('registeredHistoricalSourceSha256','0'*64),('currentProductQualification',{}),('currentWholeJoinPending',False),('productTestsExecutedByReview',1),('oldRuntimeReassigned',True),('newAccepted',1)]:
        bad=copy.deepcopy(sample);bad[field]=value
        try:validate(bad)
        except ValueError:labels.append(field)
        else:raise AssertionError('wrong source-only applicability metadata accepted')
    def counts(value):
        if value.get('sourceContexts')!=len(chosen) or value.get('rawRetained')!=len(chosen) or value.get('rawRetainedMeaning')!='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS' or value.get('wholeStaticScopeRaw','missing') is not None or value.get('sourceCorrections')!=0 or value.get('newAccepted')!=0:raise ValueError('selected unique ID count and whole-source unknown required')
    counts(m)
    for field,value in [('sourceContexts',7),('rawRetained',3),('rawRetainedMeaning','WHOLE_GLOBAL_RAW'),('wholeStaticScopeRaw',0),('sourceCorrections',8),('newAccepted',1)]:
        bad=dict(m);bad[field]=value
        try:counts(bad)
        except ValueError:labels.append('manifest.'+field)
        else:raise AssertionError('wrong auxiliary count/scope accepted')
    paths=sorted({r['path'] for r in rows});original_owners=[dict(path=p,sha256=hashes[p],owner=logical[p]['owner']) for p in paths]
    validate_join(review['canonicalOwnership'],original_owners,logical,hashes,'WBS-F03')
    for field,value in [('canonicalOwner','WBS-F03'),('canonicalCostOwner','WBS-F03'),('currentSourcePtQualificationInferred',True)]:
        bad=copy.deepcopy(review['canonicalOwnership']);bad[0][field]=value
        try:validate_join(bad,original_owners,logical,hashes,'WBS-F03')
        except ValueError:labels.append('owner.'+field)
        else:raise AssertionError('wrong ownership qualification accepted')
    support=review['supportValueSourceHashes'];assert len(support)==3
    for path,h in support.items():assert data.sha((data.ROOT/path).read_bytes())==hashes[path]==h and 'public record ' in (data.ROOT/path).read_text()
    assert len(labels)==28 and normal['source']==SOURCE and m['source']==review['source']==SOURCE and m['productTestsExecuted']==m['sourceCorrections']==0 and not m['wholeF03Accepted']
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=len(chosen),rawRetained=len(chosen),metadataNegativeVectors=len(labels),metadataNegativeLabels=labels,reviewedMainSourceCount=len(paths),supportValueSources=support,sourceCorrections=0,productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,externalActions=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
