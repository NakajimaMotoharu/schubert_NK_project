"""Apply the source-domain repair from qualified static descriptors, retaining all old values."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import platform
import subprocess
import sys

import wbs_current_source_structure as view_tool

B = Path('evidence/01_PT/018_NK-OPS-001')
C = B / 'input/653_current_source_wbs_structure_scope.json'
O = B / 'evidence/PG24162-wbs-current-source-structure-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def capture(name, command):
    start = datetime.datetime.now().astimezone().isoformat()
    run = subprocess.run(command, capture_output=True, text=True, timeout=60)
    (O / (name + '.stdout')).write_text(run.stdout)
    (O / (name + '.stderr')).write_text(run.stderr)
    return dict(command=command, actualExit=run.returncode, startedAtJST=start,
                endedAtJST=datetime.datetime.now().astimezone().isoformat(),
                stdoutSha256=sha(O / (name + '.stdout')), stderrSha256=sha(O / (name + '.stderr')))


def main():
    assert not O.exists()
    c = load(C)
    for name, digest in c['inputPins'].items():
        path = Path(name)
        if name == 'tools/quality/wbs_progress_audit.py':
            path = B / 'evidence/PG24158-wbs-source-domain-before-v1/wbs_progress_audit.py'
        assert sha(path) == digest, name
    ip, sp, mp = map(Path, (c['wbsInventory'], c['wbsSnapshot'], c['wbsMaster']))
    old_i, old_s, old_m = load(ip), load(sp), load(mp)
    assert old_s['inventorySha256'] == sha(ip)
    base = load(Path(c['descriptorBase']['path']))
    current = {v['path']: v for v in old_i['artifacts']}
    overrides = {v['path']: {name: current[v['path']][name] for name in ['owner', 'costOwner', 'kind']}
                 for v in base if v['path'] in current
                 and any(v[name] != current[v['path']][name] for name in ['owner', 'costOwner', 'kind'])}
    view = dict(version=1, source=c['source'], artifactCount=1068, productionArtifacts=1063,
                characterizationArtifacts=5, descriptorBase=c['descriptorBase'],
                identityProof=c['identityProof'], lineageManifest=c['lineageManifest'],
                ownerKindOverrides=overrides, addedComparedToLegacy=c['addedPaths'], retiredHistoricalPaths=c['retiredPaths'],
                preservedLegacyInventorySource=old_i['source'],
                preservedLegacyCandidateSource=old_i['currentPhysicalCandidate']['source'],
                preservedLegacyArtifactRowsDigest=view_tool.value_digest(old_i['artifacts']),
                preservedLegacyCandidateDigest=view_tool.value_digest(old_i['currentPhysicalCandidate']),
                qualification='CURRENT_STATIC_STRUCTURE_AND_RESPONSIBILITY_ONLY', runtimeQualified=False,
                wholeAcceptance=False, oldRuntimeQualificationTransferred=False, newAcceptance=0, effortRate=None)
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', '-z', c['source'], '--',
                                     'src', 'program/characterization/src/main/java']).decode().rstrip('\0').split('\0')
    resolved = view_tool.resolve_descriptors(view, base, old_i['artifacts'], old_m['tasks'], names)
    assert len(resolved) == 1068 and len(overrides) == 131
    assert set(c['addedPaths']) == {v['path'] for v in resolved} - set(current)
    assert len(c['addedPaths']) == 9 and len(c['retiredPaths']) == 2
    assert c['viewKey'] not in old_i and c['masterProjectionKey'] not in old_m
    after_i, after_s, after_m = copy.deepcopy(old_i), copy.deepcopy(old_s), copy.deepcopy(old_m)
    after_i[c['viewKey']] = view
    after_m[c['masterProjectionKey']] = dict(source=c['source'], viewKey=c['viewKey'], artifactCount=1068,
          ownerArtifactCounts=view_tool.owner_counts(v['owner'] for v in resolved),
          descriptorBase=c['descriptorBase'], qualification='STATIC_RESPONSIBILITY_NOT_RUNTIME_OR_ACCEPTANCE',
          runtimeQualified=False, newAcceptance=0, effortRate=None)
    inventory_bytes, master_bytes = encoded(after_i), encoded(after_m)
    after_s['inventorySha256'] = hashlib.sha256(inventory_bytes).hexdigest()
    snapshot_bytes = encoded(after_s)
    O.mkdir()
    for path in [ip, sp, mp]:
        (O / ('before-' + path.name)).write_bytes(path.read_bytes())
    regression = capture('metadata-regression', [sys.executable, '-B', '-m', 'unittest',
                                                'wbs_current_source_structure_test', '-v'])
    assert regression['actualExit'] == 0
    (O / 'current-source-structure-view.json').write_bytes(encoded(view))
    ip.write_bytes(inventory_bytes)
    mp.write_bytes(master_bytes)
    sp.write_bytes(snapshot_bytes)
    assert load(sp)['inventorySha256'] == sha(ip)
    structure = capture('current-structure', [sys.executable, '-B', 'tools/quality/wbs_progress_audit.py',
                                             '--current-source-structure-only'])
    assert structure['actualExit'] == 0
    structure_value = json.loads((O / 'current-structure.stdout').read_text())
    assert structure_value['artifactCount'] == 1068 and structure_value['wholeWbsAccepted'] is False
    full = capture('full-audit', [sys.executable, '-B', 'tools/quality/wbs_progress_audit.py'])
    assert full['actualExit'] == 1
    full_value = json.loads((O / 'full-audit.stdout').read_text())
    assert full_value['status'] == 'HOLD' and full_value['wholeWbsAccepted'] is False
    assert full_value['privateRuntimeEvidenceRead'] is False and full_value['unverifiedChecks']
    result = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=c['source'],
                  config={'path': str(C), 'sha256': sha(C)}, identityRecomputed=False,
                  artifactCount=1068, productionArtifacts=1063, characterizationArtifacts=5,
                  canonicalOwnerKindOverrides=131, sharedLegacyPaths=1059, addedPaths=9, retiredPaths=2,
                  legacyArtifactRowsUnchanged=True, legacyCandidateUnchanged=True,
                  originalTasksBudgetAcceptanceUnchanged=True, currentStructureExit=0, fullAuditExit=1,
                  fullAuditStatus='HOLD', fullAuditUnverifiedChecks=full_value['unverifiedChecks'],
                  metadataRegressionTests=8, productTestsExecuted=0, formalUpdated=False, newAcceptance=0, effortRate=None,
                  runtimeQualificationTransferred=False, privateRuntimeEvidenceRead=False,
                  pythonVersion=platform.python_version(), os=platform.system(),
                  stages={'metadataRegression': regression, 'currentStructure': structure, 'fullAudit': full},
                  modifiedDocuments={str(p): sha(p) for p in [ip, sp, mp]},
                  files={p.name: sha(p) for p in O.iterdir()},
                  tools={str(p): sha(p) for p in [Path(__file__), Path('tools/quality/wbs_current_source_structure.py'),
                         Path('tools/quality/wbs_current_source_structure_test.py'), Path('tools/quality/wbs_progress_audit.py')]})
    (O / 'manifest.json').write_bytes(encoded(result))
    print(json.dumps(dict(actualExit=0, artifactCount=1068, ownerKindOverrides=131, metadataTests=8,
                         currentStructureExit=0, fullAuditExit=1, fullAuditStatus='HOLD',
                         manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
