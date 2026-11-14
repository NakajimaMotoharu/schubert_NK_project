"""Text/golden review of V030 and guarded cutback, not SQL execution or actual DB PT PASS."""
from pathlib import Path
import json,hashlib,re,datetime
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';proof=json.loads((b/'evidence/PG32606-audio-role818-source-v1/manifest.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
for path,h in proof['oldApplied29SqlHashes'].items():assert sha(r/path)==h
forward=r/proof['newDdlPaths'][0];rollback=r/proof['newDdlPaths'][1]
def statements(sql):
 result=[];text='';index=0;quote=None
 while index<len(sql):
  if quote:
   if sql.startswith(quote,index):text+=quote;index+=len(quote);quote=None
   else:text+=sql[index];index+=1
  elif sql.startswith('--',index):
   end=sql.find('\n',index);index=len(sql) if end<0 else end
  elif sql[index]=="'":quote="'";text+="'";index+=1
  elif sql[index]=='$':
   m=re.match(r'\$[A-Za-z_][A-Za-z_0-9]*\$|\$\$',sql[index:]);assert m;quote=m.group();text+=quote;index+=len(quote)
  elif sql[index]==';':
   result.append(re.sub(r'\s+',' ',text).strip());text='';index+=1
  else:text+=sql[index];index+=1
 assert quote is None and not text.strip()
 return result
f=statements(forward.read_text());expected=['ALTER TABLE schubert.audio_files ALTER COLUMN audio_role TYPE varchar(11)','ALTER TABLE schubert.audio_files DROP CONSTRAINT ck_audio_files_audio_role_bytes','ALTER TABLE schubert.audio_files ADD CONSTRAINT ck_audio_files_audio_role_bytes CHECK (octet_length(audio_role) BETWEEN 1 AND 11)'];assert f==expected
back=statements(rollback.read_text());expectedback=['BEGIN','LOCK TABLE schubert.audio_files IN ACCESS EXCLUSIVE MODE',"DO $audio_role_guard$ BEGIN IF EXISTS (SELECT 1 FROM schubert.audio_files WHERE octet_length(audio_role) > 8) THEN RAISE EXCEPTION 'audio role rollback blocked by values beyond original byte limit'; END IF; END $audio_role_guard$",'ALTER TABLE schubert.audio_files DROP CONSTRAINT ck_audio_files_audio_role_bytes','ALTER TABLE schubert.audio_files ALTER COLUMN audio_role TYPE varchar(8)','ALTER TABLE schubert.audio_files ADD CONSTRAINT ck_audio_files_audio_role_bytes CHECK (octet_length(audio_role) BETWEEN 1 AND 8)','COMMIT'];assert back==expectedback
vectors=[('voice',True),('movie_audio',True),('12345678901',True),('123456789012',False),('あああab',True),('ああああ',False),('',False)]
for value,accepted in vectors:assert (1<=len(value.encode())<=11)==accepted
rollback_vectors=[([],True),(['voice'],True),(['12345678'],True),(['movie_audio'],False),(['voice','123456789'],False),(['あああab'],False)]
for values,allowed in rollback_vectors:assert not any(len(s.encode())>8 for s in values)==allowed
newfields={};migration=r/'src/schubert-nk-api/src/main/resources/db/migration';assert len(list(migration.glob('V*.sql')))==30
for path in proof['dbTestSourceOnlyNotCompiledOrRun']:
 s=(r/path).read_text();assert ('V030__preserve_current_audio_role.sql' in s) if path.endswith('DatabaseMigrationTest.java') else ('"030"' in s)
p=i/'3046_audio_role818_independent_oracle.json';assert not p.exists();p.write_text(json.dumps(dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),metadataOnly=True,sourceTextReviewOnly=True,forward=ref(forward),rollback=ref(rollback),forwardGoldenStatements=expected,rollbackGoldenStatements=expectedback,old29AppliedSqlUnchanged=True,sourceMigrationArtifactCount=30,roleByteVectors=vectors,rollbackGuardLogicalVectors=rollback_vectors,actualDatabaseOrTransactionOrIndexFkGrantCheckExecuted=False,ddlRuntimePt='HOLD_NOT_RUN_NOT_PASS_NOT_MEASURED_COVERAGE',javaWholeExpected=818,newJavaDefinitions=1,independentGoldenFromSS396=True,productionMethodUsedForExpected=False,externalReviewSources=[dict(url='https://www.postgresql.org/docs/18/plpgsql-structure.html',supports='Final outer END may omit semicolon; grouping BEGIN/END is separate from SQL transaction control.'),dict(url='https://www.postgresql.org/docs/18/sql-do.html',supports='Dollar-quoted anonymous body form; execution is not performed here.')],defectState='JAVA_AND_DDL_STATIC_TARGETS_ONLY_DB_RETEST_HOLD'),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,metadataOnly=True,old29SqlUnchanged=True,forwardStatements=3,rollbackStatements=7,actualDbPt='HOLD_NOT_RUN'))
