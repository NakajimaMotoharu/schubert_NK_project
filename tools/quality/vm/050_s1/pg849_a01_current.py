"""Current832 shared Current A01, same new parent/ordinary peers; no restart/oracle rewrite."""
import ast
from pathlib import Path
from pg762_a01_current import code as previous
R=Path(__file__).resolve().parent
def code():
 raw=previous()
 for a,b in(
  ('8d4b68b4f1449932ebe506aaf08e584bbfea8dd2','2a0d5aa392c85a1dc12a1cdb423978e8500895b8'),
  ('a96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289','8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977'),
  ('0.1.0-PG750','0.1.0-PG832'),('PG762','PG849'),('pg762','pg849'),
  ('pg759-watch-private-v1.jsonl','pg843-parent-watch-v1.private.jsonl'),
  ('pg759-observer-v1.exit','pg843-watch-v1.exit'),('pg758-fresh-parent-v1','pg844-external-once-v1'),
  ('pg758-start-v1.exit','pg844-external-once-v1.exit'),('pg760-retention-post-v1.exit','pg842-resume-post-v1.exit'),
 ):
  assert a in raw,a;raw=raw.replace(a,b)
 ast.parse(raw);return raw
if __name__=='__main__':
 env={'__file__':str(R/'pg849_a01_current.py'),'__name__':'current832_A01'}
 exec(compile(code(),'<same current shared driver 832 A01>','exec'),env);env['main']()
