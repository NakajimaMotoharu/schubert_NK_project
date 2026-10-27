"""Two current finite100 JSON fixture thread references reauthenticated, raw retained."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from pg11054_api_request_context import original_match

SOURCE='264dc69591876147d76c19082cb69658cfe03dd8'
OUT=data.BASE/'PG11901-session-json-owner-context-v1'

def review():
    host=data.read_checked(data.BASE/'PG11896-session-json-fixture-host-v1/manifest.json','16c268b9a665056032da2b0a69fb3001692e88812022ef13c24f30fdce057e39');assert host['source']==SOURCE and host['actualExit']==0 and host['observedTestExecutions']==12
    sp=data.BASE/'PG11898-session-json-fixture-static-v1';m=data.read_checked(sp/'manifest.json','edf4a68b01e404ff0b728a50b8520e1d0fdbdf40417333f61519e241ecfec488');raw=(sp/'pmd.xml').read_bytes();assert data.sha(raw)==m['reports']['pmd']['sha256'] and m['actualExit']==1
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation'];root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[]
    for path,node in actual:
        identity=original_match(path,node,root,actual);text=(data.ROOT/path).read_text();assert data.sha(text.encode())==host['begin']['sourceInputHashes'][path];a=node.attrib;assert a['rule']=='DoNotUseThreads';lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;end=sum(map(len,lines[:int(a['endline'])-1]))+int(a['endcolumn']);ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))];i=next(i for i,(_,p) in enumerate(ts) if p==start);ma,mb,name=min((s for s in functions(ts) if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0]);compact=''.join(t for t,_ in ts[ma:mb+1]);assert name=='web015ConcurrentAttributesHaveNoCrossSessionState' and 'try(varpool=Executors.newFixedThreadPool(10))' in compact and 'i<100' in compact and 'pool.submit(' in compact and 'future.get(20,TimeUnit.SECONDS)' in compact
        case=next(c for c in host['begin']['cases'] if c['path']==path and c['method']==name);assert any(c['classname']==case['className'] and c['name']==name and not c['nonPass'] for c in host['cases'])
        rows.append(dict(id=identity['id'],path=path,rule=a['rule'],attributes=dict(a),originalRowSha256=identity['rowSha256'],source=SOURCE,sourceSha256=data.sha(text.encode()),sourceSpanSha256=data.sha(text[start:end].encode()),method=name,methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[ma:mb+1]).encode()),currentCase=case,kind='OWN_FINITE100_JSON_VALUE_TASKS',disposition='CONTEXT_NOT_APPLICABLE',reason='The J2EE application-thread rule does not apply to this dedicated JavaSE JUnit fixture. Ten own TWR workers execute exactly100 finite strict JSON encode/decode and independent literal/value comparisons, with20-second Future bounds. Inputs are synthetic immutable session snapshots; no authentication action, key, persistence or network is used. This measures these current inputs/schedules, not all production schedules or service ownership.',previousReferenceRetainedAsHistorical=True,newSourceReason=False,currentWholeJoinPending=True,productTestsExecutedByReview=0,oldRuntimeReassigned=False))
    assert len(rows)==len({r['id'] for r in rows})==2
    return rows

def main():
    invocation=capture(__file__);assert not OUT.exists();rows=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',dict(source=SOURCE,rows=rows));data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=2,existingThreadReferencesReauthenticated=2,newSourceReasons=0,rawRetained=2,productTestsExecuted=0,wholeF03Accepted=False,newAccepted=0,coverage=None,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
