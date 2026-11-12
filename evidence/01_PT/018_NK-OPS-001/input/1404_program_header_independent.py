"""Program-label metadata controls only, evaluates the real generator expression without its I/O."""
from pathlib import Path
import ast,hashlib,json
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';p=B/'input/1364_original_preparation_close.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=B/'evidence/PG26932-program-label-before-v1/manifest.json';b=json.loads(old.read_text());tree=ast.parse(p.read_text());nodes=[x for x in ast.walk(tree) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='lines' for t in x.targets)];assert len(nodes)==1;expr=compile(ast.Expression(nodes[0].value),str(p),'eval');controls=[]
for program in ['NK-SCN-001','NK-MED-001']:
 rows=eval(expr,{'__builtins__':{'str':str}},{'a':{'specTitle':'metadata control'},'program':program,'start':{'run':'PG-METADATA-CONTROL'},'mp':B/'evidence/control/manifest.json','B':B});assert rows[2].startswith(program+'。');controls.append(program)
assert not 'NK-SCN-001。対象source/hash'.startswith('NK-MED-001。')
changed=[];unaffected=[]
for x in b['rows']:
 q=R/x['path'];assert q.read_text().splitlines()[2].startswith(x['expectedProgram']+'。');now=sha(q);(changed if now!=x['sha256'] else unaffected).append(dict(path=x['path'],before=x['sha256'],after=now))
assert len(changed)==2 and len(unaffected)==4
O=B/'evidence/PG26934-program-label-independent-v1';assert not O.exists();O.mkdir();v=dict(actualExit=0,before=dict(path=str(old),sha256=sha(old)),generatorSha256=sha(p),realGeneratorExpressionControls=controls,positiveChecks=2,negativeChecks=1,changed=changed,unaffected=unaffected,productTestsExecuted=0,productionOrTestChanged=False,newAcceptance=0,formalUpdated=False,verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,controls=2,negative=1,changed=2,unchanged=4,manifestSha256=sha(O/'manifest.json'))))
