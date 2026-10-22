"""Read original4222 proof for exactly four prerequisites plus catalog; never run PT/VM.

This produces evidence, not acceptance from counters. A separate reviewed source register
uses the existing strict per-criterion/dependency validator; historical17 is untouched.
"""
import argparse
import copy
import hashlib
import json
import os
import subprocess
import tarfile
import zipfile
from pathlib import Path

from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6932_original4222_artifacts import read_whole
from pg5966_api_sql_selected import ordinary_names
from pg6092_current3985_static_join import source_case_candidates
import pg3284_protocol_canonical_fixtures as canonical
from pg3390_broker_config_oracle import self_check
import wbs_progress_audit as audit
import wbs_component_overlay

SOURCE = 'e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
IDS = ('WBS-P001-01', 'WBS-P001-02', 'WBS-P002-03', 'WBS-C04', 'WBS-P005-01')
PMO = ROOT / 'documents/400_PGPT/470_PMO'
OUT = BASE / 'PG6958-required-four-catalog-v1'
REVIEW = 'evidence/01_PT/018_NK-OPS-001/1524_PG6958_リカバリ初回五項目・当source受入matrix.md'
SUITES = {
 'WBS-P001-01': ('protocol:header.HeaderModelTest', 'protocol:codec.MessageCodecTest',
                  'protocol:codec.FieldCodecTest', 'protocol:layout.PayloadTypeCatalogTest'),
 'WBS-P001-02': ('protocol:layout.LayoutMetadataTest', 'protocol:layout.LayoutFieldCatalogTest',
                  'protocol:layout.PayloadTypeCatalogTest', 'protocol:codec.MessageCodecTest',
                  'protocol:codec.PayloadCodecTest'),
 'WBS-P002-03': ('protocol:codec.MessageCodecTest',),
 'WBS-C04': ('api:messaging.config.ArtemisBrokerConfigurationTest',
             'api:messaging.config.ArtemisSecurityTest', 'api:messaging.config.ArtemisFileJournalTest',
             'api:messaging.config.ArtemisTransportContractTest',
             'batch:mq.ArtemisExpiryManagementAuthorizationTest'),
 'WBS-P005-01': ('protocol:transport.BrokerTopologyTest', 'api:dispatch.ApiSyncRequestDispatcherTest',
                 'api:security.AuthenticationContextVerifierTest', 'api:security.AuthorizationServiceTest',
                 'api:database.DatabaseMigrationTest', 'web:security.MqAuthenticationProviderTest'),
}
TYPES = ('LINE', 'METHOD', 'CLASS', 'BRANCH')


def require(value, message):
    if not value:
        raise ValueError(message)


def git(ref, path):
    return subprocess.check_output(['git', 'show', ref + ':' + path], cwd=ROOT)


def suite_path(selector):
    module, suffix = selector.split(':')
    clazz = 'dev.codex.schubert.nk.' + module + '.' + suffix
    return module, clazz, 'src/schubert-nk-' + module + '/src/test/java/' + clazz.replace('.', '/') + '.java'


def join_suite(selector, text, cases):
    module, clazz, _ = suite_path(selector)
    actual = [c for c in cases if c['module'] == module and c['class'] == clazz]
    joined = []
    for method in ordinary_names(text):
        identities = {hashlib.sha256(s.encode()).hexdigest() for s in source_case_candidates(text, method)}
        found = [c for c in actual if c['caseNameSha256'] in identities]
        require(len(found) == 1 and found[0]['source'] == SOURCE
                and found[0]['result'] == 'PASS_ORIGINAL_XML', 'one genuine original case per method')
        joined.append(dict(method=method, methodIdentitySha256=found[0]['caseNameSha256'], originalCase=found[0]))
    require(len(joined) == len(actual) > 0, 'no missing/extra/duplicate source or original cases')
    require(len({j['originalCase']['testId'] for j in joined}) == len(joined), 'one-to-one case identity')
    return joined


def family_counters(path, q):
    if path.endswith('/package-info.java'):
        return dict(applicability='PACKAGE_ANNOTATION_NO_EXECUTABLE_METHOD', counters={})
    module = path.split('/')[1].removeprefix('schubert-nk-')
    name = path.split('/src/main/java/')[1][:-5]
    rows = {k: v for k, v in q['allActualClassCounters'].items()
            if k == module + ':' + name + '.class' or k.startswith(module + ':' + name + '$')}
    require(rows, 'physical/coverage family must be present, no inferred coverage')
    not_applicable = {k: empty_counter_reason(k, q) for k, v in rows.items() if not v}
    executable = [v for v in rows.values() if v]
    require(executable or (len(rows) == 1 and next(iter(not_applicable.values()))['kind'] == 'ABSTRACT_INTERFACE_NO_CODE'),
            'real executable family or independently verified declaration')
    for counter in executable:
        require(all(k in TYPES and c['missed'] == 0 for k, c in counter.items()), 'all actual family counters missed0')
        require(all(counter[k]['covered'] > 0 for k in ('LINE', 'METHOD', 'CLASS')), 'positive real executable counters')
    return dict(applicability='ACTUAL_ORIGINAL_XML_COUNTERS', counters=rows,
                emptyCounterApplicability=not_applicable,
                absentCounters='NOT_APPLICABLE_NOT_SYNTHESIZED')


