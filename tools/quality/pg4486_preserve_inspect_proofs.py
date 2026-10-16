"""Retrieve existing private full proofs; do not reproduce reads or print materials."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W, SSH
from pg4434_current_candidate_admission_read import authenticate_host

FILES = {
 'pg4482-bound-configuration-pair-read-v1/second-pair.private.json':'e1558f41bdf20aa2c85eaf7a821820d4d339b9f1dc0a657f1e4c0b9924c5dbaa',
 'pg4482-bound-configuration-pair-read-v1/second-data.private.json':'cf3a4d1d3cd190600054566609666a99421da7fcbb58bc6423e74da77c8f8211',
 'pg4482-bound-configuration-pair-read-v1/second-config.private.json':'457c2d37338dbee9667efa689840c09fa43003c0e88988dcf9d9d93e281ef015',
 'pg4484-inspect-pair-identity-read-v1/identity.private.json':'62787733f66625dfa2f94e897d6785e21b3dea4bb1cda1747d733ff330b686da'}


def main():
    authenticate_host();os.umask(0o077);out=W/'pg4486-preserved-inspect-proofs-v1';out.mkdir(mode=0o700)
    for path,digest in FILES.items():
        result=subprocess.run(SSH+['sudo','-n','cat','/var/lib/pgpt-s1-preservation/'+path],capture_output=True,timeout=30)
        if result.returncode!=0 or hashlib.sha256(result.stdout).hexdigest()!=digest:raise ValueError('exact saved private proof required')
        with(out/path.split('/')[-1]).open('xb')as f:f.write(result.stdout);f.flush();os.fsync(f.fileno())
    pair=json.loads((out/'second-pair.private.json').read_bytes());data=json.loads((out/'second-data.private.json').read_bytes())
    summary={'actualExit':0,'files':FILES,'dataKeys':sorted(data),'peerKeys':sorted(data['database']['peers'][0]),
        'javaNonJarFds':{k:v['target']for k,v in pair['java']['fds'].items()if not v['target'].endswith('.jar')},'javaFdNumbers':sorted(map(int,pair['java']['fds'])),'operationsIssued':0}
    (out/'manifest.safe.json').write_text(json.dumps(summary,sort_keys=True));print(json.dumps(summary));return 0


if __name__=='__main__':
    raise SystemExit(main())
