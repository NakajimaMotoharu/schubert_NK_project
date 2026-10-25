"""Bind seven reviewed methods and source literals to existing independent fixtures; no PT."""
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
BASE = data.BASE
OUT = BASE / 'PG9628-layout7-oracle-trace-v2'
DOCS = ROOT / 'evidence/01_PT/018_NK-OPS-001'
REVIEW = DOCS / '1956_G13LayoutCatalog7_独立期待値意味対応表.md'
ORACLE = ROOT / 'evidence/01_PT/001_NK-PRO-001/001_NK-PRO-001_単体テスト仕様書.md'
PRIOR = ROOT / 'evidence/01_PT/001_NK-PRO-001/evidence/provisional/PG3284-canonical-acceptance/canonical-fixtures.json'
PRIOR_SHA = '0e9a0c22816212b1a019e904f7ba46a67980b51490768efedf4a9d2d2817b3cd'
CANON = '8b91944df5820535e23ba2469740f1c0aa94c447'
PACKAGE = 'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/'


def content_rows(raw):
    return [line for line in raw.splitlines() if line and not line.startswith('#')]


def registry_literals(source):
    block = source.split('private static List<LayoutDefinition> standardDefinitions() {', 1)[1]
    block = block.split('return List.of(', 1)[1].split(');', 1)[0]
    pattern = re.compile(r'd\(\s*"([A-Z0-9]{8})",\s*MessageKind\.(REQUEST|RESPONSE|EVENT),\s*'
                         r'InteractionKind\.(SYNCHRONOUS|ASYNC_ACCEPTANCE|INTERNAL),\s*'
                         r'([0-9_]+),\s*([0-9_]+),\s*([0-9_]+),\s*([0-9_]+)\s*\)')
    matches = list(pattern.finditer(block))
    assert not re.sub(r'[\s,]', '', pattern.sub('', block)), 'unparsed registry declaration'
    kinds = dict(REQUEST='Q', RESPONSE='S', EVENT='E')
    interactions = dict(SYNCHRONOUS='S', ASYNC_ACCEPTANCE='A', INTERNAL='I')
    result = []
    for match in matches:
        identifier, kind, interaction, *numbers = match.groups()
        values = [int(number.replace('_', '')) for number in numbers]
        assert 256 + values[0] + values[1] * values[2] == values[3]
        result.append('\t'.join([identifier, kinds[kind], interactions[interaction], *map(str, values)]))
    return result


