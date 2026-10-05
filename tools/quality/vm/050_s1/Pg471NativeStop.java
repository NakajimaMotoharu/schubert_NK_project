import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.util.*;

/** SSC193194195 / PT-OPS-NPARENT195010: completed PG471 same-cohort TERM only.
 * No deployment, start, permit, epoch change, DB update or old UNKNOWN normalization.
 */
public final class Pg471NativeStop {
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg471-native-stop-v1");
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg471-native-tools-v1");
  static String phase="PREFLIGHT";
  static boolean touched;
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed native owned stop refused");}
  static void retain(){
    System.err.println("PG471_NATIVE_STOP_UNKNOWN phase="+phase+" ownershipRetained=true nextOperationIsolated=true");
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException failure){Thread.interrupted();}
  }
  static boolean retainRequired(String at,boolean changed,Throwable failure){
    return changed || Pg471CompletedReadback.retainRequired(at,failure);
  }
  static void save(String name,String value)throws Exception{
    byte[] bytes=value.getBytes(java.nio.charset.StandardCharsets.UTF_8);
    try(var f=java.nio.channels.FileChannel.open(SAVE.resolve(name),Set.of(StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS),
        java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")))){
      var b=java.nio.ByteBuffer.wrap(bytes);while(b.hasRemaining())f.write(b);f.force(true);
    }
    try(var directory=java.nio.channels.FileChannel.open(SAVE,StandardOpenOption.READ)){directory.force(true);}
    require(Arrays.equals(bytes,Files.readAllBytes(SAVE.resolve(name))));
  }
  static void helper(String action)throws Exception{
    Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/python3","-B",TOOLS.resolve("pg471_native_owned_stop.py").toString(),action);
  }
  static void peers()throws Exception{
    Pg471CompletedReadback.peer("schubert-nk-api.service",2265107,"8d6e47b48a58468aaac34643bbeddb16");
    Pg471CompletedReadback.peer("schubert-nk-web.service",2267460,"a0e695e907204a7eaf84ae16013493ad");
    Pg471CompletedReadback.peer("caddy.service",2273164,"d3f960c22ef2455386519d18146139a8");
  }
  public static void main(String[] args)throws Exception{
    require(Arrays.equals(args,new String[]{"stop"}) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals("e07aa706-1acd-4e65-b309-d7f330f79d54"));
    try{require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{var admission=StartupAdmissionFile.create().tryExclusive(owner->Pg387TrustedDeployment.checked(()->{
        phase="BODY";
        Pg387TrustedDeployment.LABEL="PG471";Pg387TrustedDeployment.STEM="pg471";
        Pg387TrustedDeployment.SOURCE=Pg471CompletedReadback.SOURCE;
        Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG471");
        Pg387TrustedDeployment.expectedSchema("027");var approval=Pg387TrustedDeployment.verify();
        require(approval.manifestSha256().equals(Pg471CompletedReadback.DIGEST)
            && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")))
            && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg387TrustedDeployment.RELEASE));
        require(Pg471CompletedReadback.parentAfter(Pg471CompletedReadback.show("schubert-nk-morning-controller.service")));
        int done=0;for(String line:Files.readAllLines(Path.of("/var/lib/pgpt-s1-preservation/pg471-completed-journal-v1/parent.private.jsonl")))
          if(Pg471CompletedReadback.jobDone(com.google.gson.JsonParser.parseString(line).getAsJsonObject()))done++;
        require(done==1);peers();Pg387TrustedDeployment.requireNoUndeliveredWork();
        try{try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"));
            var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()){
          db.setReadOnly(true);db.setAutoCommit(false);schema.setReadOnly(true);schema.setAutoCommit(false);
          try(var q=db.createStatement();var r=q.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")){require(r.next()&&r.getBoolean(1)&&!r.next());}
          var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
          require(epoch.state()==StartupPermitRecords.State.ISSUED);
          var completed=MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()));
          require(completed.completed().orElseThrow().outcome()==MaintenanceCompletion.Outcome.SUCCESS);
          var rows=Pg407FailedRootRecovery.databaseRows(db);require(rows.size()==371);
          var business=Pg456SignedMigration.business(schema);var original=Pg428ColdBootPreparation.original();
          var backup=Pg428ColdBootPreparation.backupSnapshot();var startup=Pg471CompletedDeployment.startupMetadata();
          var names=new HashSet<String>();try(var stream=Files.list(Path.of("/run/schubert-nk/startup"))){stream.forEach(p->names.add(p.getFileName().toString()));}
          require(Pg471CompletedReadback.namespace(names));
          Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
          save("rows-before.private",rows.toString());save("business-before.private",business.toString());
          save("original-before.private",original.toString());save("backup-before.private",backup.toString());save("startup-before.private",startup.toString());
          helper("capture");peers();touched=true;
          Pg471CompletedDeployment.stopOwned(Pg471NativeStop::helper);
          Pg471CompletedDeployment.terminal();
          require(rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema))
              && original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot())
              && startup.equals(Pg471CompletedDeployment.startupMetadata()) && epoch.equals(files.current())
              && completed.equals(MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()))));
          save("body.complete.private","sameSource=true\nallEightOwnedTerminal=true\nrows371=true\npostL01BusinessPreserved=true\noriginalBackupStartupPreserved=true\nstarts0=true\n");
          db.rollback();schema.rollback();phase="DATABASE_SCOPE_CLOSE";
        }}catch(Exception|Error failure){if(retainRequired(phase,touched,failure))retain();throw failure;}
        phase="A_SCOPE_CLOSE";return Boolean.TRUE;
      })).orElseThrow();phase="M_SCOPE_CLOSE";return admission;
      }catch(Exception|Error failure){if(retainRequired(phase,touched,failure))retain();throw failure;}
    })).orElseThrow());}catch(Exception|Error failure){if(retainRequired(phase,touched,failure))retain();throw failure;}
    phase="RETURNED";save("complete.private","allNewScopesReturnedNormally=true\noldUnknownNormalized=false\n");
    System.out.println("PG471_NATIVE_STOP actualNormalReturn=true sameSource=true starts0=true nativeFilesNotYetAccepted=true oldUnknownNormalized=false");
  }
}
