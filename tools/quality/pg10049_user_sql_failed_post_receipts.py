"""Export only the known host report-tool failure receipts; never re-execute a stage."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def main():
    invocation = capture(Path(__file__))
    source = data.ROOT.parent/'pgpt-runs/PG379/pg10046-user-sql-post-v1'
    out = data.BASE/'PG10049-user-sql-failed-post-receipts-v1'
    assert not out.exists()
    names = ['compile-report-exit.safe.json','measure-complete-codec-exit.safe.json']
    receipts = {n:data.read_checked(source/n,data.sha((source/n).read_bytes())) for n in names}
    assert [receipts[n]['actualExit'] for n in names] == [0,1]
    assert not any(v['timedOut'] for v in receipts.values())
    assert all('UserSqlInterfaceCoverageMeasure' in str(receipts[n]['command']) for n in names)
    verify(invocation)
    out.mkdir()
    for name in names:
        (out/name).write_bytes((source/name).read_bytes())
    data.write(out/'manifest.json',dict(actualExit=0,source='dac963b29f62c0da68ca9d71f61db986a02d28a1',
        invocation=invocation,originalReportExit=1,originalStageExit=[0,1],
        receiptHashes={n:data.sha((out/n).read_bytes()) for n in names},
        originalHelperSha256=data.sha((data.ROOT/'tools/quality/architecture/UserSqlInterfaceCoverageMeasure.java').read_bytes()),
        sourceDirectory=str(source),productTestsExecuted=0,externalActions=0,newAccepted=0,formalUpdated=False))
    print(data.sha((out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
