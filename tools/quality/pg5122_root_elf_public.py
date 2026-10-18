"""Independent original XML/input/physical delta checks; allowlisted evidence only, no PT replay."""
import datetime
import json
import os
import platform
import pg4852_selected_public_evidence as evidence
import pg5120_root_elf_selected as selected

ROOT = selected.ROOT
W = ROOT.parent / 'pgpt-runs/PG379'
RUN = W / 'pg5120-root-elf-green-v3'
PUBLIC = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5120-root-elf-green-v3'
NAMES = (
    'fixedDigestFactoryIsCalledOnceAndBorrowedChannelStaysOpen',
    'unavailableAlgorithmIsRedactedAndDoesNotReadOrClose',
    'unexpectedRuntimeAndErrorPreserveIdentityWithoutIo',
    'nullContractsFailBeforeInputReads',
    'oversizedReadReportIsRejectedAndBufferIsWiped',
    'exactBufferBoundaryAndSplitHeaderKeepLiteralDigest',
    'readFailurePreservesIdentityAndWipesWithoutClose',
    'exactMaximumElfHasIndependentFixedHash',
)


def main():
    result = json.loads((RUN / 'manifest.safe.json').read_bytes())
    begin = json.loads((RUN / 'begin.safe.json').read_bytes())
    if not (type(result['actualExit']) is int and result['actualExit'] == 0
            and result['phaseExits'] == [0, 0] and not result['reasons']
            and result['tests'] == 28 and result['suites'] == 4
            and result['sourceSnapshot'] == begin['sourceSnapshot']
            and result['deployedSource'] == selected.BASE and result['formalAccepted'] is False):
        raise ValueError('actual original 28/4 green required')
    for name, digest in begin['inputs'].items():
        if selected.sha(RUN / 'source' / name) != digest:
            raise ValueError('original fixed snapshot input changed')
    if selected.main_delta(RUN / 'source') != result['mainDelta']:
        raise ValueError('actual compiled Main delta changed')
    records = []; suites = []
    for name, digest in result['xmlSha256'].items():
        module = selected.SUITES[name]
        path = RUN / 'source' / ('src/schubert-nk-' + module + '/target/surefire-reports/TEST-' + name + '.xml')
        raw = path.read_bytes()
        if evidence.sha(raw) != digest: raise ValueError('original XML hash')
        cases = evidence.cases(raw, name)
        if sorted(c['method'] for c in cases) != begin['expectedMethods'][name]:
            raise ValueError('literal original case inventory')
        for case in cases:
            if name.endswith('.RootElfDigestPortTest'):
                if case['method'] not in NAMES: raise ValueError('unknown new case')
                case.update(testId='PT-ROOTELF-SSC306-' + str(NAMES.index(case['method']) + 1).zfill(3),
                            newIndependentCase=True)
        records += cases; suites.append({'class': name, 'module': module, 'originalXmlSha256': digest, 'tests': len(cases)})
    if len(records) != 28 or sum(r['newIndependentCase'] for r in records) != 8:
        raise ValueError('exact eight new and twenty related cases')
    failures = []
    for slot, description in (
        ('pg5120-root-elf-red-v1', 'BUG1411 root-reactor format failure; PT0'),
        ('pg5120-root-elf-red-v2', 'unimplemented-overload TDD RED; dependencies14 only'),
        ('pg5120-root-elf-green-v2', 'BUG1412 test-oracle mismatch; failed1/28, not acceptance'),
    ):
        old = json.loads((W / slot / 'manifest.safe.json').read_bytes())
        if type(old['actualExit']) is not int or old['actualExit'] != 1:
            raise ValueError('original failure history must remain failure')
        failures.append({'slot': slot, 'description': description, 'actualExit': 1,
                         'phaseExits': old['phaseExits'], 'tests': old['tests'], 'suites': old['suites'],
                         'manifestSha256': selected.sha(W / slot / 'manifest.safe.json'),
                         'logSha256': old['logSha256'], 'successImported': False})
    value = {'kind': 'LIMITED_SELECTED_NOT_FORMAL', 'actualExit': 0, 'tests': 28, 'suites': 4,
             'productionCandidateSource': result['sourceSnapshot'], 'deployedProductionSource': selected.BASE,
             'FESFlakyNotRun': 0, 'newIndependentCases': 8, 'relatedCases': 20,
             'cases': records, 'suiteProofs': suites, 'digestMethodCounters': result['targetCoverage'],
             'freshStaticThreeCompiledModules': result['freshStatic'], 'allSixFormatBeforeAnyPt': True,
             'mainDelta': result['mainDelta'], 'startUTC': result['startUTC'], 'endUTC': result['endUTC'],
             'commands': result['commands'], 'phaseExits': result['phaseExits'],
             'originalBeginSha256': selected.sha(RUN / 'begin.safe.json'),
             'originalManifestSha256': selected.sha(RUN / 'manifest.safe.json'),
             'logSha256': result['logSha256'], 'sourceInputsSha256': evidence.sha(json.dumps(begin['inputs'], sort_keys=True).encode()),
             'configuredToolchain': {'jdk': '25.0.4', 'maven': '3.9.12', 'jacoco': '0.8.15', 'spotbugs': '4.10.4.0', 'formatter': '1.36.1'},
             'hostOsMeasuredAtPublication': platform.platform(), 'failuresPreserved': failures,
             'spec': '1045_Root_ELF固定digest内部port・独立PT仕様.md',
             'bugs': ['BUG1411', 'BUG1412'], 'ykt': ['YKT1175', 'YKT1176'],
             'wholeRegression': False, 'formalAccepted': False, 'acceptedLeafDelta': 0,
             'effortPercent': None, 'oldNativeImported': False, 'newSourceNativeQualified': False,
             'wholeCoverage100': False, 'rawXmlPropertiesOrSecretsExported': False,
             'vmActions': 0, 'mavenReissued': False, 'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    os.umask(0o077); PUBLIC.mkdir(parents=True)
    with (PUBLIC / 'manifest.json').open('x') as output:
        json.dump(value, output, ensure_ascii=False, indent=2); output.write('\n'); output.flush(); os.fsync(output.fileno())
    print(json.dumps({'actualExit': 0, 'tests': 28, 'newIndependentCases': 8,
                      'publicManifest': str((PUBLIC / 'manifest.json').relative_to(ROOT)),
                      'sha256': selected.sha(PUBLIC / 'manifest.json'), 'formalAccepted': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
