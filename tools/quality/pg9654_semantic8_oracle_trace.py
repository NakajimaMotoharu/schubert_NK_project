"""Static business-semantic oracle links, with scalar-constructor versus validator limits explicit."""
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
import static_oracle_review_binding as binding

ROOT = data.ROOT
BASE = data.BASE
DOCS = ROOT / 'evidence/01_PT/018_NK-OPS-001'
OUT = BASE / 'PG9654-semantic8-oracle-trace-v1'


def extra():
    normal = data.read_checked(BASE / data.PINS['normal'][0] / 'manifest.json', data.PINS['normal'][1])
    path = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/PayloadTypeCatalogTest.java'
    digest = normal['begin']['inputHashes'][path]
    assert data.sha((ROOT / path).read_bytes()) == data.sha((data.NORMAL / path).read_bytes()) == digest
    prior = data.read_checked(ROOT / 'evidence/01_PT/001_NK-PRO-001/evidence/provisional/PG3284-canonical-acceptance/canonical-fixtures.json',
        '0e9a0c22816212b1a019e904f7ba46a67980b51490768efedf4a9d2d2817b3cd')
    canonical = '8b91944df5820535e23ba2469740f1c0aa94c447'
    assert subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip() == canonical
    hashes = {p: h for p, h in prior['canonicalHashes'].items() if any('/' + str(n) + '_' in p for n in (234, 235, 236))}
    hashes['documents/300_SS/320_メッセージング/322_固定長電文codec実装設計.md'] = 'f6dcecf979d9dbac0338aae079d5730f97ba53afaa3dd46db3e20ef49b21618d'
    for name, expected in hashes.items():
        assert data.sha(subprocess.check_output(['git', 'show', canonical + ':' + name], cwd=ROOT)) == expected
    assert max(1, (0 + 100 - 1) // 100) == 1 and max(1, (101 + 100 - 1) // 100) == 2
    assert (2 - 1) * 100 + 1 == min(2 * 100, 101) == 101
    assert (999_999 - 1) * 100 + 1 == 99_999_801 and 999_999 * 100 == 99_999_900
    assert 4_800 * 10_000 == 48_000_000 and 1 + 2 + 1 == 4
    return dict(fixtureSourcePath=path, fixtureSourceSha256=digest, canonicalCommit=canonical,
        canonicalHashes=hashes, independentArithmeticOnly=True, actualValidatorExecuted=False,
        namedConstructorVsValidatorCaseAttributionUnproved=True, dedicatedPaginationVectorsPlannedNotExecuted=True)


if __name__ == '__main__':
    spec = DOCS / '1966_G13Semantic8_業務条件oracle対応仕様.md'
    review = DOCS / '1967_G13Semantic8_業務条件意味対応表.md'
    mains = ['src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/' + name + '.java'
        for name in ('PayloadSemanticValidator', 'PayloadTypeCatalog', 'TypedPayloadValues')]
    value, digest = binding.run(Path(__file__), OUT,
        (spec, 'dd9a5473fe5cd6fa3b6f966fc60f5c3f1354f5559f631ef2aeddf600790b64bd'),
        (review, '77a98bd2edaa86a851c2c5da15be3cd8c604150390b621b4d115eb0ebb331375'),
        {'PT-PRO-002-': ('evidence/01_PT/002_NK-PRO-002/001_NK-PRO-002_単体テスト仕様書.md',
            '210282dee66ff779a910012781910b3253591da96d23449c4e8d6922a643d59e')},
        dict(PayloadSemanticValidatorTest=8), mains, extra)
    print(json.dumps({key: value[key] for key in ('actualExit', 'methods', 'existingFamilies', 'methodFamilyRelations', 'productTestsExecuted')}))
    print('manifestSha256=' + digest)
