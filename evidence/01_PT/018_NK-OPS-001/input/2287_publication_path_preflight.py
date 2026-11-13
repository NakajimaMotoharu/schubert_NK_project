"""Read-only string predicate preflight; remove protected names before any file access.
No source/admission change, file contents, protected stats or staging/commit occur here.
"""
from pathlib import Path
import ast,json,subprocess
R=Path.cwd();tool=R.parent/'pgpt-runs/PG379/publish_characterization_delta.py';tree=ast.parse(tool.read_text());candidates=[n for n in ast.walk(tree) if isinstance(n,ast.Assert) and {'name','any'} <= {x.id for x in ast.walk(n.test) if isinstance(x,ast.Name)}];assert len(candidates)==1;a=candidates[0];assert {n.id for n in ast.walk(a.test) if isinstance(n,ast.Name)}<={'name','n','any'}
for n in ast.walk(a.test):
 if isinstance(n,ast.Call):
  f=n.func;assert (isinstance(f,ast.Name) and f.id=='any') or (isinstance(f,ast.Attribute) and isinstance(f.value,ast.Name) and f.value.id in ('name','n') and f.attr in ('startswith','endswith'))
raw=subprocess.check_output(['git','diff','--name-only','-z'],cwd=R)+subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=R);names=set(raw.decode().split('\0'))-{''}-{'tools/quality/architecture/SnapshotKeyCloseWitness.java','tools/quality/pg9892_snapshot_key_close_witness.py'};expr=compile(ast.Expression(a.test),'reviewed-pure-string-path-predicate','eval');unknown=[n for n in sorted(names) if not eval(expr,{'__builtins__':{'any':any},'name':n})];print(json.dumps(dict(actualExit=0,scope='NAME_ONLY_NO_CONTENT_NO_STAGE',candidateCount=len(names),unsupported=unknown),ensure_ascii=False))

if unknown:raise SystemExit(1)
