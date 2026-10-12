"""Read only safe traceback coordinates; Python indentation is not contractual."""
import hashlib
import json
import os
import subprocess
from pg1805_retained_stop_readonly_diagnosis import owner,PAYLOAD,SSH,W

SLOT='pg1806-retained-stop-trace-v1'


def main():
    os.umask(0o077);before=owner();out=W/SLOT;out.mkdir(mode=0o700)
    raw=PAYLOAD.replace("re.fullmatch(r'  File", "re.search(r'File")
    raw=raw.replace("frames=[]","frames=[]\nexceptionTypes=[]\nfor line in log.decode('utf-8').splitlines():\n m=re.search(r'\\b([A-Za-z_]+(?:Error|Exception)):',line)\n if m:exceptionTypes.append(m[1])")
    raw=raw.replace("'frames':frames,","'frames':frames,'exceptionTypes':exceptionTypes,")
    compile(raw,'<safe trace observer>','exec')
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw.encode(),capture_output=True,timeout=20)
    (out/'stderr.private.log').write_bytes(r.stderr)
    if before!=owner():raise ValueError('fixed owner/phase changed')
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'hostRetainedOwner':before,'formalAccepted':False}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True)
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
