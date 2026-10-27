"""Thirty exact full-payload JUnit/null/immediate-close contexts; nine duplicate/Comparable warnings unclassified."""
import copy
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11054_api_request_context import original_match
from pg11297_batch_standard_text_fixture_context import basis as batch_basis

OUT=data.BASE/'PG11387-full-payload-guard-context-v1'
POST=data.BASE/'PG11389-full-payload-guard-context-post-v1'
SOURCE='4aee5c4b73ffae5426e0cc5d15fc928e06ece7b8'


def inputs():
    normal=data.read_checked(data.BASE/'PG11380-full-payload-guard-six-compile-v1/manifest.json','f9691978776defaba64743818d99b493a80ab4f36b1cd30bae3eee542ab55be2')
    static_path=data.BASE/'PG11384-full-payload-guard-static-v1/manifest.json'
    static=data.read_checked(static_path,'075bc441fc602c77dfa0b6d7cb6eadcbf4c570893655850f6cb6140c47841a09')
    inverse=data.read_checked(data.BASE/'PG11378-full-payload-guard-source-post-v1/manifest.json','7e135397d059752d94d46a7475c54a388846a1150a5460600c0528915dd160bc')
    assert normal['source']==static['source']==SOURCE and normal['actualExit']==0 and inverse['allOriginalOracleTokensRestored']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    raw=(static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert len(actual)==39
    return normal,original,actual


def basis(path,node):
    stem=Path(path).stem
    if stem=='BatchMetricTextTest':
        return batch_basis(path,node)
    assert stem in ('ApiCustomMetricPayloadTest','WebCustomMetricPayloadTest')
    role='api' if stem.startswith('Api') else 'web'
    text=(data.ROOT/path).read_text()
    compact=re.sub(r'\s+','',text)
    rule,method=node.get('rule'),node.get('method')
    if rule=='AvoidDuplicateLiterals':
        return None
    if rule=='CloseResource':
        assert method==role+'pay011ClosedSourceIsNotReopenedOrClosedAgain' and node.get('variable')=='source'
        assert 'varsource=newBorrowed();source.close();assertThrows(' in compact
        return dict(kind='FRESH_CANDIDATE_IMMEDIATELY_CLOSED_BEFORE_ASSERTIONS',ownership='No intervening operation between acquisition and close; later oracle deliberately tests closed borrowed source. Raw warning retained, whole-current classification pending')
    assert rule=='DoNotUseThreads'
    if method==role+'pay013FiniteConcurrentIndependentPayloads':
        assert 'try(varworkers=Executors.newFixedThreadPool(4))' in compact
        assert 'i<64' in compact and 'job.get(10,TimeUnit.SECONDS)' in compact
        return dict(kind='FINITE_ORDINARY_JUNIT_OWN_MEMORY_PAYLOAD_WORKERS',workers=4,tasks=64,ownership='Each worker uses own Bundle TWR; fixed golden/ten-second futures/outerJVM240s, not application executor')
    if method==role+'full011ConcurrentFullScrapesKeepIndependentGoldenAndOwnership':
        assert 'try(varexecutor=Executors.newFixedThreadPool(4))' in compact
        assert 'executor.invokeAll(tasks,30,TimeUnit.SECONDS)' in compact and 'executor.awaitTermination(30,TimeUnit.SECONDS)' in compact
        return dict(kind='FINITE_ORDINARY_JUNIT_SHARED_STANDARD_OWNER_SCRAPES',workers=4,tasks=64,ownership='Owner outer TWR, executor inner TWR plus original shutdown/await30s, fixed own-JVM CPU golden/immutable Bundle')
    if method==role+'full012CallerCloseBetweenSourcesCannotReturnPartialText':
        assert 'varstandard=fullOwner(probe);try{try(varexecutor=Executors.newSingleThreadExecutor())' in compact
        assert 'finally{release.countDown();executor.shutdownNow();assertTrue(executor.awaitTermination(30,TimeUnit.SECONDS));standard.close();}' in compact
        assert 'finally{standard.close();}' in compact and 'future.get(30,TimeUnit.SECONDS)' in compact
        return dict(kind='FINITE_ORDINARY_JUNIT_CALLER_CLOSE_BETWEEN_BORROWED_VIEWS',workers=1,tasks=1,ownership='Immediate outer owner finally, own executor TWR, release/shutdown/await30s and original close identity oracle; no external caller')
    assert method=='awaitFull'
    assert 'release.await(30,TimeUnit.SECONDS)' in compact and 'Thread.currentThread().interrupt();' in compact
    return dict(kind='FINITE_OWN_LATCH_INTERRUPT_RESTORATION_HELPER',ownership='Only own worker latch30s; interrupt restored then fixed fixture exception propagated, no application thread lifecycle')


def require(rows,original,hashes,actual):
    if len(rows)!=30 or len({r['id'] for r in rows})!=30:
        raise ValueError('thirty unique concrete current contexts required')
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
    assert len(unclassified)==9
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        reviewed=30,unclassifiedOriginalIds=unclassified,rawWarnings=39,rawStaticGate=1,productTestsExecuted=0,coverage=None,
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
        contextsSha256=primary['contextsSha256'],metadataNegativeVectors=len(bads),reviewed=30,unclassified=9,rawStaticGate=1,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


PRIMARY_SHA=None

if __name__=='__main__':
    main()

