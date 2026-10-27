"""Nine independent literal constants and two diagnostic read ordinals, no Main/oracle change."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg10840_web_view_duplicate_plan import transformed as strings

OUT=data.BASE/'PG11830-mq-media-collector-value-plan-v1'
FILES=['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/MqPressureMetricCollectorTest.java','src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/MediaStreamsMetricCollectorTest.java']
NAMES={'"nk.async.work"':'ASYNC_ADDRESS','"nk.web.log"':'LOG_ADDRESS','"nk_mq_queue_messages"':'QUEUE_MESSAGES','"DEBUG"':'DEBUG_MODE','"nk_media_streams"':'STREAMS_NAME','"media_type"':'MEDIA_LABEL','"AUDIO"':'AUDIO_TYPE','"VIDEO"':'VIDEO_TYPE'}

def inputs():
    normal=data.read_checked(data.BASE/'PG11804-job-outbox-value-literal-six-compile-v1/manifest.json','cfa574ea833d73ee31adfb96fba25fb5909890a2fb1fe32413049618b4ca58ea');assert normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');table={}
    for path in FILES:
        text=(snapshot/path).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][path];ts=list(LEX.finditer(text));rows=[]
        for row in root:
            if row['path']!=path or row['rule'] not in ('AvoidDuplicateLiterals','AvoidLiteralsInIfCondition'):continue
            assert row['inputSha256']==normal['begin']['inputHashes'][path];a=row['attributes'];lines=text.splitlines(keepends=True);point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
            if row['rule']=='AvoidDuplicateLiterals':
                m=next(m for m in ts if m.start()==point);literal=m.group();count=int(re.search(r' appears ([0-9]+) times',row['message'])[1]);assert literal in NAMES and sum(m.group()==literal for m in ts)==count
                rows.append(dict(id=row['id'],kind='STRING',literal=literal,name=NAMES[literal],references=count))
            else:
                # PMD spans the whole if; isolate its exact integer token, not every numeric fixture.
                target='1' if 'MqPressure' in path else '2';name='FIRST_READ_ORDINAL' if target=='1' else 'BLOCKED_READ_ORDINAL'
                line=lines[int(a['beginline'])-1];needle='if (call == '+target+')';assert needle in line
                start=sum(map(len,lines[:int(a['beginline'])-1]));offset=start+line.index(needle)+len('if (call == ');assert text[offset:offset+1]==target
                rows.append(dict(id=row['id'],kind='ORDER_INT',literal=target,name=name,references=1,point=offset))
        assert len(rows)==(5 if 'MqPressure' in path else 6);assert not any(m.group() in {r['name'] for r in rows} for m in ts);table[path]=rows
    assert sum(r['kind']=='STRING' for rows in table.values() for r in rows)==9
    return normal,snapshot,table

def transformed(text,stem,rows):
    row=next(r for r in rows if r['kind']=='ORDER_INT');i=row['point'];assert text[i:i+1]==row['literal'];result=text[:i]+row['name']+text[i+1:];result=strings(result,stem,[r for r in rows if r['kind']=='STRING']);header='class '+stem+' {\n';assert result.count(header)==1
    return result.replace(header,header+'  private static final int '+row['name']+' = '+row['literal']+';\n',1)

def emit():
    _,snapshot,table=inputs();patch='*** Begin Patch\n'
    for path,rows in table.items():
        before=(snapshot/path).read_text();assert (data.ROOT/path).read_text()==before;after=transformed(before,Path(path).stem,rows);patch+='*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,table=inputs();assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table);changes=[]
    for path,rows in table.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text();assert canonical(after)==canonical(transformed(before,Path(path).stem,rows));changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,stringConstants=9,stringReferences=sum(r['references'] for rows in table.values() for r in rows if r['kind']=='STRING'),orderConstants=2,comparisonReferences=2,originalMethods=16,rawDiagnosticCorrectionsExpected=11,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
