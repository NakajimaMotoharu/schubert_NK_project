"""Independent preservation check for additive static reference only."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg15922_g13_static_inventory_binding as writer

OUT = data.BASE / 'PG15924-g13-static-binding-post-v1'

def assess(inv, snap, old, old_snap, ref):
    current = copy.deepcopy(inv)
    assert current.pop(writer.FIELD) == ref and current == old
    snapshot = copy.deepcopy(snap)
    snapshot['inventorySha256'] = old_snap['inventorySha256']
    assert snapshot == old_snap
    assert ref['status'] == 'UNQUALIFIED_STATIC_INVENTORY_NOT_WHOLE_ACCEPTANCE'
    assert ref['qualifiedCandidateReplaced'] is ref['currentWholeSourceQualified'] is ref['exactMethodTestRequirementTraceVerified'] is ref['formalUpdated'] is False
    assert type(ref['newAccepted']) is int and ref['newAccepted'] == 0 and ref['effortPercent'] is None

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    p = json.loads((writer.OUT / 'manifest.json').read_bytes())
    assert p['actualExit'] == 0 and p['source'] == writer.descriptor.SOURCE
    old, old_snap = [json.loads(subprocess.check_output(['git', 'show', writer.descriptor.BEFORE + ':' + name], cwd=data.ROOT)) for name in (writer.INV, writer.SNAP)]
    inv, snap = [data.read_checked(data.ROOT / name, p[key]) for name, key in ((writer.INV, 'inventorySha256'), (writer.SNAP, 'snapshotSha256'))]
    assert snap['inventorySha256'] == p['inventorySha256']
    d = data.read_checked(writer.descriptor.OUT / 'manifest.json', writer.post.PIN)
    q = data.read_checked(writer.post.OUT / 'manifest.json', writer.POST_PIN)
    ref = inv[writer.FIELD]
    assert ref['sha256'] == writer.post.PIN and ref['independentSha256'] == writer.POST_PIN and ref['artifactsSha256'] == d['artifactsSha256'] and ref['artifactCount'] == 1065
    assess(inv, snap, old, old_snap, ref)
    negatives = []
    for label, mutate in [('candidate', lambda i, s: i['currentPhysicalCandidate'].update(source=writer.descriptor.SOURCE)), ('logical-scope', lambda i, s: i['artifacts'].pop()), ('snapshot', lambda i, s: s.update(effortPercent=0)), ('acceptance', lambda i, s: i[writer.FIELD].update(newAccepted=1)), ('qualified', lambda i, s: i[writer.FIELD].update(currentWholeSourceQualified=True)), ('descriptor-drop', lambda i, s: i.pop(writer.FIELD))]:
        bad, bad_snap = copy.deepcopy(inv), copy.deepcopy(snap)
        mutate(bad, bad_snap)
        try:
            assess(bad, bad_snap, old, old_snap, ref)
        except (AssertionError, KeyError):
            negatives.append(label)
        else:
            raise ValueError('unrejected change: ' + label)
    verify(p['invocation'])
    verify(d['invocation'])
    verify(q['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation, source=writer.descriptor.SOURCE,
        bindingManifestSha256=data.sha((writer.OUT / 'manifest.json').read_bytes()), inventorySha256=p['inventorySha256'], snapshotSha256=p['snapshotSha256'],
        independentNegativeVectors=len(negatives), negativeLabels=negatives, frozenCandidateAndAllPriorFieldsUnchanged=True,
        currentWholeSourceQualified=False, wholeG13Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, independentNegativeVectors=len(negatives), newAccepted=0)))

if __name__ == '__main__':
    main()
