"""One immutable host continuation of already-issued Root; never starts/retries a Root."""
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time
from pg1446_current_cold_stage import W
from pg3564_current_browser_resume_sources import SOURCE

SLOT='pg3599-current-browser-finite-chain-v1'
PHASES=[
    ('terminal',['tools/quality/pg3582_current_browser_acceptance.py','terminal']),
    ('rows',['tools/quality/pg3582_current_browser_acceptance.py','rows']),
    ('root-seal',['tools/quality/pg3582_current_browser_acceptance.py','seal']),
    ('browser',['tools/quality/pg3580_current_browser_actual.py']),
    ('composite',['tools/quality/pg3592_current_browser_composite_seal.py']),
    ('parent18',['tools/quality/pg3594_current_browser_parent_projection.py']),
]


def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()


def private(out,name,value):
    with(out/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean immutable continuation required')
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    live=json.loads((W/'pg3576-current-browser-live-binding-v1/manifest.safe.json').read_bytes())
    if live['actualExit']!=0 or live['productionSource']!=SOURCE:raise ValueError('current once-issued Root binding required')
    # Any evidence of a prior dispatch forbids replay, including missing results.
    forbidden=['pg3582-current-browser-terminal-v1','pg3584-current-browser-root-rows-v1','pg3586-current-browser-root-full-seal-v1','pg3580-current-browser-business-actual-v1','pg3592-current-browser-composite-full-seal-v1','pg3594-current-browser-parent-projection-v1.safe.json']
    if any((W/name).exists()for name in forbidden):raise ValueError('existing next-phase evidence requires recovery, no duplicate continuation')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    pid=os.getpid();proc=W.__class__('/proc')/str(pid)
    owner={'pid':pid,'ticks':int((proc/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((proc/'cmdline').read_bytes()).hexdigest()}
    private(out,'begin.safe.json',{'startedUTC':stamp(),'operatorSource':operator,'productionSource':SOURCE,'rootBinding':live['binding'],'owner':owner,'RootStarts0':True,'retries0':True,'formalAccepted':False})
    deadline=time.monotonic()+2000
    while not(W/'pg3572-watch-v1.exit').exists():
        if time.monotonic()>=deadline:raise ValueError('existing observer result unresolved, no operation issued')
        time.sleep(5)
    if(W/'pg3572-watch-v1.exit').read_text()!='0\n':raise ValueError('original observer failure preserved, no downstream inference')
    frames=[json.loads(l)for l in(W/'pg3572-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    if not frames or frames[-1].get('terminalObserved')is not True:raise ValueError('genuine Root terminal observation still required')
    results=[]
    for index,(phase,args)in enumerate(PHASES,1):
        if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()!=operator:raise ValueError('fixed source changed, no next dispatch')
        private(out,f'{index:02d}-{phase}-reserved.safe.json',{'phase':phase,'timeUTC':stamp(),'command':[sys.executable,'-B',*args],'operatorSource':operator,'attempt':1,'retryAllowed':False})
        log=out/f'{index:02d}-{phase}.private.log';start=stamp()
        with log.open('xb')as f:
            r=subprocess.run([sys.executable,'-B',*args],stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
        result={'phase':phase,'actualExit':r.returncode,'startedUTC':start,'completedUTC':stamp(),'logSha256':hashlib.sha256(log.read_bytes()).hexdigest()}
        private(out,f'{index:02d}-{phase}-result.safe.json',result);results.append(result);print(json.dumps(result),flush=True)
        if r.returncode:break
    value={'actualExit':results[-1]['actualExit'],'completedUTC':stamp(),'operatorSource':operator,'productionSource':SOURCE,'phases':results,'throughParent18Only':True,'ownedStopNotIssued':True,'nativeNotQualified':True,'formalAccepted':False}
    private(out,'manifest.safe.json',value);return value['actualExit']


if __name__=='__main__':raise SystemExit(main())
