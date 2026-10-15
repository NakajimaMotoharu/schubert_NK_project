"""One bounded read-only actual Root progress diagnostic, no start/stop or recovery."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
from pg3466_outbox_current_live_binding import SLOT as LIVE

SLOT = 'pg3488-outbox-root-progress-v1'


def main():
    live = json.loads((W / LIVE / 'manifest.safe.json').read_bytes())
    assert live['actualExit'] == 0
    expected = {**live['binding'], 'pid': live['rootPid'], 'ticks': live['rootTicks'],
                'argvSha256': live['rootArgvSha256']}
    raw = 'EXPECTED=' + repr(expected) + '\n' + r'''
import pathlib,hashlib,json,subprocess,datetime
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip().replace('-','')==EXPECTED['boot']
p=pathlib.Path('/proc')/str(EXPECTED['pid']);s=(p/'stat').read_text().rsplit(')',1)[1].split()
assert int(s[19])==EXPECTED['ticks']and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==EXPECTED['argvSha256']
r=subprocess.run(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=InvocationID,MainPID,Job,ExecMainStartTimestampMonotonic'],capture_output=True,text=True,timeout=5);assert r.returncode==0
state=dict(x.split('=',1)for x in r.stdout.splitlines())
assert state=={'InvocationID':EXPECTED['invocation'],'MainPID':str(EXPECTED['pid']),'Job':EXPECTED['job'],'ExecMainStartTimestampMonotonic':str(EXPECTED['start'])}
sql="begin read only;set local statement_timeout='3s';select coalesce(json_agg(json_build_object('step',step,'status',status)order by id),'[]'::json)from schubert.batch_runs where run_id='"+EXPECTED['run']+"';commit;"
r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],capture_output=True,timeout=8);assert r.returncode==0
rows=json.loads(r.stdout);assert len(rows)<=10 and all(set(x)=={'step','status'}for x in rows)
assert all(x['status']in {'RUNNING','SUCCESS','WARNING','FAILED','SKIPPED'}for x in rows)
j=subprocess.run(['journalctl','--no-pager','-u','schubert-nk-morning-controller.service','-n','30','-o','json'],capture_output=True,timeout=10);assert j.returncode==0 and len(j.stdout)<1048576
messages=[json.loads(x).get('MESSAGE','')for x in j.stdout.splitlines()]
assert all(isinstance(x,str)for x in messages)
status=dict(x.split(':',1)for x in(p/'status').read_text().splitlines()if ':'in x)
print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sameIssuedRoot':True,'procState':s[0],'userCpuTicks':int(s[11]),'systemCpuTicks':int(s[12]),'threads':int(status['Threads']),'wchan':(p/'wchan').read_text().strip(),'batchRows':rows,'lastJournalMessageHashes':[hashlib.sha256(x.encode()).hexdigest()for x in messages],'journalKeywordCounts':{k:sum(k in m for m in messages)for k in ['ERROR','FATAL','UNKNOWN','Exception','WARNING','WAITING']},'startsStopsSqlWrites0':True,'formalAccepted':False}))
'''
    os.umask(0o077)
    out = W / SLOT
    out.mkdir()
    (out / 'payload.private.py').write_text(raw)
    with management_gate(P / 'current-management-critical.lock'):
        actual = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), capture_output=True, timeout=40)
    (out / 'stderr.private.log').write_bytes(actual.stderr)
    value = {'actualExit': actual.returncode, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if actual.returncode == 0:
        value['guest'] = json.loads(actual.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value))
    return actual.returncode


if __name__ == '__main__':
    raise SystemExit(main())
