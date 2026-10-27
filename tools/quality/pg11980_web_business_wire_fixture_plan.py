"""Independent Web business fixture22 strings and two length-table field renames, Main unchanged."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10840_web_view_duplicate_plan import transformed as strings
OUT=data.BASE/'PG11980-web-business-wire-fixture-plan-v1'
FILE='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/WebBusinessWireClientsTest.java'
NAMES={'"'+k+'"':k+'_TYPE' for k in ('QSB','QSS','QSD','QDL','NTS','NTD','NTC','USR','UDT','UCR','UST','URL','UPW','ULK','LOG','AUD','VID','MED')}
NAMES.update({'"9000"':'ERROR_RESULT_CODE','"0000"':'SUCCESS_RESULT_CODE','"2026-10-02T19:00:00.123Z"':'EXPECTED_INSTANT_TEXT','"20261003040000123"':'WIRE_TIMESTAMP_TEXT'})
RENAMES={'REQUEST':'REQUEST_DATA_LENGTHS','RESPONSE':'RESPONSE_DATA_LENGTHS'}
def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
def inputs():
    normal=data.read_checked(data.BASE/'PG11954-jms-proxy-fixture-six-compile-v1/manifest.json','9914ca39739520420fbad05428dbf20ef4c776998175713a838b4ca0ab1b6824');assert normal['actualExit']==normal['testsExecuted']==0;snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;text=(snapshot/FILE).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][FILE];ts=list(LEX.finditer(text));lines=text.splitlines(keepends=True);original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[];fields=[]
    for row in original:
        if row['path']!=FILE or row['rule'] not in ('AvoidDuplicateLiterals','AvoidFieldNameMatchingMethodName'):continue
        assert row['inputSha256']==normal['begin']['inputHashes'][FILE];a=row['attributes'];point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;literal=next(m.group() for m in ts if m.start()==point)
        if row['rule']=='AvoidDuplicateLiterals':
            count=int(re.search(r' appears ([0-9]+) times',row['message'])[1]);assert literal in NAMES and sum(m.group()==literal for m in ts)==count;rows.append(dict(id=row['id'],literal=literal,name=NAMES[literal],references=count))
        else:
            assert literal in RENAMES;fields.append(dict(id=row['id'],oldName=literal,newName=RENAMES[literal],bindings=raw(text).count(literal)))
    assert len(rows)==22 and len(fields)==2 and all(f['bindings']==2 for f in fields);assert not set(raw(text))&({r['name'] for r in rows}|set(RENAMES.values()));assert len(re.findall(r'@Test\s+void ',text))==8
    return normal,snapshot,rows,fields

def transformed(text,rows):
    value=strings(text,'WebBusinessWireClientsTest',rows)
    return LEX.sub(lambda m:RENAMES.get(m.group(),m.group()),value)
def emit():
    _,snapshot,rows,_=inputs();before=(snapshot/FILE).read_text();assert (data.ROOT/FILE).read_text()==before;after=transformed(before,rows);return '*** Begin Patch\n*** Update File: '+str(data.ROOT/FILE)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n*** End Patch\n'
def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,rows,fields=inputs();assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p!=FILE);before=(snapshot/FILE).read_text();after=(data.ROOT/FILE).read_text();assert raw(after)==raw(transformed(before,rows));verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=[dict(path=FILE,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows,renames=fields)],stringConstants=22,stringReferences=sum(r['references'] for r in rows),renamedFields=2,renamedBindings=4,originalMethods=8,rawDiagnosticCorrectionsExpected=24,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
