"""New-only after963 partial v3 assembly; no private v3 overwrite or freeze replay."""
from pathlib import Path
import sys
import pg835_pending_sources as profile
from pg835_pending_v3 import source as previous,java
R=Path(__file__).resolve().parent
def bind(raw):
    return raw.replace('pg835-pending-tools-v1','pg835-pending-tools-v4').replace('pg835-pending-codeonly','pg835-pending-codeonly-v4')
def source(mode):
    return previous(mode).replace('pg835-pending-tools-v3','pg835-pending-tools-v4').replace('pg835-pending-codeonly-v3','pg835-pending-codeonly-v4').replace('pg835-frozen-v3','pg835-frozen-v4').replace("'-v3.private.log'","'-v4.private.log'").replace("'-v3.exit'","'-v4.exit'").replace("action+'-v3'","action+'-v4'").replace('pg835-stage-v3','pg835-stage-v4').replace('pg835-fixed-stage-v3','pg835-fixed-stage-v4')
if __name__=='__main__':
    mode=sys.argv[1];assert mode in('compile','stage','activate')
    if mode=='compile':
        old=profile.java;profile.java=lambda old=old:java(old()).replace('pg835-pending-tools-v3','pg835-pending-tools-v4').replace('pg835-pending-codeonly-v3','pg835-pending-codeonly-v4')
        for name in ('refs','before_freeze'):
            old=getattr(profile,name);setattr(profile,name,lambda old=old:bind(old()))
    exec(compile(source(mode),'<835 corrected closure newonly v4>', 'exec'),{'__file__':str(R/'pg835_pending_v4.py'),'__name__':'__main__'})
