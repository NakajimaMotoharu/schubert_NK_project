"""Six same-byte independent JSON fixture constants and one first-token condition only."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg10840_web_view_duplicate_plan import transformed as strings

OUT=data.BASE/'PG11890-session-json-fixture-plan-v1'
FILE='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/SessionAttributeCodecTest.java'
NAMES=dict(zip(['PMD-09045','PMD-09046','PMD-09047','PMD-09048','PMD-09049','PMD-09050'],['READER_NAME','QUESTION_SUBMIT_PURPOSE','NULL_JSON_LITERAL','FIELD_SEPARATOR','USER_ROLE','LOGS_TARGET']))

def inputs():
    normal=data.read_checked(data.BASE/'PG11864-web-exporter-fixture-six-compile-v1/manifest.json','920dd983970da239050bc75e2f736650e4d5a6349aa5bff3d05e5203a40d2f2d');assert normal['actualExit']==normal['testsExecuted']==0;snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;text=(snapshot/FILE).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][FILE];root=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');ts=list(LEX.finditer(text));rows=[]
    for row in root:
        if row['path']!=FILE or row['rule']!='AvoidDuplicateLiterals':continue
        assert row['inputSha256']==normal['begin']['inputHashes'][FILE];a=row['attributes'];lines=text.splitlines(keepends=True);point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;m=next(m for m in ts if m.start()==point);literal=m.group();count=int(re.search(r' appears ([0-9]+) times',row['message'])[1]);assert row['id'] in NAMES and sum(m.group()==literal for m in ts)==count;rows.append(dict(id=row['id'],kind='STRING',literal=literal,name=NAMES[row['id']],references=count))
    assert len(rows)==6 and sum(r['references'] for r in rows)==33;needle='if (i > 1)';assert text.count(needle)==1;offset=text.index(needle)+len('if (i > ');assert text[offset]=='1';rows.append(dict(id='PMD-09053',kind='ORDER_INT',literal='1',name='FIRST_TOKEN_INDEX',references=1,point=offset));assert not any(m.group() in {r['name'] for r in rows} for m in ts)
    return normal,snapshot,rows

def transformed(text,rows):
    row=rows[-1];i=row['point'];assert text[i]=='1';value=text[:i]+row['name']+text[i+1:];value=strings(value,'SessionAttributeCodecTest',rows[:-1]);header='class SessionAttributeCodecTest {\n';assert value.count(header)==1;return value.replace(header,header+'  private static final int FIRST_TOKEN_INDEX = 1;\n',1)

def emit():
    _,snapshot,rows=inputs();before=(snapshot/FILE).read_text();assert (data.ROOT/FILE).read_text()==before;after=transformed(before,rows);return '*** Begin Patch\n*** Update File: '+str(data.ROOT/FILE)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,rows=inputs();assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p!=FILE);before=(snapshot/FILE).read_text();after=(data.ROOT/FILE).read_text();assert canonical(after)==canonical(transformed(before,rows));verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=[dict(path=FILE,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows)],stringConstants=6,stringReferences=33,orderConstants=1,comparisonReferences=1,originalMethods=7,relatedUnchangedV2Methods=5,plannedSelectedMethods=12,rawDiagnosticCorrectionsExpected=7,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
