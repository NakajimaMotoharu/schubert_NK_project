"""Nine exact finite JUnit worker/owner contexts; mutable Tag Comparable rule remains unclassified."""
import copy
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11139-web-presentation-context-v1'
POST=data.BASE/'PG11141-web-presentation-context-post-v1'
SOURCE='497dea5e49082d063d1c41e5e17999a473db6c91'


def inputs():
    normal=data.read_checked(data.BASE/'PG11132-web-presentation-six-compile-v1/manifest.json','6ba6867e803958aa47837d6628faeecdf42917be8d23bff7a38b5e1b18579eee')
    static_path=data.BASE/'PG11136-web-presentation-static-v1/manifest.json'
    static=data.read_checked(static_path,'abe48dfe23f7b14485638cf467ba3593df309e84e2780836b295f04729b9345e')
    proof=data.read_checked(data.BASE/'PG11138-web-presentation-post-v1/manifest.json','3bb27a2ab2c5da7500ffb7c86e5395fc05a319c2cf28602b3c9876d01413f3c7')
    inverse=data.read_checked(data.BASE/'PG11130-web-presentation-source-post-v1/manifest.json','528f8b48f979c631a1cad041a13f95e7436a7768e014502632e92787ba2ac3f9')
    assert normal['source']==static['source']==proof['source']==SOURCE and proof['actualExit']==0 and inverse['allOriginalOracleTokensRestored']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    raw=(static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert len(actual)==5
    return normal,original,actual


def basis(path,node):
    text=(data.ROOT/path).read_text()
    compact=re.sub(r'\s+','',text)
    stem=Path(path).stem
    if node.get('rule')=='AvoidSynchronizedStatement':
        assert stem=='WebSecurityHeaderTest' and node.get('method')=='web094ConcurrentResponsesHaveNoSharedMutableState'
        assert 'synchronized(writer){for(varfuture:pool.invokeAll(jobs))future.get(10,TimeUnit.SECONDS);}' in compact
        main=data.ROOT/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/WebSecurityHeaderWriter.java'
        body=main.read_text()
        assert 'synchronized' not in body and 'ReentrantLock' not in body and 'public void writeHeaders' in body
        return dict(kind='PUBLIC_MONITOR_STATELESS_HEADER_WRITER_INDEPENDENCE_ORACLE',mainSha256=data.sha(body.encode()),
            ownership='Holds same public writer monitor while workers invoke it. invokeAll has no inner timeout; enclosing owned JVM240s bounds the negative contract.')
    assert node.get('rule')=='DoNotUseThreads'
    assert 'i<100' in compact
    if stem=='WebSecurityHeaderTest':
        assert node.get('method')=='web094ConcurrentResponsesHaveNoSharedMutableState'
        assert 'try(varpool=Executors.newFixedThreadPool(8))' in compact and 'future.get(10,TimeUnit.SECONDS)' in compact
        workers,seconds=8,10
    else:
        assert stem=='SavedRequestTargetTest' and node.get('method')=='web008ConcurrentTargetsRemainIndependent'
        assert 'try(varpool=Executors.newFixedThreadPool(10))' in compact and 'future.get(20,TimeUnit.SECONDS)' in compact
        workers,seconds=10,20
    assert not any(t in text for t in ('ProcessBuilder','getConnection(','java.net.','LinuxDirectoryCalls','@Before','@After','@TempDir'))
    return dict(kind='FINITE_ORDINARY_JUNIT_NOT_J2EE_APPLICATION_RUNTIME',workers=workers,tasks=100,
        futureSeconds=seconds,ownership='TWR owned executor, finite pure Mock header or URI value tasks; dedicated JVM240s')


def require(rows,original,hashes,actual):
    if len(rows)!=5 or len({r['id'] for r in rows})!=5:
        raise ValueError('five unique concrete current contexts required')
    for row in rows:
        node=next((n for p,n in actual if p==row['path'] and dict(n.attrib)==row['attributes']),None)
        if node is None or original_match(row['path'],node,original,actual)['id']!=row['id']:
            raise ValueError('original same-signature occurrence and actual coordinates')
        if row['source']!=SOURCE or row['sourceSha256']!=hashes[row['path']] or row['basis']!=basis(row['path'],node):
            raise ValueError('exact source and concrete owner/thread context')
        if row['status']!='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING' or not row['rawWarningRetained'] or row['ptExecutionExempt']:
            raise ValueError('no suppression or whole-current exemption')
        if row['productTestsExecuted']!=0 or row['coverage'] is not None or row['oldRuntimeReassigned']:
            raise ValueError('static review is not execution/coverage')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    normal,original,actual=inputs()
    rows,unclassified=[],[]
    for path,node in actual:
        old=original_match(path,node,original,actual)
        context=basis(path,node)
        if context is None:
            unclassified.append(old['id'])
            continue
        rows.append(dict(id=old['id'],path=path,source=SOURCE,sourceSha256=normal['begin']['inputHashes'][path],rule=node.get('rule'),
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],basis=context,status='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING',
            rawWarningRetained=True,ptExecutionExempt=False,productTestsExecuted=0,coverage=None,oldRuntimeReassigned=False))
    require(rows,original,normal['begin']['inputHashes'],actual)
    assert len(unclassified)==0
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        reviewed=5,unclassifiedOriginalIds=unclassified,rawWarnings=5,rawStaticGate=1,productTestsExecuted=0,coverage=None,
        wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__)
    assert not POST.exists()
    primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA)
    rows=data.read_checked(OUT/'contexts.json',primary['contextsSha256'])
    normal,original,actual=inputs()
    require(rows,original,normal['begin']['inputHashes'],actual)
    bads=[rows[:-1],rows+[rows[0]]]
    for k,v in [('source','old'),('sourceSha256','0'*64),('status','PASS'),('rawWarningRetained',False),('ptExecutionExempt',True),
        ('productTestsExecuted',24),('coverage',100),('oldRuntimeReassigned',True)]:
        bad=copy.deepcopy(rows)
        bad[0][k]=v
        bads.append(bad)
    for bad in bads:
        try:
            require(bad,original,normal['begin']['inputHashes'],actual)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid source/runtime/context metadata')
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,
        contextsSha256=primary['contextsSha256'],metadataNegativeVectors=len(bads),reviewed=5,unclassified=0,rawStaticGate=1,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


PRIMARY_SHA=None

if __name__=='__main__':
    main()

