"""New-only observer stage/watch for PG626; exact existing observer logic, no business actions."""
import json
import os
import pathlib
import subprocess
import sys

R = pathlib.Path(__file__).resolve().parent
W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
DEST = '/var/lib/pgpt-s1-preservation/pg627-observer-v1'
SOURCE = '72fb7440697ee1048a5c0145055dc1cc3c577914'
DIGEST = '4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e'


def main():
    os.umask(0o077)
    assert sys.argv[1:] in (['stage'], ['watch'])
    ssh = ['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1']
    if sys.argv[1] == 'stage':
        assert (W/'pg626-prepare-v2.exit').read_bytes()==b'0\n'
        files={name:(R/name).read_bytes()for name in ('pg627_watch_parent.py','pg554_stable_actor.py','pg462_observer_identity.py')}
        payload='FILES='+repr(files)+'\nDEST='+repr(DEST)+'\n'+r'''
import hashlib,json,os,pathlib,subprocess
os.umask(0o077);assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
before=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg626-fresh-parent-v2/before.private.json').read_bytes())
for unit,v in before['units'].items():
 current=dict(l.split('=',1)for l in subprocess.check_output(['systemctl','show',unit,'--property='+','.join(v)],text=True).splitlines());assert current==v
root=pathlib.Path(DEST);assert not os.path.lexists(root);root.mkdir(mode=0o700)
for name,raw in FILES.items():
 with(root/name).open('xb')as f:os.fchmod(f.fileno(),0o400);f.write(raw);f.flush();os.fsync(f.fileno())
for p in (root,root.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'stageExit':0,'starts0':True,'fileHashes':{n:hashlib.sha256(raw).hexdigest()for n,raw in FILES.items()}}))
'''
        with(W/'pg627-stage-v1.private.log').open('xb')as f:
            r=subprocess.run(ssh+['sudo -n python3 -B -'],input=payload.encode(),stdout=f,stderr=f,timeout=30);f.flush();os.fsync(f.fileno())
        with(W/'pg627-stage-v1.exit').open('x')as f:f.write(str(r.returncode)+'\n')
    else:
        assert (W/'pg627-stage-v1.exit').read_bytes()==b'0\n'
        with(W/'pg627-observer-v1.started').open('x')as f:f.write('reserved\n')
        with(W/'pg627-watch-private-v1.jsonl').open('xb')as out, (W/'pg627-observer-v1.private.stderr').open('xb')as err:
            r=subprocess.run(ssh+['sudo -n python3 -B '+DEST+'/pg627_watch_parent.py '+SOURCE+' '+DIGEST+' PG621'],stdout=out,stderr=err)
            out.flush();os.fsync(out.fileno());err.flush();os.fsync(err.fileno())
        with(W/'pg627-observer-v1.exit').open('x')as f:f.write(str(r.returncode)+'\n')
    print(json.dumps({'actualExit':r.returncode,'starts0':True}));raise SystemExit(r.returncode)


if __name__=='__main__':main()
