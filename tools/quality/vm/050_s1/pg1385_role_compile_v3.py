"""New immutable corrected role ABI; old tool directory stays untouched."""
import pg1375_bootstrap_role_compile_v2 as previous
import pg1380_bootstrap_role_sources_v3 as source

def text():
    raw=previous.text().replace('1374','1380').replace('pg1375-','pg1385-')
    raw=raw.replace('pg1380_bootstrap_role_sources_test.py','pg1385_role_contract_test.py')
    raw=raw.replace('pg1368-bootstrap-fixed-ref-handoff-v1','pg1382-role-fixed-ref-handoff-v1')
    marker="    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();"
    if raw.count(marker)!=1:raise ValueError('one immutable compiler checkpoint required')
    raw=raw.replace(marker,"    if (W/'pg1383-role-sql-parse-v1.exit').read_bytes()!=b'0\\n':raise ValueError('actual corrected peer SQL parse required')\n"+marker)
    compile(raw,'<corrected full role ABI compiler>','exec');return raw

if __name__=='__main__':
    env=dict(previous.previous.__dict__,source=source)
    exec(compile(text(),'<new corrected role compiler>','exec'),env)
    raise SystemExit(env['main']())
