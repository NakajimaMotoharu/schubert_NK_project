import ast,os,pathlib,tempfile,types,unittest
import pg805_resume_sources as p

class Test(unittest.TestCase):
 def test_actual_fixed_dropin_against_independent_literal(self):
  def require(v):
   if not v:raise ValueError('fixture refusal')
  env={'require':require,'RUN_ID':'9de2d03c-28c7-4647-97d9-c66ace06048c'};exec(compile(p.fixed_dropin_source(),'<actual derivation>','exec'),env)
  base=b'[Service]\nExecStart=/usr/bin/java -cp /opt/schubert-nk/current/operations/batch.jar dev.codex.schubert.nk.batch.file.MorningProcessMain\n'
  argv=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false -cp /opt/schubert-nk/current/operations/batch.jar dev.codex.schubert.nk.batch.file.MorningProcessMain'
  native=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+argv+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
  expected=b'# SSC198: fixed one-run same-cutoff resume; retire only after genuine terminal.\n[Service]\nExecStart=\nExecStart='+argv+b' --resume 9de2d03c-28c7-4647-97d9-c66ace06048c\n'
  self.assertEqual(expected,env['fixed_dropin'](base,native))
  for a,b in ((None,native),(base,None),(b'',native),(base,b''),(base+base,native),(base+b'ExecStart=foreign\n',native),(base.replace(b'MorningProcessMain',b'ForeignMain'),native),(base.replace(b'/usr/bin/java ',b'/usr/bin/java -javaagent:foreign '),native)):
   with self.assertRaises(ValueError):env['fixed_dropin'](a,b)
 def test_real_fd_writer_all_operation_faults_and_foreign(self):
  node=next(n for n in ast.parse(p.helper()).body if isinstance(n,ast.FunctionDef)and n.name=='prepare');code=compile(ast.Module(body=[node],type_ignores=[]),'<actual exclusive writer>', 'exec')
  def exercise(at=None,foreign=False,zero=False):
   events=[];fds=set()
   def point(name):
    events.append(name)
    if len(events)==at:raise OSError('fixed injected fault')
   with tempfile.TemporaryDirectory(prefix='pg805-writer-')as temp:
    root=pathlib.Path(temp);root.chmod(0o755);s=root.stat();expected=[s.st_dev,s.st_ino,0,0,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns];name='pg805-once-resume.conf';target=root/name
    if foreign:target.write_bytes(b'independent existing')
    class Ops:
     def __getattr__(self,n):return getattr(os,n)
     def open(self,*a,**kw):point('open');fd=os.open(*a,**kw);fds.add(fd);return fd
     def fstat(self,fd):
      point('fstat');x=os.fstat(fd);return types.SimpleNamespace(**{k:getattr(x,k)for k in('st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns')},st_uid=0,st_gid=0)
     def fchmod(self,*a):point('fchmod');return os.fchmod(*a)
     def write(self,fd,data):point('write');return 0 if zero else os.write(fd,data[:11])
     def fsync(self,*a):point('fsync');return os.fsync(*a)
     def close(self,fd):os.close(fd);fds.remove(fd);point('close')
    def require(v):
     if not v:raise ValueError('fixture refusal')
    def command(argv):point('reload');self.assertEqual(['/usr/bin/systemctl','daemon-reload'],argv)
    env={'os':Ops(),'RUNTIME':root,'NAME':name,'require':require,'h':types.SimpleNamespace(command=command)};exec(code,env)
    try:env['prepare'](target,b'independent runtime input\n'*3,expected);self.assertEqual(b'independent runtime input\n'*3,target.read_bytes());self.assertEqual(1,events.count('reload'));self.assertFalse(fds);return events,None
    except(OSError,ValueError)as failure:
     if foreign:self.assertEqual(b'independent existing',target.read_bytes());self.assertNotIn('reload',events)
     if zero:self.assertNotIn('reload',events)
     return events,failure
    finally:
     for fd in list(fds):os.close(fd)
  events,failure=exercise();self.assertIsNone(failure)
  for at in range(1,len(events)+1):self.assertIsInstance(exercise(at=at)[1],OSError)
  self.assertIsInstance(exercise(foreign=True)[1],ValueError);self.assertIsInstance(exercise(zero=True)[1],ValueError)
 def test_all_surface_namespace_scope_and_data_guard(self):
  for raw in(p.helper(),p.snapshot_library()):ast.parse(raw)
  for value in(p.SOURCE,p.DIGEST,'"PG796"','pg805-resume-tools-v1','pg805-runtime-resume-v1','lease.confirmClosed()','PG805-runtime-resume'):
   self.assertIn(value,p.java())
  for value in('pg802-current-source-post-v1/after.private.json','fc1fb69cbc9e6db2d5c246547a0181f1a1b41c7b89c1ac7198edb69f638e07c5','PG805-runtime-resume',"b'Pg805RuntimeResume'"):
   self.assertIn(value,p.snapshot_library())
  self.assertIn('baseline[\'unitFiles\']',p.helper());self.assertIn("baseline['coverageBefore']",p.helper())
  self.assertNotIn('systemctl start',p.helper());self.assertIn("'pg805-once-resume.conf'",p.helper())
 def test_flattened_compile_and_transport(self):
  from pg805_resume_compile import source,sources
  from pg805_resume_native import source as native
  raw=source();ast.parse(raw);ast.parse(native())
  for value in('pg796-release-v1','pg805-resume-tools-v1','pg805-frozen-v1.safe.json','Pg805RuntimeResumeTest.java'):self.assertIn(value,raw)
  for value in('Pg805RuntimeResume prepare','0.1.0-PG796',"sys.argv[1]in ('stage','prepare')"):self.assertIn(value,native())
  for name,value in sources().items():
   if name.endswith('.py'):ast.parse(value)
  self.assertNotIn('pg799-',raw);self.assertNotIn('Pg799',raw);self.assertNotIn('Pg778',native())

if __name__=='__main__':unittest.main()
