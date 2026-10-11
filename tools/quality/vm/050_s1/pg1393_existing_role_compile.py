"""Fresh immutable read-only existing-role verification ABI with sent phase matrix."""
import pg1385_role_compile_v3 as previous
import pg1392_existing_role_sources as source

def text():
    raw=previous.text().replace('1380','1392').replace('pg1385-','pg1393-')
    raw=raw.replace('pg1385_role_contract_test.py','pg1392_existing_role_sources_test.py')
    raw=raw.replace('pg1382-role-fixed-ref-handoff-v1','pg1390-prepared-role-fixed-pair-v1')
    compile(raw,'<existing-role read-only full ABI compiler>','exec');return raw

if __name__=='__main__':
    env=dict(previous.previous.previous.__dict__,source=source)
    exec(compile(text(),'<new existing-role verification compiler>','exec'),env)
    raise SystemExit(env['main']())
