"""Credential-specific design bindings supplement generic independent-post references, no new PT."""
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE / 'PG17221-credential-value-design-trace-v1'
PIN = '67425b36190ea32bc9ae6c588d8a0de10393eae56e45962adc0cde1a52b6208a'


def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    post = data.read_checked(data.BASE / 'PG17220-bootstrap-credential-values-twenty-independent-v1/manifest.json', PIN)
    assert post['actualExit'] == 0 and post['source'] == '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
    assert post['tests'] == 20 and post['independentOracleVectors'] == 20
    refs = {}
    for root, numbers in [('documents/300_SS', ('324', '343', '352')),
                          ('documents/200_UI', ('212', '241', '251')),
                          ('documents/100_RD', ('141', '171'))]:
        for number in numbers:
            paths = list((data.ROOT / root).glob('*/' + number + '_*.md'))
            assert len(paths) == 1
            path = paths[0]; relative = str(path.relative_to(data.ROOT)); blob = path.read_bytes()
            assert blob == subprocess.check_output(['git', 'show', 'origin/main:' + relative], cwd=data.ROOT)
            refs[relative] = data.sha(blob)
    source_prefix = 'src/schubert-nk-bootstrap/src/'
    prefix = 'java/dev/codex/schubert/nk/api/maintenance/'
    mappings = []
    all_test_text = ''
    for leaf, ids in [('InspectorDbCredential', [f'PT-DB-INBOX-{v}' for v in range(193, 197)]),
                      ('InspectorAesCredential', [f'PT-DB-INBOX-{v}' for v in range(105, 113)]),
                      ('InspectorCredentialAccess', [f'PT-DB-INBOX-{v}' for v in range(113, 121)])]:
        main = source_prefix + 'main/' + prefix + leaf + '.java'
        test = source_prefix + 'test/' + prefix + leaf + 'Test.java'
        text = (data.ROOT / main).read_text(); test_text = (data.ROOT / test).read_text()
        assert '@NullMarked' in text and 'catch (NullPointerException' not in text
        assert 'QA-046/SSC-049' in text
        assert test_text.count('@Test') == len(ids)
        cases = [v for v in data.read_checked(data.BASE / 'PG17218-bootstrap-credential-values-twenty-post-v1/manifest.json',
                  '558a9b4aceeae4b3541be0cadfe7586e71db7d08ff2fa55470094b4ef0872dbd')['cases']
                 if v['classname'].endswith('.' + leaf + 'Test')]
        assert len(cases) == len(ids)
        mappings.append(dict(main=main, mainSha256=data.sha(text.encode()), test=test,
            testSha256=data.sha(test_text.encode()), testIds=ids, caseMethods=[v['name'] for v in cases],
            module='bootstrap', package='dev.codex.schubert.nk.api.maintenance', modulePackageAliasExplicit=True,
            requirementIds=['DAT-009', 'OPS-009'], designDocuments=sorted(refs), nullContract='API_REJECT_AND_CONSTRUCTOR_INVARIANTS_NO_NPE_NORMALIZATION'))
        all_test_text += test_text
    assert '.requireDatabaseFile(' not in all_test_text
    verify(post['invocation']); verify(invocation); OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=post['source'], invocation=invocation,
        originalIndependentPostSha256=PIN, originMain=subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=data.ROOT, text=True).strip(),
        credentialSpecificApprovedDesignHashes=refs, programMappings=mappings,
        originalGenericDesignReferencesRetained=True, requireDatabaseFileGapExplicit=True,
        specificTraceSupplementIsProductExecution=False, productTestsExecuted=0, newAccepted=0,
        sourceChanged=False, designChanged=False, formalUpdated=False, wholeF03Accepted=False, whole451Accepted=False, effortPercent=None))
    print(data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
