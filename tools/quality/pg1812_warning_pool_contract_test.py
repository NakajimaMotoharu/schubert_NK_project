"""Independent min/max populations and every role/identity/null boundary."""
import copy
import unittest
from pg1812_warning_pool_contract import validate_current_peers


class Pools(unittest.TestCase):
    def fixture(self,api=2,web=1):
        rows=[]
        for role,app,count in [('schubert_app','schubert-nk-api',api),('schubert_web_session','schubert-nk-web',web),('schubert_batch','PG998-native-stop',1)]:
            for _ in range(count):
                number=len(rows)+1;rows.append({'pid':479217 if role=='schubert_batch'else 500000+number,'port':35000+number,'role':role,'app':app,'state':'idle in transaction'if role=='schubert_batch'else 'idle','address':'127.0.0.1','database':'schubert_nk','backendStart':'2026-10-12T20:27:00Z'})
        return rows

    def test_approved_min_max_and_actual_web_two(self):
        for api,web in [(2,1),(2,2),(8,1),(8,2)]:self.assertEqual(479217,validate_current_peers(self.fixture(api,web),1,479217)['pid'])
        for api,web in [(1,1),(9,1),(2,0),(2,3)]:
            with self.assertRaises(ValueError):validate_current_peers(self.fixture(api,web),1,479217)

    def test_every_typed_field_and_foreign_owner(self):
        for key,value in [('pid',True),('pid',0),('port',True),('port',0),('port',65536),('role','postgres'),('app','foreign'),('address','::1'),('database','foreign'),('backendStart',None),('backendStart','')]:
            rows=self.fixture();rows[0][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):validate_current_peers(rows,1,479217)
        for key,value in [('pid',479218),('state','active'),('app','foreign')]:
            rows=self.fixture();rows[-1][key]=value
            with self.assertRaises(ValueError):validate_current_peers(rows,1,479217)
        for key in ['pid','port']:
            rows=copy.deepcopy(self.fixture());rows[1][key]=rows[0][key]
            with self.assertRaises(ValueError):validate_current_peers(rows,1,479217)
        for count in [0,2,True,None]:
            with self.assertRaises(ValueError):validate_current_peers(self.fixture(),count,479217)
        for backend in [True,0,None,479218]:
            with self.assertRaises(ValueError):validate_current_peers(self.fixture(),1,backend)


if __name__=='__main__':unittest.main()
