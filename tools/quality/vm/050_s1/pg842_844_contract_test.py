"""Independent literal identity/one-issuance/original-generation joins before guest."""
import ast,unittest
import pg842_resume_post as post
import pg843_parent_observer as observer
import pg844_external_once as once
class Test(unittest.TestCase):
 def test_post_all_original_new_binding(self):
  raw=post.payload();ast.parse(raw)
  for v in(post.AFTER,'pg841-runtime-resume-v1','pg841-resume-tools-v1',"==554","'startupEntries':43","'pg841-once-resume.conf'",'2a0d5aa392c85a1dc12a1cdb423978e8500895b8'):self.assertIn(v,raw)
  for v in('systemctl start','systemctl stop','a1cd831','pg805','PG796'):self.assertNotIn(v,raw)
 def test_observer_only_same_generation(self):
  ast.parse(observer.source());raw=observer.watch();ast.parse(raw)
  for v in('PG832',"assert role in roots and same(roots[role],aa)","'wholeMorningAccepted':False","'automaticStop':False",'before==metadata9(ca)'):self.assertIn(v,raw)
  self.assertIn('pg842-resume-post-v1',observer.source());self.assertNotIn('systemctl start',raw)
 def test_exact_reserved_start_original_and_all_fields(self):
  tree=ast.parse(once.source());raw=next(n.value.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
  start="['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']"
  self.assertEqual(1,raw.count(start));self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index(start))
  for v in(post.AFTER,'pg841-runtime-resume-v1','pg841-resume-tools-v1','pg841-once-resume.conf','0.1.0-PG832','2a0d5aa392c85a1dc12a1cdb423978e8500895b8','8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977',"'originalBudgetSeconds':1800","'repeatForbidden':True","before['coverageBefore']","before['unitFiles'].items()",'9de2d03c-28c7-4647-97d9-c66ace06048c'):
   self.assertIn(v,raw)
  self.assertIn('pg843-watch-v1',once.source());self.assertIn('pg842-resume-post-v1',once.source())
  for v in('PG796','pg808','pg805','systemctl stop'):self.assertNotIn(v,raw)
if __name__=='__main__':unittest.main()
