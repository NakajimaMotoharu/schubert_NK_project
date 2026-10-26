"""Preserve one existing report compiler failure, without replaying any process."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def main():
    invocation = capture(Path(__file__))
    work = data.ROOT.parent/'pgpt-runs/PG379/pg10134-uid-oracle-post-v1'
    out = data.BASE/'PG10133-uid-failed-report-receipt-v1'
    assert not out.exists()
    receipt = work/'compile-report-exit.safe.json'
    value = data.read_checked(receipt,data.sha(receipt.read_bytes()))
    assert value['actualExit'] == 1 and not value['timedOut']
    assert 'UidOracleCoverageMeasure.java' in str(value['command'])
    assert value['stderrSha256'] == '42fe504cef9213b66a20c63ce4d2308c39000baa52467d7c238cf0fae4227552'
    helper = data.ROOT/'tools/quality/architecture/UidOracleCoverageMeasure.java'
    assert 'analyzeAll(testBytes' in helper.read_text()
    verify(invocation)
    out.mkdir()
    (out/receipt.name).write_bytes(receipt.read_bytes())
    data.write(out/'manifest.json',dict(actualExit=0,source='d17f122d2026b804be626bf7a3b76912923bd240',
        invocation=invocation,originalStageExit=1,receiptSha256=data.sha(receipt.read_bytes()),
        originalHelperSha256=data.sha(helper.read_bytes()),productTestsExecuted=0,
        originalFailurePreserved=True,externalActions=0,newAccepted=0,formalUpdated=False))
    print(data.sha((out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
