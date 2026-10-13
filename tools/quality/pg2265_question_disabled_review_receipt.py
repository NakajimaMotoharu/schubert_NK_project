"""Independent Current-negative/candidate-positive receipt; no Production mutation or PT credit."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W
from pg2176_newsource_normal_observer import SOURCE


def main():
    os.umask(0o077);root=Path(__file__).resolve().parents[2];out=W/'pg2265-question-disabled-review-v1';out.mkdir(mode=0o700)
    node=Path('/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node')
    relative='src/schubert-nk-web/src/main/resources/static/js/question-input-validation.js'
    current=root/relative;candidate=Path('/home/mini/codex/project1/work/web-display-deputy-20261011/source')/relative
    test=root/'tools/quality/pg2264_question_submit_disabled_canary.cjs';paths=[current,candidate,test]
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={str(p):sha(p)for p in paths};results=[]
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();commands=[]
    for label,path in [('current',current),('candidate',candidate)]:
        command=[str(node),str(test),str(path)];commands.append(command)
        r=subprocess.run(command,capture_output=True,timeout=15);(out/(label+'.log')).write_bytes(r.stdout+r.stderr);results.append(r.returncode)
    unchanged=before=={str(p):sha(p)for p in paths}
    current_matches=subprocess.check_output(['git','show',SOURCE+':'+relative],cwd=root)==current.read_bytes()
    candidate_matches=subprocess.check_output(['git','show','44aa51e79fdcf8bb154f26a51a40d1d087babc32:'+relative],cwd=root)==candidate.read_bytes()
    value={'actualExit':0 if results==[1,0]and unchanged and current_matches and candidate_matches else 1,'productionSource':SOURCE,'candidateSource':'44aa51e79fdcf8bb154f26a51a40d1d087babc32','operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'currentActualExit':results[0],'candidateActualExit':results[1],'inputHashes':before,'inputsUnchanged':unchanged,'currentSourceMatches':current_matches,'candidateSourceMatches':candidate_matches,'commands':commands,'nodeVersion':'24.19.0','startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bugs':['BUG1222','YKT988'],'failedCurrentNotAccepted':True,'candidateNotIntegrated':True,'productionChanges0':True,'dbVmActions0':True,'coverageAccepted':False,'formalAccepted':False,'actualTokens':None,'actualAllocatedPp':None}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k not in ['inputHashes','commands']}));return value['actualExit']


if __name__=='__main__':raise SystemExit(main())
