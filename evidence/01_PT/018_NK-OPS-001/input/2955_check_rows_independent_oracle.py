"""Source-DDL oracle only; never imports product code, driver, DB, Current data or SQL evaluator."""
from pathlib import Path
import re,json,hashlib,datetime
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';ddl=r/'src/schubert-nk-api/src/main/resources/db/migration/V002__account_session_and_master_tables.sql';update=ddl.with_name('V029__strict_nullable_compound_checks.sql');base=ddl.read_text();changed=update.read_text();manual=json.loads((i/'2937_constraint_scope_independent_oracle.json').read_text())['tables']
def parenthesized(text,start):
 assert text[start]=='(';depth=0;quoted=False;pos=start
 while pos<len(text):
  char=text[pos]
  if quoted:
   if char=="'":
    if pos+1<len(text) and text[pos+1]=="'":pos+=2;continue
    quoted=False
  elif char=="'":quoted=True
  elif char=='(':depth+=1
  elif char==')':
   depth-=1
   if depth==0:return text[start+1:pos],pos+1
  pos+=1
 raise ValueError('unbalanced source expression')
# Literal tests are authoring parser guards, not application PT or DB evaluation.
examples=[("(a AND (b OR c))tail",'a AND (b OR c)'),("(x = '(' AND y = ')')", "x = '(' AND y = ')'"),("(x = 'it''s)(')", "x = 'it''s)('")]
for text,expected in examples:assert parenthesized(text,0)[0]==expected
for text in ['(x','(x = \'broken)']:
 try:parenthesized(text,0)
 except ValueError:pass
 else:raise AssertionError('unterminated expression accepted')
tables={};sourceRefs=[]
for table,rows in manual.items():
 marker='CREATE TABLE schubert.'+table+' (';at=base.index(marker)+len(marker)-1;block,_=parenthesized(base,at);expressions={}
 for match in re.finditer(r'\bCONSTRAINT\s+(\w+)\s+CHECK\s*\(',block):
  name=match.group(1);expr,_=parenthesized(block,match.end()-1);assert name not in expressions;expressions[name]=expr
 assert set(expressions)=={row[0] for row in rows if row[1]=='c'}
 if table=='media_assets':
  match=re.search(r'ADD CONSTRAINT ck_media_assets_pair CHECK\s*\(',changed);assert match;expr,_=parenthesized(changed,match.end()-1);assert expr.rstrip().endswith('IS TRUE');expressions['ck_media_assets_pair']=expr
 tables[table]=dict(checks=expressions,query='SELECT count(*) FROM schubert.'+table+' WHERE ('+' AND '.join('('+expr+')' for _,expr in sorted(expressions.items()))+') IS FALSE')
assert [len(v['checks']) for v in tables.values()]==[3,9,8,10,15,2] and sum(len(v['checks']) for v in tables.values())==47
for p in [ddl,update]:sourceRefs.append(dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
# SQL three-valued AND: a FALSE dominates NULL, otherwise NULL propagates; CHECK only rejects FALSE.
truth=[dict(inputs=[True,None],conjunction=None,violations=0),dict(inputs=[False,None],conjunction=False,violations=1),dict(inputs=[True,True],conjunction=True,violations=0),dict(inputs=[None],conjunction=None,violations=0)]
out=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceDdl=sourceRefs,tables=tables,queries=[v['query'] for v in tables.values()],namedChecks=47,expectedCounts=[0]*6,negativeReturnedCountVectors=[-1,1,9223372036854775807,None],sqlCheckUnknownRemainsAllowed=True,threeValuedIndependentTruthVectors=truth,authoringParserGuardExamples=5,manual47NamesMatchSourceDdl=True,productionMethodsCalled=0,actualSqlEvaluatorOrDatabaseOperations=0,checkExpressionCatalogNotQualified=True,technicalSource='https://www.postgresql.org/docs/18/ddl-constraints.html')
(i/'2955_check_rows_independent_oracle.json').open('x').write(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,checks=47,tableCounts=[len(v['checks']) for v in tables.values()],v029PairApplied=True,authoringGuards=5,productTestsExecuted=0))
