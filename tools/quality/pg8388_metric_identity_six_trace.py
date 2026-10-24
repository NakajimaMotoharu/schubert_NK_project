"""BUG1701 exact four name-copy repairs, full physical and current responsibility closure."""
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
SOURCE = 'f775f095c0721340c20376b8d37d8baa2e97bc21'
BEFORE = 'e5f0ae543177ccd5f399e58d8588092868466f8e'
COMPILE = host.W / 'pg8382-metric-identity-six-compile-v1'
SLOT = host.W / 'pg8388-metric-identity-six-trace-v1'
OUT = host.BASE / 'PG8388-metric-identity-six-trace-v1'
API = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiDurationMetricExporter.java'
WEB = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/'
CHANGED = {API, *[WEB + name + '.java' for name in ('WebCounterMetricExporter', 'WebGaugeMetricExporter', 'WebDurationMetricExporter')]}
CLASSES = {'api:dev/codex/schubert/nk/api/monitoring/ApiDurationMetricExporter.class', *['web:dev/codex/schubert/nk/web/monitoring/' + name + '.class' for name in ('WebCounterMetricExporter', 'WebGaugeMetricExporter', 'WebDurationMetricExporter')]}
WITNESSES = (
    ('normal', 'PG8382-metric-identity-six-compile-v1/manifest.json', '3e5b5fa6e22805dde3d851e880ba74d27713b854e7aa1d9aa694fa94669f73b5'),
    ('current', 'PG8386-metric-identity-post-v1/manifest.json', '9c32ed6d3cc5addb8319c943241e360053d4c12d03050342a88bbb5d7531febf'),
    ('priorNormal', 'PG8368-web-catalog-fixed-six-compile-v1/manifest.json', '0081b454a19a70df71693d96bb1e8d5dccf5ebad339ea34ad25c8fe343bde28f'),
    ('priorTrace', 'PG8374-web-catalog-six-trace-v1/manifest.json', '4349c8d94461c1ce21f3b2790a866e2366ed4638d4ba961d17a2728412f0a390'),
    ('ownerOriginal', 'PG8317-app-duration-owner-guard-v1/manifest.json', '5e83ac7eed1e7dc6c04cf3190044ad6096899ce2163cff92f3a6a33d85471e4d'),
    ('reproduction', 'PG8380-metric-identity-host-v1/manifest.json', 'dd3b3b9e8c22a229483d02ee826525d16def51ab881832b8fcc2c85bdfe3ab09'),
    ('original', 'PG6930-current4222-cases/qualification.json', '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
    ('architecture', 'PG6960-archunit-static-v1/manifest.json', '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'))


def validate_owners(model, extras):
    contract.validate(model)
    base.require(set(extras) == {'WebCounterMetricExporter', 'WebGaugeMetricExporter'}, 'two exact additional typed Web exporters')
    for name, row in extras.items():
        base.require(row['package'] == 'dev.codex.schubert.nk.web.monitoring' and row['type'] == name, 'Web-only extra exporter owner')
        base.require(not any(p.startswith(('dev.codex.schubert.nk.api.', 'dev.codex.schubert.nk.batch.', 'dev.codex.schubert.nk.bootstrap.')) for p in row['imports']), 'no extra app/shared Bootstrap edge')
        wanted = 'Counter' if name == 'WebCounterMetricExporter' else 'Gauge'
        base.require('io.micrometer.core.instrument.' + wanted in row['imports'], 'fixed correct additional observation type')


def main():
    invocation = capture(Path(__file__))
    require = base.require
    require(not SLOT.exists() and not OUT.exists(), 'new-only current full proof')
    proofs, pins = {}, {}
    for name, path, digest in WITNESSES:
        require(host.sha(host.BASE / path) == digest, 'immutable ' + name + ' witness')
        proofs[name] = json.loads((host.BASE / path).read_text())
        pins[name] = dict(path=path, sha256=digest)
    normal, current, prior = proofs['normal'], proofs['current'], proofs['priorNormal']
    require(normal['source'] == current['source'] == SOURCE and normal['actualExit'] == normal['terminal']['actualExit'] == current['actualExit'] == 0 and normal['testsExecuted'] == 0, 'same source real compile/qualification')
    require(current['tests'] == 100 and current['suites'] == 9 and len(current['executableClasses']) == 5 and current['actualCrcMismatch'] == 0 and current['actualSessions'] == 1 and not current['coverageUnion'] and all(v['missed'] == 0 for v in current['counters'].values()), 'one original100/9 exact five classes four100')
    require(proofs['reproduction']['source'] == BEFORE and proofs['reproduction']['actualExit'] == 1 and len(proofs['reproduction']['cases']) == 4 and all(r['result'] == 'NOT_PASS' for r in proofs['reproduction']['cases']), 'original four failures preserved')
    snapshot = COMPILE / 'snapshot'
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all current/frozen normal input bytes')
    require(prior['source'] == proofs['priorTrace']['source'] == BEFORE and prior['actualExit'] == proofs['priorTrace']['actualExit'] == 0 and set(prior['begin']['inputHashes']) == set(normal['begin']['inputHashes']), 'same complete prior input namespace')
    require({p for p, h in prior['begin']['inputHashes'].items() if normal['begin']['inputHashes'][p] != h} == CHANGED, 'only four existing Main paths changed; all tests/config/POM unchanged')
    for path in CHANGED:
        old = subprocess.check_output(['git', 'show', BEFORE + ':' + path], cwd=host.ROOT)
        expected = old.replace(b'      var keys = namespace.get(id.getName());', b'      String name = Objects.requireNonNull(id.getName(), "metric name");\n      var keys = namespace.get(name);').replace(b'.computeIfAbsent(id.getName(),', b'.computeIfAbsent(name,')
        require(old.count(b'id.getName()') == 2 and (snapshot / path).read_bytes() == expected and expected.count(b'id.getName()') == 1, 'exact one-name-copy mechanical repair only')
    previous, physical = base.inventory(prior), base.inventory(normal)
    changed = {p: dict(beforeSha256=previous[p], sha256=physical[p]) for p in previous if previous[p] != physical[p]}
    require(len(previous) == len(physical) == 1805 and set(previous) == set(physical) and set(changed) == CLASSES, 'all1805 exact four app repairs, other1801 raw/debug identical')
    original = proofs['original']['allPhysicalMainSha256']
    require(len(original) == 1669 and all(physical[p] == h for p, h in original.items()), 'original1669 same byte, no PT transfer')
    require(all(physical[current['classModules'].get(p.removesuffix('.class'), 'api') + ':' + p] == h for p, h in current['physicalClasses'].items()), 'all current component physical owners')
    parts = subprocess.check_output(['git', 'diff', '--no-renames', '--name-status', '-z', BEFORE, SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts) == 8 and {parts[n + 1].decode(): parts[n].decode() for n in range(0, len(parts), 2)} == {p: 'M' for p in CHANGED}, 'four exact source delta paths')
    old_rows = {r['path']: r for r in proofs['priorTrace']['sourceRows']}
    require(len(old_rows) == 167 and CHANGED <= set(old_rows), 'all existing167 source owners')
    rows = []
    for path in sorted(old_rows):
        digest = host.sha(snapshot / path)
        require(path in CHANGED or old_rows[path]['sha256'] == digest, 'all other163 source owner bytes unchanged')
        rows.append(dict(path=path, sha256=digest, owner='WBS-P018-09', sharedReference='WBS-C07', sharedAdditionalCostPp=0, relationship='CURRENT_SCOPED_SOURCE_OR_DEPENDENCY' if path in CHANGED or path in current['sourceFiles'] else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION', sourceUnchanged=path not in CHANGED))
    model = copy.deepcopy(proofs['ownerOriginal']['ownerModel'])
    for role in ('api', 'web', 'bootstrap'):
        parsed = contract.pom((snapshot / ('src/schubert-nk-' + role + '/pom.xml')).read_bytes())
        require(parsed['artifact'] == model[role]['artifact'] and parsed['dependencies'] == [tuple(r) for r in model[role]['dependencies']], 'original exact app SDK/test-only edge/limited Bootstrap descriptors')
        model[role].update(parsed)
    model['api']['java'] = contract.java((snapshot / API).read_text())
    model['web']['java'] = contract.java((snapshot / (WEB + 'WebDurationMetricExporter.java')).read_text())
    extras = {name: contract.java((snapshot / (WEB + name + '.java')).read_text()) for name in ('WebCounterMetricExporter', 'WebGaugeMetricExporter')}
    validate_owners(model, extras)
    rejected = []
    for name, mutate in (
        ('bootstrap-sdk', lambda m, x: m['bootstrap']['dependencies'].append(('io.prometheus', 'prometheus-metrics-exposition-textformats', '1.7.0', 'compile'))),
        ('web-api-production', lambda m, x: m['web']['dependencies'].append(('dev.codex.schubert', 'schubert-nk-api', '0.1.0-SNAPSHOT', 'compile'))),
        ('api-web-production', lambda m, x: m['api']['dependencies'].append(('dev.codex.schubert', 'schubert-nk-web', '0.1.0-SNAPSHOT', 'compile'))),
        ('api-wrong-type', lambda m, x: m['api']['java'].update(imports=['io.micrometer.core.instrument.Timer'])),
        ('web-duration-owner', lambda m, x: m['web']['java'].update(package='dev.codex.schubert.nk.bootstrap.monitoring')),
        ('web-counter-owner', lambda m, x: x['WebCounterMetricExporter'].update(package='dev.codex.schubert.nk.api.monitoring')),
        ('web-gauge-type', lambda m, x: x['WebGaugeMetricExporter'].update(imports=['io.micrometer.core.instrument.Counter']))):
        m, x = copy.deepcopy(model), copy.deepcopy(extras)
        mutate(m, x)
        try:
            validate_owners(m, x)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('all current role negatives must reject')
    require(len(rejected) == 7 and proofs['priorTrace']['ownerGuardBinding']['bootstrapSourcesUnchanged'] == 34, 'current seven negatives and all limited Bootstrap source inputs unchanged')
    require(host.sha(architecture.SOURCE) == proofs['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH) == architecture.ARCH_SHA and host.sha(architecture.SLF) == architecture.SLF_SHA, 'canary-qualified unchanged reader')
    SLOT.mkdir()
    steps.SLOT = SLOT
    classes = SLOT / 'audit-classes'
    classes.mkdir()
    compiled, _ = steps.step('architecture-compile', [str(architecture.JAVAC), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', os.pathsep.join([str(architecture.ARCH), str(architecture.SLF)]), '-d', str(classes), str(architecture.SOURCE)])
    require(compiled['actualExit'] == 0, 'noninitializing architecture reader compile')
    checked, text = steps.step('architecture-six', [str(architecture.JAVA), '-cp', os.pathsep.join([str(classes), str(architecture.ARCH), str(architecture.SLF)]), 'ModuleDependencyAudit', *[m + '=' + normal['jars'][m]['path'] for m in architecture.MODULES]])
    analysis = architecture.parse(text)
    require(checked['actualExit'] == 0 and analysis['physical'] == 1805 and not analysis['findings'] and len(analysis['rules']) == 5 and all(v == 0 for v in analysis['rules'].values()), 'all1805/five actual bytecode edges zero')
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all original inputs immutable after reader')
    verify(invocation)
    value = dict(actualExit=0, source=SOURCE, invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), witnesses=pins, physicalClasses=physical, allPhysicalClassCount=1805, physicalAdded=[], physicalRemoved=[], physicalChanged=changed, previousPhysicalUnchanged=1801, originalPhysicalUnchanged=1669, sourceRows=rows, sourceCount=167, currentTests=100, currentSuites=9, currentExecutableScope=sorted(current['executableClasses']), currentCounters=current['counters'], exactNameCopyDelta=True, ownerGuardBinding=dict(currentRoles=model, extraWebTypes=extras, newNegativeGuards=rejected, bootstrapSourcesUnchanged=34, descriptorsUnchanged=True, metadataOnly=True), architecture=dict(result=analysis, compileReceipt=compiled, receipt=checked, targetInitialized=False), productTestsExecutedByPost=0, coverageUnion=False, sourceByteOnlyRowsNotCurrentPtPass=True, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, physical=1805, sourceOwners=167, responsibilityNegatives=len(rejected), architecture=analysis['rules'], manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
