"""Necessary new-source full six after SSC269; preserve all failed selected campaigns."""
import hashlib
import json
import os
import subprocess
import pg1476_corrected_server_six as prior

PRODUCTION='f8770ff083954664b299ba82a9fcd2ae92fbc391'

def server_source(head,archive_sha):
 raw=prior.server_source(head,archive_sha).replace('PG1476','PG1528').replace('3578','3582').replace('523','524').replace('1635','1637').replace('769ddb15cd735c25fef581b5f9850ef9d0053c0f',PRODUCTION)
 compile(raw,'<new production filesystem necessary full six>','exec');return raw

def main():
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=prior.ROOT)
 os.umask(0o077);out=prior.W/'pg1528-server-six-v1';out.mkdir(mode=0o700)
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=prior.ROOT,text=True).strip();archive=out/'source.tar'
 with archive.open('xb')as f:subprocess.run(['git','archive',head,'src','pom.xml','mvnw','.mvn','program/characterization'],cwd=prior.ROOT,stdout=f,check=True);f.flush();os.fsync(f.fileno())
 raw=server_source(head,hashlib.sha256(archive.read_bytes()).hexdigest());helper=out/'pg1528_server_six.py';helper.write_text(raw)
 files=[(archive,prior.REMOTE+'/transfer/PG1528-source.tar'),(helper,prior.REMOTE+'/tools/pg1528_server_six.py')];hashes={dest:hashlib.sha256(p.read_bytes()).hexdigest()for p,dest in files}
 code,status=prior.run('test ! -e '+prior.REMOTE+'/source-full-PG1528 && test ! -e '+prior.REMOTE+'/runs/PG1528-six-v1 && '+' && '.join('test ! -e '+d for _,d in files));assert code==0
 for p,d in files:code,status=prior.copy(str(p),d,timeout=300);assert code==0
 code,status=prior.run('sha256sum '+' '.join(hashes));assert code==0 and all(h in status for h in hashes.values())
 with(out/'begin.safe.json').open('x')as f:json.dump({'snapshot':head,'productionSource':PRODUCTION,'transferHashes':hashes,'expectedTests':3582,'expectedSuites':524,'expectedClasses':1637,'expectedCountBasis':'3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained','trigger':'SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved','workers':1,'formalAccepted':False,'vmMutation0':True},f,sort_keys=True);f.flush();os.fsync(f.fileno())
 code,status=prior.run('mkdir -m700 '+prior.REMOTE+'/source-full-PG1528 && tar -xf '+prior.REMOTE+'/transfer/PG1528-source.tar -C '+prior.REMOTE+'/source-full-PG1528',timeout=120);assert code==0
 code,status=prior.run('python3 -B '+prior.REMOTE+'/tools/pg1528_server_six.py',timeout=3600)
 (out/'observer.private.log').write_text(status)
 v={'run':'PG1528-server-six-v1','actualExit':code,'snapshot':head,'productionSource':PRODUCTION,'formalAccepted':False,'xmlSourceQualificationPending':True}
 with(out/'manifest.safe.json').open('x')as f:json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 print(json.dumps(v));return code
if __name__=='__main__':raise SystemExit(main())
