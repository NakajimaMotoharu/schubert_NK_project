"""Eight same-value HTTP fixture constants, private field rename and owned executor TWR."""
import difflib
import json
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg10840_web_view_duplicate_plan import transformed as strings

OUT=data.BASE/'PG11260-http-recorder-fixture-plan-v1'
FILE='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/HttpMetricRecorderTest.java'
NAMES={'service':'SERVICE_LABEL','WEB':'WEB_SERVICE_NAME','route':'ROUTE_LABEL','/login':'LOGIN_PATH',
    'GET':'GET_METHOD','DEBUG':'DEBUG_MODE','2xx':'SUCCESS_STATUS_LABEL','/search':'SEARCH_PATH'}


def inputs():
    normal=data.read_checked(data.BASE/'PG11238-batch-supplied-metric-label-fixture-six-compile-v1/manifest.json',
        '5c832221f384ea840e6a9b5cf9b55e7c6f797e472647d7831c3a8ad1409f0bbe')
    assert normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    rows=[r for r in original if r['path']==FILE and r['rule']=='AvoidDuplicateLiterals']
    assert len(rows)==8
    before=(snapshot/FILE).read_text()
    table=[]
    for row in rows:
        assert data.sha(before.encode())==row['inputSha256']==normal['begin']['inputHashes'][FILE]
        match=re.fullmatch(r'The String literal "(.*)" appears ([0-9]+) times in this file; the first occurrence is on line [0-9]+',row['message'])
        assert match and match[1] in NAMES
        literal=json.dumps(match[1],ensure_ascii=False)
        found=[m for m in LEX.finditer(before) if m.group()==literal]
        assert len(found)==int(match[2]) and before[:found[0].start()].count('\n')+1==row['line']
        name=NAMES[match[1]]
        assert not any(m.group()==name for m in LEX.finditer(before))
        table.append(dict(id=row['id'],name=name,literal=literal,references=len(found)))
    return normal,snapshot,table


def transformed(before,rows):
    after=strings(before,'HttpMetricRecorderTest',rows)
    assert 'DURATION_METRIC' not in after
    for m in reversed(list(LEX.finditer(after))):
        if m.group()=='DURATION':
            after=after[:m.start()]+'DURATION_METRIC'+after[m.end():]
    start='      var executor = Executors.newFixedThreadPool(4);\n      try {'
    end='        assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));\n      }\n      assertEquals(64.0,'
    assert after.count(start)==after.count(end)==1
    after=after.replace(start,'      try (var executor = Executors.newFixedThreadPool(4)) {\n      try {',1)
    return after.replace(end,'        assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));\n      }\n      }\n      assertEquals(64.0,',1)


def emit():
    _,snapshot,rows=inputs()
    before=(snapshot/FILE).read_text()
    assert (data.ROOT/FILE).read_text()==before
    after=transformed(before,rows)
    diff=list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:]
    return '*** Begin Patch\n*** Update File: '+str(data.ROOT/FILE)+'\n'+'\n'.join('@@' if x.startswith('@@') else x for x in diff)+'\n*** End Patch\n'


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    normal,snapshot,rows=inputs()
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p!=FILE)
    before,after=(snapshot/FILE).read_text(),(data.ROOT/FILE).read_text()
    assert canonical(after)==canonical(transformed(before,rows))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,
        sourceChanges=[dict(path=FILE,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),constants=rows)],
        stringConstants=8,referencesReplaced=sum(r['references'] for r in rows),privateFieldRename='DURATION_TO_DURATION_METRIC',
        ownedExecutorTwr=1,originalFinallyAndTimeoutAssertionsRetained=True,allMainAndOtherInputBytesPreserved=True,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
