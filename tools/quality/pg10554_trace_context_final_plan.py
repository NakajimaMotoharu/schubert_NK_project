"""Two independent assertion blocks and one same-value attribute suffix only."""
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10548_trace_context_plan import BASE, P, BLOCKS, tokens

OUT = data.BASE/'PG10554-trace-context-final-plan-v1'
NAME = 'FIXTURE_REQUEST_ID_ATTRIBUTE_SUFFIX'


def remove_once(values,needle):
    starts = [i for i in range(len(values)-len(needle)+1) if values[i:i+len(needle)] == needle]
    if len(starts) != 1:
        raise ValueError('one exact original contract block required')
    i = starts[0]
    return values[:i]+values[i+len(needle):]


def validate(before,after):
    values = tokens(after)
    values = remove_once(values,tokens('private static final String '+NAME+' = ".requestId";'))
    if values.count(NAME) != 4:
        raise ValueError('four same-value suffix references required')
    values = ['".requestId"' if value == NAME else value for value in values]
    for block in BLOCKS:
        values = remove_once(values,tokens(block))
    if values != tokens(before):
        raise ValueError('all previous assertions, literals and other tokens preserved')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10552-trace-context-compile-v1/manifest.json',
        'a1fc9281a481ed7cf7ff3f23ee54cae6da29910fba082562290624d12d1c2aa7')
    assert normal['source'] == 'ce6070c2d0ccef9c734372775f4ab88240711712' and normal['actualExit'] == normal['testsExecuted'] == 0
    before = subprocess.check_output(['git','show',BASE+':'+P],cwd=data.ROOT).decode()
    after = (data.ROOT/P).read_text()
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p != P)
    validate(before,after)
    damaged = [after.replace('= ".requestId";','= ".wrongId";',1),
        after.replace('new UUID(0, 3),\n        WebRequestContext.identify','new UUID(0, 4),\n        WebRequestContext.identify'),
        after.replace('web request context is unavailable','unsafe details'),
        after.replace('new UUID(1, 90), first.correlationId()','first.eventId(), first.correlationId()'),
        after.replace('assertEquals(37, annotations);','assertEquals(38, annotations);'),
        after.replace('assertNull(contextFailure.getCause());','')]
    rejected = 0
    for sample in damaged:
        assert sample != after
        try:
            validate(before,sample)
        except ValueError:
            rejected += 1
    assert rejected == 6
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,baseSource=BASE,invocation=invocation,
        intermediateSource=normal['source'],intermediateCompileOnly=True,
        sourceChanges={P:data.sha(after.encode())},originalSha256=data.sha(before.encode()),
        addedBlocks=2,existingMethodsChanged=2,sameValueSuffixConstant=NAME,suffixReferences=4,
        metadataNegativeVectors=6,allOriginalAssertionsAndOtherTokensPreserved=True,
        oldFallbackOraclePreserved=True,productTestsExecuted=0,externalActions=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
