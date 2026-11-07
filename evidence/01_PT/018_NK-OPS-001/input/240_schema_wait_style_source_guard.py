"""Independent exact source transform for two deadlines and four styles; no Product execution."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,re,subprocess
R=Path(__file__).resolve().parents[4];OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22680-schema-source-transform-guard-v1'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 assert not OUT.exists();original=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22654-schema-wait-original-v1';op=json.loads((original/'manifest.json').read_bytes());p=original/'SchemaHistoryAdmissionTest.java';assert hashlib.sha256(p.read_bytes()).hexdigest()==op['sourceSha256'];current=R/op['sourcePath'];text=p.read_text();assert text.count('task.get()')==text.count('barrier.await()')==1;text=text.replace('task.get()','task.get(5, java.util.concurrent.TimeUnit.SECONDS)').replace('barrier.await()','barrier.await(5, java.util.concurrent.TimeUnit.SECONDS)');masker=R/'evidence/01_PT/018_NK-OPS-001/input/219_test_wait_source_inventory_independent_post.py';lexer=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';mask=module('owned_schema_mask',masker).mask;tokens=module('owned_schema_tokens',lexer).java_tokens;hits=list(re.finditer(r'\b(?:SCHEMA|FIRST)\b',mask(text)));counts={k:sum(x.group()==k for x in hits) for k in ['SCHEMA','FIRST']};assert counts==dict(SCHEMA=10,FIRST=5)
 for x in reversed(hits):text=text[:x.start()]+{'SCHEMA':'SCHEMA_ROW','FIRST':'FIRST_ROW'}[x.group()]+text[x.end():]
 quoted='"\\"schubert_meta\\""';assert text.count(quoted)==7;text=text.replace(quoted,'SCHEMA_SCRIPT');text=text.replace('  private static final String FIXTURE_SCHEMA_E38F1889','  private static final String SCHEMA_SCRIPT = "\\"schubert_meta\\"";\n  private static final String FIXTURE_SCHEMA_E38F1889',1);assert text.count('boolean next = ++index < rows.size();')==1;text=text.replace('boolean next = ++index < rows.size();','index++;\n                    boolean next = index < rows.size();');actual=current.read_text();assert tokens(text)==tokens(actual)
 for bad in [actual.replace('barrier.await(5, java.util.concurrent.TimeUnit.SECONDS)','barrier.await()',1),actual.replace('task.get(5, java.util.concurrent.TimeUnit.SECONDS)','task.get()',1),actual.replace('"SCHEMA"','"WRONG_SCHEMA"',1)]:assert tokens(text)!=tokens(bad)
 # ++index expression and separate increment compare the identical updated signed32 value;
 # the selected Probe index is a private int and all size reads remain after increment.
 assert 'int index = -1;' in actual;checks=0
 for before in [-2147483648,-1,0,2147483647]:
  for size in [0,1,2]:
   updated=((before+1+2147483648)%4294967296)-2147483648;oldvalue=updated<size;newindex=updated;newvalue=newindex<size;assert oldvalue==newvalue;checks+=1
 OUT.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),productTestsExecuted=0,waitDeadlineAdditions=2,fieldIdentifierRenames=counts,quotedLiteralSites=7,assignmentExpansionSites=1,allOtherJavaTokensAndOracleValuesUnchanged=True,negativeGuards=3,primitiveIntBoundaryChecks=checks,originalTestSha256=op['sourceSha256'],currentTestSha256=hashlib.sha256(current.read_bytes()).hexdigest(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command=['python3','-B',str(Path(__file__).relative_to(R))],helperHashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [masker,lexer]},verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()));(OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,deadlines=2,negative=3,oracleUnchanged=True)))
if __name__=='__main__':main()
