"""One necessary whole-six campaign after new streaming PT source.
No selector/no-tests overrides or old run reuse; exact known PG926 quality CLI.
"""
import subprocess
from pg926_body_full import source as previous

def source():
    raw=previous();assert raw.count('pg926-body-six-host-v1')==1
    return raw.replace('pg926-body-six-host-v1','pg1011-stream-six-host-v1').replace('PG926_FULL','PG1011_FULL')

if __name__=='__main__':
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    raise SystemExit(subprocess.run(['/bin/bash','-s','--',head],input=source().encode()).returncode)
