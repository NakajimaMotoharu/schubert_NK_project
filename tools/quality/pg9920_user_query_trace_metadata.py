"""Emit apply_patch for two current WBS references; independently verify raw hash and actual audit HOLD."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9338_wbs_reference_metadata_post as metadata
from pg9880_snapshot_nonce_trace import audit
import pg9916_user_query_changed_test_trace as registry

ROOT = data.ROOT
PMO = 'documents/400_PGPT/470_PMO/'
INV = PMO+'485_WBS網羅性・受入対応.json'
SNAP = PMO+'486_WBS現行実績.json'
BEFORE = '82d1577acd5e17c2d056ef5ad2707db5756cdf98'
REGISTRY = 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9916-user-query-changed-test-trace-v1/manifest.json'
REGISTRY_SHA = '42899a03f8ddd657805f55c053cfb0f64616356c2ff889a912c8d77505303b0b'
PROOF = 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9918-user-query-trace-post-v1/manifest.json'
PROOF_SHA = '406809d157c194743667ffbc4daae32c4ba934f49bbc2f9f2fcd2d09dd521c3b'
OUT = data.BASE/'PG9920-user-query-trace-metadata-post-v1'
SECTIONS = ('currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership')


def inputs():
    old_raw = subprocess.check_output(['git','show',BEFORE+':'+INV],cwd=ROOT)
    old_snap_raw = subprocess.check_output(['git','show',BEFORE+':'+SNAP],cwd=ROOT)
    joined,proof = data.read_checked(ROOT/REGISTRY,REGISTRY_SHA),data.read_checked(ROOT/PROOF,PROOF_SHA)
    assert joined['actualExit'] == proof['actualExit'] == 0 and joined['source'] == proof['source'] == registry.SOURCE
    return old_raw,old_snap_raw,joined,proof


def expected_inventory(old_raw, joined):
    result = json.loads(old_raw)
    for name in SECTIONS:
        section = result[name]
        refkeys = ['source','manifest','sha256','record']+(['guardManifest','guardSha256'] if name == SECTIONS[1]
            else ['independentPostManifest','independentPostSha256'])
        assert 'previousUserQueryTestHashOverlay' not in section and 'currentChangedTestBindings' not in section
        section['previousUserQueryTestHashOverlay'] = {k:copy.deepcopy(section[k]) for k in refkeys}
        section['source'] = registry.SOURCE
        section['manifest'] = REGISTRY
        section['sha256'] = REGISTRY_SHA
        section['record'] = 'evidence/01_PT/018_NK-OPS-001/2007_User照会2Test現source束縛_結果.md'
        if name == SECTIONS[1]:
            section['guardManifest'],section['guardSha256'] = PROOF,PROOF_SHA
        else:
            section['independentPostManifest'],section['independentPostSha256'] = PROOF,PROOF_SHA
        section['currentChangedTestBindings'] = joined['changedTestBindings']
    return result


def replaced(raw, key, value):
    lines = raw.decode().splitlines(keepends=True)
    found = [i for i,line in enumerate(lines) if line.startswith('  "'+key+'":')]
    assert len(found) == 1
    index = found[0]
    original = lines[index]
    assert original.endswith(',\n')
    replacement = '  "'+key+'": '+json.dumps(value,ensure_ascii=False,separators=(',',':'))+',\n'
    lines[index] = replacement
    return ''.join(lines).encode(),original,replacement


def emit():
    old_raw,old_snap_raw,joined,_ = inputs()
    assert (ROOT/INV).read_bytes() == old_raw and (ROOT/SNAP).read_bytes() == old_snap_raw
    expected = expected_inventory(old_raw,joined)
    new_raw = old_raw
    replacements = []
    for name in SECTIONS:
        new_raw,old_line,new_line = replaced(new_raw,name,expected[name])
        replacements.append((old_line,new_line))
    _,old_line,new_line = replaced(old_snap_raw,'inventorySha256',data.sha(new_raw))
    patch = '*** Begin Patch\n*** Update File: '+str(ROOT/INV)+'\n'
    for before,after in replacements:
        patch += '@@\n-'+before+'+'+after
    patch += '*** Update File: '+str(ROOT/SNAP)+'\n@@\n-'+old_line+'+'+new_line+'*** End Patch\n'
    print(patch,end='')


def contract(inv_raw,snap_raw,old_raw,old_snap_raw,joined):
    metadata.validate(inv_raw,snap_raw,json.loads(old_raw),json.loads(old_snap_raw))
    if json.loads(inv_raw) != expected_inventory(old_raw,joined):
        raise ValueError('exact two current references/history and static-only Test bindings')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    old_raw,old_snap_raw,joined,proof = inputs()
    raw,sraw = (ROOT/INV).read_bytes(),(ROOT/SNAP).read_bytes()
    contract(raw,sraw,old_raw,old_snap_raw,joined)
    negatives = []
    for label,edit in (
        ('source',lambda a,b:a[SECTIONS[0]].update(source='0'*40)),
        ('proof',lambda a,b:a[SECTIONS[1]].update(guardSha256='0'*64)),
        ('owner',lambda a,b:a[SECTIONS[0]]['currentChangedTestBindings'][0].update(canonicalOwner='WBS-G13.07')),
        ('history',lambda a,b:a[SECTIONS[1]]['previousUserQueryTestHashOverlay'].update(source=registry.SOURCE)),
        ('unknown-erased',lambda a,b:a[SECTIONS[0]].update(unregistered=0,registered=1796)),
        ('support-lost',lambda a,b:a[SECTIONS[0]].pop('sharedOracleSupportDecision')),
        ('formal',lambda a,b:a[SECTIONS[1]].update(formalAccepted=True)),
        ('raw-hash',lambda a,b:b.update(inventorySha256='0'*64))):
        inv,snap = json.loads(raw),json.loads(sraw)
        edit(inv,snap)
        inv_bytes = json.dumps(inv,ensure_ascii=False).encode()
        if label != 'raw-hash':
            snap['inventorySha256'] = data.sha(inv_bytes)
        try:
            contract(inv_bytes,json.dumps(snap).encode(),old_raw,old_snap_raw,joined)
        except ValueError:
            negatives.append(label)
        else:
            raise AssertionError('invalid WBS metadata accepted')
    for name in ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json'):
        assert (ROOT/PMO/name).read_bytes() == subprocess.check_output(['git','show',BEFORE+':'+PMO+name],cwd=ROOT)
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in proof['auditSourceHashes'].items())
    after = audit()
    assert after['actualExit'] == 1 and after['lastError'] == 'ValueError: current physical candidate exact Git/worktree scope'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=registry.SOURCE,invocation=invocation,
        registryManifestSha256=REGISTRY_SHA,independentPostSha256=PROOF_SHA,inventorySha256=data.sha(raw),snapshotSha256=data.sha(sraw),
        registered=1794,javaPaths=1796,unknown=2,reboundTestHashes=2,metadataNegativeVectors=negatives,
        original941AndHistorical943Preserved=True,originalBudgetAndAcceptanceSemanticsPreserved=True,
        onlyTwoCurrentSectionsChanged=True,snapshotOnlyChangedField='inventorySha256',rawHashFallbackAllowed=False,
        wholeWbsAuditBefore=proof['wholeWbsAuditBefore'],wholeWbsAuditAfter=after,
        originalBeforeAuditReusedWithoutReplay=True,productTestsExecuted=0,dynamicQualificationInferred=False,
        newAccepted=0,formalUpdated=False,wholeG13Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,metadataNegatives=len(negatives),inventorySha256=data.sha(raw),
        wholeAuditBefore=1,wholeAuditAfter=1,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        emit()
    elif not sys.argv[1:]:
        main()
    else:
        raise ValueError('known metadata emission/verification mode only')
