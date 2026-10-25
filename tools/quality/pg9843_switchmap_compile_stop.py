"""Preserve the already terminated static-tool compiler failure; never restart any stage."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SLOT = ROOT.parent / 'pgpt-runs/PG379/pg9842-protocol-switchmap-review-v1'
OUT = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG9843-switchmap-compile-stop-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    begin = data.read_checked(SLOT / 'begin.safe.json',data.sha((SLOT / 'begin.safe.json').read_bytes()))
    exit_path = SLOT / 'compile-static-reader-exit.safe.json'
    receipt = data.read_checked(exit_path,data.sha(exit_path.read_bytes()))
    assert receipt['actualExit'] == 1 and not receipt['timedOut']
    assert not (SLOT / 'map-original-probes-begin.safe.json').exists()
    error = (SLOT / 'compile-static-reader.stderr').read_bytes()
    assert data.sha(error) == receipt['stderrSha256'] and b'AbstractInsnNode cannot be converted to LabelNode' in error
    helper = ROOT / 'tools/quality/architecture/ProtocolSwitchMapApplicabilityReview.java'
    assert data.sha(helper.read_bytes()) == begin['helperSha256']
    verify(invocation)
    OUT.mkdir()
    with (OUT / 'compiler-diagnostic.txt').open('xb') as stream:
        stream.write(error)
    data.write(OUT / 'manifest.json',dict(actualExit=1,source=begin['source'],invocation=invocation,bug='BUG1767',horizontalReview='YKT1518',
        stage='STATIC_REVIEW_TOOL_COMPILE_ERROR_NOT_PRODUCT_TEST',beginSha256=data.sha((SLOT / 'begin.safe.json').read_bytes()),
        compilerReceipt=receipt,originalHelperSha256=begin['helperSha256'],readerStarted=False,productTestsExecuted=0,
        actualExternalOperations=0,originalBytesPreserved=True,newAccepted=0,formalUpdated=False))
    print('preservedCompilerActualExit=1; readerStarted=false; manifestSha256=' + data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
