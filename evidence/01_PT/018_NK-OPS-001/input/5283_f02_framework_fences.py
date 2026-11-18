"""Inspect six synthetic JARs for the explicit SS311 framework ownership rules."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import runpy
import sys

COMMON = runpy.run_path(str(Path(__file__).with_name('5267_f02_controller_archunit_canaries.py')))
E = COMMON['OPS']
P = COMMON['P']
JAVA = COMMON['JAVA']
TOOL = COMMON['TOOL']
DESIGN = 'documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md'
STUBS = {
    'org.springframework.jms.core.JmsTemplate': 'public final class JmsTemplate {}',
    'org.springframework.web.client.RestClient': 'public interface RestClient {}',
    'jakarta.jms.Connection': 'public interface Connection {}',
    'org.springframework.web.bind.annotation.RestController': (
        '@java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME) '
        'public @interface RestController {}'
    ),
    'org.springframework.http.server.ServerHttpResponse': 'public interface ServerHttpResponse {}',
    'org.apache.activemq.artemis.api.core.management.ActiveMQServerControl':
        'public interface ActiveMQServerControl {}',
}
# The expected owner/target pairs come from SS311, independent of the detector implementation.
CASES = (
    ('013', 'bootstrap', 'SpringMessaging', 'org.springframework.jms.core.JmsTemplate', True),
    ('014', 'bootstrap', 'SpringHttp', 'org.springframework.web.client.RestClient', True),
    ('015', 'bootstrap', 'JdkHttp', 'java.net.http.HttpClient', True),
    ('016', 'bootstrap', 'JmsApi', 'jakarta.jms.Connection', True),
    ('017', 'api', 'ControllerAnnotation', 'org.springframework.web.bind.annotation.RestController', True),
    ('018', 'batch', 'ControllerAnnotation', 'org.springframework.web.bind.annotation.RestController', True),
    ('019', 'api', 'BrowserResponse', 'org.springframework.http.server.ServerHttpResponse', True),
    ('020', 'bootstrap', 'JdbcAdmission', 'java.sql.Connection', False),
    ('021', 'api', 'BusinessMessaging', 'org.springframework.jms.core.JmsTemplate', False),
    ('022', 'batch', 'BrokerManagement', 'org.apache.activemq.artemis.api.core.management.ActiveMQServerControl', False),
)
RUNS = {'before': 'PG40115-f02-framework-fences-before-v2',
        'after': 'PG40116-f02-framework-fences-after-v1'}


def fixtures(directory):
    owners = {module: [P + module + '.KnownValue'] for module in COMMON['MODULES']}
    definitions = {names[0]: 'public final class KnownValue {}' for names in owners.values()}
    definitions[P + 'protocol.KnownValue'] = (
        'public final class KnownValue { static { System.setProperty("nk.archunit.canary.initialized","true"); } }'
    )
    definitions.update(STUBS)
    for _, module, name, target, _ in CASES:
        origin = P + module + '.' + name
        owners[module].append(origin)
        if target.endswith('.RestController'):
            definitions[origin] = f'@{target} public final class {name} {{}}'
        else:
            definitions[origin] = f'public final class {name} {{ public {target} dependency; }}'
    paths = []
    for name, body in sorted(definitions.items()):
        path = directory / (name.replace('.', '/') + '.java')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('package ' + name.rpartition('.')[0] + ';\n' + body + '\n')
        paths.append(path)
    return owners, paths


def examine(text, owners):
    rows = [line.split('\t') for line in text.splitlines()]
    total = sum(map(len, owners.values()))
    assert [r for r in rows if r[0] == 'ARCHUNIT'] == [['ARCHUNIT', '1.4.2', str(total), str(total)]]
    assert {r[1]: int(r[2]) for r in rows if r[0] == 'MODULE'} == {m: len(v) for m, v in owners.items()}
    assert all(r[1] == 'FRAMEWORK_FENCES' for r in rows if r[0] == 'FINDING')
    pairs = {(r[2], r[3]) for r in rows if r[0] == 'FINDING'}
    rules = {r[1]: int(r[2]) for r in rows if r[0] == 'RULE'}
    assert set(rules) == COMMON['RULES'] and sum(rules.values()) == len(pairs)
    assert rules['FRAMEWORK_FENCES'] == len(pairs)
    case_pairs = {(P + module + '.' + name, target) for _, module, name, target, _ in CASES}
    assert pairs <= case_pairs
    return [dict(testId='PT-F02-ARCH-' + number, origin=P + module + '.' + name, target=target,
                 expected=expected, observed=(P + module + '.' + name, target) in pairs)
            for number, module, name, target, expected in CASES]


def main(phase):
    start_path = next(COMMON['PLAN'].glob('611_F02*.json'))
    start = json.loads(start_path.read_bytes())['values']
    git, pin = COMMON['git'], COMMON['pin']
    source = start['source'] if phase == 'before' else git('rev-parse', 'HEAD').decode().strip()
    canonical = start['canonicalDesignSource']
    assert canonical == git('rev-parse', 'origin/main').decode().strip()
    design = git('show', f'{canonical}:{DESIGN}')
    assert COMMON['sha'](design) == start['oracleReferences'][1]['sha256']
    assert 'HTTP/JMS/業務repository/process entry/DDLは含めない'.encode() in design
    assert all(pin(path)['sha256'] == actual for path, actual in COMMON['PINS'].items())
    original = git('show', f'{source}:{TOOL}')
    assert (COMMON['sha'](original) == start['oracleReferences'][0]['sha256']) == (phase == 'before')
    out = E / RUNS[phase]
    out.mkdir()
    with TemporaryDirectory(prefix='pgpt-f02-framework-', dir='/dev/shm') as temporary:
        slot = Path(temporary)
        audit = slot / TOOL.name
        audit.write_bytes(original)
        owners, java_files = fixtures(slot / 'src')
        cp = os.pathsep.join(map(str, (COMMON['ARCH'], COMMON['SLF'])))
        compiler = [JAVA.with_name('javac'), '--release', '25', '-Xlint:all', '-Werror', '-proc:none']
        receipts = {}
        for label, command in (
            ('tool-compile', [*compiler, '-cp', cp, '-d', slot / 'audit', audit]),
            ('fixture-compile', [*compiler, '-d', slot / 'fixtures', *java_files]),
        ):
            receipts[label], _ = COMMON['execute'](out, label, command, slot)
            assert receipts[label]['actualExit'] == 0
        artifacts = {}
        for module, names in owners.items():
            jar = slot / (module + '.jar')
            COMMON['archive'](jar, names, slot / 'fixtures')
            entries = {name: COMMON['sha'](
                (slot / 'fixtures' / (name.replace('.', '/') + '.class')).read_bytes()) for name in sorted(names)}
            artifacts[module] = entries
        command = [JAVA, '-cp', os.pathsep.join([str(slot / 'audit'), cp]), 'ModuleDependencyAudit',
                   *(f'{module}={slot / (module + ".jar")}' for module in owners)]
        receipts['audit'], output = COMMON['execute'](out, 'audit', command, slot)
        assert receipts['audit']['actualExit'] == 1  # deliberate static canary violations
        cases = examine(output, owners)
    correct = sum(case['expected'] == case['observed'] for case in cases)
    assert correct == (4 if phase == 'before' else 10)
    manifest = dict(actualExit=0, childAuditExit=1, phase=phase, source=source,
                    productionCoreMain=start['productionCoreMain'], start=pin(start_path), toolSha256=COMMON['sha'](original),
                    canonical=canonical, designSha256=COMMON['sha'](design), artifacts=artifacts,
                    productClassesInitialized=0, productTests=0, externalOperations=0,
                    cases=cases, correct=correct, total=len(cases), receipts=receipts,
                    wholeF02Accepted=False, terminalAtUTC=COMMON['timestamp'](), verifier=pin(Path(__file__)))
    COMMON['dump'](out / 'manifest.json', manifest)
    print(correct, len(cases), pin(out / 'manifest.json'))


if __name__ == '__main__':
    main(sys.argv[1])
