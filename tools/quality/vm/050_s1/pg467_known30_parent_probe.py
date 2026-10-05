"""BUG730 actual exit30 exec, same Production df9 bytes, no normal closure/coverage100 inference."""
import hashlib,os,pathlib,subprocess
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SSH=['ssh','-i',str(PRIVATE/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(PRIVATE/'known_hosts'),'ubuntu@127.0.0.1']
os.umask(0o077)
raw=subprocess.check_output(SSH+['sudo -n systemctl show schubert-nk-morning-controller.service --property=InvocationID,MainPID,ControlPID,Job,ExecMainStatus'],text=True);state=dict(line.split('=',1) for line in raw.splitlines())
assert state['InvocationID']=='86fd86f54b464bd29f73a844ee4f1bd3' and state['MainPID']==state['ControlPID']=='0' and not state['Job'] and state['ExecMainStatus']=='30'
target=WORK/'pg467-parent-native-v1.exec'
with target.open('xb') as stream:r=subprocess.run(SSH+['sudo -n cat /run/schubert-nk/pt-coverage/parent/parent.exec'],stdout=stream,stderr=subprocess.DEVNULL)
assert r.returncode==0 and target.stat().st_size>0
repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[]
for pattern in ['org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar']:
    matches=list(repo.glob(pattern));assert len(matches)==1;cp.append(str(matches[0]))
jars=[WORK/'pg465-host'/m/f'schubert-nk-{m}-0.1.0-SNAPSHOT.jar' for m in ['protocol','storage','bootstrap','api','web','batch']];assert all(p.is_file() for p in jars)
script='''import org.jacoco.core.tools.*;import org.jacoco.core.analysis.*;import java.io.*;
var data=new ExecFileLoader();data.load(new File("'''+str(target)+'''"));
var sessions=data.getSessionInfoStore().getInfos();
if(sessions.size()!=1 || sessions.get(0).getStartTimeStamp()<1791172756000L || sessions.get(0).getDumpTimeStamp()>1791173524000L)throw new IllegalStateException("actual PG467 session interval required");
System.out.println("SESSION count="+sessions.size()+" start="+sessions.get(0).getStartTimeStamp()+" dump="+sessions.get(0).getDumpTimeStamp());
var builder=new CoverageBuilder();var analyzer=new Analyzer(data.getExecutionDataStore(),builder);
'''+''.join('analyzer.analyzeAll(new File("'+str(p)+'"));\n' for p in jars)+'''
if(!builder.getNoMatchClasses().isEmpty())throw new IllegalStateException("same frozen byte required");
System.out.println("DIAG mismatch="+builder.getNoMatchClasses().size());
for(var c:builder.getClasses())if(c.getName().endsWith("/MorningCaddyReadiness") || c.getName().endsWith("/MorningStartupLaunchOwner")){
 for(var m:c.getMethods())System.out.println("DIAG "+c.getName()+" "+m.getName()+" L"+m.getLineCounter().getCoveredCount()+"/"+m.getLineCounter().getMissedCount()+" B"+m.getBranchCounter().getCoveredCount()+"/"+m.getBranchCounter().getMissedCount());
 if(c.getName().endsWith("/MorningCaddyReadiness"))for(int n:new int[]{191,210,220,227})System.out.println("COLDPATH "+n+" status="+c.getLine(n).getStatus());
}
/exit
'''
out=WORK/'pg467-parent-diagnostic-v1.private.txt'
with out.open('xb') as stream:r=subprocess.run(['/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/jshell','--class-path',':'.join(cp)],input=script.encode(),stdout=stream,stderr=stream)
text=out.read_text();assert r.returncode==0 and 'DIAG mismatch=0' in text and 'SESSION count=1' in text and 'Exception ' not in text
print('PG467_KNOWN30_PROBE sameSixFrozenSource=true execSha256='+hashlib.sha256(target.read_bytes()).hexdigest()+' privateDiagnosis=true normalCloseClaimed=false fullCoverage=false')
