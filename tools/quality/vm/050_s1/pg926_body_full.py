"""451 consolidated changed-main API body/daemon UID group fresh six regression."""
import subprocess
from pg915_snapshot_full import source as previous
def source():
    raw=previous();assert raw.count('pg915-snapshot-six-host-v1')==1
    return raw.replace('pg915-snapshot-six-host-v1','pg926-body-six-host-v1').replace('PG915_FULL','PG926_FULL')
if __name__=='__main__':
    fixed=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash','-s','--',fixed],input=source().encode()).returncode)
