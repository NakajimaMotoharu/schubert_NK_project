"""Independent22 current spans/owners/cases and metadata negatives; no execution of reviewed Java."""
from collections import Counter
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg11054_api_request_context import original_match
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions

SOURCE='b4810698856cc2ae7edabb899a47aad34ef52cc2'
OUT=data.BASE/'PG11653-db-pool-binding-current-owner-context-post-v1'

def valid(row):
    worker=row['kind']=='REQUIRED_EXECUTOR_BOUNDED_STOP_FINALLY'
    if row['source']!=SOURCE or not row['reason'].strip() or not row['rawWarningRetained'] or not row['currentWholeJoinPending'] or row['oldRuntimeReassigned'] or row['productTestsExecutedByReview']!=0:
        raise ValueError('current explicit raw-retaining source reason without new execution required')
    if row['newDispositionCreated']!=worker or row['previousReferenceRetainedAsHistorical']==worker or row['disposition']!=('REQUIRED_CONTRACT' if worker else 'CONTEXT_NOT_APPLICABLE'):
        raise ValueError('two new bounded owner points versus20 existing thread contexts must be distinguished')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    cp=data.BASE/'PG11651-db-pool-binding-current-owner-context-v1';cm=data.read_checked(cp/'manifest.json','581e4415fdddde304b466767d4cebed8a249dd7c82f3a41158b804a5b1df316b');value=data.read_checked(cp/'review.json',cm['reviewSha256'])
    prior_path=data.BASE/'PG11629-db-pool-binding-thread-context-v1';prior=data.read_checked(prior_path/'manifest.json','4cd805b22bfd8bac876ccf0f4a1ea3f6d3377f13fc95c80f94e17dad43a73eb4');old={r['id']:r for r in data.read_checked(prior_path/'review.json',prior['reviewSha256'])['rows']}
    normal=data.read_checked(data.BASE/'PG11644-db-pool-binding-fatal-case-six-compile-v1/manifest.json','b6ab06836da09a0be7d6337e3c3d269b030afc06efc18352b9eb1034886b77b6')
    host=data.read_checked(data.BASE/'PG11646-db-pool-binding-fatal-case-host-v1/manifest.json','056a66e456e83ecdbcaffad464d50ce41d25955286457a364b188b92d43b687a');assert host['source']==normal['source']==SOURCE and host['actualExit']==normal['actualExit']==0 and host['observedTestExecutions']==30
    sp=data.BASE/'PG11648-db-pool-binding-fatal-case-static-v1';st=data.read_checked(sp/'manifest.json','acead561d795d044cc51826684268d6b2729f529fd86bd2bfa21688e887869c2');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==st['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    mapped={original_match(p,n,root,actual)['id']:(p,n) for p,n in actual};rows={r['id']:r for r in value['rows']};assert len(mapped)==len(rows)==22 and set(mapped)==set(rows)
    counts=Counter();worker=None
    for identity,row in rows.items():
        valid(row);path,node=mapped[identity];assert row['path']==path and row['attributes']==dict(node.attrib)
        text=(data.ROOT/path).read_text();assert data.sha(text.encode())==row['sourceSha256']==normal['begin']['inputHashes'][path]
        lines=text.splitlines(keepends=True);point=sum(map(len,lines[:int(node.get('beginline'))-1]))+int(node.get('begincolumn'))-1;end=sum(map(len,lines[:int(node.get('endline'))-1]))+int(node.get('endcolumn'))
        assert data.sha(text[point:end].encode())==row['sourceSpanSha256'];ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))];index=next(i for i,(_,pos) in enumerate(ts) if pos==point)
        ma,mb,name=min((s for s in functions(ts) if s[0]<=index<=s[1]),key=lambda s:s[1]-s[0]);assert name==row['method'] and data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode())==row['methodTokenSha256']
        compact=''.join(t for t,_ in ts);assert compact.count('Executors.newFixedThreadPool(2)')==1 and compact.count('workers.submit(')==2
        assert 'finally{release.countDown();workers.shutdownNow();assertTrue(workers.awaitTermination(30,TimeUnit.SECONDS));}' in compact
        assert 'first.get(30,TimeUnit.SECONDS);second.get(30,TimeUnit.SECONDS);' in compact and 'latch.await(30,TimeUnit.SECONDS)' in compact
        assert row['currentCase'] in host['begin']['cases'] and any(c['classname']==row['currentCase']['className'] and c['name']==row['currentCase']['method'] and not c['nonPass'] for c in host['cases'])
        if node.get('rule')=='CloseResource':
            assert identity not in old and row['kind']=='REQUIRED_EXECUTOR_BOUNDED_STOP_FINALLY' and name==row['currentCase']['method'];worker=row;counts['newOwnerPoint']+=1
        else:
            assert node.get('rule')=='DoNotUseThreads' and identity in old and row['methodTokenSha256']==old[identity]['methodTokenSha256'];counts['threadReauth']+=1
    assert counts==Counter(newOwnerPoint=2,threadReauth=20) and worker is not None
    for key,v in [('source','old'),('productTestsExecutedByReview',1),('reason',''),('rawWarningRetained',False),('currentWholeJoinPending',False),('newDispositionCreated',False),('previousReferenceRetainedAsHistorical',True),('disposition','CONTEXT_NOT_APPLICABLE')]:
        bad=copy.deepcopy(worker);bad[key]=v;assert bad!=worker
        try:valid(bad)
        except ValueError:pass
        else:raise AssertionError('wrong source/owner/ref/history/execution claim accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextManifestSha256=data.sha((cp/'manifest.json').read_bytes()),counts=dict(counts),metadataNegativeVectors=8,rawRetained=22,
        currentRuntimeReferencedNotReexecuted=30,productTestsExecuted=0,coverage=None,wholeF03Accepted=False,newAccepted=0,effortPercent=None,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
