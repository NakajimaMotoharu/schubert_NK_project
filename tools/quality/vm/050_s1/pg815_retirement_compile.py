"""Whole current796 ABI/Werror/fixed argv, new-only815; no VM."""
import ast
from pathlib import Path
import pg815_retirement_sources as p
R=Path(__file__).resolve().parent
def sources():
 result={'Pg815RuntimeRetirement.java':p.java(),'Pg815RuntimeRetirementTest.java':p.java_test(),'pg815_runtime_retirement_refs.py':p.helper(),'pg815_snapshot.py':p.snapshot_library()}
 for name in('pg481_native_owned_stop.py','pg480_backup_refs.py','pg466_term_witness.py','pg471_native_term_witness.py'):result[name]=(R/name).read_text()
 from pg799_pending_compile import W
 result['pg777_reference_capability.py']=(W/'pg813-failed949-tools-v2/pg777_reference_capability.py').read_text()
 return result
def source():
 raw=(R/'pg799_pending_compile.py').read_text();start=raw.index('def sources():');end=raw.index('def main():',start);raw=raw[:start]+raw[end:]
 for old,new in(('import pg799_pending_sources as p','import pg815_retirement_sources as p'),('pg799-pending-tools-v1','pg815-retirement-tools-v1'),('pg798-scope-tools-v1','pg813-failed949-tools-v2'),('pg750-release-v1','pg796-release-v1'),('pg800-probe-post-v1','pg814-recovered949-post-v1'),('07b39c1faf43629f79d36e58055817aedb1a30ac36d0c3e34707df5e7e3cb5b2',p.SNAPSHOT),('post[\'M_A_OFD0\']and post[\'databaseSessions0\']',"post['M_A0']and post['databaseClient0']"),('pg799_pending_test.py','pg815_retirement_test.py'),('Pg799PendingDeployment','Pg815RuntimeRetirement'),("'pg799-'","'pg815-'"),('pg799-frozen-v1.safe.json','pg815-frozen-v1.safe.json'),('p.OLD_SOURCE','p.SOURCE')):
  assert old in raw,old;raw=raw.replace(old,new)
 ast.parse(raw);return raw
if __name__=='__main__':exec(compile(source(),'<815 exact one compiler>','exec'),{'__file__':str(R/'pg815_retirement_compile.py'),'__name__':'__main__','sources':sources})
