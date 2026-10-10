"""SSC262 actual ordinary-DONE scoped finite publication, not cold/empty authority."""
import ast
from pathlib import Path
from pg1300_current_candidate_ro_sources import sources as previous
from pg1293_completed_unused_stage_sources import once

HERE=Path(__file__).resolve().parent

JAVA_PUBLICATION=r'''
  static StartupPermitRecords.Epoch invalidExpected;
  static void transitionOriginal(StartupPermitRecords.Epoch epoch,MaintenanceCompletion done){
    if(invalidExpected==null){verifyOriginalValues(epoch,done);return;}
    require(epoch!=null&&done!=null&&epoch.equals(invalidExpected)&&done.activation().equals(invalidExpected.activation())
        &&done.outcome()==MaintenanceCompletion.Outcome.SUCCESS&&done.endedAt().equals(java.time.Instant.parse("2026-10-10T20:22:34.439375Z")));
  }
  static void publish(References refs)throws Exception{
    require(Files.readSymbolicLink(Path.of("/proc/self/ns/mnt")).equals(Files.readSymbolicLink(Path.of("/proc/1/ns/mnt"))));
    Pg387TrustedDeployment.LABEL="PG1292";Pg387TrustedDeployment.STEM="pg1292";
    Pg387TrustedDeployment.SOURCE="769ddb15cd735c25fef581b5f9850ef9d0053c0f";
    Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG1292");
    require(readOnlyMount(Files.readString(Path.of("/proc/self/mountinfo")),Pg387TrustedDeployment.RELEASE.toString()));
    var candidate=Pg387TrustedDeployment.verify();
    require(candidate.version().equals("0.1.0-PG1292")&&candidate.manifestSha256().equals("ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99"));
    byte[] literal=("NKRELEASEAPPROVAL1\nversion=0.1.0-PG1292\nmanifest_sha256=ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99\n").getBytes(StandardCharsets.US_ASCII);
    require(Arrays.equals(literal,candidate.encode()));
    var directory=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"));
    try{
      var permits=new StartupPermitFiles(directory,LinuxInodeSecurity.create());var old=permits.current();verifyOriginal();
      UUID fresh=UUID.randomUUID();require(fresh.version()==4&&fresh.variant()==2&&!fresh.equals(old.boot())&&!fresh.equals(old.epoch())&&!fresh.equals(old.activation().id())&&!fresh.equals(old.activation().run().id()));
      invalidExpected=new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,old.boot(),fresh,old.activation(),Optional.empty());
      Pg481PendingDeployment.privateWrite(SAVE.resolve("expected-epoch.private"),StartupPermitRecords.epoch(invalidExpected));
      phase="CANONICAL_INVALID";var actual=permits.invalidate(old.boot(),fresh,old.activation());require(actual.equals(invalidExpected)&&permits.current().equals(invalidExpected));
      refs.check("epoch");verifyOriginal();
      Path approval=Path.of("/etc/schubert-nk/release-approval/current"),part=approval.resolveSibling("pg1306-approval.part");
      phase="ATOMIC_APPROVAL";Pg481PendingDeployment.privateWrite(part,literal);
      Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));
      try(var file=java.nio.channels.FileChannel.open(part,StandardOpenOption.READ)){file.force(true);}
      Files.move(part,approval,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(approval.getParent());
      refs.check("approval");verifyOriginal();
      phase="CURRENT_EXCHANGE_OLD_LINK_PRESERVATION";refs.check("exchange");verifyOriginal();
      require(Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg387TrustedDeployment.RELEASE)&&Arrays.equals(Files.readAllBytes(approval),literal));
      var verified=StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(candidate);
      require(verified.version().equals("0.1.0-PG1292")&&permits.current().equals(invalidExpected));
      phase="PUBLICATION_DIRECTORY_NORMAL_CLOSE";directory.close();
    }catch(Exception|Error failure){retain(failure);throw failure;}
  }
'''


