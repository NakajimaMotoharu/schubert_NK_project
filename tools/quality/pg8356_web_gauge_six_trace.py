"""All prior source/bytes unchanged, one new Web Gauge with current-scope quality/ownership."""
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
SOURCE = 'e1ba2ccc51f1f24bd48d74e3b906b48489473a39'
BEFORE = '6c91f378543e9c1cbfa0c8a9dd3115f91cbbdccb'
COMPILE = host.W / 'pg8350-web-gauge-six-compile-v1'
SLOT = host.W / 'pg8356-web-gauge-six-trace-v1'
OUT = host.BASE / 'PG8356-web-gauge-six-trace-v1'
MAIN = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/WebGaugeMetricExporter.java'
INPUTS = {MAIN, MAIN.replace('/main/', '/test/').replace('.java', 'Test.java')}
CLASS = 'web:dev/codex/schubert/nk/web/monitoring/WebGaugeMetricExporter.class'
WITNESSES = (
    ('normal', 'PG8350-web-gauge-six-compile-v1/manifest.json', '62abed6fa1b60fd22df54f575562c476423376acc43f4155798107c26697b05b'),
    ('current', 'PG8354-web-gauge-post-v1/manifest.json', 'bee70ede6157dad8167f2d7aa3cf36eb3dfcc23c75698513ffda1afe774b70fb'),
    ('priorNormal', 'PG8338-web-counter-fixed-six-compile-v1/manifest.json', '8d4135584a58c820674879d539153abd3813a4b9bac6168284ab245cf07c3efe'),
    ('priorTrace', 'PG8344-web-counter-six-trace-v1/manifest.json', '653ca5c6a98a4938ae9d5aed852cf8dbf7eec63f9b9e8905bf7a1a3f20f54889'),
    ('priorToolLint', 'PG8345-web-counter-tool-lint-followup-v1/manifest.json', '6a03da26ae057c439d4ed3bfefc1f45994d082636ab7fa2feaa3984e34c22c6b'),
    ('original', 'PG6930-current4222-cases/qualification.json', '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
    ('architecture', 'PG6960-archunit-static-v1/manifest.json', '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'))


def validate_owner(row):
    base.require(row['package'] == 'dev.codex.schubert.nk.web.monitoring' and row['type'] == 'WebGaugeMetricExporter', 'exact new application owner/type')
    base.require('io.micrometer.core.instrument.Gauge' in row['imports'] and not any(p.startswith(('dev.codex.schubert.nk.api.', 'dev.codex.schubert.nk.batch.', 'dev.codex.schubert.nk.bootstrap.')) or p in ('io.micrometer.core.instrument.Timer', 'io.micrometer.core.instrument.Counter') for p in row['imports']), 'Web-owned Gauge only, no shared/cross-app type mode')


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
    require(current['tests'] == 22 and current['suites'] == 2 and len(current['executableClasses']) == 2 and current['actualCrcMismatch'] == 0 and current['actualSessions'] == 1 and not current['coverageUnion'] and all(v['missed'] == 0 for v in current['counters'].values()), 'exact original22/2 and two classes four100')
    snapshot = COMPILE / 'snapshot'
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all current/frozen source input bytes')
    require(prior['source'] == proofs['priorTrace']['source'] == BEFORE and prior['actualExit'] == proofs['priorTrace']['actualExit'] == proofs['priorToolLint']['actualExit'] == 0, 'qualified prior ownership and lint followup')
    require(set(normal['begin']['inputHashes']) - set(prior['begin']['inputHashes']) == INPUTS and all(normal['begin']['inputHashes'].get(p) == h for p, h in prior['begin']['inputHashes'].items()), 'only new Main/Unit inputs, all prior production/test/POM bytes identical')
    previous, physical = base.inventory(prior), base.inventory(normal)
    require(len(previous) == 1803 and len(physical) == 1804 and set(physical) - set(previous) == {CLASS} and all(physical.get(p) == h for p, h in previous.items()), 'one new Web physical class, all previous1803 raw/debug identical')
    original = proofs['original']['allPhysicalMainSha256']
    require(len(original) == 1669 and all(physical[p] == h for p, h in original.items()), 'original1669 byte identity is not current PT transfer')
    require(all(physical['web:' + p] == h for p, h in current['physicalClasses'].items()), 'all selected physical owner bytes')
    parts = subprocess.check_output(['git', 'diff', '--no-renames', '--name-status', '-z', BEFORE, SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts) == 4 and {parts[n + 1].decode(): parts[n].decode() for n in range(0, len(parts), 2)} == {p: 'A' for p in INPUTS}, 'exact two additive source paths')
    old_rows = {r['path']: r for r in proofs['priorTrace']['sourceRows']}
    require(len(old_rows) == 163 and not (set(old_rows) & INPUTS), 'complete prior163 source owners')
    rows = []
    for path in sorted(set(old_rows) | INPUTS):
        digest = host.sha(snapshot / path)
        require(path in INPUTS or old_rows[path]['sha256'] == digest, 'all old owner bytes unchanged')
        rows.append(dict(path=path, sha256=digest, owner='WBS-P018-09', sharedReference='WBS-C07', sharedAdditionalCostPp=0, relationship='CURRENT_GAUGE_SOURCE_OR_EXPLICIT_DEPENDENCY' if path in INPUTS or path in current['sourceFiles'] else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION', sourceUnchanged=path not in INPUTS))
    require(len(rows) == 165, 'all165 source owners')
    owner = contract.java((snapshot / MAIN).read_text())
    validate_owner(owner)
    rejected = []
    for name, change in (('other-app', lambda x: x.update(package='dev.codex.schubert.nk.api.monitoring')), ('shared-bootstrap-import', lambda x: x['imports'].append('dev.codex.schubert.nk.bootstrap.monitoring.FORBIDDEN_FIXTURE_ONLY')), ('wrong-observation-type', lambda x: x['imports'].append('io.micrometer.core.instrument.Timer'))):
        mutant = copy.deepcopy(owner)
        change(mutant)
        try:
            validate_owner(mutant)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('new owner metadata negatives must reject')
    require(len(rejected) == 3 and proofs['priorTrace']['ownerGuardBinding']['unchangedBootstrapSources'] == 34 and len(proofs['priorTrace']['ownerGuardBinding']['currentNegativeGuards']) == 10, 'new three negatives plus all prior role inputs byte identity; no old mutant replay')
    require(host.sha(architecture.SOURCE) == proofs['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH) == architecture.ARCH_SHA and host.sha(architecture.SLF) == architecture.SLF_SHA, 'same canary-qualified noninitializing bytecode reader')
    SLOT.mkdir()
    steps.SLOT = SLOT
    classes = SLOT / 'audit-classes'
    classes.mkdir()
    compiled, _ = steps.step('architecture-compile', [str(architecture.JAVAC), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', os.pathsep.join([str(architecture.ARCH), str(architecture.SLF)]), '-d', str(classes), str(architecture.SOURCE)])
    require(compiled['actualExit'] == 0, 'architecture reader compile')
    checked, text = steps.step('architecture-six', [str(architecture.JAVA), '-cp', os.pathsep.join([str(classes), str(architecture.ARCH), str(architecture.SLF)]), 'ModuleDependencyAudit', *[m + '=' + normal['jars'][m]['path'] for m in architecture.MODULES]])
    analysis = architecture.parse(text)
    require(checked['actualExit'] == 0 and analysis['physical'] == 1804 and not analysis['findings'] and len(analysis['rules']) == 5 and all(v == 0 for v in analysis['rules'].values()), 'all1804 and five actual architecture edges zero')
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all source inputs unchanged after reader')
    verify(invocation)
    value = dict(actualExit=0, source=SOURCE, invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), witnesses=pins, physicalClasses=physical, allPhysicalClassCount=1804, physicalAdded=[CLASS], physicalChanged={}, physicalRemoved=[], previousPhysicalUnchanged=1803, originalPhysicalUnchanged=1669, sourceRows=rows, sourceCount=165, currentTests=22, currentSuites=2, currentExecutableScope=sorted(current['executableClasses']), currentCounters=current['counters'], ownerGuardBinding=dict(newOwner=owner, newNegativeGuards=rejected, priorAllInputsByteIdentical=True, priorRoleGuardsReplayed=False, bootstrapSourcesUnchanged=34, descriptorsUnchanged=True, metadataOnly=True), architecture=dict(result=analysis, compileReceipt=compiled, receipt=checked, targetInitialized=False), productTestsExecutedByPost=0, coverageUnion=False, sourceByteOnlyRowsNotCurrentPtPass=True, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, physical=1804, sourceOwners=165, newResponsibilityNegatives=len(rejected), architecture=analysis['rules'], manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
