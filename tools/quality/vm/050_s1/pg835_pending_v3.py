"""New-only after962 argv source mismatch; verify existing candidate RO, never freeze twice."""
import ast
from pathlib import Path
import sys
import pg835_pending_sources as profile
from pg835_pending_v2 import source as previous
R=Path(__file__).resolve().parent
def bind(raw):
    return raw.replace('pg835-pending-tools-v1','pg835-pending-tools-v3').replace('pg835-pending-codeonly','pg835-pending-codeonly-v3')
def java(raw):
    raw=bind(raw)
    marker='phase="FIXED_FREEZE";Pg387TrustedDeployment.freezeCandidate();'
    assert raw.count(marker)==1
    return raw.replace(marker,'phase="EXISTING_FIXED_FREEZE";require(Files.readSymbolicLink(Path.of("/proc/self/ns/mnt")).equals(Files.readSymbolicLink(Path.of("/proc/1/ns/mnt"))) && Files.getFileStore(NEXT).isReadOnly());')
def source(mode):
    raw=previous(mode).replace('pg835-pending-tools-v2','pg835-pending-tools-v3').replace('pg835-pending-codeonly-v2','pg835-pending-codeonly-v3').replace('pg835-frozen-v2.safe.json','pg835-frozen-v3.safe.json')
    raw=raw.replace("'pg835-'+phase+'-v2.private.log'","'pg835-'+phase+'-v3.private.log'").replace("'pg835-'+phase+'-v2.exit'","'pg835-'+phase+'-v3.exit'").replace("action+'-v2'","action+'-v3'").replace('pg835-stage-v2.exit','pg835-stage-v3.exit').replace('pg835-fixed-stage-v2','pg835-fixed-stage-v3')
    ast.parse(raw);return raw
if __name__=='__main__':
    mode=sys.argv[1];assert mode in('compile','stage','activate')
    if mode=='compile':
        old=profile.java;profile.java=lambda:java(old())
        for name in ('refs','before_freeze'):
            old=getattr(profile,name);setattr(profile,name,lambda old=old:bind(old()))
    exec(compile(source(mode),'<835 corrected candidate source v3>', 'exec'),{'__file__':str(R/'pg835_pending_v3.py'),'__name__':'__main__'})
