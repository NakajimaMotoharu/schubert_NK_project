"""SSC267 fresh three-suite PT after design-only PR108; old failures retained."""
import inspect
import hashlib
from pathlib import Path
import pg1466_server_dispatch as dispatch


def main():
    template=Path(__file__).with_name('pg1466_server_selected.py').read_text()
    raw=template.replace('PG1466','PG1471')
    assert "'SCHUBERT_AUTH_DIAGNOSTICS_DIR':str(OUT/'tmp')" in raw
    compile(raw,'<corrected independent auth/static selected>','exec')
    body=inspect.getsource(dispatch.main).replace('PG1466','PG1471').replace('pg1466','pg1471')
    body=body.replace("helper=ROOT/'tools/quality/pg1471_server_selected.py'",
                      "helper=out/'pg1471_server_selected.py'\n    helper.write_text(raw)")
    body=body.replace("(helper,REMOTE+'/tools/pg1471_server_selected.py'),\n           (shell,REMOTE+'/tools/shellcheck-0.11.0')",
                      "(helper,REMOTE+'/tools/pg1471_server_selected.py')")
    body=body.replace("assert code==0 and all(h in status for h in hashes.values()) and 'version: 0.11.0' in status",
       "assert code==0 and all(h in status for h in hashes.values()) and 'version: 0.11.0' in status\n    code,status=run('sha256sum '+REMOTE+'/tools/shellcheck-0.11.0');assert code==0 and hashlib.sha256(shell.read_bytes()).hexdigest() in status")
    assert "(shell,REMOTE+'/tools/shellcheck-0.11.0')" not in body
    namespace={**dispatch.__dict__,'raw':raw}
    exec(compile(body,'<fresh corrected dispatch>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
