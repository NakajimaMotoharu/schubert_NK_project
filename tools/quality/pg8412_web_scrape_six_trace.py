"""One new pure Web policy, exact stateless fields/all prior bytes, no product replay."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg8388_metric_identity_six_trace as common
import web_metric_policy_field_contract as field_contract
from host_tool_invocation import capture, verify

host, architecture, steps = common.host, common.architecture, common.steps
require = common.base.require
SOURCE = '8c8a8c51a166948a03510bda521a6e3930e88fa2'
BEFORE = 'b347581d26d925885a4cb882eeb2326449eded94'
COMPILE = host.W / 'pg8406-web-scrape-six-compile-v1'
SLOT = host.W / 'pg8412-web-scrape-six-trace-v1'
OUT = host.BASE / 'PG8412-web-scrape-six-trace-v1'
MAIN = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/WebMetricScrape.java'
INPUTS = {MAIN, MAIN.replace('/main/', '/test/').replace('.java', 'Test.java')}
CLASS = 'web:dev/codex/schubert/nk/web/monitoring/WebMetricScrape.class'
FIELDS = {name: 'dev.codex.schubert.nk.web.monitoring.' + type_name for name, type_name in (('gauges', 'WebGaugeMetricExporter'), ('counters', 'WebCounterMetricExporter'), ('timers', 'WebDurationMetricExporter'))}
WITNESSES = (
    ('normal', 'PG8406-web-scrape-six-compile-v1/manifest.json', '2176ef1e0b5b1e70d7f4bdd28ea797075846e10dd0a31a58b641c9de9de3789f'),
    ('current', 'PG8410-web-scrape-post-v1/manifest.json', '8cc2d19bc49c9558573a5bfa4a82bd73ccf75f599908abf6a62087270bba74ed'),
    ('priorNormal', 'PG8394-web-approved-six-compile-v1/manifest.json', '6dd0204d10bb95888fed9693cb864685f37fb34323b0a54c5ec801413eda51fe'),
    ('priorTrace', 'PG8400-web-approved-six-trace-v1/manifest.json', '5d07f62bf70dee47f9bfe64fcf57f7336ab0e0842018f53ddacd7f762ebc416f'),
    ('original', 'PG6930-current4222-cases/qualification.json', '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
    ('architecture', 'PG6960-archunit-static-v1/manifest.json', '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'))


def validate_owner(row, fields):
    require(row['package'] == 'dev.codex.schubert.nk.web.monitoring' and row['type'] == 'WebMetricScrape', 'new Web-only policy owner/type')
    require(set(row['imports']) == {'io.micrometer.core.instrument.MeterRegistry', 'java.util.Objects'} and fields == FIELDS, 'exact three stateless formatter fields, no retained source/clock/mode or IO imports')


def main():
    invocation = capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(), 'new-only stateless policy physical/owner proof')
    proofs, pins = {}, {}
    for name, path, digest in WITNESSES:
        require(host.sha(host.BASE / path) == digest, 'immutable ' + name + ' witness')
        proofs[name] = json.loads((host.BASE / path).read_text())
        pins[name] = dict(path=path, sha256=digest)
    normal, current, prior = proofs['normal'], proofs['current'], proofs['priorNormal']
    require(normal['source'] == current['source'] == SOURCE and normal['actualExit'] == normal['terminal']['actualExit'] == current['actualExit'] == 0 and normal['testsExecuted'] == 0, 'same-source real build and bounded qualification')
    require(current['tests'] == 14 and current['suites'] == 1 and len(current['executableClasses']) == 1 and current['actualCrcMismatch'] == 0 and current['actualSessions'] == 1 and not current['coverageUnion'] and all(v['missed'] == 0 for v in current['counters'].values()), 'one original14/1 exact new class four100')
    snapshot = COMPILE / 'snapshot'
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all current/frozen source inputs')
    require(prior['source'] == proofs['priorTrace']['source'] == BEFORE and prior['actualExit'] == proofs['priorTrace']['actualExit'] == 0, 'exact prior normal/trace source')
    require(set(normal['begin']['inputHashes']) - set(prior['begin']['inputHashes']) == INPUTS and all(normal['begin']['inputHashes'].get(p) == h for p, h in prior['begin']['inputHashes'].items()), 'only new Main/Unit paths, every prior source/test/POM/config byte unchanged')
    old, physical = common.base.inventory(prior), common.base.inventory(normal)
    require(len(old) == 1805 and len(physical) == 1806 and set(physical) - set(old) == {CLASS} and all(physical.get(p) == h for p, h in old.items()), 'one new physical policy class, all1805 old raw/debug bytes identical')
    original = proofs['original']['allPhysicalMainSha256']
    require(len(original) == 1669 and all(physical[p] == h for p, h in original.items()), 'original1669 byte identity, no qualification transfer')
    require(all(physical['web:' + p] == h for p, h in current['physicalClasses'].items()), 'all current component physical owners')
    parts = subprocess.check_output(['git', 'diff', '--no-renames', '--name-status', '-z', BEFORE, SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts) == 4 and {parts[n + 1].decode(): parts[n].decode() for n in range(0, len(parts), 2)} == {p: 'A' for p in INPUTS}, 'two exact additive source paths')
    old_rows = {r['path']: r for r in proofs['priorTrace']['sourceRows']}
    require(len(old_rows) == 167 and not (set(old_rows) & INPUTS), 'all167 existing source owners')
    rows = []
    for path in sorted(set(old_rows) | INPUTS):
        digest = host.sha(snapshot / path)
        require(path in INPUTS or old_rows[path]['sha256'] == digest, 'all prior owner bytes identical')
        rows.append(dict(path=path, sha256=digest, owner='WBS-P018-09', sharedReference='WBS-C07', sharedAdditionalCostPp=0, relationship='CURRENT_PURE_POLICY_SOURCE' if path in INPUTS else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION', sourceUnchanged=path not in INPUTS))
    require(len(rows) == 169 and proofs['priorTrace']['ownerGuardBinding']['bootstrapSourcesUnchanged'] == 34, 'all169 owners, limited Bootstrap and descriptors unchanged')
    require(host.sha(architecture.SOURCE) == proofs['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH) == architecture.ARCH_SHA and host.sha(architecture.SLF) == architecture.SLF_SHA, 'same canary-qualified noninitializing reader')
    SLOT.mkdir()
    steps.SLOT = SLOT
    class_file = snapshot / 'src/schubert-nk-web/target/classes/dev/codex/schubert/nk/web/monitoring/WebMetricScrape.class'
    field_receipt, body = steps.step('policy-fields', [str(architecture.JAVA.with_name('javap')), '-p', '-s', str(class_file)])
    require(field_receipt['actualExit'] == 0, 'physical field reader terminal')
    fields, methods = field_contract.verify_contract(body, FIELDS)
    field_negatives = field_contract.negative_guards(body, FIELDS)
    owner = common.contract.java((snapshot / MAIN).read_text())
    require(len(fields) == 3 and len(methods) == 2 and len(field_negatives) == 5, 'three physical fields and two method pairs/five grammar negatives')
    validate_owner(owner, fields)
    rejected = []
    for name, other_owner, other_fields in (
        ('other-app-owner', dict(owner, package='dev.codex.schubert.nk.api.monitoring'), fields),
        ('retained-source', owner, dict(fields, source='io.micrometer.core.instrument.MeterRegistry')),
        ('io-import', dict(owner, imports=owner['imports'] + ['java.net.Socket']), fields)):
        try:
            validate_owner(other_owner, other_fields)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('all new role/retention negatives must reject')
    require(len(rejected) == 3, 'three current metadata negatives only, not PT')
    classes = SLOT / 'audit-classes'
    classes.mkdir()
    compiled, _ = steps.step('architecture-compile', [str(architecture.JAVAC), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', os.pathsep.join([str(architecture.ARCH), str(architecture.SLF)]), '-d', str(classes), str(architecture.SOURCE)])
    require(compiled['actualExit'] == 0, 'architecture reader compile')
    checked, text = steps.step('architecture-six', [str(architecture.JAVA), '-cp', os.pathsep.join([str(classes), str(architecture.ARCH), str(architecture.SLF)]), 'ModuleDependencyAudit', *[m + '=' + normal['jars'][m]['path'] for m in architecture.MODULES]])
    analysis = architecture.parse(text)
    require(checked['actualExit'] == 0 and analysis['physical'] == 1806 and not analysis['findings'] and len(analysis['rules']) == 5 and all(v == 0 for v in analysis['rules'].values()), 'all1806/five actual edges zero')
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all inputs immutable after metadata reader')
    verify(invocation)
    value = dict(actualExit=0, source=SOURCE, invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), witnesses=pins, physicalClasses=physical, allPhysicalClassCount=1806, physicalAdded=[CLASS], physicalRemoved=[], physicalChanged={}, previousPhysicalUnchanged=1805, originalPhysicalUnchanged=1669, sourceRows=rows, sourceCount=169, currentTests=14, currentSuites=1, currentExecutableScope=sorted(current['executableClasses']), currentCounters=current['counters'], ownerGuardBinding=dict(newOwner=owner, exactPhysicalFields=fields, fieldReceipt=field_receipt, newNegativeGuards=rejected, priorAllInputsByteIdentical=True, bootstrapSourcesUnchanged=34, descriptorsUnchanged=True, metadataOnly=True), architecture=dict(result=analysis, compileReceipt=compiled, receipt=checked, targetInitialized=False), productTestsExecutedByPost=0, coverageUnion=False, sourceByteOnlyRowsNotCurrentPtPass=True, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, physical=1806, sourceOwners=169, responsibilityNegatives=len(rejected), architecture=analysis['rules'], manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