def field_literals(source):
    body = source.split('CATALOG_TSV =', 1)[1].split('"""', 2)[1]
    rows = []
    for raw in body.splitlines():
        text = raw.strip()
        if not text:
            continue
        assert not re.search(r'\\(?!t)', text), 'unsupported Java escape'
        rows.append(text.replace('\\t', '\t'))
    return rows


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior = data.read_checked(PRIOR, PRIOR_SHA)
    assert prior['actualExit'] == 0 and prior['expectedGeneratedFromProduction'] is False
    assert subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip() == CANON
    for path, digest in prior['canonicalHashes'].items():
        assert data.sha(subprocess.check_output(['git', 'show', CANON + ':' + path], cwd=ROOT)) == digest
    normal = data.read_checked(BASE / 'PG9246-web-life-lock-six-compile-v1/manifest.json', data.PINS['normal'][1])
    hashes = {}
    for path, digest in prior['fixtureHashes'].items():
        assert data.sha((ROOT / path).read_bytes()) == data.sha((data.NORMAL / path).read_bytes()) == digest
        hashes[path] = digest
    method_manifest = data.read_checked(BASE / 'PG9592-current-test-method-post-v1/manifest.json',
        'd73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    methods = data.read_checked(BASE / 'PG9592-current-test-method-post-v1/method-declaration-bindings.json', method_manifest['bindingsSha256'])
    oracle_lines = ORACLE.read_text().splitlines()
    records = []
    for number, line in enumerate(REVIEW.read_text().splitlines(), 1):
        if not line.startswith(('| LayoutMetadataTest |', '| LayoutFieldCatalogTest |')):
            continue
        kind, name, ids, basis, limit = [cell.strip() for cell in line.split('|')[1:-1]]
        found = [row for row in methods if row['className'].rpartition('.')[2] == kind and row['method'] == name]
        assert len(found) == 1
        method = found[0]
        assert method['compiledDescriptor'] == '()V'
        references = []
        for identifier in ids.split(', '):
            lines = [(i, text) for i, text in enumerate(oracle_lines, 1) if text.startswith('| ' + identifier + ' |')]
            assert len(lines) == 1
            at, text = lines[0]
            references.append(dict(testId=identifier, line=at, rowSha256=data.sha(text.encode())))
        hashes[method['path']] = method['sourceSha256']
        records.append(dict(method=method, reviewLine=number, reviewRowSha256=data.sha(line.encode()),
            oracleReferences=references, independentBasis=basis, limits=limit, productExecuted=False))
    assert len(records) == 7 and len({row['method']['methodDeclarationKey'] for row in records}) == 7
    for name in ('LayoutRegistry', 'LayoutDefinition', 'LayoutId', 'FieldDefinition', 'LayoutFields', 'LayoutFieldCatalog'):
        path = PACKAGE + name + '.java'
        hashes[path] = normal['begin']['inputHashes'][path]
    for path, digest in hashes.items():
        assert normal['begin']['inputHashes'][path] == data.sha((ROOT / path).read_bytes()) == data.sha((data.NORMAL / path).read_bytes()) == digest
    layout_expected = content_rows((ROOT / next(p for p in hashes if p.endswith('layouts-ui233.tsv'))).read_text())
    field_expected = content_rows((ROOT / next(p for p in hashes if p.endswith('fields-ui234-236.tsv'))).read_text())
    assert registry_literals((ROOT / (PACKAGE + 'LayoutRegistry.java')).read_text()) == layout_expected
    assert field_literals((ROOT / (PACKAGE + 'LayoutFieldCatalog.java')).read_text()) == field_expected
    assert len(layout_expected) == 64 and len(field_expected) == 389
    assert 256 + 8 + 10 * 0 == 264 and 256 + 8 + 10 == 274 and 256 + 8 + 20 == 284
    assert subprocess.check_output(['git', 'diff', '--name-only', data.SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=ROOT) == b''
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'method-oracle-review.json', records)
    result = dict(actualExit=0, source=data.SOURCE, timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(), invocation=invocation,
        reviewSha256=data.sha(REVIEW.read_bytes()), specSha256=data.sha((DOCS / '1955_G13LayoutCatalog7_独立fixture意味対応仕様.md').read_bytes()),
        oraclePath=str(ORACLE.relative_to(ROOT)), oracleSha256=data.sha(ORACLE.read_bytes()), priorFixtureProofSha256=PRIOR_SHA,
        reusedPureFixtureProofOnly=True, oldSourceQualifiedOrDynamicTransferred=False, canonicalCommit=CANON,
        canonicalHashes=prior['canonicalHashes'], sourceHashes=hashes, methodsReviewed=7,
        methodOracleReviewSha256=data.sha((OUT / 'method-oracle-review.json').read_bytes()),
        existingFamilies=6, methodFamilyRelations=sum(len(row['oracleReferences']) for row in records),
        currentRegistryLiteralTuples=64, currentFieldLiteralRows=389, productTestsExecuted=0,
        newTestIds=0, newMain=0, coverage=None, newAccepted=0, formalUpdated=False, effortPercent=None,
        wholeG13Accepted=False, whole451Accepted=False, productionParserOrInitializerExecuted=False)
    assert result['methodFamilyRelations'] == 11
    data.write(OUT / 'manifest.json', result)
    print(json.dumps(dict(actualExit=0, methods=7, registryLiterals=64, fieldLiterals=389, productTestsExecuted=0)))
    print('manifestSha256=' + data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
