"""All44 raw diagnostics,36 concrete contexts and six explicit new IDs; no warning suppression."""
import copy
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11054_api_request_context import original_match
from pg10398_role_view_preflight import canonical
from pg11312_batch_resource_ownership_review import method_tokens

SOURCE='495313cd8e724d5f1906fca64d9d9fd3516aae50'
OUT=data.BASE/'PG11451-gc-fake-guard-context-v1'
POST=data.BASE/'PG11453-gc-fake-guard-context-post-v1'
PRIMARY_SHA=None


def inputs():
    normal=data.read_checked(data.BASE/'PG11444-gc-fake-guard-six-compile-v1/manifest.json','0f5f38eb4fc41cde15284301f8b57b53c4f22743004411b71ece13a60ed1edfb')
    sp=data.BASE/'PG11448-gc-fake-guard-static-v1/manifest.json'
    static=data.read_checked(sp,'4540e528ae063a80dfcdfa454da340a397e0449f006ee7692e95d19e8d86e185')
    inverse=data.read_checked(data.BASE/'PG11442-gc-fake-guard-source-post-v1/manifest.json','ee7e93ea6dd4a8444f60778b1742d568e5f9767dae016bddd3604f9b065c8778')
    host=data.read_checked(data.BASE/'PG11446-gc-fake-guard-host-v1/manifest.json','c849836c6b0356430eaaf4426718bc8307bc1d8cd5581eb659cd776e8a529e74')
    assert normal['source']==static['source']==host['source']==SOURCE and normal['actualExit']==host['actualExit']==0 and host['observedTestExecutions']==48
    assert inverse['allOriginalOracleTokensRestored'] and inverse['metadataNegativeVectors']==63
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    raw=(sp.parent/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file'
        for n in f if n.tag.rpartition('}')[2]=='violation']
    assert len(actual)==44
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    return normal,original,actual


def discoveries(actual,hashes):
    selected=sorted(((p,n) for p,n in actual if re.fullmatch(r'(api|web|batch)gc01[56]\w*',n.get('method',''))),key=lambda item:(item[0],item[1].get('method')))
    assert len(selected)==6
    rows=[]
    for i,(path,node) in enumerate(selected,1):
        assert node.get('rule')=='CloseResource' and node.get('variable')=='resource'
        descriptor=dict(sourceDiscovered=SOURCE,path=path,rule=node.get('rule'),method=node.get('method'),variable='resource',message=''.join(node.itertext()).strip())
        rows.append(dict(id=f'PMD-NEW-PG11448-{i:03d}',path=path,rule=node.get('rule'),attributes=dict(node.attrib),sourceSha256=hashes[path],
            origin='NEW_SOURCE_DIAGNOSTIC_NOT_ORIGINAL_10690',rowSha256=data.sha(json.dumps(descriptor,sort_keys=True).encode()),descriptor=descriptor))
    return rows


def identity(path,node,original,actual,new):
    matches=[r for r in new if r['path']==path and r['attributes']==dict(node.attrib)]
    if matches:
        assert len(matches)==1
        return matches[0]
    return original_match(path,node,original,actual)


def basis(path,node):
    text=(data.ROOT/path).read_text();whole=''.join(canonical(text));method=node.get('method');rule=node.get('rule')
    if rule=='AvoidDuplicateLiterals':
        return None
    body=''.join(method_tokens(text,method))
    if rule=='DoNotUseThreads':
        assert re.fullmatch(r'(api|web|batch)gc013\w*',method)
        assert 'try(varworkers=Executors.newFixedThreadPool(4))' in body and 'i<64' in body and 'job.get(10,TimeUnit.SECONDS)' in body
        return dict(kind='FINITE_ORDINARY_JUNIT_OWN_CANDIDATE_SCOPES',workers=4,tasks=64,
            ownership='Each task owns Registry and immediate Fake finally; future10s/TWR/enclosingJVM240s, not J2EE/application worker lifecycle')
    assert rule=='CloseResource'
    variable=node.get('variable')
    if re.fullmatch(r'(api|web|batch)gc001\w*',method):
        assert variable=='resource' and 'finally{for(varresource:owned)resource.close();}' in body
        return dict(kind='RETAINED_ACKNOWLEDGED_OWN_JVM_GC_FINALLY_CLOSE_BEFORE_BORROWED_REGISTRY',ownership='Actual SDK handle retained before activation; same-Test finally closes all acknowledged handles, not an implicit installer close')
    if re.fullmatch(r'(api|web|batch)gc006\w*',method):
        assert variable=='source' and 'varsource=newRegistry();source.close();' in body
        return dict(kind='IMMEDIATELY_CLOSED_REGISTRY_NEGATIVE_FIXTURE',ownership='No operation between acquisition and explicit close; fixed closed DEBUG and STANDARD-no-read boundary, not a new resource acquisition')
    assert variable in ('resource','one','two')
    guard='finally{if(!'+variable+'.closeConfirmed)'+variable+'.close();}'
    assert guard in body
    assert 'publicvoidclose(){closeConfirmed=false;closeInvocations.incrementAndGet();onCloseCallback.run();closeConfirmed=true;}' in whole
    assert 'publicvoidbindTo(MeterRegistrysource){bindInvocations.incrementAndGet();onBindCallback.accept(source);}' in whole
    if re.fullmatch(r'(api|web|batch)gc01[56]\w*',method):
        assert 'assertTrue(resource.closeConfirmed);' in body
        kind='NEW_INDEPENDENT_LOGICAL_CLOSE_CONFIRMATION_AND_RETRY_ORACLE'
    else:
        assert any(re.fullmatch(r'(api|web|batch)gc'+number+r'\w*',method) for number in ('009','010','011','012','014'))
        assert 'var'+variable+'=newFake();try{' in body
        kind='CONDITIONAL_FINALLY_LOGICAL_FAKE_CLEANUP_WITH_CONFIRMED_CLOSE_STATE'
    return dict(kind=kind,ownership='Fake never activates SDK; flag cleared before attempt and set only after callback returns. Finally attempts unconfirmed cleanup, skips an already completed close. Raw PMD conditional-flow warning retained; not real SDK/worker termination proof')


