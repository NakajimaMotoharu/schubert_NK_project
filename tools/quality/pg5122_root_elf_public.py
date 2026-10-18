"""Independent original XML/input/physical delta checks; allowlisted evidence only, no PT replay."""
import argparse
import datetime
import json
import os
import platform
import xml.etree.ElementTree as ET
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
PENDING_NAMES = (
    'pending001ImmediateBothServicesHaveExactObservationOrder',
    'pending002MissingTwiceUsesSameDeadlineAndExactOrder',
    'pending003EqualOrPastDeadlineRejectsBeforeOwner',
    'pending004MissingCannotRestartOrExtendDeadline',
    'pending005FinalDeadlineIsStrictAndAfterOwner',
    'pending006EitherOwnerFailureStopsWithoutLaterObservation',
    'pending007UnknownClockOwnerReadAndPauseFailuresKeepIdentity',
    'pending008WrongChildGenerationStopsBeforeSecondOwner',
    'pending009InterruptedPauseRestoresFlagAndRedactsCause',
    'pending010NullBoundariesDoNotObserveNativeInputs',
    'pending011OnlyMissingLaunchBecomesEmpty',
    'pending012ReadIdentityAndNullContractsStayFailures',
)
GUARD_NAMES = ('guard001SetprivRejectsEveryNonServiceRoleBeforeAnyIo',
               'guard002ObserveRejectsEveryNonServiceRoleBeforeAnyIo',
               'guard003AllNativeEntryNullContractsPrecedeIoAndCallbacks')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--group', choices=('elf', 'pending', 'guards'), default='elf')
    args = parser.parse_args()
    run = RUN if args.group == 'elf' else W / 'pg5124-root-pending-green-v1'
    if args.group == 'guards': run = W / 'pg5126-root-guards-green-v1'
    public = PUBLIC if args.group == 'elf' else PUBLIC.parent / run.name
    required = (28, 4, 8) if args.group == 'elf' else (47, 7, 20)
    if args.group == 'guards': required = (50, 8, 23)
    suite_modules = selected.SUITES if args.group == 'elf' else {**selected.SUITES, **selected.PENDING_SUITES}
    if args.group == 'guards': suite_modules = {**suite_modules, 'dev.codex.schubert.nk.batch.file.RootEntryRejectionTest': 'batch'}
    result = json.loads((run / 'manifest.safe.json').read_bytes())
    begin = json.loads((run / 'begin.safe.json').read_bytes())
    if not (type(result['actualExit']) is int and result['actualExit'] == 0
            and result['phaseExits'] == [0, 0] and not result['reasons']
            and result['tests'] == required[0] and result['suites'] == required[1]
            and result['sourceSnapshot'] == begin['sourceSnapshot']
            and result['deployedSource'] == selected.BASE and result['formalAccepted'] is False):
        raise ValueError('actual original 28/4 green required')
    for name, digest in begin['inputs'].items():
        if selected.sha(run / 'source' / name) != digest:
            raise ValueError('original fixed snapshot input changed')
    if selected.main_delta(run / 'source', 'elf' if args.group == 'elf' else 'pending') != result['mainDelta']:
        raise ValueError('actual compiled Main delta changed')
    # Independent actual XML counter/static re-read, not merely a runner exit-code assertion.
    wanted = {
        'digest(Ljava/nio/channels/SeekableByteChannel;)Ljava/lang/String;',
        'digest(Ljava/nio/channels/SeekableByteChannel;Ldev/codex/schubert/nk/batch/file/RootServiceExecutableAdmission$DigestFactory;)Ljava/lang/String;',
        'lambda$digest$0()Ljava/security/MessageDigest;'}
    if args.group != 'elf':
        wanted |= {
            'awaitLaunch(Ldev/codex/schubert/nk/batch/platform/RootStartupContext$Snapshot;JLdev/codex/schubert/nk/batch/file/RootStartupPending$WaitIo;)V',
            'readLaunch(Ldev/codex/schubert/nk/batch/file/RootStartupPending$LaunchRead;)Ljava/util/Optional;'}
    coverage_path = run / 'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml'
    measured = {}
    for cls in ET.parse(coverage_path).getroot().findall('package/class'):
        if cls.get('name') not in (selected.CLASS, selected.PENDING): continue
        for method in cls.findall('method'):
            key = method.get('name') + method.get('desc')
            if key not in wanted: continue
            if key in measured: raise ValueError('duplicate target method')
            counts = {c.get('type'): {f: int(c.get(f)) for f in ('missed', 'covered')} for c in method.findall('counter')}
            if not {'LINE', 'METHOD'} <= set(counts) or any(v['missed'] or v['covered'] <= 0 for k, v in counts.items()
                                                         if k in ('LINE', 'METHOD', 'BRANCH')):
                raise ValueError('actual target counter gap')
            measured[key] = counts
    if set(measured) != wanted or measured != result['targetCoverage']:
        raise ValueError('independent actual target XML must equal declared measurement')
    static_hashes = {}
    for module in ('storage', 'bootstrap', 'batch'):
        path = run / 'source' / ('src/schubert-nk-' + module + '/target/spotbugsXml.xml')
        if ET.parse(path).getroot().findall('.//BugInstance'): raise ValueError('actual static issue')
        static_hashes[module] = selected.sha(path)
    if result['freshStatic'] != {'storage': 0, 'bootstrap': 0, 'batch': 0}:
        raise ValueError('exact actual three-module static declaration')
    records = []; suites = []
    for name, digest in result['xmlSha256'].items():
        module = suite_modules[name]
        path = run / 'source' / ('src/schubert-nk-' + module + '/target/surefire-reports/TEST-' + name + '.xml')
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
            elif name.endswith('.RootPendingWaitTest'):
                if case['method'] not in PENDING_NAMES: raise ValueError('unknown wait case')
                case.update(testId='PT-ROOTWAIT-SSC307-' + str(PENDING_NAMES.index(case['method']) + 1).zfill(3),
                            newIndependentCase=True)
            elif name.endswith('.RootEntryRejectionTest'):
                if case['method'] not in GUARD_NAMES: raise ValueError('unknown guard case')
                case.update(testId='PT-ROOTGUARD-' + str(GUARD_NAMES.index(case['method']) + 1).zfill(3),
                            newIndependentCase=True)
        records += cases; suites.append({'class': name, 'module': module, 'originalXmlSha256': digest, 'tests': len(cases)})
    if len(records) != required[0] or sum(r['newIndependentCase'] for r in records) != required[2]:
        raise ValueError('exact literal required cases')
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
    value = {'kind': 'LIMITED_SELECTED_NOT_FORMAL', 'actualExit': 0, 'tests': required[0], 'suites': required[1],
             'productionCandidateSource': result['sourceSnapshot'], 'deployedProductionSource': selected.BASE,
             'FESFlakyNotRun': 0, 'newIndependentCases': {'elf':8, 'pending':12, 'guards':3}[args.group],
             'cumulativeIndependentCasesInRun': required[2], 'priorIndependentCasesRevalidated': {'elf':0, 'pending':8, 'guards':20}[args.group],
             'relatedCases': required[0] - required[2],
             'cases': records, 'suiteProofs': suites, 'targetMethodCounters': measured,
             'independentCoverageXmlSha256': selected.sha(coverage_path), 'independentStaticXmlSha256': static_hashes,
             'freshStaticThreeCompiledModules': result['freshStatic'], 'allSixFormatBeforeAnyPt': True,
             'mainDelta': result['mainDelta'], 'startUTC': result['startUTC'], 'endUTC': result['endUTC'],
             'commands': result['commands'], 'phaseExits': result['phaseExits'],
             'originalBeginSha256': selected.sha(run / 'begin.safe.json'),
             'originalManifestSha256': selected.sha(run / 'manifest.safe.json'),
             'logSha256': result['logSha256'], 'sourceInputsSha256': evidence.sha(json.dumps(begin['inputs'], sort_keys=True).encode()),
             'configuredToolchain': {'jdk': '25.0.4', 'maven': '3.9.12', 'jacoco': '0.8.15', 'spotbugs': '4.10.4.0', 'formatter': '1.36.1'},
             'hostOsMeasuredAtPublication': platform.platform(), 'failuresPreserved': failures,
             'spec': {'elf':'1045_Root_ELF固定digest内部port・独立PT仕様.md',
                      'pending':'1047_Root待機・同owner期限・欠落例外の独立PT仕様.md',
                      'guards':'1049_Root入口の不許可role・null・I_Oゼロ独立PT仕様.md'}[args.group],
             'bugs': ['BUG1411', 'BUG1412'], 'ykt': ['YKT1175', 'YKT1176'],
             'wholeRegression': False, 'formalAccepted': False, 'acceptedLeafDelta': 0,
             'effortPercent': None, 'oldNativeImported': False, 'newSourceNativeQualified': False,
             'wholeCoverage100': False, 'rawXmlPropertiesOrSecretsExported': False,
             'vmActions': 0, 'mavenReissued': False, 'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    os.umask(0o077); public.mkdir(parents=True)
    with (public / 'manifest.json').open('x') as output:
        json.dump(value, output, ensure_ascii=False, indent=2); output.write('\n'); output.flush(); os.fsync(output.fileno())
    print(json.dumps({'actualExit': 0, 'tests': required[0], 'newIndependentCases': value['newIndependentCases'],
                      'publicManifest': str((public / 'manifest.json').relative_to(ROOT)),
                      'sha256': selected.sha(public / 'manifest.json'), 'formalAccepted': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
