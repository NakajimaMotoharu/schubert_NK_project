"""Independent current five XML/span/method/case/closed-flow bindings,8 metadata negatives."""
import copy
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
SOURCE='913eedbc22a42fa077c2c408baa7d63f7004abc3'
OUT=data.BASE/'PG12051-api-web-scrape-fixture-context-post-v1'
PIN='8a1d76ee89e42839efa9b827a5c563825fec0bb04537ba46b8d89b3546c113a0'
def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG12053-api-web-scrape-fixture-context-v2';m=data.read_checked(p/'manifest.json',PIN);rows=data.read_checked(p/'review.json',m['reviewSha256'])['rows'];host=data.read_checked(data.BASE/'PG12046-api-web-scrape-fixture-host-v1/manifest.json','dd0589eac679dfba08ccc9cc581b630ad160784d7eb1a6e69b9bd36fc4ec6cb9');sp=data.BASE/'PG12048-api-web-scrape-fixture-static-v1';st=data.read_checked(sp/'manifest.json','8611c53e8258e30c485fb8fc95ced1ec763286324b0f3ab524bf2bc844d28b40');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'];actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');mapped={(p,tuple(sorted(n.attrib.items()))):original_match(p,n,original,actual) for p,n in actual}
    def validate(row):
        path=row['path'];a=row['attributes'];text=(data.ROOT/path).read_text();lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi,name=min((v for v in functions(ts) if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);compact=''.join(t for t,_ in ts[lo:hi+1]);ident=mapped[(path,tuple(sorted(a.items())))];thread=a['rule']=='DoNotUseThreads';case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name);expected=dict(id=ident['id'],originalRowSha256=ident['rowSha256'],rule=a['rule'],source=SOURCE,sourceSha256=host['begin']['sourceInputHashes'][path],sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),currentCase=case,kind='OWN_FINITE64_PURE_SCRAPE_WORKERS' if thread else 'EXPLICIT_ALREADY_CLOSED_EMPTY_SDK_REGISTRY_FIXTURE',disposition='CONTEXT_NOT_APPLICABLE' if thread else 'REQUIRED_CONTRACT',previousReferenceRetainedAsHistorical=thread,newSourceReason=not thread,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason'):raise ValueError('current exact source/span/method/case/flow required')
        assert data.sha(text.encode())==row['sourceSha256'] and host['source']==SOURCE and host['actualExit']==0
        if thread:assert name==('apipol012FiniteConcurrentCallsKeepSource' if 'ApiMetric' in path else 'scrape012FiniteConcurrentScrapesRemainIndependent') and 'Executors.newFixedThreadPool(4)' in compact and 'workers.submit(' in compact and 'job.get(10,TimeUnit.SECONDS)' in compact and ('i<64' in compact or 'index<64' in compact)
        else:
            assert a['rule']=='CloseResource' and name=='apipol008ClosedSourceNotReopenedOrReadByStandard';body=[t for t,_ in ts[lo:hi+1]];assert body[:15]==['apipol008ClosedSourceNotReopenedOrReadByStandard','(',')','{','var','source','=','new','Compatible','(',')',';','source','.','close'];assert body[15:18]==['(',')',';'];assert 'assertTrue(source.isClosed());' in compact and 'policy.scrape(source,STANDARD_MODE)' in compact and 'policy.scrape(source,DEBUG_MODE)' in compact
        assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
    assert len(rows)==len(mapped)==len({r['id'] for r in rows})==5 and Counter(r['rule'] for r in rows)==Counter(DoNotUseThreads=4,CloseResource=1)
    for row in rows:validate(row)
    assert m['closedFixtureGuardVectors']==dict(positive=1,negative=8,methodNameStartRequired=True,productionExecuted=False) and data.sha((data.ROOT/'tools/quality/pg12049_api_web_scrape_fixture_context.py').read_bytes())==m['failedPriorEntrySha256']=='1e07fdb71799ea4fb77ee2b625e205d2ba5f6a431f3907042e425efb93caf5fc'
    negatives=0
    for field,value in [('source','0'*40),('oldRuntimeReassigned',True),('reason',''),('sourceSpanSha256','0'*64),('method','foreign'),('currentCase',{}),('disposition','SUPPRESSED'),('currentWholeJoinPending',False)]:
        bad=copy.deepcopy(rows[0]);bad[field]=value
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('bad current source/reason binding accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=5,newSourceReasons=1,existingThreadReferencesReauthenticated=4,metadataNegativeVectors=negatives,closedGuardPositiveVectors=1,closedGuardNegativeVectors=8,priorFailedEntryUnchanged=True,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
