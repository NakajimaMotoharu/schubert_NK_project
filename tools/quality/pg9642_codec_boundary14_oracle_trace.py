"""Static 14-method oracle references and independent UI Scenario golden; never target execution."""
from collections import Counter
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
BASE = data.BASE
OUT = BASE / 'PG9642-codec-boundary14-oracle-trace-v1'
REVIEW = ROOT / 'evidence/01_PT/018_NK-OPS-001/1961_G13CodecBoundary14_独立期待値意味対応表.md'
REVIEW_SHA = '63ab0cce9fe8c84abc18fa9457bb7bbb9623c414182c92a8ee49b49f7a82e4bb'
SPEC = ROOT / 'evidence/01_PT/018_NK-OPS-001/1960_G13CodecBoundary14_独立oracle対応仕様.md'
SPEC_SHA = 'ab1d826be8386b9d87ea1bb6585316a7d46764895f92017282440ab287545a95'
ORACLES = {
    'PT-PRO-002-': ('evidence/01_PT/002_NK-PRO-002/001_NK-PRO-002_単体テスト仕様書.md',
        '210282dee66ff779a910012781910b3253591da96d23449c4e8d6922a643d59e'),
    'PT-SCN-008-': ('evidence/01_PT/008_NK-SCN-001/001_NK-SCN-001_単体テスト仕様書.md',
        'de74fa1ce7398ea1eb4177a96fd6fe3f7360974941dbb92d120662129f6cea50')}
