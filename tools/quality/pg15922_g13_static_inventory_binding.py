"""Add a separate UNQUALIFIED reference; preserve frozen candidate and all acceptance."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9954_pure_query_registry_metadata import INV, SNAP, replaced
import pg15918_g13_current_static_descriptor as descriptor
import pg15920_g13_static_descriptor_post as post

OUT = data.BASE / 'PG15922-g13-static-inventory-binding-v1'
FIELD = 'currentUnqualifiedPhysicalInventoryPG15918'
POST_PIN = 'f8538961ddc61f4231c2d4092d77134802916974afc344fe0f57fd562997c4cd'

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    before = [subprocess.check_output(['git', 'show', descriptor.BEFORE + ':' + name], cwd=data.ROOT) for name in (INV, SNAP)]
    assert all(raw == (data.ROOT / name).read_bytes() for raw, name in zip(before, (INV, SNAP)))
    p = data.read_checked(descriptor.OUT / 'manifest.json', post.PIN)
    q = data.read_checked(post.OUT / 'manifest.json', POST_PIN)
    assert p['actualExit'] == q['actualExit'] == 0 and q['parentManifestSha256'] == post.PIN
    assert p['source'] == q['source'] == descriptor.SOURCE and p['artifactCount'] == q['artifactCount'] == 1065
    ref = dict(source=descriptor.SOURCE, manifest=str((descriptor.OUT / 'manifest.json').relative_to(data.ROOT)), sha256=post.PIN,
               independentManifest=str((post.OUT / 'manifest.json').relative_to(data.ROOT)), independentSha256=POST_PIN,
               artifactCount=1065, artifactsSha256=p['artifactsSha256'], status=p['status'],
               qualifiedCandidateReplaced=False, currentWholeSourceQualified=False, exactMethodTestRequirementTraceVerified=False,
               newAccepted=0, formalUpdated=False, effortPercent=None)
    old, old_snap = map(json.loads, before)
    assert FIELD not in old and before[0].startswith(b'{\n')
    result = b'{\n  ' + json.dumps(FIELD).encode() + b': ' + json.dumps(ref, ensure_ascii=False, separators=(',', ':')).encode() + b',\n' + before[0][2:]
    new_snap, _, _ = replaced(before[1], 'inventorySha256', data.sha(result))
    restored = json.loads(result)
    assert restored.pop(FIELD) == ref and restored == old
    restored_snap = json.loads(new_snap)
    restored_snap['inventorySha256'] = old_snap['inventorySha256']
    assert restored_snap == old_snap
    verify(p['invocation'])
    verify(q['invocation'])
    verify(invocation)
    OUT.mkdir()
    (data.ROOT / INV).write_bytes(result)
    (data.ROOT / SNAP).write_bytes(new_snap)
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation, source=descriptor.SOURCE, beforeGit=descriptor.BEFORE,
        field=FIELD, descriptorManifestSha256=post.PIN, independentManifestSha256=POST_PIN,
        inventorySha256=data.sha(result), snapshotSha256=data.sha(new_snap),
        frozenCandidateAndAllPriorFieldsUnchanged=True, snapshotOnlyInventoryHashChanged=True,
        wholeAuditExecuted=False, currentWholeSourceQualified=False, wholeG13Accepted=False,
        newAccepted=0, productTestsExecuted=0, formalUpdated=False, effortPercent=None))
    print(data.sha((OUT / 'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
