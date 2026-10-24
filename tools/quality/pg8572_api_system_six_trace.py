"""All prior source/bytes unchanged, one new API non-resource CPU-FD with current-scope quality/ownership."""
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
SOURCE = 'e027929a7a6da504e0d03efd517ea98656ce369b'
BEFORE = '623be8eeaf078f85cfa5682dced7a3b2e21a2b49'
COMPILE = host.W / 'pg8566-api-system-six-compile-v1'
SLOT = host.W / 'pg8572-api-system-six-trace-v1'
OUT = host.BASE / 'PG8572-api-system-six-trace-v1'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiSystemMetrics.java'
INPUTS = {MAIN, MAIN.replace('/main/', '/test/').replace('.java', 'Test.java')}
CLASS = 'api:dev/codex/schubert/nk/api/monitoring/ApiSystemMetrics.class'
WITNESSES = (
    ('normal', 'PG8566-api-system-six-compile-v1/manifest.json', 'a5c9cc24d4c0f5663ac7d79f66f254dc95dc507bbefc6208b633687a0f11d522'),
    ('current', 'PG8570-api-system-post-v1/manifest.json', '3e738e7b0fa822ad2c8fa46850896aa9ab9584f42cdfcef586a488eebdbc7bf5'),
    ('priorNormal', 'PG8546-web-batch-gc-six-compile-v1/manifest.json', 'cac5a32fa54aad3854c3f843a2289fd04ec26a70765c4da45a36ebe31b2fd8cb'),
    ('priorTrace', 'PG8560-web-batch-gc-six-trace-v1/manifest.json', 'a7d6b0c8a178b61139a9862c63d671f70be0db93f8d0823781740ded4db25b45'),
    ('sdkTypes', 'PG8565-system-sdk-type-proof-v1/manifest.json', 'a213a9ff6f4c9f4e88af6935ece7e82f20945a7628b4a3631e993bb64dfd7449'),
    ('original', 'PG6930-current4222-cases/qualification.json', '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
    ('architecture', 'PG6960-archunit-static-v1/manifest.json', '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'))


def validate_owner(row):
    base.require(row['package'] == 'dev.codex.schubert.nk.api.monitoring' and row['type'] == 'ApiSystemMetrics', 'exact new application owner/type')
    base.require({'io.micrometer.core.instrument.binder.system.ProcessorMetrics', 'io.micrometer.core.instrument.binder.system.FileDescriptorMetrics'} <= set(row['imports']) and not any(p.startswith(('dev.codex.schubert.nk.web.', 'dev.codex.schubert.nk.batch.', 'dev.codex.schubert.nk.bootstrap.')) or p in ('io.micrometer.core.instrument.Timer', 'io.micrometer.core.instrument.DistributionSummary', 'io.micrometer.core.instrument.binder.jvm.JvmGcMetrics') for p in row['imports']), 'API-owned two non-resource standard binders only, no shared/cross-app type mode')


def state_fields(text):
    lines = [line for line in text.splitlines() if line.strip()]
    base.require(lines[:2] == ['Compiled from "ApiSystemMetrics.java"', 'public final class dev.codex.schubert.nk.api.monitoring.ApiSystemMetrics {'] and lines[-1] == '}', 'exact new physical owner grammar')
    fields = [(line, lines[i + 1]) for i, line in enumerate(lines[:-1]) if line.startswith('  ') and not line.startswith('    ') and line.endswith(';') and '(' not in line]
    base.require(fields == [('  private static final int BINDER_COUNT = 2;', '    descriptor: I')], 'one fixed non-executable constant, zero retained instance fields')
    return fields


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
    require(len(previous) == 1817 and len(physical) == 1818 and set(physical) - set(previous) == {CLASS} and all(physical.get(p) == h for p, h in previous.items()), 'one new API non-resource CPU-FD physical class, all previous1817 raw/debug identical')
    original = proofs['original']['allPhysicalMainSha256']
    require(len(original) == 1669 and all(physical[p] == h for p, h in original.items()), 'original1669 byte identity is not current PT transfer')
    require(all(physical['api:' + p] == h for p, h in current['physicalClasses'].items()), 'all selected physical owner bytes')
    parts = subprocess.check_output(['git', 'diff', '--no-renames', '--name-status', '-z', BEFORE, SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts) == 4 and {parts[n + 1].decode(): parts[n].decode() for n in range(0, len(parts), 2)} == {p: 'A' for p in INPUTS}, 'exact two additive source paths')
    old_rows = {r['path']: r for r in proofs['priorTrace']['sourceRows']}
    require(len(old_rows) == 191 and not (set(old_rows) & INPUTS), 'complete prior191 source owners')
    rows = []
    for path in sorted(set(old_rows) | INPUTS):
        digest = host.sha(snapshot / path)
        require(path in INPUTS or old_rows[path]['sha256'] == digest, 'all old owner bytes unchanged')
        rows.append(dict(path=path, sha256=digest, owner='WBS-P018-09', sharedReference='WBS-C07', sharedAdditionalCostPp=0, relationship='CURRENT_API_SYSTEM_SOURCE_OR_EXPLICIT_DEPENDENCY' if path in INPUTS or path in current['sourceFiles'] else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION', sourceUnchanged=path not in INPUTS))
    require(len(rows) == 193, 'all193 source owners')
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

    require(proofs['sdkTypes']['actualExit'] == 0 and proofs['sdkTypes']['metadataOnly'] and proofs['sdkTypes']['productTestsExecuted'] == 0, 'independent fixed SDK CPU-FD name/type/unit mapping, not product PT')
    field_receipt, field_text = steps.step('state-fields', [str(architecture.JAVA.with_name('javap')), '-p', '-s', '-constants', str(snapshot / MAIN.replace('/src/main/java/', '/target/classes/').replace('.java', '.class'))])
    require(field_receipt['actualExit'] == 0, 'compiled field metadata terminal')
    fields = state_fields(field_text)
    field_rejected = []
    for name, mutant in (
        ('retained-source', field_text.replace('  public dev.codex.schubert.nk.api.monitoring.ApiSystemMetrics();', '  private final io.micrometer.core.instrument.MeterRegistry source;\n    descriptor: Lio/micrometer/core/instrument/MeterRegistry;\n  public dev.codex.schubert.nk.api.monitoring.ApiSystemMetrics();')),
        ('public-count', field_text.replace('private static final int', 'public static final int', 1)),
        ('wrong-descriptor', field_text.replace('descriptor: I', 'descriptor: J', 1)),
        ('wrong-count', field_text.replace('BINDER_COUNT = 2;', 'BINDER_COUNT = 3;', 1))):
        try:
            state_fields(mutant)
        except ValueError:
            field_rejected.append(name)
        else:
            raise ValueError('every current state-field negative rejects')
    require(len(field_rejected) == 4, 'four exact field contract negatives, not PT count')

    classes = SLOT / 'audit-classes'
    classes.mkdir()
    compiled, _ = steps.step('architecture-compile', [str(architecture.JAVAC), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', os.pathsep.join([str(architecture.ARCH), str(architecture.SLF)]), '-d', str(classes), str(architecture.SOURCE)])
    require(compiled['actualExit'] == 0, 'architecture reader compile')
    checked, text = steps.step('architecture-six', [str(architecture.JAVA), '-cp', os.pathsep.join([str(classes), str(architecture.ARCH), str(architecture.SLF)]), 'ModuleDependencyAudit', *[m + '=' + normal['jars'][m]['path'] for m in architecture.MODULES]])
    analysis = architecture.parse(text)
    require(checked['actualExit'] == 0 and analysis['physical'] == 1818 and not analysis['findings'] and len(analysis['rules']) == 5 and all(v == 0 for v in analysis['rules'].values()), 'all1818 and five actual architecture edges zero')
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all source inputs unchanged after reader')
    verify(invocation)
    value = dict(actualExit=0, source=SOURCE, invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), witnesses=pins, physicalClasses=physical, allPhysicalClassCount=1818, physicalAdded=[CLASS], physicalChanged={}, physicalRemoved=[], previousPhysicalUnchanged=1817, originalPhysicalUnchanged=1669, sourceRows=rows, sourceCount=193, currentTests=14, currentSuites=1, currentExecutableScope=sorted(current['executableClasses']), currentCounters=current['counters'], ownerGuardBinding=dict(newOwner=owner, newNegativeGuards=rejected, exactFields=fields, instanceFieldCount=0, fieldReceipt=field_receipt, fieldNegatives=field_rejected, priorAllInputsByteIdentical=True, priorRoleGuardsReplayed=False, bootstrapSourcesUnchanged=34, descriptorsUnchanged=True, metadataOnly=True), architecture=dict(result=analysis, compileReceipt=compiled, receipt=checked, targetInitialized=False), productTestsExecutedByPost=0, coverageUnion=False, sourceByteOnlyRowsNotCurrentPtPass=True, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, physical=1818, sourceOwners=193, newResponsibilityNegatives=len(rejected), architecture=analysis['rules'], manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
