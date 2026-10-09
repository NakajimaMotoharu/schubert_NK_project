"""Install already-qualified857 artifacts locally, not a new build/coverage gate or PT pass."""
import datetime,hashlib,json,os,shutil,subprocess
from pathlib import Path
from pg911_snapshot_selected_v2 import dependency_bytes
T=Path(__file__).resolve().parents[4];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');M2=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'],cwd=T)==b''
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip();host=W/'pg857-completed-reference-six-host-v1';h=json.loads((host/'manifest.safe.json').read_bytes());assert h['actualExit']==0 and h['candidateSource']=='e01612fcd7f2752df5ae0836b78538fd5e87f120'
 target=W/'pg913-frozen-dependency-cache-v1';target.mkdir(mode=0o700);old=target/'preimage';old.mkdir(mode=0o700);preserved={};inputs={}
 env=dict(os.environ);env['JAVA_HOME']='/home/mini/codex/project1/work/toolchain/jdk-25.0.4';env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH'];start=datetime.datetime.now(datetime.timezone.utc);commands=[];code=0
 for m in ('protocol','storage','bootstrap'):
  name='schubert-nk-'+m;pom='src/'+name+'/pom.xml';assert subprocess.check_output(['git','diff','--name-only',h['candidateSource'],'--',pom],cwd=T)==b''
  jar=host/m/(name+'-0.1.0-SNAPSHOT.jar');assert sha(jar)==h['moduleResults'][m]['jarSha256'];inputs[m]={'jarSha256':sha(jar),'pomSha256':sha(T/pom)}
  cache=M2/'dev/codex/schubert'/name/'0.1.0-SNAPSHOT';preimage=old/m;preimage.mkdir(mode=0o700)
  for p in cache.iterdir():
   if p.is_file():shutil.copyfile(p,preimage/p.name);(preimage/p.name).chmod(0o600);preserved[m+'/'+p.name]=sha(p)
  cmd=['./mvnw','-o','--no-transfer-progress','-Dstyle.color=never','-Dmaven.repo.local='+str(M2),'org.apache.maven.plugins:maven-install-plugin:3.1.2:install-file','-Dfile='+str(jar),'-DpomFile='+str(T/pom),'-DgeneratePom=false'];commands.append(cmd)
  with(target/(m+'.private.log')).open('xb')as f:r=subprocess.run(cmd,cwd=T,env=env,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
  code=r.returncode
  if code:break
 assert head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip();counts=dependency_bytes()if not code else None
 with(target/'exit').open('x')as f:f.write(str(code)+'\n')
 record={'actualExit':code,'source':head,'frozenProductionSource':h['candidateSource'],'frozenHostManifestSha256':sha(host/'manifest.safe.json'),'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'commands':commands,'inputs':inputs,'preimageHashes':preserved,'dependencyClassCounts':counts,'acceptedPTCount':0,'notCoverageOrFormalGate':True,'qualityConfigurationChanged':False,'vmOperations0':True,'logHashes':{p.name:sha(p)for p in target.glob('*.private.log')}}
 with(target/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 print(json.dumps({k:v for k,v in record.items()if k not in('preimageHashes','commands')}));raise SystemExit(code)
if __name__=='__main__':main()
