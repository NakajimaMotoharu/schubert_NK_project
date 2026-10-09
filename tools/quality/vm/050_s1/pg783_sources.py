"""SSC236 fresh existing-INVALID three-intent retirement only; no stop/revoke/start."""
import ast
from pathlib import Path
import pg779_sources as prior

R=Path(__file__).resolve().parent
SOURCE=prior.SOURCE
DIGEST=prior.DIGEST


def bind(raw):return raw.replace('Pg779FailedRecovery','Pg783ExistingPairRetirement').replace('pg779','pg783').replace('PG779','PG783')

BODY=r'''
  static void body(boolean verify,OwnedTransferDirectory root,Connection db,Connection schema)throws Exception{
    phase="EXISTING_INVALID_PAIR";
    var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var invalid=files.current();pending(invalid,db);signed();
    require(invalid.state()==StartupPermitRecords.State.INVALID&&actualNames().equals(quarantinedNames()));
    var observed=RootFailedStartRecovery.observePair(root,LinuxInodeSecurity.create());
    var raw=new TreeMap<String,byte[]>();var metadata=new TreeMap<String,Map<String,Object>>();
    for(String name:actualNames()){
      var p=STARTUP.resolve(name);raw.put(name,Pg410KnownAuthRecovery.material(p,4096));metadata.put(name,Pg410KnownAuthRecovery.metadata(p));
    }
    require(observed.equals(pair(invalid,observed.api().permit(),raw))&&invalid.equals(observed.api().invalid()));
    var originals=Pg428ColdBootPreparation.original();var backups=Pg481NativeStop.backup();var data=business(schema);require(data.get("schubert.batch_runs").rows()==544);
    phase="FIXED_ALL_TERMINAL";helper("verify");parent();signed();pending(invalid,db);
    if(verify)return;
    Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
    helper("capture");phase="PURE_TYPED_RETIRE";touched=true;
    try{
      RootFailedStartRecovery.retirePair(root,LinuxInodeSecurity.create(),observed,expected->Pg387TrustedDeployment.checked(()->{
        require(observed.equals(expected)&&invalid.equals(files.current()));parent();signed();pending(invalid,db);helper("retirement");
        require(originals.equals(Pg428ColdBootPreparation.original())&&backups.equals(Pg481NativeStop.backup())&&data.equals(business(schema)));
        for(var e:raw.entrySet())if(!e.getKey().endsWith(".start.intent")&&!e.getKey().equals("permit-start.intent")){
          Path p=STARTUP.resolve(e.getKey());require(Arrays.equals(e.getValue(),Pg410KnownAuthRecovery.material(p,4096))&&metadata.get(e.getKey()).equals(Pg410KnownAuthRecovery.metadata(p)));
        }
        return Boolean.TRUE;
      }));
    }catch(Exception|Error failure){
      try{RootFailedStartRecovery.quarantinePair(root,LinuxInodeSecurity.create(),observed);}catch(Exception|Error secondary){failure.addSuppressed(secondary);}throw failure;
    }
    phase="RETIRED_POSTCONDITIONS";require(actualNames().equals(retiredNames())&&invalid.equals(files.current()));helper("retired");parent();signed();pending(invalid,db);
    require(originals.equals(Pg428ColdBootPreparation.original())&&backups.equals(Pg481NativeStop.backup())&&data.equals(business(schema)));
    save("body-complete.private","existingPairRetired=true\nstartsStopsRevoke0=true\nall24Preserved=true\noldCloseUnknown=true\nnewOuterScopesNotYetReturned=true\n");
  }
'''


def java():
    raw=bind(prior.java());start=raw.index('  static void body(');end=raw.index('  public static void main(',start)
    raw=raw[:start]+BODY+raw[end:]
    raw=raw.replace('  static Set<String> retiredNames()', '  static Set<String> quarantinedNames(){var n=new HashSet<>(names());n.add("permit-start.intent");return Set.copyOf(n);}\n  static Set<String> retiredNames()')
    raw=raw.replace('pg783-failed758-recovery-v1','pg783-existing-pair-retire-v1').replace('pg783-failed758-tools-v1','pg783-existing-pair-tools-v1')
    return raw


