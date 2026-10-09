"""Exact failed949/current796 scope: owned stop, canonical revoke, typed quarantine retirement.
SSC179/211/235/238 already-approved primitives; original active remains, no start/publication.
"""
import ast
from pathlib import Path
import pg779_sources as prior
from pg798_probe_sources import HELPER_JAVA,BUSINESS_JAVA
R=Path(__file__).resolve().parent
SOURCE='102cdf1d365ab321f74b523237590eee764ae858'
DIGEST='c48af3ada5e2f00b1704f65fdb4625d6220bed29b6cecbbd23d7354cf708880d'
EPOCH='0eece14c-f832-47c2-b7dd-14125682e7ea'
SNAPSHOT='92d01a39b3397702cb6635417bdf5d56a9c493e052a088e02faaecf31f9eb11c'
PAIRS=(('Pg779FailedRecovery','Pg813FailedRecovery'),('pg779','pg813'),('PG779','PG813'),
 (prior.SOURCE,SOURCE),(prior.DIGEST,DIGEST),('e4093109ab234700b61dd45711126e4e','7ea672e8a76c4a4a8a7994652366a4cc'),
 ('2797579','3123795'),('137240785885','155954641282'),('13724078','15595464'),
 ('PG750','PG796'),('pg750','pg796'),('3063762','3342473'),('2dd9f106319e4c79995c8d6880c3f1a6','6220dab5a87945d2bb144cb9e14f5f14'),('13884944','15742135'),
 ('3066272','3344741'),('b49fd80a49a9408e8b8e13dd52f733b5','02ae69dca0514d8c917831eee3ca82b6'),('13886491','15743589'),
 ('3072633','3350579'),('b9c8ad2fabf244939367171499e0eac9','42e945fbd2894199b7dfca297c989627'),('13889925','15746848'),
 ('2841798','3158873'),('47c9e398cfc043dfa7504bedbe486269','cb2f7a6c4beb4420a0e96adb65fb6f11'),('13746502','15613132'))
def bind(raw):
 for old,new in PAIRS:raw=raw.replace(old,new)
 return raw
NAMES=r'''  static Set<String> names(){
    var n=new HashSet<String>();n.add("epoch.current");
    for(String epoch:List.of("3c5cdcc5-204c-40fd-a731-996c6cd859e8","41691d5c-68c5-40c9-9bcc-899ce341df6b","538fe967-f9cb-4770-a03c-9bab715d0fdc","a3fd90d9-7470-4695-9ee8-c818fe19e42d","a46f1379-6025-4850-9930-658a72b0fa70","c84f3015-5f29-4844-868b-57de02b1b3fc","e45cbbc0-3eea-4b3b-bd00-2bb39e3ecc19","f5a2d1aa-3879-4f21-8e48-cfb40e48b677","e9f11f1c-f087-458a-aad0-8c1e4e140571",EPOCH))
      for(String suffix:List.of(".permit",".owner",".API.launch",".WEB.launch"))n.add(epoch+suffix);
    n.add("0a87a07d-09cf-478d-b276-180df3977e6f.owner");n.add("0a87a07d-09cf-478d-b276-180df3977e6f.permit");n.add(EPOCH+".API.start.intent");return Set.copyOf(n);
  }
  static Set<String> retiredNames(){var n=new HashSet<>(names());n.remove(EPOCH+".API.start.intent");return Set.copyOf(n);}
'''
LIVENESS=r'''  static Pg797OwnedDatabase batchLease,schemaLease;
  static Pg798DatabaseScope databaseScope;
  static long lastPulse;
  static Pg797OwnedDatabase lease(Connection db,String role,String app,boolean readOnly,boolean lock)throws Exception{
    try(var q=db.createStatement();var r=q.executeQuery("select pg_backend_pid()")){
      require(r.next());int backend=r.getInt(1);require(!r.wasNull()&&!r.next());
      var result=new Pg797OwnedDatabase(db,new Pg797OwnedDatabase.Expected(backend,role,app,"schubert_nk",readOnly,lock));result.verify();return result;
    }
  }
  static void pulse()throws Exception{
    long now=System.nanoTime();if(lastPulse==0||now-lastPulse>=java.util.concurrent.TimeUnit.SECONDS.toNanos(1)){
      if(databaseScope!=null)databaseScope.verify();lastPulse=System.nanoTime();
    }
  }
'''
def java():
 raw=bind(prior.java()).replace('static final String EPOCH="e9f11f1c-f087-458a-aad0-8c1e4e140571"','static final String EPOCH="'+EPOCH+'"')
 start=raw.index('  static Set<String> names()');end=raw.index('  static final class References',start);raw=raw[:start]+NAMES+raw[end:]
 raw=raw.replace('names().size()==41','names().size()==44').replace('retiredNames().size()==39','retiredNames().size()==43').replace('rows()==544','rows()==554')
 raw=raw.replace('static boolean refsHeld;','static boolean refsHeld;\n'+LIVENESS)
 start=raw.index('  static void helper(');end=raw.index('  static Set<String> businessTableNames()',start)
 raw=raw[:start]+HELPER_JAVA.replace('pg798','pg813')+BUSINESS_JAVA+raw[end:]
 raw=raw.replace('phase="REFERENCE_ACQUIRE";refsHeld=true;','batchLease=lease(db,"schubert_batch","PG813-fixed-recovery",false,true);schemaLease=lease(schema,"schubert_migration","PG813-fixed-snapshot",true,false);databaseScope=new Pg798DatabaseScope(batchLease,schemaLease);pulse();phase="REFERENCE_ACQUIRE";refsHeld=true;')
 raw=raw.replace('while(System.nanoTime()<deadline){','while(System.nanoTime()<deadline){pulse();')
 raw=raw.replace('phase="A_SCOPE_CLOSE";return Boolean.TRUE;','batchLease.confirmClosed();schemaLease.confirmClosed();phase="A_SCOPE_CLOSE";return Boolean.TRUE;')
 raw=raw.replace('for(;;)try{Thread.sleep(1000);}catch(InterruptedException ignored){Thread.interrupted();}',r'''boolean notified=false;
    for(;;){if(!notified)try{if(databaseScope!=null)databaseScope.verify();}catch(Exception|Error lost){System.err.println("PG813_DB_NOT_CONFIRMED ownershipNotInferred=true");notified=true;}try{Thread.sleep(1000);}catch(InterruptedException ignored){Thread.interrupted();}}
''')
 raw=raw.replace('helper("verify");parent();signed();','helper("verify");pulse();parent();pulse();signed();pulse();')
 raw=raw.replace('parent();signed();pending(', 'pulse();parent();pulse();signed();pulse();pending(')
 raw=raw.replace('body(verify,root,db,schema);phase="REFERENCE_CLOSE";', 'body(verify,root,db,schema);pulse();phase="REFERENCE_CLOSE";')
 raw=raw.replace('save("body-complete.private",','save("observations.private","count="+databaseScope.observations()+"\\nmaxGapNanos="+databaseScope.maxGapNanos()+"\\n");save("body-complete.private",')
 return raw

