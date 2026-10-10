"""YKT768 all directly inherited generator tests, independent logs, no VM effects."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent;W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
if __name__=='__main__':
    os.umask(0o077);out=W/'pg974-native-baseline-retest-v1';out.mkdir(mode=0o700);rows=[]
    for name,count in (('pg973_native_baseline_test.py',3),('pg614_binding_test.py',1),('pg644_binding_test.py',1),('pg657_binding_test.py',1),('pg697698_binding_test.py',2),('pg879_binding_test.py',2),('pg891_binding_test.py',3),('pg970_current_native_binding_test.py',2)):
        p=out/(name+'.private.log');start=datetime.datetime.now(datetime.timezone.utc)
        with p.open('xb')as f:r=subprocess.run(['python3','-B',str(R/name)],stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        rows.append({'test':name,'cases':count,'actualExit':r.returncode,'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'sourceSha256':hashlib.sha256((R/name).read_bytes()).hexdigest(),'logSha256':hashlib.sha256(p.read_bytes()).hexdigest()});assert r.returncode==0
    record={'actualExit':0,'cases':15,'tests':rows,'bug':'BUG-999','ykt':'YKT-768','productionPtAdded':0,'formalAccepted':False,'guestMutations0':True}
    with(out/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'cases':15,'manifestSha256':hashlib.sha256((out/'manifest.safe.json').read_bytes()).hexdigest()}))
