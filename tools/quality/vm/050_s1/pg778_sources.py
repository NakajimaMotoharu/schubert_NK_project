"""SSC235 fixed failed143 operator sources. No import-time VM/mutation or old DONE authority."""
from pathlib import Path
from pg662_sources import replace

R=Path(__file__).resolve().parent
SOURCE='8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'
DIGEST='a96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289'
EPOCH='e9f11f1c-f087-458a-aad0-8c1e4e140571'
PAIRS=(('Pg496TimeoutRecovery','Pg778FailedRecovery'),('PG496','PG778'),('pg496','pg778'),
 ('38899a05b5c2daeecfc5af8ea5ae748e29954c60',SOURCE),('652a5e4a31dd9251c5a89cb4f5dea031f157b17ab58f466fb329cdcbfbe1be1c',DIGEST),
 ('52accf6d68f44487b6e0b3635c20396f','e4093109ab234700b61dd45711126e4e'),('e07aa706-1acd-4e65-b309-d7f330f79d54','cc9ed874-7f4f-450e-a188-8de1e42c8441'),
 ('4d35762d-54b4-4187-ab03-cc9b7e9e3baf',EPOCH),('91a748b4-1abe-484c-9682-44f46429b324','9de2d03c-28c7-4647-97d9-c66ace06048c'),
 ('179758d2-5b77-443a-a743-bf0065e732ea','021111b4-6de5-4733-917d-5ac176240ffc'),('2026-10-06T12:06:14.564793Z','2026-10-09T05:42:22.532331Z'),
 ('3905484','2797579'),('255346663838','137240785885'),('PG489','PG750'),('pg489','pg750'),
 ('pg778-timeout-no-intents-v1','pg778-failed758-recovery-v1'),('pg778-timeout-tools-v6','pg778-failed758-tools-v1'))


def bind(raw):
    for old,new in PAIRS:raw=raw.replace(old,new)
    return raw

NAMES=r'''
  static Set<String> names(){
    var n=new HashSet<>(Set.of("epoch.current",EPOCH+".permit",EPOCH+".owner",EPOCH+".API.launch",EPOCH+".WEB.launch",EPOCH+".API.start.intent",EPOCH+".WEB.start.intent"));
    for(String old:List.of("3c5cdcc5-204c-40fd-a731-996c6cd859e8","41691d5c-68c5-40c9-9bcc-899ce341df6b","538fe967-f9cb-4770-a03c-9bab715d0fdc","a3fd90d9-7470-4695-9ee8-c818fe19e42d","a46f1379-6025-4850-9930-658a72b0fa70","c84f3015-5f29-4844-868b-57de02b1b3fc","e45cbbc0-3eea-4b3b-bd00-2bb39e3ecc19","f5a2d1aa-3879-4f21-8e48-cfb40e48b677"))
      for(String suffix:List.of(".permit",".owner",".API.launch",".WEB.launch"))n.add(old+suffix);
    n.add("0a87a07d-09cf-478d-b276-180df3977e6f.owner");n.add("0a87a07d-09cf-478d-b276-180df3977e6f.permit");return Set.copyOf(n);
  }
  static Set<String> retiredNames(){var n=new HashSet<>(names());n.remove(EPOCH+".API.start.intent");n.remove(EPOCH+".WEB.start.intent");return Set.copyOf(n);}
'''

