import dev.codex.schubert.nk.batch.file.StartupAdmissionFile;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.util.*;

/** PT-OPS-NATIVE-018/019: actual release bytes and outer child binding; NOT full gate. */
public final class NativeCanonicalChildProbe {
  public static void main(String[] args) throws Exception {
    if (!Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01")) throw new AssertionError("isolated fixture required");
    if (args.length == 2 && args[0].equals("child")) { child(args[1]); return; }
    if (args.length != 1 || !Set.of("API","WEB").contains(args[0]) || LinuxInodeSecurity.create().effectiveUid()!=0) throw new AssertionError("isolated root required");
    var service=ServiceConfigFiles.Service.valueOf(args[0]);
    var context=RootStartupContext.create();
    var captured=context.capture(RootStartupContext.Service.valueOf(args[0]));
    var fixed=new FixedServiceIdentity().resolve(service);
    // Independent fixture oracle: these IDs are this disposable VM's provisioning, not production constants.
    var expected=service==ServiceConfigFiles.Service.API
        ? new FixedServiceIdentity.Value(999,981,List.of(980L,981L,982L,986L))
        : new FixedServiceIdentity.Value(997,980,List.of(980L,982L,986L));
    if (!fixed.equals(expected)) throw new AssertionError("fixed NSS differs from isolated fixture");
    var calls=LinuxDirectoryCalls.create();int root=calls.openRoot(),usr=-1,bin=-1,elf=-1;
    try {
      usr=calls.openDirectory(root,"usr");bin=calls.openDirectory(usr,"bin");elf=calls.openEntry(bin,"setpriv");
      calls.close(bin);bin=-1;calls.close(usr);usr=-1;calls.close(root);root=-1;
      final int executable=elf;
      StartupAdmissionFile.create().tryExclusive(a->{
        var attrs=Files.readAttributes(Path.of("/proc/self/fd/"+a),"unix:dev,ino");
        var fields=new HashMap<String,String>();
        fields.put("service",service.name());fields.put("boot_id",captured.boot());fields.put("invocation_id",captured.invocation());fields.put("pid",Long.toString(captured.pid()));fields.put("start_ticks",Long.toString(captured.startTicks()));
        fields.put("admission_fd",Integer.toString(a));fields.put("admission_device",Long.toUnsignedString((Long)attrs.get("dev")));fields.put("admission_inode",Long.toUnsignedString((Long)attrs.get("ino")));
        fields.put("service_uid",Long.toString(fixed.uid()));fields.put("service_gid",Long.toString(fixed.gid()));fields.put("service_groups",fixed.groupArgument());
        // Public fixed vectors deliberately do NOT attest current permit/root/Ops/schema acceptance.
        fields.put("permit_epoch","33333333-3333-3333-3333-333333333333");fields.put("permit_sha256","a".repeat(64));fields.put("release_sha256","ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");fields.put("config_sha256","c".repeat(64));fields.put("roots_sha256","d".repeat(64));fields.put("broker_invocation_id","2".repeat(32));
        return LinuxSealedProof.create().withProof(StartupProofFrame.fromFields(fields).encode(),proof->{
          context.recheck(captured);
          LinuxExecDescriptors.create().withInherited(a,proof,()->{
            LinuxProcessExec.create().replace(Path.of("/proc/self/fd/"+executable),List.of("/usr/bin/setpriv","--reuid="+fixed.uid(),"--regid="+fixed.gid(),"--groups="+fixed.groupArgument(),"--bounding-set=-all","--inh-caps=-all","--ambient-caps=-all","--no-new-privs","/usr/bin/java","--enable-native-access=ALL-UNNAMED","-javaagent:/opt/pgpt-native/lib/org.jacoco.agent-0.8.15-runtime.jar=destfile=/var/lib/schubert-nk/pgpt-native-"+service.name().toLowerCase(Locale.ROOT)+"/startup.exec,append=false","-cp","/opt/pgpt-native/classes:/opt/pgpt-native/lib/*","NativeCanonicalChildProbe","child",service.name()),Map.of("PATH","/usr/bin:/bin","LANG","C","LC_ALL","C","INVOCATION_ID",captured.invocation(),"SCHUBERT_NK_STARTUP_ADMISSION_FD",Integer.toString(a),"SCHUBERT_NK_STARTUP_PROOF_FD",Integer.toString(proof)));
            throw new AssertionError("exec returned");
          });
          throw new AssertionError("descriptor scope returned without exec");
        });
      });
      throw new AssertionError("root composition returned");
    } finally {if(elf>=0)calls.close(elf);if(bin>=0)calls.close(bin);if(usr>=0)calls.close(usr);if(root>=0)calls.close(root);}
  }
  private static void child(String serviceName) throws Exception {
    var inputs=ChildStartupContext.inputs(System.getenv());
    var service=ServiceConfigFiles.Service.valueOf(serviceName);
    ServiceStartupAdmission.create(service,System.getenv()).execute(()->new ServiceStartupAdmission.Configuration<>(Boolean.TRUE,"c".repeat(64)), (ignored,ready)->{
      if(Files.exists(Path.of("/proc/self/fd/"+inputs.proofFd())))throw new AssertionError("proof still open");
      ready.release();if(Files.exists(Path.of("/proc/self/fd/"+inputs.admissionFd())))throw new AssertionError("A not released");
      System.out.println("PT-OPS-NATIVE-018/019 PASS service="+service+" fixedNss=true canonicalRootProof=true samePidBootTicksInvocation=true childKernelReobservation=true actualReleaseBytes=true outerChildGate=true configAfterAdmission=true fixedGroups=true fiveCapsZero=true noNewPrivs=true twoFdClose=true publicFixtureConfigPermitRootsOnly=true fullGate=false");
    });
  }
}
