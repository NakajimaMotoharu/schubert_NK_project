"""All54 concrete source ownership contexts, including two new diagnostics; raw retained, not PT exemption."""
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

SOURCE='7f035ccfe89c46e8f4fae52099b1c0e4e890e66b'
OUT=data.BASE/'PG11543-memory-http-guard-context-v1'
POST=data.BASE/'PG11545-memory-http-guard-context-post-v1'
PRIMARY_SHA=None

def inputs():
    normal=data.read_checked(data.BASE/'PG11536-memory-http-guard-six-compile-v1/manifest.json','038ace9c4a7187703381af22f7ecb5680f7b5d3adb2a07a242c579ca36019936')
    sp=data.BASE/'PG11540-memory-http-guard-static-v1/manifest.json';static=data.read_checked(sp,'b853cc3070e3a836a251a2118fdeb8ef038680be336e929fde1b604fb385314b')
    inverse=data.read_checked(data.BASE/'PG11534-memory-http-guard-source-post-v2/manifest.json','3ef570ac261440a23dad39b11e8bdd324ffa21968426253fbb936bc46f100c32')
    host=data.read_checked(data.BASE/'PG11538-memory-http-guard-host-v1/manifest.json','793e7131b39cb23b41c29a3342a9695504ec9cd1c526a0ee758b813ab20b9216')
    assert normal['source']==static['source']==host['source']==SOURCE and normal['actualExit']==host['actualExit']==0 and host['observedTestExecutions']==46
    assert inverse['allOriginalOracleTokensRestored'] and inverse['metadataNegativeVectors']==104
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    raw=(sp.parent/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    assert len(actual)==54 and all(n.get('rule')=='CloseResource' for _,n in actual)
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    return normal,original,actual

def discoveries(actual,hashes):
    selected=sorted(((p,n) for p,n in actual if re.fullmatch(r'(api|web)mhttp023\w*',n.get('method',''))),key=lambda item:(item[0],item[1].get('method')))
    assert len(selected)==2;rows=[]
    for index,(path,node) in enumerate(selected,1):
        assert node.get('variable')=='exchange'
        descriptor=dict(sourceDiscovered=SOURCE,path=path,rule=node.get('rule'),method=node.get('method'),variable='exchange',message=''.join(node.itertext()).strip())
        rows.append(dict(id=f'PMD-NEW-PG11540-{index:03d}',path=path,rule=node.get('rule'),attributes=dict(node.attrib),sourceSha256=hashes[path],
            origin='NEW_SOURCE_DIAGNOSTIC_NOT_ORIGINAL_10690',descriptor=descriptor,rowSha256=data.sha(json.dumps(descriptor,sort_keys=True).encode())))
    return rows

def identity(path,node,original,actual,new):
    matches=[r for r in new if r['path']==path and r['attributes']==dict(node.attrib)]
    if matches:
        assert len(matches)==1
        return matches[0]
    return original_match(path,node,original,actual)

def basis(path,node):
    text=(data.ROOT/path).read_text();whole=''.join(canonical(text));method=node.get('method');variable=node.get('variable')
    body=''.join(method_tokens(text,method))
    if variable=='context':
        assert method.endswith('mhttp009') and 'varcontext=standard();context.close();' in body
        return dict(kind='IMMEDIATELY_CLOSED_CONTEXT_CURRENT_WHOLE_PENDING',ownership='Closed context negative fixture before assertions/setup; no new SDK activation')
    assert variable in ('exchange','first','second','missing')
    assert re.search(r'var'+variable+r'=newExchange\([^;]*\);try\{',body)
    assert 'finally{if(!'+variable+'.closed)'+variable+'.close();}' in body
    assert 'publicvoidclose(){closed=true;closeCalls++;}' in whole
    assert 'privateExchange(Stringmethod,Stringpath){this.method=method;this.uri=URI.create(path);}' in whole
    if re.fullmatch(r'(api|web)mhttp023\w*',method):
        assert 'assertSame(failure,assertThrows(AssertionError.class,()->{try{throwfailure;}finally{if(!exchange.closed)exchange.close();}}));' in body
        assert body.count('assertEquals(1,exchange.closeCalls);')==2 and 'assertTrue(exchange.closed);' in body
        kind='NEW_INDEPENDENT_CALLER_FAILURE_CLEANUP_AND_COMPLETED_CLOSE_SKIP_ORACLE'
    else:
        kind='IMMEDIATE_LOGICAL_MEMORY_EXCHANGE_FINALLY_GUARD'
    return dict(kind=kind,ownership='Caller guards fresh memory Exchange until Main.handle or explicit caller close sets closed. Conditional finally preserves original close-count and borrowed-write non-close assertions; URI/byte streams only, not real socket/SDK/OS termination proof')

def require(rows,normal,original,actual,new):
    if len(rows)!=54 or len({r['id'] for r in rows})!=54:
        raise ValueError('all54 exact distinct current diagnostics')
    for row in rows:
        node=next((n for p,n in actual if p==row['path'] and dict(n.attrib)==row['attributes']),None)
        if node is None or identity(row['path'],node,original,actual,new)['id']!=row['id']:
            raise ValueError('exact actual warning/original or new diagnostic identity')
        if row['source']!=SOURCE or row['sourceSha256']!=normal['begin']['inputHashes'][row['path']] or row['basis']!=basis(row['path'],node):
            raise ValueError('exact current source/variable and concrete ownership context')
        origin='NEW_SOURCE_DIAGNOSTIC_NOT_ORIGINAL_10690' if any(r['id']==row['id'] for r in new) else 'ORIGINAL_10690_DIAGNOSTIC'
        if row['origin']!=origin or row['status']!='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING' or not row['rawWarningRetained'] or row['ptExecutionExempt']:
            raise ValueError('no reassignment, suppression, exemption or whole acceptance')
        if row['productTestsExecuted']!=0 or row['coverage'] is not None or row['oldRuntimeReassigned']:
            raise ValueError('context is not added PT/coverage/runtime')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    normal,original,actual=inputs();new=discoveries(actual,normal['begin']['inputHashes']);rows=[]
    for path,node in actual:
        old=identity(path,node,original,actual,new)
        rows.append(dict(id=old['id'],path=path,source=SOURCE,sourceSha256=normal['begin']['inputHashes'][path],attributes=dict(node.attrib),identityRowSha256=old['rowSha256'],
            origin=old.get('origin','ORIGINAL_10690_DIAGNOSTIC'),basis=basis(path,node),status='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING',rawWarningRetained=True,
            ptExecutionExempt=False,productTestsExecuted=0,coverage=None,oldRuntimeReassigned=False))
    require(rows,normal,original,actual,new)
    verify(invocation);OUT.mkdir();data.write(OUT/'contexts.json',rows);data.write(OUT/'new-diagnostics.json',new)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),newDiagnosticsSha256=data.sha((OUT/'new-diagnostics.json').read_bytes()),
        newDiagnosticIds=[r['id'] for r in new],reviewed=54,unclassifiedOriginalIds=[],oldDiagnostics=52,newDiagnostics=2,rawWarnings=54,rawStaticGate=1,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

