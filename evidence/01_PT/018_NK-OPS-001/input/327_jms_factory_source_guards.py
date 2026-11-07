"""Two named char values and controller-key correction only; independent source/AST guards."""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,json
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';OLD=B/'evidence/PG23040-jms-factory-tool-failure-v1';O=B/'evidence/PG23044-jms-factory-source-guards-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sp=importlib.util.spec_from_file_location('jms_factory_guard_tokens',R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py');lib=importlib.util.module_from_spec(sp);sp.loader.exec_module(lib);tok=lib.java_tokens
def inverse(text):
 t=tok(text)
 for name,value in [('EVENT_KIND',"'E'"),('RESPONSE_KIND',"'S'")]:
  decl=tok('private static final char '+name+' = '+value+';');indices=[i for i in range(len(t)-len(decl)+1) if t[i:i+len(decl)]==decl];assert len(indices)==1;i=indices[0];t=t[:i]+t[i+len(decl):];assert t.count(name)==1;t=[value if v==name else v for v in t]
 return t
def tuple_indices(text):return sum(isinstance(n,ast.Subscript) and isinstance(n.slice,ast.Tuple) for n in ast.walk(ast.parse(text)))
def main():
 assert not O.exists();old=OLD/'JmsMessageFactoryPortTest.java';p=R/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/JmsMessageFactoryPortTest.java';actual=p.read_text();assert inverse(actual)==tok(old.read_text());negative=0
 for symbol,value in [('EVENT_KIND',"'E'"),('RESPONSE_KIND',"'S'")]:
  bad=actual.replace(symbol+' = '+value+';',symbol+" = 'X';",1)
  try:ok=inverse(bad)==tok(old.read_text())
  except AssertionError:ok=False
  assert not ok;negative+=1
 tool=B/'input/323_jms_factory_port_qualifier.py';legacy=(OLD/'original-qualifier.py').read_text();current=tool.read_text();assert tuple_indices(legacy)==3 and tuple_indices(current)==0;assert "for mod in ['protocol','api']" in current and "for module in ['protocol','api']" in current and "nm['jars']['api']['path']" in current;assert "['reports']['protocol','api']" not in current;O.mkdir();m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),previousFailure=dict(path=str((OLD/'manifest.json').relative_to(R)),sha256=sha(OLD/'manifest.json')),testSource=dict(path=str(p.relative_to(R)),sha256=sha(p)),toolSource=dict(path=str(tool.relative_to(R)),sha256=sha(tool)),namedCharConditions=2,allOtherJavaTokensFixturesAndOraclesUnchanged=True,charMutationNegatives=negative,legacyInvalidTupleIndices=3,currentInvalidTupleIndices=0,protocolApiDependencyAndStaticReportListsPreserved=True,targetJarExplicitApi=True,productTestsExecuted=0);(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,charConditions=2,negative=negative,legacyTuple3Rejected=True)))
if __name__=='__main__':main()
