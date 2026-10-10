"""SSC249250 completed-cold activation source, fixed no-remount/new slot only."""
import ast
from pg1084_cold_candidate_ro_sources import files as previous
from pg1091_cold_activation_refs import source as refs_source
from pg1069_cold_candidate_sources import replace_once

PUBLISH=r'''
  static void publication(ReleaseApproval candidate,References refs,MaintenanceRunFiles.Session session)throws Exception {
    require(candidate.version().equals("0.1.0-PG1068")&&candidate.manifestSha256().equals("0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d"));
    Path startup=Path.of("/run/schubert-nk/startup");
    try(var entries=Files.list(startup)){require(entries.findAny().isEmpty());}
    Path approval=Path.of("/etc/schubert-nk/release-approval/current");
    Path current=Path.of("/opt/schubert-nk/current");
    Pg481PendingDeployment.privateWrite(SAVE.resolve("old-approval.private"),Files.readAllBytes(approval));
    Pg481PendingDeployment.privateWrite(SAVE.resolve("old-current.private"),Files.readSymbolicLink(current).toString().getBytes(StandardCharsets.US_ASCII));
    UUID fresh=UUID.randomUUID();
    require(fresh.version()==4&&fresh.variant()==2&&!fresh.equals(UUID.fromString(BOOT))
        &&!fresh.equals(ORIGINAL.id())&&!fresh.equals(ORIGINAL.run().id()));
    var expected=new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,UUID.fromString(BOOT),fresh,ORIGINAL,Optional.empty());
    Pg481PendingDeployment.privateWrite(SAVE.resolve("new-epoch.private"),StartupPermitRecords.epoch(expected));
    try(var directory=dev.codex.schubert.nk.storage.OwnedTransferDirectory.open(
        dev.codex.schubert.nk.storage.LinuxDirectoryCalls.create(),startup)) {
      var permits=new StartupPermitFiles(directory,dev.codex.schubert.nk.storage.LinuxInodeSecurity.create());
      phase="LEGITIMATE_EMPTY_INVALID";
      var actual=permits.invalidate(UUID.fromString(BOOT),fresh,ORIGINAL);
      require(actual.equals(expected)&&permits.current().equals(expected));
      refs.check("epoch");original(session);
      phase="ATOMIC_APPROVAL";
      Path part=approval.resolveSibling("pg1091-approval.part");
      Pg481PendingDeployment.privateWrite(part,candidate.encode());
      Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));
      try(var file=java.nio.channels.FileChannel.open(part,StandardOpenOption.READ)){file.force(true);}
      Files.move(part,approval,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
      Pg387TrustedDeployment.sync(approval.getParent());refs.check("approval");original(session);
      phase="ATOMIC_EXCHANGE_LINKED_OLD";
      refs.check("exchange");original(session);
      require(Files.readSymbolicLink(current).equals(Path.of("/opt/schubert-nk/releases/0.1.0-PG1068")));
      require(Arrays.equals(Files.readAllBytes(approval),candidate.encode()));
      var verified=dev.codex.schubert.nk.bootstrap.StartupReleaseManifest.createHost(
          new dev.codex.schubert.nk.bootstrap.FixedServiceIdentity().configurationGroup()).verify(candidate);
      require(verified.version().equals("0.1.0-PG1068"));
      require(permits.current().equals(expected));
    }
  }
'''


def files():
    original=previous();result={}
    for name,text in original.items():
        if name.endswith('.py'):continue
        for old,new in [('Pg1084ColdCandidateRo','Pg1091ColdActivation'),
                        ('pg1084_cold_refs.py','pg1091_cold_refs.py'),
                        ('pg1084-cold-tools-v1','pg1091-cold-tools-v1'),
                        ('pg1084-cold-candidate-ro-v1','pg1091-cold-activate-v1'),
                        ('PG1084_','PG1091_')]:
            name=name.replace(old,new);text=text.replace(old,new)
        if not name.endswith('Test.java'):
            text=replace_once(text,'"prepare-ro".equals(args[0])','"activate".equals(args[0])')
            old='Set.of("prepare","prepared","run")'
            text=replace_once(text,old,'Set.of("prepare","prepared","epoch","approval","exchange","run")')
            # Child takes backend only; SAVE and operation are source constants.
            text=replace_once(text,'"verify",Integer.toString(backend)','Integer.toString(backend)')
            start=text.index('              phase="NECESSARY_CANDIDATE_HOST_RO";')
            end=text.index('              phase="FULL_IMMUTABLE_CANDIDATE";',start)
            text=text[:start]+'''              phase="ALREADY_QUALIFIED_CANDIDATE_RO";
              require(readOnlyMount(Files.readString(Path.of("/proc/self/mountinfo")),Pg387TrustedDeployment.RELEASE.toString()));
'''+text[end:]
            marker='              Pg387TrustedDeployment.LABEL="PG932";Pg387TrustedDeployment.STEM="pg932";'
            text=replace_once(text,marker,'              phase="FINITE_COLD_PUBLICATION";publication(candidate,refs,session);\n'+marker)
            text=replace_once(text,'              refs.check("prepared");original(session);','              original(session);')
            text=replace_once(text,'  public static void main(String[] args)throws Exception {',PUBLISH+'\n  public static void main(String[] args)throws Exception {')
            text=text.replace('candidateImmutableVerified=true','finiteColdActivation=true')
        else:
            text=text.replace('"prepare-ro"','"activate"')
        result[name]=text
    result['pg1091_cold_refs.py']=refs_source()
    ast.parse(result['pg1091_cold_refs.py'])
    return result
