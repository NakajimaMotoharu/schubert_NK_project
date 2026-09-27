import dev.codex.schubert.nk.batch.file.BackupWorkerRequestFiles;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.time.Instant;
import java.util.*;

/** NATIVE025: actual Production worker + fixed Unit/request; not root M/A/full backup admission. */
public final class NativeBackupWorkerProbe {
  private static final UUID RUN=UUID.fromString("30900000-2222-4333-8444-555555555555");
  private static final Instant START=Instant.parse("2026-09-27T15:30:00Z");
  private static final Path ROOT=Path.of("/run/schubert-nk/backup-request");
  private static final Path BEFORE=Path.of("/run/pgpt-backup-309-before");
  public static void main(String[] args)throws Exception {
    var security=LinuxInodeSecurity.create();
    if(args.length!=1||security.effectiveUid()!=0||!Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))throw new AssertionError("isolated root VM only");
    var probe=InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.BACKUP);
    var request=new BackupWorkerRequest(RUN,START);
    if(args[0].equals("prepare")){
      var before=probe.read();
      if(!before.quiescent())throw new AssertionError("unit not idle");
      if(before.invocationId().isEmpty()) {
        // Cold inactive Unit can be GC'ed between show and GetUnitProcesses. A query failure is
        // NOT empty. This VM-only root fixture independently observes the fixed kernel absence.
        rootKernelAbsent();
        if(!before.matches(probe.read()))throw new AssertionError("cold Unit changed");
      }else probe.quiescent().orElseThrow();
      Files.writeString(BEFORE,before.invocationId().map(UUID::toString).orElse("none")+"\n",StandardCharsets.US_ASCII,StandardOpenOption.CREATE_NEW);
      Files.setPosixFilePermissions(BEFORE,PosixFilePermissions.fromString("rw-------"));
      Files.createDirectory(ROOT,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
      try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),ROOT)){
        var files=new BackupWorkerRequestFiles(root,security);files.prepare(request,UUID.randomUUID());
        if(!files.read().equals(request))throw new AssertionError("request readback");
      }
      System.out.println("PT-OPS-NATIVE-025 prepared=true actualRootPublisher=true previousUnitTerminal=true fullParentGate=false");
    }else if(args[0].equals("complete")){
      String text=Files.readString(BEFORE).trim();Optional<UUID> previous=text.equals("none")?Optional.empty():Optional.of(UUID.fromString(text));
      if(probe.completionAfter(previous).orElseThrow()!=0)throw new AssertionError("fresh success required");
      Path output=Path.of("/srv/schubert-nk/backup/20260928-003000-30900000-2222-4333-8444-555555555555.part/schubert_nk.dump");
      if(Files.size(output)<=0||!Files.getPosixFilePermissions(output).equals(PosixFilePermissions.fromString("rw-------")))throw new AssertionError("positive private dump required");
      try(var material=Files.list(Path.of("/run/schubert-nk-backup"))){
        if(material.anyMatch(p->!p.getFileName().toString().equals("worker.exec")))throw new AssertionError("copy not retired");
      }
      System.out.println("PT-OPS-NATIVE-025 PASS actualProductionMain=true fixedUnit=true fixedNssKernel=true actualDumpAndList=true copyRetired=true freshReceiptZero=true allUnitProcessesEmpty=true fullBackup=false fullParentGate=false fullBusinessGate=false");
    }else if(args[0].equals("retire")){
      var stopped=probe.read();if(!stopped.quiescent())throw new AssertionError("stop not terminal");
      rootKernelAbsent();if(!stopped.matches(probe.read()))throw new AssertionError("stopped Unit changed");
      try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),ROOT)){new BackupWorkerRequestFiles(root,security).retire(request);}
      if(Files.exists(ROOT.resolve("backup-request")))throw new AssertionError("original request remains");
      System.out.println("PT-OPS-NATIVE-025 stoppedAllTerminal=true originalRequestRetired=true fullParentGate=false");
    }else throw new IllegalArgumentException("fixed action only");
  }
  private static void rootKernelAbsent()throws Exception {
    Path kernel=Path.of("/sys/fs/cgroup/system.slice/schubert-nk-backup.service");
    if(!Files.getFileStore(Path.of("/sys/fs/cgroup")).type().equals("cgroup2"))throw new AssertionError("kernel cgroup2 required");
    try{Files.readAttributes(kernel,"unix:mode,uid",LinkOption.NOFOLLOW_LINKS);throw new AssertionError("fixed cgroup present");}catch(NoSuchFileException expected){/* exact absence, not general IO */}
  }
}
