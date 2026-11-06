"""Independent path/hash/owner qualification, with no Product or external action."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

r = Path.cwd()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
canonical = lambda x: sha(json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())
p = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21942-current56720-static-artifact-lineage-v1/manifest.json'
assert sha(p.read_bytes()) == 'bb8ed9e6d7e33cc2c29e912cb35e055b73f527026b3c49e3b3aab8fcc36d6673'
m = json.loads(p.read_text())
assert m['actualExit'] == 0 and m['artifactCount'] == 1068
assert (m['changedArtifacts'], m['addedArtifacts'], m['unchangedArtifacts'], m['removedArtifacts']) == (4, 1, 1063, 0)
for n, h in m['files'].items():
    assert sha((p.parent / n).read_bytes()) == h
oldp = r / m['previous']['path']
assert sha(oldp.read_bytes()) == m['previous']['sha256']
old = json.loads(oldp.read_text())
assert sha((oldp.parent / 'artifacts.json').read_bytes()) == old['files']['artifacts.json']
before = {a['path']: a for a in json.loads((oldp.parent / 'artifacts.json').read_text())}
rows = json.loads((p.parent / 'artifacts.json').read_text())
after = {a['path']: a for a in rows}
assert len(before) == 1067 and len(after) == len(rows) == 1068 and set(before) <= set(after)
added = {'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/InboundConsumerGroup.java':'WBS-P005-03'}
assert set(after) - set(before) == set(added)
held = set(m['heldNamesExcludedBeforeIO'])
assert all(Path(n).name not in held for n in after)
changes = {}
for n, a in after.items():
    assert sha((r / n).read_bytes()) == a['sha256']
    assert a['staticSource'] == m['source'] and a['acceptance'] == 'UNASSESSED'
    assert a['qualification'] == 'UNQUALIFIED_STATIC_DESCRIPTOR_ONLY'
    assert a['runtimeQualificationTransferred'] is False and a['methodTestRequirementTrace'] == 'NOT_VERIFIED'
    assert a['owner'] == a['costOwner'] and a['additionalBudgetPp'] == 0
    if n in before:
        b = before[n]
        assert a['owner'] == b['owner'] and a['costOwner'] == b['costOwner'] and a['kind'] == b['kind']
        assert a['previousLineage'] == b['lineage'] and a['lineage']['oldSha256'] == b['sha256']
        assert a['lineage']['source'] == old['source']
        assert a['lineage']['byteChanged'] == (a['sha256'] != b['sha256'])
        if a['sha256'] != b['sha256']:
            changes[n] = (b['sha256'], a['sha256'])
    else:
        assert a['owner'] == added[n] and a['kind'] == 'JAVA' and a['previousLineage'] is None
assert len(changes) == 4
delta = json.loads((p.parent / 'changed-artifacts.json').read_text())
assert {a['path']: (a['oldSha256'], a['currentSha256']) for a in delta} == changes
new = json.loads((p.parent / 'added-artifacts.json').read_text())
assert {a['path']: a['owner'] for a in new} == added and len(new) == 1
for a in new:
    assert a['additionalBudgetPp'] == 0 and a['retrospectiveCostReallocation'] is False
statuses = subprocess.check_output(['git', 'diff', '--name-status', '--no-renames', old['source'], m['source'], '--', *sorted(after)], text=True).splitlines()
assert set(statuses) == {'M\t' + n for n in changes} | {'A\t' + n for n in added}
assert not subprocess.check_output(['git', 'diff', '--name-only', m['source'], 'HEAD', '--', *sorted(after)])
normal_inputs = {}
for ref in m['normalManifests']:
    f = Path(ref['path'])
    assert sha(f.read_bytes()) == ref['sha256']
    v = json.loads(f.read_text())
    assert v['actualExit'] == 0 and v['source'] == ref['source']
    java = {n: h for n, h in v['begin']['inputHashes'].items() if '/src/main/java/' in n and n.endswith('.java')}
    assert len(java) == ref['javaSources'] and not (set(java) & set(normal_inputs))
    normal_inputs.update(java)
assert normal_inputs == {n: a['sha256'] for n, a in after.items() if '/src/main/java/' in n and n.endswith('.java')}
assert len(normal_inputs) == 972
eligible = lambda n: ('/src/main/java/' in n and n.endswith('.java')) or '/src/main/resources/' in n or n.startswith('src/deployment/')
tracked=subprocess.check_output(['git','ls-tree','-r','-z','--name-only',m['source'],'--','src','program/characterization']).decode().split('\0')
assert set(after)=={n for n in tracked if n and eligible(n)}
rootdelta=subprocess.check_output(['git','diff','--name-status','--no-renames',old['previous']['source'],m['source'],'--',*sorted(after)],text=True).splitlines()
assert sum(n.startswith('M\t') for n in rootdelta)==27 and sum(n.startswith('A\t') for n in rootdelta)==3 and len(rootdelta)==30
proofp=r/'evidence/01_PT/005_NK-MSG-001/evidence/PG21930-consumer-stop-static-independent-post-v1/manifest.json'
assert sha(proofp.read_bytes())=='a7f4de3a2de800464ecddc23c208d04ed021b3ee43f7d1010bdd2e4aa94ffc7e'
proof=json.loads(proofp.read_text());assert proof['productionCoreMain']==m['source'] and proof['newInterfaceNoCodeMetadata'] and proof['productTestsExecuted']==0 and proof['coverage'] is None and proof['bugsRemainOpen']==['BUG-2407','YKT-2152']
assert m['dynamicRegressionStatus']=='PT-JMS-STOP-GROUP001..006 NOT_RUN/HOLD'
inv = json.loads((r / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_text())
frozen = {k: canonical(inv[k]) for k in ['artifacts', 'currentPhysicalCandidate']}
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
assert sha(subprocess.check_output(['git', 'show', head + ':' + str(Path(__file__).relative_to(r))])) == sha(Path(__file__).read_bytes())
out = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21944-current56720-static-lineage-independent-post-v1'
assert not out.exists()
out.mkdir()
result = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), checkerSource=head,
    checkerSha256=sha(Path(__file__).read_bytes()), source=m['source'], observerSource=m['observerSource'],
    original=dict(path=str(p.relative_to(r)), sha256=sha(p.read_bytes())), artifactCount=1068,
    changed=4, added=1, unchanged=1063, removed=0, boundJavaSources=972,
    ownerAndCostPreserved=True, rootLineageChanged=27,rootLineageAdded=3,interfaceNoCodeMetadataBound=True,interfaceCoverageSuccessInferred=False,bugsRemainOpen=proof['bugsRemainOpen'], unclassifiedNewOwners=0, additionalBudgetPp=0,
    frozenInventorySemanticHashes=frozen, exactMethodTestRequirementTraceVerified=False,
    wholeAuditAccepted=False, wholeG13Accepted=False, productTests=0,
    newMethods=0, newSourceProofs=0, newAcceptance=0, effortRate=None)
(out / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(actualExit=0, artifactCount=1068, added=1, changed=4,
    manifestSha256=sha((out / 'manifest.json').read_bytes()))))
