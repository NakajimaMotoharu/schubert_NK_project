"""Ten same-value String fixtures and two second-registration markers, source-only."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg10840_web_view_duplicate_plan import transformed as strings

OUT=data.BASE/'PG11730-mq-recorder-literal-plan-v1'
FILES=[f'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/Mq{kind}MetricRecorderTest.java' for kind in ('Pressure','Redelivery')]
NAMES={'"nk.sync.request"':'SYNC_REQUEST_ADDRESS','"nk_mq_queue_messages"':'QUEUE_MESSAGES_METRIC','"queue"':'QUEUE_LABEL','"address"':'ADDRESS_LABEL','"DEBUG"':'DEBUG_MODE','"nk.async.work"':'ASYNC_WORK_ADDRESS','"nk_mq_redeliveries_total"':'REDELIVERY_METRIC','"delivery_count"':'DELIVERY_COUNT_LABEL'}
ORDER='FAILURE_REGISTRATION_ORDINAL'

def inputs():
    normal=data.read_checked(data.BASE/'PG11704-jvm-system-literal-six-compile-v1/manifest.json','e4715f0201f26ed2372db61d1c97e23c0c2b80fb6d7ff309053a74fb93e36e83');assert normal['source']=='eee3d32be87396f61f94e6013f4864330ceee4f3' and normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');table={}
    for path in FILES:
        text=(snapshot/path).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][path];ts=list(LEX.finditer(text));rows=[]
        for row in root:
            if row['path']!=path or row['rule']!='AvoidDuplicateLiterals':continue
            assert row['inputSha256']==normal['begin']['inputHashes'][path];a=row['attributes'];lines=text.splitlines(keepends=True);point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;m=next(m for m in ts if m.start()==point);literal=m.group();count=int(re.search(r' appears ([0-9]+) times',row['message'])[1]);assert literal in NAMES and sum(t.group()==literal for t in ts)==count
            rows.append(dict(id=row['id'],kind='STRING',literal=literal,name=NAMES[literal],references=count))
        needle='if (registrations.incrementAndGet() == 2';assert text.count(needle)==1;point=text.index(needle)+len(needle)-1;i=next(i for i,m in enumerate(ts) if m.start()==point);prefix=canonical('registrations.incrementAndGet()==');assert ts[i].group()=='2' and [m.group() for m in ts[i-len(prefix):i]]==prefix
        ids=[row['id'] for row in root if row['path']==path and row['rule']=='AvoidLiteralsInIfCondition'];assert len(ids)==(1 if 'Redelivery' in path else 0)
        rows.append(dict(id=ids[0] if ids else None,sourcePointId=Path(path).stem+'#secondRegistration',kind='ORDER_INT',literal='2',name=ORDER,references=1,point=point,diagnosticPresent=bool(ids)))
        assert len(rows)==6 and not any(m.group() in {r['name'] for r in rows} for m in ts);table[path]=rows
    assert sum(r['references'] for rows in table.values() for r in rows if r['kind']=='STRING')==57
    return normal,snapshot,table

def transformed(text,stem,rows):
    row=next(r for r in rows if r['kind']=='ORDER_INT');i=row['point'];assert text[i:i+1]=='2';result=text[:i]+ORDER+text[i+1:];result=strings(result,stem,[r for r in rows if r['kind']=='STRING']);header='class '+stem+' {\n';assert result.count(header)==1
    return result.replace(header,header+'  private static final int '+ORDER+' = 2;\n',1)

def emit():
    _,snapshot,table=inputs();patch='*** Begin Patch\n'
    for path,rows in table.items():
        before=(snapshot/path).read_text();assert (data.ROOT/path).read_text()==before;after=transformed(before,Path(path).stem,rows);patch+='*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,table=inputs();assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table);changes=[]
    for path,rows in table.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text();assert canonical(after)==canonical(transformed(before,Path(path).stem,rows));changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,stringConstants=10,stringReferences=57,orderConstants=2,comparisonReferences=2,originalMethods=16,rawDiagnosticCorrectionsExpected=11,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
