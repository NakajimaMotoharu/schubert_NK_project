"""PG1115 receipt-only terminal observation. Never start/stop/extend a Unit.

NK-OPS-001/SS343/353/SSC253; PT-DEP-1117. Full originals/source/DB/native
closure is separate and must not be inferred from this limited receipt.
"""
import ast
import hashlib
import json
import os
import subprocess
from pathlib import Path
from pg1041_cold_policy_diagnostic import W, P

R = Path(__file__).resolve().parent
BINDING = dict(boot='cbca87383b244090b77cbf029677cdd6',
               invocation='21f20c0cdbe34ce99431a55b10f92285', job='36002',
               start=34658346852, run='343a5a1b-d064-47d5-88c2-31c36d7ba7a4',
               cutoff='2026-10-10T12:40:27.396847Z',
               activation='ada3f7ff-8287-48d7-9ba9-5cce71f61bd3')


def payload():
    receipt = (R / 'pg1116_current_receipt.py').read_text()
    receipt = receipt.replace(
        "oracle = Path(__file__).with_name('pg609_parent_receipt.py').read_bytes()",
        'oracle = ORACLE_SOURCE')
    raw = ('ORACLE_SOURCE=' + repr((R / 'pg609_parent_receipt.py').read_bytes())
           + '\nBINDING=' + repr(BINDING) + '\n' + receipt + '\n' + PROBE)
    ast.parse(raw)
    return raw


PROBE = r'''
import hashlib,json,os,stat,subprocess
UNIT='schubert-nk-morning-controller.service'
def metadata(p):
 s=p.stat(follow_symlinks=False)
 return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def read(p):
 a=metadata(p)
 if not stat.S_ISREG(a[4])or a[2:4]!=(0,0)or stat.S_IMODE(a[4])!=0o600 or a[5]!=1:raise ValueError('private original inode refused')
 raw=p.read_bytes()
 if metadata(p)!=a:raise ValueError('original changed during observation')
 return raw,a
def show():
 r=subprocess.check_output(['/usr/bin/systemctl','show',UNIT,'-pActiveState','-pSubState','-pMainPID','-pJob','-pInvocationID','-pResult','-pExecMainCode','-pExecMainStatus','-pExecMainStartTimestampMonotonic','-pExecMainExitTimestampMonotonic'],timeout=5,text=True)
 return dict(row.split('=',1)for row in r.splitlines())
if Path('/proc/sys/kernel/random/boot_id').read_text().strip().replace('-','')!=BINDING['boot']:raise ValueError('current boot refused')
state=show()
if not(state['ActiveState']=='active'and state['SubState']=='exited'and state['MainPID']=='0'and not state['Job']and state['Result']=='success'and state['ExecMainCode']=='1'and state['ExecMainStatus']=='0'and state['InvocationID']==BINDING['invocation']and int(state['ExecMainStartTimestampMonotonic'])==BINDING['start']):raise ValueError('current parent not terminal-success')
base=Path('/var/lib/schubert-nk/maintenance')
expected=('NKACT1\n'+BINDING['run']+'\n'+BINDING['cutoff']+'\n'+BINDING['activation']+'\n').encode('ascii')
active,a=read(base/'active');begin,b=read(base/'attempts'/(BINDING['activation']+'.begin'))
done,c=read(base/'attempts'/(BINDING['activation']+'.done'))
if active!=begin or active!=expected:raise ValueError('actual current original binding refused')
cmd=['/usr/bin/journalctl','--boot='+BINDING['boot'],'_PID=1','UNIT='+UNIT,'INVOCATION_ID='+BINDING['invocation'],'-o','json','--no-pager']
raw=subprocess.check_output(cmd,timeout=10);rows=[json.loads(x)for x in raw.splitlines()]
result=qualify(BINDING,rows,done)
if show()!=state or read(base/'active')!=(active,a)or read(base/'attempts'/(BINDING['activation']+'.begin'))!=(begin,b)or read(base/'attempts'/(BINDING['activation']+'.done'))!=(done,c)or subprocess.check_output(cmd,timeout=10)!=raw:raise ValueError('terminal receipt unstable')
print(json.dumps({'receipt':result,'activeSha256':hashlib.sha256(active).hexdigest(),'doneSha256':hashlib.sha256(done).hexdigest(),'pid1JournalSha256':hashlib.sha256(raw).hexdigest(),'unit':state,'scope':'RECEIPT_ONLY','rawPrinted':False,'wholeAccepted':False}))
'''


def main():
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('fixed clean source required')
    watched = json.loads((W / 'pg1112-parent-watch-v1.private.jsonl').read_bytes().splitlines()[-1])
    if not (watched.get('terminalObserved') and watched.get('parentExit') == '0'
            and watched.get('parentResult') == 'success'):
        raise ValueError('actual current terminal observation required')
    base = W / 'pg1117-current-done-receipt-v1'
    if Path(str(base) + '.safe.json').exists():
        raise ValueError('existing receipt preserved; no repeat')
    os.umask(0o077)
    script = payload().encode()
    ssh = ['ssh', '-i', str(P / 'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile=' + str(P / 'known_hosts'),
           '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    result = subprocess.run(ssh, input=script, capture_output=True, timeout=45)
    with Path(str(base) + '.private.log').open('xb') as f:
        f.write(result.stderr); f.flush(); os.fsync(f.fileno())
    safe = dict(actualExit=result.returncode, scriptSha256=hashlib.sha256(script).hexdigest(),
                logSha256=hashlib.sha256(result.stderr).hexdigest(), formalAccepted=False,
                operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                source='d5b00104280028d9ea81b44c1d1c805f3c2861ed', run='PG1117-current-done-receipt-v1')
    if result.returncode == 0: safe.update(json.loads(result.stdout))
    with Path(str(base) + '.safe.json').open('x') as f:
        json.dump(safe, f, indent=2); f.flush(); os.fsync(f.fileno())
    print(json.dumps(safe)); return result.returncode


if __name__ == '__main__': raise SystemExit(main())
