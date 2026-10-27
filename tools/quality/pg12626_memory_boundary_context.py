"""Five retained original Test thread applicability reasons from actual current20 and static XML."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='915a8ed153b00d76a80164d36f9ce5b86d645046'
OUT=data.BASE/'PG12626-memory-boundary-context-v1'
METHOD_CONTROLS={'concurrentOwnership': ['try(varpool=Executors.newFixedThreadPool(12))', 'i<100', 'pool.invokeAll(work)', 'done.get(5,TimeUnit.SECONDS)', 'pool.submit(material::close)', 'closing.get(5,TimeUnit.SECONDS)'], 'web035ConcurrentGenerationAndMatchingStayIndependent': ['try(varpool=Executors.newFixedThreadPool(10))', 'i<100', 'pool.invokeAll(jobs)', 'future.get(20,TimeUnit.SECONDS)', 'assertEquals(100,values.size())']}


def main():
    invocation=capture(__file__);assert not OUT.exists()
    hp=data.BASE/'PG12620-memory-boundary-host-v1/manifest.json';host=data.read_checked(hp,'42a5c55b0a4ea53bd1f579f62b12b6dbe614506cea6123c3da6e300ca54b8e98');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==8
    sp=data.BASE/'PG12622-memory-boundary-static-v1';st=data.read_checked(sp/'manifest.json','d4cf88fc455039623e235190936553ad1d55c420c047fc5f693646f02f8e6011');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'] and st['reports']['pmd']['findings']==6 and st['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        ident=original_match(path,node,original,actual);a=dict(node.attrib);rule=a['rule'];method=a.get('method');text=(data.ROOT/path).read_text();sha=data.sha(text.encode());assert sha==host['begin']['sourceInputHashes'][path]
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point=next(i for i,(_,p) in enumerate(ts) if p==start)
        assert method in METHOD_CONTROLS;lo,hi,name=min((v for v in functions(ts) if v[0]<=point<=v[1]),key=lambda v:v[1]-v[0]);assert name==method;holder=method;controls=METHOD_CONTROLS[method]
        assert rule=='DoNotUseThreads'
        kind='FINITE_OWNED_MEMORY_INPUT_CSRF_FIXTURE_WORKERS'
        reason='Standalone JavaSE JUnit owns fixed12 or10 workers, each100 finite memory callbacks, TWR and finally erased synthetic buffers. Inspector get5seconds and CSRF get20seconds; invokeAll/TWR have no local timeout, distinct whole JVM bound240seconds. No application executor, real credentials, database, actual sessions, HTTP, Root, Unit, FFM, VM or network. Six historical context references are source-rebound, not new classifications; raw6 retained.'
        body=''.join(t for t,_ in ts[lo:hi+1]);assert all(c in body for c in controls)
        case_refs=[c for c in host['begin']['cases'] if c['path']==path and c['method']==method];assert case_refs
        assert all(any(a['classname']==c['className'] and a['name']==c['method'] and not a['nonPass'] for a in host['cases']) for c in case_refs)
        rows.append(dict(id=ident['id'],path=path,rule=rule,attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=sha,sourceSpanSha256=data.sha(text[start:end].encode()),scopeName=holder,scopeKind='OWNER_CLASS' if method is None else 'METHOD',scopeTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=controls,currentCases=case_refs,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',reason=reason,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0))
    count=len({r['id'] for r in rows});assert count==len(rows)==6
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=count,rawRetained=count,rawRetainedMeaning='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholeStaticScopeRaw=count,productTestsExecuted=0,sourceCorrections=0,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
