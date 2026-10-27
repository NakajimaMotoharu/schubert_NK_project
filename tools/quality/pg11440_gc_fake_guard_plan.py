"""Twenty-four immediate Fake guards, logical close confirmation and six independent cleanup vectors."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg11376_full_payload_guard_plan import block

OUT=data.BASE/'PG11440-gc-fake-guard-plan-v1'
FILES={role:f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{role.capitalize()}GcMetricRegistrationTest.java' for role in ('api','web','batch')}


def guards(before):
    pairs={};stack=[]
    tokens=[m for m in LEX.finditer(before) if not m.group().startswith(('//','/*'))]
    for m in tokens:
        if m.group()=='{':
            stack.append(m.start())
        elif m.group()=='}':
            pairs[stack.pop()]=m.start()
    assert not stack
    declarations=list(re.finditer(r'\bvar (resource|one|two) = new Fake\(\);',before))
    assert len(declarations)==8
    grouped={};edits=[]
    for d in declarations:
        scopes=[(a,b) for a,b in pairs.items() if a<d.start()<b]
        _,end=min(scopes,key=lambda x:x[1]-x[0])
        grouped.setdefault(end,[]).append(d)
        edits.append((d.end(),'\ntry {\n'))
    for end,rows in grouped.items():
        closing=''
        for d in sorted(rows,key=lambda d:d.start(),reverse=True):
            v=d[1]
            closing+='\n} finally {\nif (!'+v+'.closeConfirmed) '+v+'.close();\n}\n'
        edits.append((end,closing))
    after=before
    for offset,value in sorted(edits,reverse=True):
        after=after[:offset]+value+after[offset:]
    return after


def added_tests(role):
    return '''
  @Test
  void ROLEgc015ConfirmedFixtureCloseIsNotRepeatedByCleanupGuard() {
    var resource = new Fake();
    try {
      assertFalse(resource.closeConfirmed);
      resource.close();
      assertTrue(resource.closeConfirmed);
      if (!resource.closeConfirmed) resource.close();
      assertEquals(1, resource.closeInvocations.get());
    } finally {
      if (!resource.closeConfirmed) resource.close();
    }
  }

  @Test
  void ROLEgc016FailedFixtureCloseRemainsUnconfirmedUntilExplicitRetry() {
    for (boolean priorSuccess : List.of(false, true)) {
      for (Throwable failure : List.of(new IllegalStateException("cleanup runtime fixture"), new AssertionError("cleanup fatal fixture"))) {
        var resource = new Fake();
        try {
          if (priorSuccess) resource.close();
          resource.onCloseCallback = () -> fail(failure);
          assertSame(failure, assertThrows(failure.getClass(), resource::close));
          assertFalse(resource.closeConfirmed);
          assertEquals(priorSuccess ? 2 : 1, resource.closeInvocations.get());
          resource.onCloseCallback = () -> {};
          if (!resource.closeConfirmed) resource.close();
          assertTrue(resource.closeConfirmed);
          assertEquals(priorSuccess ? 3 : 2, resource.closeInvocations.get());
        } finally {
          resource.onCloseCallback = () -> {};
          if (!resource.closeConfirmed) resource.close();
        }
      }
    }
  }
'''.replace('ROLE',role)


def transformed(before,role):
    after=guards(before)
    a,b=block(after,r'private static final class Fake extends JvmGcMetrics\s*\{')
    body=after[a:b]
    marker='final AtomicInteger closeInvocations = new AtomicInteger();'
    assert body.count(marker)==1 and 'closeConfirmed' not in body
    body=body.replace(marker,marker+'\nboolean closeConfirmed;',1)
    old='public void close() {\n      closeInvocations.incrementAndGet();\n      onCloseCallback.run();\n    }'
    new='public void close() {\n      closeConfirmed = false;\n      closeInvocations.incrementAndGet();\n      onCloseCallback.run();\n      closeConfirmed = true;\n    }'
    assert body.count(old)==1
    body=body.replace(old,new,1)
    after=after[:a]+body+after[b:]
    end=after.rfind('}')
    return after[:end]+added_tests(role)+after[end:]


def inputs():
    normal=data.read_checked(data.BASE/'PG11412-api-web-payload-literal-six-compile-v1/manifest.json',
        'b560ea0179e27b26375d96e7deb6f39deba5e728a2c5d57ed0fee6c46a67933d')
    proof=data.read_checked(data.BASE/'PG11436-gc-fake-comparable-review-post-v1/manifest.json',
        'f0f43844636b1862964a1b12fa7f7376b1b7e54a5b3b7e9aae3cb05e90d41649')
    assert normal['source']==proof['source']=='2d733dbd80350c819b732ae3d9b9b0f85ba0172f' and normal['actualExit']==proof['actualExit']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    return normal,snapshot


def emit():
    normal,snapshot=inputs();patch='*** Begin Patch\n'
    for role,path in FILES.items():
        before=(snapshot/path).read_text()
        assert data.sha(before.encode())==normal['begin']['inputHashes'][path] and (data.ROOT/path).read_text()==before
        after=transformed(before,role)
        patch+='*** Update File: '+str(data.ROOT/path)+'\n'
        patch+='\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    normal,snapshot=inputs();rows=[]
    for role,path in FILES.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text()
        assert canonical(after)==canonical(transformed(before,role))
        old=re.findall(r'@Test\s+void (\w+)\(\)',before);new=re.findall(r'@Test\s+void (\w+)\(\)',after)
        assert len(old)==14 and len(new)==16 and len(set(new))==16
        rows.append(dict(path=path,role=role,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),
            originalMethods=old,addedMethods=[m for m in new if m not in old],candidateGuards=8))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in FILES.values())
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=rows,
        candidateGuards=24,logicalCloseConfirmationFields=3,originalMethods=42,addedIndependentMethods=6,
        productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None,allMainAndOtherInputsPreserved=True,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
