"""SS198/266 fixed pending code-only owner. No epoch/revoke/Unit/DB business writes."""
from pg1546_pending_candidate_ro_sources import java as old_java,RO_JAVA,CLASS as OLD_CLASS,TOOLS as OLD_TOOLS,SAVE as OLD_SAVE,once

CLASS='Pg1553PendingPublication'
TOOLS='pg1553-pending-publication-tools-v1'
SAVE='pg1556-pending-publication-v1'

PUBLICATION=r'''
  static void publication(dev.codex.schubert.nk.bootstrap.ReleaseApproval candidate,References refs,MaintenanceRunFiles.Session session)throws Exception {
    Path approval=Path.of("/etc/schubert-nk/release-approval/current");
    Path current=Path.of("/opt/schubert-nk/current");
    Path epoch=Path.of("/run/schubert-nk/startup/epoch.current");
    byte[] oldEpoch=Files.readAllBytes(epoch);
    byte[] oldApproval=("NKRELEASEAPPROVAL1\nversion=0.1.0-PG1292\nmanifest_sha256=ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99\n").getBytes(StandardCharsets.US_ASCII);
    byte[] literal=("NKRELEASEAPPROVAL1\nversion=0.1.0-PG1544\nmanifest_sha256=e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c\n").getBytes(StandardCharsets.US_ASCII);
    require(Arrays.equals(Files.readAllBytes(approval),oldApproval)&&Arrays.equals(candidate.encode(),literal));
    require(Files.readSymbolicLink(current).equals(Path.of("/opt/schubert-nk/releases/0.1.0-PG1292")));
    Pg481PendingDeployment.privateWrite(SAVE.resolve("old-approval.private"),oldApproval);
    Pg481PendingDeployment.privateWrite(SAVE.resolve("old-epoch.private"),oldEpoch);
    phase="ATOMIC_APPROVAL_ONLY";
    Path part=approval.resolveSibling("pg1553-approval.part");
    Pg481PendingDeployment.privateWrite(part,literal);
    Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));
    try(var file=java.nio.channels.FileChannel.open(part,StandardOpenOption.READ)){file.force(true);}
    Files.move(part,approval,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
    Pg387TrustedDeployment.sync(approval.getParent());refs.check("approval");original(session);
    phase="CURRENT_EXCHANGE_OLD_INODE_PRIVATE";
    refs.check("exchange");original(session);
    require(Files.readSymbolicLink(current).equals(Path.of("/opt/schubert-nk/releases/0.1.0-PG1544"))&&Arrays.equals(Files.readAllBytes(approval),literal));
    require(Arrays.equals(Files.readAllBytes(epoch),oldEpoch));
    var verified=dev.codex.schubert.nk.bootstrap.StartupReleaseManifest.createHost(
        new dev.codex.schubert.nk.bootstrap.FixedServiceIdentity().configurationGroup()).verify(candidate);
    require(verified.version().equals("0.1.0-PG1544"));
  }
'''

VERIFY_AND_PUBLISH=r'''
              phase="ALREADY_QUALIFIED_CANDIDATE_RO";
              Pg387TrustedDeployment.LABEL="PG1544";Pg387TrustedDeployment.STEM="pg1544";
              Pg387TrustedDeployment.SOURCE="4d6bcbddb417b76d27e52d5d9640752c300edccf";
              Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG1544");
              var mounted=new ProcessBuilder("/usr/bin/findmnt","-n","-o","OPTIONS","--mountpoint",Pg387TrustedDeployment.RELEASE.toString()).start();
              byte[] options=mounted.getInputStream().readAllBytes();require(options.length<=4096);int status=mounted.waitFor();
              mounted.getInputStream().close();mounted.getOutputStream().close();mounted.getErrorStream().close();
              require(status==0&&readonlyOptions(new String(options,StandardCharsets.US_ASCII).strip()));
              var candidate=Pg387TrustedDeployment.verify();
              require(candidate.version().equals("0.1.0-PG1544")&&candidate.manifestSha256().equals("e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c"));
              publication(candidate,refs,session);
'''

def java():
    s=old_java().replace(OLD_CLASS,CLASS).replace(OLD_TOOLS,TOOLS).replace(OLD_SAVE,SAVE).replace('pg1546_pending_candidate_ro_refs.py','pg1553_pending_publication_refs.py').replace('PG1549_','PG1556_').replace('PG269-candidate-ro','PG270-pending-code')
    s=once(s,'"prepare-ro".equals(args[0])','"activate".equals(args[0])')
    s=once(s,'Set.of("prepare","prepared","run")','Set.of("prepare","approval","exchange","run")')
    s=once(s,RO_JAVA,VERIFY_AND_PUBLISH)
    s=once(s,'              refs.check("prepared");original(session);','              original(session);')
    s=once(s,'  public static void main(String[] args)throws Exception {',PUBLICATION+'\n  public static void main(String[] args)throws Exception {')
    return s.replace('candidateHostRo=true','pendingCodeOnly=true').replace('candidateHostRo','pendingCodeOnly')
