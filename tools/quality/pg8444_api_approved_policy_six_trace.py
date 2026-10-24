"""Exact API catalog/model/mode join ownership and all physical bytes; no product replay."""
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
SOURCE = '75a198d53081b2a70babc9f2497d4faddfdbd508'
BEFORE = '6143bf358a3b07c558e43aad56b8982922c3c548'
COMPILE = host.W / 'pg8438-api-approved-policy-fixed-six-compile-v1'
SLOT = host.W / 'pg8444-api-approved-policy-six-trace-v1'
OUT = host.BASE / 'PG8444-api-approved-policy-six-trace-v1'
API = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/'
PREFIX = 'api:dev/codex/schubert/nk/api/monitoring/'
NEW = {'ApiMetricCatalog', 'ApiMetricScrape'}
OLD = {'ApiDurationMetricExporter', 'ApiScalarMetricExporter'}
ADDED = {API + n + '.java' for n in NEW} | {(API + n + 'Test.java').replace('/main/', '/test/') for n in NEW}
CHANGED = {API + n + '.java' for n in OLD}
NEW_CLASSES = {PREFIX + n + '.class' for n in NEW}
OLD_CLASSES = {PREFIX + n + '.class' for n in OLD}
WITNESSES = (
    ('normal', 'PG8438-api-approved-policy-fixed-six-compile-v1/manifest.json', 'ec6c46e3d158b053cc3d958b633e6ead0ec77ebd8cb30d0d3ba14bf559544daa'),
    ('current', 'PG8442-api-approved-policy-fixed-post-v1/manifest.json', '342871a5bc73d68f190014cf3b98ee146f9820c3c76bf42cf77814c1edc1725c'),
    ('priorNormal', 'PG8418-api-scalar-six-compile-v1/manifest.json', 'cbd5b74c6409bc0c53b8732c5807661d6fe94fbf51743ba706c9018fafafeced'),
    ('priorTrace', 'PG8424-api-scalar-six-trace-v1/manifest.json', 'e21b0fed0161fed34365d35d8fc0ddf804a5c82285a283a50065e59b760c070d'),
    ('original', 'PG6930-current4222-cases/qualification.json', '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
    ('architecture', 'PG6960-archunit-static-v1/manifest.json', '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'),
    ('failedSource', 'PG8435-api-approved-policy-static-stop-v1/manifest.json', '7c9baef6cd653f62ef8fe5b5f6ad0e20e98499fddf50df0c5c0dc7a3debf7d94'))

# Independent literal complete declaration/descriptor pairs; descriptor lines are not fields.
POLICY_LINES = [
    'Compiled from "ApiMetricScrape.java"',
    'public final class dev.codex.schubert.nk.api.monitoring.ApiMetricScrape {',
    '  private static final java.lang.String STANDARD_MODE;',
    '    descriptor: Ljava/lang/String;',
    '  private static final java.lang.String DEBUG_MODE;',
    '    descriptor: Ljava/lang/String;',
    '  private final dev.codex.schubert.nk.api.monitoring.ApiScalarMetricExporter scalars;',
    '    descriptor: Ldev/codex/schubert/nk/api/monitoring/ApiScalarMetricExporter;',
    '  private final dev.codex.schubert.nk.api.monitoring.ApiDurationMetricExporter durations;',
    '    descriptor: Ldev/codex/schubert/nk/api/monitoring/ApiDurationMetricExporter;',
    '  public dev.codex.schubert.nk.api.monitoring.ApiMetricScrape();',
    '    descriptor: ()V',
    '  public java.lang.String scrape(io.micrometer.core.instrument.MeterRegistry, java.lang.String);',
    '    descriptor: (Lio/micrometer/core/instrument/MeterRegistry;Ljava/lang/String;)Ljava/lang/String;',
    '}']


def policy(text):
    require([line for line in text.splitlines() if line.strip()] == POLICY_LINES,
            'exact two constants/two stateless fields/two method descriptor pairs, no retained source')


def owners(rows):
    require(set(rows) == NEW | OLD, 'all four current API owners')
    for name, row in rows.items():
        require(row['package'] == 'dev.codex.schubert.nk.api.monitoring' and row['type'] == name,
                'same API role and exact source type')
        require(not any(p.startswith(('dev.codex.schubert.nk.web.', 'dev.codex.schubert.nk.batch.',
                                      'dev.codex.schubert.nk.bootstrap.', 'java.net.'))
                        or p in ('java.nio.file.Files', 'java.lang.ProcessBuilder') for p in row['imports']),
                'no shared/cross-app or target IO responsibility')


def main():
    invocation = capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(), 'new-only current metadata proof')
    proofs, pins = {}, {}
    for key, relative, digest in WITNESSES:
        require(host.sha(host.BASE / relative) == digest, 'immutable ' + key)
        proofs[key] = json.loads((host.BASE / relative).read_text())
        pins[key] = dict(path=relative, sha256=digest)
    normal, current, prior = proofs['normal'], proofs['current'], proofs['priorNormal']
    require(normal['source'] == current['source'] == SOURCE and normal['actualExit'] == normal['terminal']['actualExit'] == current['actualExit'] == 0 and normal['testsExecuted'] == 0, 'same actual source normal/quality')
    require(current['tests'] == 94 and current['suites'] == 7 and len(current['executableClasses']) == 4 and current['actualCrcMismatch'] == 0 and current['actualSessions'] == 1 and not current['coverageUnion'] and all(c['missed'] == 0 for c in current['counters'].values()), 'original94/7 four actual classes four100')
    require(subprocess.check_output(['git', 'rev-parse', prior['source']], cwd=host.ROOT, text=True).strip() == BEFORE and prior['source'] == proofs['priorTrace']['source'] and prior['actualExit'] == proofs['priorTrace']['actualExit'] == 0, 'original shortened source resolves exact prior Git object')
    require(proofs['failedSource']['actualExit'] == 1 and proofs['failedSource']['originalTests'] == 94 and not proofs['failedSource']['postAccepted'] and len(proofs['failedSource']['rawFindings']) == 4, 'failed original static and old source retained, not current qualification')
    snapshot = COMPILE / 'snapshot'
    before_inputs, after_inputs = prior['begin']['inputHashes'], normal['begin']['inputHashes']
    require(set(after_inputs) - set(before_inputs) == ADDED and not (set(before_inputs) - set(after_inputs)) and {p for p, h in before_inputs.items() if after_inputs[p] != h} == CHANGED, 'only four additive paths/two existing Main changes, other source-tests-POM-config same')
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in after_inputs.items()), 'all frozen/current inputs exact')
    old, physical = common.base.inventory(prior), common.base.inventory(normal)
    changed = {p: dict(beforeSha256=old[p], sha256=physical[p]) for p in old if old[p] != physical[p]}
    require(len(old) == 1807 and len(physical) == 1809 and set(physical) - set(old) == NEW_CLASSES and set(changed) == OLD_CLASSES, 'two new physical classes/two changed, other1805 raw/debug same')
    original = proofs['original']['allPhysicalMainSha256']
    require(len(original) == 1669 and all(physical[p] == h for p, h in original.items()), 'original1669 raw/debug same, not a current success transfer')
    require(all(physical['api:' + p] == h for p, h in current['physicalClasses'].items()), 'all four actual component byte owners')
    parts = subprocess.check_output(['git', 'diff', '--no-renames', '--name-status', '-z', BEFORE, SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=host.ROOT).split(b'\0')[:-1]
    require({parts[i + 1].decode(): parts[i].decode() for i in range(0, len(parts), 2)} == {**dict.fromkeys(ADDED, 'A'), **dict.fromkeys(CHANGED, 'M')} and len(parts) == 12, 'six exact source changes only')
    old_rows = {r['path']: r for r in proofs['priorTrace']['sourceRows']}
    require(len(old_rows) == 171 and CHANGED <= set(old_rows), 'all171 prior source owners')
    source_rows = []
    for path in sorted(set(old_rows) | ADDED):
        digest = host.sha(snapshot / path)
        require(path in ADDED | CHANGED or old_rows[path]['sha256'] == digest, 'all unrelated owner bytes unchanged')
        source_rows.append(dict(path=path, sha256=digest, owner='WBS-P018-09', sharedReference='WBS-C07', sharedAdditionalCostPp=0, relationship='CURRENT_API_APPROVED_SOURCE' if path in ADDED | CHANGED else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION', sourceUnchanged=path not in ADDED | CHANGED))
    require(len(source_rows) == 175 and proofs['priorTrace']['ownerGuardBinding']['bootstrapSourcesUnchanged'] == 34, 'all175 owners/limited Bootstrap sources and all descriptors unchanged')
    current_owners = {n: common.contract.java((snapshot / (API + n + '.java')).read_text()) for n in NEW | OLD}
    owners(current_owners)
    rejected = []
    for name, mutate in (
        ('wrong-role', lambda rows: rows['ApiMetricCatalog'].update(package='dev.codex.schubert.nk.web.monitoring')),
        ('shared-bootstrap', lambda rows: rows['ApiScalarMetricExporter']['imports'].append('dev.codex.schubert.nk.bootstrap.metrics.FORBIDDEN')),
        ('target-io', lambda rows: rows['ApiMetricScrape']['imports'].append('java.net.Socket'))):
        candidate = copy.deepcopy(current_owners)
        mutate(candidate)
        try:
            owners(candidate)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('every current owner negative rejects')
    require(len(rejected) == 3 and host.sha(architecture.SOURCE) == proofs['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH) == architecture.ARCH_SHA and host.sha(architecture.SLF) == architecture.SLF_SHA, 'three ownership negatives and exact qualified noninitializing reader')
    SLOT.mkdir()
    steps.SLOT = SLOT
    receipt, text = steps.step('policy-fields', [str(architecture.JAVA.with_name('javap')), '-p', '-s', str(snapshot / (API.replace('/src/main/java/', '/target/classes/') + 'ApiMetricScrape.class'))])
    require(receipt['actualExit'] == 0, 'physical policy descriptor reader exit0')
    policy(text)
    metadata_negatives = []
    for name, replacement in (
        ('retained-source', text.replace('  private final dev.codex.schubert.nk.api.monitoring.ApiScalarMetricExporter scalars;', '  private final io.micrometer.core.instrument.MeterRegistry source;')),
        ('public-field', text.replace('  private final ', '  public final ', 1)),
        ('wrong-descriptor', text.replace('descriptor: ()V', 'descriptor: ()Ljava/lang/String;', 1)),
        ('extra-method', text.replace('\n}', '\n  public void extra();\n    descriptor: ()V\n}')),
        ('missing-constant', text.replace('  private static final java.lang.String STANDARD_MODE;\n    descriptor: Ljava/lang/String;\n', ''))):
        try:
            policy(replacement)
        except ValueError:
            metadata_negatives.append(name)
        else:
            raise ValueError('every full-pair metadata negative rejects')
    require(len(metadata_negatives) == 5, 'five exact physical policy guard negatives')
    classes = SLOT / 'audit-classes'
    classes.mkdir()
    compiled, _ = steps.step('architecture-compile', [str(architecture.JAVAC), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', os.pathsep.join([str(architecture.ARCH), str(architecture.SLF)]), '-d', str(classes), str(architecture.SOURCE)])
    require(compiled['actualExit'] == 0, 'architecture reader compile')
    checked, body = steps.step('architecture-six', [str(architecture.JAVA), '-cp', os.pathsep.join([str(classes), str(architecture.ARCH), str(architecture.SLF)]), 'ModuleDependencyAudit', *[m + '=' + normal['jars'][m]['path'] for m in architecture.MODULES]])
    analysis = architecture.parse(body)
    require(checked['actualExit'] == 0 and analysis['physical'] == 1809 and not analysis['findings'] and len(analysis['rules']) == 5 and all(v == 0 for v in analysis['rules'].values()), 'all1809 actual bytecode five edges0')
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in after_inputs.items()), 'source unchanged after metadata reader')
    verify(invocation)
    value = dict(actualExit=0, source=SOURCE, invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), witnesses=pins, physicalClasses=physical, allPhysicalClassCount=1809, physicalAdded=sorted(NEW_CLASSES), physicalRemoved=[], physicalChanged=changed, previousPhysicalUnchanged=1805, originalPhysicalUnchanged=1669, sourceRows=source_rows, sourceCount=175, currentTests=94, currentSuites=7, currentExecutableScope=sorted(current['executableClasses']), currentCounters=current['counters'], ownerGuardBinding=dict(currentApiRoles=current_owners, newNegativeGuards=rejected, policyMetadataNegatives=metadata_negatives, policyFieldReceipt=receipt, bootstrapSourcesUnchanged=34, descriptorsUnchanged=True, metadataOnly=True), architecture=dict(result=analysis, compileReceipt=compiled, receipt=checked, targetInitialized=False), productTestsExecutedByPost=0, coverageUnion=False, sourceByteOnlyRowsNotCurrentPtPass=True, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, physical=1809, sourceOwners=175, responsibilityNegatives=len(rejected), policyNegatives=len(metadata_negatives), architecture=analysis['rules'], manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()

