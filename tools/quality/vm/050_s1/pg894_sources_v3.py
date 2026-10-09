"""New-only v3 after global-contract recurrence; never alter frozen v1/v2."""
import ast
from pg894_sources_v2 import files as previous,SOURCE
def files(baseline_sha):
 values=previous(baseline_sha)
 for name,raw in list(values.items()):
  raw=raw.replace('pg894-bootstrap-tools-v2','pg894-bootstrap-tools-v3')
  if name=='Pg894BootstrapExisting.java':
   old='"/var/lib/pgpt-s1-preservation/pg894-bootstrap-"+(MODE.equals("verify")?"verify":"existing")+"-v2"';assert raw.count(old)==1
   raw=raw.replace(old,old.replace('"-v2"','"-v3"'))
  if name=='pg894_bootstrap_existing.py':
   old="'/var/lib/pgpt-s1-preservation/pg894-bootstrap-'+('verify'if MODE=='verify'else'existing')+'-v2'";assert raw.count(old)==1
   raw=raw.replace(old,old.replace("'-v2'","'-v3'"))
  if name.endswith('.py'):ast.parse(raw)
  values[name]=raw
 return values
