"""Metadata-only latent guard witness. Expected diagnostic exit1, never a product PT failure/PASS."""
import copy
import json
import g07_host_class_provenance_inputs as data
import pg9838_shared_probe_snapshot_post as original
from host_tool_invocation import capture, verify
from pathlib import Path

OUT = data.BASE / 'PG9837-snapshot-hash-guard-witness-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    raw = (original.PMO / '485_WBS網羅性・受入対応.json').read_bytes()
    snapraw = (original.PMO / '486_WBS現行実績.json').read_bytes()
    inv,snap = json.loads(raw),json.loads(snapraw)
    assert snap['inventorySha256'] == data.sha(raw)
    changed = copy.deepcopy(snap)
    changed['inventorySha256'] = data.sha(json.dumps(inv,ensure_ascii=False).encode())
    assert changed['inventorySha256'] != data.sha(raw)
    original.current_contract(inv,changed)
    verify(invocation)
    OUT.mkdir()
    result = dict(actualExit=1,source=original.SOURCE,invocation=invocation,bug='BUG1766',horizontalReview='YKT1517',
        defectReproduced=True,expected='reject non-original-byte hash',actual='inner guard accepted canonical reserialization hash',
        actualMetadataWasCorrect=True,actualInventorySha256=data.sha(raw),hypotheticalInventorySha256=changed['inventorySha256'],
        originalHelperSha256=data.sha(Path(original.__file__).read_bytes()),actualFilesMutated=False,
        outerStrictBoundaryNotBypassed=True,productTestsExecuted=0,newAccepted=0,formalUpdated=False,actualExternalOperations=0)
    data.write(OUT / 'manifest.json',result)
    print(json.dumps(dict(actualExit=1,defectReproduced=True,productTestsExecuted=0,manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))
    raise SystemExit(1)


if __name__ == '__main__':
    main()
