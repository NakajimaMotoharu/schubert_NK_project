"""Execute the six intact Music hierarchy template cases on current admitted inputs."""

from datetime import datetime, timezone
import importlib.util
import os
from pathlib import Path
import subprocess
from tempfile import mkdtemp

from jacoco_readonly_exec_subset import decode

previous = Path(__file__).with_name('5685_scr013_track_current_six.py')
spec = importlib.util.spec_from_file_location('track_receipt_helpers', previous)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
ROOT, OPS, PLAN, TOOLS = helpers.ROOT, helpers.OPS, helpers.PLAN, helpers.TOOLS
JAVA, JAVAC = helpers.JAVA, helpers.JAVAC
read, write, pin, now, git, cases, evidence = (helpers.read, helpers.write, helpers.pin, helpers.now,
                                              helpers.git, helpers.cases, helpers.evidence)
RUN = 'PG41502-scr011-012-current-template-six-v1'
TEST = 'dev.codex.schubert.nk.web.view.MusicHierarchyTemplateTest'
PREFIXES = ('dev/codex/schubert/nk/web/view/MusicCategoryViewModel',
            'dev/codex/schubert/nk/web/view/MusicSectionViewModel',
            'dev/codex/schubert/nk/web/config/WebMvcConfiguration')


def main():
    start = read(next(PLAN.glob('1901_*')))
    head, core = start['values']['source'], start['values']['productionCoreMain']
    quota = start['quota']
    age = datetime.now(timezone.utc) - datetime.fromisoformat(quota['observedAtUTC'])
    assert quota['ordinaryUsageAllowed'] and 0 <= age.total_seconds() <= 120
    assert all(window is None or window['remainingPercent'] > 10
               for window in (quota['primary'], quota['secondary']))
    assert head == git('rev-parse', 'HEAD').decode().strip()
    old_path = evidence('27750')
    old = read(old_path)
    closure = read(evidence('27740'))
    original_xml = old_path.parent / 'original-TEST-junit-jupiter.xml'
    assert pin(original_xml)['sha256'] == old['files'][original_xml.name]
    expected = [row for row in cases(original_xml) if row[1] == TEST]
    assert len(expected) == 6 and all(row[-1] == 'pass' for row in expected)
    java_root = 'src/schubert-nk-web/src'
    fixture = f"{java_root}/test/java/{TEST.replace('.', '/')}.java"
    main_paths = [*closure['newSafeMainInputHashes'], *closure['reusedRootMainSourceHashes']]
    resource_paths = [f'{java_root}/main/resources/{p}' for p in (
        'templates/music.html', 'templates/music-sections.html', 'templates/fragments/layout.html', 'static/css/schubert.css')]
    assert len(set(main_paths)) == 29
    current_source = {}
    held = ('TemporaryInfrastructureException', 'FingerprintKeyRing', 'ResponseSnapshotCodec', 'WebStartupException')
    for name in [*main_paths, fixture, *resource_paths]:
        path = Path(name)
        assert pin(path)['sha256'] == old['inputHashes'][name], name
        content = git('show', f'{head}:{name}')
        assert path.read_bytes() == content and not any(word.encode() in content for word in held), name
        current_source[name] = pin(path)['sha256']
    receipt = read(evidence('41322'))['packagingProof']['artifacts']['protocol']
    protocol = Path(receipt['artifact']['path'])
    assert pin(protocol)['sha256'] == receipt['artifact']['sha256']
    assert not git('diff', '--name-only', receipt['archiveSource'], head, '--', 'pom.xml', 'src/schubert-nk-protocol')
    sdk = []
    for name, checksum in old['dependencies'].items():
        path = Path(name)
        if path.is_relative_to(TOOLS):
            assert pin(path)['sha256'] == checksum
            sdk.append(path)
    assert len(sdk) == 24
    analysis_deps = read(evidence('41304'))['tools'][0]['argv'][5]
    agent = next((TOOLS / 'm2/repository/org/jacoco/org.jacoco.agent/0.8.15').glob('*-runtime.jar'))
    assert pin(agent)['sha256'] == read(evidence('38002'))['measurementAgentSha256']
    analyzer_source = ROOT / 'tools/quality/jacoco/UnfilteredCodeMeasurement.java'
    assert analyzer_source.read_bytes() == git('show', f'{head}:tools/quality/jacoco/UnfilteredCodeMeasurement.java')

    private = ROOT.parent / 'pgpt-runs/PG379' / RUN
    private.mkdir(mode=0o700)
    scratch = Path(mkdtemp(prefix='pgpt-scr011-012-template-', dir='/dev/shm'))
    prod, test, analyzer = (scratch / name for name in ('main', 'test', 'analyzer'))
    for folder in (prod, test, analyzer):
        folder.mkdir()
    resources = scratch / 'src/main/resources'
    for name in resource_paths:
        p = resources / name.split('/resources/', 1)[1]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((ROOT / name).read_bytes())
    stages = []

    def run(label, command):
        began = now()
        args = list(map(str, command))
        r = subprocess.run(args, cwd=scratch, capture_output=True, timeout=75)
        for key, data in (('stdout', r.stdout), ('stderr', r.stderr)):
            (private / f'{label}.{key}').write_bytes(data)
        entry = dict(stage=label, argv=args, cwd=str(scratch), beganUTC=began, terminalUTC=now(),
                     exit=r.returncode, output=pin(private / f'{label}.stdout'), error=pin(private / f'{label}.stderr'))
        write(private / f'{label}.terminal.json', entry)
        stages.append(entry)
        return r

    write(private / 'begin.json', dict(run=RUN, source=head, core=core, estimates=start['values']['estimateAtGroupStartPp'],
          scope=current_source, protocol=pin(protocol), sdk=list(map(pin, sdk)), originals=expected, scratch=str(scratch)))
    cp = lambda rows: os.pathsep.join(map(str, rows))
    flags = ['--release', '25', '-g', '-encoding', 'UTF-8', '-Xlint:all', '-Werror', '-proc:none', '-implicit:none']
    assert run('main-compile', [JAVAC, *flags, '-cp', cp([protocol, *sdk]), '-d', prod,
                                *(ROOT / p for p in main_paths)]).returncode == 0
    assert run('test-compile', [JAVAC, *flags, '-cp', cp([prod, protocol, *sdk]), '-d', test, ROOT / fixture]).returncode == 0
    assert run('analyzer-compile', [JAVAC, '--release', '25', '-cp', analysis_deps, '-d', analyzer, analyzer_source]).returncode == 0
    exec_path, xml_dir = private / 'unit.exec', private / 'xml'
    r = run('junit', [JAVA, '-Duser.timezone=Asia/Tokyo', f'-javaagent:{agent}=destfile={exec_path},append=false,sessionid={RUN}',
                      '-cp', cp([test, prod, resources, protocol, *sdk]), 'org.junit.platform.console.ConsoleLauncher',
                      'execute', '--disable-banner', '--disable-ansi-colors', '--details', 'summary', '--fail-if-no-tests',
                      '--include-engine', 'junit-jupiter', '--select-class', TEST, '--reports-dir', xml_dir])
    report = xml_dir / 'TEST-junit-jupiter.xml'
    assert r.returncode == 0 and cases(report) == expected
    files = sorted(prod.rglob('*.class'))
    names = {p.relative_to(prod).as_posix().removesuffix('.class') for p in files}
    assert all(not any(x in name for x in held) for name in names)
    result = run('coverage', [JAVA, '-cp', cp([analyzer, analysis_deps]),
                              'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',
                              '--strict-original-exec', '--line-deficits', exec_path, *files])
    assert result.returncode == 0
    exec_info = decode(exec_path.read_bytes(), names, strict_class_names=True)
    assert len(exec_info['sessions']) == 1 and exec_info['sessions'][0]['labelBytesHex'] == RUN.encode().hex()
    counters = {}
    for line in result.stdout.decode().splitlines():
        parts = line.split('\t')
        if parts[0] == 'CLASS':
            name, crc, seen = parts[1:4]
            if seen == 'true':
                assert int(crc, 16) == int(exec_info['classes'][name]['crc64'], 16)
            counters[name] = {key: dict(missed=int(missed), covered=int(covered)) for
                              key, missed, covered in (part.split(':') for part in parts[6:])}
    assert set(counters) == names
    out = OPS / RUN
    out.mkdir()
    raw = out / 'unfiltered.tsv'
    raw.write_bytes(result.stdout)
    focus = {key: value for key, value in counters.items() if key.startswith(PREFIXES)}
    write(out / 'manifest.json', dict(run=RUN, productionCore=core, source=head, actualExit=0, firstTestPassed=6,
          tests=expected, productTestInvocations=1, newDefinitions=0, failures=0, skipped=0, errors=0, notRun=0,
          currentInputs=current_source, currentProtocol=pin(protocol), sourceSnapshot=pin(private / 'begin.json'),
          actualXml=pin(report), actualExec=pin(exec_path), raw=pin(raw), physicalClasses=len(counters),
          ownedAndSharedSelected=focus, allScopeCounters=counters, invocationReceipts=stages,
          originalTestAndOracle=pin(old_path), noCoverageUnion=True, noRealRuntimeActions=True, whole451=False,
          formalAcceptanceId=None, terminalAtUTC=now()))
    print('tests', len(expected), 'web physical', len(counters))


if __name__ == '__main__':
    main()
