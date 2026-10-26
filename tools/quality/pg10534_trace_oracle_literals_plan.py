"""One oracle replacement plus three independently fixed Test-local literal constants."""
from pathlib import Path
import re
import subprocess
from public_java_digest_provenance import LEX
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10530_trace_fallback_plan import BASE, P, OLD, NEW

OUT = data.BASE/'PG10534-trace-oracle-literals-plan-v1'
VALUES = {'FIXTURE_LOGIN_ROUTE':'"/login"','FIXTURE_ERROR_ROUTE':'"/error"',
          'FIXTURE_ATTRIBUTE_FAILURE':'"synthetic-private-attribute-canary"'}


def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def validate(before,after):
    restored = after
    for name,literal in VALUES.items():
        pattern = r'\s*private static final String '+name+r'\s*=\s*'+re.escape(literal)+r';'
        restored,count = re.subn(pattern,'',restored)
        if count != 1:
            raise ValueError('exact independent Test-local literal required')
        if tokens(restored).count(name) != 4:
            raise ValueError('all four original references required')
        restored = re.sub(r'\b'+name+r'\b',literal,restored)
    if tokens(restored) != tokens(before.replace(OLD,NEW,1)) or before.count(OLD) != 1:
        raise ValueError('only oracle replacement and same-value constants allowed')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10508-anm-type-name-compile-v1/manifest.json',
        'bc2c2ee9ff267ab6ea56f33df42b0272636cd928c23cdb3cc9b33bf1db3773c5')
    before = subprocess.check_output(['git','show',BASE+':'+P],cwd=data.ROOT).decode()
    after = (data.ROOT/P).read_text()
    assert data.sha(before.encode()) == normal['begin']['inputHashes'][P]
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p != P)
    validate(before,after)
    damaged = [after.replace('new UUID(1, 90), first.correlationId()',
                            'first.eventId(), first.correlationId()'),
               after.replace('new UUID(1, 90), first.correlationId()',
                            'new UUID(1, 91), first.correlationId()'),
               after.replace('var first = trace(new MockHttpServletRequest(), 90);',
                             'var first = trace(new MockHttpServletRequest(), 89);')]
    damaged += [after.replace('= '+literal+';','= "WRONG";',1) for literal in VALUES.values()]
    rejected = 0
    for sample in damaged:
        try:
            validate(before,sample)
        except ValueError:
            rejected += 1
    assert rejected == 6
    methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(',after)
    assert len(methods) == len(set(methods)) == 10
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,baseSource=BASE,invocation=invocation,
        sourceChanges={P:data.sha(after.encode())},originalSha256=data.sha(before.encode()),
        fixedFallbackReplacements=1,sameValueConstants=VALUES,literalReferences=12,
        allOtherSourceTokensPreserved=True,metadataNegativeVectors=6,exactMethods=methods,
        expectedUuidWhenDifferent='00000000-0000-0001-0000-00000000005a',
        expectedUuidWhenSame='00000000-0000-0002-0000-00000000005b',
        productTestsExecuted=0,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
