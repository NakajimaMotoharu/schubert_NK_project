"""Apply only individually reviewed P001-02, with unchanged strict WBS audit.

Immutable successful source/run witnesses, canonical oracle, all owned artifacts,
four counters, and explicit review107 are prerequisites. No runtime action.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from pg3274_header_group_full_six import ROOT, SOURCE, W
from pg3282_wbs_current_source_apply import replace_public, rewrite_root
from pg3286_protocol_existing_run_witness import PUBLIC
import wbs_progress_audit as audit

ID = 'WBS-P001-02'
SPEC = Path('evidence/01_PT/001_NK-PRO-001/107_現source正本fixture照合・layout個別受入.md')


def require(value, message):
    if not value:
        raise ValueError(message)


def one_line_task(text, id, changed):
    lines = text.splitlines(keepends=True); hits = 0
    for index, line in enumerate(lines):
        try:
            old = json.loads(line.strip().removesuffix(','))
        except json.JSONDecodeError:
            continue
        if isinstance(old, dict) and old.get('id') == id:
            require(old['id'] == id and set(old) == set(changed), 'same exact task schema required')
            lines[index] = line[:len(line) - len(line.lstrip())] + json.dumps(changed, ensure_ascii=False) + (',' if line.rstrip().endswith(',') else '') + '\n'; hits += 1
    require(hits == 1, 'one task line required')
    return ''.join(lines)


def check_inputs(canonical, witness, task, row):
    require(canonical['actualExit'] == witness['actualExit'] == 0
            and canonical['productionSource'] == witness['productionSource'] == SOURCE,
            'successful same-source witnesses required')
    require((canonical['layoutTuples'], canonical['fieldRows'], canonical['nonemptyAreas'], canonical['namedMappings']) == (64, 389, 74, 64)
            and canonical['expectedGeneratedFromProduction'] is False, 'complete independent canonical oracle required')
    require(len(witness['suites']) == 17 and sum(s['counts']['tests'] for s in witness['suites']) == 84
            and witness['staticIssues'] == witness['testsReissued'] == witness['vmActions'] == 0, 'actual84 and no replay required')
    require(task['id'] == row['id'] == ID and task['acceptance']['status'] == 'NOT_ACCEPTED'
            and task['dependencies'] == [] and len(task['ownedArtifacts']) == 20
            and row['measurementSource'] == SOURCE and row['measurementStatus'] == 'HOST_COUNTERS_CLOSED'
            and all(v == 0 for v in row['missed'].values()), 'exact unaccepted complete leaf required')
    methods = {s['class']: set(s['tests']) for s in witness['suites']}
    needed = {
        'layout.LayoutMetadataTest': {'registryMatchesIndependentUi233Catalog', 'registryRejectsEmptyNullDuplicateAndKindMismatches', 'layoutDefinitionChecksEveryLengthAndKindInvariant', 'layoutIdAndFieldDefinitionAreStrictAndOneBased'},
        'layout.LayoutFieldCatalogTest': {'catalogMatchesIndependentUi234To236Fixture', 'parserRejectsMalformedUnknownAndDuplicateRows', 'layoutFieldsRejectWrongAreaGapLengthAndNull'},
        'layout.PayloadTypeCatalogTest': {'explicitCatalogMatchesIndependentSs323NamedTypeFixture', 'catalogRejectsUnknownLayoutsAndMismatchedDataOrRecordTypes', 'typedModelsAndHelpersRejectNullMissingAndWrongKinds'},
        'codec.PayloadCodecTest': {'valuesAreImmutableNullSafeAndRedacted'},
        'codec.MessageCodecTest': {'fixedPayloadIsDefensiveAndWireMessageChecksLengths'},
        'codec.PayloadGoldenVectorTest': {'sharedCodecProducesIdenticalBytesUnderConcurrentUse'}}
    for short, names in needed.items():
        require(names <= methods.get('dev.codex.schubert.nk.protocol.' + short, set()), 'every explicitly reviewed method must actually have passed')


def main(resume=False):
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'fixed clean reviewed tool/doc/proof required')
    before = audit.verify()
    require(before['acceptedTasks'] == 0, 'first individually reviewed acceptance, not repeated operation')
    master_path = audit.PMO / '481_PGPT詳細WBS.json'; snapshot_path = audit.PMO / '486_WBS現行実績.json'
    master = audit.read_json(master_path); snapshot = audit.read_json(snapshot_path)
    inventory = audit.read_json(audit.PMO / master['inventoryRef'])
    task = next(t for t in master['tasks'] if t['id'] == ID); row = next(t for t in snapshot['rows'] if t['id'] == ID)
    canonical = audit.read_json(ROOT / PUBLIC / 'canonical-fixtures.json'); witness = audit.read_json(ROOT / PUBLIC / 'test-witness.json')
    check_inputs(canonical, witness, task, row)
    require(snapshot['source'] == SOURCE and len(task['acceptanceChecks']) == 3, 'current source/all criteria required')
    for name, sha in {**canonical['canonicalHashes'], **canonical['fixtureHashes'], **witness['testSourceHashes']}.items():
        require(audit.digest(ROOT / name) == sha, 'reviewed canonical/fixture/Test bytes changed')
    for name, sha in canonical['canonicalHashes'].items():
        require(hashlib.sha256(subprocess.check_output(['git', 'show', 'origin/main:' + name], cwd=ROOT)).hexdigest() == sha, 'origin/main oracle changed')
    coverage = audit.coverage_root(inventory['measurementBindings']['coverageRoot']) / 'protocol/site/jacoco/jacoco.xml'
    module = next(m for m in audit.read_json(ROOT / inventory['measurementBindings']['manifest'])['modules'] if m['module'] == 'protocol')
    require(audit.digest(coverage) == module['coverageXmlSha256'], 'qualified coverage hash required')
    classes = {n.get('name'): n for n in ET.parse(coverage).getroot().findall('./package/class')}
    owned = [x for x in inventory['artifacts'] if x['owner'] == ID]
    require({x['path'] for x in owned} == set(task['ownedArtifacts']), 'all20 exact owned artifacts required')
    for item in owned:
        require(audit.digest(ROOT / item['path']) == item['sha256'], 'owned artifact byte drift')
        if item['kind'] == 'JAVA':
            node = classes[item['class']]
            require(all(int(c.get('missed')) == 0 for c in node.findall('counter') if c.get('type') in ('LINE', 'METHOD', 'CLASS', 'BRANCH')), 'every owned family four100 required')
    old_out = W / 'pg3288-layout-acceptance-v1'
    old_matrix = ROOT / PUBLIC / 'layout-acceptance.json'
    if resume:
        # First failure wrote only an intention and private before-images. It
        # never applied acceptance; prove this, do not overwrite that attempt.
        for path in (master_path, snapshot_path):
            require(path.read_bytes() == (old_out / ('before-' + path.name)).read_bytes(), 'original failed attempt must not have applied WBS')
        intent = audit.read_json(old_matrix)
        require(intent['productionSource'] == SOURCE and intent['wbs'] == ID
                and intent['operatorSource'] == 'bb5be0a9296782c8eb2e952cda14e3b8fcc612e4'
                and audit.digest(old_matrix) == 'e6b36c991fd697110be9a43ebe641ab0ccb9d893e3cf5d15907f4b219c76ace2', 'exact preserved original un-applied intent required')
    out = W / ('pg3288-layout-acceptance-v2' if resume else 'pg3288-layout-acceptance-v1'); out.mkdir(mode=0o700)
    for path in (master_path, snapshot_path):
        with (out / ('before-' + path.name)).open('xb') as stream:
            stream.write(path.read_bytes())
    proof_paths = [SPEC, PUBLIC / 'canonical-fixtures.json', PUBLIC / 'test-witness.json', Path(inventory['measurementBindings']['manifest'])]
    matrix = {'productionSource': SOURCE, 'wbs': ID, 'run': 'PG3288-individual-layout-review',
              'verifiedChecks': [c['id'] for c in task['acceptanceChecks']],
              'review': str(SPEC), 'reviewedBy': 'Codex individual contract/oracle/scope review; not GitHub approval',
              'ownedArtifacts': [{'path': a['path'], 'sha256': a['sha256']} for a in owned],
              'proofs': [{'path': str(p), 'sha256': audit.digest(ROOT / p)} for p in proof_paths],
              'dependencies': [], 'actualExit': 0, 'acceptedLeafDelta': 1, 'formalAccepted': False,
              'wholeEffortCompletionRate': None, 'coverageCredit': 0, 'newPtCredit': 0, 'vmActions': 0,
              'operatorSource': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
    if resume:
        matrix.update(originalAttemptExit=1, originalAttemptApplied=False,
                      originalIntentSha256=audit.digest(old_matrix), resumedAfterBug='BUG1284/YKT1050')
    matrix_path = ROOT / PUBLIC / ('layout-acceptance-v2.json' if resume else 'layout-acceptance.json')
    with matrix_path.open('x') as stream:
        json.dump(matrix, stream, ensure_ascii=False, indent=2); stream.write('\n')
    acceptance = {'status': 'ACCEPTED', 'source': SOURCE,
                  'evidence': [{'path': str(matrix_path.relative_to(ROOT)), 'sha256': audit.digest(matrix_path),
                                'source': SOURCE, 'run': matrix['run'], 'verifiedChecks': matrix['verifiedChecks']}],
                  'criteriaSatisfied': matrix['verifiedChecks'], 'acceptedBy': matrix['reviewedBy']}
    changed = copy.deepcopy(task); changed['acceptance'] = acceptance
    rows = copy.deepcopy(snapshot['rows']); next(r for r in rows if r['id'] == ID)['acceptance'] = acceptance
    candidates = [(master_path, one_line_task(master_path.read_text(), ID, changed)),
                  (snapshot_path, rewrite_root(snapshot_path.read_text(), {'rows': rows}))]
    temporary = []
    for path, text in candidates:
        target = out / ('candidate-' + path.name); target.write_text(text); temporary.append(target)
    audit.verify(master_path=temporary[0], snapshot_path=temporary[1])
    for path, text in candidates:
        replace_public(path, text.encode())
    after = audit.verify(); require(after['acceptedTasks'] == 1, 'exactly one accepted leaf required')
    with (out / 'manifest.safe.json').open('x') as stream:
        json.dump({'actualExit': 0, 'before': before, 'after': after, 'matrixSha256': audit.digest(matrix_path), 'productionSource': SOURCE}, stream)
    print(json.dumps({'actualExit': 0, 'acceptedTasks': 1, 'scope': ID, 'formalChanged': False, 'effortPercent': None}))
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resume-bug1284', action='store_true')
    raise SystemExit(main(parser.parse_args().resume_bug1284))
