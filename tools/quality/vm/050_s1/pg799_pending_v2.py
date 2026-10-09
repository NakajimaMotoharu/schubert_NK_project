"""New-only recipe after946: capture all ten declarations before guard, preserve old slot."""
from pathlib import Path
import sys
import pg799_pending_sources as profile

R=Path(__file__).resolve().parent

def bind(raw):return raw.replace('pg799-pending-tools-v1','pg799-pending-tools-v2').replace('pg799-pending-codeonly','pg799-pending-codeonly-v2')

def compile_source():
 raw=(R/'pg799_pending_compile.py').read_text()
 return bind(raw).replace("'pg799-'+phase+'-v1.private.log'","'pg799-'+phase+'-v2.private.log'").replace("'pg799-'+phase+'-v1.exit'","'pg799-'+phase+'-v2.exit'").replace('pg799-frozen-v1.safe.json','pg799-frozen-v2.safe.json')

def native_source():
 from pg799_pending_native import source
 raw=bind(source()).replace('pg799-frozen-v1.safe.json','pg799-frozen-v2.safe.json')
 return raw.replace("action+'-v1'","action+'-v2'").replace('pg799-stage-v1.exit','pg799-stage-v2.exit').replace('pg799-fixed-stage-v1','pg799-fixed-stage-v2')

if __name__=='__main__':
 mode=sys.argv[1];assert mode in('compile','stage','activate')
 if mode=='compile':
  for name in('java','refs','before_freeze'):
   previous=getattr(profile,name);setattr(profile,name,lambda previous=previous:bind(previous()))
  raw=compile_source()
 else:raw=native_source();sys.argv=[sys.argv[0],mode]
 exec(compile(raw,'<799 new946 immutable v2>', 'exec'),{'__file__':str(R/'pg799_pending_v2.py'),'__name__':'__main__'})
