"""Nine exact finite JUnit worker/owner contexts; mutable Tag Comparable rule remains unclassified."""
import copy
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11054_api_request_context import original_match

OUT=data.BASE/'PG11113-web-pure-value-context-v1'
POST=data.BASE/'PG11115-web-pure-value-context-post-v1'
SOURCE='5fce2af667d8d5cdd9b67da9b02080b105848c28'


def inputs():
    normal=data.read_checked(data.BASE/'PG11106-web-pure-value-six-compile-v1/manifest.json','77fd485d4718416d3cb75e57e16458d2633289b432bb30a97738d326edcc364b')
    static_path=data.BASE/'PG11110-web-pure-value-static-v1/manifest.json'
    static=data.read_checked(static_path,'d9fb45add999405f77dd42178b344e1da40983e46fa8c3c897088f2db5bb03d6')
    proof=data.read_checked(data.BASE/'PG11112-web-pure-value-post-v1/manifest.json','811d07907c69923f43ccdfd66bbdd3e301cb7c50b03946a0e8135863354471a8')
    inverse=data.read_checked(data.BASE/'PG11104-web-pure-value-source-post-v1/manifest.json','73822a5a3bbd2a40eeff44f2b09b4ee1836da45ca3c777264e779a4ec4b1d1f9')
    assert normal['source']==static['source']==proof['source']==SOURCE and proof['actualExit']==0 and inverse['allOriginalOracleTokensRestored']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    raw=(static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert len(actual)==10
    return normal,original,actual


def basis(path,node):
    text=(data.ROOT/path).read_text()
    compact=re.sub(r'\s+','',text)
    stem=Path(path).stem
    if node.get('rule')=='OverrideBothEqualsAndHashCodeOnComparable':
        assert stem=='WebMetricCatalogTest' and node.get('method')=='compareTo' and 'class MutableTag implements Tag' in text
        return None
    assert node.get('rule') in ('CloseResource','DoNotUseThreads')
    if stem=='MediaResponseDecoderTest':
        assert node.get('method')=='med040ConcurrentDecodeOwnsBytesAndIsolatesRequests'
        assert 'try(varexecutor=Executors.newFixedThreadPool(8))' in compact and 'i<100' in compact
        assert 'job.get(10,TimeUnit.SECONDS)' in compact
        workers,tasks,owner=8,100,'TWR executor; all Futures10s; pure wire bytes; dedicated JVM240s'
    elif stem=='WebMetricCatalogTest':
        assert node.get('method')=='webcat014FiniteConcurrentCallsHaveNoRetainedMutableState'
        assert 'try(varworkers=Executors.newFixedThreadPool(4))' in compact and 'index<64' in compact and 'job.get(10,TimeUnit.SECONDS)' in compact
        workers,tasks,owner=4,64,'TWR executor; all Futures10s; immutable label metadata; dedicated JVM240s'
    else:
        assert stem=='HttpMetricContractTest' and node.get('method')=='httpMetric006ConcurrentClassifiersAreStateless'
        assert 'varexecutor=Executors.newFixedThreadPool(4);try{' in compact and 'index<64' in compact
        assert 'executor.invokeAll(tasks,10,TimeUnit.SECONDS)' in compact
        assert 'finally{executor.shutdownNow();assertTrue(executor.awaitTermination(10,TimeUnit.SECONDS));}' in compact
        workers,tasks,owner=4,64,'finally shutdownNow/awaitTermination10s asserted; invokeAll10s; no external resources; JVM240s'
    assert not any(t in text for t in ('ProcessBuilder','getConnection(','java.net.','LinuxDirectoryCalls','@Before','@After','@TempDir'))
    return dict(kind='EXECUTOR_EXPLICIT_FINALLY_OWNER' if node.get('rule')=='CloseResource' else 'FINITE_ORDINARY_JUNIT_NOT_J2EE_APPLICATION_RUNTIME',
        workers=workers,tasks=tasks,ownership=owner)


def require(rows,original,hashes,actual):
    if len(rows)!=9 or len({r['id'] for r in rows})!=9:
        raise ValueError('nine unique concrete current contexts required')
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
    assert len(unclassified)==1
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        reviewed=9,unclassifiedOriginalIds=unclassified,rawWarnings=10,rawStaticGate=1,productTestsExecuted=0,coverage=None,
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
        contextsSha256=primary['contextsSha256'],metadataNegativeVectors=len(bads),reviewed=9,unclassified=1,rawStaticGate=1,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


PRIMARY_SHA=None

if __name__=='__main__':
    main()