def helper():
    raw=bind(prior.helper()).replace('pg783-failed758-recovery-v1','pg783-existing-pair-retire-v1')
    # An inactive Unit may be GC'd after the independent786 Ref scope closes.
    # Only the typed idle transition is admitted; no old execution success is inferred.
    raw=raw.replace("require(old is not None and new is not None and old[:4]==new[:4]and old[5]==new[5])", "require(accepted(old,new,show(unit),{}))")
    raw=(R/'pg785_exec_history.py').read_text()+'\n'+raw
    tree=ast.parse(raw);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='verify_live')
    lines=raw.splitlines(keepends=True)
    replacement=r'''def verify_live():
 owner=holder();parent();all_units={u:show(u)for u in ORDER+EXTRA}
 for u,v in all_units.items():
  require(v['MainPID']==v['ControlPID']=='0'and v['Job']==''and v['ActiveState']in ('inactive','failed'));kernel_empty(u)
 require(snapshot()==baseline()['capturedSnapshot']and owner==holder());return all_units
'''
    raw=''.join(lines[:node.lineno-1])+replacement+''.join(lines[node.end_lineno:])
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='baseline');lines=raw.splitlines(keepends=True)
    replacement=r'''def baseline():
 path=pathlib.Path('/var/lib/pgpt-s1-preservation/pg786-stopped-current-v1/before.private.json');data=path.read_bytes()
 require(hashlib.sha256(data).hexdigest()=='b6165c75ccc067991654d0b43db272096fc05019029d7e15e31af157cf35ad23')
 value=json.loads(data);require(len(value['rows'])==24 and len(value['rows']['schubert.batch_runs'])==544)
 return {**value,'capturedSnapshot':value}
'''
    raw=''.join(lines[:node.lineno-1])+replacement+''.join(lines[node.end_lineno:])
    # No service process is started/stopped by this profile; capture is read-only current snapshot.
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='main');lines=raw.splitlines(keepends=True)
    replacement=r'''def main():
 require(os.geteuid()==0 and len(sys.argv)==2);load_definitions();action=sys.argv[1]
 require(action in ('verify','capture','retirement','retired'));parent();holder()
 if action=='verify':verify_live();return
 require(ROOT.is_dir()and not ROOT.is_symlink()and ROOT.stat().st_uid==ROOT.stat().st_gid==0 and stat.S_IMODE(ROOT.stat().st_mode)==0o700)
 if action=='capture':
  verify_live();before=snapshot();require(before==snapshot());save('snapshot-before.private.json',json.dumps(before,sort_keys=True).encode());save('units-before.private.json',json.dumps({u:show(u)for u in ORDER+EXTRA},sort_keys=True).encode());return
 for u in ORDER+EXTRA:
  v=show(u);require(v['MainPID']==v['ControlPID']=='0'and v['Job']=='');kernel_empty(u)
 before=json.loads((ROOT/'snapshot-before.private.json').read_text());actual=snapshot();startup='/run/schubert-nk/startup'
 require(epoch_value(pathlib.Path(startup+'/epoch.current').read_bytes(),True))
 intents={startup+'/e9f11f1c-f087-458a-aad0-8c1e4e140571.API.start.intent',startup+'/e9f11f1c-f087-458a-aad0-8c1e4e140571.WEB.start.intent',startup+'/permit-start.intent'}
 oldnames=set(before['trees'][startup]);newnames=set(actual['trees'][startup])
 if action=='retired':require(newnames==oldnames-intents)
 else:require(newnames-intents==oldnames-intents and newnames<=oldnames)
 for name in intents:
  actual['trees'][startup].pop(name,None);before['trees'][startup].pop(name,None)
 # Root identity remains held by Java/Refs; only our unlink updates directory time/size.
 require(actual['trees'][startup][startup]['metadata'][:6]==before['trees'][startup][startup]['metadata'][:6])
 actual['trees'][startup][startup]=before['trees'][startup][startup]
 require(before==actual and holder())
 # A repeated read gate performs no diagnostic receipt creation. Final result remains once-only.
 if action=='retired':save('retired.private.json',json.dumps({'allTenKernel0':True,'all24Preserved':True,'existingThreeIntentsRetired':True,'oldCloseUnknown':True},sort_keys=True).encode())
'''
    raw=''.join(lines[:node.lineno-1])+replacement+''.join(lines[node.end_lineno:])
    return raw