def empty_counter_reason(key, q):
    allowed = {
      'dev/codex/schubert/nk/protocol/layout/FieldDefinition$1.class':'COMPILER_ENUM_SWITCH_HELPER',
      'dev/codex/schubert/nk/protocol/layout/LayoutFieldCatalog$1.class':'COMPILER_ENUM_SWITCH_HELPER',
      'dev/codex/schubert/nk/protocol/layout/FieldValue.class':'ABSTRACT_INTERFACE_NO_CODE',
      'dev/codex/schubert/nk/protocol/layout/LayoutPayload.class':'ABSTRACT_INTERFACE_NO_CODE'}
    module, name = key.split(':', 1)
    require(module == 'protocol' and name in allowed and q['allActualClassCounters'][key] == {},
            'only four explicit original empty-counter classes, never arbitrary omission')
    jar = W / 'pg6932-original4222-artifacts-v1/jars/schubert-nk-protocol.jar'
    with zipfile.ZipFile(jar) as archive:
        digest = hashlib.sha256(archive.read(name)).hexdigest()
    require(digest == q['allPhysicalMainSha256'][key], 'actual original physical class bytes')
    javap = ROOT.parent / 'toolchain/jdk-25.0.4/bin/javap'
    raw = subprocess.check_output([str(javap), '-v', '-p', '-classpath', str(jar), name[:-6].replace('/', '.')], text=True)
    flags = next((s.strip() for s in raw.splitlines() if s.strip().startswith('flags:')), '')
    kind = allowed[name]
    if kind == 'ABSTRACT_INTERFACE_NO_CODE':
        require('ACC_INTERFACE' in flags and 'ACC_ABSTRACT' in flags and 'Code:' not in raw,
                'actual interface must have no executable Code attribute')
    else:
        require('ACC_SYNTHETIC' in flags and 'static {};' in raw,
                'only actual compiler synthetic switch-table initializer')
    return dict(kind=kind, actualClassSha256=digest, originalCounter={}, javapExit=0,
                classFlags=flags, javapOutputSha256=hashlib.sha256(raw.encode()).hexdigest(),
                coverage100Claim=False, exclusionAdded=False)


def canonical_fixtures():
    ui = ROOT / 'documents/200_UI/230_インターフェース'
    ss = ROOT / 'documents/300_SS/320_メッセージング'
    paths = [*(canonical.unique_file(ui, str(n) + '_*.md') for n in (233, 234, 235, 236)),
             canonical.unique_file(ss, '323_*.md')]
    layouts = canonical.layouts(paths[0].read_text())
    areas = canonical.field_areas([p.read_text() for p in paths[1:4]])
    names = canonical.named_types(paths[4].read_text())
    fixtures = [ROOT / canonical.FIXTURE / n for n in
                ('layouts-ui233.tsv', 'fields-ui234-236.tsv', 'named-types-ss323.tsv')]
    expected = {i: (k, a, *map(int, sizes)) for i, k, a, *sizes in canonical.tsv(fixtures[0])}
    fields = {}
    for i, area, name, start, length, wire, presence, rule in canonical.tsv(fixtures[1]):
        fields.setdefault((i, area), []).append((name, int(start), int(length), wire, presence, rule))
    types = {i: (d, r) for i, d, r in canonical.tsv(fixtures[2])}
    require(layouts == expected and len(expected) == 64, '64 canonical independent layout tuples')
    require({k: v for k, v in areas.items() if v} == fields and sum(map(len, fields.values())) == 389,
            '389 canonical independent fields')
    require(names == types and set(types) == set(layouts)
            and len({n for pair in names.values() for n in pair if n != '-'}) == 69, '64/69 independent named types')
    for i, (_, _, data, record, _, _) in layouts.items():
        for area, length in (('DATA', data), ('RECORD', record)):
            position = 1
            for field in areas.get((i, area), []):
                require(field[1] == position and field[2] > 0, 'canonical one-based contiguous field')
                position += field[2]
            require(position - 1 == length, 'independent area length')
    return paths, fixtures


