"""Minimal full helper transfer/failure guards and three independent closed-candidate vectors."""
import difflib
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg11318_batch_source_guard_plan import body_span,owner_end

OUT=data.BASE/'PG11376-full-payload-guard-plan-v1'
FILES={role:f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{stem}.java'
    for role,stem in [('api','ApiCustomMetricPayloadTest'),('web','WebCustomMetricPayloadTest'),('batch','BatchMetricTextTest')]}


def block(text,pattern):
    matches=list(re.finditer(pattern,text))
    if len(matches)!=1:
        raise ValueError('one exact source body header')
    start=matches[0].end()
    depth=1
    for m in LEX.finditer(text,start):
        depth+=(m.group()=='{')-(m.group()=='}')
        if not depth:
            return start,m.start()
    raise ValueError('complete source block')


def added_test(role):
    return '''
  @Test
  void ROLEfull013HelperReleasesRejectedCandidateBeforeReturningOwner() {
    var probe = new FullProbe();
    try {
      probe.close();
      assertEquals(1, probe.closes.get());
      var failure = assertThrows(IllegalStateException.class, () -> fullOwner(probe));
      assertEquals("standard metric registry closed", failure.getMessage());
      assertEquals(2, probe.closes.get());
      assertEquals(0, probe.scrapes.get());
      assertTrue(probe.isClosed());
    } finally {
      probe.close();
    }
  }
'''.replace('ROLE',role)


def transformed(text,role):
    a,b=block(text,r'private static final class FullProbe\s+extends\s+[\w.]+\s*\{')
    body=text[a:b]
    assert 'final AtomicInteger closes' not in body
    body=body.replace('final AtomicInteger scrapes = new AtomicInteger();',
        'final AtomicInteger scrapes = new AtomicInteger();\n    final AtomicInteger closes = new AtomicInteger();')
    body+='''
    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
'''
    text=text[:a]+body+text[b:]
    a,b=block(text,r'private static '+role.capitalize()+r'StandardMetricSource fullOwner\(FullProbe probe\)\s*\{')
    body=text[a:b];split=owner_end(body)
    rest=body[split:]
    assert canonical(rest)==canonical('owner.bind('+('DEBUG_MODE' if role=='batch' else '"DEBUG"')+');return owner;')
    text=text[:a]+body[:split]+'''\n    boolean transferred = false;
    try {
'''+rest.replace('return owner;','transferred = true;\n    return owner;')+'''\n    } finally {
      if (!transferred) owner.close();
    }
  '''+text[b:]
    if role!='batch':
        name=role+'full011ConcurrentFullScrapesKeepIndependentGoldenAndOwnership'
        a,b=body_span(text,name);body=text[a:b]
        old='var executor = Executors.newFixedThreadPool(4);\n      try {'
        assert body.count(old)==1
        body=body.replace(old,'try (var executor = Executors.newFixedThreadPool(4)) {\n      try {')
        marker='      Reference.reachabilityFence(bundle);'
        assert body.count(marker)==1
        body=body.replace(marker,'      }\n'+marker)
        text=text[:a]+body+text[b:]
        name=role+'full012CallerCloseBetweenSourcesCannotReturnPartialText'
        a,b=body_span(text,name);body=text[a:b]
        old='var standard = fullOwner(probe);\n    var executor = Executors.newSingleThreadExecutor();'
        assert body.count(old)==1
        body=body.replace(old,'var standard = fullOwner(probe);\n    try {\n    try (var executor = Executors.newSingleThreadExecutor()) {')
        body=body.rstrip()+'''\n    }
    } finally {
      standard.close();
    }
  '''
        text=text[:a]+body+text[b:]
    last=text.rfind('}')
    return text[:last]+added_test(role)+text[last:]


def inputs():
    normal=data.read_checked(data.BASE/'PG11348-api-web-source-guard-six-compile-v1/manifest.json',
        '46569de89d536e303184cd570d83f5138eb3a344abeb64f4e01160622a5482e8')
    review=data.read_checked(data.BASE/'PG11372-source-constructor-owner-audit-post-v1/manifest.json',
        '62d37929e30ccea89145ea07a5a8c599c00f74edfc357727ba31fb7383e27555')
    assert normal['source']==review['source']=='d4b5507ba6a76a85c23806e5604a0278f1795f37' and normal['actualExit']==review['actualExit']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    return normal,snapshot


def emit():
    normal,snapshot=inputs()
    patch='*** Begin Patch\n'
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
    normal,snapshot=inputs()
    changed=[]
    for role,path in FILES.items():
        before=(snapshot/path).read_text();after=(data.ROOT/path).read_text()
        assert canonical(after)==canonical(transformed(before,role))
        old=re.findall(r'@Test\s+void (\w+)\(\)',before)
        new=re.findall(r'@Test\s+void (\w+)\(\)',after)
        assert len(old)=={'api':25,'web':25,'batch':36}[role] and len(new)==len(old)+1
        changed.append(dict(path=path,role=role,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),
            originalMethods=old,newMethod=role+'full013HelperReleasesRejectedCandidateBeforeReturningOwner'))
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in FILES.values())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=changed,
        helperTransferGuards=3,outerOwnerGuards=2,executorTwr=4,originalMethods=86,addedMethods=3,suites=3,
        productTestsExecuted=0,coverage=None,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
