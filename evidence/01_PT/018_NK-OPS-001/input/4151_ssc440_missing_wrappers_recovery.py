"""Recover only absent wrapper files after preserving producer failure; do not replay fixture producer."""
from pathlib import Path
import ast
b=Path('evidence/01_PT/018_NK-OPS-001/input');tree=ast.parse((b/'4145_ssc440_fixture_v2_prepare.py').read_text());loop=next(n for n in tree.body if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and len(n.target.elts)==3);rows=ast.literal_eval(loop.iter)
for src,dst,changes in rows:
 text=(b/src).read_text()
 for old,new in changes.items():assert old in text;text=text.replace(old,new)
 path=b/dst
 if path.exists():assert path.read_text()==text
 else:path.open('x').write(text)
print('all three exact wrappers recovered, existing results retained')
