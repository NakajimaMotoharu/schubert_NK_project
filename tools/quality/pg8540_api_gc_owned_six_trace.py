"""All prior source/bytes unchanged, explicit owner-before-GC activation metadata and current qualification."""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg8302_http_cdf_six_trace as base
import duration_exposition_owner_contract as contract
from host_tool_invocation import capture, verify

host, architecture, steps = base.host, base.architecture, base.steps
SOURCE = '20075e7f66c3ba8fcf9c52139e77de646abbc7c2'
BEFORE = '4950b3daf1632ed9f57c3ca42276532b24204745'
COMPILE = host.W / 'pg8534-api-gc-owned-six-compile-v1'
SLOT = host.W / 'pg8540-api-gc-owned-six-trace-v1'
OUT = host.BASE / 'PG8540-api-gc-owned-six-trace-v1'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiGcMetricRegistration.java'
INPUTS = {MAIN, MAIN.replace('/main/', '/test/').replace('.java', 'Test.java')}
CLASS = 'api:dev/codex/schubert/nk/api/monitoring/ApiGcMetricRegistration.class'
WITNESSES = (
    ('normal', 'PG8534-api-gc-owned-six-compile-v1/manifest.json', '889dff45e9791631d80c81431741a1d8134fbaa7d41b1a74813bb3d2954d8d19'),
    ('current', 'PG8538-api-gc-owned-post-v1/manifest.json', '81bcbb71e93028f15e1c0d518c26eca8df37c317b70b9550939fcea948cd833a'),
    ('priorNormal', 'PG8504-web-batch-jvm-six-compile-v1/manifest.json', '3e19a0703f8b845bdf71d7e7d78fdb73733528103acad510a69ba65b4652cf8e'),
    ('priorTrace', 'PG8510-web-batch-jvm-six-trace-v1/manifest.json', '26a46535835b9cd98dba97cb1d2f974c79e0e0cd55156e138728a344e95eaa4f'),
    ('original', 'PG6930-current4222-cases/qualification.json', '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
    ('architecture', 'PG6960-archunit-static-v1/manifest.json', '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'))


def validate_owner(row):
    base.require(row['package'] == 'dev.codex.schubert.nk.api.monitoring' and row['type'] == 'ApiGcMetricRegistration', 'exact new application owner/type')
    base.require('io.micrometer.core.instrument.binder.jvm.JvmGcMetrics' in row['imports'] and not any(p.startswith(('dev.codex.schubert.nk.web.', 'dev.codex.schubert.nk.batch.', 'dev.codex.schubert.nk.bootstrap.', 'java.net.')) or p in ('io.micrometer.core.instrument.Timer', 'io.micrometer.core.instrument.DistributionSummary') for p in row['imports']), 'API-owned GC only, no shared/cross-app type mode')


def activation_metadata(snapshot):
    require = base.require
    javap = str(architecture.JAVA.with_name('javap'))
    sdk = host.TC / 'm2/repository/io/micrometer/micrometer-core/1.17.1/micrometer-core-1.17.1.jar'
    require(host.sha(sdk) == '9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56', 'fixed SDK GC byte identity')
    receipt, text = steps.step('sdk-gc-activation-metadata', [javap, '-c', '-p', '-classpath', str(sdk), 'io.micrometer.core.instrument.binder.jvm.JvmGcMetrics'])
    require(receipt['actualExit'] == 0, 'public SDK bytecode terminal')
    constructor, rest = text.split('  public void bindTo(io.micrometer.core.instrument.MeterRegistry);', 1)
    binding, close = rest.split('  public void close();', 1)
    require('java.lang.AutoCloseable' in constructor and 'getMemoryPoolMXBeans' in constructor and 'addNotificationListener' not in constructor, 'constructor metadata only, no GC notification registration')
    require('NotificationEmitter.addNotificationListener:' in binding and 'notificationListenerCleanUpRunnables' in binding, 'SDK bind activates listener and captures cleanup')
    require('notificationListenerCleanUpRunnables' in close and 'NotificationEmitter.removeNotificationListener:' in close, 'SDK close cleanup and owned listener removal bytecode')
    cls = snapshot / MAIN.replace('/src/main/java/', '/target/classes/').replace('.java', '.class')
    field_receipt, fields = steps.step('state-fields', [javap, '-p', '-s', str(cls)])
    require(field_receipt['actualExit'] == 0, 'own compiled field metadata terminal')
    def validate(value):
        lines = [line for line in value.splitlines() if line.strip()]
        require(lines[:2] == ['Compiled from "ApiGcMetricRegistration.java"', 'public final class dev.codex.schubert.nk.api.monitoring.ApiGcMetricRegistration {'] and lines[-1] == '}', 'exact GC owner field grammar')
        declarations = [line for line in lines if line.startswith('  ') and not line.startswith('    ') and line.endswith(';') and '(' not in line]
        require(not declarations, 'no retained field or constant')
    validate(fields)
    rejected = []
    for name, mutant in (
        ('retained-source', fields.replace('  public dev.codex', '  private final io.micrometer.core.instrument.MeterRegistry source;\n    descriptor: Lio/micrometer/core/instrument/MeterRegistry;\n  public dev.codex', 1)),
        ('retained-static', fields.replace('  public dev.codex', '  private static final java.lang.Object handle;\n    descriptor: Ljava/lang/Object;\n  public dev.codex', 1)),
        ('foreign-owner', fields.replace('nk.api.monitoring.ApiGcMetricRegistration {', 'nk.web.monitoring.ApiGcMetricRegistration {', 1))):
        try:
            validate(mutant)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('field guard must reject each metadata mutant')
    return (dict(jarPath=str(sdk), jarSha256=host.sha(sdk), receipt=receipt, metadataOnly=True, sdkInitialized=False, constructorHasNoNotificationRegistration=True, bindRegisters=True, closeRemoves=True),
            dict(receipt=field_receipt, fields=0, negatives=rejected))


def main():
    invocation = capture(Path(__file__))
    require = base.require
    require(not SLOT.exists() and not OUT.exists(), 'new-only exact current metadata proof')
    proofs, pins = {}, {}
    for name, path, digest in WITNESSES:
        require(host.sha(host.BASE / path) == digest, 'immutable ' + name + ' witness')
        proofs[name] = json.loads((host.BASE / path).read_text())
        pins[name] = dict(path=path, sha256=digest)
    normal, current, prior = proofs['normal'], proofs['current'], proofs['priorNormal']
    require(normal['source'] == current['source'] == SOURCE and normal['actualExit'] == normal['terminal']['actualExit'] == current['actualExit'] == 0 and normal['testsExecuted'] == 0, 'same-source real normal and current qualification')
    require(current['tests'] == 14 and current['suites'] == 1 and len(current['executableClasses']) == 1 and current['actualCrcMismatch'] == 0 and current['actualSessions'] == 1 and not current['coverageUnion'] and all(v['missed'] == 0 for v in current['counters'].values()), 'exact original14/1 and one class four100')
    snapshot = COMPILE / 'snapshot'
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all current/frozen source input bytes')
    require(prior['source'] == proofs['priorTrace']['source'] == BEFORE and prior['actualExit'] == proofs['priorTrace']['actualExit'] == 0, 'qualified prior ownership and lint followup')
    require(set(normal['begin']['inputHashes']) - set(prior['begin']['inputHashes']) == INPUTS and all(normal['begin']['inputHashes'].get(p) == h for p, h in prior['begin']['inputHashes'].items()), 'only new Main/Unit inputs, all prior production/test/POM bytes identical')
    previous, physical = base.inventory(prior), base.inventory(normal)
    require(len(previous) == 1814 and len(physical) == 1815 and set(physical) - set(previous) == {CLASS} and all(physical.get(p) == h for p, h in previous.items()), 'one new API GC physical class, all previous1809 raw/debug identical')
    original = proofs['original']['allPhysicalMainSha256']
    require(len(original) == 1669 and all(physical[p] == h for p, h in original.items()), 'original1669 byte identity is not current PT transfer')
    require(all(physical['api:' + p] == h for p, h in current['physicalClasses'].items()), 'all selected physical owner bytes')
    parts = subprocess.check_output(['git', 'diff', '--no-renames', '--name-status', '-z', BEFORE, SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts) == 4 and {parts[n + 1].decode(): parts[n].decode() for n in range(0, len(parts), 2)} == {p: 'A' for p in INPUTS}, 'exact two additive source paths')
    old_rows = {r['path']: r for r in proofs['priorTrace']['sourceRows']}
    require(len(old_rows) == 185 and not (set(old_rows) & INPUTS), 'complete prior175 source owners')
    rows = []
    for path in sorted(set(old_rows) | INPUTS):
        digest = host.sha(snapshot / path)
        require(path in INPUTS or old_rows[path]['sha256'] == digest, 'all old owner bytes unchanged')
        rows.append(dict(path=path, sha256=digest, owner='WBS-P018-09', sharedReference='WBS-C07', sharedAdditionalCostPp=0, relationship='CURRENT_API_GC_SOURCE_OR_EXPLICIT_DEPENDENCY' if path in INPUTS or path in current['sourceFiles'] else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION', sourceUnchanged=path not in INPUTS))
    require(len(rows) == 187, 'all177 source owners')
    owner = contract.java((snapshot / MAIN).read_text())
    validate_owner(owner)
    rejected = []
    for name, change in (('other-app', lambda x: x.update(package='dev.codex.schubert.nk.web.monitoring')), ('shared-bootstrap-import', lambda x: x['imports'].append('dev.codex.schubert.nk.bootstrap.monitoring.FORBIDDEN_FIXTURE_ONLY')), ('wrong-observation-type', lambda x: x['imports'].append('io.micrometer.core.instrument.Timer'))):
        mutant = copy.deepcopy(owner)
        change(mutant)
        try:
            validate_owner(mutant)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('new owner metadata negatives must reject')
    require(len(rejected) == 3 and proofs['priorTrace']['ownerGuardBinding']['bootstrapSourcesUnchanged'] == 34, 'new three negatives plus all prior role inputs byte identity; no old mutant replay')
    require(host.sha(architecture.SOURCE) == proofs['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH) == architecture.ARCH_SHA and host.sha(architecture.SLF) == architecture.SLF_SHA, 'same canary-qualified noninitializing bytecode reader')
    SLOT.mkdir()
    steps.SLOT = SLOT
    sdk_proof, field_proof = activation_metadata(snapshot)
    classes = SLOT / 'audit-classes'
    classes.mkdir()
    compiled, _ = steps.step('architecture-compile', [str(architecture.JAVAC), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', os.pathsep.join([str(architecture.ARCH), str(architecture.SLF)]), '-d', str(classes), str(architecture.SOURCE)])
    require(compiled['actualExit'] == 0, 'architecture reader compile')
    checked, text = steps.step('architecture-six', [str(architecture.JAVA), '-cp', os.pathsep.join([str(classes), str(architecture.ARCH), str(architecture.SLF)]), 'ModuleDependencyAudit', *[m + '=' + normal['jars'][m]['path'] for m in architecture.MODULES]])
    analysis = architecture.parse(text)
    require(checked['actualExit'] == 0 and analysis['physical'] == 1815 and not analysis['findings'] and len(analysis['rules']) == 5 and all(v == 0 for v in analysis['rules'].values()), 'all1810 and five actual architecture edges zero')
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all source inputs unchanged after reader')
    verify(invocation)
    value = dict(actualExit=0, source=SOURCE, invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), witnesses=pins, physicalClasses=physical, allPhysicalClassCount=1815, physicalAdded=[CLASS], physicalChanged={}, physicalRemoved=[], previousPhysicalUnchanged=1814, originalPhysicalUnchanged=1669, sourceRows=rows, sourceCount=187, currentTests=14, currentSuites=1, currentExecutableScope=sorted(current['executableClasses']), currentCounters=current['counters'], sdkActivationMetadata=sdk_proof, exactFieldMetadata=field_proof, ownerGuardBinding=dict(newOwner=owner, newNegativeGuards=rejected, priorAllInputsByteIdentical=True, priorRoleGuardsReplayed=False, bootstrapSourcesUnchanged=34, descriptorsUnchanged=True, metadataOnly=True), architecture=dict(result=analysis, compileReceipt=compiled, receipt=checked, targetInitialized=False), productTestsExecutedByPost=0, coverageUnion=False, sourceByteOnlyRowsNotCurrentPtPass=True, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, physical=1815, sourceOwners=187, newResponsibilityNegatives=len(rejected), architecture=analysis['rules'], manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
