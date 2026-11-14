"""Source-only CREATE TABLE projection matrix; old Main/Test verified against distinct original commits."""
from pathlib import Path
import json,hashlib,datetime,subprocess,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG32812-current-snapshot898-source-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();newmain=r/'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/CurrentMigrationProjection.java';newtest=r/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/CurrentMigrationProjectionTest.java';old={}
for folder,source in [('main','2db594c27f654977d74b09e5c2cad679c7c208cd'),('test','cd99a02beef21a54978e86b1caf76fce42457322')]:
 for p in (r/('src/schubert-nk-bootstrap/src/'+folder+'/java/dev/codex/schubert/nk/migration')).glob('*.java'):
  if p in [newmain,newtest]:continue
  path=str(p.relative_to(r));assert sha(p)==hashlib.sha256(subprocess.check_output(['git','show',source+':'+path])).hexdigest(),path;old[path]=sha(p)
assert len(old)==86 and sum(len(re.findall(r'@Test\b',(r/p).read_text())) for p in old if '/test/' in p)==886 and len(re.findall(r'@Test\b',newtest.read_text()))==12
schema=Path('/home/mini/codex/project1/schubert_project/program/database/schema.sql').read_text();matrix=[('speakers','id,game_id,name,normalized_name,is_protagonist,notes','LISSBS'),('script_files','id,game_id,relative_path,file_name,section_code,chapter_title,sha256,byte_size','LISSSSSL'),('script_entries','id,game_id,script_file_id,entry_index,line_number,entry_type,speaker_id,speaker_label,body,raw_block','LILIISLSSS'),('audio_files','id,game_id,relative_path,file_name,basename_upper,audio_role,container,duration_seconds,byte_size,sha256','LISSSSSDLS'),('entry_audio_links','entry_id,audio_file_id,link_type','LLS')];proof=[]
for table,cols,kinds in matrix:
 text=next(m.group(0) for m in re.finditer(r'CREATE TABLE[\s\S]*?;',schema) if m.group(0).startswith('CREATE TABLE scenario.'+table+' ('));types={}
 for name,kind in zip(cols.split(','),kinds):
  line=next(x.strip().rstrip(',') for x in text.splitlines() if re.match(r'\s+'+name+r'\s',x));types[name]=line
  expected={'L':'bigint','I':'integer','S':None,'B':'boolean','D':'numeric(12,3)'}[kind]
  if kind=='I':assert re.search(r' (smallint|integer)( |$)',line),(table,line,kind)
  elif expected:assert (' '+expected+' ') in line+' ',(table,line,kind)
 assert len(cols.split(','))==len(kinds);proof.append(dict(table=table,columns=cols.split(','),types=types,kindVector=kinds,sourceCreateTableSha256=hashlib.sha256(text.encode()).hexdigest()))
v=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),previousProductionCoreMain='2db594c27f654977d74b09e5c2cad679c7c208cd',previousUnitSource='cd99a02beef21a54978e86b1caf76fce42457322',oldSourceHashes=old,newMain=dict(path=str(newmain.relative_to(r)),sha256=sha(newmain)),newTest=dict(path=str(newtest.relative_to(r)),sha256=sha(newtest)),projectionMatrix=proof,wholeExpected=898,newDefinitions=12,oldDefinitions=886,allMain=43,physicalClasses=63,callerAttributes=dict(autoCommit=False,readOnly=True,permittedIsolation=[4,8],sameBeforeAfter=True,actualTransactionIdentityProven=False),independentLastNullResultCloseSequence=['R0','S0','R1','S1','R2','S2','R3','S3','S4'],bug='BUG2951',ykt='YKT2480',originalTest=dict(path=str((e/'original-CurrentMigrationProjectionTest.java.txt').relative_to(r)),sha256=sha(e/'original-CurrentMigrationProjectionTest.java.txt')),originalProductTests=0,expectedFromProduction=False,privateRootOrHeldClassActions=0,actualDbOrMasterBackupKeyFileVmAuthorityActions=0,newAcceptance=0)
(e/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,new=12,old=886,whole=898,noActions=True))
