"""Independent XML/span/enclosing-method and exact fixture ownership context validation."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg12248_main_local_maps_post import enclosing_method
from pg11054_api_request_context import original_match

SOURCE='f75d2fea05a98fe40d731d1a3046a64d20bbbb65'
PIN='4424f49ea3ed72c64cd7d2249c3759ae5012c0a36e7eca1bff9a87ddbee71ea8'
OUT=data.BASE/'PG12752-metric-context-context-post-v1'
EXPECTED={
 '021':['try(varexecutor=Executors.newSingleThreadExecutor())','active.get(30,TimeUnit.SECONDS)','release.countDown()','executor.shutdownNow()','executor.awaitTermination(30,TimeUnit.SECONDS)'],
 '023':['try(varexecutor=Executors.newSingleThreadExecutor())','List.of(true,false)','init.get(30,TimeUnit.SECONDS)','release.countDown()','executor.shutdownNow()','executor.awaitTermination(30,TimeUnit.SECONDS)'],
 '024':['try(varexecutor=Executors.newSingleThreadExecutor())','init.get(30,TimeUnit.SECONDS)','release.countDown()','executor.shutdownNow()','executor.awaitTermination(30,TimeUnit.SECONDS)'],
 '033':['try(varworker=Executors.newSingleThreadExecutor())','future.get(30,TimeUnit.SECONDS)','proceed.countDown()','worker.shutdownNow()','worker.awaitTermination(30,TimeUnit.SECONDS)','context.close()'],
 '032':['context.initialize()','context.render(true)','finally{context.close();}','assertTrue(observed.get().isClosed())']}


def main():
    invocation=capture(__file__);assert not OUT.exists()
    directory=data.BASE/'PG12750-metric-context-context-v1'
    manifest=data.read_checked(directory/'manifest.json',PIN)
    rows=data.read_checked(directory/'review.json',manifest['reviewSha256'])['rows']
    host=data.read_checked(data.BASE/'PG12744-metric-context-host-v1/manifest.json','c3c41d37e0ade8e22f6c50f2424fc1e6d6ecd67cc4f5c6e5346e94fa60d45381')
    static=data.read_checked(data.BASE/'PG12746-metric-context-static-v1/manifest.json','6ea3560962d32afd4d0921d7c81f2ef47f101c3c7aca7bca3f0c0ab38f6b9e75')
    raw=(data.BASE/'PG12746-metric-context-static-v1/pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),node) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for node in f if node.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    mapped={original_match(path,node,original,actual)['id']:(path,node) for path,node in actual}
    assert len(mapped)==len(rows)==len({row['id'] for row in rows})==38 and set(mapped)=={row['id'] for row in rows}
    def validate(row):
        if row.get('id') not in mapped:
            raise ValueError('known original current node required')
        path,node=mapped[row['id']];attributes=dict(node.attrib);method=attributes['method'];text=(data.ROOT/path).read_text()
        digest=data.sha(text.encode());assert digest==host['begin']['sourceInputHashes'][path]
        tokens=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
        lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(attributes['beginline'])-1]))+int(attributes['begincolumn'])-1;end=sum(map(len,lines[:int(attributes['endline'])-1]))+int(attributes['endcolumn'])
        point=next(i for i,(_,offset) in enumerate(tokens) if offset==start)
        lo,hi=enclosing_method(tokens,method,point)
        compact=''.join(value for value,_ in tokens[lo:hi+1]);whole=''.join(value for value,_ in tokens)
        role='api' if '/nk/api/' in path else 'web';title=role.title();prefix=role+'mctx'
        candidates=[case for case in host['begin']['cases'] if case['path']==path]
        owner_controls=[]
        if method=='Harness':
            assert attributes['rule']=='CloseResource' and attributes['variable']=='standardOwner'
            controls=['varstandardOwner=new'+title+'StandardMetricSource(this::standard,(registry,gc)->{});','context=new'+title+'MetricContext<T>','this::custom,standardOwner']
            owner_controls=['context.close();','if(!customRegistry.isClosed())customRegistry.close();','if(!standardRegistry.isClosed())standardRegistry.close();']
            assert all(value in whole for value in owner_controls)
            cases=[]
            for case in candidates:
                cp=next(i for i,(value,_) in enumerate(tokens) if value==case['method'] and tokens[i+1][0]=='(')
                ca,cb=enclosing_method(tokens,case['method'],cp)
                if 'newHarness<' in ''.join(value for value,_ in tokens[ca:cb+1]):
                    cases.append(case)
            assert len(cases)==23
            kind='UNBOUND_RESOURCE_FREE_OWNER_TRANSFERRED_TO_HARNESS_CONTEXT'
        elif method=='await':
            assert attributes['rule']=='DoNotUseThreads'
            controls=['latch.await(30,TimeUnit.SECONDS)','catch(InterruptedExceptioninterrupted)','Thread.currentThread().interrupt()']
            cases=[case for case in candidates if any(case['method'].startswith(prefix+suffix) for suffix in ['021','023','024','033'])]
            assert len(cases)==4
            kind='PRIVATE_BOUNDED_LATCH_AND_INTERRUPT_STATUS_RESTORE_NOT_J2EE'
        else:
            suffix=method[len(prefix):len(prefix)+3];assert suffix in EXPECTED
            controls=EXPECTED[suffix];cases=[case for case in candidates if case['method']==method]
            assert len(cases)==1
            kind='RESOURCE_FREE_CONTEXT_PUBLISHED_BEFORE_INIT_WITH_EXPLICIT_FINALLY_CLOSE' if suffix=='032' else 'OWNED_FINITE_STANDALONE_SDK_FIXTURE_WORKERS_NOT_J2EE'
        assert all(value in compact for value in controls)
        assert all(any(actual_case['classname']==case['className'] and actual_case['name']==case['method'] and not actual_case['nonPass'] for actual_case in host['cases']) for case in cases)
        identity=original_match(path,node,original,actual)
        expected=dict(path=path,rule=attributes['rule'],attributes=attributes,originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=digest,sourceSpanSha256=data.sha(text[start:end].encode()),scopeName=method,scopeKind='CONSTRUCTOR' if method=='Harness' else 'METHOD',scopeTokenSha256=data.sha('\0'.join(value for value,_ in tokens[lo:hi+1]).encode()),controls=controls,ownerControls=owner_controls,currentCases=cases,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0,newAccepted=0)
        if any(row.get(key)!=value for key,value in expected.items()) or not row.get('reason'):
            raise ValueError('exact current constructor/method/owner/control/current case basis required')
    for row in rows:
        validate(row)
    labels=[]
    for field,bad_value in [('id','foreign'),('source','0'*40),('sourceSha256','0'*64),('sourceSpanSha256','0'*64),('scopeName','foreign'),('scopeKind','UNKNOWN'),('scopeTokenSha256','0'*64),('controls',[]),('currentCases',[]),('kind','EXEMPT'),('disposition','SUPPRESSED'),('reason',''),('currentWholeJoinPending',False),('oldRuntimeReassigned',True),('productTestsExecutedByReview',1),('newAccepted',1)]:
        bad=copy.deepcopy(rows[0]);assert bad[field]!=bad_value;bad[field]=bad_value
        try:
            validate(bad)
        except ValueError:
            labels.append(field)
        else:
            raise AssertionError('wrong scope accepted')
    constructor=next(row for row in rows if row['scopeName']=='Harness')
    bad=copy.deepcopy(constructor);assert bad['ownerControls'];bad['ownerControls']=[]
    try:
        validate(bad)
    except ValueError:
        labels.append('constructor.ownerControls')
    else:
        raise AssertionError('dropped retained-owner cleanup accepted')
    def counts(value):
        if value.get('sourceContexts')!=38 or value.get('rawRetained')!=38 or value.get('wholeStaticScopeRaw')!=38 or value.get('historicalThreadSourceRebindings')!=34 or value.get('newOwnershipContexts')!=4 or value.get('sourceCorrections')!=0 or value.get('newAccepted')!=0:
            raise ValueError('no raw deletion or extra product credit')
    counts(manifest)
    for field,bad_value in [('sourceContexts',0),('rawRetained',0),('wholeStaticScopeRaw',0),('historicalThreadSourceRebindings',0),('newOwnershipContexts',38),('sourceCorrections',16),('newAccepted',1)]:
        bad=dict(manifest);assert bad[field]!=bad_value;bad[field]=bad_value
        try:
            counts(bad)
        except ValueError:
            labels.append('manifest.'+field)
        else:
            raise AssertionError('wrong context cardinality accepted')
    assert len(labels)==24 and host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==66
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=38,rawRetained=38,historicalThreadSourceRebindings=34,newOwnershipContexts=4,metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,productTestsExecuted=0,sourceCorrections=0,coverage=None,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
