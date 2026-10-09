"""Immutable deployed2a real Session reproduction, no rewind/new-code expected/VM action."""
import hashlib,json,os,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parent;T=R.parents[3]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');J=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
SOURCE='2a0d5aa392c85a1dc12a1cdb423978e8500895b8'
JAVA=r'''package dev.codex.schubert.nk.batch.file;
import dev.codex.schubert.nk.batch.repository.*;
import java.nio.file.*;import java.time.*;import java.util.*;import java.io.*;
public final class Pg853BeforeFixReference{
 public static void main(String[]args)throws Exception{
  var run=new BatchRun(UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),Instant.parse("2026-09-12T04:05:06.123456Z"));
  var act=new MaintenanceActivation(run,UUID.fromString("fedcba98-7654-3210-8fed-cba987654321"));
  var done=new MaintenanceCompletion(act,Instant.parse("2026-09-12T05:06:07.234567Z"),MaintenanceCompletion.Outcome.SUCCESS);
  try(var f=new MaintenanceRunFilesTest.Fixture(Files.createTempDirectory("pg853-same-session-"))){
   f.files.execute(s->{
    s.start(run,act.id());if(!s.successReferenceRun(act,run.id(),run.cutoff()).equals(run))throw new AssertionError("pending lookup");
    if(!s.complete(done).equals(done))throw new AssertionError("done publication");
    if(!s.observeStartup(act).completed().equals(Optional.of(done))||Files.exists(f.maintenance.resolve("active")))throw new AssertionError("done data proof");
    try{s.successReferenceRun(act,run.id(),run.cutoff());throw new AssertionError("old branch should reproduce failure");}catch(IOException expected){}
    return null;
   });
  }
  System.out.println("RLOOK852001_REPRODUCED sameRealSession=true pendingReadPassed=true completeAndReadbackPassed=true activeAbsent=true doneAfterLookupIo=true oldSource2a=true productionPass0=true");
 }
}
'''
if __name__=='__main__':
 os.umask(0o077);d=W/'pg853-beforefix-reference-v1';d.mkdir(mode=0o700)
 old=W/'pg830-manager-six-host-v1';xml=next((old/'batch').glob('TEST-*.MaintenanceRunFilesTest.xml'))
 properties={p.attrib['name']:p.attrib['value']for p in ET.parse(xml).getroot().find('properties')}
 external=[s for s in properties['java.class.path'].split(':')if '/m2/repository/'in s and s.endswith('.jar')]
 jars=[old/m/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar')for m in ('batch','storage','bootstrap','protocol','api','web')]
 assert all(p.exists()for p in jars)
 raw=subprocess.check_output(['git','show',SOURCE+':src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MaintenanceRunFilesTest.java'])
 for name,data in(('MaintenanceRunFilesTest.java',raw),('Pg853BeforeFixReference.java',JAVA.encode())):
  with(d/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data)
 cp=':'.join([str(d),*[str(p)for p in jars],*external])
 commands=[[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(d),str(d/'MaintenanceRunFilesTest.java'),str(d/'Pg853BeforeFixReference.java')],[str(J/'java'),'--enable-native-access=ALL-UNNAMED','-cp',cp,'dev.codex.schubert.nk.batch.file.Pg853BeforeFixReference']]
 code=0
 with(d/'repro.private.log').open('xb')as log:
  for command in commands:
   r=subprocess.run(command,stdout=log,stderr=log);log.flush();os.fsync(log.fileno());code=r.returncode
   if code:break
 value={'actualExit':code,'productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'kind':'BUG968_BEFORE_FIX_REPRO_NOT_IMPLEMENTATION_PASS','oldTestSourceSha256':hashlib.sha256(raw).hexdigest(),'oldJarSha256':{str(p.relative_to(old)):hashlib.sha256(p.read_bytes()).hexdigest()for p in jars},'commands':commands,'privateLogSha256':hashlib.sha256((d/'repro.private.log').read_bytes()).hexdigest(),'guestActions0':True,'formalAccepted':False}
 with(d/'result.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
 print(json.dumps({k:v for k,v in value.items()if k not in('commands','oldJarSha256')}));raise SystemExit(code)
