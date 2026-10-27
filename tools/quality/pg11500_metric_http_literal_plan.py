"""Sixteen same-value memory HTTP fixture constants with coordinate-bound Java raw literals."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg10840_web_view_duplicate_plan import transformed

OUT=data.BASE/'PG11500-metric-http-literal-plan-v1'
FILES=[f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{role.capitalize()}MetricHttpHandlerTest.java' for role in ('api','web')]
NAMES={'"GET"':'GET_METHOD',r'"1\n"':'READY_TRUE_SUFFIX',r'"0\n"':'READY_FALSE_SUFFIX','"DEBUG"':'DEBUG_MODE',
    '"Content-Type"':'CONTENT_TYPE_HEADER','"no-store"':'NO_STORE_VALUE','"Cache-Control"':'CACHE_CONTROL_HEADER','"STANDARD"':'STANDARD_MODE'}

def inputs():
    normal=data.read_checked(data.BASE/'PG11474-api-web-gc-literal-six-compile-v1/manifest.json','53e240a80b6c663419f8cff7ecb2199c8f36c343cfa9c072f8087ba0b3062cd2')
    assert normal['source']=='d1fa07bbd145ea48854b9f2b3b8be6f0f3c99dd7' and normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    rows=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    selected=[r for r in rows if r['path'] in FILES and r['rule']=='AvoidDuplicateLiterals']
    assert len(selected)==16
    table={}
    for row in selected:
        path=row['path'];before=(snapshot/path).read_text()
        assert data.sha(before.encode())==row['inputSha256']==normal['begin']['inputHashes'][path]
        matches=[m for m in LEX.finditer(before) if before[:m.start()].count('\n')+1==row['line'] and m.start()-before.rfind('\n',0,m.start())==int(row['attributes']['begincolumn'])]
        assert len(matches)==1
        literal=matches[0].group();assert literal in NAMES
        found=[m for m in LEX.finditer(before) if m.group()==literal]
        count=int(re.search(r' appears ([0-9]+) times in this file;',row['message'])[1])
        assert len(found)==count and found[0].start()==matches[0].start()
        name=NAMES[literal];assert not any(m.group()==name for m in LEX.finditer(before))
        table.setdefault(path,[]).append(dict(id=row['id'],name=name,literal=literal,references=count))
    assert set(table)==set(FILES) and sum(len(v) for v in table.values())==16 and sum(r['references'] for v in table.values() for r in v)==168
    return normal,snapshot,table

def emit():
    _,snapshot,table=inputs();patch='*** Begin Patch\n'
    for path,rows in table.items():
        before=(snapshot/path).read_text();assert (data.ROOT/path).read_text()==before
        after=transformed(before,Path(path).stem,rows)
        patch+='*** Update File: '+str(data.ROOT/path)+'\n'
        patch+='\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    normal,snapshot,table=inputs()
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table)
    changes=[]
    for path,rows in table.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text()
        assert canonical(after)==canonical(transformed(before,Path(path).stem,rows))
        changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows))
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changes,
        stringConstants=16,referencesReplaced=168,originalMethods=44,allMainAndOtherInputsPreserved=True,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