def helper():
 raw=bind(prior.helper()).replace('e9f11f1c-f087-458a-aad0-8c1e4e140571',EPOCH).replace('==544','==554')
 tree=ast.parse(raw);lines=raw.splitlines(keepends=True)
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='baseline')
 replacement=r'''def baseline():
 path=pathlib.Path('/var/lib/pgpt-s1-preservation/pg812-current-timeout-v4/current.private.json');data=path.read_bytes()
 require(hashlib.sha256(data).hexdigest()=='92d01a39b3397702cb6635417bdf5d56a9c493e052a088e02faaecf31f9eb11c')
 value=json.loads(data);require(len(value['rows'])==24 and len(value['rows']['schubert.batch_runs'])==554)
 for unit,a in list(value['actors'].items()):
  status={k:v.strip()for k,v in(r.split(':',1)for r in a['statusPrivate'].splitlines()if ':'in r)}
  value['actors'][unit]={'pid':str(a['pid']),'invocation':value['units'][unit]['InvocationID'],'ticks':a['ticks'],'authority':{k:status[k]for k in ['Uid','Gid','Groups','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs']},'cgroup':a['cgroup'],'argvSha256':a['argvSha256']}
 return value
'''
 raw=''.join(lines[:node.lineno-1])+replacement+''.join(lines[node.end_lineno:])
 raw=raw.replace('==oldnames-intents','==oldnames-intents')
 raw=raw.replace('  for tree_name in (startup,leaf):actual', '  require(actual[\'trees\'][startup][startup][\'metadata\'][:6]==before[\'trees\'][startup][startup][\'metadata\'][:6])\n  for tree_name in (startup,leaf):actual')
 # The retirement gate is invoked repeatedly: read-only proof, not a fresh O_EXCL receipt each time.
 raw=raw.replace(" save(action+'.private.json',", " if action=='retirement':return\n save(action+'.private.json',")
 ast.parse(raw);return raw

def java_test():
 raw=bind((R/'Pg778FailedRecoveryTest.java').read_text())
 raw=raw.replace('names().size()==41&&Pg813FailedRecovery.retiredNames().size()==39','names().size()==44&&Pg813FailedRecovery.retiredNames().size()==43')
 raw=raw.replace('"e9f11f1c-f087-458a-aad0-8c1e4e140571"))','"e9f11f1c-f087-458a-aad0-8c1e4e140571","0eece14c-f832-47c2-b7dd-14125682e7ea"))')
 raw=raw.replace('expected.add("e9f11f1c-f087-458a-aad0-8c1e4e140571.API.start.intent");expected.add("e9f11f1c-f087-458a-aad0-8c1e4e140571.WEB.start.intent");','expected.add("0eece14c-f832-47c2-b7dd-14125682e7ea.API.start.intent");')
 return raw
