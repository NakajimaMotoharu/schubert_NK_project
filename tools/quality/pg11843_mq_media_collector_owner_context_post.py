"""Independent current20 XML/span/method/case/owner checks; nine unequal metadata negatives."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='69d50093df9e655a39eadcd7a392646ff65bfbb0'
OUT=data.BASE/'PG11843-mq-media-collector-owner-context-post-v1'
PIN='a86573a6cd91408d192bf148f327295e306f5a07821518ac2b2fcccb759fa54e'

def main():
    invocation=capture(__file__);assert not OUT.exists();cp=data.BASE/'PG11841-mq-media-collector-owner-context-v1';m=data.read_checked(cp/'manifest.json',PIN);review=data.read_checked(cp/'review.json',m['reviewSha256'])
    host=data.read_checked(data.BASE/'PG11836-mq-media-collector-value-host-v1/manifest.json','e2911e57d15ba6dc00b7e68ffe075b4f2edb2e05e9ffadf3e2d4e72cd281016d')
    sp=data.BASE/'PG11838-mq-media-collector-value-static-v1';st=data.read_checked(sp/'manifest.json','1c5b7a45fd5c3a1b3b3d4ab49355213784cdd36d4cb5068da46eaaeeb67d45ab');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');mapped={(p,tuple(sorted(n.attrib.items()))):original_match(p,n,root,actual) for p,n in actual}
    def validate(row):
        path=row['path'];a=row['attributes'];text=(data.ROOT/path).read_text();lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn'])
        ts=[(t.group(),t.start()) for t in LEX.finditer(text) if not t.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);ma,mb,name=min((s for s in functions(ts) if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0]);compact=''.join(t for t,_ in ts[ma:mb+1]);prefix='mqConn' if 'MqPressure' in path else 'mediaConn'
        serial='006' if name=='await' or name.startswith(prefix+'006') else '007';case=next(c for c in host['begin']['cases'] if c['path']==path and c['method'].startswith(prefix+serial));identity=mapped[(path,tuple(sorted(a.items())))];kind='FINITE_LATCH_AND_RESTORED_INTERRUPT' if name=='await' else 'OWN_TWO_WORKER_BLOCKED_PUBLICATION' if serial=='006' else 'OWN_FINITE64_SUPPLIED_VALUE_TASKS'
        expected=dict(id=identity['id'],originalRowSha256=identity['rowSha256'],rule='DoNotUseThreads',source=SOURCE,sourceSha256=host['begin']['sourceInputHashes'][path],sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),currentCase=case,kind=kind,disposition='CONTEXT_NOT_APPLICABLE',previousReferenceRetainedAsHistorical=True,newSourceReason=False,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False)
        if any(row.get(k)!=v for k,v in expected.items()) or not row.get('reason'):raise ValueError('exact current source/case/span/owner contract required')
        assert data.sha(text.encode())==expected['sourceSha256'] and host['source']==SOURCE and host['actualExit']==0
        if name=='await':assert '.await(5,TimeUnit.SECONDS)' in compact and 'Thread.currentThread().interrupt()' in compact
        elif serial=='006':assert name==case['method'] and 'Executors.newFixedThreadPool(2)' in compact and 'Thread.State.BLOCKED' in compact and 'TimeUnit.SECONDS.toNanos(5)' in compact and 'finally{release.countDown();}' in compact and '.get(5,TimeUnit.SECONDS)' in compact
        else:assert name==case['method'] and 'Executors.newFixedThreadPool(8)' in compact and ('i<64' in compact or 'index<64' in compact) and 'executor.invokeAll(tasks)' in compact and '.get(5,TimeUnit.SECONDS)' in compact
        assert any(c['classname']==case['className'] and c['name']==case['method'] and not c['nonPass'] for c in host['cases'])
    rows=review['rows'];assert len(rows)==len(mapped)==len({r['id'] for r in rows})==20
    for row in rows:validate(row)
    first=rows[0];negatives=0
    for field,value in [('source','0'*40),('oldRuntimeReassigned',True),('reason',''),('sourceSpanSha256','0'*64),('method','foreign'),('currentCase',{}),('kind','APPLICATION_WORKER'),('disposition','SUPPRESSED'),('currentWholeJoinPending',False)]:
        bad=copy.deepcopy(first);bad[field]=value;assert bad!=first
        try:validate(bad)
        except ValueError:negatives+=1
        else:raise AssertionError('invalid source contract metadata accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=20,existingThreadReferencesReauthenticated=20,newSourceReasons=0,metadataNegativeVectors=negatives,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
