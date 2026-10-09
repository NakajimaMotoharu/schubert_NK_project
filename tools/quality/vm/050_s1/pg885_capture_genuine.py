"""New93cb/75f genuine only; actual wrapper882 failure is retained separately."""
import ast
from pathlib import Path
from pg875_capture_genuine import payload as previous
R=Path(__file__).resolve().parent
def payload():
 raw=previous()
 for old,new in (
  ('19022204-8a9e-418d-ba2a-9967ff923dc2','93cb976e-c36c-47a3-b9e2-0ad28d2996de'),
  ('2026-10-09T18:28:14.612111Z','2026-10-09T19:07:23.894279Z'),
  ('cf07d74f-14c7-4223-9eb9-82eb6f0fbd0d','0dfe0b7f-0e36-4b81-9086-500d896d1187'),
  ('3592151','3701511'),('09167719cb0445fea8da5a6fdbaa3b0f','75f48ce36cd740e98a801eede7fdbb7f'),
  ('189291','195974'),('183192933299','185542282251'),
  ('pg872-ordinary-once-v1','pg882-ordinary-once-v1'),('pg870-ordinary-before-v1','pg880-ordinary-before-v1'),
  ('a8c6c5d4dca5c02b1ae6b3ee797ba87d129b0dc4851ae31f6e7609ebfd31d980','ef5e9a5df932069c7681dbe119cebf26ecf5203bca42cd5002e848e2048f2198'),
  ("len(baseline['rows']['schubert.batch_runs'])==564","len(baseline['rows']['schubert.batch_runs'])==574"),
  ('pg875-completed-readonly-v1','pg885-completed-readonly-v1'),('PG875-completed-readonly-v1','PG885-completed-readonly-v1'),
 ):
  assert old in raw,old;raw=raw.replace(old,new)
 ast.parse(raw);return raw
def source():
 raw=(R/'pg875_capture_genuine.py').read_text();a=raw.index("if __name__=='__main__':")
 raw=raw[a:].replace('pg875','pg885').replace('PG875','PG885').replace('pg871','pg881').replace('pg876','pg884')
 return raw
if __name__=='__main__':
 import datetime,hashlib,json,os,subprocess
 from pg875_capture_genuine import W,P
 exec(compile(source(),'<885 new93cb trueDONE>','exec'),globals())
