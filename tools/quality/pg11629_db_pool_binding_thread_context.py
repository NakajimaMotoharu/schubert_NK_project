"""Current source JavaSE applicability of20 existing thread references; no target code execution."""
from pathlib import Path
import xml.etree.ElementTree as ET
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg11370_source_constructor_owner_audit import functions
from pg11569_four_repository_scope_facts import span
from pg11054_api_request_context import original_match

SOURCE='b2790ba78d8876c058dfcebf46e25805ac0bf56e'
OUT=data.BASE/'PG11629-db-pool-binding-thread-context-v1'

def review():
    normal=data.read_checked(data.BASE/'PG11614-db-pool-binding-literal-six-compile-v1/manifest.json','da1fa15da3656d99970d1bd3afe64efee9a7fe5e153d2144af2f79c69662f16f')
    host=data.read_checked(data.BASE/'PG11616-db-pool-binding-literal-host-v1/manifest.json','99a7d4eff8df99df5fa0f9b697ebf87c4b6ed662aa6499bd779900c5b8f9de67')
    post=data.read_checked(data.BASE/'PG11620-db-pool-binding-literal-post-v1/manifest.json','4752359ce64abacc7e6fe314c6cbb62fd20a18ef52395e65849899bc30f366f3')
    assert normal['source']==host['source']==post['source']==SOURCE and normal['actualExit']==host['actualExit']==post['actualExit']==0
    assert host['observedTestExecutions']==30 and not host['oldExecUnion']
    sp=data.BASE/'PG11618-db-pool-binding-literal-static-v1';st=data.read_checked(sp/'manifest.json','5a3585696589d6307496597bc5672bde35d35d71dddc2db09962b48c353bc334');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    rows=[];counts=Counter();kinds=Counter()
    for path,node in actual:
        if node.get('rule')!='DoNotUseThreads':continue
        text=(data.ROOT/path).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][path]
        tokens=canonical(text);compact=''.join(tokens)
        assert 'Executors.newFixedThreadPool(2)' in compact and compact.count('workers.submit(')==2
        assert 'first.get(30,TimeUnit.SECONDS);second.get(30,TimeUnit.SECONDS);' in compact
        assert 'finally{release.countDown();workers.shutdownNow();assertTrue(workers.awaitTermination(30,TimeUnit.SECONDS));}' in compact
        assert 'latch.await(30,TimeUnit.SECONDS)' in compact and 'TimeUnit.SECONDS.toNanos(30)' in compact
        assert not any(s in text for s in ('@Before','@After','@ExtendWith','@Disabled','@TempDir','ProcessBuilder','getConnection(','new Socket(','HttpServer.create(','System.getenv','setAccessible'))
        point,_,fragment=span(text,node.attrib);ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
        index=next(i for i,(_,pos) in enumerate(ts) if pos==point)
        ma,mb,method=min((s for s in functions(ts) if s[0]<=index<=s[1]),key=lambda s:s[1]-s[0]);assert method==node.get('method')
        target=next(c for c in host['begin']['cases'] if c['path']==path and '010OneRetainedCollector' in c['method'])
        assert method in ('await',target['method']) and any(c['classname']==target['className'] and c['name']==target['method'] and not c['nonPass'] for c in host['cases'])
        identity=original_match(path,node,original,actual);counts[path]+=1
        if 'newFixedThreadPool' in fragment:kind='OWN_TWO_WORKERS'
        elif 'workers.submit' in fragment:kind='OWN_BOUNDED_TASK'
        elif 'shutdownNow' in fragment or 'awaitTermination' in fragment:kind='FINALLY_OWN_STOP_WAIT'
        elif fragment=='Thread>':kind='TYPE_ONLY'
        else:kind='THREAD_IDENTITY_INTERRUPT_OR_STATE_OBSERVATION'
        kinds[kind]+=1
        rows.append(dict(id=identity['id'],path=path,source=SOURCE,sourceSha256=normal['begin']['inputHashes'][path],attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],
            sourceSpanSha256=data.sha(fragment.encode()),methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),method=method,kind=kind,currentCase=target,
            disposition='CONTEXT_NOT_APPLICABLE',reason='J2EE thread restriction is not applicable to this exact dedicated JavaSE JUnit source point: one owned two-worker collector serialization test, bounded30s future/latch waits, release+shutdownNow+termination in finally; type/observation/interrupt points do not grant external actor ownership. Typed pool statistics proxies never acquire a DB/pool/JMX resource. Raw warning retained; no general thread exemption or current whole qualification.',
            previousReferenceRetainedAsHistorical=True,currentWholeJoinPending=True,rawWarningRetained=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False))
    assert len(rows)==20 and sorted(counts.values())==[10,10]
    assert kinds==Counter(OWN_TWO_WORKERS=2,OWN_BOUNDED_TASK=4,FINALLY_OWN_STOP_WAIT=4,TYPE_ONLY=2,THREAD_IDENTITY_INTERRUPT_OR_STATE_OBSERVATION=8)
    return dict(source=SOURCE,rows=rows,kindCounts=dict(kinds),sourceHashes={p:normal['begin']['inputHashes'][p] for p in counts},existingReferenceSourceReauthenticated=20,newIndividualDispositions=0,
        currentRuntimeReferencedNotReexecuted=30,productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0)

def main():
    invocation=capture(__file__);assert not OUT.exists();value=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),existingReferenceSourceReauthenticated=20,newIndividualDispositions=0,productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