def bind_archive(paths):
    run = W / 'pg6930-fixture4222-six-v1'
    begin = json.loads((run / 'begin.safe.json').read_bytes())
    require(begin['source'] == SOURCE and sha(run / 'source.tar') == begin['archiveSha256'], 'original archive authority')
    result = {}
    with tarfile.open(run / 'source.tar') as tar:
        for path in sorted(set(paths)):
            member = tar.getmember(path)
            require(member.isfile(), 'regular fixed public source input')
            data = tar.extractfile(member).read()
            require(data == (ROOT / path).read_bytes() == git(SOURCE, path), 'archive/Git/current bytes equal')
            result[path] = hashlib.sha256(data).hexdigest()
    return result


def witness():
    qp, q, cases = read_whole()
    require(sha(qp) == '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'
            and q['productionSource'] == SOURCE and q['tests'] == 4222 and q['suites'] == 660
            and q['FESFlakyNotRun'] == q['staticSixModules'] == 0, 'original4222 qualified, no replay')
    master = json.loads((PMO / '481_PGPT詳細WBS.json').read_bytes())
    tasks = {r['id']: r for r in master['tasks'] if r['id'] in IDS}
    require(set(tasks) == set(IDS), 'exact four required dependencies and one new candidate')
    inventory = json.loads((PMO / '485_WBS網羅性・受入対応.json').read_bytes())['currentPhysicalCandidate']
    require(inventory['source'] == SOURCE, 'same source current physical ownership')
    tests = {s: suite_path(s)[2] for values in SUITES.values() for s in values}
    designs, fixtures = canonical_fixtures()
    design_paths = {str(p.relative_to(ROOT)) for p in designs}
    design_paths.update(p for t in tasks.values() for p in t['evidencePlan']['designFiles'])
    design_paths.add('documents/100_RD/130_インターフェース要件/131_MQインターフェース要件.md')
    for path in design_paths:
        require(git('origin/main', path) == (ROOT / path).read_bytes(), 'canonical design agreement')
    source_paths = [p for t in tasks.values() for p in t['ownedArtifacts']] + list(tests.values())
    source_paths += [str(p.relative_to(ROOT)) for p in fixtures]
    inputs = bind_archive(source_paths)
    joined = {s: join_suite(s, (ROOT / p).read_text(), cases) for s, p in tests.items()}
    static_path = BASE / 'PG6936-current4222-static-v1/manifest.json'
    require(sha(static_path) == 'e6de32cbea868ca65b56a1caf9cbf428aa51dcf00ec996577c28823a5b5631f8', 'current static qualification')
    static = json.loads(static_path.read_bytes())
    raw_path = static_path.with_name(static['inventoryFile'])
    require(sha(raw_path) == static['inventorySha256'], 'unfiltered static inventory authority')
    findings = json.loads(raw_path.read_bytes())
    rows = {}
    for rid in IDS:
        task = tasks[rid]
        actual = {a['path']: a['sha256'] for a in inventory['artifacts'] if a['owner'] == rid}
        require(set(actual) == set(task['ownedArtifacts']) and not task['sharedClassReferences'], 'exact full scope/shared boundary')
        require(actual == {p: inputs[p] for p in actual}, 'owned artifact qualified hashes')
        relevant = [r for r in findings if r['sourcePath'] in actual]
        require(all(r['currentWholeSource'] == SOURCE and r['sourceSha256'] == inputs[r['sourcePath']]
                    and r['status'] in ('REQUIRED_CONTRACT', 'CONTEXT_NOT_APPLICABLE', 'FALSE_POSITIVE') for r in relevant),
                'no unreviewed target static finding')
        counters = {p: family_counters(p, q) for p in actual if '/src/main/java/' in p}
        rows[rid] = dict(scopePaths=task['ownedArtifacts'], requirementIds=task['requirementIds'],
                         dependencies=task['dependencies'], sharedReferences=[], inputHashes=actual,
                         applicableCounters=counters, suiteRefs=list(SUITES[rid]),
                         originalCaseCount=sum(len(joined[s]) for s in SUITES[rid]),
                         staticFindingIds=[r['findingId'] for r in relevant],
                         criteriaExpected=task['acceptanceChecks'], status='EVIDENCE_READY_REVIEW_REQUIRED')
    policy = self_check(ROOT / 'src/deployment/artemis/etc/broker.xml')
    schema_path = BASE / 'PG3392-broker-config-contract/manifest.json'
    schema = json.loads(schema_path.read_bytes())['schemaCanary']
    require(schema['actualExit'] == schema['compileExit'] == 0 and schema['originalAcceptedBeforeAndAfter']
            and schema['independentInvalidFourRejected'], 'historical schema validator qualification only')
    require(sha(ROOT / 'tools/quality/vm/050_s1/ArtemisConfigurationSchemaCanary.java') == schema['sourceSha256'],
            'unchanged schema validator source')
    jar = ROOT.parent / 'toolchain/m2/repository/org/apache/artemis/artemis-server/2.56.0/artemis-server-2.56.0.jar'
    with zipfile.ZipFile(jar) as zipped:
        require(all(hashlib.sha256(zipped.read('schema/' + n)).hexdigest() == h
                    for n, h in schema['officialSchemaSha256'].items()), 'fixed official schema bytes')
    return dict(actualExit=0, source=SOURCE, run='PG6930-six-v1', rows=rows,
                originalQualification={'path':str(qp.relative_to(ROOT)), 'sha256':sha(qp)},
                allInputHashes=inputs, originalSuiteJoins=joined,
                canonicalMain=subprocess.check_output(['git','rev-parse','origin/main'], cwd=ROOT,text=True).strip(),
                canonicalDesignHashes={p:sha(ROOT / p) for p in sorted(design_paths)},
                historicalStateHashes={n:sha(PMO / n) for n in
                                       ('481_PGPT詳細WBS.json', '484_WBSコスト枠・細分化.json',
                                        '485_WBS網羅性・受入対応.json', '486_WBS現行実績.json')},
                independentFixtures=dict(layouts=64, fields=389, namedTypes=69),
                brokerPolicy=policy, historicalSchemaQualification={'path':str(schema_path.relative_to(ROOT)), 'sha256':sha(schema_path),
                                                                  'currentDynamicPassImported':False},
                semanticReviewPath=REVIEW, semanticReviewSha256=sha(ROOT / REVIEW),
                scope='FOUR_PREREQUISITES_AND_CATALOG_ONLY', acceptance='NOT_APPLIED', newAccepted=0,
                revalidated=0, testsExecuted=0, wholeReplayed=False, vmActions=0, formalAccepted=False,
                effortPercent=None, ptAlternativeCompleted=0,
                toolSha256=sha(ROOT / 'tools/quality/pg6958_recovery_catalog.py'))


