"""All prior source/bytes unchanged, one new Batch closed text with current-scope quality/ownership."""
import copy
import hashlib
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg8302_http_cdf_six_trace as base
import duration_exposition_owner_contract as contract
from host_tool_invocation import capture, verify

host, architecture, steps = base.host, base.architecture, base.steps
SOURCE = '441158e6eda607cb2cb24a192d73555740cb27a9'
BEFORE = 'cc6638e7a185901e9102f4bcb1db2d92a6330135'
COMPILE = host.W / 'pg8462-batch-text-six-compile-v1'
SLOT = host.W / 'pg8468-batch-text-six-trace-v1'
OUT = host.BASE / 'PG8468-batch-text-six-trace-v1'
MAIN = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/BatchMetricText.java'
INPUTS = {MAIN, MAIN.replace('/main/', '/test/').replace('.java', 'Test.java')}
CLASS = 'batch:dev/codex/schubert/nk/batch/monitoring/BatchMetricText.class'
WITNESSES = (
    ('normal', 'PG8462-batch-text-six-compile-v1/manifest.json', '0f0f417d1605188ca9b35f3178a6dbd181a445b297747200a07da722729bf637'),
    ('current', 'PG8466-batch-text-post-v1/manifest.json', '1caf65635e113427e17023a536b1159fb12a9d2e10abe9e9fe2cc7a87105901c'),
    ('priorNormal', 'PG8450-batch-label-policy-six-compile-v1/manifest.json', 'ec739b4d0b388391f0d6af721c45c9ad52b295ec3f9adadadc1c40d793d8e463'),
    ('priorTrace', 'PG8456-batch-label-policy-six-trace-v1/manifest.json', '3c9ae8f158825a33ab1a9c7a782a8e1974cfd72beada22df140a97ed8380612d'),
    ('original', 'PG6930-current4222-cases/qualification.json', '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
    ('architecture', 'PG6960-archunit-static-v1/manifest.json', '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'))


def validate_owner(row):
    base.require(row['package'] == 'dev.codex.schubert.nk.batch.monitoring' and row['type'] == 'BatchMetricText', 'exact new application owner/type')
    base.require({'io.micrometer.core.instrument.Counter', 'io.micrometer.core.instrument.Gauge'} <= set(row['imports']) and not any(p.startswith(('dev.codex.schubert.nk.web.', 'dev.codex.schubert.nk.api.', 'dev.codex.schubert.nk.bootstrap.', 'java.net.')) or p in ('io.micrometer.core.instrument.Timer', 'io.micrometer.core.instrument.DistributionSummary') for p in row['imports']), 'Batch-owned scalar text only, no shared/cross-app type mode')


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
    require(current['tests'] == 32 and current['suites'] == 2 and len(current['executableClasses']) == 1 and current['actualCrcMismatch'] == 0 and current['actualSessions'] == 1 and not current['coverageUnion'] and all(v['missed'] == 0 for v in current['counters'].values()), 'exact original32/2 and one class four100')
    snapshot = COMPILE / 'snapshot'
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all current/frozen source input bytes')
    require(prior['source'] == proofs['priorTrace']['source'] == BEFORE and prior['actualExit'] == proofs['priorTrace']['actualExit'] == 0, 'qualified prior ownership and lint followup')
    require(set(normal['begin']['inputHashes']) - set(prior['begin']['inputHashes']) == INPUTS and all(normal['begin']['inputHashes'].get(p) == h for p, h in prior['begin']['inputHashes'].items()), 'only new Main/Unit inputs, all prior production/test/POM bytes identical')
    previous, physical = base.inventory(prior), base.inventory(normal)
    require(len(previous) == 1810 and len(physical) == 1811 and set(physical) - set(previous) == {CLASS} and all(physical.get(p) == h for p, h in previous.items()), 'one new Batch closed text physical class, all previous1809 raw/debug identical')
    original = proofs['original']['allPhysicalMainSha256']
    require(len(original) == 1669 and all(physical[p] == h for p, h in original.items()), 'original1669 byte identity is not current PT transfer')
    require(all(physical['batch:' + p] == h for p, h in current['physicalClasses'].items()), 'all selected physical owner bytes')
    parts = subprocess.check_output(['git', 'diff', '--no-renames', '--name-status', '-z', BEFORE, SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts) == 4 and {parts[n + 1].decode(): parts[n].decode() for n in range(0, len(parts), 2)} == {p: 'A' for p in INPUTS}, 'exact two additive source paths')
    old_rows = {r['path']: r for r in proofs['priorTrace']['sourceRows']}
    require(len(old_rows) == 177 and not (set(old_rows) & INPUTS), 'complete prior175 source owners')
    rows = []
    for path in sorted(set(old_rows) | INPUTS):
        digest = host.sha(snapshot / path)
        require(path in INPUTS or old_rows[path]['sha256'] == digest, 'all old owner bytes unchanged')
        rows.append(dict(path=path, sha256=digest, owner='WBS-P018-09', sharedReference='WBS-C07', sharedAdditionalCostPp=0, relationship='CURRENT_BATCH_LABEL_POLICY_SOURCE_OR_EXPLICIT_DEPENDENCY' if path in INPUTS or path in current['sourceFiles'] else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION', sourceUnchanged=path not in INPUTS))
    require(len(rows) == 179, 'all177 source owners')
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
    classes = SLOT / 'audit-classes'
    classes.mkdir()
    compiled, _ = steps.step('architecture-compile', [str(architecture.JAVAC), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', os.pathsep.join([str(architecture.ARCH), str(architecture.SLF)]), '-d', str(classes), str(architecture.SOURCE)])
    require(compiled['actualExit'] == 0, 'architecture reader compile')
    checked, text = steps.step('architecture-six', [str(architecture.JAVA), '-cp', os.pathsep.join([str(classes), str(architecture.ARCH), str(architecture.SLF)]), 'ModuleDependencyAudit', *[m + '=' + normal['jars'][m]['path'] for m in architecture.MODULES]])
    analysis = architecture.parse(text)
    require(checked['actualExit'] == 0 and analysis['physical'] == 1811 and not analysis['findings'] and len(analysis['rules']) == 5 and all(v == 0 for v in analysis['rules'].values()), 'all1810 and five actual architecture edges zero')
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all source inputs unchanged after reader')

    raw_file = host.BASE / 'PG8464-batch-text-host-v1/manifest.json'
    require(host.sha(raw_file) == 'f6fa626f636469c0ca110289ff1f1b687096a8b12768a0490cafcfbba533207a', 'original current32 parser parent witness')
    raw = json.loads(raw_file.read_text())
    parser_log = host.W / 'pg8464-batch-text-host-v1/selected-junit.log'
    require(raw['source'] == SOURCE and raw['actualExit'] == 0 and host.sha(parser_log) == raw['stages'][1]['logSha256'], 'same original source/JVM0 and exact parser stdout')
    parser_rows = [dict(part.split('=', 1) for part in line.removeprefix('BATCHWIRE008 ').split('; ')) for line in parser_log.read_text().splitlines() if line.startswith('BATCHWIRE008 ')]
    negative = b'# HELP fixture Invalid numeric literal.\n# TYPE fixture gauge\nfixture definitely_not_a_number\n'
    require(len(parser_rows) == 2 and all(set(r) == {'command', 'stdinSHA256', 'actualExit', 'outputSHA256', 'timeUTC'} and r['command'] == 'promtool check metrics' for r in parser_rows), 'exact two actual stdin-only parser receipts')
    require(parser_rows[0]['actualExit'] == '0' and parser_rows[0]['stdinSHA256'] == 'f373bf1d1e2c138fd6d9543672f4f5abf80ce4baba4afc62bd0c8e68c7cbe1dc' and parser_rows[1]['actualExit'] == '1' and parser_rows[1]['stdinSHA256'] == hashlib.sha256(negative).hexdigest(), 'positive actual text accepted, independently malformed numeric literal rejected')
    parser_binary = host.TC / 'promtool-3.13.5-linux-amd64/promtool'
    require(not parser_binary.is_symlink() and host.sha(parser_binary) == '4e84296dc89ef03d856674d76d387f5ccc54a698136c2f0dc30ceef2286908ff', 'same independently pinned official syntax binary')

    verify(invocation)
    value = dict(actualExit=0, source=SOURCE, invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), witnesses=pins, physicalClasses=physical, allPhysicalClassCount=1811, physicalAdded=[CLASS], physicalChanged={}, physicalRemoved=[], previousPhysicalUnchanged=1810, originalPhysicalUnchanged=1669, sourceRows=rows, sourceCount=179, currentTests=32, currentSuites=2, currentExecutableScope=sorted(current['executableClasses']), currentCounters=current['counters'], ownerGuardBinding=dict(newOwner=owner, newNegativeGuards=rejected, priorAllInputsByteIdentical=True, priorRoleGuardsReplayed=False, bootstrapSourcesUnchanged=34, descriptorsUnchanged=True, metadataOnly=True), architecture=dict(result=analysis, compileReceipt=compiled, receipt=checked, targetInitialized=False), parserProof=dict(originalJvmLogSha256=host.sha(parser_log), actualRows=parser_rows, binarySha256=host.sha(parser_binary), parserProcessesRepeatedByPost=0, junitCaseCount=1), productTestsExecutedByPost=0, coverageUnion=False, sourceByteOnlyRowsNotCurrentPtPass=True, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, physical=1811, sourceOwners=179, newResponsibilityNegatives=len(rejected), architecture=analysis['rules'], manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()



