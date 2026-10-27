"""Five retained original Test thread applicability reasons from actual current20 and static XML."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='af3f0f86d295ed721f5c1b41670ef224eb1d49e3'
OUT=data.BASE/'PG12726-alert-threshold-context-v1'
METHOD_CONTROLS={'threshold014ConcurrentStatelessEvaluations':['try(varexecutor=Executors.newFixedThreadPool(4))','index<64','executor.invokeAll(tasks,10,TimeUnit.SECONDS)','future.get()','executor.shutdownNow()','assertTrue(executor.awaitTermination(10,TimeUnit.SECONDS))','assertEquals(expected,future.get())']}


def main():
    invocation=capture(__file__);assert not OUT.exists()
    hp=data.BASE/'PG12720-alert-threshold-host-v1/manifest.json';host=data.read_checked(hp,'ccb4a097f17f8e40779ca3f01f3ab79a876f0c33eccb94d27c31f54661562513');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==14
    sp=data.BASE/'PG12722-alert-threshold-static-v1';st=data.read_checked(sp/'manifest.json','2cd61dcada2767e9c62b6e580d0e5e2215758471408d6e69833e9d6452996707');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'] and st['reports']['pmd']['findings']==4 and st['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        ident=original_match(path,node,original,actual);a=dict(node.attrib);rule=a['rule'];method=a.get('method');text=(data.ROOT/path).read_text();sha=data.sha(text.encode());assert sha==host['begin']['sourceInputHashes'][path]
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        point=next(i for i,(_,p) in enumerate(ts) if p==start)
        assert method in METHOD_CONTROLS;lo,hi,name=min((v for v in functions(ts) if v[0]<=point<=v[1]),key=lambda v:v[1]-v[0]);assert name==method;holder=method;controls=METHOD_CONTROLS[method]
        assert rule=='DoNotUseThreads'
        kind='FINITE_OWNED_PURE_ALERT_THRESHOLD_WORKERS'
        reason='Standalone JavaSE whole JUnit fixture owns four workers with64 finite pure numeric callbacks, independent SS literal expected values. TWR and original shutdownNow/awaitTermination10seconds remain. invokeAll has10second task bound; get and TWR close have no local deadline, distinct outer JVM240seconds. No application worker, collector, DB, FS, network, VM, Root, native, credential or authority operations. Four historical context references source-rebound only; raw4 retained.'
        body=''.join(t for t,_ in ts[lo:hi+1]);assert all(c in body for c in controls)
        case_refs=[c for c in host['begin']['cases'] if c['path']==path and c['method']==method];assert case_refs
        assert all(any(a['classname']==c['className'] and a['name']==c['method'] and not a['nonPass'] for a in host['cases']) for c in case_refs)
        rows.append(dict(id=ident['id'],path=path,rule=rule,attributes=a,originalRowSha256=ident['rowSha256'],source=SOURCE,sourceSha256=sha,sourceSpanSha256=data.sha(text[start:end].encode()),scopeName=holder,scopeKind='OWNER_CLASS' if method is None else 'METHOD',scopeTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),controls=controls,currentCases=case_refs,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',reason=reason,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0))
    count=len({r['id'] for r in rows});assert count==len(rows)==4
    verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=count,rawRetained=count,rawRetainedMeaning='COUNT_UNIQUE_SELECTED_REVIEWED_RETAINED_FINDING_IDS',wholeStaticScopeRaw=count,productTestsExecuted=0,sourceCorrections=0,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
