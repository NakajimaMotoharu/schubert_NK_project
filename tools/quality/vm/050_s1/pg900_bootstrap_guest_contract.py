"""New894v3 actual guest pure normal namespace before any M/A/DB/Ref/credentials."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
def source():
 raw=(R/'pg898_bootstrap_import.py').read_text().replace('pg894-bootstrap-tools-v2','pg894-bootstrap-tools-v3').replace('pg894-stage-v2.exit','pg894-stage-v3.exit').replace('pg894-frozen-v2.safe.json','pg894-frozen-v3.safe.json').replace('pg898-bootstrap-import-v1','pg900-bootstrap-contract-v1')
 marker='for name in modules:importlib.import_module(name)';assert raw.count(marker)==1
 raw=raw.replace(marker,marker+'''
from pg894_db_contract import namespace_valid,peer_counts_valid,peer_query
normal={n:{'metadata':[1,2,0,0,stat.S_IFDIR|(0o755 if n=='runtime-parent'else 0o700),2,0,0,0],'entries':[],'xattrs':[]}for n in ('backup-request','cleanup-request','expiry-request','runtime-parent')}
assert namespace_valid(normal)and not namespace_valid(None)and not namespace_valid({})
assert peer_counts_valid(True,[b'1',b'1',b'0',b'1'])and peer_counts_valid(False,[b'0']*4)
assert "application_name='PG894-bootstrap-guard'"in peer_query(123)
''')
 ast.parse(raw);return raw
if __name__=='__main__':exec(compile(source(),'<900 actual guest pure contracts>','exec'),{'__file__':str(R/'pg900_bootstrap_guest_contract.py'),'__name__':'__main__'})
