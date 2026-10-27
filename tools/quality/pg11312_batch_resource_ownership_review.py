"""Bind31 existing public resource sites to exact owners/guards; no product execution or blanket exemption."""
import copy
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg11297_batch_standard_text_fixture_context import inputs
from pg11054_api_request_context import original_match
from pg10398_role_view_preflight import canonical

OUT=data.BASE/'PG11312-batch-resource-ownership-review-v1'
POST=data.BASE/'PG11314-batch-resource-ownership-review-post-v1'
SOURCE='d431ad964355c4e5c602fcb94fe0182da6ae3a61'
COUNTS=dict(DIRECT_ALREADY_CLOSED_CONTEXT_WHOLE_PENDING=7,RETAINED_GC_FINALLY_CLOSE_CONTEXT_WHOLE_PENDING=1,
    FAKE_NO_SDK_ACTIVATION_LOGICAL_LIFETIME_UNCLASSIFIED=6,OWNER_EXCEPTIONAL_GUARD_GAP_BUG1908=14,
    COMPOSITE_GC_CLEANUP_DEPENDS_ON_OWNER_GUARD=2,EXECUTOR_OWNER_SETUP_GUARD_AND_TWR_GAP_BUG1908=1)


def method_tokens(text,name):
    tokens=canonical(text)
    starts=[i for i in range(len(tokens)-2) if tokens[i:i+2]==['void',name]]
    if len(starts)!=1:
        raise ValueError('one exact existing ordinary Test method')
    a=starts[0]
    b=tokens.index('{',a)
    depth=1
    i=b+1
    while depth:
        depth+=(tokens[i]=='{')-(tokens[i]=='}')
        i+=1
    return tokens[a:i]


def basis(path,node):
    assert node.get('rule')=='CloseResource'
    text=(data.ROOT/path).read_text()
    tokens=method_tokens(text,node.get('method'))
    compact=''.join(tokens)
    stem=Path(path).stem
    method=node.get('method')
    variable=node.get('variable')
    if stem!='BatchStandardMetricSourceTest':
        if variable=='source':
            assert stem in ('BatchGcMetricRegistrationTest','BatchJvmMetricsTest','BatchSystemMetricsTest','BatchStandardMetricsTest')
            assert 'varsource=newRegistry();source.close();' in compact
            return dict(status='DIRECT_ALREADY_CLOSED_CONTEXT_WHOLE_PENDING',
                proof='Fresh empty Registry is closed immediately before any assertion/setup; subsequent operations intentionally test closed DEBUG/STD behavior',
                methodTokenSha256=data.sha('\0'.join(tokens).encode()),bug=None)
        assert stem=='BatchGcMetricRegistrationTest'
        if method=='batchgc001DefaultSdkIsOwnedAndClosedBeforeBorrowedRegistry':
            assert 'finally{for(varresource:owned)resource.close();}' in compact
            assert 'registration.bind(source,DEBUG_MODE,owned::add);' in compact and 'assertEquals(1,owned.size());' in compact
            return dict(status='RETAINED_GC_FINALLY_CLOSE_CONTEXT_WHOLE_PENDING',
                proof='Real fresh own-JVM GC is retained before activation; finally closes the one acknowledged handle before outer Registry TWR',
                methodTokenSha256=data.sha('\0'.join(tokens).encode()),bug=None)
        assert variable in ('resource','one','two') and ('var'+variable+'=newFake();') in compact
        fake=re.sub(r'\s+','',text)
        assert 'publicvoidbindTo(MeterRegistrysource){bindInvocations.incrementAndGet();onBindCallback.accept(source);}' in fake
        return dict(status='FAKE_NO_SDK_ACTIVATION_LOGICAL_LIFETIME_UNCLASSIFIED',
            proof='Fake bindTo never calls SDK activation; some paths transfer/close via owned list, reject/throw cases do not. Logical lifetime/exception cleanup not exempted',
            methodTokenSha256=data.sha('\0'.join(tokens).encode()),bug=None)
    if variable=='gc':
        assert method in ('batchhost011GcRetainedBeforeFatalAndClosedInReverseOrder','batchhost012FailedGcCloseKeepsRegistryAndExplicitRetryOwnership')
        assert 'vargc=newProbeGc(order);' in compact and 'ack.test(gc)' in compact and 'owner.close();' in compact
        return dict(status='COMPOSITE_GC_CLEANUP_DEPENDS_ON_OWNER_GUARD',
            proof='Main acknowledgement retains exact GC before error; normal owner.close handles it, exceptional Test lifetime depends on BUG1908 guard fix',
            methodTokenSha256=data.sha('\0'.join(tokens).encode()),bug='BUG-1908')
    assert variable in ('owner','executor') and 'owner.close();' in compact
    if method=='batchhost016CloseWaitsForOwnedScrapeAndThenRejectsNewScrapes':
        marker='owner.bind(DEBUG_MODE);varexecutor=Executors.newFixedThreadPool(2);try{'
        assert marker in compact and 'finally{release.countDown();executor.shutdownNow();assertTrue(executor.awaitTermination(10,TimeUnit.SECONDS));owner.close();}' in compact
        status='EXECUTOR_OWNER_SETUP_GUARD_AND_TWR_GAP_BUG1908' if variable=='executor' else 'OWNER_EXCEPTIONAL_GUARD_GAP_BUG1908'
        proof='Owner bind and executor construction precede first finally; a setup throw bypasses owner cleanup. Existing worker release/shutdown/await remains required'
    else:
        assert variable=='owner' and 'finally' not in tokens and 'newBatchStandardMetricSource(' in compact
        first_close=compact.index('owner.close();')
        assert 'assert' in compact[:first_close]
        status='OWNER_EXCEPTIONAL_GUARD_GAP_BUG1908'
        proof='Normal explicit close exists, but an earlier assertion/setup throw has no finally cleanup edge. Static counterexample, not an observed SDK leak'
    return dict(status=status,proof=proof,methodTokenSha256=data.sha('\0'.join(tokens).encode()),bug='BUG-1908')


