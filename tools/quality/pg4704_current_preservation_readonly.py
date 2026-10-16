"""Fresh same-source stopped-data authentication for the next candidate, no start authority."""
import ast
import hashlib
import json
from pg4584_current_admission_image import execute, SOURCE
from pg1446_current_cold_stage import W

SLOT = 'pg4704-current-preservation-readonly-v1'
ORIGINAL = 'pg4658-current-owned-post-v1'
AFTER_SHA = '612beec0ca58fcf4ecc7a15e21f4dfedd574608ba3ce947d20c6d3be728d3b90'


def payload():
    proof = json.loads((W / ORIGINAL / 'manifest.safe.json').read_bytes())
    raw = (W / ORIGINAL / 'payload.private.py').read_text()
    if (proof['actualExit'] != 0 or proof['productionSource'] != SOURCE
            or proof['nativePhysicalFiles'] != 64
            or proof['proofHashes']['after.private.json']['sha256'] != AFTER_SHA
            or hashlib.sha256(raw.encode()).hexdigest() != proof['payloadSha256']):
        raise ValueError('exact original stopped/current snapshot and completed verifier required')
    tree = ast.parse(raw); changed = 0
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'save' for t in node.targets):
            if not isinstance(node.value, ast.BinOp) or not isinstance(node.value.right, ast.Constant) or node.value.right.value != ORIGINAL:
                raise ValueError('one exact evidence-only output path')
            node.value.right.value = SLOT; changed += 1
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'result' for t in node.targets):
            for key, value in zip(node.value.keys, node.value.values):
                if isinstance(key, ast.Constant) and key.value == 'run':
                    if value.value != 'PG4658-current-owned-post-v1': raise ValueError('original result label')
                    value.value = 'PG4704-current-preservation-readonly-v1'; changed += 1
    if changed != 2: raise ValueError('only output path and result run are rebound')
    raw = ast.unparse(ast.fix_missing_locations(tree))
    boundary = "with (save / 'result.safe.json').open('x') as f:"
    if raw.count(boundary) != 1: raise ValueError('one final data-only result boundary')
    extra = """
require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active'))
require(not list(pathlib.Path('/run/schubert-nk/startup').glob('*.start.intent')))
require(set(after)=={'backup','configuration','extraDurable','originals','pid1','rows','runtime','startup','unitFilesActual','units'})
require(set(after['runtime'])=={'/run/systemd/system','/run/systemd/system/schubert-nk-morning-controller.service.d'})
canonical=(root/'after.private.json').read_bytes()
require(hashlib.sha256(canonical).hexdigest()==AFTER_SHA)
full=json.dumps({**after,'native':native},sort_keys=True).encode()
for name,body in [('before.private.json',canonical),('sealed-with-native.private.json',full)]:
 with(save/name).open('xb')as handle:
  os.fchmod(handle.fileno(),0o600);handle.write(body);handle.flush();os.fsync(handle.fileno())
fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:os.fsync(fd)
finally:os.close(fd)
result.update(freshCurrentPreservation=True,dataOnlyNotRuntimeAuthority=True,currentOriginalClosedAndNoIntent=True,
 canonicalBeforeFields=10,sealedImageFields=11,privateBeforeSha256=AFTER_SHA,
 sealedWithNativeSha256=hashlib.sha256(full).hexdigest(),guestBeforePath=str(save/'before.private.json'),
 nativeCandidateCredit=False,rawExported=False,runtimeConfigFilesToRetire=0)
"""
    return 'AFTER_SHA=' + repr(AFTER_SHA) + '\n' + raw.replace(boundary, extra + '\n' + boundary)


if __name__ == '__main__': raise SystemExit(execute(SLOT, payload(), 180))
