"""Read-only immutable PG462 parent exec capture and same-byte method/line diagnosis."""
import hashlib, os, pathlib, subprocess
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SSH=['ssh','-i',str(PRIVATE/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(PRIVATE/'known_hosts'),'ubuntu@127.0.0.1']
os.umask(0o077)
check=subprocess.check_output(SSH+['sudo -n systemctl show schubert-nk-morning-controller.service --property=InvocationID,MainPID,ControlPID,Job,ExecMainStatus'],text=True)
d=dict(line.split('=',1) for line in check.splitlines())
assert d['InvocationID']=='4105e7a77d3449b1aeff0dcea2f0d5ca' and d['MainPID']==d['ControlPID']=='0' and not d['Job'] and d['ExecMainStatus']=='30'
target=WORK/'pg462-parent-native-v1.exec'
with target.open('xb') as stream:
    r=subprocess.run(SSH+['sudo -n cat /run/schubert-nk/pt-coverage/parent/parent.exec'],stdout=stream,stderr=subprocess.DEVNULL)
assert r.returncode==0 and target.stat().st_size>0
repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository')
cp=[]
for pattern in ['org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar']:
    matches=list(repo.glob(pattern));assert len(matches)==1;cp.append(str(matches[0]))
jars=[WORK/'pg462-host'/m/'target'/f'schubert-nk-{m}-0.1.0-SNAPSHOT.jar' for m in ['batch','bootstrap']]
commands='''import org.jacoco.core.tools.*;
import org.jacoco.core.analysis.*;
import java.io.*;
var data=new ExecFileLoader();
data.load(new File("'''+str(target)+'''"));
var builder=new CoverageBuilder();
var analyzer=new Analyzer(data.getExecutionDataStore(),builder);
'''+''.join('analyzer.analyzeAll(new File("'+str(p)+'"));\n' for p in jars)+'''
System.out.println("DIAG mismatch="+builder.getNoMatchClasses().size());
for(var c:builder.getClasses()) if(c.getName().matches(".*(MorningCaddyReadiness|MorningStartupLaunchOwner|ChildStartupContext|OriginalProof).*")) { for(var m:c.getMethods())System.out.println("DIAG "+c.getName()+" "+m.getName()+" L"+m.getLineCounter().getCoveredCount()+"/"+m.getLineCounter().getMissedCount()+" B"+m.getBranchCounter().getCoveredCount()+"/"+m.getBranchCounter().getMissedCount()); for(int n=c.getFirstLine();n<=c.getLastLine();n++){var l=c.getLine(n); if(l.getInstructionCounter().getTotalCount()>0)System.out.println("LINE "+c.getName()+" "+n+" status="+l.getStatus());}}
/exit
'''
out=WORK/'pg462-parent-diagnostic-v1.txt'
with out.open('xb') as stream:
    r=subprocess.run(['/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/jshell','--class-path',':'.join(cp)],input=commands.encode(),stdout=stream,stderr=stream)
assert r.returncode==0
print('PG462_PARENT_PROBE captured=true sameFrozenBatchBootstrap=true execSha256='+hashlib.sha256(target.read_bytes()).hexdigest()+' diagnosisPrivate=true wholeAccepted=false')
