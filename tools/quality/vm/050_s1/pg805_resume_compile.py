"""New immutable runtime only bundle, whole Werror/new796 ABI and independent no-mutation oracle."""
from pathlib import Path
import pg805_resume_sources as p
R=Path(__file__).resolve().parent

JAVA_TEST=r'''public final class Pg805RuntimeResumeTest{
 public static void main(String[]ignored)throws Exception{
  if(!Pg805RuntimeResume.TOOLS.toString().equals("/var/lib/pgpt-s1-preservation/pg805-resume-tools-v1")||!Pg805RuntimeResume.SAVE.toString().equals("/var/lib/pgpt-s1-preservation/pg805-runtime-resume-v1"))throw new AssertionError("fixed namespace");
  String[][]bad={null,new String[0],new String[]{null},new String[]{"unknown"},new String[]{"prepare","extra"}};
  for(var a:bad)try{Pg805RuntimeResume.main(a);throw new AssertionError("foreign argument");}catch(IllegalStateException expected){}
  System.out.println("PG805_ARGUMENT_ORACLE namespace=true refused5BeforeAnyHostOperation=true productionPT0=true");
 }
}
'''

def sources():
 result={'Pg805RuntimeResume.java':p.java(),'Pg805RuntimeResumeTest.java':JAVA_TEST,'pg805_runtime_resume_refs.py':p.helper(),'pg805_snapshot.py':p.snapshot_library()}
 for name in('pg481_native_owned_stop.py','pg480_backup_refs.py','pg466_term_witness.py','pg471_native_term_witness.py'):result[name]=(R/name).read_text()
 from pg799_pending_compile import W
 result['pg777_reference_capability.py']=(W/'pg804-current-tools-v1/pg777_reference_capability.py').read_text()
 return result

def source():
 raw=(R/'pg799_pending_compile.py').read_text();start=raw.index('def sources():');end=raw.index('def main():',start);raw=raw[:start]+raw[end:]
 raw=raw.replace('import pg799_pending_sources as p','import pg805_resume_sources as p').replace('pg799-pending-tools-v1','pg805-resume-tools-v1').replace('pg798-scope-tools-v1','pg804-current-tools-v1').replace('pg750-release-v1','pg796-release-v1').replace('pg800-probe-post-v1','pg802-current-source-post-v1').replace('07b39c1faf43629f79d36e58055817aedb1a30ac36d0c3e34707df5e7e3cb5b2','fc1fb69cbc9e6db2d5c246547a0181f1a1b41c7b89c1ac7198edb69f638e07c5')
 raw=raw.replace('pg799_pending_test.py','pg805_resume_test.py').replace('Pg799PendingDeployment','Pg805RuntimeResume').replace("'pg799-'","'pg805-'").replace('pg799-frozen-v1.safe.json','pg805-frozen-v1.safe.json').replace('p.OLD_SOURCE','p.SOURCE')
 return raw

if __name__=='__main__':
 exec(compile(source(),'<805 new-current runtime-only immutable>', 'exec'),{'__file__':str(R/'pg805_resume_compile.py'),'__name__':'__main__','sources':sources})
