"""Thirteen fixture strings and one semantics-preserving operand increment extraction."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg10840_web_view_duplicate_plan import transformed as strings

OUT=data.BASE/'PG11760-jdbc-collector-literal-plan-v1'
FILES=[f'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/{kind}MetricCollectorTest.java' for kind in ('AsyncJob','Outbox')]
NAMES={'"RECEIVED"':'RECEIVED_STATE','"PROCESSING"':'PROCESSING_STATE','"COMPLETED"':'COMPLETED_STATE','"ERROR"':'ERROR_VALUE','"CANCELLED"':'CANCELLED_STATE','"state"':'STATE_LABEL','"DEBUG"':'DEBUG_MODE','"nk_outbox_rows"':'OUTBOX_ROWS_METRIC','"nk_outbox_oldest_seconds"':'OUTBOX_AGES_METRIC','"PENDING"':'PENDING_STATUS','"SENT"':'SENT_STATUS'}
ASSERT='assertEquals(++count, registry.get("nk_async_jobs").tag("state", state).gauge().value());'

def inputs():
    normal=data.read_checked(data.BASE/'PG11734-mq-recorder-literal-six-compile-v1/manifest.json','7d0f5f532b32896695e553c7ae886cdfef02595cbeb3c54c85c78b95b541505b');assert normal['source']=='6c96b262e88d9863ffb1e883780a249eaa11be27' and normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');table={}
    for path in FILES:
        text=(snapshot/path).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][path];ts=list(LEX.finditer(text));rows=[]
        for row in root:
            if row['path']!=path or row['rule']!='AvoidDuplicateLiterals':continue
            assert row['inputSha256']==normal['begin']['inputHashes'][path];a=row['attributes'];lines=text.splitlines(keepends=True);point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;m=next(m for m in ts if m.start()==point);literal=m.group();count=int(re.search(r' appears ([0-9]+) times',row['message'])[1]);assert literal in NAMES and sum(t.group()==literal for t in ts)==count
            rows.append(dict(id=row['id'],literal=literal,name=NAMES[literal],references=count))
        assert len(rows)==(7 if 'AsyncJob' in path else 6) and not any(m.group() in {r['name'] for r in rows} for m in ts);table[path]=rows
        assignment=[r for r in root if r['path']==path and r['rule']=='AssignmentInOperand'];assert len(assignment)==(1 if 'AsyncJob' in path else 0) and text.count(ASSERT)==len(assignment)
    assert sum(r['references'] for rows in table.values() for r in rows)==98
    return normal,snapshot,table

def transformed(text,stem,rows):
    if stem=='AsyncJobMetricCollectorTest':
        assert text.count(ASSERT)==1;text=text.replace(ASSERT,'{\n      ++count;\n      '+ASSERT.replace('++count','count',1)+'\n      }',1)
    return strings(text,stem,rows)

def emit():
    _,snapshot,table=inputs();patch='*** Begin Patch\n'
    for path,rows in table.items():
        before=(snapshot/path).read_text();assert (data.ROOT/path).read_text()==before;after=transformed(before,Path(path).stem,rows);patch+='*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,table=inputs();assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table);changes=[]
    for path,rows in table.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text();assert canonical(after)==canonical(transformed(before,Path(path).stem,rows));changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows,assignmentExtracted='AsyncJob' in path))
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,stringConstants=13,stringReferences=98,extractedPrefixAssignments=1,originalMethods=16,rawDiagnosticCorrectionsExpected=14,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
