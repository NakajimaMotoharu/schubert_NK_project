"""New immutable v2 after960 parent-cohort mismatch, preserve v1 and old143 failure."""
import ast
from pathlib import Path
import sys
import pg835_pending_sources as profile
R=Path(__file__).resolve().parent
def bind(raw):
    return raw.replace('pg835-pending-tools-v1','pg835-pending-tools-v2').replace('pg835-pending-codeonly','pg835-pending-codeonly-v2')
def source(mode):
    if mode=='compile':
        raw=(R/'pg835_pending_compile.py').read_text()
        raw=bind(raw).replace("'pg835-'+phase+'-v1.private.log'","'pg835-'+phase+'-v2.private.log'").replace("'pg835-'+phase+'-v1.exit'","'pg835-'+phase+'-v2.exit'").replace('pg835-frozen-v1.safe.json','pg835-frozen-v2.safe.json')
    else:
        raw=bind((R/'pg835_pending_native.py').read_text()).replace('pg835-frozen-v1.safe.json','pg835-frozen-v2.safe.json')
        raw=raw.replace("action+'-v1'","action+'-v2'").replace('pg835-stage-v1.exit','pg835-stage-v2.exit').replace('pg835-fixed-stage-v1','pg835-fixed-stage-v2')
    ast.parse(raw);return raw
if __name__=='__main__':
    mode=sys.argv[1];assert mode in('compile','stage','activate')
    if mode=='compile':
        for name in ('java','refs','before_freeze'):
            previous=getattr(profile,name);setattr(profile,name,lambda previous=previous:bind(previous()))
    exec(compile(source(mode),'<835 newonly corrected cohort v2>', 'exec'),{'__file__':str(R/'pg835_pending_v2.py'),'__name__':'__main__'})