def require(rows,original,hashes,actual,new):
    if len(rows)!=36 or len({r['id'] for r in rows})!=36:
        raise ValueError('all36 current concrete contexts including six new diagnostic IDs')
    for row in rows:
        node=next((n for p,n in actual if p==row['path'] and dict(n.attrib)==row['attributes']),None)
        if node is None or identity(row['path'],node,original,actual,new)['id']!=row['id']:
            raise ValueError('exact actual source warning and original/new diagnostic identity')
        if row['source']!=SOURCE or row['sourceSha256']!=hashes[row['path']] or row['basis']!=basis(row['path'],node):
            raise ValueError('exact source and concrete GC ownership/fixture state')
        origin='NEW_SOURCE_DIAGNOSTIC_NOT_ORIGINAL_10690' if any(n['id']==row['id'] for n in new) else 'ORIGINAL_10690_DIAGNOSTIC'
        if row['origin']!=origin or row['status']!='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING' or not row['rawWarningRetained'] or row['ptExecutionExempt']:
            raise ValueError('six new IDs cannot be reassigned to original IDs, suppressed or exempted')
        if row['productTestsExecuted']!=0 or row['coverage'] is not None or row['oldRuntimeReassigned']:
            raise ValueError('context is not extra PT/coverage/runtime')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    normal,original,actual=inputs();new=discoveries(actual,normal['begin']['inputHashes']);rows=[];unclassified=[]
    for path,node in actual:
        old=identity(path,node,original,actual,new);context=basis(path,node)
        if context is None:
            unclassified.append(old['id']);continue
        rows.append(dict(id=old['id'],path=path,source=SOURCE,sourceSha256=normal['begin']['inputHashes'][path],rule=node.get('rule'),
            attributes=dict(node.attrib),identityRowSha256=old['rowSha256'],basis=context,
            origin=old.get('origin','ORIGINAL_10690_DIAGNOSTIC'),status='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING',
            rawWarningRetained=True,ptExecutionExempt=False,productTestsExecuted=0,coverage=None,oldRuntimeReassigned=False))
    require(rows,original,normal['begin']['inputHashes'],actual,new)
    assert len(unclassified)==8
    verify(invocation);OUT.mkdir()
    data.write(OUT/'contexts.json',rows);data.write(OUT/'new-diagnostics.json',new)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        newDiagnosticsSha256=data.sha((OUT/'new-diagnostics.json').read_bytes()),newDiagnosticIds=[r['id'] for r in new],
        reviewed=36,oldDiagnostics=38,newDiagnostics=6,rawWarnings=44,rawStaticGate=1,unclassifiedOriginalIds=unclassified,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__)
    assert not POST.exists()
    primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA)
    rows=data.read_checked(OUT/'contexts.json',primary['contextsSha256']);new=data.read_checked(OUT/'new-diagnostics.json',primary['newDiagnosticsSha256'])
    normal,original,actual=inputs()
    assert new==discoveries(actual,normal['begin']['inputHashes'])
    require(rows,original,normal['begin']['inputHashes'],actual,new)
    bads=[rows[:-1],rows+[rows[0]]]
    for key,value in [('source','old'),('sourceSha256','0'*64),('status','PASS'),('rawWarningRetained',False),('ptExecutionExempt',True),('productTestsExecuted',48),('coverage',100),('oldRuntimeReassigned',True)]:
        bad=copy.deepcopy(rows);bad[0][key]=value;bads.append(bad)
    bad=copy.deepcopy(rows)
    index=next(i for i,r in enumerate(bad) if r['origin']=='NEW_SOURCE_DIAGNOSTIC_NOT_ORIGINAL_10690')
    bad[index]['origin']='ORIGINAL_10690_DIAGNOSTIC';bads.append(bad)
    bad=copy.deepcopy(rows);bad[index]['id']='PMD-00001';bads.append(bad)
    for bad in bads:
        try:
            require(bad,original,normal['begin']['inputHashes'],actual,new)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid/suppressed/reassigned current diagnostic accepted')
    verify(invocation);POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,
        contextsSha256=primary['contextsSha256'],newDiagnosticsSha256=primary['newDiagnosticsSha256'],metadataNegativeVectors=len(bads),
        reviewed=36,unclassified=8,oldDiagnostics=38,newDiagnostics=6,rawStaticGate=1,productTestsExecuted=0,coverage=None,
        wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
