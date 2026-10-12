"""Fresh complete current read-only seal before new-source maintenance.

Reuses independent current post oracle, not its old success. No placement,
mount/reload/start/stop, epoch, SQL write or business operation is available.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W, SSH
import pg1613_current_ordinary_stop_independent_post as prior
import pg1257_fresh_independent_terminal_post as seal_contract
from pg1609_current_ordinary_owned_stop_sources import TOOLS, SOURCE


def payload():
    post = json.loads((W / 'pg1613-current-ordinary-terminal-post-v1.safe.json').read_bytes())
    if post.get('actualExit') != 0 or post.get('productionSource') != SOURCE or post.get('allClientAdvisoryFlock0') is not True:
        raise ValueError('independent genuine closed current required')
    seals = {n: post['proofHashes'][n]['sha256'] for n in seal_contract.previous.SEALS}
    raw = prior.payload(seals)
    marker = "result={'actualExit':0"
    if raw.count(marker) != 1:
        raise ValueError('one full independent read-only terminal boundary required')
    raw = raw[:raw.index(marker)] + BODY
    # Embed the exact sealed read-only definitions, so the entire generated
    # payload is statically inspectable rather than hiding names behind exec.
    helper = (Path(__file__).parent / 'vm/050_s1/pg480_backup_refs.py').read_bytes()
    if hashlib.sha256(helper).hexdigest() != '0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7':
        raise ValueError('sealed host read-only definitions required')
    tree = ast.parse(helper)
    names = {'command', 'metadata', 'strict', 'show', 'tree', 'configuration_fields', 'kernel'}
    constants = [n for n in tree.body if isinstance(n, ast.Assign) and all(isinstance(t, ast.Name) and t.id in {'UNITS', 'FIELDS'} for t in n.targets)]
    definitions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    if len(constants) != 2 or len(definitions) != 7:
        raise ValueError('exact sealed helper scope required')
    boundary = "exec(compile(ast.Module(body=constants+nodes,type_ignores=[]),'<sealed terminal metadata>','exec'),globals())"
    if raw.count(boundary) != 1:
        raise ValueError('one sealed dynamic definition boundary required')
    raw = raw.replace(boundary, ast.unparse(ast.Module(body=constants + definitions, type_ignores=[])))
    raw = raw.replace('subprocess,sys,time', 'subprocess')
    receipt = (W / TOOLS / 'pg1609_parent_receipt.py').read_text()
    raw = 'HASHES=' + repr(post['toolHashes']) + '\nRECEIPT=' + repr(receipt) + '\n' + raw
    compile(raw, '<fresh completed current before maintenance>', 'exec')
    return raw


BODY = r'''
require(native==after['native'])
require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1544')
save=base/'pg1639-completed-current-before-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
raw=json.dumps(after,sort_keys=True).encode()
with(save/'before.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
for p in (save,save.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'productionSource':data['source']['commit'],'genuineCompletion':summary,'privateBeforeSha256':hashlib.sha256(raw).hexdigest(),'all24UnchangedTwice':True,'allTenUnitsKernelEmpty':True,'allActorGone':True,'allClientAdvisoryFlock0':True,'whole187SignedArtifactBytesVerified':True,'normalNewMetadataScopes':True,'nativeMetadataStableTwice':True,'allOriginalBackupRuntimePreserved':True,'startsStopsReloadsSqlWrites0':True,'rawExported':False,'formalAccepted':False}))
'''


def main():
    os.umask(0o077)
    require_clean = subprocess.check_output(['git', 'status', '--porcelain'])
    if require_clean:
        raise ValueError('clean operator required')
    out = W / 'pg1639-completed-current-before-v1'
    out.mkdir(mode=0o700)
    raw = payload().encode()
    (out / 'payload.private.py').write_bytes(raw)
    r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-'], input=raw, capture_output=True, timeout=90)
    (out / 'stderr.private.log').write_bytes(r.stderr)
    v = {'actualExit': r.returncode, 'payloadSha256': hashlib.sha256(raw).hexdigest(), 'formalAccepted': False}
    if r.returncode == 0:
        v.update(json.loads(r.stdout))
    with (out / 'manifest.safe.json').open('x') as f:
        json.dump(v, f, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(v))
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