def verify_register(register):
    require(register['source'] == SOURCE and register['formalUpdated'] is False
            and register['wholeEffortCompletionRate'] is None, 'fixed source, no formal or effort promotion')
    manifest_path = ROOT / register['witness']['path']
    require(sha(manifest_path) == register['witness']['sha256'], 'explicit current witness hash')
    proof = json.loads(manifest_path.read_bytes())
    require(proof['actualExit'] == 0 and proof['source'] == SOURCE and proof['acceptance'] == 'NOT_APPLIED', 'actual reviewed witness first')
    require(sha(ROOT / proof['semanticReviewPath']) == proof['semanticReviewSha256'], 'fixed semantic review')
    require(register['reviewState'] == 'COMPLETE' and register['acceptedBy'], 'explicit PG review, never coverage inference')
    require(wbs_component_overlay.historical_state_unchanged(PMO,proof['historicalStateHashes']),
            'historical17/source/criteria/scope/cost state unchanged')
    master = json.loads((PMO / '481_PGPT詳細WBS.json').read_bytes())
    tasks = {t['id']: t for t in master['tasks'] if t['id'] in IDS}
    require(set(register['records']) == set(IDS), 'no bulk historical revalidation or extra acceptance')
    states = register['records']
    for rid in IDS:
        task = copy.deepcopy(tasks[rid])
        row = proof['rows'][rid]
        require(row['scopePaths'] == task['ownedArtifacts'] and row['requirementIds'] == task['requirementIds']
                and row['dependencies'] == task['dependencies'], 'scope/requirements/dependencies unchanged')
        require(all(sha(ROOT / p) == h and git(SOURCE, p) == (ROOT / p).read_bytes() for p, h in proof['allInputHashes'].items()),
                'reviewed original source/Test/fixture remains fixed')
        task['acceptance'] = states[rid]
        audit.check_acceptance(task, SOURCE, states)
    require(register['newAcceptedIds'] == ['WBS-P005-01'] and register['revalidatedIds'] == list(IDS[:-1]),
            'one new/four revalidated, no mixed-source arithmetic')
    return dict(actualExit=0, source=SOURCE, currentSourceAccepted=5, newAccepted=1, revalidated=4,
                historical17Unchanged=True, formalUpdated=False, wholeEffortCompletionRate=None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--register', type=Path)
    args = parser.parse_args()
    if args.register:
        print(json.dumps(verify_register(json.loads(args.register.read_bytes()))))
        return
    value = witness()
    os.umask(0o077)
    OUT.mkdir()
    path = OUT / 'manifest.json'
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps(dict(actualExit=0, manifestSha256=sha(path), rows=len(value['rows']),
                         originalReferencedCases=sum(len(v) for v in value['originalSuiteJoins'].values()),
                         newAccepted=0, testsExecuted=0)))


if __name__ == '__main__':
    main()
