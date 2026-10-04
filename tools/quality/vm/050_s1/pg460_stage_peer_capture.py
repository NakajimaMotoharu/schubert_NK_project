"""Preserve actual external observer bytes, no process/current/permit mutation."""
import hashlib, os, pathlib, subprocess
private = pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
source = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg459-parent-watch-private-v1.jsonl')
expected = '089998999b9d95fc7d093e3bb6d7403f78e22882a3883c8ff0fd3b8c6d9e0e65'
raw = source.read_bytes()
assert hashlib.sha256(raw).hexdigest() == expected
opts = ['-i', str(private/'vm-access'), '-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'UserKnownHostsFile='+str(private/'known_hosts')]
ssh = ['ssh', *opts, '-p', '22222', 'ubuntu@127.0.0.1']
# Root writes one new-only private receipt; all previous captures remain untouched.
script = '''import os,pathlib,hashlib,json,sys
assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg460-parent-known30-private')
s=root.lstat();assert s.st_uid==s.st_gid==0 and s.st_mode==0o40700
raw=sys.stdin.buffer.read();assert hashlib.sha256(raw).hexdigest()==EXPECTED
fd=os.open(root/'external-watch.private.jsonl',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
assert len(hashes)==14
print('PG460_PEER_CAPTURE files=14 captureSetSha256='+hashlib.sha256(json.dumps(dict(sorted(hashes.items())),separators=(',',':'),ensure_ascii=False).encode()).hexdigest()+' previousFilesPreserved=true startStopIssued=false')
'''
# Script is passed as fixed code; observer bytes enter stdin, never command arguments/logs.
import shlex
command='sudo -n python3 -c '+shlex.quote('EXPECTED='+repr(expected)+'\n'+script)
r=subprocess.run(ssh+[command],input=raw,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print(r.stdout.decode(),end='')
if r.returncode:print('PG460_PEER_CAPTURE_REFUSED actual='+str(r.returncode)+' diagnosticsRedacted=true')
raise SystemExit(r.returncode)
