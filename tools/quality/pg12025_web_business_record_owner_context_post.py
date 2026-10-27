"""Independent current2 XML/span/raw-token-method/case and eight metadata negatives."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='54e84fe04836dd88c3adfda5ac3f010eb591a7ee'
OUT=data.BASE/'PG12025-web-business-record-owner-context-post-v1'
PIN='4f6727e8ba7420a072ea01a4e7dd3a30b0782ac9b690810a2c3c2c87babcca13'

def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG12023-web-business-record-owner-context-v1';m=data.read_checked(p/'manifest.json',PIN);review=data.read_checked(p/'review.json',m['reviewSha256']);host=data.read_checked(data.BASE/'PG12018-web-business-record-host-v1/manifest.json','83e830344ae46b8097d1ca8027c34e7d2dc7fb3596206e9da2ffe3c0308a4048');sp=data.BASE/'PG12020-web-business-record-static-v1';st=data.read_checked(sp/'manifest.json','3bfc240dc4772cdaec9c574f9e0527fdab3d6ba89d28872161c2de5aaaf3ae3b');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256'];actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');mapped={(p,tuple(sorted(n.attrib.items()))):original_match(p,n,root,actual) for p,n in actual}
    def validate(row):
        path=row['path'];a=row['attributes'];text=(data.ROOT/path).read_text();lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);ma,mb,name=min((s for s in functions(ts) if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0]);compact=''.join(t for t,_ in ts[ma:mb+1]);case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name);identity=mapped[(path,tuple(sorted(a.items())))];expected=dict(id=identity['id'],originalRowSha256=identity['rowSha256'],rule='DoNotUseThreads',source=SOURCE,sourceSha256=host['begin']['sourceInputHashes'][path],sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),currentCase=case,kind='OWN_FINITE180_WIRE_CALLBACK_TASKS',disposition='CONTEXT_NOT_APPLICABLE',previousReferenceRetainedAsHistorical=True,newSourceReason=False,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason'):raise ValueError('exact current2 source/span/method/case/owner required')
        assert data.sha(text.encode())==expected['sourceSha256'] and host['source']==SOURCE and host['actualExit']==0 and name=='wire008ConcurrentFacadesKeepRepliesAndContextsSeparate' and 'try(varpool=Executors.newFixedThreadPool(8))' in compact and 'n<180' in compact and 'pool.submit(' in compact and 'task.get(10,TimeUnit.SECONDS)' in compact
        assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
    rows=review['rows'];assert len(rows)==len(mapped)==len({r['id'] for r in rows})==2
    for row in rows:validate(row)
    negatives=0
    for field,value in [('source','0'*40),('oldRuntimeReassigned',True),('reason',''),('sourceSpanSha256','0'*64),('method','foreign'),('currentCase',{}),('disposition','SUPPRESSED'),('currentWholeJoinPending',False)]:
        bad=copy.deepcopy(rows[0]);bad[field]=value;assert bad!=rows[0]
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('invalid current source metadata accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=2,existingThreadReferencesReauthenticated=2,newSourceReasons=0,metadataNegativeVectors=negatives,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
