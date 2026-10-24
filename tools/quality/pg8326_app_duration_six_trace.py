"""All-six app exposition placement and immutable owner-guard input rebinding, no PT replay."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg8302_http_cdf_six_trace as base
from host_tool_invocation import capture, verify

host, architecture, steps = base.host, base.architecture, base.steps
SOURCE = '3968abacec2052b9e7b803702a3a9231f9209f26'
BEFORE = 'f02fae44edbcf7abba214a6507935c15ae5f9ee9'
COMPILE = host.W / 'pg8320-app-duration-six-compile-v1'
SLOT = host.W / 'pg8326-app-duration-six-trace-v1'
OUT = host.BASE / 'PG8326-app-duration-six-trace-v1'
WITNESSES = (
    ('normal', 'PG8320-app-duration-six-compile-v1/manifest.json', '873d524e75f2826777d633eaadc1888b76d47ad0913c8f74b8d957a447d8c7aa'),
    ('current', 'PG8324-app-duration-post-v1/manifest.json', '89b5f4a47fe347ce5b92acc9f8bc06f59a2ba9ee0d3e5e0276ffcf45ce6a21cb'),
    ('priorNormal', 'PG8296-http-cdf-six-compile-v1/manifest.json', '51309cd76e4e5d2c3822813dba8e1e75a944f895769767831e7325f00908b8bd'),
    ('priorTrace', 'PG8302-http-cdf-six-trace-v1/manifest.json', '0eb09bf4e6da405733ad99eb9c81084450c5f55ca1acfe4dec83f55db59565fb'),
    ('ownerGuard', 'PG8317-app-duration-owner-guard-v1/manifest.json', '5e83ac7eed1e7dc6c04cf3190044ad6096899ce2163cff92f3a6a33d85471e4d'),
    ('ownerNormal', 'PG8316-app-duration-six-compile-v1/manifest.json', '2b979a3b19cb662a6c74d42dc48b426ac9086d34c312928e093a434b88839196'),
    ('original', 'PG6930-current4222-cases/qualification.json', '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
    ('architecture', 'PG6960-archunit-static-v1/manifest.json', '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'))
API = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiDurationMetricExporter.java'
WEB = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/WebDurationMetricExporter.java'
OLD = 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/monitoring/'
DELETED = {OLD + 'PrometheusSummaryExporter.java', OLD + 'package-info.java', (OLD + 'PrometheusSummaryExporterTest.java').replace('/main/', '/test/')}
ADDED_SOURCE = {API, WEB, API.replace('/main/', '/test/').replace('.java', 'Test.java'), WEB.replace('/main/', '/test/').replace('.java', 'Test.java')}
POMS = {'src/schubert-nk-' + role + '/pom.xml' for role in ('api', 'web', 'bootstrap')}
REMOVED_CLASS = {'bootstrap:dev/codex/schubert/nk/bootstrap/monitoring/' + name + '.class' for name in ('PrometheusSummaryExporter', 'package-info')}
ADDED_CLASS = {'api:dev/codex/schubert/nk/api/monitoring/ApiDurationMetricExporter.class', 'web:dev/codex/schubert/nk/web/monitoring/WebDurationMetricExporter.class'}


def main():
    invocation = capture(Path(__file__))
    require = base.require
    require(not SLOT.exists() and not OUT.exists(), 'new-only complete ownership/physical proof')
    proofs, pins = {}, {}
    for name, path, digest in WITNESSES:
        require(host.sha(host.BASE / path) == digest, 'full immutable ' + name + ' witness')
        proofs[name] = json.loads((host.BASE / path).read_text())
        pins[name] = dict(path=path, sha256=digest)
    normal, current, prior = proofs['normal'], proofs['current'], proofs['priorNormal']
    require(normal['source'] == current['source'] == SOURCE and normal['actualExit'] == normal['terminal']['actualExit'] == current['actualExit'] == 0 and normal['testsExecuted'] == 0, 'current same-source successful compile/limited quality')
    require(current['tests'] == 52 and current['suites'] == 4 and len(current['executableClasses']) == 2 and current['actualCrcMismatch'] == 0 and current['actualSessions'] == 1 and all(v['missed'] == 0 for v in current['counters'].values()), 'exact two app encoders, one original exec four100')
    snapshot = COMPILE / 'snapshot'
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all current/frozen input bytes')
    require(prior['source'] == proofs['priorTrace']['source'] == BEFORE and prior['actualExit'] == 0, 'complete prior source')
    previous, physical = base.inventory(prior), base.inventory(normal)
    require(len(previous) == len(physical) == 1801 and set(previous) - set(physical) == REMOVED_CLASS and set(physical) - set(previous) == ADDED_CLASS, 'exact two responsibility-retired classfiles/two app-owned additions')
    require(all(previous[p] == physical[p] for p in set(previous) & set(physical)), 'all retained1799 raw/debug bytes unchanged')
    original = proofs['original']['allPhysicalMainSha256']
    require(len(original) == 1669 and all(physical[p] == h for p, h in original.items()), 'original1669 unchanged, not current PT qualification')
    for entry, digest in current['physicalClasses'].items():
        role = current['classModules'].get(entry.removesuffix('.class'), 'api')
        require(physical[role + ':' + entry] == digest, 'all current app source/metadata physical owners')
    parts = subprocess.check_output(['git', 'diff', '--no-renames', '--name-status', '-z', BEFORE, SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts) == 20, 'exact ten source delta paths; explicit no-rename grammar')
    delta = {parts[n + 1].decode(): parts[n].decode() for n in range(0, len(parts), 2)}
    require(delta == {**{p: 'D' for p in DELETED}, **{p: 'A' for p in ADDED_SOURCE}, **{p: 'M' for p in POMS}}, 'only app placement/typed fixtures/three explicit POMs')
    old_rows = {r['path']: r for r in proofs['priorTrace']['sourceRows']}
    require(len(old_rows) == 159 and DELETED <= set(old_rows) and not (ADDED_SOURCE & set(old_rows)), 'complete159 old source owners')
    rows = []
    for path in sorted((set(old_rows) - DELETED) | ADDED_SOURCE):
        digest = host.sha(snapshot / path)
        require(path in delta or old_rows[path]['sha256'] == digest, 'all other retained source bytes unchanged')
        rows.append(dict(path=path, sha256=digest, owner='WBS-P018-09', sharedReference='WBS-C07', sharedAdditionalCostPp=0, relationship='CURRENT_APP_SOURCE_OR_EXPLICIT_DEPENDENCY' if path in delta else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION', sourceUnchanged=path not in delta))
    require(len(rows) == 160 and all(not (host.ROOT / p).exists() and not (snapshot / p).exists() for p in DELETED), 'all160 current owners and exact retired source absence')
    guard = proofs['ownerGuard']
    require(guard['actualExit'] == 0 and guard['productionPT'] == guard['productClassInitialization'] == 0 and len(guard['negativeGuards']) == 9 and guard['bootstrapSources'] == 34, 'original responsibility metadata guard, never PT')
    require(all(host.sha(snapshot / p) == host.sha(host.ROOT / p) == h for p, h in guard['sourceHashes'].items()), 'every measured owner-guard production source unchanged')
    require(all(proofs['ownerNormal']['begin']['inputHashes'][p] == normal['begin']['inputHashes'][p] for p in POMS), 'all three measured original descriptor bytes identical; test-only edit not guard replay')
    require(host.sha(architecture.SOURCE) == proofs['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH) == architecture.ARCH_SHA and host.sha(architecture.SLF) == architecture.SLF_SHA, 'unchanged canary-qualified five-edge reader')
    SLOT.mkdir()
    steps.SLOT = SLOT
    classes = SLOT / 'audit-classes'
    classes.mkdir()
    compiled, _ = steps.step('architecture-compile', [str(architecture.JAVAC), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', os.pathsep.join([str(architecture.ARCH), str(architecture.SLF)]), '-d', str(classes), str(architecture.SOURCE)])
    require(compiled['actualExit'] == 0, 'architecture reader compile')
    checked, text = steps.step('architecture-six', [str(architecture.JAVA), '-cp', os.pathsep.join([str(classes), str(architecture.ARCH), str(architecture.SLF)]), 'ModuleDependencyAudit', *[m + '=' + normal['jars'][m]['path'] for m in architecture.MODULES]])
    analysis = architecture.parse(text)
    require(checked['actualExit'] == 0 and analysis['physical'] == 1801 and not analysis['findings'] and len(analysis['rules']) == 5 and all(v == 0 for v in analysis['rules'].values()), 'all1801/five edges zero; responsibility guard separate')
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all source inputs unchanged after audit')
    design_ref = '8b91944df5820535e23ba2469740f1c0aa94c447:documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md'
    design = subprocess.check_output(['git', 'show', design_ref], cwd=host.ROOT)
    verify(invocation)
    value = dict(actualExit=0, source=SOURCE, invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), witnesses=pins, physicalClasses=physical, allPhysicalClassCount=1801, physicalAdded=sorted(ADDED_CLASS), physicalRemoved=sorted(REMOVED_CLASS), physicalChanged={}, previousPhysicalUnchanged=1799, originalPhysicalUnchanged=1669, sourceRows=rows, sourceCount=160, currentTests=52, currentSuites=4, currentExecutableScope=sorted(current['executableClasses']), currentCounters=current['counters'], ownerGuardBinding=dict(source=guard['source'], productionInputsByteIdentical=True, originalNegatives=9, guardReplayed=False, productPTTransferred=False), canonicalDesign=dict(gitRef=design_ref, sha256=hashlib.sha256(design).hexdigest(), changed=False), architecture=dict(result=analysis, compileReceipt=compiled, receipt=checked, targetInitialized=False), productTestsExecutedByPost=0, coverageUnion=False, sourceByteOnlyRowsNotCurrentPtPass=True, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, physical=1801, sourceOwners=160, architecture=analysis['rules'], manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
