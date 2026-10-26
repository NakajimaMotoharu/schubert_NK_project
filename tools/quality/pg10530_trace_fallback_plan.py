"""One fixed input oracle expression, original entire source byte preservation."""
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

BASE = '6612747b7a5492e5c49647d85cfc2dcbe6d75c9f'
P = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebRequestTraceTest.java'
OLD = 'assertEquals(same ? new UUID(2, 91) : first.eventId(), first.correlationId());'
NEW = 'assertEquals(same ? new UUID(2, 91) : new UUID(1, 90), first.correlationId());'
OUT = data.BASE/'PG10530-trace-fallback-plan-v1'


def validate(before,after):
    if before.count(OLD) != 1 or after != before.replace(OLD,NEW,1):
        raise ValueError('one exact independent expected expression; all other bytes unchanged')
    if 'var first = trace(new MockHttpServletRequest(), 90);' not in after:
        raise ValueError('fixed input first identity required')
    if '() -> calls.getAndIncrement() == 0 ? new UUID(0, id) : new UUID(1, id)' not in after:
        raise ValueError('fixed input event generator required')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10508-anm-type-name-compile-v1/manifest.json',
        'bc2c2ee9ff267ab6ea56f33df42b0272636cd928c23cdb3cc9b33bf1db3773c5')
    before = subprocess.check_output(['git','show',BASE+':'+P],cwd=data.ROOT).decode()
    after = (data.ROOT/P).read_text()
    assert data.sha(before.encode()) == normal['begin']['inputHashes'][P] == '0702bba0a2a3c0e0bfa7dd20b592bd232cba0ec1fba0935a231ecf32be4b8cb9'
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p != P)
    validate(before,after)
    rejected = 0
    for damaged in (before,after.replace('new UUID(1, 90), first.correlationId()',
                                        'new UUID(1, 91), first.correlationId()'),
                    after.replace('var first = trace(new MockHttpServletRequest(), 90);',
                                  'var first = trace(new MockHttpServletRequest(), 89);')):
        try:
            validate(before,damaged)
        except ValueError:
            rejected += 1
    assert rejected == 3
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,baseSource=BASE,invocation=invocation,
        sourceChanges={P:data.sha(after.encode())},originalSha256=data.sha(before.encode()),
        replacementCount=1,allOtherSourceBytesPreserved=True,metadataNegativeVectors=3,
        expectedUuidWhenDifferent='00000000-0000-0001-0000-00000000005a',
        expectedUuidWhenSame='00000000-0000-0002-0000-00000000005b',
        independentBasis='TEST_LITERAL_SUPPLIER_SECOND_EVENT_VALUE_NOT_PRODUCT_GETTER',
        productTestsExecuted=0,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
