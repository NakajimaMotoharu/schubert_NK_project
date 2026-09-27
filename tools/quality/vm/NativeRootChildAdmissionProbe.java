import dev.codex.schubert.nk.batch.file.StartupAdmissionFile;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** PT-OPS-NATIVE-015: actual root/samePID/setpriv/2FD admission composition, NOT business gate. */
public final class NativeRootChildAdmissionProbe {
  private static final byte[] PUBLIC = "PUBLIC-ROOT-FD".getBytes(StandardCharsets.US_ASCII);
  public static void main(String[] args) throws Exception {
    if(!Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))throw new AssertionError("isolated fixture required");
    if(args.length==1 && args[0].equals("child")){child();return;}
    if(args.length!=0 || LinuxInodeSecurity.create().effectiveUid()!=0)throw new AssertionError("isolated root required");
    var context=RootStartupContext.create();var captured=context.capture(RootStartupContext.Service.API);
    long uid=id("-u","schubert-api"),gid=id("-g","schubert-api");
    String groups=Arrays.stream(query(List.of("/usr/bin/id","-G","schubert-api")).trim().split(" ")).mapToLong(Long::parseLong).sorted().distinct().mapToObj(Long::toString).collect(java.util.stream.Collectors.joining(","));
    var calls=LinuxDirectoryCalls.create();
    int root=calls.openRoot(),usr=-1,bin=-1,elf=-1;
    try {
      usr=calls.openDirectory(root,"usr");bin=calls.openDirectory(usr,"bin");elf=calls.openEntry(bin,"setpriv");
      calls.close(bin);bin=-1;calls.close(usr);usr=-1;calls.close(root);root=-1;
      final int executable=elf;
      var result=StartupAdmissionFile.create().tryExclusive(a->LinuxSealedProof.create().withProof(PUBLIC,proof->{
        context.recheck(captured);
        LinuxExecDescriptors.create().withInherited(a,proof,()->LinuxProcessExec.create().replace(Path.of("/proc/self/fd/"+executable),List.of("/usr/bin/setpriv","--reuid="+uid,"--regid="+gid,"--groups="+groups,"--bounding-set=-all","--inh-caps=-all","--ambient-caps=-all","--no-new-privs","/usr/bin/java","--enable-native-access=ALL-UNNAMED","-cp","/opt/pgpt-native/classes:/opt/pgpt-native/lib/*","NativeRootChildAdmissionProbe","child"),Map.of("PATH","/usr/bin:/bin","LANG","C","LC_ALL","C","INVOCATION_ID",captured.invocation(),"PGPT_PUBLIC_A",Integer.toString(a),"PGPT_PUBLIC_PROOF",Integer.toString(proof),"PGPT_PUBLIC_PID",Long.toString(captured.pid()),"PGPT_PUBLIC_UID",Long.toString(uid),"PGPT_PUBLIC_GID",Long.toString(gid),"PGPT_PUBLIC_GROUPS",groups)));
        throw new AssertionError("exec returned");
      }));
      throw new AssertionError("root composition returned without exec");
    } finally {if(elf>=0)calls.close(elf);if(bin>=0)calls.close(bin);if(usr>=0)calls.close(usr);if(root>=0)calls.close(root);}
  }
  private static void child() throws Exception {
    var env=System.getenv();if(ProcessHandle.current().pid()!=Long.parseLong(env.get("PGPT_PUBLIC_PID")))throw new AssertionError("PID changed");
    if(LinuxInodeSecurity.create().effectiveUid()!=Long.parseLong(env.get("PGPT_PUBLIC_UID")))throw new AssertionError("UID changed");
    var status=new HashMap<String,String>();for(String line:Files.readAllLines(Path.of("/proc/self/status"))){int i=line.indexOf(':');if(i>0)status.put(line.substring(0,i),line.substring(i+1).trim());}
    for(String key:List.of("CapInh","CapPrm","CapEff","CapBnd","CapAmb"))if(!status.get(key).equals("0000000000000000"))throw new AssertionError("capability remains");
    if(!status.get("NoNewPrivs").equals("1"))throw new AssertionError("no-new-privileges absent");
    String groups=Arrays.stream(status.get("Groups").split("\\s+")).mapToLong(Long::parseLong).sorted().mapToObj(Long::toString).collect(java.util.stream.Collectors.joining(","));
    if(!groups.equals(env.get("PGPT_PUBLIC_GROUPS")))throw new AssertionError("groups differ");
    for(String id:status.get("Gid").split("\\s+"))if(!id.equals(env.get("PGPT_PUBLIC_GID")))throw new AssertionError("gid differs");
    int a=Integer.parseInt(env.get("PGPT_PUBLIC_A")),proof=Integer.parseInt(env.get("PGPT_PUBLIC_PROOF"));
    LinuxStartupAdmission.create().withAdmitted(a,proof,(lease,bytes)->{
      if(!Arrays.equals(PUBLIC,bytes))throw new AssertionError("public oracle differs");
      if(Files.exists(Path.of("/proc/self/fd/"+proof)))throw new AssertionError("proof still open");
      if(!Files.exists(Path.of("/proc/self/fd/"+a)))throw new AssertionError("A closed before ready");
      lease.close();if(Files.exists(Path.of("/proc/self/fd/"+a)))throw new AssertionError("A not released");return 1;
    });
    System.out.println("PT-OPS-NATIVE-015 PASS samePid=true fixedUidGidGroups=true fiveCapsZero=true noNewPrivs=true rootProofAttributesAndSeals=true readonlyA=true proofClosedBeforeCallback=true aReleasedAtReadyBoundary=true fullGate=false");
  }
  private static long id(String option,String account)throws Exception{return Long.parseLong(query(List.of("/usr/bin/id",option,account)).trim());}
  private static String query(List<String> argv)throws Exception{
    var builder=new ProcessBuilder(argv).redirectError(ProcessBuilder.Redirect.DISCARD);builder.environment().clear();builder.environment().put("PATH","/usr/bin:/bin");
    Process p=builder.start();try(var out=p.getInputStream();var in=p.getOutputStream();var err=p.getErrorStream()){if(!p.waitFor(5,java.util.concurrent.TimeUnit.SECONDS)||p.exitValue()!=0)throw new AssertionError("NSS fixture failed");return new String(out.readNBytes(1025),StandardCharsets.US_ASCII);}finally{if(p.isAlive())p.destroy();}
  }
}
