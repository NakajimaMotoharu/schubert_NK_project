"""Check the SS311 API repository direction on four handwritten class-file fixtures."""
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import runpy
import sys

COMMON = runpy.run_path(str(Path(__file__).with_name('5267_f02_controller_archunit_canaries.py')))
E = COMMON['OPS']
TOOL = COMMON['TOOL']
BASE = 'dev.codex.schubert.nk.api.'
SERVICE = BASE + 'application.log.DummyService'
REPO = BASE + 'persistence.DummyRepository'
MONITOR = BASE + 'monitoring.persistence.MonitoringRepository'
LOWER = BASE + 'monitoring.persistence.LocalRepository'
CASES = (
    ('027', REPO, SERVICE, True),
    ('028', MONITOR, SERVICE, True),
    ('029', SERVICE, REPO, False),
    ('030', LOWER, 'java.time.Clock', False),
)
BODIES = {
    SERVICE: 'public static int value() { return DummyRepository.fixed(); }',
    REPO: f'public int back() {{ return {SERVICE}.value(); }} public static int fixed() {{return 2;}}',
    MONITOR: f'public int back() {{ return {SERVICE}.value(); }}',
    LOWER: 'public java.time.Clock clock() { return java.time.Clock.systemUTC(); }',
}
NAMES = ('PG40170-f02-monitoring-repository-before-v1', 'PG40172-f02-monitoring-repository-after-v1')


def fixtures(folder):
    owners = {name: [COMMON['P'] + name + '.OwnedCanary'] for name in COMMON['MODULES']}
    bodies = {names[0]: '' for names in owners.values()}
    bodies.update(BODIES)
    owners['api'].extend(BODIES)
    bodies[owners['protocol'][0]] = 'static { System.setProperty("nk.archunit.canary.initialized","true"); }'
    files = []
    for name, body in sorted(bodies.items()):
        package, _, kind = name.rpartition('.')
        file = folder / (name.replace('.', '/') + '.java')
        file.parent.mkdir(exist_ok=True, parents=True)
        extra = 'import ' + REPO + ';\n' if name == SERVICE else ''
        file.write_text(f'package {package};\n{extra}public final class {kind} {{ {body} }}\n')
        files.append(file)
    return owners, files


def main(after):
    s = json.loads(next(COMMON['PLAN'].glob('645_F02*')).read_bytes())['values']
    pin, git, sha = (COMMON[k] for k in ('pin', 'git', 'sha'))
    head = git('rev-parse', 'HEAD').decode().strip()
    assert (head != s['source']) == after
    prior, rule = s['oracleReferences']
    design = git('show', f"{s['canonicalDesignSource']}:{rule['path']}")
    assert sha(design) == rule['sha256'] and 'repositoryから上位層を呼ばない'.encode() in design
    work_tool = git('show', f'{head}:{TOOL}')
    assert (sha(work_tool) != prior['sha256']) == after
    assert all(pin(p)['sha256'] == h for p, h in COMMON['PINS'].items())
    out = E / NAMES[after]
    out.mkdir()
    with TemporaryDirectory(dir='/dev/shm', prefix='pgpt-f02-repository-') as area:
        work = Path(area)
        tool_file = work / TOOL.name
        tool_file.write_bytes(work_tool)
        owners, files = fixtures(work / 'source')
        java = COMMON['JAVA']
        cp = os.pathsep.join(map(str, (COMMON['ARCH'], COMMON['SLF'])))
        compiler = [java.with_name('javac'), '--release', '25', '-Xlint:all', '-Werror', '-proc:none']
        receipts = {}
        for label, command in (
            ('tool-compile', [*compiler, '-cp', cp, '-d', work / 'tool', tool_file]),
            ('fixture-compile', [*compiler, '-d', work / 'classes', *files]),
        ):
            receipts[label], _ = COMMON['execute'](out, label, command, work)
            assert receipts[label]['actualExit'] == 0
        hashes = {}
        for module, names in owners.items():
            COMMON['archive'](work / (module + '.jar'), names, work / 'classes')
            hashes[module] = {name: pin(work / 'classes' / (name.replace('.', '/') + '.class'))['sha256']
                              for name in names}
        receipts['audit'], stdout = COMMON['execute'](
            out, 'audit', [java, '-cp', str(work / 'tool') + os.pathsep + cp, 'ModuleDependencyAudit',
                           *(f'{m}={work / (m + ".jar")}' for m in owners)], work)
    rows = [line.split('\t') for line in stdout.splitlines()]
    assert [r for r in rows if r[0] == 'ARCHUNIT'] == [['ARCHUNIT', '1.4.2', '10', '10']]
    findings = {(rule, origin, target) for _, rule, origin, target in (r for r in rows if r[0] == 'FINDING')}
    expected = {('REPOSITORY_DIRECTION', REPO, SERVICE)}
    if after:
        expected.add(('REPOSITORY_DIRECTION', MONITOR, SERVICE))
    assert findings == expected and receipts['audit']['actualExit'] == 1
    tests = [dict(testId=f'PT-F02-ARCH-{n}', origin=source, target=target, expected=forbidden,
                  observed=('REPOSITORY_DIRECTION', source, target) in findings)
             for n, source, target, forbidden in CASES]
    manifest = dict(actualExit=0, source=head, core=s['productionCoreMain'],
                    canonical=s['canonicalDesignSource'], toolSha256=sha(work_tool), physical=hashes, receipts=receipts,
                    tests=tests, matched=sum(t['expected'] == t['observed'] for t in tests),
                    productTests=0, productJars=0, wholeF02Accepted=False,
                    terminalAtUTC=datetime.now(timezone.utc).isoformat())
    file = out / 'manifest.json'
    COMMON['dump'](file, manifest)
    print(pin(file), manifest['matched'])


if __name__ == '__main__':
    main({'before': False, 'after': True}[sys.argv[1]])