def post():
    invocation=capture(__file__);assert not POST.exists()
    primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA);rows=data.read_checked(OUT/'contexts.json',primary['contextsSha256']);new=data.read_checked(OUT/'new-diagnostics.json',primary['newDiagnosticsSha256'])
    normal,original,actual=inputs();assert new==discoveries(actual,normal['begin']['inputHashes']);require(rows,normal,original,actual,new)
    bads=[rows[:-1],rows+[rows[0]]]
    for key,value in [('source','old'),('sourceSha256','0'*64),('status','PASS'),('rawWarningRetained',False),('ptExecutionExempt',True),('productTestsExecuted',46),('coverage',100),('oldRuntimeReassigned',True)]:
        bad=copy.deepcopy(rows);bad[0][key]=value;bads.append(bad)
    index=next(i for i,r in enumerate(rows) if r['id'].startswith('PMD-NEW-'))
    bad=copy.deepcopy(rows);bad[index]['id']='PMD-00001';bads.append(bad)
    bad=copy.deepcopy(rows);bad[index]['origin']='ORIGINAL_10690_DIAGNOSTIC';bads.append(bad)
    for bad in bads:
        try:
            require(bad,normal,original,actual,new)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid source/diagnostic/runtime context accepted')
    verify(invocation);POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,contextsSha256=primary['contextsSha256'],newDiagnosticsSha256=primary['newDiagnosticsSha256'],
        metadataNegativeVectors=len(bads),reviewed=54,unclassified=0,oldDiagnostics=52,newDiagnostics=2,rawStaticGate=1,productTestsExecuted=0,coverage=None,
        wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
