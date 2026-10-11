"""Current complete repository type imports; new-only artifact namespace."""
import inspect
import pg1373_bootstrap_role_compile as previous
import pg1374_bootstrap_role_sources_v2 as source

def text():
    raw=inspect.getsource(previous.main)
    raw=raw.replace('pg1372-bootstrap-role-tools-v1','pg1374-bootstrap-role-tools-v2').replace('Pg1372','Pg1374')
    raw=raw.replace("(R/'Pg1374BootstrapRoleArgumentTest.java').read_text()","(R/'Pg1372BootstrapRoleArgumentTest.java').read_text().replace('Pg1372','Pg1374').replace('PG1372','PG1374')")
    raw=raw.replace('pg1373-role-byte-oracle-v1','pg1375-role-byte-oracle-v2').replace('pg1373-','pg1375-').replace('pg1375-frozen-v1','pg1375-frozen-v2')
    raw=raw.replace('pg1372_bootstrap_role_sources_test.py','pg1374_bootstrap_role_sources_test.py')
    compile(raw,'<new-only imported complete Role main compiler>','exec');return raw

if __name__=='__main__':
    env=dict(previous.__dict__,source=source)
    exec(compile(text(),'<actual new Role management compiler>','exec'),env)
    raise SystemExit(env['main']())
