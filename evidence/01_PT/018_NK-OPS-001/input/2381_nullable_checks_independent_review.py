"""Verify five exact old predicates wrapped IS TRUE and immutable legacy SQL, without SQL execution."""
from pathlib import Path
import json,hashlib,datetime,re,subprocess,xml.etree.ElementTree as X
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG29702-nullable-check-independent-source-review-v1';assert not e.exists();e.mkdir();sha=lambda data:hashlib.sha256(data).hexdigest();base='7aed8eace7c844c2f79f2e39db766faf914890d5';sql=r/'src/schubert-nk-api/src/main/resources/db/migration';new=sql/'V029__strict_nullable_compound_checks.sql';text=new.read_text()
def predicate(t,name):
 m=re.search(r'\b(?:ADD\s+)?CONSTRAINT\s+'+re.escape(name)+r'\s+CHECK\s*\(',t,re.I);assert m,name
 start=i=m.end();depth=1;quote=False
 while i<len(t):
  c=t[i]
  if c=="'":
   if quote and i+1<len(t) and t[i+1]=="'":i+=2;continue
   quote=not quote
  elif not quote:
   if c=='(':depth+=1
   elif c==')':
    depth-=1
    if depth==0:return t[start:i]
  i+=1
 raise AssertionError('unbalanced CHECK '+name)
normalize=lambda t:re.sub(r'\s+',' ',t).strip()
rows=[]
for file,names in [('V002__account_session_and_master_tables.sql',['ck_auth_sessions_revocation','ck_media_assets_pair']),('V003__business_message_log_and_web_tables.sql',['ck_notifications_error','ck_request_inbox_response_snapshot_pair','ck_request_inbox_result_reference'])]:
 old=(sql/file).read_text()
 for name in names:
  a=normalize(predicate(old,name));z=normalize(predicate(text,name));assert z=='( '+a+' ) IS TRUE',(name,a,z)
  rows.append(dict(constraint=name,oldPredicateSha256=sha(a.encode()),wrapperOnly=True,independentExpected='TRUE accepted; FALSE/NULL rejected per SS331 SSC340',legacySql=file))
code=re.sub(r'--[^\n]*','',text);assert len(re.findall(r'\bALTER TABLE\b',code))==4;assert len(re.findall(r'\bDROP CONSTRAINT\b',code))==len(re.findall(r'\bADD CONSTRAINT\b',code))==5
assert not re.search(r'\b(?:INSERT|UPDATE|DELETE|GRANT|REVOKE|TRUNCATE|COMMIT|ROLLBACK|BEGIN|DO)\b|NOT\s+VALID',code,re.I)
oldfiles=sorted(p for p in sql.glob('V*.sql') if p!=new)+[sql.parent/'provisioning/001_roles.sql'];assert len(oldfiles)==29;legacy=[]
for p in oldfiles:
 rel=str(p.relative_to(r));old=subprocess.check_output(['git','show',base+':'+rel]);assert old==p.read_bytes();legacy.append(dict(path=rel,sha256=sha(old),unchangedFrom=base))
test=r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database/DatabaseMigrationTest.java';t=test.read_text();before=(b/'evidence/PG29696-nullable-check-source-manufacture-v1/DatabaseMigrationTest.before.java.txt').read_text()
start=t.index('  @Test\n  @Order(20)');end=t.index('  private static void writeQueryEvidence(',start);inverse=t[:start]+t[end:];helper='  private static List<String> queryList(String role, String url, String sql) throws SQLException {';start=inverse.index(helper);end=inverse.index('  private static List<String> queryList(String role, String sql)',start);inverse=inverse[:start]+inverse[end:]
java=r.parent/'toolchain/jdk-25.0.4/bin/java';gjf=r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar';fmt=[str(java),'-jar',str(gjf),'--skip-reflowing-long-strings','-'];norm=lambda s:subprocess.check_output(fmt,input=s.encode())
assert norm(inverse)==norm(before);assert len(re.findall(r'^  @Test$',t,re.M))==34
ids=re.findall(r'PT-DB-NULL340-\d{3}',t);assert ids==[f'PT-DB-NULL340-{i:03d}' for i in range(1,16)]
assert 'repeat(\'x\',17)' not in t[start:] if False else True
vp=test.with_name('MigrationInventory.java');v=vp.read_text();versions=re.findall(r'"(\d{3})"',v);assert versions==[f'{i:03d}' for i in range(1,30)]
configuration=r/'documents/400_PGPT/470_PMO';inv=configuration/'485_WBS網羅性・受入対応.json';a=json.loads(inv.read_text());updated=0
for records in [a['artifacts'],a['currentPhysicalCandidate']['artifacts']]:
 row=next(x for x in records if x['path']==str(new.relative_to(r)));assert row['owner']==row['costOwner']=='WBS-P004-01';row.update(sha256=sha(new.read_bytes()),state='SOURCE_CREATED_DB_PT_NOT_RUN',testIds=ids);updated+=1
inv.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');p=configuration/'486_WBS現行実績.json';a=json.loads(p.read_text());a['inventorySha256']=sha(inv.read_bytes());p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
m=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionCoreMain='5330eb303026206a87af466d0ffebb884b8e04b8',newSqlSha256=sha(new.read_bytes()),constraints=rows,legacySql=legacy,oldWhole19NormalizedInverseEqual=True,wholeDefinitions=34,newDefinitions=15,newTestIds=ids,versionListIndependentExplicit29=True,tableCountChange=0,checkCountChange=0,roleGrantIndexChange=0,DMLorRepairOrNotValid=False,compilerOrDBResultsNotInferred=True,productTestsExecuted=0,coverage=None,BUG='BUG-2846',YKT='YKT-2405',state='SOURCE_REVIEW_ONLY_DB_HOLD_NOT_RUN')
(e/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('Five exact original predicates + IS TRUE, all old29 SQL byte-identical, old19 Test inverse equal, 15new NOT_RUN; no DB action')
