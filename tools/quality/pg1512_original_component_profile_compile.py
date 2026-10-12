"""Compile new readonly measuring ports and owner against qualified immutable Main769."""
import json
import os
from pathlib import Path
import subprocess
from pg1442_current_cold_compile import ROOT,W,J,write,sha
from pg1512_original_component_profile_sources import java,refs,PROFILE_JAVA,CLASS,TOOLS

def main():
 os.umask(0o077)
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 prior=json.loads((W/'pg1396-frozen-v3.safe.json').read_bytes())
 assert prior['actualExit']==0 and prior['productionSource']=='769ddb15cd735c25fef581b5f9850ef9d0053c0f'
 out=W/TOOLS;out.mkdir(mode=0o700);build=W/'pg1512-original-io-build-v1';build.mkdir(mode=0o700)
 for name,digest in prior['fileHashes'].items():
  p=W/'pg1396-bootstrap-tools-v3'/name;assert sha(p)==digest
  if name.endswith('.class'):write(out/name,p.read_bytes())
 write(out/(CLASS+'.java'),java().encode());write(out/'pg1512_original_component_refs.py',refs().encode())
 helper=build/'Pg1512OriginalIoProfile.java';write(helper,PROFILE_JAVA.encode());classes=build/'classes';classes.mkdir(mode=0o700)
 release=W/'pg1292-release-v1';cp=':'.join(map(str,[out,release/'api/api.jar',release/'operations/batch.jar',release/'api/lib/*',release/'operations/lib/*']))
 repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp+=':'+':'.join(str(repo/x)for x in ['com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar','com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar','com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar'])
 jar=out/'original-io-profile.jar'
 commands=[['python3','-B',str(ROOT/'tools/quality/pg1512_original_component_profile_sources_test.py')],
  [str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(helper)],
  [str(J/'jar'),'--create','--file',str(jar),'-C',str(classes),'.'],
  [str(J/'javac'),'-Xlint:all','-Werror','-cp',cp+':'+str(jar),'-d',str(out),str(out/(CLASS+'.java'))]]
 phases=[]
 for i,command in enumerate(commands):
  log=build/('phase-'+str(i)+'.private.log')
  with log.open('xb')as f:r=subprocess.run(command,cwd=ROOT,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
  phases.append({'command':command,'exit':r.returncode,'logSha256':sha(log)})
  if r.returncode:break
 hashes={p.name:sha(p)for p in out.iterdir()if p.is_file()}
 write(out/'payload-sha256.json',json.dumps(hashes,sort_keys=True).encode())
 for p in out.iterdir():p.chmod(0o400)
 result={'run':'PG1512-original-component-compile-v1','actualExit':phases[-1]['exit'],'operatorSource':head,'productionSource':prior['productionSource'],'phases':phases,'fileHashes':hashes,'helperSourceSha256':sha(helper),'vmActions':0,'formalAccepted':False}
 write(W/'pg1512-original-component-frozen-v1.safe.json',json.dumps(result,sort_keys=True).encode())
 print(json.dumps({k:v for k,v in result.items()if k not in ['phases','fileHashes']}));return result['actualExit']
if __name__=='__main__':raise SystemExit(main())
