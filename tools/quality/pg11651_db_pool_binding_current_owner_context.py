"""Current JavaSE20 source reauthentication and two bounded executor ownership point reviews; no target code execution."""
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

SOURCE='b4810698856cc2ae7edabb899a47aad34ef52cc2'
OUT=data.BASE/'PG11651-db-pool-binding-current-owner-context-v1'

def review():
    normal=data.read_checked(data.BASE/'PG11644-db-pool-binding-fatal-case-six-compile-v1/manifest.json','b6ab06836da09a0be7d6337e3c3d269b030afc06efc18352b9eb1034886b77b6')
    host=data.read_checked(data.BASE/'PG11646-db-pool-binding-fatal-case-host-v1/manifest.json','056a66e456e83ecdbcaffad464d50ce41d25955286457a364b188b92d43b687a')
    post=data.read_checked(data.BASE/'PG11650-db-pool-binding-fatal-case-post-v1/manifest.json','824e6ae171170484a2358a9a47f1203ea3335abdd583cba4aa74d5e201baa038')
    assert normal['source']==host['source']==post['source']==SOURCE and normal['actualExit']==host['actualExit']==post['actualExit']==0
    assert host['observedTestExecutions']==30 and not host['oldExecUnion']
    sp=data.BASE/'PG11648-db-pool-binding-fatal-case-static-v1';st=data.read_checked(sp/'manifest.json','acead561d795d044cc51826684268d6b2729f529fd86bd2bfa21688e887869c2');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    prior_path=data.BASE/'PG11629-db-pool-binding-thread-context-v1';prior=data.read_checked(prior_path/'manifest.json','4cd805b22bfd8bac876ccf0f4a1ea3f6d3377f13fc95c80f94e17dad43a73eb4');prior_value=data.read_checked(prior_path/'review.json',prior['reviewSha256']);prior_rows={r['id']:r for r in prior_value['rows']}
    rows=[];counts=Counter();kinds=Counter()
    for path,node in actual:
        if node.get('rule') not in ('DoNotUseThreads','CloseResource'):continue
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
        if node.get('rule')=='CloseResource':kind='REQUIRED_EXECUTOR_BOUNDED_STOP_FINALLY'
        elif 'newFixedThreadPool' in fragment:kind='OWN_TWO_WORKERS'
        elif 'workers.submit' in fragment:kind='OWN_BOUNDED_TASK'
        elif 'shutdownNow' in fragment or 'awaitTermination' in fragment:kind='FINALLY_OWN_STOP_WAIT'
        elif fragment=='Thread>':kind='TYPE_ONLY'
        else:kind='THREAD_IDENTITY_INTERRUPT_OR_STATE_OBSERVATION'
        kinds[kind]+=1
        rows.append(dict(id=identity['id'],path=path,source=SOURCE,sourceSha256=normal['begin']['inputHashes'][path],attributes=dict(node.attrib),originalRowSha256=identity['rowSha256'],
            sourceSpanSha256=data.sha(fragment.encode()),methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),method=method,kind=kind,currentCase=target,
            disposition='REQUIRED_CONTRACT' if node.get('rule')=='CloseResource' else 'CONTEXT_NOT_APPLICABLE',reason=('The exact worker handle is acquired immediately before try and always reaches finally release.countDown/shutdownNow/30-second awaitTermination; failure to terminate remains an assertion failure. This explicit bounded owner protocol is retained, not mechanically replaced by another lifecycle. Current010 success and inverse missing-stop/deadline negatives support this source fact; no real service termination is inferred.' if node.get('rule')=='CloseResource' else 'J2EE thread restriction is not applicable to this exact dedicated JavaSE JUnit source point: one owned two-worker collector serialization test, bounded30s future/latch waits, release+shutdownNow+termination in finally; type/observation/interrupt points do not grant external actor ownership. Typed pool statistics proxies never acquire a DB/pool/JMX resource. Raw warning retained; no general thread exemption or current whole qualification.'),
            previousReferenceRetainedAsHistorical=node.get('rule')=='DoNotUseThreads',newDispositionCreated=node.get('rule')=='CloseResource',currentWholeJoinPending=True,rawWarningRetained=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False))
    for row in rows:
        if row['id'] in prior_rows:assert row['methodTokenSha256']==prior_rows[row['id']]['methodTokenSha256']
        else:assert row['kind']=='REQUIRED_EXECUTOR_BOUNDED_STOP_FINALLY'
    assert set(prior_rows)=={r['id'] for r in rows if r['previousReferenceRetainedAsHistorical']}
    assert len(rows)==22 and sorted(counts.values())==[11,11]
    assert kinds==Counter(OWN_TWO_WORKERS=2,OWN_BOUNDED_TASK=4,FINALLY_OWN_STOP_WAIT=4,TYPE_ONLY=2,THREAD_IDENTITY_INTERRUPT_OR_STATE_OBSERVATION=8,REQUIRED_EXECUTOR_BOUNDED_STOP_FINALLY=2)
    return dict(source=SOURCE,rows=rows,kindCounts=dict(kinds),sourceHashes={p:normal['begin']['inputHashes'][p] for p in counts},existingReferenceSourceReauthenticated=20,currentExecutorOwnershipPointReviews=2,newIndividualDispositions=2,
        currentRuntimeReferencedNotReexecuted=30,productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0)

def main():
    invocation=capture(__file__);assert not OUT.exists();value=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),existingReferenceSourceReauthenticated=20,currentExecutorOwnershipPointReviews=2,newIndividualDispositions=2,productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
