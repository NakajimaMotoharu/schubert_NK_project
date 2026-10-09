"""Actual75s same two connections under current750 M/A/tenRef; no business operation."""
import ast
from pathlib import Path
from pg783_sources import java as previous_java,helper as previous_helper

R=Path(__file__).resolve().parent
SOURCE='8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'
DIGEST='a96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289'


def bind(raw):return raw.replace('Pg783ExistingPairRetirement','Pg797DatabaseProbe').replace('pg783','pg797').replace('PG783','PG797').replace('pg797-existing-pair-tools-v1','pg797-liveness-tools-v1').replace('pg797-existing-pair-retire-v1','pg797-liveness-probe-v1')


BODY=r'''
  static Pg797OwnedDatabase batchLease,schemaLease;
  static long lastPulse;
  static Pg797OwnedDatabase lease(Connection db,String role,String app,boolean readOnly,boolean lock)throws Exception{
    try(var q=db.createStatement();var r=q.executeQuery("select pg_backend_pid()")){
      require(r.next());int backend=r.getInt(1);require(!r.wasNull()&&!r.next());
      var result=new Pg797OwnedDatabase(db,new Pg797OwnedDatabase.Expected(backend,role,app,"schubert_nk",readOnly,lock));result.verify();return result;
    }
  }
  static void pulse()throws Exception{
    long now=System.nanoTime();
    if(lastPulse==0||now-lastPulse>=java.util.concurrent.TimeUnit.SECONDS.toNanos(1)){
      if(batchLease!=null)batchLease.verify();if(schemaLease!=null)schemaLease.verify();lastPulse=System.nanoTime();
    }
  }
  static void body(boolean verify,OwnedTransferDirectory root,Connection db,Connection schema)throws Exception{
    require(verify);phase="LIVE_BEFORE";helper("verify");parent();signed();
    var invalid=new StartupPermitFiles(root,LinuxInodeSecurity.create()).current();require(invalid.state()==StartupPermitRecords.State.INVALID&&actualNames().equals(retiredNames()));pending(invalid,db);
    var original=Pg428ColdBootPreparation.original();var backups=Pg481NativeStop.backup();var rows=business(schema);require(rows.get("schubert.batch_runs").rows()==544);
    Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));touched=true;
    helper("capture");phase="SAME_SERVER_LONG_WAIT";long began=System.nanoTime();int observations=0;
    for(int n=0;n<15;n++){
      batchLease.verify();schemaLease.verify();observations++;Thread.sleep(5000);pulse();
    }
    require(System.nanoTime()-began>=java.util.concurrent.TimeUnit.SECONDS.toNanos(75)&&observations==15);batchLease.verify();schemaLease.verify();
    helper("verify");parent();signed();pending(invalid,db);
    require(invalid.equals(new StartupPermitFiles(root,LinuxInodeSecurity.create()).current())&&actualNames().equals(retiredNames())&&original.equals(Pg428ColdBootPreparation.original())&&backups.equals(Pg481NativeStop.backup())&&rows.equals(business(schema)));
    save("body-complete.private","sameTwoServersAliveOver75s=true\nroleIdleTimeoutUnchanged=true\nall24Preserved=true\nstartsStopsRevokeRetire0=true\nnewOuterScopesNotYetReturned=true\n");
  }
'''


def java():
    raw=bind(previous_java());start=raw.index('  static void body(');end=raw.index('  public static void main(',start);raw=raw[:start]+BODY+raw[end:]
    raw=raw.replace('require(args.length==1 && Set.of("verify","recover").contains(args[0]));boolean verify=args[0].equals("verify");', 'require(args.length==1 && "verify".equals(args[0]));boolean verify=true;')
    raw=raw.replace('phase="REFERENCE_ACQUIRE";refsHeld=true;', 'batchLease=lease(db,"schubert_batch","PG797-fixed-recovery",false,true);schemaLease=lease(schema,"schubert_migration","PG797-fixed-snapshot",true,false);phase="REFERENCE_ACQUIRE";refsHeld=true;')
    raw=raw.replace('while(System.nanoTime()<deadline){', 'while(System.nanoTime()<deadline){pulse();')
    raw=raw.replace('phase="A_SCOPE_CLOSE";return Boolean.TRUE;', 'batchLease.confirmClosed();schemaLease.confirmClosed();phase="A_SCOPE_CLOSE";return Boolean.TRUE;')
    old='for(;;)try{Thread.sleep(1000);}catch(InterruptedException ignored){Thread.interrupted();}'
    new='''boolean notified=false;
    for(;;){
      try{if(batchLease!=null&&batchLease.heartbeatAllowed())batchLease.verify();if(schemaLease!=null&&schemaLease.heartbeatAllowed())schemaLease.verify();}
      catch(Exception|Error lost){if(!notified){System.err.println("PG797_DB_NOT_CONFIRMED ownershipNotInferred=true");notified=true;}}
      try{Thread.sleep(1000);}catch(InterruptedException ignored){Thread.interrupted();}
    }'''
    assert raw.count(old)==1;raw=raw.replace(old,new)
    old='if(!verify)save("complete.private","allNewScopesReturnedNormally=true\\noldCloseNotInferred=true\\nexistingPairRetired=true\\ncurrentSameEpochInvalid=true\\nstarts0=true\\n");'
    assert old in raw;raw=raw.replace(old,'save("complete.private","allNewScopesReturnedNormally=true\\nsameTwoServersOver75s=true\\ndbClosedConfirmed=true\\noldCloseNotInferred=true\\nstartsStopsRevokeRetire0=true\\n");')
    return raw


def helper():
    raw=bind(previous_helper()).replace('pg786-stopped-current-v1/before.private.json','pg787-retired-post-v1/after.private.json').replace('b6165c75ccc067991654d0b43db272096fc05019029d7e15e31af157cf35ad23','07b39c1faf43629f79d36e58055817aedb1a30ac36d0c3e34707df5e7e3cb5b2')
    # Readonly probe helper has no retirement action/surface.
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='main');lines=raw.splitlines(keepends=True)
    main=r'''def main():
 require(os.geteuid()==0 and len(sys.argv)==2);load_definitions();action=sys.argv[1];require(action in ('verify','capture'));parent();holder()
 if action=='verify':verify_live();return
 require(ROOT.is_dir()and not ROOT.is_symlink()and ROOT.stat().st_uid==ROOT.stat().st_gid==0 and stat.S_IMODE(ROOT.stat().st_mode)==0o700)
 verify_live();value=snapshot();require(value==snapshot());save('snapshot-before.private.json',json.dumps(value,sort_keys=True).encode())
'''
    return ''.join(lines[:node.lineno-1])+main+''.join(lines[node.end_lineno:])