REFERENCES=r'''
  static final class References {
    final Process child;final java.io.InputStream input;final java.io.OutputStream output;
    References(Connection db,boolean verify)throws Exception{
      int backend;try(var q=db.createStatement();var r=q.executeQuery("select pg_backend_pid()")){require(r.next());backend=r.getInt(1);require(backend>1&&!r.next());}
      var log=TOOLS.resolve(verify?"refs-verify.private.log":"refs-recover.private.log");Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg778_refs.py").toString(),verify?"verify":"recover",Integer.toString(backend)).redirectError(log.toFile()).start();
      input=child.getInputStream();output=child.getOutputStream();await("REF_READY");
    }
    void await(String expected)throws Exception{
      long deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(60);var bytes=new java.io.ByteArrayOutputStream();
      while(System.nanoTime()<deadline){
        while(input.available()>0){int v=input.read();require(v>=0&&bytes.size()<64);bytes.write(v);if(v==10){require(Arrays.equals(bytes.toByteArray(),(expected+"\n").getBytes(StandardCharsets.US_ASCII)));return;}}
        if(child.waitFor(10,java.util.concurrent.TimeUnit.MILLISECONDS)&&input.available()==0)throw new java.io.IOException("fixed Ref channel unavailable");
      }throw new java.io.IOException("fixed Ref deadline");
    }
    void release()throws Exception{
      output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED");require(child.waitFor(5,java.util.concurrent.TimeUnit.SECONDS)&&child.exitValue()==0);
      output.close();input.close();child.getErrorStream().close();
    }
  }
'''

PAIR=r'''
  static MaintenanceOwnerFrame.Parent child(byte[] raw,String service,long pid,String invocation,long ticks,StartupPermitRecords.Epoch epoch,MaintenanceOwnerFrame owner,String permitHash,byte[] ownerRaw)throws Exception{
    var v=Pg461Known30PairRecovery.launch(raw);
    require(v.get("service").equals(service)&&v.get("boot").equals(BOOT)&&v.get("epoch").equals(epoch.epoch().toString())&&v.get("invocation").equals(invocation)&&v.get("pid").equals(Long.toString(pid))&&v.get("start_ticks").equals(Long.toString(ticks))&&v.get("permit_sha256").equals(permitHash)&&v.get("owner_sha256").equals(Pg410KnownAuthRecovery.hash(ownerRaw)));
    require(owner.morning().pid()!=pid&&!owner.morning().invocation().equals(invocation));return new MaintenanceOwnerFrame.Parent(invocation,pid,ticks);
  }
  static RootFailedStartRecovery.PairEvidence pair(StartupPermitRecords.Epoch invalid,StartupPermitRecords.Permit permit,Map<String,byte[]> startup)throws Exception{
    byte[] raw=startup.get(EPOCH+".owner");var owner=MaintenanceOwnerFrame.consume(raw.clone());String hash=Pg410KnownAuthRecovery.hash(StartupPermitRecords.permit(permit));
    require(owner.cleanup().isEmpty()&&owner.boot().toString().equals(BOOT)&&owner.epoch().toString().equals(EPOCH)&&owner.run().equals(RUN)&&owner.activation().equals(ACTIVATION)&&owner.cutoff().equals(invalid.activation().run().cutoff())&&owner.morning().pid()==2797579&&owner.morning().invocation().equals(PARENT)&&owner.morning().startTicks()==13724078);
    var api=child(startup.get(EPOCH+".API.launch"),"API",3063762,"2dd9f106319e4c79995c8d6880c3f1a6",13884944,invalid,owner,hash,raw);
    var web=child(startup.get(EPOCH+".WEB.launch"),"WEB",3066272,"b49fd80a49a9408e8b8e13dd52f733b5",13886491,invalid,owner,hash,raw);
    return new RootFailedStartRecovery.PairEvidence(new RootFailedStartRecovery.Evidence(invalid,permit,hash,owner,ServiceConfigFiles.Service.API,api),new RootFailedStartRecovery.Evidence(invalid,permit,hash,owner,ServiceConfigFiles.Service.WEB,web));
  }
'''