def sources():
    result={}
    for name,text in previous().items():
        name=name.replace('Pg1300','Pg1306').replace('pg1300','pg1306').replace('CandidateRo','OrdinaryPublication')
        text=text.replace('Pg1300','Pg1306').replace('pg1300','pg1306').replace('PG1300','PG1306').replace('CandidateRo','OrdinaryPublication')
        if name=='Pg1306OrdinaryPublication.java':
            text=once(text,'"prepare-ro".equals(args[0])','"activate".equals(args[0])')
            text=once(text,'"prepare-ro",Integer.toString(pid)','"activate",Integer.toString(pid)')
            text=once(text,'require("before".equals(name) || "ro".equals(name) || "terminal".equals(name));',
                'require(Set.of("before","epoch","approval","exchange","terminal").contains(name));')
            text=once(text,'phase="CANDIDATE_RO";candidateReadOnly();refs.check("ro");','phase="FINITE_ORDINARY_PUBLICATION";publish(refs);')
            text=once(text,'      verifyOriginalValues(epoch,done);','      transitionOriginal(epoch,done);')
            begin=text.index('  static void candidateReadOnly()');end=text.index('  public static void main',begin)
            text=text[:begin]+JAVA_PUBLICATION+'\n'+text[end:]
            text=text.replace('candidateReadOnlyVerified=true','finiteOrdinaryPublication=true')
        elif name=='pg1306_native_owned_stop.py':
            text=text.replace("b'prepare-ro'","b'activate'")
            begin=text.index('def placement_action(')
            text=text[:begin]+r'''
def placement_action(action,state):
 require(type(action)is str and type(state)is str and action in ['before','epoch','approval','exchange','terminal','release'])
 require(action=='before'and state=='before'or action=='epoch'and state=='before'or action=='approval'and state=='epoch'or action=='exchange'and state=='approval'or action in ['terminal','release']and state=='old-linked-private')
 return True
'''
        elif name=='pg1306_native_refs.py':
            text=once(text,"sys.argv[1] == 'prepare-ro'","sys.argv[1] == 'activate'")
            begin=text.index('    candidate_root=');end=text.index('    held = owner()',begin)
            text=text[:begin]+text[end:]
            text=text.replace('placed = False','publication_phase = \'before\'')
            text=once(text,"require(str(pathlib.Path('/opt/schubert-nk/current').readlink()) == '/opt/schubert-nk/releases/0.1.0-PG1068' and owner() == held)",
                "require(str(pathlib.Path('/opt/schubert-nk/current').readlink()) == ('/opt/schubert-nk/releases/0.1.0-PG1292'if publication_phase=='old-linked-private'else'/opt/schubert-nk/releases/0.1.0-PG1068')and owner()==held)")
            begin=text.index('    def check_data(now):');end=text.index("    print('REF_READY', flush=True)",begin)
            text=text[:begin]+REF_INITIAL+text[end:]
            begin=text.index('    for line in sys.stdin.buffer:');end=text.index("    raise ValueError('readonly owner channel ended')",begin)
            text=text[:begin]+REF_LOOP+text[end:]
            ast.parse(text)
        if name.endswith('.py'):ast.parse(text)
        result[name]=text
    for name in ['pg1304_ordinary_publication_contract.py','pg1305_ordinary_exchange_io.py','pg1083_cold_publication_contract.py','pg1088_cold_exchange_io.py','pg1090_cold_finite_capture.py']:
        result[name]=(HERE/name).read_text()
    result['Pg1306TransitionTest.java']=TRANSITION_TEST
    return result


