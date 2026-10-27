"""Sixteen exact same-value typed fixture constants; no Main or independent-oracle changes."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10840_web_view_duplicate_plan import transformed

OUT=data.BASE/'PG12348-pool-capacity-plan-v1'
NORMAL='96605de485f83a38656ca3d0f479f679f708193d263671784582acb088d4b88b'
FILES=['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/DbPoolMetricObservationTest.java','src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebDbPoolMetricObservationTest.java','src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OperationMismatchMetricRecorderTest.java','src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/storage/TransferCapacityTest.java']
COUNTS=dict(DbPoolMetricObservationTest=8,WebDbPoolMetricObservationTest=8,OperationMismatchMetricRecorderTest=8,TransferCapacityTest=5)
NAMES={'"active"':'ACTIVE_GETTER_POINT','"QDLREQ01"':'DELETE_QUESTION_OPERATION','"DEBUG"':'DEBUG_MONITORING_MODE','"CRITICAL"':'CRITICAL_CAPACITY_LEVEL'}
NUMBERS={
 'PMD-02129':('int','FAULT_IDLE_INDEX','1'), 'PMD-02130':('int','FAULT_PENDING_INDEX','2'),
 'PMD-02131':('int','FAULT_NEGATIVE_MAXIMUM_INDEX','3'), 'PMD-02132':('int','FAULT_ZERO_MAXIMUM_INDEX','4'),
 'PMD-08339':('int','FAULT_IDLE_INDEX','1'), 'PMD-08340':('int','FAULT_PENDING_INDEX','2'),
 'PMD-08341':('int','FAULT_NEGATIVE_MAXIMUM_INDEX','3'), 'PMD-08342':('int','FAULT_ZERO_MAXIMUM_INDEX','4'),
 'PMD-02250':('int','FAILED_REGISTRATION_ORDINAL','2'),
 'PMD-02655':('long','CRITICAL_BYTE_GATE','4_500_000_000L'),
 'PMD-02656':('long','CRITICAL_FILE_GATE','9_000')}

def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inputs():
    normal=data.read_checked(data.BASE/'PG12312-readiness-dependency-six-compile-v1/manifest.json',NORMAL);assert normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');table={}
    for p in FILES:
        text=(snapshot/p).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][p]
        ts=list(LEX.finditer(text));lines=text.splitlines(keepends=True);rows=[]
        for r in original:
            if r['path']!=p or (r['rule']!='AvoidDuplicateLiterals' and r['id'] not in NUMBERS):continue
            assert r['inputSha256']==normal['begin']['inputHashes'][p]
            a=r['attributes'];start=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
            if r['rule']=='AvoidDuplicateLiterals':
                literal=next(m.group() for m in ts if m.start()==start);count=int(re.search(r' appears ([0-9]+) times',r['message'])[1]);name=NAMES[literal]
                assert sum(m.group()==literal for m in ts)==count
                rows.append(dict(id=r['id'],type='String',name=name,literal=literal,references=count))
            else:
                typ,name,literal=NUMBERS[r['id']];assert r['rule']=='AvoidLiteralsInIfCondition' and text[start:start+len(literal)]==literal
                rows.append(dict(id=r['id'],type=typ,name=name,literal=literal,references=1,originalStart=start))
            assert name not in raw(text)
        assert len(rows)==dict(DbPoolMetricObservationTest=5,WebDbPoolMetricObservationTest=5,OperationMismatchMetricRecorderTest=3,TransferCapacityTest=3)[Path(p).stem]
        assert len(re.findall(r'@Test\s+void ',text))==COUNTS[Path(p).stem];table[p]=rows
    assert sum(len(rs) for rs in table.values())==16 and sum(r['references'] for rs in table.values() for r in rs if r['type']=='String')==24
    return normal,snapshot,table

def changed(before,path,rows):
    after=before;numbers=[r for r in rows if r['type']!='String']
    for r in sorted(numbers,key=lambda r:r['originalStart'],reverse=True):
        start=r['originalStart'];assert after[start:start+len(r['literal'])]==r['literal'];after=after[:start]+r['name']+after[start+len(r['literal']):]
    after=transformed(after,Path(path).stem,[r for r in rows if r['type']=='String'])
    header='class '+Path(path).stem+' {\n';assert after.count(header)==1
    return after.replace(header,header+''.join('  private static final '+r['type']+' '+r['name']+' = '+r['literal']+';\n' for r in numbers),1)

def emit():
    _,snapshot,table=inputs();patch='*** Begin Patch\n'
    for p,rows in table.items():
        before=(snapshot/p).read_text();assert (data.ROOT/p).read_text()==before;after=changed(before,p,rows)
        patch+='*** Update File: '+str(data.ROOT/p)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,table=inputs()
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table)
    changes=[]
    for p,rows in table.items():
        before=(snapshot/p).read_text();after=(data.ROOT/p).read_text();assert raw(after)==raw(changed(before,p,rows))
        changes.append(dict(path=p,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,sourceBefore=normal['source'],sourceChanges=changes,stringConstants=5,stringReferences=24,numericConstants=11,numericReferences=11,rawDiagnosticsCorrected=16,originalMethods=29,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