def java():
    raw=bind((R/'Pg496TimeoutRecovery.java').read_text());start=raw.index('  static Set<String> names(){');end=raw.index('  static boolean parentValue(',start)
    raw=raw[:start]+NAMES+REFERENCES+PAIR+raw[end:]
    raw=replace(raw,(('names().size()==73','names().size()==41'),('rows()==442','rows()==544'),
        ('body(verify,root,db,schema);db.rollback();schema.rollback();phase="DATABASE_SCOPE_CLOSE";',
         'phase="REFERENCE_ACQUIRE";var refs=new References(db,verify);body(verify,root,db,schema);phase="REFERENCE_CLOSE";refs.release();db.rollback();schema.rollback();phase="DATABASE_SCOPE_CLOSE";')))
    raw=replace(raw, (('phase="CANONICAL_REVOKE";require(files.revoke(invalid,permit).equals(invalid));',
        'var pair=pair(invalid,permit,startup);phase="CANONICAL_REVOKE";require(files.revoke(invalid,permit).equals(invalid));'),))
    old='    save("body-complete.private","parentTimeout143=true\\noldCloseNotInferred=true\\nintentsRetired0=true\\ncurrentSameEpochInvalid=true\\nall24TablesPreserved=true\\nallNewScopesNotYetReturned=true\\n");'
    new=r'''    phase="PUBLICATION_QUARANTINE";
    RootFailedStartRecovery.quarantinePair(root,LinuxInodeSecurity.create(),pair);
    require(pair.equals(RootFailedStartRecovery.observePair(root,LinuxInodeSecurity.create())));
    phase="TYPED_PAIR_RETIRE";
    try{
      RootFailedStartRecovery.retirePair(root,LinuxInodeSecurity.create(),pair,expected->Pg387TrustedDeployment.checked(()->{
        require(pair.equals(expected)&&invalid.equals(files.current()));parent();signed();pending(invalid,db);helper("retirement");
        require(originals.equals(Pg428ColdBootPreparation.original())&&backups.equals(Pg481NativeStop.backup())&&data.equals(business(schema)));return Boolean.TRUE;
      }));
    }catch(Exception|Error failure){
      try{RootFailedStartRecovery.quarantinePair(root,LinuxInodeSecurity.create(),pair);}catch(Exception|Error secondary){failure.addSuppressed(secondary);}throw failure;
    }
    require(actualNames().equals(retiredNames())&&retiredNames().size()==39&&invalid.equals(files.current()));helper("retired");parent();signed();pending(invalid,db);
    save("body-complete.private","parentTimeout143=true\noldCloseNotInferred=true\nexistingPairRetired=true\ncurrentSameEpochInvalid=true\nall24TablesPreserved=true\nallNewScopesNotYetReturned=true\n");'''
    raw=replace(raw,((old,new),('intentsRetired0=true\\ncurrentSameEpochInvalid=true\\nstarts0=true','existingPairRetired=true\\ncurrentSameEpochInvalid=true\\nstarts0=true')))
    raw=replace(raw,(('return mutated || at.endsWith("_CLOSE") || failure.getSuppressed().length!=0;',
        'return mutated || at.startsWith("REFERENCE_") || at.endsWith("_CLOSE") || failure.getSuppressed().length!=0;'),))
    return raw.replace('SSC204/QA047/BUG799/YKT570: fixed PG493 timeout with ZERO existing intents.','SSC235/QA047/BUG927/YKT696: fixed PG758 timeout143 and actual two intents.')


