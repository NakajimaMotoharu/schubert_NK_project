"""New current862/bootstrap-existing20 fixed profile, no old source/credential reuse."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
SOURCE='e01612fcd7f2752df5ae0836b78538fd5e87f120'
DIGEST='20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'
def bind(raw):
 for old,new in (
  ('Pg570','Pg894'),('PG570','PG894'),('pg570','pg894'),
  ('969d8ded10c0bf5841d9e3a5c531e922caf4a24a',SOURCE),
  ('a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b',DIGEST),
  ('PG548','PG862'),('pg548','pg862'),
  ('b7e73994-b951-4696-bdd1-cfbc8a10e734','93cb976e-c36c-47a3-b9e2-0ad28d2996de'),
  ('2026-10-08T04:03:00.714124Z','2026-10-09T19:07:23.894279Z'),
  ('12f1af04-180e-405c-8738-853bbd875443','0dfe0b7f-0e36-4b81-9086-500d896d1187'),
  ('2026-10-08T04:27:59.110604Z','2026-10-09T19:31:23.759513Z'),
  ('075ad6644b284056a6cccf7af252519b','75f48ce36cd740e98a801eede7fdbb7f'),
  ('46382089521','187002958845'),
  ('pg559-terminal-readback-v2','pg895-bootstrap-before-v1'),
  ('23263d00948c5df5aca9aa4741a4d0266d9b8d20ebe400c7d180f89bb9ce6677','BASELINE895_SHA'),
  ('==472','==584'),('pg557-native-stop-v1','pg887-native-stop-v1'),
  ('pg535_bootstrap_contract','pg894_bootstrap_contract'),
  ('from pg569_parent_join import completed_journal','from pg894_parent_join import completed_journal'),
  ('PG559-terminal-readback','PG894-bootstrap-guard'),
 ):raw=raw.replace(old,new)
 return raw
def java():
 raw=bind((R/'Pg570BootstrapExisting.java').read_text())
 old='Pg464CodeOnlyDeployment.configure("PG862","'+SOURCE+'",Path.of("/opt/schubert-nk/releases/0.1.0-PG862"));';assert raw.count(old)==1
 raw=raw.replace(old,'Pg387TrustedDeployment.LABEL="PG862";Pg387TrustedDeployment.STEM="pg862";Pg387TrustedDeployment.SOURCE="'+SOURCE+'";Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG862");')
 raw=raw.replace('  static String phase="PREFLIGHT";','''  static String phase="PREFLIGHT";
  static Pg797OwnedDatabase lease;
  static boolean lossReported;
  static long lastPulse,maxGap;
  static void pulse()throws Exception{if(lease==null)return;long now=System.nanoTime();if(lastPulse!=0)maxGap=Math.max(maxGap,now-lastPulse);if(lastPulse!=0&&now-lastPulse>=TimeUnit.SECONDS.toNanos(30))throw new java.sql.SQLException("owned database observation interval exceeded");lease.verify();lastPulse=now;}
''')
 raw=raw.replace('for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}','for(;;){if(lease!=null&&!lossReported)try{pulse();}catch(Exception|Error lost){System.err.println("PG894_DB_NOT_CONFIRMED ownershipNotInferred=true");lossReported=true;}try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}}')
 raw=raw.replace('while(System.nanoTime()<deadline){','while(System.nanoTime()<deadline){pulse();')
 marker='return database;';assert raw.count(marker)==1
 raw=raw.replace(marker,'lease=new Pg797OwnedDatabase(database,new Pg797OwnedDatabase.Expected(backend(database),"schubert_batch","PG894-bootstrap-guard","schubert_nk",true,true));lastPulse=0;pulse();return database;')
 # Confirm closed scopes explicitly before refs switch from present to absent.
 old='phase="PREPARE_DATABASE_SCOPE_CLOSE";\n          }';assert raw.count(old)==1
 raw=raw.replace(old,old+'lease.confirmClosed();lease=null;lastPulse=0;')
 old='phase="POST_DATABASE_SCOPE_CLOSE";\n            }';assert raw.count(old)==1
 raw=raw.replace(old,old+'lease.confirmClosed();lease=null;lastPulse=0;')
 return raw
def helper(baseline_sha):
 assert len(baseline_sha)==64 and all(x in '0123456789abcdef'for x in baseline_sha)
 raw=bind((R/'pg570_bootstrap_existing.py').read_text()).replace('BASELINE895_SHA',baseline_sha)
 raw=raw.replace('from pg536_bootstrap_execution_contract import configuration as history_configuration\n','')
 raw=raw.replace('from pg559_terminal_refs import peer_query,peer_counts_valid,namespace_valid','from pg894_db_contract import peer_query,peer_counts_valid,namespace_valid')
 raw=raw.replace('for unit in units:manager.RefUnit(unit);refs.append(unit)','for unit in units:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)')
 marker="require(SAVE.is_dir()";index=raw.rfind('\n',0,raw.index(marker))+1
 raw=raw[:index]+''' from pg894_configuration import FIELDS as CONFIG_FIELDS,same as config_same
 from pg894_configuration_capture import complete_configuration
 from pg894_exec_record import exec_record
 raw_show=show
 def show(unit,properties):
  if set(properties)==set(CONFIG_FIELDS):return complete_configuration(command(['systemctl','show',unit,'--property='+','.join(sorted(CONFIG_FIELDS))]).decode(),unit)
  return raw_show(unit,properties)
 cfg=lambda:CONFIG_FIELDS
'''+raw[index:]
 # Canonical full32 identity permits only legitimate same declaration execution-history change.
 a=raw.index("  if terminal is None:require(configuration==baseline['configuration'])");b=raw.index('  raw_dependencies=',a)
 raw=raw[:a]+"  require(set(configuration)==set(baseline['configuration'])and all(config_same(baseline['configuration'][u],configuration[u],exec_record)for u in units))\n"+raw[b:]
 ast.parse(raw);return raw
def files(baseline_sha):
 from pg870_ordinary_before import parser_source
 from pg776_failure_full import ADDITIONAL
 raw={'Pg894BootstrapExisting.java':java(),'Pg894BootstrapArgumentTest.java':bind((R/'Pg570BootstrapArgumentTest.java').read_text()),'pg894_bootstrap_existing.py':helper(baseline_sha)}
 contract=(R/'pg535_bootstrap_contract.py').read_text()
 contract=contract.replace("path = role + '/' + invocation + '.terminal.exec'","path = role + '/' + invocation + '.terminal.exec'\n    closing = role + '/' + invocation + '.closing.exec'")
 contract=contract.replace("path not in before and set(actual) == set(before) | {path}","path not in before and closing not in before and set(actual) == set(before) | {path,closing}")
 # Validate BOTH new files, never allow an unverified closing path.
 start=contract.index('    value = actual[path]');block=contract[start:]
 contract=contract[:start]+'    for selected in (path,closing):\n'+''.join('    '+l+'\n'for l in block.replace('actual[path]','actual[selected]').splitlines())
 raw['pg894_bootstrap_contract.py']=contract
 raw['pg894_parent_join.py']=(R/'pg569_parent_join.py').read_text().replace('from pg556_parent_receipt import completed','from pg887_parent_receipt import completed')
 parsed=ast.parse((R/'pg559_terminal_refs.py').read_text());names={'require','peer_query','peer_counts_valid','namespace_valid'}
 defs=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in names];assert len(defs)==4
 raw['pg894_db_contract.py']='import stat\n'+ast.unparse(ast.Module(body=defs,type_ignores=[])).replace('PG559-terminal-readback','PG894-bootstrap-guard')+'\n'
 for name in('pg529_dependency_graph.py','pg570_directory_identity.py','pg457_stable_actor.py','pg887_parent_receipt.py'):
  target='pg894_directory_identity.py'if name=='pg570_directory_identity.py'else name
  raw[target]=(R/name).read_text()if name!='pg887_parent_receipt.py'else(Path('/home/mini/codex/project1/work/pgpt-runs/PG379')/'pg887-native-tools-v1'/name).read_text()
 raw['pg894_configuration.py']=(R/'pg847_configuration.py').read_text()
 raw['pg894_configuration_capture.py']=(R/'pg775_configuration.py').read_text().replace('FragmentPath,DropInPaths','FragmentPath,DropInPaths,RestrictSUIDSGID,UMask,LimitCORE,MemoryMax,TasksMax')+ADDITIONAL
 raw['pg894_exec_record.py']='import re\n'+parser_source()
 for name,value in raw.items():
  if name.endswith('.py'):ast.parse(value)
 return raw
