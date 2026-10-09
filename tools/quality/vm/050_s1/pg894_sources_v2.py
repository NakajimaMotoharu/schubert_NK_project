"""Only new v2 tools/save modes; preserve old v1 partial and its failure evidence."""
import ast
from pathlib import Path
from pg894_bootstrap_sources import files as previous,SOURCE
R=Path(__file__).resolve().parent
def files(baseline_sha):
 values=previous(baseline_sha)
 for name,raw in list(values.items()):
  raw=raw.replace('pg894-bootstrap-tools-v1','pg894-bootstrap-tools-v2')
  if name=='Pg894BootstrapExisting.java':
   old='"/var/lib/pgpt-s1-preservation/pg894-bootstrap-"+(MODE.equals("verify")?"verify":"existing")+"-v1"';assert raw.count(old)==1
   raw=raw.replace(old,old.replace('"-v1"','"-v2"'))
  if name=='pg894_bootstrap_existing.py':
   old="'/var/lib/pgpt-s1-preservation/pg894-bootstrap-'+('verify'if MODE=='verify'else'existing')+'-v1'";assert raw.count(old)==1
   raw=raw.replace(old,old.replace("'-v1'","'-v2'"))
  if name.endswith('.py'):ast.parse(raw)
  values[name]=raw
 return values
