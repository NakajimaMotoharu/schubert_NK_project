"""Existing NativeCoverage diagnostic over D3 frozen host + this parent's real child exec.
No process start/stop, agent attach, raw exec Git export, exclusions or formal gate claims.
"""
import datetime,hashlib,json,os,pathlib,subprocess,xml.etree.ElementTree as ET
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');T=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private');J=pathlib.Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
SOURCE='d3bba6db6eb9fec13e4847a10541cf337f575731'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 os.umask(0o077)
 assert (W/'pg469-readback-native-v1.exit').read_text().strip()=='0' and (W/'pg469-six-full-v1.source').read_text().strip()==SOURCE
 assert subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml'],cwd=T)==b''
 out=T/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG469-child-native-counter-v1';assert not out.exists()
 ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
 native=[W/'pg469-parent-native-v1.exec']
 for role in ['backup','cleanup','expiry']:
  path=W/('pg469-'+role+'-native-v1.exec');assert not path.exists()
  with path.open('xb') as stream:r=subprocess.run(ssh+['sudo -n cat /run/schubert-nk/pt-coverage/'+role+'/'+role+'.exec'],stdout=stream,stderr=subprocess.DEVNULL,timeout=10)
  assert r.returncode==0 and path.stat().st_size>0;native.append(path)
 repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[]
 for pattern in ['org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar']:
  matches=list(repo.glob(pattern));assert len(matches)==1;cp.append(str(matches[0]))
 target=W/'pg469-native-counter-tools-v1';target.mkdir(mode=0o700)
 r=subprocess.run([str(J/'javac'),'-Xlint:all','-Werror','-cp',':'.join(cp),'-d',str(target),str(T/'tools/quality/vm/050_s1/NativeCoverage.java')],capture_output=True)
 assert r.returncode==0 and not r.stdout and not r.stderr
 validation='import org.jacoco.core.tools.*;\nimport java.io.*;\n'
 for n,path in enumerate(native):
  validation+='var d'+str(n)+'=new ExecFileLoader(); d'+str(n)+'.load(new File("'+str(path)+'"));\n'
  validation+='var s'+str(n)+'=d'+str(n)+'.getSessionInfoStore().getInfos();\n'
  validation+='if(s'+str(n)+'.size()!=1 || s'+str(n)+'.get(0).getStartTimeStamp()<1791218060000L || s'+str(n)+'.get(0).getDumpTimeStamp()>1791219861000L || s'+str(n)+'.get(0).getDumpTimeStamp()<s'+str(n)+'.get(0).getStartTimeStamp())throw new IllegalStateException("fixed current native session");\n'
  validation+='System.out.println("NATIVE_SESSION '+str(n)+' start="+s'+str(n)+'.get(0).getStartTimeStamp()+" dump="+s'+str(n)+'.get(0).getDumpTimeStamp());\n'
 validation+='/exit\n'
 with (W/'pg469-native-session-check-v1.private.log').open('xb') as stream:r=subprocess.run([str(J/'jshell'),'--class-path',':'.join(cp)],input=validation.encode(),stdout=stream,stderr=stream)
 text=(W/'pg469-native-session-check-v1.private.log').read_text();assert r.returncode==0 and 'Exception ' not in text and sum('NATIVE_SESSION '+str(n)+' start=' in text for n in range(4))==4
 modules=['protocol','storage','bootstrap','api','web','batch'];host=[W/'pg469-host'/m/'jacoco.exec' for m in modules]
 result={}
 for module in modules:
  jar=W/'pg469-host'/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
  r=subprocess.run([str(J/'java'),'-cp',str(target)+':'+':'.join(cp),'NativeCoverage',str(jar)]+[str(p) for p in host+native],capture_output=True,timeout=30)
  assert r.returncode==0
  value=json.loads(r.stdout);assert value['classByteMismatch']==0 and not value['formal']
  before={c.attrib['type']:int(c.attrib['missed']) for c in ET.parse(W/'pg469-host'/module/'site/jacoco/jacoco.xml').getroot().findall('counter')}
  result[module]={'fullHostMissed':{k:before[k] for k in ['BRANCH','LINE','METHOD','CLASS']},'sameByteUnionMissed':{k:value[k]['missed'] for k in ['BRANCH','LINE','METHOD','CLASS']}}
  assert all(result[module]['sameByteUnionMissed'][k]<=result[module]['fullHostMissed'][k] for k in result[module]['fullHostMissed'])
 out.mkdir(parents=True)
 manifest={'source':SOURCE,'classification':'PROVISIONAL_COUNTER_NOT_FORMAL','captured':datetime.datetime.now(datetime.timezone.utc).isoformat(),'freshNativeStreams':4,'singleSessionPerStream':True,'startBound':1791218060000,'endBound':1791219861000,'execHashes':{p.name:sha(p) for p in native},'frozenHostExecHashes':{m:sha(p) for m,p in zip(modules,host)},'moduleCounters':result,'rootApiExecBytes':0,'rootApiIncluded':False,'ordinaryWebAgent':False,'sameFrozenClassByteMismatch':0,'formal':False,'coverage100':False,'rawExecExported':False,'collectorSha256':sha(pathlib.Path(__file__)),'existingAnalyzerSha256':sha(T/'tools/quality/vm/050_s1/NativeCoverage.java')}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'sameByteUnionMissed':{m:v['sameByteUnionMissed'] for m,v in result.items()},'manifestSha256':sha(out/'manifest.json'),'formal':False}))
if __name__=='__main__':main()
