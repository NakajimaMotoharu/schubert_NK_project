"""Consolidated necessary whole run after selected34; four-counter closure remains unmet."""
import subprocess
from pg1011_stream_full import source as previous

def source():
    raw=previous();assert raw.count('pg1011-stream-six-host-v1')==1
    return raw.replace('pg1011-stream-six-host-v1','pg1018-stream-six-host-v2').replace('PG1011_FULL','PG1018_FULL')

if __name__=='__main__':
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash','-s','--',head],input=source().encode()).returncode)
