"""27 same-value explicit-binary modes, five fixed field names and one independent bound."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10840_web_view_duplicate_plan import transformed as strings

OUT=data.BASE/'PG11920-storage-attribute-fixture-plan-v1'
FILE='src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/StorageAttributeGuardTest.java'
JAVA=re.compile(r'(?:0[bB][01](?:_?[01])*|0[0-7]+|[1-9][0-9]*(?:_?[0-9])*)|(?:'+LEX.pattern+')',LEX.flags)
NAMES={'"size"':'SIZE_FIELD','"owner"':'OWNER_FIELD','"group"':'GROUP_FIELD','"mode"':'MODE_FIELD','"nlink"':'LINK_COUNT_FIELD'}

def lexical(text):
    return [m.group() for m in JAVA.finditer(text) if not m.group().startswith(('//','/*'))]

def binary(old):
    assert re.fullmatch(r'0[0-7]+',old)
    value='0b'+'_'.join(format(int(d),'03b') for d in old[1:]);assert int(old,8)==int(value[2:].replace('_',''),2)<2**31
    return value

def inputs():
    normal=data.read_checked(data.BASE/'PG11894-session-json-fixture-six-compile-v1/manifest.json','3cc0fa3b71e348b8d5821b1269e616a69999c0c5467d6f7bb38c9b3cf69830e0');assert normal['actualExit']==normal['testsExecuted']==0;snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;text=(snapshot/FILE).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][FILE];root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');rows=[];lines=text.splitlines(keepends=True);ts=list(LEX.finditer(text))
    for row in root:
        if row['path']!=FILE or row['rule'] not in ('AvoidDuplicateLiterals','AvoidUsingOctalValues'):continue
        assert row['inputSha256']==normal['begin']['inputHashes'][FILE];a=row['attributes'];point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
        if row['rule']=='AvoidDuplicateLiterals':
            literal=next(m.group() for m in ts if m.start()==point);count=int(re.search(r' appears ([0-9]+) times',row['message'])[1]);assert literal in NAMES and sum(m.group()==literal for m in ts)==count;rows.append(dict(id=row['id'],kind='STRING',literal=literal,name=NAMES[literal],references=count))
        else:
            match=re.match(r'0[0-7]+(?!\w)',text[point:]);assert match is not None;literal=match.group();rows.append(dict(id=row['id'],kind='MODE',literal=literal,replacement=binary(literal),decimalValue=int(literal,8),point=point,references=1))
    needle='if (size > 48_000_000)';assert text.count(needle)==1;point=text.index(needle)+len('if (size > ');rows.append(dict(id='PMD-07136',kind='BOUND',literal='48_000_000',replacement='TRANSFER_LIMIT_BYTES',point=point,references=1));assert sum(r['kind']=='MODE' for r in rows)==27 and sum(r['kind']=='STRING' for r in rows)==5 and sum(r['references'] for r in rows if r['kind']=='STRING')==55
    assert not any(t in {'TRANSFER_LIMIT_BYTES',*NAMES.values()} for t in lexical(text));assert not any(t.startswith(('0b','0B')) for t in lexical(text))
    return normal,snapshot,rows

def transformed(text,rows):
    for row in sorted((r for r in rows if r['kind']!='STRING'),key=lambda r:r['point'],reverse=True):
        i=row['point'];assert text[i:i+len(row['literal'])]==row['literal'];text=text[:i]+row['replacement']+text[i+len(row['literal']):]
    text=strings(text,'StorageAttributeGuardTest',[r for r in rows if r['kind']=='STRING']);header='class StorageAttributeGuardTest {\n';assert text.count(header)==1;return text.replace(header,header+'  private static final int TRANSFER_LIMIT_BYTES = 48_000_000;\n',1)

def emit():
    _,snapshot,rows=inputs();before=(snapshot/FILE).read_text();assert (data.ROOT/FILE).read_text()==before;after=transformed(before,rows);return '*** Begin Patch\n*** Update File: '+str(data.ROOT/FILE)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,rows=inputs();assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p!=FILE);before=(snapshot/FILE).read_text();after=(data.ROOT/FILE).read_text();assert lexical(after)==lexical(transformed(before,rows));verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=[dict(path=FILE,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows)],stringConstants=5,stringReferences=55,modeLiteralPoints=27,boundConstants=1,originalMethods=7,rawDiagnosticCorrectionsExpected=33,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
