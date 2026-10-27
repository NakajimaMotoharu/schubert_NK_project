"""Independent XML/current span/method/case reasons binding and eight metadata negative vectors."""
import copy
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match
from host_tool_invocation import capture,verify
SOURCE='5672593199b6b4e9cbfcc9bc01b26bdcda87a638'
OUT=data.BASE/'PG11963-jms-proxy-fixture-context-post-v1'
PIN='7cbf809203b90adaaecf34e04284f6c925070806ff2ddd2560de7ad436b82591'
def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG11961-jms-proxy-fixture-context-v1';m=data.read_checked(p/'manifest.json',PIN);rows=data.read_checked(p/'review.json',m['reviewSha256'])['rows'];host=data.read_checked(data.BASE/'PG11956-jms-proxy-fixture-host-v1/manifest.json','a1ef69cbd52dc7f8fbedbe2538a09ed341d122fb5496a2561f7caaa2445cbbd9');sp=data.BASE/'PG11958-jms-proxy-fixture-static-v1';st=data.read_checked(sp/'manifest.json','fec45644accf3140542a82a3b8189f4205796b7c5edbccbcca159ae0b84895f6');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'];actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');mapped={(p,tuple(sorted(n.attrib.items()))):original_match(p,n,original,actual) for p,n in actual}
    def validate(row):
        path=row['path'];a=row['attributes'];text=(data.ROOT/path).read_text();lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);lo,hi,name=min((v for v in functions(ts) if v[0]<=i<=v[1]),key=lambda v:v[1]-v[0]);ident=mapped[(path,tuple(sorted(a.items())))];cases=[c for c in host['begin']['cases'] if c['path']==path];expected=dict(id=ident['id'],originalRowSha256=ident['rowSha256'],rule=a['rule'],source=SOURCE,sourceSha256=host['begin']['sourceInputHashes'][path],sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[lo:hi+1]).encode()),currentCases=cases,disposition='REQUIRED_CONTRACT',newSourceReason=True,currentWholeJoinPending=True,oldRuntimeReassigned=False,productTestsExecutedByReview=0)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason'):raise ValueError('exact independent current finding/source/span/case required')
        compact=''.join(t for t,_ in ts[lo:hi+1]);assert data.sha(text.encode())==row['sourceSha256'] and host['source']==SOURCE and host['actualExit']==0 and len(cases)==6
        if a['rule']=='UseConcurrentHashMap':assert name in ('baseValues','validReply','with','without') and 'newHashMap<>' in compact and 'null' in {t for t,_ in ts}
        elif a['rule']=='UseProperClassLoader':assert name=='proxy' and 'type.getClassLoader()' in compact and 'newClass<?>[]{type}' in compact
        else:assert a['rule']=='CompareObjectsWithEquals' and name=='proxy' and 'returnignored==arguments[0];' in compact and 'System.identityHashCode(ignored)' in compact
        assert not {'Thread','Executors','ExecutorService'}&{t for t,_ in ts};assert all(any(v['classname']==c['className'] and v['name']==c['method'] and not v['nonPass'] for v in host['cases']) for c in cases)
    assert len(rows)==len(mapped)==len({r['id'] for r in rows})==10 and Counter(r['rule'] for r in rows)==Counter(UseConcurrentHashMap=6,UseProperClassLoader=2,CompareObjectsWithEquals=2)
    for row in rows:validate(row)
    negatives=0
    for field,value in [('source','0'*40),('oldRuntimeReassigned',True),('reason',''),('sourceSpanSha256','0'*64),('method','foreign'),('currentCases',[]),('disposition','SUPPRESSED'),('currentWholeJoinPending',False)]:
        bad=copy.deepcopy(rows[0]);bad[field]=value
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('bad current-context binding accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=10,newSourceReasons=10,metadataNegativeVectors=negatives,rawRetained=10,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
