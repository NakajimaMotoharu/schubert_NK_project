"""451 fresh whole-six trigger: SSC239 shared Root IO transport and original RPC budget."""
import subprocess
from pg794_completion_full import source as previous
def source():
    raw = previous()
    assert raw.count('pg794-completion-six-host-v1') == 1
    return raw.replace('pg794-completion-six-host-v1','pg830-manager-six-host-v1').replace('PG794_FULL','PG830_FULL')
if __name__ == '__main__':
    fixed = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash','-s','--',fixed],input=source().encode()).returncode)
