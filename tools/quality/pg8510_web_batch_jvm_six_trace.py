"""Two new fixed-role JVM compositions, all source/bytes/ownership, no API or baseline replay."""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg8388_metric_identity_six_trace as common
from host_tool_invocation import capture, verify

host, architecture, steps = common.host, common.architecture, common.steps
require = common.base.require
SOURCE = '4950b3daf1632ed9f57c3ca42276532b24204745'
BEFORE = 'fe91dc6898c2f5b679c8fe14c70a490bed770c73'
COMPILE = host.W / 'pg8504-web-batch-jvm-six-compile-v1'
SLOT = host.W / 'pg8510-web-batch-jvm-six-trace-v1'
OUT = host.BASE / 'PG8510-web-batch-jvm-six-trace-v1'
ROLES = {'web': 'WebJvmMetrics', 'batch': 'BatchJvmMetrics'}
PATHS = {role: 'src/schubert-nk-' + role + '/src/main/java/dev/codex/schubert/nk/' + role + '/monitoring/' + name + '.java' for role, name in ROLES.items()}
ADDED = set(PATHS.values()) | {p.replace('/main/', '/test/').replace('.java', 'Test.java') for p in PATHS.values()}
CLASSES = {role + ':dev/codex/schubert/nk/' + role + '/monitoring/' + name + '.class' for role, name in ROLES.items()}
WITNESSES = (
    ('normal', 'PG8504-web-batch-jvm-six-compile-v1/manifest.json', '3e19a0703f8b845bdf71d7e7d78fdb73733528103acad510a69ba65b4652cf8e'),
    ('current', 'PG8508-web-batch-jvm-post-v1/manifest.json', 'e505d63a7be4ab18361100c34c59cb52b3a3a0787d21b180d5c4fe1a59c5e344'),
    ('priorNormal', 'PG8492-api-jvm-oracle-fixed-six-compile-v1/manifest.json', 'b6c9978bf0c71e1b76314c81557ffe7113911c27ed172e01c7eaf66ad52ac884'),
    ('priorTrace', 'PG8498-api-jvm-six-trace-v1/manifest.json', '292710c7d4dd584c5efe6fb118445cfadf82d3b1a742795536b3b97f35fd91f0'),
    ('sdkTypes', 'PG8493-api-jvm-sdk-type-proof-v1/manifest.json', '692661761d930f6aa6a3a44ca5bb0ae6b2ceec5222e2a1c78b911b2307ea6d50'),
    ('original', 'PG6930-current4222-cases/qualification.json', '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
    ('architecture', 'PG6960-archunit-static-v1/manifest.json', '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'))
SDK_IMPORTS = {'io.micrometer.core.instrument.binder.jvm.' + name for name in ('ClassLoaderMetrics', 'JvmMemoryMetrics', 'JvmThreadMetrics')} | {'io.micrometer.core.instrument.binder.system.UptimeMetrics'}


def owner(row, role):
    require(row['package'] == 'dev.codex.schubert.nk.' + role + '.monitoring' and row['type'] == ROLES[role], 'fixed role/type, not a shared helper')
    forbidden = tuple('dev.codex.schubert.nk.' + other + '.' for other in ('api', 'web', 'batch', 'bootstrap') if other != role)
    require(SDK_IMPORTS <= set(row['imports']) and not any(p.startswith(forbidden + ('java.net.',)) or p == 'io.micrometer.core.instrument.binder.jvm.JvmGcMetrics' for p in row['imports']), 'exact four non-resource SDK binders, no cross-app/shared/GC/target IO')


def fields(text, role):
    lines = [line for line in text.splitlines() if line.strip()]
    name = ROLES[role]
    require(lines[:2] == ['Compiled from "' + name + '.java"', 'public final class dev.codex.schubert.nk.' + role + '.monitoring.' + name + ' {'] and lines[-1] == '}', 'exact role class field grammar')
    result = [(line, lines[i + 1]) for i, line in enumerate(lines[:-1]) if line.startswith('  ') and not line.startswith('    ') and line.endswith(';') and '(' not in line]
    require(result == [('  private static final int BINDER_COUNT = 4;', '    descriptor: I')], 'fixed count constant only, no retained instance state')
    return result


def main():
    invocation = capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(), 'new-only role proof')
    proofs, pins = {}, {}
    for key, path, digest in WITNESSES:
        require(host.sha(host.BASE / path) == digest, 'immutable ' + key)
        proofs[key] = json.loads((host.BASE / path).read_text())
        pins[key] = dict(path=path, sha256=digest)
    normal, current, prior = proofs['normal'], proofs['current'], proofs['priorNormal']
    require(normal['source'] == current['source'] == SOURCE and normal['actualExit'] == normal['terminal']['actualExit'] == current['actualExit'] == 0 and normal['testsExecuted'] == 0, 'same actual source normal/current quality')
    require(current['tests'] == 28 and current['suites'] == 2 and len(current['executableClasses']) == 2 and current['actualCrcMismatch'] == 0 and current['actualSessions'] == 1 and not current['coverageUnion'] and all(c['missed'] == 0 for c in current['counters'].values()), 'original28/2 exact new2 four100')
    require(prior['source'] == proofs['priorTrace']['source'] == BEFORE and prior['actualExit'] == proofs['priorTrace']['actualExit'] == 0, 'exact qualified prior source')
    before, after = prior['begin']['inputHashes'], normal['begin']['inputHashes']
    require(set(after) - set(before) == ADDED and not (set(before) - set(after)) and all(after[p] == h for p, h in before.items()), 'only four additive source paths, all previous inputs/POM/other-role source unchanged')
    snapshot = COMPILE / 'snapshot'
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in after.items()), 'all actual frozen/current input bytes')
    old, physical = common.base.inventory(prior), common.base.inventory(normal)
    require(len(old) == 1812 and len(physical) == 1814 and set(physical) - set(old) == CLASSES and all(physical[p] == h for p, h in old.items()), 'two new physical classes, all1812 prior raw/debug bytes same')
    original = proofs['original']['allPhysicalMainSha256']
    require(len(original) == 1669 and all(physical[p] == h for p, h in original.items()), 'all original1669 same bytes, no qualification transfer')
    for path, digest in current['physicalClasses'].items():
        role = next((r for r in ROLES if path.startswith('dev/codex/schubert/nk/' + r + '/')), None)
        require(role is not None and physical[role + ':' + path] == digest, 'all current component physical owners')
    delta = subprocess.check_output(['git', 'diff', '--no-renames', '--name-status', '-z', BEFORE, SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=host.ROOT).split(b'\0')[:-1]
    require(len(delta) == 8 and {delta[i + 1].decode(): delta[i].decode() for i in range(0, len(delta), 2)} == dict.fromkeys(ADDED, 'A'), 'four exact additive Main/Unit paths')
    old_rows = {r['path']: r for r in proofs['priorTrace']['sourceRows']}
    require(len(old_rows) == 181 and not (set(old_rows) & ADDED), 'all181 prior owners')
    rows = []
    for path in sorted(set(old_rows) | ADDED):
        digest = host.sha(snapshot / path)
        require(path in ADDED or old_rows[path]['sha256'] == digest, 'all prior owner source same bytes')
        rows.append(dict(path=path, sha256=digest, owner='WBS-P018-09', sharedReference='WBS-C07', sharedAdditionalCostPp=0, relationship='CURRENT_ROLE_JVM_SOURCE' if path in ADDED else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION', sourceUnchanged=path not in ADDED))
    require(len(rows) == 185 and proofs['priorTrace']['ownerGuardBinding']['bootstrapSourcesUnchanged'] == 34, 'all185 owners/limited Bootstrap and all descriptors unchanged')
    models, rejected = {}, []
    for role in ROLES:
        body = (snapshot / PATHS[role]).read_text()
        model = common.contract.java(body)
        owner(model, role)
        compact = ''.join(body.split())
        expected_mode = 'newHttpMetricContract().detailedMetricsEnabled(mode)' if role == 'web' else 'MonitoringModePolicy.parse(mode).detailedMetricsEnabled()'
        require('Tags.of("service","' + role.upper() + '")' in compact and 'booleandetailed=' + expected_mode + ';' in compact, 'fixed non-user-selected role tag and existing own-role mode contract')
        models[role] = model
        for name, change in (('wrong-owner', lambda r: r.update(package='dev.codex.schubert.nk.api.monitoring')), ('shared-bootstrap', lambda r: r['imports'].append('dev.codex.schubert.nk.bootstrap.metrics.FORBIDDEN')), ('GC-listener', lambda r: r['imports'].append('io.micrometer.core.instrument.binder.jvm.JvmGcMetrics'))):
            mutant = copy.deepcopy(model)
            change(mutant)
            try:
                owner(mutant, role)
            except ValueError:
                rejected.append(role + ':' + name)
            else:
                raise ValueError('every role responsibility mutant rejects')
    core = host.TC / 'm2/repository/io/micrometer/micrometer-core/1.17.1/micrometer-core-1.17.1.jar'
    require(len(rejected) == 6 and proofs['sdkTypes']['metadataOnly'] and proofs['sdkTypes']['actualExit'] == 0 and host.sha(core) == proofs['sdkTypes']['sdkJarSha256'], 'six role negatives and same independent SDK type contract, no ABI replay')
    require(host.sha(architecture.SOURCE) == proofs['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH) == architecture.ARCH_SHA and host.sha(architecture.SLF) == architecture.SLF_SHA, 'same canary-qualified noninitializing bytecode reader')
    SLOT.mkdir()
    steps.SLOT = SLOT
    field_proofs, field_rejected = {}, []
    for role, name in ROLES.items():
        receipt, body = steps.step(role + '-fields', [str(architecture.JAVA.with_name('javap')), '-p', '-s', '-constants', str(snapshot / PATHS[role].replace('/src/main/java/', '/target/classes/').replace('.java', '.class'))])
        require(receipt['actualExit'] == 0, 'actual compiled fields terminal')
        actual = fields(body, role)
        anchor = '  public dev.codex.schubert.nk.' + role + '.monitoring.' + name + '();'
        require(body.count(anchor) == 1, 'independent constructor fixture present')
        for label, mutant in (
            ('retained-source', body.replace(anchor, '  private final io.micrometer.core.instrument.MeterRegistry source;\n    descriptor: Lio/micrometer/core/instrument/MeterRegistry;\n' + anchor)),
            ('public-count', body.replace('private static final int', 'public static final int', 1)),
            ('wrong-descriptor', body.replace('descriptor: I', 'descriptor: J', 1)),
            ('wrong-count', body.replace('BINDER_COUNT = 4;', 'BINDER_COUNT = 5;', 1))):
            try:
                fields(mutant, role)
            except ValueError:
                field_rejected.append(role + ':' + label)
            else:
                raise ValueError('every current role field mutant rejects')
        field_proofs[role] = dict(fields=actual, instanceFieldCount=0, receipt=receipt)
    require(len(field_rejected) == 8, 'eight exact field guard negatives, not PT')
    classes = SLOT / 'audit-classes'
    classes.mkdir()
    compiled, _ = steps.step('architecture-compile', [str(architecture.JAVAC), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', os.pathsep.join([str(architecture.ARCH), str(architecture.SLF)]), '-d', str(classes), str(architecture.SOURCE)])
    require(compiled['actualExit'] == 0, 'architecture reader compile')
    checked, body = steps.step('architecture-six', [str(architecture.JAVA), '-cp', os.pathsep.join([str(classes), str(architecture.ARCH), str(architecture.SLF)]), 'ModuleDependencyAudit', *[m + '=' + normal['jars'][m]['path'] for m in architecture.MODULES]])
    analysis = architecture.parse(body)
    require(checked['actualExit'] == 0 and analysis['physical'] == 1814 and not analysis['findings'] and len(analysis['rules']) == 5 and all(v == 0 for v in analysis['rules'].values()), 'all1814/five actual bytecode edges0')
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in after.items()), 'all inputs immutable after metadata proof')
    verify(invocation)
    value = dict(actualExit=0, source=SOURCE, invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), witnesses=pins, physicalClasses=physical, allPhysicalClassCount=1814, physicalAdded=sorted(CLASSES), physicalRemoved=[], physicalChanged={}, previousPhysicalUnchanged=1812, originalPhysicalUnchanged=1669, sourceRows=rows, sourceCount=185, currentTests=28, currentSuites=2, currentExecutableScope=sorted(current['executableClasses']), currentCounters=current['counters'], ownerGuardBinding=dict(currentRoleModels=models, newNegativeGuards=rejected, roleFields=field_proofs, fieldNegatives=field_rejected, bootstrapSourcesUnchanged=34, descriptorsUnchanged=True, metadataOnly=True), architecture=dict(result=analysis, compileReceipt=compiled, receipt=checked, targetInitialized=False), productTestsExecutedByPost=0, coverageUnion=False, sourceByteOnlyRowsNotCurrentPtPass=True, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, physical=1814, sourceOwners=185, roleNegatives=len(rejected), fieldNegatives=len(field_rejected), architecture=analysis['rules'], manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()

