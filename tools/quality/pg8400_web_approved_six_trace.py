"""Exact Web four-input approved join; all physical/role bindings without product replay."""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg8388_metric_identity_six_trace as previous
from host_tool_invocation import capture, verify

host, architecture, steps = previous.host, previous.architecture, previous.steps
require = previous.base.require
SOURCE = 'b347581d26d925885a4cb882eeb2326449eded94'
BEFORE = 'f775f095c0721340c20376b8d37d8baa2e97bc21'
COMPILE = host.W / 'pg8394-web-approved-six-compile-v1'
SLOT = host.W / 'pg8400-web-approved-six-trace-v1'
OUT = host.BASE / 'PG8400-web-approved-six-trace-v1'
WEB = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/'
NAMES = ('WebCounterMetricExporter', 'WebGaugeMetricExporter', 'WebDurationMetricExporter', 'WebMetricCatalog')
CHANGED = {WEB + name + '.java' for name in NAMES}
CLASSES = {'web:dev/codex/schubert/nk/web/monitoring/' + name + '.class' for name in NAMES}
WITNESSES = (
    ('normal', 'PG8394-web-approved-six-compile-v1/manifest.json', '6dd0204d10bb95888fed9693cb864685f37fb34323b0a54c5ec801413eda51fe'),
    ('current', 'PG8398-web-approved-post-v1/manifest.json', 'db9e85e36caffcf0e48515f128dd98cfb120c269617db12b778543ab8c582a74'),
    ('priorNormal', 'PG8382-metric-identity-six-compile-v1/manifest.json', '3e5b5fa6e22805dde3d851e880ba74d27713b854e7aa1d9aa694fa94669f73b5'),
    ('priorTrace', 'PG8388-metric-identity-six-trace-v1/manifest.json', '746732b59daf1d0aebb1ba090b8997df3df185ee3a80e8680563d34c11d58ee4'),
    ('original', 'PG6930-current4222-cases/qualification.json', '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
    ('architecture', 'PG6960-archunit-static-v1/manifest.json', '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'))


def main():
    invocation = capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(), 'new-only approved Web physical/owner proof')
    proofs, pins = {}, {}
    for name, path, digest in WITNESSES:
        require(host.sha(host.BASE / path) == digest, 'immutable ' + name + ' witness')
        proofs[name] = json.loads((host.BASE / path).read_text())
        pins[name] = dict(path=path, sha256=digest)
    normal, current, prior = proofs['normal'], proofs['current'], proofs['priorNormal']
    require(normal['source'] == current['source'] == SOURCE and normal['actualExit'] == normal['terminal']['actualExit'] == current['actualExit'] == 0 and normal['testsExecuted'] == 0, 'same-source genuinely successful normal/scoped quality')
    require(current['tests'] == 96 and current['suites'] == 9 and len(current['executableClasses']) == 5 and current['actualCrcMismatch'] == 0 and current['actualSessions'] == 1 and not current['coverageUnion'] and all(v['missed'] == 0 for v in current['counters'].values()), 'one original96/9 five classes four100')
    snapshot = COMPILE / 'snapshot'
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all current/frozen source inputs')
    require(prior['source'] == proofs['priorTrace']['source'] == BEFORE and prior['actualExit'] == proofs['priorTrace']['actualExit'] == 0 and set(prior['begin']['inputHashes']) == set(normal['begin']['inputHashes']), 'exact prior source/input namespace')
    require({p for p, h in prior['begin']['inputHashes'].items() if normal['begin']['inputHashes'][p] != h} == CHANGED, 'only four Web Main inputs changed; API/Bootstrap/POM/tests unchanged')
    before_catalog = subprocess.check_output(['git', 'show', BEFORE + ':' + WEB + 'WebMetricCatalog.java'], cwd=host.ROOT, text=True)
    after_catalog = (snapshot / (WEB + 'WebMetricCatalog.java')).read_text()
    domain = lambda text: text[text.index('  private static final String HTTP'):text.index('  public WebMetricCatalog()')]
    require(domain(before_catalog) == domain(after_catalog), 'exact same fixed seven-family type/name/key/value definitions')
    old, physical = previous.base.inventory(prior), previous.base.inventory(normal)
    require(len(old) == len(physical) == 1805 and set(old) == set(physical), 'same complete1805 physical namespace')
    changed = {p: dict(beforeSha256=old[p], sha256=h) for p, h in physical.items() if old[p] != h}
    require(set(changed) == CLASSES, 'only Web three exporters/catalog changed; all other1801 raw/debug identical')
    original = proofs['original']['allPhysicalMainSha256']
    require(len(original) == 1669 and all(physical[p] == h for p, h in original.items()), 'original1669 same byte, not current qualification')
    require(all(physical['web:' + p] == h for p, h in current['physicalClasses'].items()), 'all current Web physical owners')
    parts = subprocess.check_output(['git', 'diff', '--no-renames', '--name-status', '-z', BEFORE, SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts) == 8 and {parts[n + 1].decode(): parts[n].decode() for n in range(0, len(parts), 2)} == {p: 'M' for p in CHANGED}, 'four exact additive-API/factor source paths only')
    old_rows = {r['path']: r for r in proofs['priorTrace']['sourceRows']}
    require(len(old_rows) == 167 and CHANGED <= set(old_rows), 'all167 existing owners')
    rows = []
    for path in sorted(old_rows):
        digest = host.sha(snapshot / path)
        require(path in CHANGED or old_rows[path]['sha256'] == digest, 'all other163 source owner bytes unchanged')
        rows.append(dict(path=path, sha256=digest, owner='WBS-P018-09', sharedReference='WBS-C07', sharedAdditionalCostPp=0, relationship='CURRENT_WEB_SCOPED_SOURCE_OR_DEPENDENCY' if path in current['sourceFiles'] else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION', sourceUnchanged=path not in CHANGED))
    role_guard = proofs['priorTrace']['ownerGuardBinding']
    require(host.sha(host.ROOT / 'tools/quality/pg8388_metric_identity_six_trace.py') == proofs['priorTrace']['invocation']['entrypointSha256'], 'same measured responsibility validation code')
    model = copy.deepcopy(role_guard['currentRoles'])
    for role in ('api', 'web', 'bootstrap'):
        parsed = previous.contract.pom((snapshot / ('src/schubert-nk-' + role + '/pom.xml')).read_bytes())
        require(parsed['artifact'] == model[role]['artifact'] and parsed['dependencies'] == [tuple(r) for r in model[role]['dependencies']], 'all original descriptors/limited SDK responsibility/test-only edge')
        model[role].update(parsed)
    model['web']['java'] = previous.contract.java((snapshot / (WEB + 'WebDurationMetricExporter.java')).read_text())
    extras = {name: previous.contract.java((snapshot / (WEB + name + '.java')).read_text()) for name in ('WebCounterMetricExporter', 'WebGaugeMetricExporter')}
    previous.validate_owners(model, extras)
    catalog = previous.contract.java(after_catalog)
    require(catalog['type'] == 'WebMetricCatalog' and catalog['package'] == 'dev.codex.schubert.nk.web.monitoring' and not any(p.startswith(('dev.codex.schubert.nk.api.', 'dev.codex.schubert.nk.batch.', 'dev.codex.schubert.nk.bootstrap.')) for p in catalog['imports']), 'Web-only immutable catalog owner, no app/shared responsibility expansion')
    rejected = []
    for name, mutate in (
        ('web-api-production', lambda m, x: m['web']['dependencies'].append(('dev.codex.schubert', 'schubert-nk-api', '0.1.0-SNAPSHOT', 'compile'))),
        ('bootstrap-sdk', lambda m, x: m['bootstrap']['dependencies'].append(('io.prometheus', 'prometheus-metrics-exposition-textformats', '1.7.0', 'compile'))),
        ('web-duration-owner', lambda m, x: m['web']['java'].update(package='dev.codex.schubert.nk.api.monitoring')),
        ('web-counter-owner', lambda m, x: x['WebCounterMetricExporter'].update(package='dev.codex.schubert.nk.bootstrap.monitoring')),
        ('web-gauge-type', lambda m, x: x['WebGaugeMetricExporter'].update(imports=['io.micrometer.core.instrument.Timer']))):
        m, x = copy.deepcopy(model), copy.deepcopy(extras)
        mutate(m, x)
        try:
            previous.validate_owners(m, x)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('all current role metadata negatives must reject')
    require(len(rejected) == 5 and role_guard['bootstrapSourcesUnchanged'] == 34, 'five current negatives/all limited Bootstrap source inputs unchanged')
    require(host.sha(architecture.SOURCE) == proofs['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH) == architecture.ARCH_SHA and host.sha(architecture.SLF) == architecture.SLF_SHA, 'unchanged canary-qualified bytecode reader')
    SLOT.mkdir()
    steps.SLOT = SLOT
    classes = SLOT / 'audit-classes'
    classes.mkdir()
    compiled, _ = steps.step('architecture-compile', [str(architecture.JAVAC), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', os.pathsep.join([str(architecture.ARCH), str(architecture.SLF)]), '-d', str(classes), str(architecture.SOURCE)])
    require(compiled['actualExit'] == 0, 'architecture reader compile')
    checked, text = steps.step('architecture-six', [str(architecture.JAVA), '-cp', os.pathsep.join([str(classes), str(architecture.ARCH), str(architecture.SLF)]), 'ModuleDependencyAudit', *[m + '=' + normal['jars'][m]['path'] for m in architecture.MODULES]])
    analysis = architecture.parse(text)
    require(checked['actualExit'] == 0 and analysis['physical'] == 1805 and not analysis['findings'] and len(analysis['rules']) == 5 and all(v == 0 for v in analysis['rules'].values()), 'all1805/five actual edges zero')
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all source inputs unchanged after static reader')
    verify(invocation)
    value = dict(actualExit=0, source=SOURCE, invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), witnesses=pins, physicalClasses=physical, allPhysicalClassCount=1805, physicalAdded=[], physicalRemoved=[], physicalChanged=changed, previousPhysicalUnchanged=1801, originalPhysicalUnchanged=1669, sourceRows=rows, sourceCount=167, currentTests=96, currentSuites=9, currentExecutableScope=sorted(current['executableClasses']), currentCounters=current['counters'], fixedSevenFamilyDomainUnchanged=True, ownerGuardBinding=dict(currentRoles=model, extraWebTypes=extras, catalog=catalog, newNegativeGuards=rejected, bootstrapSourcesUnchanged=34, descriptorsUnchanged=True, metadataOnly=True), architecture=dict(result=analysis, compileReceipt=compiled, receipt=checked, targetInitialized=False), productTestsExecutedByPost=0, coverageUnion=False, sourceByteOnlyRowsNotCurrentPtPass=True, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, physical=1805, sourceOwners=167, responsibilityNegatives=len(rejected), architecture=analysis['rules'], manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
