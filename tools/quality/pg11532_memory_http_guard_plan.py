"""Fifty immediate conditional Exchange guards and two independent caller-failure cleanup oracles."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical

OUT=data.BASE/'PG11532-memory-http-guard-plan-v1'
FILES={role:f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{role.capitalize()}MetricHttpHandlerTest.java' for role in ('api','web')}

def guards(before):
    pairs={};stack=[]
    for m in LEX.finditer(before):
        if m.group()=='{':
            stack.append(m.start())
        elif m.group()=='}':
            pairs[stack.pop()]=m.start()
    assert not stack
    declarations=list(re.finditer(r'\bvar (exchange|first|second|missing) = new Exchange\([^;]*\);',before));assert len(declarations)==25
    grouped={};edits=[]
    for d in declarations:
        _,end=min(((a,b) for a,b in pairs.items() if a<d.start()<b),key=lambda item:item[1]-item[0])
        grouped.setdefault(end,[]).append(d);edits.append((d.end(),'\ntry {\n'))
    for end,rows in grouped.items():
        text=''
        for d in sorted(rows,key=lambda row:row.start(),reverse=True):
            v=d[1];text+='\n} finally {\nif (!'+v+'.closed) '+v+'.close();\n}\n'
        edits.append((end,text))
    after=before
    for offset,value in sorted(edits,reverse=True):
        after=after[:offset]+value+after[offset:]
    return after

def added_test(role):
    return '''
  @Test
  void ROLEmhttp023CallerFailureStillCleansOnceAndCompletedCloseIsNotRepeated() {
    var exchange = new Exchange(GET_METHOD, PATH);
    try {
      var failure = new AssertionError("caller cleanup fixture");
      assertFalse(exchange.closed);
      assertSame(failure, assertThrows(AssertionError.class, () -> {
        try { throw failure; }
        finally { if (!exchange.closed) exchange.close(); }
      }));
      assertTrue(exchange.closed);
      assertEquals(1, exchange.closeCalls);
      if (!exchange.closed) exchange.close();
      assertEquals(1, exchange.closeCalls);
    } finally { if (!exchange.closed) exchange.close(); }
  }
'''.replace('ROLE',role)

def transformed(before,role):
    after=guards(before);end=after.rfind('}')
    return after[:end]+added_test(role)+after[end:]

def inputs():
    normal=data.read_checked(data.BASE/'PG11504-metric-http-literal-six-compile-v1/manifest.json','8a626280621377d27599da1616906f6f1ef2d6f83420e25d495554392b250b11')
    audit=data.read_checked(data.BASE/'PG11530-memory-http-owner-review-post-v1/manifest.json','bb9d0931587191d79ddac3132a03cc42f8a14a5cd35a61e9aeab02f2ace752f8')
    assert normal['source']==audit['source']=='60d702bf8d83b6c4c8531397a7b770234fd9cf6e' and normal['actualExit']==audit['actualExit']==0 and audit['guardGaps']==50
    return normal,Path(normal['jars']['protocol']['path']).parent.parent.parent.parent

def emit():
    _,snapshot=inputs();patch='*** Begin Patch\n'
    for role,path in FILES.items():
        before=(snapshot/path).read_text();assert (data.ROOT/path).read_text()==before
        after=transformed(before,role)
        patch+='*** Update File: '+str(data.ROOT/path)+'\n'
        patch+='\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation=capture(__file__);assert not OUT.exists();normal,snapshot=inputs();rows=[]
    for role,path in FILES.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text();assert canonical(after)==canonical(transformed(before,role))
        old=re.findall(r'@Test\s+void (\w+)\(\)',before);new=re.findall(r'@Test\s+void (\w+)\(\)',after)
        assert len(old)==22 and len(new)==len(set(new))==23
        rows.append(dict(path=path,role=role,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),originalMethods=old,addedMethods=[m for m in new if m not in old],candidateGuards=25))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in FILES.values())
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=rows,candidateGuards=50,
        originalMethods=44,addedIndependentMethods=2,productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None,allMainAndOtherInputsPreserved=True,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
