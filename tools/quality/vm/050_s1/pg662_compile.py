"""New-only current existing ADMIN tooling: pure independent tests before compile."""
import os
from pathlib import Path
import subprocess
from pg662_sources import java, refs, receipt, join, argument_test, compile_script

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def main():
    os.umask(0o077)
    assert (W/'pg661-completed-baseline-v1.exit').read_bytes()==b'0\n'
    for test in ('pg662_sources_test.py','pg662_receipt_test.py','pg570_directory_identity_test.py'):
        subprocess.run(['python3','-B',str(R/test)],check=True)
    root=W/'pg662-bootstrap-tools-v1'
    root.mkdir(mode=0o700)
    for name,raw in {'Pg662BootstrapExisting.java':java(),'Pg662BootstrapArgumentTest.java':argument_test(),
                     'pg662_bootstrap_existing.py':refs(),'pg662_parent_receipt.py':receipt(),
                     'pg662_parent_join.py':join()}.items():
        with (root/name).open('x')as f:
            os.fchmod(f.fileno(),0o400);f.write(raw);f.flush();os.fsync(f.fileno())
    subprocess.run(['/bin/bash','-s'],input=compile_script().encode(),check=True)


if __name__=='__main__':main()