REF_INITIAL=r'''
    import pg1304_ordinary_publication_contract as oracle
    import pg1305_ordinary_exchange_io as exchange_io
    from pg1090_cold_finite_capture import direct_tree,fd_record,path_record
    roots=[oracle.STARTUP,oracle.APPROVAL,oracle.CURRENT]
    public=lambda:{p:direct_tree(p)for p in roots}
    public_before=public();require(public_before==public())
    begin_ns=time.time_ns();held_fds={};new_fds={}
    for p in roots:held_fds[p]=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    save_fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    for p in [oracle.STARTUP+'/epoch.current',oracle.APPROVAL+'/current']:
        held_fds[p]=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    held_fds[oracle.CURRENT+'/current']=os.open(oracle.CURRENT+'/current',os.O_PATH|os.O_NOFOLLOW|os.O_CLOEXEC)
    expected_epoch=None
    def phase_observe(phase):
        actual=public();require(actual==public())
        oracle.verify(public_before,actual,phase,expected_epoch,begin_ns,time.time_ns())
        for path,fd in held_fds.items():
            if path==oracle.CURRENT+'/current':
                name='current'if phase in ['before','epoch','approval','link-staged']else'pg1305-current.part'if phase=='exchanged'else'current-link.private'
                parent=save_fd if phase in ['old-linked-private','release']else held_fds[oracle.CURRENT]
                observed=exchange_io.linked_attributes(parent,name,fd)
            else:observed=fd_record(fd)
            oracle.verify_retained(path,public_before[next(r for r in roots if path==r or path.startswith(r+'/'))][path],observed,phase,actual,begin_ns,time.time_ns())
        for path,fd in new_fds.items():
            if path==oracle.CURRENT+'/current':
                name='pg1305-current.part'if phase=='link-staged'else'current'
                observed=exchange_io.linked_attributes(held_fds[oracle.CURRENT],name,fd)
                linked=actual[oracle.CURRENT][oracle.CURRENT+'/'+name]
            else:observed=fd_record(fd);linked=actual[next(r for r in roots if path.startswith(r+'/'))][path]
            require(observed==linked)
        durable_save(SAVE,'finite-'+phase+'-'+str(time.time_ns())+'.private.json',json.dumps(actual,sort_keys=True).encode())
    def check_data(now):
        require(first is not None and same_value({k:v for k,v in now.items()if k!='startup'},{k:v for k,v in first.items()if k!='startup'}))
        for u in UNITS:require(h.terminal(show(u,FIELDS)));h.kernel_empty(u)
        phase_observe(publication_phase)
    def save(name,v):durable_save(SAVE,name,json.dumps(v,sort_keys=True).encode())
    first=capture_data(True);require(first==capture_data(True));save('before.private.json',first)
    baseline=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1253-native-stop-v1/after.private.json').read_bytes()
    require(hashlib.sha256(baseline).hexdigest()==BASELINE_SHA and same_value(first,json.loads(baseline)))
    for u in UNITS:require(h.terminal(show(u,FIELDS)));h.kernel_empty(u)
    phase_observe('before')
'''

REF_LOOP=r'''
    for line in sys.stdin.buffer:
        action=line.rstrip(b'\n').decode('ascii');h.placement_action(action,publication_phase)
        if action=='epoch':
            expected_epoch=(SAVE/'expected-epoch.private').read_bytes();oracle.canonical_epoch(expected_epoch)
            publication_phase='epoch'
            p=oracle.STARTUP+'/epoch.current';new_fds[p]=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        elif action=='approval':
            publication_phase='approval';p=oracle.APPROVAL+'/current';new_fds[p]=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        elif action=='exchange':
            check_data(capture_data(True))
            directory=held_fds[oracle.CURRENT]
            require(not os.path.lexists(oracle.PART));os.symlink(oracle.NEW_LINK,'pg1305-current.part',dir_fd=directory);os.fsync(directory)
            new_fds[oracle.CURRENT+'/current']=os.open('pg1305-current.part',os.O_PATH|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=directory)
            phase_observe('link-staged')
            exchange_io.exchange(directory,'pg1305-current.part');os.fsync(directory);phase_observe('exchanged')
            exchange_io.move_old_link(directory,save_fd,held_fds[oracle.CURRENT+'/current']);publication_phase='old-linked-private'
        check_data(capture_data(action!='release'))
        if action=='release':
            phase_observe('release');save('after.private.json',capture_data(False))
            for fd in reversed(list(new_fds.values())):os.close(fd)
            for fd in reversed(list(held_fds.values())):os.close(fd)
            os.close(save_fd)
            for i,raw in enumerate(JOURNAL_READS):durable_save(SAVE,'parent-journal-read-'+str(i)+'.private.jsonl',raw)
            for u in reversed(refs):manager.UnrefUnit(u)
            bus.close();print('REF_RELEASED',flush=True);return
        print('REF_CHECKED',flush=True)
'''

