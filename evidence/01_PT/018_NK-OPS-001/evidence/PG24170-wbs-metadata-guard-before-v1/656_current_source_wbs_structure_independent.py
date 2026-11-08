"""Independent static-view and history delta verification. No runtime operations or test replay."""
from pathlib import Path
from collections import Counter
import copy
import datetime
import hashlib
import json

B = Path('evidence/01_PT/018_NK-OPS-001')
C = B / 'input/653_current_source_wbs_structure_scope.json'
P = B / 'evidence/PG24162-wbs-current-source-structure-v1'
O = B / 'evidence/PG24164-wbs-current-source-structure-independent-v1'


def load(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_state(master, inventory, snapshot, before_m, before_i, before_s, cfg, base, full_report):
    m, i, s = copy.deepcopy(master), copy.deepcopy(inventory), copy.deepcopy(snapshot)
    projection = m.pop(cfg['masterProjectionKey'])
    view = i.pop(cfg['viewKey'])
    s['inventorySha256'] = before_s['inventorySha256']
    assert m == before_m and i == before_i and s == before_s
    assert view['source'] == cfg['source'] and view['descriptorBase'] == cfg['descriptorBase']
    assert view['identityProof'] == cfg['identityProof'] and view['lineageManifest'] == cfg['lineageManifest']
    assert view['runtimeQualified'] is False and view['wholeAcceptance'] is False
    assert view['oldRuntimeQualificationTransferred'] is False
    previous = {v['path']: v for v in before_i['artifacts']}
    expected_overrides, owners = {}, Counter()
    for row in base:
        path = row['path']
        old = previous.get(path)
        wanted = {key: old[key] if old is not None else row[key] for key in ['owner', 'costOwner', 'kind']}
        if any(wanted[key] != row[key] for key in wanted):
            expected_overrides[path] = wanted
        assert wanted['owner'] == wanted['costOwner']
        owners[wanted['owner']] += 1
    assert view['ownerKindOverrides'] == expected_overrides and len(expected_overrides) == 131
    paths = {v['path'] for v in base}
    assert view['addedComparedToLegacy'] == sorted(paths - set(previous)) == cfg['addedPaths']
    assert view['retiredHistoricalPaths'] == sorted(set(previous) - paths) == cfg['retiredPaths']
    assert view['artifactCount'] == 1068 and view['productionArtifacts'] == 1063 and view['characterizationArtifacts'] == 5
    assert projection['source'] == cfg['source'] and projection['artifactCount'] == 1068
    assert projection['viewKey'] == cfg['viewKey'] and projection['ownerArtifactCounts'] == dict(owners)
    assert projection['runtimeQualified'] is False and projection['newAcceptance'] == 0
    assert full_report['status'] == 'HOLD' and full_report['wholeWbsAccepted'] is False
    assert full_report['privateRuntimeEvidenceRead'] is False and full_report['originalRuntimeTestsExecuted'] is False
    assert full_report['newAcceptance'] == 0 and full_report['formalUpdated'] is False
    assert len(full_report['unverifiedChecks']) == 4


def main():
    assert not O.exists()
    cfg = load(C)
    result = load(P / 'manifest.json')
    assert result['actualExit'] == 0
    for name, pin in result['files'].items():
        assert sha(P / name) == pin
    for name, pin in result['tools'].items():
        assert sha(Path(name)) == pin
    mp, ip, sp = map(Path, (cfg['wbsMaster'], cfg['wbsInventory'], cfg['wbsSnapshot']))
    master, inventory, snapshot = load(mp), load(ip), load(sp)
    before_m, before_i, before_s = [load(P / ('before-' + p.name)) for p in [mp, ip, sp]]
    assert snapshot['inventorySha256'] == sha(ip)
    assert sha(Path('documents/400_PGPT/470_PMO/484_WBSコスト枠・細分化.json')) == cfg['inputPins']['documents/400_PGPT/470_PMO/484_WBSコスト枠・細分化.json']
    assert sha(Path(cfg['descriptorBase']['path'])) == cfg['descriptorBase']['sha256']
    base = load(Path(cfg['descriptorBase']['path']))
    full = json.loads((P / 'full-audit.stdout').read_text())
    structure = json.loads((P / 'current-structure.stdout').read_text())
    assert result['stages']['metadataRegression']['actualExit'] == 0 and result['metadataRegressionTests'] == 8
    assert result['stages']['currentStructure']['actualExit'] == 0
    assert result['stages']['fullAudit']['actualExit'] == 1
    assert structure['status'] == 'PASS_CURRENT_STATIC_SOURCE_STRUCTURE_ONLY' and structure['wholeWbsAccepted'] is False
    assert structure['artifactCount'] == 1068 and structure['identityRecomputed'] is False
    check_state(master, inventory, snapshot, before_m, before_i, before_s, cfg, base, full)
    negatives = []
    for label, mutate in [
        ('legacy-artifact-change', lambda m, i, s, f: i['artifacts'][0].update(sha256='0' * 64)),
        ('runtime-import', lambda m, i, s, f: i[cfg['viewKey']].update(runtimeQualified=True)),
        ('source-change', lambda m, i, s, f: i[cfg['viewKey']].update(source='0' * 40)),
        ('new-set-missing', lambda m, i, s, f: i[cfg['viewKey']].update(addedComparedToLegacy=[])),
        ('retired-set-missing', lambda m, i, s, f: i[cfg['viewKey']].update(retiredHistoricalPaths=[])),
        ('projection-owner-missing', lambda m, i, s, f: m[cfg['masterProjectionKey']]['ownerArtifactCounts'].clear()),
        ('task-acceptance-change', lambda m, i, s, f: m['tasks'][0]['acceptance'].update(status='ACCEPTED')),
        ('full-fake-pass', lambda m, i, s, f: f.update(status='PASS')),
        ('private-read', lambda m, i, s, f: f.update(privateRuntimeEvidenceRead=True)),
        ('full-accepted', lambda m, i, s, f: f.update(wholeWbsAccepted=True)),
    ]:
        a, b, c, d = copy.deepcopy(master), copy.deepcopy(inventory), copy.deepcopy(snapshot), copy.deepcopy(full)
        mutate(a, b, c, d)
        try:
            check_state(a, b, c, before_m, before_i, before_s, cfg, base, d)
        except AssertionError:
            negatives.append(label)
        else:
            raise AssertionError(label)
    O.mkdir()
    output = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=cfg['source'],
                  producerManifest={'path': str(P / 'manifest.json'), 'sha256': sha(P / 'manifest.json')},
                  artifactCount=1068, productionArtifacts=1063, characterizationArtifacts=5,
                  canonicalOwnerKindOverrides=131, sharedLegacyPaths=1059, addedPaths=9, retiredPaths=2,
                  currentStructureExit=0, fullAuditExit=1, fullAuditStatus='HOLD', metadataRegressionTests=8,
                  metadataNegativeChecks=negatives, legacyArtifactRowsUnchanged=True, legacyCandidateUnchanged=True,
                  originalTasksBudgetAcceptanceUnchanged=True, inventorySnapshotReferenceCoherent=True,
                  identityRecomputed=False, runtimeQualificationTransferred=False, privateRuntimeEvidenceRead=False,
                  productTestsExecuted=0, wholeWbsAccepted=False, newAcceptance=0, formalUpdated=False, effortRate=None,
                  bugs=['BUG-2517'], ykts=['YKT-2255'], verifier={'path': str(Path(__file__)), 'sha256': sha(Path(__file__))})
    (O / 'manifest.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, artifactCount=1068, currentStructureExit=0, fullAuditExit=1,
                         metadataNegatives=len(negatives), manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
