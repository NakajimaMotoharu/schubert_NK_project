"""Check direct Spring JDBC edges in four synthetic bytecode canaries for SS311 §5.2."""
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
WEB = 'dev.codex.schubert.nk.web.canary.'
JDBC = 'org.springframework.jdbc.core.'
TEMPLATE = JDBC + 'JdbcTemplate'
OPERATIONS = JDBC + 'JdbcOperations'
REST = 'org.springframework.web.bind.annotation.RestController'
CASES = (
    ('023', 'JdbcTemplateController',
     'public int read() { return new org.springframework.jdbc.core.JdbcTemplate().getFetchSize(); }', TEMPLATE, True),
    ('024', 'JdbcOperationsEndpoint',
     'public int read(org.springframework.jdbc.core.JdbcOperations port) { return port.getFetchSize(); }',
     OPERATIONS, True),
    ('025', 'TechnicalReadFacade',
     'public int read() { return new org.springframework.jdbc.core.JdbcTemplate().getFetchSize(); }', TEMPLATE, False),
    ('026', 'ReadFacadeController',
     'public int read(TechnicalReadFacade facade) { return facade.read(); }', WEB + 'TechnicalReadFacade', False),
)
RUNS = {
    'before': 'PG40142-f02-controller-spring-jdbc-before-v1',
    'after': 'PG40144-f02-controller-spring-jdbc-after-v1',
}


def fixtures(folder):
    owners = {name: [COMMON['P'] + name + '.OwnedCanary'] for name in COMMON['MODULES']}
    types = {items[0]: 'public final class OwnedCanary {}' for items in owners.values()}
    types[owners['protocol'][0]] = (
        'public final class OwnedCanary { static { System.setProperty("nk.archunit.canary.initialized","true"); } }')
    types.update({
        TEMPLATE: 'public final class JdbcTemplate { public int getFetchSize() { return 0; } }',
        OPERATIONS: 'public interface JdbcOperations { int getFetchSize(); }',
        REST: '@java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME) public @interface RestController {}',
    })
    for _, owner, member, _, _ in CASES:
        name = WEB + owner
        header = ('@' + REST + ' ') if owner == 'JdbcOperationsEndpoint' else ''
        types[name] = f'{header}public final class {owner} {{ {member} }}'
        owners['web'].append(name)
    paths = []
    for name, source in sorted(types.items()):
        path = folder / (name.replace('.', '/') + '.java')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('package ' + name.rpartition('.')[0] + ';\n' + source + '\n')
        paths.append(path)
    return owners, paths


def main(phase):
    start = json.loads(next(COMMON['PLAN'].glob('626_F02*.json')).read_bytes())['values']
    pin, git, sha = (COMMON[name] for name in ('pin', 'git', 'sha'))
    head = git('rev-parse', 'HEAD').decode().strip()
    assert (head == start['source']) == (phase == 'before')
    old, design = start['oracleReferences']
    design_bytes = git('show', f"{start['canonicalDesignSource']}:{design['path']}")
    assert sha(design_bytes) == design['sha256']
    assert 'ControllerはJDBC、JMS template、filesystem APIを直接呼ばない'.encode() in design_bytes
    tool_bytes = git('show', f'{head}:{TOOL}')
    assert (sha(tool_bytes) == old['sha256']) == (phase == 'before')
    assert all(pin(path)['sha256'] == digest for path, digest in COMMON['PINS'].items())
    out = E / RUNS[phase]
    out.mkdir()
    with TemporaryDirectory(dir='/dev/shm', prefix='pgpt-f02-jdbc-') as temporary:
        work = Path(temporary)
        tool = work / TOOL.name
        tool.write_bytes(tool_bytes)
        owners, sources = fixtures(work / 'source')
        java = COMMON['JAVA']
        cp = os.pathsep.join(map(str, (COMMON['ARCH'], COMMON['SLF'])))
        javac = [java.with_name('javac'), '--release', '25', '-Xlint:all', '-Werror', '-proc:none']
        receipts = {}
        for name, command in (
            ('tool-compile', [*javac, '-cp', cp, '-d', work / 'tool', tool]),
            ('fixture-compile', [*javac, '-d', work / 'fixtures', *sources]),
        ):
            receipts[name], _ = COMMON['execute'](out, name, command, work)
            assert receipts[name]['actualExit'] == 0
        physical = {}
        for module, items in owners.items():
            jar = work / (module + '.jar')
            COMMON['archive'](jar, items, work / 'fixtures')
            physical[module] = {name: pin(work / 'fixtures' / (name.replace('.', '/') + '.class'))['sha256']
                                for name in sorted(items)}
        receipts['audit'], output = COMMON['execute'](
            out, 'audit', [java, '-cp', str(work / 'tool') + os.pathsep + cp, 'ModuleDependencyAudit',
                           *(f'{m}={work / (m + ".jar")}' for m in owners)], work)
    rows = [line.split('\t') for line in output.splitlines()]
    assert [item for item in rows if item[0] == 'ARCHUNIT'] == [['ARCHUNIT', '1.4.2', '10', '10']]
    hits = {(item[1], item[2], item[3]) for item in rows if item[0] == 'FINDING'}
    observed_counts = {item[1]: int(item[2]) for item in rows if item[0] == 'RULE'}
    assert set(observed_counts) == COMMON['RULES'] and sum(observed_counts.values()) == len(hits)
    assert hits == ({('CONTROLLER_BOUNDARY', WEB + owner, target) for _, owner, _, target, forbidden in CASES if forbidden}
                    if phase == 'after' else set())
    cases = [dict(testId='PT-F02-ARCH-' + n, origin=WEB + owner, target=target, expected=forbidden,
                  observed=('CONTROLLER_BOUNDARY', WEB + owner, target) in hits)
             for n, owner, _, target, forbidden in CASES]
    assert receipts['audit']['actualExit'] == (phase == 'after')
    result = dict(actualExit=0, phase=phase, source=head, currentCore=start['productionCoreMain'],
                  canonicalDesign=start['canonicalDesignSource'], design=design, toolSha256=sha(tool_bytes),
                  physical=physical, receipts=receipts, cases=cases, matched=sum(c['expected'] == c['observed'] for c in cases),
                  productTests=0, productionClassesLoaded=0, wholeF02Accepted=False,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    COMMON['dump'](out / 'manifest.json', result)
    print(pin(out / 'manifest.json'), result['matched'])


if __name__ == '__main__':
    main(sys.argv[1])
