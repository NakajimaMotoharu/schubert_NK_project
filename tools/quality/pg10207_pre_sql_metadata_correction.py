"""Preserve original result/tool, correct only additional-ID metadata without replay."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10207-pre-sql-metadata-correction-v1'
    assert not out.exists()
    original = data.read_checked(data.BASE/'PG10206-pre-sql-boundary-host-v1/manifest.json',
        '6ae5f9a5f80539efa065ccf388c8b719c5d4bcc748dc12de57bf9a94fce6837e')
    prepared = data.read_checked(data.BASE/'PG10204-pre-sql-boundary-preflight-v1/manifest.json',
        '2ff834c4411928d402f0cdc1f67aa579edca4d6bf6566cd256c82623df55502c')
    cases = data.read_checked(data.BASE/'PG10204-pre-sql-boundary-preflight-v1/cases.json',prepared['casesSha256'])
    source = data.ROOT/'tools/quality/pg10206_pre_sql_boundary_host.py'
    fixed = source.read_bytes()
    before = fixed.replace(b'newTestIds=len({r["testId"] for r in cases})',b'newTestIds=4')
    assert before != fixed and data.sha(before) == original['begin']['invocation']['entrypointSha256']
    assert original['actualExit'] == 0 and original['newTestIds'] == 4
    assert len(cases) == len({r['testId'] for r in cases}) == len(original['cases']) == 13
    assert {(r['className'],r['method']) for r in cases} == {(r['classname'],r['name']) for r in original['cases']}
    assert len(original['xmlHashes']) == 3 and not any(r['nonPass'] for r in original['cases'])
    verify(invocation)
    out.mkdir()
    (out/'qualified-original-tool.py').write_bytes(before)
    data.write(out/'manifest.json',dict(actualExit=0,source=original['source'],invocation=invocation,
        originalHostManifestSha256='6ae5f9a5f80539efa065ccf388c8b719c5d4bcc748dc12de57bf9a94fce6837e',
        originalToolSha256=data.sha(before),futureToolSha256=data.sha(fixed),originalNewTestIds=4,
        correctedNewTestIds=len(cases),testIds=sorted(r['testId'] for r in cases),productTestsExecuted=0,
        originalManifestModified=False,productReplay=False,formalUpdated=False,newAccepted=0,bug='BUG-1804',ykt='YKT-1555'))
    print(data.sha((out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
