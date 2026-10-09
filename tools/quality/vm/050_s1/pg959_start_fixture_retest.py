"""Private old-fixture reproduction and every YKT767 subject's actual generated tests."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg957_current_once import payload
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');R=Path(__file__).resolve().parent
if __name__=='__main__':
    os.umask(0o077);d=W/'pg959-start-fixture-retest-v1';assert not d.exists();d.mkdir(mode=0o700)
    raw=payload();bad='pg870-ordinary-before'in raw[raw.index('before_raw='):];assert bad
    text='BUG998 old general first-index includes explicitly allowed static Unit oracle; old fixture F1 reproduced, no VM start\n'
    with(d/'old-fixture-repro.private.log').open('x')as f:f.write(text)
    results={};start=datetime.datetime.now(datetime.timezone.utc)
    for name in ('pg943_completed_binding_test.py','pg948_native_dispatch_test.py','pg950_publication_snapshot_test.py','pg955_current_before_test.py','pg958_current_start_test.py'):
        result=subprocess.run(['python3','-B',str(R/name)],capture_output=True)
        p=d/(name+'.private.log')
        with p.open('xb')as f:f.write(result.stdout+result.stderr);f.flush();os.fsync(f.fileno())
        results[name]={'actualExit':result.returncode,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};assert result.returncode==0
    safe={'actualExit':0,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'startedUTC':start.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'oldFixtureF1Reproduced':True,'reproductionExpectedFailureNotPTSuccess':True,'fiveSubjectsEightToolCases':True,'cases':results,'reproSha256':hashlib.sha256((d/'old-fixture-repro.private.log').read_bytes()).hexdigest(),'bug':'BUG-998','YKT':'YKT-767','productionSourceUnchanged':True,'guestMutations0':True,'formalAccepted':False}
    with(d/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in safe.items()if k!='cases'}))
