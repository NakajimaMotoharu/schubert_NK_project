"""Fresh one-use same-original runtime at current832; prepare only, no start."""
import ast
from pathlib import Path
import sys
import pg805_resume_sources as previous
import pg805_resume_compile as compiler
from pg805_resume_native import source as previous_native
R=Path(__file__).resolve().parent
SOURCE='2a0d5aa392c85a1dc12a1cdb423978e8500895b8'
DIGEST='8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977'
BASELINE='051d450c29ffa6c372410794a52d144901a3c5af0e519d8447903af1a5e5498f'

def bind(raw):
 return (raw.replace('Pg805','Pg841').replace('PG805','PG841').replace('pg805','pg841')
  .replace('pg802-current-source-post-v1','pg840-current832-post-v2')
  .replace('fc1fb69cbc9e6db2d5c246547a0181f1a1b41c7b89c1ac7198edb69f638e07c5',BASELINE)
  .replace(previous.SOURCE,SOURCE).replace(previous.DIGEST,DIGEST)
  .replace('PG796','PG832').replace('pg796','pg832')
  .replace('e4093109ab234700b61dd45711126e4e','7ea672e8a76c4a4a8a7994652366a4cc')
  .replace('137240785885','155954641282').replace('2797579','3123795')
  .replace('e9f11f1c-f087-458a-aad0-8c1e4e140571','0eece14c-f832-47c2-b7dd-14125682e7ea')
  .replace('==544','==554').replace('== 544','== 554'))

def java():return bind(previous.java())
def helper():return bind(previous.helper())
def snapshot_library():return bind(previous.snapshot_library())
def fixed_dropin_source():return previous.fixed_dropin_source()

def sources():
 values={'Pg841RuntimeResume.java':java(),'Pg841RuntimeResumeTest.java':bind(compiler.JAVA_TEST),'pg841_runtime_resume_refs.py':helper(),'pg841_snapshot.py':snapshot_library()}
 for name in('pg481_native_owned_stop.py','pg480_backup_refs.py','pg466_term_witness.py','pg471_native_term_witness.py'):values[name]=(R/name).read_text()
 values['pg777_reference_capability.py']=(Path('/home/mini/codex/project1/work/pgpt-runs/PG379')/'pg804-current-tools-v1/pg777_reference_capability.py').read_text()
 return values

def source(mode):
 raw=bind(compiler.source() if mode=='compile' else previous_native())
 if mode=='compile':
  raw=raw.replace('import pg841_resume_sources as p','import pg841_resume as p')
  raw=raw.replace('pg841_resume_test.py','pg841_resume_test.py')
 ast.parse(raw);return raw

if __name__=='__main__':
 mode=sys.argv[1];assert mode in('compile','stage','prepare')
 exec(compile(source(mode),'<841 current832 one-use prepare>','exec'),{'__file__':str(R/'pg841_resume.py'),'__name__':'__main__','sources':sources})
