"""Independent literal hashed metadata fixtures, no raw session ids/production authority."""
import copy,unittest
from pg892_same_source_union import session_identities
def fixture():return[{'dumpMs':200,'startMs':100,'index':0,'sessions':1,'sessionIdSha256':format(i,'064x')}for i in range(16)]
class Test(unittest.TestCase):
 def test_canonical_all_sixteen(self):self.assertEqual(len(session_identities(fixture())),16)
 def test_null_missing_extra_type_and_reverse(self):
  for rows in (None,[],fixture()[:15],fixture()+[fixture()[0]]):
   with self.assertRaises(ValueError):session_identities(rows)
  for k,v in [('dumpMs',False),('startMs',201),('startMs',0),('sessions',2),('index',1),('sessionIdSha256',None),('sessionIdSha256','raw-id'),('id','raw-id')]:
   rows=fixture();rows[0][k]=v
   with self.assertRaises(ValueError):session_identities(rows)
  rows=fixture();rows[1]=copy.deepcopy(rows[0])
  with self.assertRaises(ValueError):session_identities(rows)
if __name__=='__main__':unittest.main()
