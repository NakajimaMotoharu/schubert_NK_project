import dev.codex.schubert.nk.batch.file.*;
import java.nio.file.*;
import java.util.*;
/** SSC191/196 separate new-owner acceptance; no deployment replay or old-close normalization. */
public final class Pg477CompletedAcceptance {
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg477-completed-acceptance");
  static String phase="PREFLIGHT";
  static void require(boolean value){if(!value)throw new IllegalStateException("completed acceptance refused");}
  static boolean arguments(String[] args){return args!=null && args.length==1 && "verify".equals(args[0]);}
  static void retain(){System.err.println("PG477_COMPLETED_UNKNOWN phase="+phase+" nextStartIsolated=true");for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}}
  public static void main(String[] args)throws Exception {
    require(arguments(args) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(Pg477StoppedDeployment.BOOT));
    try{require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{var result=StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
        try{
          phase="REFERENCE_SCOPE_CLOSE";var refs=new Pg477CompletedReferences(TOOLS,"verify");
          phase="READ_ONLY_BODY";
          try {
            try(var db=Pg407FailedRootRecovery.openDatabase()){
              db.setReadOnly(true);db.setAutoCommit(false);
              try(var q=db.createStatement();var v=q.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")){require(v.next() && v.getBoolean(1) && !v.next());}
              var before=Pg477PartialReadback.values();require(before.equals(Pg477PartialReadback.values()));refs.check();
              Path log=TOOLS.resolve("native-acceptance.private.log");
              Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
              phase="NATIVE_HELPER_SCOPE_CLOSE";
              var helper=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg477_completed_native.py").toString(),"after").redirectErrorStream(true).redirectOutput(log.toFile()).start();
              try(var pipe=helper.getOutputStream()){pipe.flush();}
              if(!helper.waitFor(60,java.util.concurrent.TimeUnit.SECONDS))retain();
              helper.getInputStream().close();helper.getErrorStream().close();
              phase="NATIVE_READBACK";require(helper.exitValue()==0);
              require(Files.readString(log).equals("PG477_STOPPED_NATIVE action=after sameSavedCohort=true allNineKernelEmpty=true ordinary143IsStopData=true currentMatched=true starts0=true stops0=true\n"));
              require(before.equals(Pg477PartialReadback.values()));db.rollback();phase="DATABASE_SCOPE_CLOSE";
            }
          }catch(Exception|Error failure){
            if(Pg477StoppedDeployment.retainRequired(phase,false,failure))retain();
            String failed=phase;phase="REFERENCE_SCOPE_CLOSE";refs.release();phase=failed;throw failure;
          }
          phase="REFERENCE_SCOPE_CLOSE";refs.check();refs.release();phase="A_SCOPE_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){if(Pg477StoppedDeployment.retainRequired(phase,false,failure))retain();throw failure;}
      })).orElseThrow();phase="M_SCOPE_CLOSE";return result;
      }catch(Exception|Error failure){if(Pg477StoppedDeployment.retainRequired(phase,false,failure))retain();throw failure;}
    })).orElseThrow());}catch(Exception|Error failure){if(Pg477StoppedDeployment.retainRequired(phase,false,failure))retain();throw failure;}
    Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
    Files.writeString(SAVE.resolve("complete.private"),"allNewScopesReturnedNormally=true\npartialDeploymentAcceptedSeparately=true\noldCloseUnknown=true\nstarts0=true\ndeployReplay0=true\npermits0=true\nddl0=true\n",StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(SAVE.resolve("complete.private"),java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var f=java.nio.channels.FileChannel.open(SAVE.resolve("complete.private"),StandardOpenOption.READ)){f.force(true);}
    Pg387TrustedDeployment.sync(SAVE);Pg387TrustedDeployment.sync(SAVE.getParent());
    System.out.println("PG477_COMPLETED_ACCEPTED allNewScopesReturnedNormally=true partialDeploymentAcceptedSeparately=true oldCloseNotInferred=true starts0=true deployReplay0=true");
  }
}
