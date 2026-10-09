"""New second93cb/75f genuine885 proof only; first875/old143 never stop authority."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
def module_source():
 raw=(R/'pg877_stop_binding.py').read_text()
 for old,new in (
  ('Pg877','Pg887'),('PG877','PG887'),('pg877','pg887'),('PG875','PG885'),('pg875','pg885'),
  ('19022204-8a9e-418d-ba2a-9967ff923dc2','93cb976e-c36c-47a3-b9e2-0ad28d2996de'),
  ('2026-10-09T18:28:14.612111Z','2026-10-09T19:07:23.894279Z'),
  ('cf07d74f-14c7-4223-9eb9-82eb6f0fbd0d','0dfe0b7f-0e36-4b81-9086-500d896d1187'),
  ('09167719cb0445fea8da5a6fdbaa3b0f','75f48ce36cd740e98a801eede7fdbb7f'),
  ('183192933299','185542282251'),('184992933299','187342282251'),
  ("'189291'","'195974'"),("'3592151'","'3701511'"),
  ('pg870-ordinary-before-v1','pg880-ordinary-before-v1'),
 ):
  assert old in raw,old;raw=raw.replace(old,new)
 ast.parse(raw);return raw
def namespace():
 env={'__file__':str(R/'pg887_stop_binding.py'),'__name__':'genuine_second_fixed'};exec(compile(module_source(),'<887 whole second source>','exec'),env);return env
def bindings(proof):return namespace()['bindings'](proof)
def generate(proof):return namespace()['generate'](proof)
