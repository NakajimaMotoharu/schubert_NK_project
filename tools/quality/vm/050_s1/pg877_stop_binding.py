"""PG875 genuine new1902 cohort only. Generate fixed owned stop; never operate VM."""
import ast
from pathlib import Path
from pg847_stop_binding import source as prior_source
R=Path(__file__).resolve().parent
SOURCE='e01612fcd7f2752df5ae0836b78538fd5e87f120'
DIGEST='20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'
RUN='19022204-8a9e-418d-ba2a-9967ff923dc2'
CUTOFF='2026-10-09T18:28:14.612111Z'
ACT='cf07d74f-14c7-4223-9eb9-82eb6f0fbd0d'
INV='09167719cb0445fea8da5a6fdbaa3b0f'
START=183192933299
DEADLINE=184992933299

def source():
 raw=prior_source()
 for old,new in (
  ('Pg847','Pg877'),('PG847','PG877'),('pg847','pg877'),
  ('2a0d5aa392c85a1dc12a1cdb423978e8500895b8',SOURCE),
  ('8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977',DIGEST),
  ('9de2d03c-28c7-4647-97d9-c66ace06048c',RUN),
  ('2026-10-09T05:42:22.532331Z',CUTOFF),
  ('2026-10-09T05:42:22.532331+00:00',CUTOFF.replace('Z','+00:00')),
  ('021111b4-6de5-4733-917d-5ac176240ffc',ACT),
  ('9c08566fff9945a492eaae25559c3084',INV),
  ('171417627031',str(START)),('173217627031',str(DEADLINE)),
  ('175948','189291'),('3417355','3592151'),
  ('pg846-completed-readonly-v1','pg875-completed-readonly-v1'),
  ('pg841-runtime-resume-v1','pg870-ordinary-before-v1'),
  ("'PG600', 'PG832'","'PG600', 'PG862'"),
 ):
  assert old in raw,old
  raw=raw.replace(old,new)
 ast.parse(raw)
 return raw

def namespace():
 env={'__file__':str(R/'pg877_stop_binding.py'),'__name__':'genuine862_ownedstop'}
 exec(compile(source(),'<877 fixed new1902 cohort>','exec'),env)
 return env

def bindings(proof):return namespace()['bindings'](proof)

def generate(proof):
 values=namespace()['generate'](proof)
 java=values['Pg877NativeStop.java']
 old='Pg464CodeOnlyDeployment.configure("PG862","'+SOURCE+'",Path.of("/opt/schubert-nk/releases/0.1.0-PG862"));'
 assert java.count(old)==1
 java=java.replace(old,'Pg387TrustedDeployment.LABEL="PG862";Pg387TrustedDeployment.STEM="pg862";Pg387TrustedDeployment.SOURCE="'+SOURCE+'";Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG862");')
 java=java.replace('  static String phase="PREFLIGHT";','''  static String phase="PREFLIGHT";
  static Pg797OwnedDatabase lease;
  static boolean lossReported;
  static long lastPulse,maxGap;
  static void pulse()throws Exception{if(lease==null)return;long now=System.nanoTime();if(lastPulse!=0)maxGap=Math.max(maxGap,now-lastPulse);if(lastPulse!=0&&now-lastPulse>=TimeUnit.SECONDS.toNanos(30))throw new java.sql.SQLException("owned database observation interval exceeded");lease.verify();lastPulse=now;}
''')
 java=java.replace('for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}','for(;;){if(lease!=null&&!lossReported)try{pulse();}catch(Exception|Error lost){System.err.println("PG877_DB_NOT_CONFIRMED ownershipNotInferred=true");lossReported=true;}try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}}')
 java=java.replace('while(System.nanoTime()<deadline){','while(System.nanoTime()<deadline){if(!phase.equals("REF_CLOSE"))pulse();')
 marker='phase="REFERENCE_SCOPE";var refs=new References(pid,db);'
 assert java.count(marker)==1
 java=java.replace(marker,'lease=new Pg797OwnedDatabase(db,new Pg797OwnedDatabase.Expected(pid,"schubert_batch","PG877-native-stop","schubert_nk",true,true));pulse();'+marker)
 java=java.replace('phase="DB_CLOSE";db.rollback();db.close();','pulse();phase="DB_CLOSE";db.rollback();db.close();lease.confirmClosed();')
 java=java.replace('phase="COMPLETE_PUBLISH";','phase="COMPLETE_PUBLISH";Pg481PendingDeployment.privateWrite(SAVE.resolve("observations.private"),("maxGapNanos="+maxGap+"\\n").getBytes(StandardCharsets.US_ASCII));')
 values['Pg877NativeStop.java']=java
 refs=values['pg877_native_refs.py']
 marker="UNITS,FIELDS=sealed['UNITS'],sealed['FIELDS']"
 assert refs.count(marker)==1
 refs=refs.replace(marker,marker+"\n from pg877_configuration import FIELDS as CONFIG_FIELDS,same as config_same\n from pg877_configuration_capture import complete_configuration\n configuration_fields=lambda:CONFIG_FIELDS")
 refs=refs.replace('for u in UNITS:manager.RefUnit(u);refs.append(u)','for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)')
 old="cfg={u:show(u,configuration_fields())for u in UNITS};signed_cfg=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg870-ordinary-before-v1/after.private.json').read_bytes())['configuration']"
 assert refs.count(old)==1
 refs=refs.replace(old,"cfg={u:complete_configuration(command(['/usr/bin/systemctl','show',u,'--property='+','.join(sorted(configuration_fields()))]).decode(),u)for u in UNITS};signed_cfg=json.loads(original)['configuration']")
 refs=refs.replace("expected=signed_cfg[u];require(set(v)==set(expected)and all(v[k]==expected[k]for k in v if k!='ExecStart'))","expected=signed_cfg[u];require(config_same(expected,v,exec_record))")
 refs=refs.replace("old=first['configuration'][u];require(set(v)==set(old)and all(v[k]==old[k]for k in old if k!='ExecStart'))","old=first['configuration'][u];require(config_same(old,v,exec_record))")
 refs=refs.replace("old=json.loads(original)['rows']","old=json.loads(original)['rows'];require(len(old)==24)")
 values['pg877_native_refs.py']=refs
 values['pg877_configuration.py']=(R/'pg847_configuration.py').read_text()
 pure=(R/'pg775_configuration.py').read_text().replace('FragmentPath,DropInPaths','FragmentPath,DropInPaths,RestrictSUIDSGID,UMask,LimitCORE,MemoryMax,TasksMax')
 from pg776_failure_full import ADDITIONAL
 values['pg877_configuration_capture.py']=pure+ADDITIONAL
 for name,raw in values.items():
  if name.endswith('.py'):ast.parse(raw)
 return values
