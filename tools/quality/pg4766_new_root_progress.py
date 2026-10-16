"""Single readonly current-generation progress, only role names/counters no argv or logs."""
import json
from pyflakes.api import check
import pg4752_new_current_admission_image as admission

SLOT='pg4766-new-root-progress-v1'


def payload():
    observed=admission.live()
    proof=json.loads((admission.W/admission.LIVE/'manifest.safe.json').read_bytes())['result']
    raw='EXPECTED='+repr(observed)+'\nARGV_SHA='+repr(proof['rootArgvSha256'])+'\nSOURCE='+repr(admission.SOURCE)+'\nBOM='+repr(admission.BOM)+'\n'+r'''
import hashlib,json,pathlib,subprocess,time
def require(v):
 if not v:raise ValueError('same current Root only')
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip().replace('-','')==EXPECTED['boot'])
manifest=(pathlib.Path('/opt/schubert-nk/current')/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==BOM and json.loads(manifest)['source']['commit']==SOURCE)
fields=['MainPID','InvocationID','Job','ActiveState','SubState','ExecMainStatus','ExecMainStartTimestampMonotonic']
r=subprocess.run(['systemctl','show','schubert-nk-morning-controller.service','--property='+','.join(fields)],capture_output=True,text=True,timeout=10);require(r.returncode==0)
unit=dict(s.split('=',1)for s in r.stdout.splitlines());require(unit['InvocationID']==EXPECTED['invocation']and int(unit['ExecMainStartTimestampMonotonic'])==EXPECTED['start'])
require(int(unit['MainPID'])==EXPECTED['rootPid']and unit['Job']==EXPECTED['job'])
parent=pathlib.Path('/proc')/unit['MainPID'];require(hashlib.sha256((parent/'cmdline').read_bytes()).hexdigest()==ARGV_SHA)
pending=[int(unit['MainPID'])];seen=set();roles={};cpuTicks=0
while pending:
 pid=pending.pop();require(pid not in seen);seen.add(pid);require(len(seen)<=200)
 p=pathlib.Path('/proc')/str(pid)
 try:
  values=(p/'stat').read_text().rsplit(')',1)[1].split();comm=(p/'comm').read_text().strip()
  if pid==EXPECTED['rootPid']:require(int(values[19])==EXPECTED['start']//10000)
  role=comm if comm in {'java','pg_dump','pg_restore','gzip','tar','sudo','python3','python3.14','systemctl','sh','bash','psql'}else'OTHER'
  roles[role]=roles.get(role,0)+1;cpuTicks+=int(values[11])+int(values[12])
  pending.extend(map(int,(p/'task'/str(pid)/'children').read_text().split()))
 except FileNotFoundError:continue
elapsed=time.monotonic()-EXPECTED['start']/1000000
require(elapsed>=0)
print(json.dumps({'actualExit':0,'sameRootGeneration':True,'unit':unit,'elapsedSeconds':elapsed,'originalBudgetSeconds':1800,'rootDescendantCount':len(seen),'processRoleCounts':roles,'aggregateCpuTicks':cpuTicks,'source':SOURCE,'argvExported':False,'startsStopsSqlWrites':0,'formalAccepted':False}))
'''
    if check(raw,'<single current Root progress>'):raise ValueError('complete progress namespace')
    compile(raw,'<current-generation readonly progress>','exec');return raw


if __name__=='__main__':raise SystemExit(admission.execute(SLOT,payload(),45))