CANON = '8b91944df5820535e23ba2469740f1c0aa94c447'
UI234 = 'documents/200_UI/230_インターフェース/234_認証・検索・シナリオ電文仕様.md'
UI234_SHA = '8f9abda07bc93262c264eae723c74245165bf0806b273b0d007e9fa46f37fa46'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists() and data.sha(REVIEW.read_bytes()) == REVIEW_SHA and data.sha(SPEC.read_bytes()) == SPEC_SHA
    normal = data.read_checked(BASE / data.PINS['normal'][0] / 'manifest.json', data.PINS['normal'][1])
    mm = data.read_checked(BASE / 'PG9592-current-test-method-post-v1/manifest.json',
        'd73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    methods = data.read_checked(BASE / 'PG9592-current-test-method-post-v1/method-declaration-bindings.json', mm['bindingsSha256'])
    oracle_text = {prefix: (ROOT / path).read_text().splitlines() for prefix, (path, _) in ORACLES.items()}
    for path, digest in ORACLES.values():
        assert data.sha((ROOT / path).read_bytes()) == digest
    rows = []
    hashes = {}
    for number, line in enumerate(REVIEW.read_text().splitlines(), 1):
        if not line.startswith(('| FieldCodecTest |', '| MessageCodecTest |', '| ScenarioRecordEncodingTest |')):
            continue
        kind, name, identifiers, basis, limits = [cell.strip() for cell in line.split('|')[1:-1]]
        found = [m for m in methods if m['className'].rpartition('.')[2] == kind and m['method'] == name]
        assert len(found) == 1
        method = found[0]
        assert method['compiledDescriptor'] == '()V'
        hashes[method['path']] = method['sourceSha256']
        references = []
        for identifier in identifiers.split(', '):
            prefix = next(p for p in ORACLES if identifier.startswith(p))
            hits = [(i, text) for i, text in enumerate(oracle_text[prefix], 1)
                if text.startswith('| ' + identifier + ' |') or text.startswith(identifier + '（')]
            assert len(hits) == 1
            at, text = hits[0]
            path, digest = ORACLES[prefix]
            references.append(dict(testId=identifier, path=path, sha256=digest, line=at, rowSha256=data.sha(text.encode())))
        rows.append(dict(method=method, reviewLine=number, reviewRowSha256=data.sha(line.encode()),
            oracleReferences=references, independentBasis=basis, limits=limits, productExecuted=False, oldDynamicTransferred=False))
    assert len(rows) == len({row['method']['methodDeclarationKey'] for row in rows}) == 14
    assert Counter(row['method']['className'].rpartition('.')[2] for row in rows) == Counter(FieldCodecTest=5, MessageCodecTest=6, ScenarioRecordEncodingTest=3)
    for package, names in [('codec', ('FieldCodec', 'HeaderCodec', 'FixedWidthEncoder', 'FixedWidthDecoder', 'ProtocolValidator',
            'TransportMetadata', 'ExpectedRoute', 'TransportBodyType', 'PayloadCodec')), ('layout', ('FixedPayload', 'WireMessage'))]:
        for name in names:
            path = 'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/' + package + '/' + name + '.java'
            hashes[path] = normal['begin']['inputHashes'][path]
    for path, digest in hashes.items():
        assert normal['begin']['inputHashes'][path] == data.sha((ROOT / path).read_bytes()) == data.sha((data.NORMAL / path).read_bytes()) == digest
    assert subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip() == CANON
    ui_raw = subprocess.check_output(['git', 'show', CANON + ':' + UI234], cwd=ROOT)
    assert data.sha(ui_raw) == UI234_SHA
    section = ui_raw.decode().split('### 10.3 `SCNRSP01` record（4,800 byte）', 1)[1].split('Record順', 1)[0]
    fields = []
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        if len(cells) == 6 and cells[1].replace(',', '').isdigit():
            fields.append((cells[0], int(cells[1].replace(',', '')), int(cells[2].replace(',', ''))))
    assert len(fields) == 10 and sum(length for _, _, length in fields) == 4800
    values = {'Entry ID': b'000000000071', 'Entry sequence': b'000001', 'Line番号': b'00000042',
        'Entry type': b'narration', '本文': '本文'.encode('utf-8'), 'Audio sequence': b'000'}
    expected = bytearray()
    for name, start, length in fields:
        assert len(expected) == start - 1
        value = values.get(name, b'')
        assert len(value) <= length
        expected.extend(value.ljust(length, b' '))
    test = next(row['method']['path'] for row in rows if row['method']['className'].endswith('.ScenarioRecordEncodingTest'))
    golden = (ROOT / test).read_text().split('private static byte[] golden() {', 1)[1].split('return expected;', 1)[0]
    assert 'new byte[4800]' in golden and "Arrays.fill(expected, (byte) ' ');" in golden
    built = bytearray(b' ' * 4800)
    assignments = re.findall(r'put\(expected, ([0-9]+), ("[^"\r\n]*")\);', golden)
    assert len(assignments) == 6
    for offset, literal in assignments:
        raw = json.loads(literal).encode('utf-8')
        offset = int(offset)
        assert 0 <= offset <= 4800 - len(raw)
        built[offset:offset + len(raw)] = raw
    assert expected == built and 256 + 9 + 272 == 537
    assert 'e\u0301'.encode('utf-8') == b'e\xcc\x81' and 'é'.encode('utf-8') == b'\xc3\xa9'
    assert len('あ'.encode('utf-8')) == 3 and len('😀'.encode('utf-8')) == 4
    assert subprocess.check_output(['git', 'diff', '--name-only', data.SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=ROOT) == b''
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'method-oracle-review.json', rows)
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=data.SOURCE, timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
        invocation=invocation, specSha256=SPEC_SHA, reviewSha256=REVIEW_SHA, sourceHashes=hashes,
        methodOracleReviewSha256=data.sha((OUT / 'method-oracle-review.json').read_bytes()), methods=14,
        existingFamilies=len({ref['testId'] for row in rows for ref in row['oracleReferences']}),
        methodFamilyRelations=sum(len(row['oracleReferences']) for row in rows), canonicalCommit=CANON, canonicalUiSha256=UI234_SHA,
        scenarioFields=fields, staticScenarioGoldenSha256=data.sha(bytes(expected)), staticScenarioGoldenBytes=4800,
        testGoldenAssignments=6, reviewedMainSourceFiles=11, semanticReviewIsParentRecord=True,
        targetClassOrCodecExecuted=False, productTestsExecuted=0, newAccepted=0, coverage=None,
        newTestIds=0, newMain=0, formalUpdated=False, effortPercent=None, whole451Accepted=False, wholeG13Accepted=False))
    print(json.dumps(dict(actualExit=0, methods=14, scenarioGoldenBytes=4800, productTestsExecuted=0)))
    print('manifestSha256=' + data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
