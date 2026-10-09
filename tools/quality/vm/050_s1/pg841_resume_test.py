"""Independent assembled-current identity/original/join and same literal dropin tests."""
import ast,unittest
import pg841_resume as p
from pg805_resume_test import Test as PreviousTests

class Test(unittest.TestCase):
 def test_current_before_all_join(self):
  generated=p.sources()
  for mode in ('compile','stage','prepare'):ast.parse(p.source(mode))
  for name,raw in generated.items():
   if name.endswith('.py'):ast.parse(raw)
  java=generated['Pg841RuntimeResume.java'];snapshot=generated['pg841_snapshot.py'];helper=generated['pg841_runtime_resume_refs.py']
  for literal in(p.SOURCE,p.DIGEST,'"PG832"','"pg832"','pg841-runtime-resume-v1','pg841-resume-tools-v1','lease.confirmClosed()'):self.assertIn(literal,java)
  for literal in(p.BASELINE,'pg840-current832-post-v2/after.private.json','7ea672e8a76c4a4a8a7994652366a4cc','155954641282','0eece14c-f832-47c2-b7dd-14125682e7ea',"b'Pg841RuntimeResume'"):self.assertIn(literal,snapshot)
  for raw in(java,helper,snapshot):
   for stale in('PG796','pg802-current','pg805','Pg805','e4093109','e9f11f1c','137240785885'):self.assertNotIn(stale,raw)
  for literal in('9de2d03c-28c7-4647-97d9-c66ace06048c',"'pg841-once-resume.conf'","baseline['unitFiles']","baseline['coverageBefore']"):self.assertIn(literal,helper)
  self.assertNotIn('systemctl start',helper)
  self.assertIn('pg832-release-v1',p.source('compile'));self.assertIn('pg840-current832-post-v2',p.source('compile'))
 def test_new_actual_dropin_with_independent_literal(self):
  env={'RUN_ID':'9de2d03c-28c7-4647-97d9-c66ace06048c','require':lambda v:None if v else (_ for _ in ()).throw(ValueError('fixture'))}
  exec(compile(p.fixed_dropin_source(),'<841 actual exact derivation>','exec'),env)
  base=b'[Service]\nExecStart=/usr/bin/java -cp /opt/schubert-nk/current/operations/batch.jar dev.codex.schubert.nk.batch.file.MorningProcessMain\n'
  argv=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false -cp /opt/schubert-nk/current/operations/batch.jar dev.codex.schubert.nk.batch.file.MorningProcessMain'
  native=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+argv+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
  expected=b'# SSC198: fixed one-run same-cutoff resume; retire only after genuine terminal.\n[Service]\nExecStart=\nExecStart='+argv+b' --resume 9de2d03c-28c7-4647-97d9-c66ace06048c\n'
  self.assertEqual(expected,env['fixed_dropin'](base,native))
 def test_writer_fault_independent_existing_same_body(self):
  self.assertEqual(previous_writer(),new_writer())
  PreviousTests('test_real_fd_writer_all_operation_faults_and_foreign').test_real_fd_writer_all_operation_faults_and_foreign()

def previous_writer():
 import pg805_resume_sources as old
 return ast.dump(next(n for n in ast.parse(old.helper()).body if isinstance(n,ast.FunctionDef)and n.name=='prepare'))
def new_writer():return ast.dump(next(n for n in ast.parse(p.helper()).body if isinstance(n,ast.FunctionDef)and n.name=='prepare'))
if __name__=='__main__':unittest.main()