TRANSITION_TEST=r'''
import dev.codex.schubert.nk.batch.file.StartupPermitRecords;
import dev.codex.schubert.nk.batch.repository.*;
import java.time.Instant;
import java.util.*;
public final class Pg1306TransitionTest{
 private Pg1306TransitionTest(){}
 static int checks;
 static final UUID BOOT=UUID.fromString("cbca8738-3b24-4090-b77c-bf029677cdd6"),RUN=UUID.fromString("9f651096-aef9-4fba-90b0-a653e99f035a"),ACT=UUID.fromString("27accac0-c118-4c98-9244-02625a2d88a7"),FRESH=UUID.fromString("11111111-2222-4333-8444-555555555555"),OTHER=UUID.fromString("aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee");
 static final Instant CUT=Instant.parse("2026-10-10T20:03:22.718197Z"),END=Instant.parse("2026-10-10T20:22:34.439375Z");
 static final MaintenanceActivation ACTIVATION=new MaintenanceActivation(new BatchRun(RUN,CUT),ACT);
 static StartupPermitRecords.Epoch e(StartupPermitRecords.State state,UUID boot,UUID epoch,MaintenanceActivation act){return new StartupPermitRecords.Epoch(state,boot,epoch,act,state==StartupPermitRecords.State.ISSUED?Optional.of("a".repeat(64)):Optional.empty());}
 static void reject(StartupPermitRecords.Epoch epoch,MaintenanceCompletion done){try{Pg1306OrdinaryPublication.transitionOriginal(epoch,done);throw new AssertionError("unknown transition accepted");}catch(IllegalStateException expected){checks++;}}
 public static void main(String[]args){
  var done=new MaintenanceCompletion(ACTIVATION,END,MaintenanceCompletion.Outcome.SUCCESS);
  Pg1306OrdinaryPublication.invalidExpected=null;Pg1306OrdinaryPublication.transitionOriginal(e(StartupPermitRecords.State.ISSUED,BOOT,FRESH,ACTIVATION),done);checks++;
  reject(e(StartupPermitRecords.State.INVALID,BOOT,FRESH,ACTIVATION),done);
  var expected=e(StartupPermitRecords.State.INVALID,BOOT,FRESH,ACTIVATION);Pg1306OrdinaryPublication.invalidExpected=expected;
  Pg1306OrdinaryPublication.transitionOriginal(expected,done);checks++;
  reject(null,done);reject(expected,null);
  reject(e(StartupPermitRecords.State.ISSUED,BOOT,FRESH,ACTIVATION),done);
  reject(e(StartupPermitRecords.State.INVALID,OTHER,FRESH,ACTIVATION),done);
  reject(e(StartupPermitRecords.State.INVALID,BOOT,OTHER,ACTIVATION),done);
  var foreign=new MaintenanceActivation(new BatchRun(OTHER,CUT),ACT);
  reject(e(StartupPermitRecords.State.INVALID,BOOT,FRESH,foreign),done);
  reject(expected,new MaintenanceCompletion(foreign,END,MaintenanceCompletion.Outcome.SUCCESS));
  reject(expected,new MaintenanceCompletion(ACTIVATION,END.minusNanos(1000),MaintenanceCompletion.Outcome.SUCCESS));
  reject(expected,new MaintenanceCompletion(ACTIVATION,END.plusNanos(1000),MaintenanceCompletion.Outcome.SUCCESS));
  reject(expected,new MaintenanceCompletion(ACTIVATION,END,MaintenanceCompletion.Outcome.FAILED));
  reject(expected,new MaintenanceCompletion(ACTIVATION,END,MaintenanceCompletion.Outcome.WARNING));
  Pg1306OrdinaryPublication.invalidExpected=null;
  if(checks!=14)throw new AssertionError("independent transition count");
  System.out.println("PG1306_TRANSITION_ORACLE independentChecks=14 IO0=true");
 }
}
'''
