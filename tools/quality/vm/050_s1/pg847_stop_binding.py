"""Same genuine846 proof only; fixed ordered TERM plus current DB lease, no start."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
SOURCE='2a0d5aa392c85a1dc12a1cdb423978e8500895b8'
DIGEST='8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977'

def source():
 raw=(R/'pg642_stop_binding.py').read_text()
 for old,new in(
  ('Pg642','Pg847'),('PG642','PG847'),('pg642','pg847'),
  ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5',SOURCE),
  ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe',DIGEST),
  ('e49243d5-de84-4714-8612-6912ddc17e9e','9de2d03c-28c7-4647-97d9-c66ace06048c'),
  ('2026-10-08T18:32:42.140966Z','2026-10-09T05:42:22.532331Z'),
  ('2026-10-08T18:32:42.140966+00:00','2026-10-09T05:42:22.532331+00:00'),
  ('7d381b67-b37b-48c6-99ac-e04a336f887d','021111b4-6de5-4733-917d-5ac176240ffc'),
  ('293d218b06454bd1a8ff350bb93de2d5','9c08566fff9945a492eaae25559c3084'),
  ('103062293730','171417627031'),('104862293730','173217627031'),('104329','175948'),('1522744','3417355'),
  ('pg640-completed-readonly-v1','pg846-completed-readonly-v1'),
  ('pg635-resume-preparation-v1','pg841-runtime-resume-v1'),
  ("'PG600', 'PG631'","'PG600', 'PG832'"),
  ("r'2026-10-08T[0-9:]{8}","r'2026-10-09T[0-9:]{8}"),
 ):
  assert old in raw,old;raw=raw.replace(old,new)
 ast.parse(raw);return raw

def namespace():
 env={'__file__':str(R/'pg847_stop_binding.py'),'__name__':'genuine832_ownedstop'}
 exec(compile(source(),'<847 same-genuine-source fixed owned bindings>','exec'),env);return env

def bindings(proof):return namespace()['bindings'](proof)

def generate(proof):
 values=namespace()['generate'](proof)
 java=values['Pg847NativeStop.java']
 old='Pg464CodeOnlyDeployment.configure("PG832","'+SOURCE+'",Path.of("/opt/schubert-nk/releases/0.1.0-PG832"));'
 assert java.count(old)==1
 java=java.replace(old,'Pg387TrustedDeployment.LABEL="PG832";Pg387TrustedDeployment.STEM="pg832";Pg387TrustedDeployment.SOURCE="'+SOURCE+'";Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG832");')
 java=java.replace('  static String phase="PREFLIGHT";','''  static String phase="PREFLIGHT";
  static Pg797OwnedDatabase lease;
  static boolean lossReported;
  static long lastPulse,maxGap;
  static void pulse()throws Exception{if(lease==null)return;long now=System.nanoTime();if(lastPulse!=0)maxGap=Math.max(maxGap,now-lastPulse);if(lastPulse!=0&&now-lastPulse>=TimeUnit.SECONDS.toNanos(30))throw new java.sql.SQLException("owned database observation interval exceeded");lease.verify();lastPulse=now;}
''')
 java=java.replace('for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}','for(;;){if(lease!=null&&!lossReported)try{pulse();}catch(Exception|Error lost){System.err.println("PG847_DB_NOT_CONFIRMED ownershipNotInferred=true");lossReported=true;}try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}}')
 java=java.replace('while(System.nanoTime()<deadline){','while(System.nanoTime()<deadline){if(!phase.equals("REF_CLOSE"))pulse();')
 marker='phase="REFERENCE_SCOPE";var refs=new References(pid,db);'
 assert java.count(marker)==1
 java=java.replace(marker,'lease=new Pg797OwnedDatabase(db,new Pg797OwnedDatabase.Expected(pid,"schubert_batch","PG847-native-stop","schubert_nk",true,true));pulse();'+marker)
 java=java.replace('phase="DB_CLOSE";db.rollback();db.close();','pulse();phase="DB_CLOSE";db.rollback();db.close();lease.confirmClosed();')
 java=java.replace('phase="COMPLETE_PUBLISH";','phase="COMPLETE_PUBLISH";Pg481PendingDeployment.privateWrite(SAVE.resolve("observations.private"),("maxGapNanos="+maxGap+"\\n").getBytes(StandardCharsets.US_ASCII));')
 values['Pg847NativeStop.java']=java
 refs=values['pg847_native_refs.py']
 refs=refs.replace("UNITS,FIELDS=sealed['UNITS'],sealed['FIELDS']", "UNITS,FIELDS=sealed['UNITS'],sealed['FIELDS']\n from pg847_configuration import FIELDS as CONFIG_FIELDS,same as config_same\n configuration_fields=lambda:CONFIG_FIELDS")
 old="cfg={u:show(u,configuration_fields())for u in UNITS};signed_cfg=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg841-runtime-resume-v1/after.private.json').read_bytes())['configuration']"
 assert refs.count(old)==1
 refs=refs.replace(old,"cfg={u:show(u,configuration_fields())for u in UNITS};signed_cfg=json.loads(original)['configuration']")
 marker="expected=signed_cfg[u];require(set(v)==set(expected)and all(v[k]==expected[k]for k in v if k!='ExecStart'))"
 assert refs.count(marker)==1
 refs=refs.replace(marker,"expected=signed_cfg[u];require(config_same(expected,v,exec_record))")
 old="old=first['configuration'][u];require(set(v)==set(old)and all(v[k]==old[k]for k in old if k!='ExecStart'))"
 assert refs.count(old)==1
 refs=refs.replace(old,"old=first['configuration'][u];require(config_same(old,v,exec_record))")
 values['pg847_native_refs.py']=refs
 values['pg847_configuration.py']=(R/'pg847_configuration.py').read_text()
 for name,raw in values.items():
  if name.endswith('.py'):ast.parse(raw)
 return values