def require(rows,normal,original,actual):
    from collections import Counter
    expected=[(p,n) for p,n in actual if n.get('rule')=='CloseResource']
    if len(rows)!=31 or len({r['id'] for r in rows})!=31 or Counter(r['basis']['status'] for r in rows)!=COUNTS:
        raise ValueError('all31 sites and exact concrete classification counts')
    expected_ids={original_match(p,n,original,actual)['id'] for p,n in expected}
    if {r['id'] for r in rows}!=expected_ids:
        raise ValueError('exact31 actual/original resource finding IDs')
    for row in rows:
        node=next((n for p,n in expected if p==row['path'] and dict(n.attrib)==row['attributes']),None)
        if node is None or original_match(row['path'],node,original,actual)['id']!=row['id']:
            raise ValueError('original warning and exact current coordinates')
        if row['source']!=SOURCE or row['sourceSha256']!=normal['begin']['inputHashes'][row['path']] or row['basis']!=basis(row['path'],node):
            raise ValueError('source and real owner/guard evidence')
        if row['productTestsExecuted']!=0 or row['coverage'] is not None or row['ptExecutionExempt'] or not row['rawWarningRetained']:
            raise ValueError('review cannot be product runtime, coverage, suppression or exemption')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    normal,original,actual=inputs()
    assert normal['source']==SOURCE
    rows=[]
    for path,node in actual:
        if node.get('rule')!='CloseResource':
            continue
        old=original_match(path,node,original,actual)
        rows.append(dict(id=old['id'],path=path,source=SOURCE,sourceSha256=normal['begin']['inputHashes'][path],
            attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],basis=basis(path,node),productTestsExecuted=0,
            coverage=None,rawWarningRetained=True,ptExecutionExempt=False))
    require(rows,normal,original,actual)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'sites.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,sitesSha256=data.sha((OUT/'sites.json').read_bytes()),
        reviewed=31,counts=COUNTS,rawWarningsRemoved=0,relatedBugs=['BUG-1908'],relatedYkt=['YKT-1659'],
        reviewStatus='CONCRETE_SITES_REVIEWED_WITH_CONFIRMED_TEST_GUARD_GAP_NOT_DYNAMIC_PASS',
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__)
    assert not POST.exists()
    primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA)
    rows=data.read_checked(OUT/'sites.json',primary['sitesSha256'])
    normal,original,actual=inputs()
    require(rows,normal,original,actual)
    bads=[rows[:-1],rows+[rows[0]]]
    for key,value in [('source','old'),('sourceSha256','0'*64),('productTestsExecuted',31),('coverage',100),
        ('rawWarningRetained',False),('ptExecutionExempt',True)]:
        bad=copy.deepcopy(rows)
        bad[0][key]=value
        bads.append(bad)
    bad=copy.deepcopy(rows)
    bad[0]['basis']['status']='ALL_RESOURCES_SAFE_PASS'
    bads.append(bad)
    for bad in bads:
        try:
            require(bad,normal,original,actual)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid owner/guard review metadata accepted')
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,
        sitesSha256=primary['sitesSha256'],reviewed=31,counts=COUNTS,metadataNegativeVectors=len(bads),
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


PRIMARY_SHA=None

if __name__=='__main__':
    main()
