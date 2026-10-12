"""No cold zero/one assumption or unbound extra role is accepted."""
import copy
import unittest
from pg1780_warning_live_peer_proof import validate_peers,payload


class Peers(unittest.TestCase):
    def fixture(self):
        return [{'pid':pid,'role':role,'port':port,'address':'127.0.0.1','database':'schubert_nk','backendStart':'2026-10-12T19:19:00Z','app':app,'state':state}for pid,role,port,app,state in [(500001,'schubert_app',35001,'JDBC','idle'),(500002,'schubert_app',35002,'JDBC','idle'),(500003,'schubert_web_session',35003,'JDBC','idle'),(476114,'schubert_batch',36058,'PG998-native-stop','idle in transaction')]]

    def test_exact_live_roles_and_all_boundary_refusals(self):
        rows=self.fixture();self.assertEqual(476114,validate_peers(rows,1)['pid'])
        for r,count in [(rows[:-1],1),(rows+[rows[0]],1),(rows,0),(rows,2),(rows,True)]:
            with self.assertRaises(ValueError):validate_peers(r,count)
        for key,value in [('pid',True),('pid',0),('port',True),('port',0),('port',65536),('address','::1'),('database','foreign'),('backendStart',None),('role','postgres')]:
            bad=copy.deepcopy(rows);bad[0][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):validate_peers(bad,1)
        for key,value in [('pid',476115),('app','foreign'),('state','active')]:
            bad=copy.deepcopy(rows);bad[-1][key]=value
            with self.assertRaises(ValueError):validate_peers(bad,1)
        bad=copy.deepcopy(rows);bad[1]['pid']=bad[0]['pid']
        with self.assertRaises(ValueError):validate_peers(bad,1)

    def test_actual_emitted_all_sockets_and_sole_lock(self):
        raw=payload();self.assertIn("owners={'schubert_app':451130,'schubert_web_session':452144,'schubert_batch':476087}",raw)
        self.assertIn('len(left)==len(right)==1',raw);self.assertIn('pid=476114',raw)
        self.assertNotIn('pidfd_send_signal',raw)


if __name__=='__main__':unittest.main()
