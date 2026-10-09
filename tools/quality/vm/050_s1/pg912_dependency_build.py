"""Preserved dependency-cache build only; skipped tests are NOT PT acceptance."""
import datetime,hashlib,json,os,shutil,subprocess
from pathlib import Path
from pg911_snapshot_selected_v2 import dependency_bytes
T=Path(__file__).resolve().parents[4];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'],cwd=T)==b''
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip();files=subprocess.check_output(['git','ls-files','src','tools','pom.xml'],cwd=T,text=True).splitlines();pins={p:sha(T/p)for p in files}
 target=W/'pg912-current-dependency-build-v1';target.mkdir(mode=0o700);old=target/'cache-preimage';old.mkdir(mode=0o700)
 repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository/dev/codex/schubert');preserved={}
 for m in ('protocol','storage','bootstrap'):
  root=repo/('schubert-nk-'+m)/'0.1.0-SNAPSHOT';copy=old/m;copy.mkdir(mode=0o700)
  for p in root.iterdir():
   if p.is_file():shutil.copyfile(p,copy/p.name);(copy/p.name).chmod(0o600);preserved[m+'/'+p.name]=sha(p)
 env=dict(os.environ);env['JAVA_HOME']='/home/mini/codex/project1/work/toolchain/jdk-25.0.4';env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
 command=['./mvnw','-o','--no-transfer-progress','-Dstyle.color=never','-Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository','-pl','src/schubert-nk-bootstrap','-am','install','-Dmaven.test.skip=true']
 start=datetime.datetime.now(datetime.timezone.utc)
 with(target/'build.private.log').open('xb')as f:r=subprocess.run(command,cwd=T,env=env,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
 with(target/'exit').open('x')as f:f.write(str(r.returncode)+'\n')
 assert head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()and pins=={p:sha(T/p)for p in files}
 counts=dependency_bytes()if r.returncode==0 else None
 record={'actualExit':r.returncode,'source':head,'productionSource':'e01612fcd7f2752df5ae0836b78538fd5e87f120','command':command,'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'dependencyClassCounts':counts,'classByteMismatch':0 if counts else None,'cachePreimageHashes':preserved,'buildLogSha256':sha(target/'build.private.log'),'acceptedPTCount':0,'skippedTestsAreNotAccepted':True,'formalAccepted':False,'vmOperations0':True}
 with(target/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 print(json.dumps({k:v for k,v in record.items()if k!='cachePreimageHashes'}));raise SystemExit(r.returncode)
if __name__=='__main__':main()
