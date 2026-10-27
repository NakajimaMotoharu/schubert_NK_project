"""Same-value five Storage and Batch repository enum catalog literals; strict raw token inverse, no Main change."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from host_tool_invocation import capture,verify
from pg10840_web_view_duplicate_plan import transformed
OUT=data.BASE/'PG12472-enum-catalog-plan-v1'
NORMAL='face6e2196f8345f8ba51f4e1d29ff10df42231737e801e109d8f0e32b6d43f2'
FILES=['src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/EnumValueCatalogCompatibilityTest.java','src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/EnumValueCatalogCompatibilityTest.java']
NAMES={'"API"':'API_NAME','"WEB"':'WEB_NAME','"PASSWORD"':'PASSWORD_KIND','"KEY"':'KEY_KIND','"CLEAN_BATCH_RUN"':'CLEAN_BATCH_RUN_NAME'}
def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
def inputs():
    normal=data.read_checked(data.BASE/'PG12450-config-template-six-compile-v1/manifest.json',NORMAL);assert normal['actualExit']==normal['testsExecuted']==0;snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966');table={}
    for path in FILES:
        text=(snapshot/path).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][path];ts=list(LEX.finditer(text));lines=text.splitlines(keepends=True);rows=[]
        for row in original:
            if row['path']!=path or row['rule']!='AvoidDuplicateLiterals':continue
            assert row['inputSha256']==normal['begin']['inputHashes'][path];a=row['attributes'];point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1;literal=next(m.group() for m in ts if m.start()==point);count=int(re.search(r' appears ([0-9]+) times',row['message'])[1]);assert literal in NAMES and sum(m.group()==literal for m in ts)==count
            rows.append(dict(id=row['id'],literal=literal,name=NAMES[literal],references=count))
        assert len(rows)==(4 if '/schubert-nk-storage/' in path else 1) and not set(raw(text))&{r['name'] for r in rows};assert len(re.findall(r'@Test\s+void ',text))==1;table[path]=rows
    return normal,snapshot,table

def emit():
    _,snapshot,table=inputs();patch='*** Begin Patch\n'
    for path,rows in table.items():
        before=(snapshot/path).read_text();assert (data.ROOT/path).read_text()==before;after=transformed(before,Path(path).stem,rows);patch+='*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'
def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,table=inputs();assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table);changes=[]
    for path,rows in table.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text();assert raw(after)==raw(transformed(before,Path(path).stem,rows));changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,stringConstants=5,stringReferences=sum(r['references'] for rows in table.values() for r in rows),originalMethods=2,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
