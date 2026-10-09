"""Independent fixed runtime delta/admission/source/bundle oracle, no VM."""
import ast,unittest
import pg815_retirement_sources as p
class Test(unittest.TestCase):
 def test_actual_runtime_derive_fixed_literal(self):
  from pg805_resume_sources import fixed_dropin_source
  def require(v):
   if not v:raise ValueError('literal refused')
  env={'require':require,'RUN_ID':'9de2d03c-28c7-4647-97d9-c66ace06048c'};exec(compile(fixed_dropin_source(),'<actual derived fixed file>','exec'),env)
  base=b'[Service]\nExecStart=/usr/bin/java -cp /opt/schubert-nk/current/operations/batch.jar dev.codex.schubert.nk.batch.file.MorningProcessMain\n'
  command=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false -cp /opt/schubert-nk/current/operations/batch.jar dev.codex.schubert.nk.batch.file.MorningProcessMain'
  native=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+command+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
  self.assertEqual(b'# SSC198: fixed one-run same-cutoff resume; retire only after genuine terminal.\n[Service]\nExecStart=\nExecStart='+command+b' --resume 9de2d03c-28c7-4647-97d9-c66ace06048c\n',env['fixed_dropin'](base,native))
  for bad in(None,b'',base+base,base.replace(b'MorningProcessMain',b'foreign')):
   with self.assertRaises(ValueError):env['fixed_dropin'](bad,native)
 def test_whole_names_and_exact_nonmutation_capability(self):
  from pg815_retirement_compile import source,sources
  from pg815_retirement_native import source as native
  for raw in(source(),native(),p.helper(),p.snapshot_library()):ast.parse(raw)
  for name,raw in sources().items():
   if name.endswith('.py'):ast.parse(raw)
  self.assertIn('public final class Pg815RuntimeRetirementTest',p.java_test())
  self.assertIn('args!=null',p.java());self.assertNotIn('Pg464CodeOnlyDeployment',p.java())
  self.assertIn('lease.confirmClosed()',p.java());self.assertIn('if(!phase.equals("REF_CLOSE"))pulse()',p.java())
  self.assertIn('pg805-once-resume.conf',p.java());self.assertIn('runtime.unlinkEntry("pg805-once-resume.conf")',p.java())
  self.assertIn('pg814-recovered949-post-v1/after.private.json',p.snapshot_library());self.assertIn(p.SNAPSHOT,p.snapshot_library())
  self.assertIn("argv[-2]==b'retire'",p.snapshot_library());self.assertIn('if db_required:require(',p.snapshot_library())
  for raw in(p.helper(),p.snapshot_library()):
   self.assertNotIn('stop_one',raw);self.assertNotIn("'stop',",raw);self.assertNotIn("'start',",raw)
  self.assertIn("('stage','retire')",native());self.assertIn('Pg815RuntimeRetirement retire',native());self.assertNotIn('RuntimeResume',native())
  self.assertIn("post['M_A0']and post['databaseClient0']",source());self.assertNotIn('pg813-frozen',source())
if __name__=='__main__':unittest.main()
