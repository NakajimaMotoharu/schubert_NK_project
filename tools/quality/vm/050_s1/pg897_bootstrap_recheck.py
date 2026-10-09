"""Fresh full read-only reauthentication after896; do not repeat start or handoff."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
def source():
 raw=(R/'pg895_bootstrap_before.py').read_text()
 raw=raw.replace('pg895-bootstrap-before-v1','pg897-bootstrap-before-v1')
 marker="snapshot_raw=json.dumps(value,sort_keys=True).encode()"
 assert raw.count(marker)==1
 raw=raw.replace(marker,marker+"\\nrequire(hashlib.sha256(snapshot_raw).hexdigest()=='2a4f222e0d9759ac7c764f3e3c581a9774ad74de01971f15bf28e759dbc04e6e')")
 ast.parse(raw);return raw
if __name__=='__main__':
 exec(compile(source(),'<897 current full reauthentication>','exec'),{'__file__':str(R/'pg897_bootstrap_recheck.py'),'__name__':'__main__'})
