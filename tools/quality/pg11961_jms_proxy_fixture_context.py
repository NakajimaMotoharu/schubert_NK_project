"""Ten current JMS fixture null-map/defining-loader/proxy-identity contexts, raw retained."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
from host_tool_invocation import capture,verify
SOURCE='5672593199b6b4e9cbfcc9bc01b26bdcda87a638'
OUT=data.BASE/'PG11961-jms-proxy-fixture-context-v1'
REASONS={
 'UseConcurrentHashMap':'Each baseValues/validReply/with/without creates a fresh caller-owned HashMap or copy. Missing and explicit null body/header/replyTo values are required negative fixtures. Proxy reads synchronously, no worker shares the map; ConcurrentHashMap rejects null before the SUT and alters this oracle. Not a production shared map.',
 'UseProperClassLoader':'Proxy defines exactly the caller-supplied BytesMessage/TextMessage interface and uses that same interface defining loader. It does not resolve context-selected services, J2EE lookup, arbitrary class names or network resources. Changing to unrelated context loader may not expose the interface identity; this is a finite local fixture, not container integration.',
 'CompareObjectsWithEquals':'The invocation handler implements the proxy equals(Object) method. ignored is that exact proxy instance, so identity implements reflexive reference equality. Calling ignored.equals would reenter this handler recursively, not compare field values; identityHashCode is paired with reference equality. No business object value equality is changed.'}
def review():
    host=data.read_checked(data.BASE/'PG11956-jms-proxy-fixture-host-v1/manifest.json','a1ef69cbd52dc7f8fbedbe2538a09ed341d122fb5496a2561f7caaa2445cbbd9');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==12
    p=data.BASE/'PG11958-jms-proxy-fixture-static-v1';m=data.read_checked(p/'manifest.json','fec45644accf3140542a82a3b8189f4205796b7c5edbccbcca159ae0b84895f6');raw=(p/'pmd.xml').read_bytes();assert data.sha(raw)==m['reports']['pmd']['sha256'];actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];assert len(actual)==10
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,n in actual:
        ident=original_match(path,n,original,actual);text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path];a=dict(n.attrib);lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi,name=min((v for v in functions(ts) if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);body=''.join(t for t,_ in ts[lo:hi+1]);full=''.join(t for t,_ in ts);rule=a['rule'];assert rule in REASONS
        if rule=='UseConcurrentHashMap':assert name in ('baseValues','validReply','with','without') and 'newHashMap<>' in body and ('.put(REPLY_TO_FIELD,null)' in full or '.put("replyTo",null)' in full)
        elif rule=='UseProperClassLoader':assert name=='proxy' and 'type.getClassLoader()' in body and 'newClass<?>[]{type}' in body
        else:assert name=='proxy' and 'returnignored==arguments[0];' in body and 'System.identityHashCode(ignored)' in body
        assert not {'Thread','Executors','ExecutorService'}&{t for t,_ in ts};cases=[c for c in host['begin']['cases'] if c['path']==path];assert len(cases)==6 and all(any(v['classname']==c['className'] and v['name']==c['method'] and not v['nonPass'] for v in host['cases']) for c in cases)
        rows.append(dict(id=ident['id'],originalRowSha256=ident['rowSha256'],path=path,rule=rule,attributes=a,source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),currentCases=cases,reason=REASONS[rule],disposition='REQUIRED_CONTRACT',newSourceReason=True,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0))
    return rows

def main():
    invocation=capture(__file__);assert not OUT.exists();rows=review();assert len({r['id'] for r in rows})==10;verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=10,newSourceReasons=10,rawRetained=10,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
