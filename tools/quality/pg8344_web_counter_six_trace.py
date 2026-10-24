"""Current Web text-only delta, all physical/owner/role bindings; no product initialization."""
import copy
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import pg8302_http_cdf_six_trace as base
import duration_exposition_owner_contract as contract
from host_tool_invocation import capture, verify

host, architecture, steps = base.host, base.architecture, base.steps
SOURCE = '6c91f378543e9c1cbfa0c8a9dd3115f91cbbdccb'
BEFORE = '3968abacec2052b9e7b803702a3a9231f9209f26'
COMPILE = host.W / 'pg8338-web-counter-fixed-six-compile-v1'
SLOT = host.W / 'pg8344-web-counter-six-trace-v1'
OUT = host.BASE / 'PG8344-web-counter-six-trace-v1'
WEB = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/'
PREFIX = 'web:dev/codex/schubert/nk/web/monitoring/'
NEW_NAMES = ('WebCounterMetricExporter', 'WebMetricText')
DELTA = {WEB + name + '.java': 'A' for name in NEW_NAMES}
DELTA.update({WEB + 'WebDurationMetricExporter.java': 'M', (WEB + 'WebCounterMetricExporterTest.java').replace('/main/', '/test/'): 'A'})
POMS = {'src/schubert-nk-' + role + '/pom.xml' for role in ('api', 'web', 'bootstrap')}
WITNESSES = (
    ('normal', 'PG8338-web-counter-fixed-six-compile-v1/manifest.json', '8d4135584a58c820674879d539153abd3813a4b9bac6168284ab245cf07c3efe'),
    ('current', 'PG8342-web-counter-post-v1/manifest.json', 'd9ec1ae97dc179dd7b4f3de0c525e88a65d31c95ef77484352d19b6e9fb09346'),
    ('priorNormal', 'PG8320-app-duration-six-compile-v1/manifest.json', '873d524e75f2826777d633eaadc1888b76d47ad0913c8f74b8d957a447d8c7aa'),
    ('priorTrace', 'PG8326-app-duration-six-trace-v1/manifest.json', '6551d57bb893ebf30df9a8241cb9d64ca2a65c661fa52c939d73ad1c8bd43996'),
    ('ownerGuard', 'PG8317-app-duration-owner-guard-v1/manifest.json', '5e83ac7eed1e7dc6c04cf3190044ad6096899ce2163cff92f3a6a33d85471e4d'),
    ('original', 'PG6930-current4222-cases/qualification.json', '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
    ('architecture', 'PG6960-archunit-static-v1/manifest.json', '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'))


def validate_owners(model, extras):
    contract.validate(model)
    base.require(set(extras) == set(NEW_NAMES), 'two exact new Web-owned types')
    for name, row in extras.items():
        base.require(row['package'] == ['dev.codex.schubert.nk.web.monitoring'] and row['types'] == [name], 'new Web-only type responsibility')
        base.require(not any(value.startswith(('dev.codex.schubert.nk.api.', 'dev.codex.schubert.nk.batch.', 'dev.codex.schubert.nk.bootstrap.')) for value in row['imports']), 'no cross-app/shared Bootstrap metric import')


def main():
    invocation = capture(Path(__file__))
    require = base.require
    require(not SLOT.exists() and not OUT.exists(), 'new-only complete public metadata proof')
    proofs, pins = {}, {}
    for name, path, digest in WITNESSES:
        require(host.sha(host.BASE / path) == digest, 'immutable ' + name + ' witness')
        proofs[name] = json.loads((host.BASE / path).read_text())
        pins[name] = dict(path=path, sha256=digest)
    normal, current, prior = proofs['normal'], proofs['current'], proofs['priorNormal']
    require(normal['source'] == current['source'] == SOURCE and normal['actualExit'] == normal['terminal']['actualExit'] == current['actualExit'] == 0 and normal['testsExecuted'] == 0, 'same-source successful compile and exact scoped qualification')
    require(current['tests'] == 44 and current['suites'] == 4 and len(current['executableClasses']) == 3 and current['actualCrcMismatch'] == 0 and current['actualSessions'] == 1 and not current['coverageUnion'] and all(v['missed'] == 0 for v in current['counters'].values()), 'one original44/4 exact three classes four100')
    snapshot = COMPILE / 'snapshot'
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all frozen/current normal input bytes')
    require(prior['source'] == proofs['priorTrace']['source'] == BEFORE and prior['actualExit'] == 0, 'exact prior normal/trace source')
    previous, physical = base.inventory(prior), base.inventory(normal)
    added = {PREFIX + name + '.class' for name in NEW_NAMES}
    changed = {p: dict(beforeSha256=previous[p], sha256=physical[p]) for p in set(previous) & set(physical) if previous[p] != physical[p]}
    require(len(previous) == 1801 and len(physical) == 1803 and set(physical) - set(previous) == added and not (set(previous) - set(physical)) and set(changed) == {PREFIX + 'WebDurationMetricExporter.class'}, 'two new Web classes/one Web duration change/other1800 raw debug identical')
    original = proofs['original']['allPhysicalMainSha256']
    require(len(original) == 1669 and all(physical[p] == h for p, h in original.items()), 'original1669 byte identity, never current qualification transfer')
    require(all(physical['web:' + p] == h for p, h in current['physicalClasses'].items()), 'all current scoped physical owners')
    parts = subprocess.check_output(['git', 'diff', '--no-renames', '--name-status', '-z', BEFORE, SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts) == 8 and {parts[n + 1].decode(): parts[n].decode() for n in range(0, len(parts), 2)} == DELTA, 'exact four source delta paths')
    old_rows = {r['path']: r for r in proofs['priorTrace']['sourceRows']}
    require(len(old_rows) == 160 and len(set(DELTA) - set(old_rows)) == 3, 'three new source owners only')
    rows = []
    for path in sorted(set(old_rows) | set(DELTA)):
        digest = host.sha(snapshot / path)
        require(path in DELTA or old_rows[path]['sha256'] == digest, 'all other source owners unchanged')
        rows.append(dict(path=path, sha256=digest, owner='WBS-P018-09', sharedReference='WBS-C07', sharedAdditionalCostPp=0, relationship='CURRENT_WEB_SCOPED_SOURCE_OR_DEPENDENCY' if path in DELTA else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION', sourceUnchanged=path not in DELTA))
    require(len(rows) == 163 and all(prior['begin']['inputHashes'][p] == normal['begin']['inputHashes'][p] for p in POMS), 'all163 source owners/three descriptors unchanged')
    guard = proofs['ownerGuard']
    require(guard['actualExit'] == 0 and guard['productionPT'] == guard['productClassInitialization'] == 0 and len(guard['negativeGuards']) == 9 and guard['bootstrapSources'] == 34, 'original limited guard provenance')
    require(host.sha(host.ROOT / 'tools/quality/duration_exposition_owner_contract.py') == guard['invocation']['loadedProjectPythonSources']['tools/quality/duration_exposition_owner_contract.py'], 'same responsibility contract algorithm')
    for path, digest in guard['sourceHashes'].items():
        require(path == WEB + 'WebDurationMetricExporter.java' or host.sha(snapshot / path) == digest, 'all unchanged Bootstrap/API responsibility inputs')
    model = copy.deepcopy(guard['ownerModel'])
    for role in ('bootstrap', 'api', 'web'):
        parsed = contract.pom((snapshot / ('src/schubert-nk-' + role + '/pom.xml')).read_bytes())
        require(parsed['artifact'] == model[role]['artifact'] and parsed['dependencies'] == [tuple(r) for r in model[role]['dependencies']], 'exact original descriptor responsibilities/test-only edge')
        model[role].update(parsed)
    model['web']['java'] = contract.java((snapshot / (WEB + 'WebDurationMetricExporter.java')).read_text())
    extras = {}
    for name in NEW_NAMES:
        value = (snapshot / (WEB + name + '.java')).read_text()
        extras[name] = dict(package=re.findall(r'^package ([A-Za-z0-9_.]+);$', value, re.M), types=re.findall(r'^(?:public )?final class ([A-Za-z0-9_]+)', value, re.M), imports=re.findall(r'^import ([A-Za-z0-9_.]+);$', value, re.M))
    validate_owners(model, extras)
    rejected = []
    mutations = (
        ('bootstrap-sdk', lambda m, x: m['bootstrap']['dependencies'].append(('io.prometheus', 'prometheus-metrics-exposition-textformats', '1.7.0', 'compile'))),
        ('bootstrap-java', lambda m, x: m['bootstrap']['metricJavaImports'].append('FORBIDDEN_FIXTURE_ONLY')),
        ('bootstrap-package', lambda m, x: m['bootstrap']['legacyMonitoringPaths'].append('FORBIDDEN_FIXTURE_ONLY')),
        ('web-api-production', lambda m, x: m['web']['dependencies'].append(('dev.codex.schubert', 'schubert-nk-api', '0.1.0-SNAPSHOT', 'compile'))),
        ('api-web-production', lambda m, x: m['api']['dependencies'].append(('dev.codex.schubert', 'schubert-nk-web', '0.1.0-SNAPSHOT', 'compile'))),
        ('app-sdk-missing', lambda m, x: m['web'].update(dependencies=[])),
        ('api-unit-swapped', lambda m, x: m['api']['java'].update(imports=['io.micrometer.core.instrument.Timer'])),
        ('duration-owner-swapped', lambda m, x: m['web']['java'].update(package='dev.codex.schubert.nk.bootstrap.monitoring')),
        ('new-counter-owner', lambda m, x: x['WebCounterMetricExporter'].update(package=['dev.codex.schubert.nk.api.monitoring'])),
        ('new-helper-import', lambda m, x: x['WebMetricText']['imports'].append('dev.codex.schubert.nk.bootstrap.monitoring.FORBIDDEN_FIXTURE_ONLY')))
    for name, mutation in mutations:
        m, x = copy.deepcopy(model), copy.deepcopy(extras)
        mutation(m, x)
        try:
            validate_owners(m, x)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('all current responsibility negatives must reject')
    require(len(rejected) == 10, 'ten changed-source responsibility negatives, metadata only')
    require(host.sha(architecture.SOURCE) == proofs['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH) == architecture.ARCH_SHA and host.sha(architecture.SLF) == architecture.SLF_SHA, 'original canary-qualified static bytecode reader')
    SLOT.mkdir()
    steps.SLOT = SLOT
    classes = SLOT / 'audit-classes'
    classes.mkdir()
    compiled, _ = steps.step('architecture-compile', [str(architecture.JAVAC), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', os.pathsep.join([str(architecture.ARCH), str(architecture.SLF)]), '-d', str(classes), str(architecture.SOURCE)])
    require(compiled['actualExit'] == 0, 'noninitializing architecture reader compilation')
    checked, text = steps.step('architecture-six', [str(architecture.JAVA), '-cp', os.pathsep.join([str(classes), str(architecture.ARCH), str(architecture.SLF)]), 'ModuleDependencyAudit', *[m + '=' + normal['jars'][m]['path'] for m in architecture.MODULES]])
    analysis = architecture.parse(text)
    require(checked['actualExit'] == 0 and analysis['physical'] == 1803 and not analysis['findings'] and len(analysis['rules']) == 5 and all(v == 0 for v in analysis['rules'].values()), 'all1803/five actual bytecode edges zero')
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all original inputs unchanged after metadata check')
    verify(invocation)
    value = dict(actualExit=0, source=SOURCE, invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), witnesses=pins, physicalClasses=physical, allPhysicalClassCount=1803, physicalAdded=sorted(added), physicalRemoved=[], physicalChanged=changed, previousPhysicalUnchanged=1800, originalPhysicalUnchanged=1669, sourceRows=rows, sourceCount=163, currentTests=44, currentSuites=4, currentExecutableScope=sorted(current['executableClasses']), currentCounters=current['counters'], ownerGuardBinding=dict(priorSource=guard['source'], unchangedBootstrapSources=34, descriptorsUnchanged=True, currentWebValidated=True, newWebTypes=extras, currentNegativeGuards=rejected, metadataOnly=True), architecture=dict(result=analysis, compileReceipt=compiled, receipt=checked, targetInitialized=False), productTestsExecutedByPost=0, coverageUnion=False, sourceByteOnlyRowsNotCurrentPtPass=True, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, physical=1803, sourceOwners=163, responsibilityNegatives=len(rejected), architecture=analysis['rules'], manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
