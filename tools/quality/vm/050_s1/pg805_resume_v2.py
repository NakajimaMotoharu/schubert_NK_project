"""948 new-only v2 after failed compilation; original runtime remains untouched."""
from pathlib import Path
import sys
import pg805_resume_sources as profile
import pg805_resume_compile as compiler
from pg805_resume_native import source as native
R=Path(__file__).resolve().parent

def bind(raw):return raw.replace('pg805-resume-tools-v1','pg805-resume-tools-v2').replace('pg805-runtime-resume-v1','pg805-runtime-resume-v2')

def compile_source():return bind(compiler.source()).replace("'pg805-'+phase+'-v1.private.log'","'pg805-'+phase+'-v2.private.log'").replace("'pg805-'+phase+'-v1.exit'","'pg805-'+phase+'-v2.exit'").replace('pg805-frozen-v1.safe.json','pg805-frozen-v2.safe.json')

def native_source():return bind(native()).replace('pg805-frozen-v1.safe.json','pg805-frozen-v2.safe.json').replace("action+'-v1'","action+'-v2'").replace('pg805-stage-v1.exit','pg805-stage-v2.exit').replace('pg805-fixed-stage-v1','pg805-fixed-stage-v2')

if __name__=='__main__':
 mode=sys.argv[1];assert mode in('compile','stage','prepare')
 if mode=='compile':
  for name in('java','helper'):
   previous=getattr(profile,name);setattr(profile,name,lambda previous=previous:bind(previous()))
  compiler.JAVA_TEST=bind(compiler.JAVA_TEST);raw=compile_source();context={'sources':compiler.sources}
 else:raw=native_source();sys.argv=[sys.argv[0],mode];context={}
 exec(compile(raw,'<805 fresh-v2 exact namespace>', 'exec'),{**context,'__file__':str(R/'pg805_resume_v2.py'),'__name__':'__main__'})
