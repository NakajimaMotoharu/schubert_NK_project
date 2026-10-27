"""Independent current12 XML/span/method/case/strict proxy facts and eight metadata negatives."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions

SOURCE='21daf2722f9b280ec005b1b971300774a1d3716f'
OUT=data.BASE/'PG11773-jdbc-collector-owner-context-post-v1'
PIN='64a2ab92fd7052a20b648757f326d1fdacc6d42bdc9c930d314b492a379abef1'

def main():
    invocation=capture(__file__);assert not OUT.exists();cp=data.BASE/'PG11771-jdbc-collector-owner-context-v1';m=data.read_checked(cp/'manifest.json',PIN);review=data.read_checked(cp/'review.json',m['reviewSha256'])
    host=data.read_checked(data.BASE/'PG11766-jdbc-collector-literal-host-v1/manifest.json','d5565981b616135c0d08d6cc686245143ad405c89c0cb020ba834101bba2ed0d');sp=data.BASE/'PG11768-jdbc-collector-literal-static-v1';st=data.read_checked(sp/'manifest.json','1fb16cae2dcaf613917f2a8bd4abce746130911ecf3525ab45b66c00748b3c68');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'];actual={(str(Path(f.get('name')).relative_to(data.ROOT)),tuple(sorted(n.attrib.items()))) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'}
    closure=host['begin']['eligibilityClosureSourceHashes'];assert len(closure)==9 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in closure.items())
    def validate(row):
        path=row['path'];a=row['attributes'];text=(data.ROOT/path).read_text();lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);ma,mb,name=min((s for s in functions(ts) if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0]);compact=''.join(t for t,_ in ts[ma:mb+1]);loader=a['rule']=='UseProperClassLoader';prefix='asyncConn' if 'AsyncJob' in path else 'outboxConn'
        method=next(c['method'] for c in host['begin']['cases'] if c['path']==path and c['method'].startswith(prefix+'006')) if loader else name;case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==method)
        kind='DECLARING_JDBC_INTERFACE_LOADER' if loader else ('OWN_GATED_TWO_TASKS' if name.startswith(prefix+'006') else 'OWN_FINITE64_READS')
        expected=dict(source=SOURCE,sourceSha256=host['begin']['sourceInputHashes'][path],sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),currentCase=case,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',previousReferenceRetainedAsHistorical=True,newSourceReason=False,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason') or (path,tuple(sorted(a.items()))) not in actual:raise ValueError('exact current standalone JDBC fixture source/case/owner contract required')
        assert data.sha(text.encode())==expected['sourceSha256'] and host['source']==SOURCE and host['actualExit']==0
        if loader:
            assert name=='gate' and 'Proxy.newProxyInstance(Connection.class.getClassLoader(),newClass<?>[]{Connection.class},' in compact and 'release.await(5,TimeUnit.SECONDS)' in compact
        elif kind=='OWN_GATED_TWO_TASKS':
            assert 'Executors.newFixedThreadPool(2)' in compact and compact.count('pool.submit(')==2 and 'finally{release.countDown();}' in compact and 'one.get(5,TimeUnit.SECONDS)' in compact and 'two.get(5,TimeUnit.SECONDS)' in compact
        else:
            assert name.startswith(prefix+'007') and 'Executors.newFixedThreadPool(8)' in compact and 'pool.invokeAll(tasks)' in compact and ('owner<64' if 'AsyncJob' in path else 'owner<=64') in compact
        assert any(c['classname']==case['className'] and c['name']==method and not c['nonPass'] for c in host['cases'])
    rows=review['rows'];assert len(rows)==len(actual)==len({r['id'] for r in rows})==12 and sum(r['rule']=='UseProperClassLoader' for r in rows)==2 and all(not r['newSourceReason'] for r in rows)
    for row in rows:validate(row)
    first=rows[0];negatives=0
    for field,value in [('source','0'*40),('oldRuntimeReassigned',True),('reason',''),('sourceSpanSha256','0'*64),('method','foreign'),('currentCase',{}),('disposition','SUPPRESSED'),('currentWholeJoinPending',False)]:
        bad=copy.deepcopy(first);bad[field]=value;assert bad!=first
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('invalid current fixture metadata accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=12,existingThreadReferencesReauthenticated=10,existingLoaderReferencesReauthenticated=2,newSourceReasons=0,metadataNegativeVectors=negatives,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
