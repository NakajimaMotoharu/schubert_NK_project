"""One required null-capable independent attribute Map fixture; raw remains pending whole F03."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='fd113e37b0783ae86d50696c9d3844e80b258d8a'
OUT=data.BASE/'PG11931-storage-attribute-map-context-v1'

def review():
    host=data.read_checked(data.BASE/'PG11926-storage-attribute-fixture-host-v1/manifest.json','e90717c76ced572401417d0a4515c79d5c82fb2cbbe3bd445bdc55f8cac1aa01');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==7
    sp=data.BASE/'PG11928-storage-attribute-fixture-static-v1';st=data.read_checked(sp/'manifest.json','1518ae6f87ba5342038fb964354e8f0ab34525ba2e76af5fabbb88a969f4933d');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'] and st['actualExit']==1;actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];assert len(actual)==1
    root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');path,node=actual[0];identity=original_match(path,node,root,actual);text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path];a=node.attrib;assert a['rule']=='UseConcurrentHashMap';lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);ma,mb,name=min((s for s in functions(ts) if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0]);compact=''.join(t for t,_ in ts[ma:mb+1]);assert name=='directory' and 'newHashMap<>()' in compact and 'returnresult;' in compact
    expected='a02DirectoryTypePermissionsOwnershipAndMissingAttributesFailClosed';case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==expected);assert 'missing.put(name,null);' in ''.join(t for t,_ in ts) and 'attrs.put(SIZE_FIELD,null);' in ''.join(t for t,_ in ts);assert any(c['classname']==case['className'] and c['name']==expected and not c['nonPass'] for c in host['cases'])
    return [dict(id=identity['id'],path=path,rule=a['rule'],attributes=dict(a),originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),currentCase=case,kind='REQUIRED_FRESH_NULL_CAPABLE_ATTRIBUTE_FIXTURE',disposition='REQUIRED_CONTRACT',reason='directory() allocates a fresh caller-owned HashMap for each independent attribute fixture. Tests deliberately put null and malformed typed values into it, then require StorageAttributeGuard to reject those values; ConcurrentHashMap would reject fixture construction instead and weaken the boundary oracle. The launcher fixes JUnit parallel execution false, the guard retains no map and this test has no workers or concurrent map access. This is not a production shared mutable map or runtime concurrency qualification.',previousReferenceRetainedAsHistorical=False,newSourceReason=True,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False)]

def main():
    invocation=capture(__file__);assert not OUT.exists();rows=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=1,newSourceReasons=1,existingReferencesReauthenticated=0,rawRetained=1,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