def helper():
    raw=bind((R/'pg496_timeout_owned.py').read_text());raw=raw.replace('import ast,hashlib,json,os,pathlib,shutil,stat,subprocess,sys','import ast,hashlib,json,os,pathlib,shutil,stat,subprocess,sys\nimport dbus')
    start=raw.index('EXPECTED=');end=raw.index('PINS=',start)
    raw=raw[:start]+"EXPECTED={'caddy.service':('3072633','b9c8ad2fabf244939367171499e0eac9',13889925),'schubert-nk-web.service':('3066272','b49fd80a49a9408e8b8e13dd52f733b5',13886491),'schubert-nk-api.service':('3063762','2dd9f106319e4c79995c8d6880c3f1a6',13884944),'artemis.service':('2841798','47c9e398cfc043dfa7504bedbe486269',13746502)}\n"+raw[end:]
    raw=replace(raw,(("def baseline():return json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg493-parent-failure-v1/observed.private.json').read_text())",r'''def baseline():
 path=pathlib.Path('/var/lib/pgpt-s1-preservation/pg777-failure-full758-v1/snapshot.private.json');data=path.read_bytes()
 require(hashlib.sha256(data).hexdigest()=='80594db5e3a5588a26b05be729e80a40f750a44230f34c3e025f923f365ddba4')
 value=json.loads(data);require(value['source']=='8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'and len(value['rows'])==24 and len(value['rows']['schubert.batch_runs'])==544)
 value['trees']={k:value[n]for k,n in [('/run/schubert-nk/startup','startup'),('/var/lib/schubert-nk/maintenance','originals'),('/srv/schubert-nk/backup','backup')]}
 value['units']=value['beforeActors'];return value'''),('==442','==544')))
    # Only manager fields common to the private capture are compared before stop. Remaining
    # declaration/security fields are separately bound by full configuration and signed files.
    raw=replace(raw,(("v==baseline()['units'][u]", "all(v[k]==x for k,x in baseline()['units'][u].items()if k in FIELDS)"),))
    # Configuration during stop contains dynamic ExecStart history. Compare its immutable
    # declaration with separately fixed principal fields and full manager/native witness.
    start=raw.index('def snapshot():');end=raw.index('def configuration(',start)
    raw=raw[:start]+r'''def snapshot():
 previous=baseline();roots=list(previous['trees'])+['/srv/schubert-nk/data/transfer','/srv/schubert-nk/data/assets','/etc/schubert-nk/credentials','/etc/schubert-nk/release-approval']
 return {'rows':rows(),'trees':{x:tree(pathlib.Path(x))for x in roots},'configuration':{u:configuration(u)for u in ORDER+EXTRA}}
'''+raw[end:]
    start=raw.index('def configuration(unit):');end=raw.index('def actor(',start)
    raw=raw[:start]+configuration_helpers()+raw[end:]
    raw=raw.replace("action in ['verify','capture','terminal','revoked']","action in ['verify','capture','terminal','revoked','retirement','retired']")
    raw=replace(raw,((" exec(compile(ast.Module(body=definitions,type_ignores=[]),'<pinned readonly metadata>','exec'),globals())",r''' exec(compile(ast.Module(body=definitions,type_ignores=[]),'<pinned readonly metadata>','exec'),globals())
 import pg481_native_owned_stop,pg466_term_witness
 pg481_native_owned_stop.BOOT=BOOT;pg466_term_witness.BOOT=BOOT.replace('-','')'''),))
    raw=replace(raw,((" if action=='revoked':", " if action in ('revoked','retirement','retired'):"),))
    # Every non-intent entry must remain byte/metadata exact; the typed primitive authenticates
    # each temporary/retired intent under its own capability. This helper never creates one.
    raw=replace(raw,(("  require(set(actual['trees'][startup])==set(before['trees'][startup]))",r'''  oldnames=set(before['trees'][startup]);newnames=set(actual['trees'][startup])
  intents={startup+'/e9f11f1c-f087-458a-aad0-8c1e4e140571.API.start.intent',startup+'/e9f11f1c-f087-458a-aad0-8c1e4e140571.WEB.start.intent'}
  publication=startup+'/permit-start.intent'
  if action=='revoked':require(newnames==oldnames)
  elif action=='retired':require(newnames==oldnames-intents)
  else:require(newnames-intents-{publication}==oldnames-intents)
  for name in intents|{publication}:
   actual['trees'][startup].pop(name,None);before['trees'][startup].pop(name,None)'''),))
    return raw


def configuration_helpers():
    pure=(R/'pg775_configuration.py').read_text().replace('FIELDS','FIELDS_CONFIGURATION')
    from pg776_failure_full import ADDITIONAL
    return pure+ADDITIONAL+r'''
def configuration(unit):
 raw=command(['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(FIELDS_CONFIGURATION))]).decode()
 value=complete_configuration(raw,unit);expected=baseline()['configuration'][unit]
 policy=pathlib.Path('/var/lib/pgpt-s1-preservation/pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
 require(hashlib.sha256(policy).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
 funcs=[n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record'];require(len(funcs)==1)
 import re
 env={'re':re};exec(compile(ast.Module(body=funcs,type_ignores=[]),'<fixed declaration>','exec'),env)
 old=env['exec_record'](expected['ExecStart']);new=env['exec_record'](value['ExecStart'])
 require(old is not None and new is not None and old[:4]==new[:4]and old[5]==new[5])
 value['ExecStart']=expected['ExecStart'];require(value==expected);return value
'''
