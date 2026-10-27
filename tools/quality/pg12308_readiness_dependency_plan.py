"""Five same-value pure readiness/POM fixture constants; full original method tokens remain unchanged."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10840_web_view_duplicate_plan import transformed

OUT=data.BASE/'PG12308-readiness-dependency-plan-v1'
NORMAL='776c71c70a1953bcdbf96f0d3b220cdcb91f7523a2ae38fa6664bdb33494104b'
FILES=['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiReadinessPredicateTest.java','src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeDependencyTest.java']
COUNTS=dict(ApiReadinessPredicateTest=3,WebRuntimeDependencyTest=1)
NAMES={'"groups"':'CONSUMER_GROUPS_STEP','"stop"':'STOP_STEP','"outbox"':'OUTBOX_STEP','"consumers"':'CONSUMERS_STEP','"<scope>runtime</scope>"':'RUNTIME_SCOPE_XML'}
METHODS=r'@Test\s+(?:@DisplayName\([^\n]*\)\s+)?void (\w+)\('

def inputs():
    normal=data.read_checked(data.BASE/'PG12286-api-value-six-compile-v1/manifest.json',NORMAL)
    assert normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    table={}
    for path in FILES:
        text=(snapshot/path).read_text();assert data.sha(text.encode())==normal['begin']['inputHashes'][path]
        tokens=list(LEX.finditer(text));lines=text.splitlines(keepends=True);rows=[]
        for row in original:
            if row['path']!=path or row['rule']!='AvoidDuplicateLiterals':continue
            assert row['inputSha256']==normal['begin']['inputHashes'][path]
            a=row['attributes'];point=sum(map(len,lines[:int(a['beginline'])-1]))+int(a['begincolumn'])-1
            literal=next(m.group() for m in tokens if m.start()==point)
            count=int(re.search(r' appears ([0-9]+) times',row['message'])[1])
            assert literal in NAMES and sum(m.group()==literal for m in tokens)==count
            assert not any(m.group()==NAMES[literal] for m in tokens)
            rows.append(dict(id=row['id'],literal=literal,name=NAMES[literal],references=count))
        assert len(rows)==dict(ApiReadinessPredicateTest=4,WebRuntimeDependencyTest=1)[Path(path).stem]
        assert len(re.findall(METHODS,text))==COUNTS[Path(path).stem];table[path]=rows
    assert sum(map(len,table.values()))==5 and sum(r['references'] for rs in table.values() for r in rs)==29
    return normal,snapshot,table

def emit():
    _,snapshot,table=inputs();patch='*** Begin Patch\n'
    for path,rows in table.items():
        before=(snapshot/path).read_text();assert (data.ROOT/path).read_text()==before
        after=transformed(before,Path(path).stem,rows)
        patch+='*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot,table=inputs()
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table)
    changes=[]
    for p,rows in table.items():
        before=(snapshot/p).read_text();after=(data.ROOT/p).read_text()
        expected=transformed(before,Path(p).stem,rows)
        assert [m.group() for m in LEX.finditer(after) if not m.group().startswith(('//','/*'))]==[m.group() for m in LEX.finditer(expected) if not m.group().startswith(('//','/*'))]
        changes.append(dict(path=p,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,sourceBefore=normal['source'],sourceChanges=changes,stringConstants=5,stringReferences=29,originalMethods=sum(COUNTS.values()),allMainAndOtherInputsPreserved=True,productTestsExecuted=0,coverage=None,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
