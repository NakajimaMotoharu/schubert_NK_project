"""New shared module/POM all-six byte/ownership/architecture proof; never replay product PT."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile
import pg6966_chr_adapter_host as host
import pg6960_archunit as architecture
import scoped_prometheus_post as steps
from host_tool_invocation import capture, verify

SOURCE = '7cba540ba7213e390d21ff46db73420caa5056e4'
BEFORE = '6246c954d6d0ac7171bf009663bb2e6539d8be32'
COMPILE = host.W / 'pg8270-summary-encoder-six-compile-v1'
SLOT = host.W / 'pg8276-summary-encoder-six-trace-v1'
OUT = host.BASE / 'PG8276-summary-encoder-six-trace-v1'
NORMAL_SHA = '41ab25f9bbaf9f8df32d600fea3c04c59eaf492bc1cbb77fcc0a6c22555f6428'
CURRENT_SHA = '829236f4817bc90af1f6af798f00d86fbda036e39b765cd9f582ac9a45b3f42c'
WITNESSES = (
    ('normal', 'PG8270-summary-encoder-six-compile-v1/manifest.json', NORMAL_SHA),
    ('current', 'PG8274-summary-encoder-post-v1/manifest.json', CURRENT_SHA),
    ('priorNormal', 'PG8212-counter-name-six-compile-v1/manifest.json', 'db14f540178f960e7aa2c08303867340a2643e6c9f9f0c73c23fd245f675f7d6'),
    ('priorTrace', 'PG8219-counter-name-six-trace-v2/manifest.json', '671663c32905d4e15ca0462f02d59d4759842a9e27ab908ee623d9f9850734af'),
    ('original', 'PG6930-current4222-cases/qualification.json', '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
    ('architecture', 'PG6960-archunit-static-v1/manifest.json', '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f'))
MAIN = 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/monitoring/PrometheusSummaryExporter.java'
PACKAGE = MAIN.rsplit('/', 1)[0] + '/package-info.java'
TEST = MAIN.replace('/main/', '/test/').replace('.java', 'Test.java')
POM = 'src/schubert-nk-bootstrap/pom.xml'
ADDED = {'bootstrap:dev/codex/schubert/nk/bootstrap/monitoring/' + n + '.class' for n in ('PrometheusSummaryExporter', 'package-info')}


def require(value, message):
    if not value:
        raise ValueError(message)


def inventory(normal):
    require(set(normal['jars']) == set(architecture.MODULES), 'all six artifacts required')
    rows = {}
    for role, row in normal['jars'].items():
        file = Path(row['path'])
        require(host.sha(file) == row['sha256'], 'all six actual original Jar hashes')
        with zipfile.ZipFile(file) as archive:
            for name in archive.namelist():
                if not name.endswith('.class'):
                    continue
                key = role + ':' + name
                require(key not in rows, 'unique one-role physical namespace')
                rows[key] = hashlib.sha256(archive.read(name)).hexdigest()
    return rows


def main():
    invocation = capture(Path(__file__))
    require(not SLOT.exists() and not OUT.exists(), 'new-only trace proof, no unknown replay')
    proofs = {}
    pins = {}
    for name, path, digest in WITNESSES:
        file = host.BASE / path
        require(len(digest) == 64 and host.sha(file) == digest, 'exact immutable ' + name + ' witness')
        proofs[name] = json.loads(file.read_text())
        pins[name] = dict(path=path, sha256=digest)
    normal, current, prior = proofs['normal'], proofs['current'], proofs['priorNormal']
    require(normal['source'] == current['source'] == SOURCE and normal['actualExit'] == normal['terminal']['actualExit'] == current['actualExit'] == 0 and normal['testsExecuted'] == 0, 'same source genuinely successful compile/qualification')
    require(current['tests'] == 58 and current['suites'] == 5 and len(current['executableClasses']) == 8 and current['actualCrcMismatch'] == 0 and current['actualSessions'] == 1 and not current['coverageUnion'], 'current eight-class exact58 only')
    snapshot = COMPILE / 'snapshot'
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all current/frozen inputs before static analysis')
    require(prior['source'] == proofs['priorTrace']['source'] == BEFORE and prior['actualExit'] == 0, 'exact previous full normal source')
    previous = inventory(prior)
    physical = inventory(normal)
    require(len(previous) == 1799 and len(physical) == 1801 and set(physical) - set(previous) == ADDED and not (set(previous) - set(physical)), 'complete physical delta: exactly two declared shared classfiles')
    require(all(physical[p] == h for p, h in previous.items()), 'all previous1799 bytes including debug unchanged')
    original = proofs['original']['allPhysicalMainSha256']
    require(len(original) == 1669 and all(physical[p] == h for p, h in original.items()), 'original whole1669 unchanged, not current PT qualification')
    for entry, digest in current['physicalClasses'].items():
        name = entry.removesuffix('.class')
        role = current['classModules'].get(name, 'api')
        require(physical[role + ':' + entry] == digest, 'all current executable/metadata byte ownership')
    parts = subprocess.check_output(['git', 'diff', '--name-status', '-z', BEFORE, SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=host.ROOT).split(b'\0')[:-1]
    require(len(parts) == 8, 'exact four input paths')
    delta = {parts[n + 1].decode(): parts[n].decode() for n in range(0, len(parts), 2)}
    require(delta == {MAIN: 'A', PACKAGE: 'A', TEST: 'A', POM: 'M'}, 'only new formatter/source metadata/test and explicit bootstrap external POM')
    old_rows = {r['path']: r for r in proofs['priorTrace']['sourceRows']}
    require(len(old_rows) == 155 and not (set(delta) & set(old_rows)), 'known disjoint four new tracked owners')
    paths = sorted(set(old_rows) | set(delta))
    rows = []
    for path in paths:
        digest = host.sha(snapshot / path)
        if path in old_rows:
            require(old_rows[path]['sha256'] == digest, 'all previous155 source owner bytes unchanged')
        rows.append(dict(path=path, sha256=digest, owner='WBS-P018-09', sharedReference='WBS-C07', sharedAdditionalCostPp=0, relationship='CURRENT_SCOPED_SOURCE_OR_DEPENDENCY' if path in delta or path in current['sourceFiles'] else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION', sourceUnchanged=path in old_rows))
    require(len(rows) == 159, 'all159 unique source owners')
    require(host.sha(architecture.SOURCE) == proofs['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH) == architecture.ARCH_SHA and host.sha(architecture.SLF) == architecture.SLF_SHA, 'previous canary-qualified architecture reader and fixed libraries')
    SLOT.mkdir()
    steps.SLOT = SLOT
    classes = SLOT / 'audit-classes'
    classes.mkdir()
    compiled, _ = steps.step('architecture-compile', [str(architecture.JAVAC), '--release', '25', '-proc:none', '-Xlint:all', '-Werror', '-cp', os.pathsep.join([str(architecture.ARCH), str(architecture.SLF)]), '-d', str(classes), str(architecture.SOURCE)])
    require(compiled['actualExit'] == 0, 'ordinary noninitializing architecture reader compile')
    checked, text = steps.step('architecture-six', [str(architecture.JAVA), '-cp', os.pathsep.join([str(classes), str(architecture.ARCH), str(architecture.SLF)]), 'ModuleDependencyAudit', *[m + '=' + normal['jars'][m]['path'] for m in architecture.MODULES]])
    analysis = architecture.parse(text)
    require(checked['actualExit'] == 0 and analysis['physical'] == 1801 and not analysis['findings'] and len(analysis['rules']) == 5 and all(v == 0 for v in analysis['rules'].values()), 'all1801 and five unchanged actual architecture rules zero')
    require(all(host.sha(snapshot / p) == h and host.sha(host.ROOT / p) == h for p, h in normal['begin']['inputHashes'].items()), 'all source inputs immutable after reader')
    verify(invocation)
    value = dict(actualExit=0, source=SOURCE, invocation=invocation, timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), witnesses=pins, physicalClasses=physical, allPhysicalClassCount=1801, previousPhysicalUnchanged=1799, originalPhysicalUnchanged=1669, physicalAdded=sorted(ADDED), physicalChanged={}, physicalRemoved=[], sourceRows=rows, sourceCount=len(rows), currentTests=58, currentSuites=5, currentExecutableScope=sorted(current['executableClasses']), currentCounters=current['counters'], architecture=dict(result=analysis, compileReceipt=compiled, receipt=checked, targetInitialized=False), productTestsExecutedByPost=0, coverageUnion=False, sourceByteOnlyRowsNotCurrentPtPass=True, formalUpdated=False, whole451Accepted=False, newAccepted=0, effortPercent=None, actualVmActions=0, actualDatabaseActions=0, actualNetworkActions=0, actualServiceActions=0)
    OUT.mkdir()
    host.write(OUT / 'manifest.json', value)
    print(json.dumps(dict(actualExit=0, physical=1801, sourceOwners=len(rows), architecture=analysis['rules'], manifestSha256=host.sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
