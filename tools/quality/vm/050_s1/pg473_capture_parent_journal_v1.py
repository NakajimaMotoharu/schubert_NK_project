"""Fixed current-run manager proof capture, no start/stop/permit/repair.
Only after the external observer terminal normal0; failed/not-run stays failed.
Raw journal remains Root/host private, Git receives hashes and counts only.
"""
import hashlib
import json
import os
import pathlib
import subprocess

os.umask(0o077)
W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
records = [json.loads(l) for l in (W/'pg473-parent-watch-private-v1.jsonl').read_text().splitlines()]
terminal = [r for r in records if r.get('terminalObserved')]
assert len(terminal) == 1
t = terminal[0]
assert t['parentResult'] == 'success' and t['parentExit'] == '0'
assert t['readyObserved'] == t['rootsCaptured'] == ['api', 'web']
assert t['caddyTlsLogin200'] and all(t['backendAlive'].values())
payload = r'''import os,pathlib,subprocess,json,hashlib,stat
os.umask(0o077)
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='e07aa706-1acd-4e65-b309-d7f330f79d54'
assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG473')
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='ffae42347b43d9654d026f66f10cbf81ce9a98baa30bb33510ff19279d90676d'
raw=subprocess.check_output(['/usr/bin/journalctl','--boot=e07aa7061acd4e65b309d7f330f79d54','--since=2026-10-06 00:19:56 UTC','--until=2026-10-06 00:49:57 UTC','UNIT=schubert-nk-morning-controller.service','-o','json','--no-pager'],timeout=10)
assert 0<len(raw)<=4194304
rows=[json.loads(l) for l in raw.splitlines()]
expected={'_BOOT_ID':'e07aa7061acd4e65b309d7f330f79d54','_PID':'1','_UID':'0','_COMM':'systemd','MESSAGE_ID':'39f53479d3a045ac8e11786248231fbf','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'0f1570d2c1cb4d8886d0bb43c96aa07f','JOB_ID':'204144','JOB_TYPE':'start','JOB_RESULT':'done'}
done=[r for r in rows if all(r.get(k)==v for k,v in expected.items())]
assert len(done)==1 and 1791245996000000<=int(done[0]['_SOURCE_REALTIME_TIMESTAMP'])<=1791247797000000
out=pathlib.Path('/var/lib/pgpt-s1-preservation/pg473-completed-journal-v1');assert not out.exists();out.mkdir(mode=0o700)
with (out/'parent.private.jsonl').open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
try:os.fsync(fd)
finally:os.close(fd)
assert stat.S_IMODE((out/'parent.private.jsonl').stat().st_mode)==0o600
os.write(1,raw)
'''
command = ['ssh', '-i', str(P/'vm-access'), '-p', '22222', '-oBatchMode=yes',
           '-oIdentitiesOnly=yes', '-oStrictHostKeyChecking=yes',
           '-oUserKnownHostsFile='+str(P/'known_hosts'), 'ubuntu@127.0.0.1',
           'sudo -n python3 -B -']
r = subprocess.run(command, input=payload.encode(), capture_output=True, timeout=20)
with (W/'pg473-parent-journal-collection-v1.private.log').open('xb') as f:
    f.write(r.stderr)
assert r.returncode == 0
with (W/'pg473-parent-journal-private-v1.jsonl').open('xb') as f:
    f.write(r.stdout); f.flush(); os.fsync(f.fileno())
print('PG473_PARENT_JOURNAL actualExit0=true pid1Done1=true rawInGit=false sha256='+hashlib.sha256(r.stdout).hexdigest())
