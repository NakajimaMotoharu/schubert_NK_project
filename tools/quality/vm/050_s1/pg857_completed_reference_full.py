"""451 fresh whole-six: SSC240 completed reference adapters; no old source result reuse."""
import subprocess
from pg830_manager_full import source as previous
def source():
    raw=previous();assert raw.count('pg830-manager-six-host-v1')==1
    return raw.replace('pg830-manager-six-host-v1','pg857-completed-reference-six-host-v1').replace('PG830_FULL','PG857_FULL')
if __name__=='__main__':
    fixed=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash','-s','--',fixed],input=source().encode()).returncode)
