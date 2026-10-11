"""Fresh diagnostic after BUG1109; reuse hash-qualified ShellCheck, no VM work."""
import inspect
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg1466_server_dispatch as dispatch
from lan_server import copy,run


def main():
    template=Path(__file__).with_name('pg1466_server_selected.py').read_text()
    raw=template.replace('PG1466','PG1467').replace(
        "SUITES = ['InspectorDeploymentTest','ApplicationServiceUnitTest','AuthenticationServiceTest']",
        "SUITES = ['AuthenticationServiceTest']")
    assert "SUITES = ['AuthenticationServiceTest']" in raw and "'SCHUBERT_AUTH_DIAGNOSTICS_DIR':str(OUT/'tmp')" in raw
    compile(raw,'<new auth diagnostic server>','exec')
    body=inspect.getsource(dispatch.main).replace('PG1466','PG1467').replace('pg1466','pg1467')
    body=body.replace("helper=ROOT/'tools/quality/pg1467_server_selected.py'",
                      "helper=out/'pg1467_server_selected.py'\n    helper.write_text(raw)")
    body=body.replace("(helper,REMOTE+'/tools/pg1467_server_selected.py'),\n           (shell,REMOTE+'/tools/shellcheck-0.11.0')",
                      "(helper,REMOTE+'/tools/pg1467_server_selected.py')")
    # Existing tool is immutable reuse, not copy/hotpatch or a new source claim.
    body=body.replace("assert code==0 and all(h in status for h in hashes.values()) and 'version: 0.11.0' in status",
       "assert code==0 and all(h in status for h in hashes.values()) and 'version: 0.11.0' in status\n    code,status=run('sha256sum '+REMOTE+'/tools/shellcheck-0.11.0');assert code==0 and hashlib.sha256(shell.read_bytes()).hexdigest() in status")
    assert "(shell,REMOTE+'/tools/shellcheck-0.11.0')" not in body
    namespace={**dispatch.__dict__,'raw':raw}
    exec(compile(body,'<fresh diagnostic dispatch>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
