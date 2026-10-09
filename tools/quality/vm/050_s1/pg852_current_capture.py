"""Current832 failed PID1 after RootDONE: full24/private owners, no stop/revoke."""
import ast,inspect
import pg784_stopped_baseline as transport
from pg812_current_capture import PAYLOAD as previous
from pg841_resume import bind
def payload():
 raw=previous.replace('pg805-resume-tools-v2','pg805-resume-tools-v1')
 raw=bind(raw).replace('pg812-current-timeout-v4','pg852-doneafter-timeout-v1')
 for old,new in(
  ('3342473','3506798'),('6220dab5a87945d2bb144cb9e14f5f14','eeb1b35ca3214176adae5d45bb6432ab'),
  ('3344741','3507964'),('02ae69dca0514d8c917831eee3ca82b6','8c46100f289f47b9a24d2c12bd443ba2'),
  ('3350579','3509997'),('42e945fbd2894199b7dfca297c989627','87dd86b0f2c243198a05ae36903fdefa'),
  ('3158873','3427249'),('cb2f7a6c4beb4420a0e96adb65fb6f11','9a576ea327854479a3196fe41b2c0a61'),
  ('7ea672e8a76c4a4a8a7994652366a4cc','9c08566fff9945a492eaae25559c3084'),
 ):
  assert old in raw,old;raw=raw.replace(old,new)
 ast.parse(raw);return raw
if __name__=='__main__':
 raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg852-doneafter-timeout-v1');context={**transport.__dict__,'PAYLOAD':payload()}
 exec(compile(raw,'<852 actual completed-original failed-parent fullcapture>','exec'),context);context['main']()
