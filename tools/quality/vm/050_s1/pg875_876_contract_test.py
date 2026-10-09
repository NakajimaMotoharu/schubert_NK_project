"""Independent fixed new cohort / unchanged driver / no old success join."""
import ast
from pg875_capture_genuine import payload
from pg876_a01_current import code
g=payload();a=code();ast.parse(g);ast.parse(a)
for text in (g,a):
 for source in ('e01612fcd7f2752df5ae0836b78538fd5e87f120','20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe','0.1.0-PG862','pg872-ordinary-once-v1'):
  assert source in text
 for stale in ('pg843','pg844','pg849','0.1.0-PG832','9c08566fff9945a492eaae25559c3084'):
  assert stale not in text
for value in ('19022204-8a9e-418d-ba2a-9967ff923dc2','2026-10-09T18:28:14.612111Z','cf07d74f-14c7-4223-9eb9-82eb6f0fbd0d','09167719cb0445fea8da5a6fdbaa3b0f','3592151','183192933299','189291','len(m.TABLES)==24','complete_configuration'):
 assert value in g
for value in ('baseline_sha','122dcc4c1be482ac3239325de6fb3d4bec12747d05adce3929c319ab5bdfd71d','approvedDIF001TitleOnly','rawCookieTokenExported'):
 assert value in a
assert "'fullGate':False"in a and 'Current baseline' in __import__('pg876_a01_current').__doc__
print('G875/A876 whole generated cohort/source/current/oracle/no-old-success closure PASS; actualnotrun')
