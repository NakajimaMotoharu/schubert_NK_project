import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/** PG315 / SSC097 / NATIVE028. Read-only private-fixture candidate validation, NOT approval issuance.
 * Fixed fixture pin is independent of candidate; this probe never mutates current/permit/DB/run.
 * No RootReleaseAdmission/Production activation/R2/R3 acceptance claim.
 */
public final class NativeCandidateReleaseProbe {
  public static void main(String[] args)throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((thread,failure)->
        System.err.println("PT-OPS-NATIVE-028 REFUSED diagnosticsRedacted=true"));
    if(args.length!=0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim()
        .equals("pgpt-r2-20260927-01"))throw new AssertionError("isolated fixture only");
    var context=RootStartupContext.create();
    var expected=context.capture(RootStartupContext.Service.MORNING);
    System.out.println("PT-OPS-NATIVE-028 STAGE rootAuthenticated=true");
    Path candidate=Path.of("/opt/schubert-nk/releases/0.1.0-PG316");
    Path current=Path.of("/opt/schubert-nk/current");
    Path old=Files.readSymbolicLink(current);
    MessageDigest sha256=MessageDigest.getInstance("SHA-256");
    var result=MaintenanceFileLock.create().tryExclusive(()->{
      context.recheck(expected);
      return StartupAdmissionFile.create().tryExclusive(reserved->{
        context.recheck(expected);
        System.out.println("PT-OPS-NATIVE-028 STAGE actualM=true actualA=true");
        byte[] key=fixedMaterial(Path.of("/etc/schubert-nk/pgpt-release-validation/pin.der"),44);
        byte[] signature=fixedMaterial(Path.of("/etc/schubert-nk/pgpt-release-validation/manifest316.sig"),64);
        byte[] original=Files.readAllBytes(candidate.resolve("RELEASE-MANIFEST.json"));
        if(original.length==0 || original.length>1_048_576)throw new AssertionError("manifest bounds");
        new ReleaseSignatureVerifier(key).verify(original,signature);
        System.out.println("PT-OPS-NATIVE-028 STAGE fixedFixturePinSignature=true");
        String digest=HexFormat.of().formatHex(sha256.digest(original));
        var claims=new ReleaseApproval("0.1.0-PG316",digest);
        var inspected=StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup())
            .verifyCandidate(claims);
        if(!inspected.version().equals("0.1.0-PG316") || !inspected.sha256().equals(digest)
            || inspected.migrations().size()!=24 || !Files.readSymbolicLink(current).equals(old))
          throw new AssertionError("candidate observation mismatch");
        context.recheck(expected);
        return Boolean.TRUE;
      }).orElseThrow();
    });
    if(!result.orElseThrow())throw new AssertionError("M/A contention");
    context.recheck(expected);
    System.out.println("PT-OPS-NATIVE-028 PASS actualRootMorning=true actualM=true actualA=true fixedFixturePin=true originalByteSignature=true actualHostRoFullBom=true migrationsExpected=23 currentUnchanged=true approvalIssued=false rootAdmission=false schemaDbVerified=false backupBegins=false productionActivation=false fullParent=false businessR2R3=false");
  }
  private static byte[] fixedMaterial(Path file,int length)throws java.io.IOException {
    var before=Files.readAttributes(file,"unix:uid,gid,mode,nlink,size,dev,ino,lastModifiedTime,ctime",LinkOption.NOFOLLOW_LINKS);
    if(!Integer.valueOf(0).equals(before.get("uid"))||!Integer.valueOf(0).equals(before.get("gid"))
        ||!Integer.valueOf(0100400).equals(before.get("mode"))||!Integer.valueOf(1).equals(before.get("nlink"))
        ||!Long.valueOf(length).equals(before.get("size")))throw new AssertionError("fixture public material attributes");
    byte[] value;
    try(var input=Files.newInputStream(file,LinkOption.NOFOLLOW_LINKS)){value=input.readNBytes(length+1);}
    if(value.length!=length||!before.equals(Files.readAttributes(file,"unix:uid,gid,mode,nlink,size,dev,ino,lastModifiedTime,ctime",LinkOption.NOFOLLOW_LINKS)))
      throw new AssertionError("fixture public material changed");
    return value;
  }
}
