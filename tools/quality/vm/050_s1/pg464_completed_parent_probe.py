"""PG464 v2: read immutable capture, prove normal return, never claim full coverage."""
import hashlib, json, os, pathlib, subprocess
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
PRIVATE=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SSH=['ssh','-i',str(PRIVATE/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(PRIVATE/'known_hosts'),'ubuntu@127.0.0.1']
journal=[json.loads(l) for l in (WORK/'pg464-parent-journal-private-v2.jsonl').read_text().splitlines()]
done=[r for r in journal if r.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf' and r.get('INVOCATION_ID')=='cc0ac086826446ba928afe79561b0898' and r.get('JOB_ID')=='114896' and r.get('JOB_RESULT')=='done']
assert len(done)==1 and 'newReadOnlyMAAndDatabaseScopesReturnedNormally=true' in (WORK/'pg464-completed-native-v7.log').read_text()
os.umask(0o077)
target=WORK/'pg464-parent-native-v1.exec'
assert hashlib.sha256(target.read_bytes()).hexdigest()=='463b116f46f92dd9a7507af58d0647ef5ea8333fc22314796e55979d4ee5dc68'
repo=pathlib.Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[]
for pattern in ['org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar']:
    matches=list(repo.glob(pattern));assert len(matches)==1;cp.append(str(matches[0]))
jars=[WORK/'pg464-host'/m/'target'/f'schubert-nk-{m}-0.1.0-SNAPSHOT.jar' for m in ['protocol','storage','bootstrap','api','web','batch']]
commands='''import org.jacoco.core.tools.*;
import org.jacoco.core.analysis.*;
import java.io.*;
var data=new ExecFileLoader();
data.load(new File("'''+str(target)+'''"));
var sessions=data.getSessionInfoStore().getInfos();
if(sessions.size()!=1 || sessions.get(0).getStartTimeStamp()<1791159830000L || sessions.get(0).getDumpTimeStamp()>1791160959000L)throw new IllegalStateException("single actual PG464 session required");
System.out.println("SESSION count="+sessions.size()+" start="+sessions.get(0).getStartTimeStamp()+" dump="+sessions.get(0).getDumpTimeStamp());
var builder=new CoverageBuilder();
var analyzer=new Analyzer(data.getExecutionDataStore(),builder);
'''+''.join('analyzer.analyzeAll(new File("'+str(p)+'"));\n' for p in jars)+'''
if(!builder.getNoMatchClasses().isEmpty())throw new IllegalStateException("same frozen byte required");
System.out.println("DIAG mismatch="+builder.getNoMatchClasses().size());
for(var c:builder.getClasses())if(c.getName().matches(".*(MorningProcessMain|MorningStartupLaunchOwner|MorningCompletionEvidence|MorningNewRunAdmission.*|MorningBackupUnitCycle|BackupUnitReceiptGate|MaintenanceFileLock|StartupAdmissionFile|ResourceScope)")) {
 for(var m:c.getMethods())System.out.println("DIAG "+c.getName()+" "+m.getName()+" L"+m.getLineCounter().getCoveredCount()+"/"+m.getLineCounter().getMissedCount()+" B"+m.getBranchCounter().getCoveredCount()+"/"+m.getBranchCounter().getMissedCount());
 if(c.getName().endsWith("/MorningProcessMain"))for(int n:new int[]{47,540,542,543})System.out.println("EXITPATH "+n+" status="+c.getLine(n).getStatus());
}
/exit
'''
out=WORK/'pg464-parent-diagnostic-v2.txt'
with out.open('xb') as stream:r=subprocess.run(['/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/jshell','--class-path',':'.join(cp)],input=commands.encode(),stdout=stream,stderr=stream)
assert r.returncode==0
text=out.read_text()
assert 'DIAG mismatch=0' in text and 'SESSION count=1' in text and 'Exception ' not in text
# BUG-712: 542 is the normal return; 543 is catch IOException, not a success path.
# System.exit at 47 cannot complete a probe after the non-returning call.
# Partial native coverage remains visible and is NOT a 451 coverage exemption.
assert all(f'EXITPATH {n} status=2' in text for n in [540,542])
assert all(f'EXITPATH {n} status=1' in text for n in [47,543])
print(json.dumps({'execSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'singleActualSession':True,'sameFrozenSixModuleBytes':True,'normalCompletedExitPath':True,'partialNativeLines':[47,543],'formal':False,'coverageQualified':False}))
