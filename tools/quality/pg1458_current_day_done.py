"""Current captured generation PID1/DONE receipt only, no start/stop or GC success inference."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pg1454_current_day_observer import R
from pg1450_current_cold_retry import W
from pg1446_current_cold_stage import SSH
from pg1194_completed_resume_receipt_v2 import payload as original


def compose(binding):
    keys={'boot','invocation','job','start','run','cutoff','activation'}
    if type(binding)is not dict or set(binding)!=keys or type(binding['start'])is not int or binding['start']<=0:raise ValueError('actual binding required')
    if any(type(binding[k])is not str or not binding[k]for k in keys-{'start'}):raise ValueError('all actual fields required')
    if binding['boot']!='3d69f5af6bac46b1a5407591c4a79a0d':raise ValueError('current boot required')
    cut=datetime.datetime.fromisoformat(binding['cutoff'].replace('Z','+00:00'))
    if cut.tzinfo is None:raise ValueError('aware actual cutoff required')
    lower=cut-datetime.timedelta(seconds=5)
    tree=ast.parse(original());counts={'BINDING':0,'CURRENT':0,'lower':0}
    for n in ast.walk(tree):
        if not isinstance(n,ast.Assign)or len(n.targets)!=1 or not isinstance(n.targets[0],ast.Name):continue
        name=n.targets[0].id
        if name=='BINDING':n.value=ast.parse(repr(binding),mode='eval').body;counts[name]+=1
        elif name=='CURRENT':n.value=ast.parse(repr({k:binding[k]for k in ['boot','invocation','job','start']}),mode='eval').body;counts[name]+=1
        elif name=='lower':
            n.value=ast.parse('datetime.datetime('+','.join(str(v)for v in [lower.year,lower.month,lower.day,lower.hour,lower.minute,lower.second])+',tzinfo=datetime.timezone.utc)',mode='eval').body;counts[name]+=1
    if counts!={'BINDING':1,'CURRENT':1,'lower':1}:raise ValueError('exact receipt closure required')
    raw=ast.unparse(ast.fix_missing_locations(tree)).replace('pg1194-completed-resume-receipt-v2','pg1458-current-day-done-v1')
    compile(raw,'<actual current-day receipt>','exec');return raw


def payload():
    live=json.loads((W/'pg1457-current-day-live-binding-v1/manifest.safe.json').read_bytes())
    assert live['actualExit']==0 and live['productionSource']=='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
    return compose(live['binding'])


def main():
    assert not subprocess.check_output(['git','status','--porcelain'])
    watch=W/'pg1454-parent-watch-v1.private.jsonl'
    with watch.open('rb')as f:f.seek(max(0,watch.stat().st_size-65536));last=json.loads(f.read().splitlines()[-1])
    assert last.get('terminalObserved')and last.get('parentExit')=='0'and last.get('parentResult')=='success'
    os.umask(0o077);out=W/'pg1458-current-day-done-v1';out.mkdir(mode=0o700)
    raw=payload().encode()
    with(out/'payload.private.py').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=45)
    with(out/'observer.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','formalAccepted':False,'scope':'RECEIPT_ONLY'}
    if r.returncode==0:result.update(json.loads(r.stdout))
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result,sort_keys=True));return r.returncode


if __name__=='__main__':raise SystemExit(main())
