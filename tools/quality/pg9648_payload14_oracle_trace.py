"""Current payload oracle links plus byte-identical prior pure golden proof; no old PT transfer."""
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
import static_oracle_review_binding as binding

ROOT = data.ROOT
BASE = data.BASE
OUT = BASE / 'PG9648-payload14-oracle-trace-v1'
DOCS = ROOT / 'evidence/01_PT/018_NK-OPS-001'


def extra():
    old = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG3292-canonical-golden/manifest.json'
    digest = 'd0fed8ce04f79dddde1537397f43dd984f67b7d2ef911db6d701da1746754f50'
    prior = data.read_checked(old, digest)
    assert prior['actualExit'] == 0 and not prior['expectedGeneratedFromProduction'] and not prior['businessSemanticValidityClaimed']
    assert prior['layouts'] == 64 and prior['responseErrors'] == 31 and prior['digestChecks'] == 287 and prior['notApplicableErrorCells'] == 33
    canonical = '8b91944df5820535e23ba2469740f1c0aa94c447'
    assert subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip() == canonical
    for path, expected in prior['canonicalHashes'].items():
        assert data.sha(subprocess.check_output(['git', 'show', canonical + ':' + path], cwd=ROOT)) == expected
    path = 'src/schubert-nk-protocol/src/test/resources/protocol/payload-golden-ui234-236.tsv'
    assert data.sha((ROOT / path).read_bytes()) == data.sha((data.NORMAL / path).read_bytes()) == prior['goldenFixtureSha256']
    fixture = (ROOT / path).read_text()
    assert 'fields-ui234-236.tsv-sha256=b07bd90705a4761ebcc97b859bd495dadaf26501fcee3b60c4edd72474a4811b' in fixture
    records = [line.split('\t') for line in fixture.splitlines() if line and not line.startswith('#')]
    assert len(records) == len({row[0] for row in records}) == 64 and all(len(row) == 6 for row in records)
    assert sum(row[-1] != '-' for row in records) == 31
    test_path = ROOT / 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/AuthenticationErrorProfileTest.java'
    helper = test_path.read_text().split('private static byte[] loginGolden(', 1)[1]
    assert 'new byte[432]' in helper and '"%06d000", retry' in helper
    assert 'System.arraycopy(digits, 0, bytes, 167, 9);' in helper and 'System.arraycopy(text, 0, bytes, 176, text.length);' in helper
    assert 167 + 6 == 173 and 173 + 3 == 176 and 176 + 256 == 432 and 85 * 3 + 1 == 256
    return dict(reusedPureGoldenManifestPath=str(old.relative_to(ROOT)), reusedPureGoldenManifestSha256=digest,
        canonicalCommit=canonical, canonicalHashes=prior['canonicalHashes'], goldenFixtureSha256=prior['goldenFixtureSha256'],
        reusedGoldenDigestChecks=287, reusedGoldenLayouts=64, reusedGoldenResponseErrors=31,
        oldSourceQualifiedOrDynamicTransferred=False, oldGoldenToolReexecuted=False,
        loginGoldenOffsets=[167, 173, 176], loginGoldenBytes=432, boundaryMessageBytes=256,
        staticBindingNotDynamicPt=True)


if __name__ == '__main__':
    mains = ['src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/' + package + '/' + name + '.java'
        for package, name in [('codec', 'PayloadCodec'), ('codec', 'FieldCodec'), ('layout', 'FieldValue'),
            ('layout', 'FieldValueSet'), ('layout', 'PayloadValues'), ('layout', 'LayoutFieldCatalog'), ('header', 'ResultCode')]]
    value, digest = binding.run(Path(__file__), OUT,
        (DOCS / '1963_G13Payload14_独立golden・profile対応仕様.md', 'fe850155cfc736b0e5708a3a9e513cbe35362cc4b2aaef5eb16357683cc33501'),
        (DOCS / '1964_G13Payload14_独立期待値意味対応表.md', 'a4f561a4ae449c19b1ba23d9fed7d790f7f286542061b39bbb761f4258b955d6'),
        {'PT-PRO-002-': ('evidence/01_PT/002_NK-PRO-002/001_NK-PRO-002_単体テスト仕様書.md',
            '210282dee66ff779a910012781910b3253591da96d23449c4e8d6922a643d59e'),
         'PT-CODEC-AUTHERR-': ('evidence/01_PT/002_NK-PRO-002/001_NK-PRO-002_単体テスト仕様書.md',
            '210282dee66ff779a910012781910b3253591da96d23449c4e8d6922a643d59e')},
        dict(PayloadCodecTest=8, PayloadGoldenVectorTest=3, AuthenticationErrorProfileTest=3), mains, extra)
    print(json.dumps({key: value[key] for key in ('actualExit', 'methods', 'existingFamilies', 'methodFamilyRelations', 'productTestsExecuted')}))
    print('manifestSha256=' + digest)
