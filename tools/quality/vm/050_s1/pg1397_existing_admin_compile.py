"""Fixed current-source complete ABI/actual Expected and CLI before normal ADMIN oneshot."""
from pathlib import Path
import pg1357_current_bootstrap_compile as previous
R=Path(__file__).resolve().parent

def source():
    raw=previous.source().replace('from pg1356_current_bootstrap_sources import files,SOURCE','from pg1396_existing_admin_sources import files,SOURCE')
    raw=raw.replace('pg1356_current_bootstrap_sources_test.py','pg1396_existing_admin_sources_test.py')
    raw=raw.replace('Pg1356','Pg1396').replace('pg1356','pg1396')
    raw=raw.replace('pg1344-current-bootstrap-before-v1','pg1395-existing-role-normal-post-v1')
    compile(raw,'<qualified current-source existing ADMIN compile>','exec');return raw

if __name__=='__main__':exec(compile(source(),'<new normal ADMIN compiler>','exec'),{'__file__':str(R/'pg1397_existing_admin_compile.py'),'__name__':'__main__'})
