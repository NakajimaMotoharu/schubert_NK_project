"""Current baseline A01 on new0916 current862; old849 result never reused."""
import ast
from pathlib import Path
from pg849_a01_current import code as previous
R=Path(__file__).resolve().parent
def code():
 raw=previous()
 for old,new in (('PG849','PG876'),('pg849','pg876'),('pg843','pg871'),('pg844-external-once-v1','pg872-ordinary-once-v1'),('2a0d5aa392c85a1dc12a1cdb423978e8500895b8','e01612fcd7f2752df5ae0836b78538fd5e87f120'),('8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977','20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'),('0.1.0-PG832','0.1.0-PG862')):
  assert old in raw;raw=raw.replace(old,new)
 marker="assert (W/'pg842-resume-post-v1.exit').read_bytes()==b'0\\n'";assert raw.count(marker)==1
 raw=raw.replace(marker,"assert json.loads((W/'pg870-ordinary-before-v1.safe.json').read_bytes())['actualExit']==0")
 ast.parse(raw);return raw
if __name__=='__main__':
 env={'__file__':str(R/'pg876_a01_current.py'),'__name__':'current862_A01'}
 exec(compile(code(),'<new current862 shared driver A01>','exec'),env);env['main']()
