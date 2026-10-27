"""Four finite JavaSE worker references plus one intentionally already-closed SDK fixture; raw retained."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
SOURCE='913eedbc22a42fa077c2c408baa7d63f7004abc3'
OUT=data.BASE/'PG12053-api-web-scrape-fixture-context-v2'
def closed_fixture(compact):
    prefix='apipol008ClosedSourceNotReopenedOrReadByStandard(){varsource=newCompatible();source.close();'
    return isinstance(compact,str) and compact.startswith(prefix) and all(v in compact for v in ('policy.scrape(source,STANDARD_MODE)','policy.scrape(source,DEBUG_MODE)','assertTrue(source.isClosed());'))
def guard_vectors():
    good='apipol008ClosedSourceNotReopenedOrReadByStandard(){varsource=newCompatible();source.close();assertEquals("",policy.scrape(source,STANDARD_MODE));assertThrows(IllegalStateException.class,()->policy.scrape(source,DEBUG_MODE));assertTrue(source.isClosed());}'
    assert closed_fixture(good)
    bads=[None,'','void'+good,good.replace('source.close();','',1),good.replace('source.close();','other.close();',1),good.replace('source.close();','policy.scrape(source,DEBUG_MODE);source.close();',1),good.replace('STANDARD_MODE','FOREIGN_MODE',1),good.replace('assertTrue(source.isClosed());','',1)]
    assert all(not closed_fixture(v) for v in bads)
    return dict(positive=1,negative=len(bads),methodNameStartRequired=True,productionExecuted=False)

def review():
    host=data.read_checked(data.BASE/'PG12046-api-web-scrape-fixture-host-v1/manifest.json','dd0589eac679dfba08ccc9cc581b630ad160784d7eb1a6e69b9bd36fc4ec6cb9');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==28;sp=data.BASE/'PG12048-api-web-scrape-fixture-static-v1';m=data.read_checked(sp/'manifest.json','8611c53e8258e30c485fb8fc95ced1ec763286324b0f3ab524bf2bc844d28b40');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==m['reports']['pmd']['sha256'] and m['actualExit']==1;actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        ident=original_match(path,node,original,actual);text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path];a=dict(node.attrib);lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi,name=min((v for v in functions(ts) if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);compact=''.join(t for t,_ in ts[lo:hi+1]);thread=a['rule']=='DoNotUseThreads'
        if thread:
            assert name==('apipol012FiniteConcurrentCallsKeepSource' if 'ApiMetric' in path else 'scrape012FiniteConcurrentScrapesRemainIndependent') and 'Executors.newFixedThreadPool(4)' in compact and 'workers.submit(' in compact and 'job.get(10,TimeUnit.SECONDS)' in compact and ('i<64' in compact or 'index<64' in compact)
            kind='OWN_FINITE64_PURE_SCRAPE_WORKERS';disposition='CONTEXT_NOT_APPLICABLE';reason='A dedicated JavaSE unit test owns four TWR workers and exactly64 finite pure SDK/text calls, with10-second Future bounds. All registry values are fixed before concurrent reads; no broker, DB, HTTP, VM, Root or service is called. This is not an application-managed J2EE thread or qualification of every production schedule.'
        else:
            assert a['rule']=='CloseResource' and name=='apipol008ClosedSourceNotReopenedOrReadByStandard' and closed_fixture(compact)
            kind='EXPLICIT_ALREADY_CLOSED_EMPTY_SDK_REGISTRY_FIXTURE';disposition='REQUIRED_CONTRACT';reason='The fresh empty Compatible SDK registry is explicitly closed before any policy call. STANDARD must not reopen/read it; DEBUG must reject it, and isClosed is asserted afterward. There is no open production handle/connection to release. The PMD ownership warning does not establish a leak; adding an implicit second close would change this deliberate closed-source fixture rather than repair an unclosed resource.'
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name);assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases']);rows.append(dict(id=ident['id'],path=path,rule=a['rule'],attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),currentCase=case,kind=kind,disposition=disposition,reason=reason,previousReferenceRetainedAsHistorical=thread,newSourceReason=not thread,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False))
    assert len(rows)==len({r['id'] for r in rows})==5 and sum(r['newSourceReason'] for r in rows)==1;return rows

def main():
    invocation=capture(__file__);assert not OUT.exists();vectors=guard_vectors();rows=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),closedFixtureGuardVectors=vectors,failedPriorEntrySha256='1e07fdb71799ea4fb77ee2b625e205d2ba5f6a431f3907042e425efb93caf5fc',sourceContexts=5,existingThreadReferencesReauthenticated=4,newSourceReasons=1,rawRetained=5,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
