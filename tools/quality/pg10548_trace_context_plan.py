"""Only two explicit ordinary Mock boundary assertion blocks, no Production change."""
from pathlib import Path
import subprocess
from public_java_digest_provenance import LEX
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10530_trace_fallback_plan import P

BASE = '36c8d53dae2a333fe97ba8beef1a9c7f100033b2'
OUT = data.BASE/'PG10548-trace-context-plan-v1'
BLOCKS = ['''    assertEquals("WebRequestContext[REDACTED]", WebRequestContext.require(request).toString());
    request.removeAttribute(WebRequestContext.class.getName() + ".requestId");
    assertEquals(
        new UUID(0, 3),
        WebRequestContext.identify(
            request,
            () -> {
              throw new AssertionError("unexpected request identity allocation");
            }));
''','''    assertThrows(
        IllegalStateException.class, () -> WebRequestContext.require(new MockHttpServletRequest()));
    assertThrows(NullPointerException.class, () -> WebRequestContext.require(null));
    var mistypedContext = new MockHttpServletRequest();
    mistypedContext.setAttribute(WebRequestContext.class.getName(), "not-context");
    var contextFailure =
        assertThrows(
            IllegalStateException.class, () -> WebRequestContext.existing(mistypedContext));
    assertEquals("web request context is unavailable", contextFailure.getMessage());
    assertNull(contextFailure.getCause());
    assertEquals(0, contextFailure.getSuppressed().length);
''']


def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def validate(before,after):
    stripped = after
    for block in BLOCKS:
        if stripped.count(block) != 1:
            raise ValueError('exact independent boundary block required')
        stripped = stripped.replace(block,'',1)
    if tokens(stripped) != tokens(before):
        raise ValueError('all existing assertions, fixtures and other tokens required')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10538-trace-oracle-compile-v1/manifest.json',
        '56ed79534c2426ccd7ee115b0c11cf093b2ce74b72c46f655bda40d40872f28e')
    before = subprocess.check_output(['git','show',BASE+':'+P],cwd=data.ROOT).decode()
    after = (data.ROOT/P).read_text()
    assert normal['source'] == BASE and data.sha(before.encode()) == normal['begin']['inputHashes'][P]
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p != P)
    validate(before,after)
    damaged = [after.replace(block,'',1) for block in BLOCKS]
    damaged += [after.replace(BLOCKS[0],BLOCKS[0].replace('new UUID(0, 3)','new UUID(0, 4)'),1),
        after.replace(BLOCKS[1],BLOCKS[1].replace('web request context is unavailable','unsafe details'),1),
        after.replace('new UUID(1, 90), first.correlationId()','first.eventId(), first.correlationId()'),
        after.replace('assertEquals(37, annotations);','assertEquals(38, annotations);')]
    rejected = 0
    for sample in damaged:
        try:
            validate(before,sample)
        except ValueError:
            rejected += 1
    assert rejected == 6
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,baseSource=BASE,invocation=invocation,
        sourceChanges={P:data.sha(after.encode())},originalSha256=data.sha(before.encode()),
        addedBlocks=2,existingMethodsChanged=2,metadataNegativeVectors=6,
        allOriginalAssertionsAndOtherTokensPreserved=True,oldFallbackOraclePreserved=True,
        expectedRequestUuid='00000000-0000-0000-0000-000000000003',
        originalContextMissedCounters=dict(line=5,method=2,branch=3),
        productTestsExecuted=0,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
