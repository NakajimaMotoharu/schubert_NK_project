"""Independent current instance driver joins; pure generation only, no operational calls."""
import ast
import unittest
from pyflakes.api import check
import pg4316_current_failed_dispatch as s
from pg4304_current_failed_parent_contract_test import fixture


def assignment(raw,name):
    return ast.literal_eval(next(n.value for n in ast.parse(raw).body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id==name))


class CurrentDispatch(unittest.TestCase):
    def test_whole_current_pins_and_exact_six_actual_stops(self):
        raw=s.payload();self.assertEqual(check(raw,'<all current recovery>'),0)
        self.assertEqual(assignment(raw,'INPUT_HASHES'),s.compiled()['inputFileHashes'])
        self.assertEqual(assignment(raw,'PARENT_SOURCE'),s.parent_source())
        self.assertIn(s.role.TOOLS,raw);self.assertIn('all37StartupEntriesPreserved',raw)
        self.assertIn("len(baseline['startup'])==38",raw);self.assertIn("==56",raw)
        stop=next(n for n in ast.walk(ast.parse(raw))if isinstance(n,ast.FunctionDef)and n.name=='stop')
        text=ast.get_source_segment(raw,stop)
        self.assertIn("['/usr/bin/systemctl','stop',unit]",text)
        self.assertNotIn("unit=='caddy.service'",text)
        for old in ['pg4160-retained-config-read','pg4152-exact-failed-done-recover','caddyPriorStopAuthenticated','pg4112-canonical-epoch-owned-tools-v1']:
            self.assertNotIn(old,raw)

    def test_declaration_and_pool_qualified_contracts_reused(self):
        raw=s.payload()
        self.assertIn("declaration_contract['same_configurations']",raw)
        self.assertIn("pool_contract['counts_valid']",raw)
        self.assertNotIn('require(config()==fixed_config)',raw)
        pool={};exec(assignment(raw,'POOL_SOURCE'),pool)
        self.assertTrue(pool['counts_valid']({'schubert_app':3,'schubert_web_session':1},set(),1,5))
        self.assertFalse(pool['counts_valid']({'schubert_app':9,'schubert_web_session':1},set(),1,11))
        self.assertFalse(pool['counts_valid']({'schubert_app':3,'schubert_web_session':1},{'schubert-nk-api.service'},1,5))

    def test_failed_parent_projection_preserves_data_only_semantics(self):
        b,state,rows,done=fixture();ns={};exec(s.parent_source(),ns)
        ns['CURRENT_BINDING']=b
        value=ns['classify'](s.role.SOURCE,s.role.BOM,ns['BOOT'],{**state,'ControlGroup':'synthetic-extra-verified-elsewhere'},rows,done)
        self.assertFalse(value['parentNormal']);self.assertFalse(value['stopAuthority'])
        for change in [{'Result':'success'},{'MainPID':'123'},{'InvocationID':'f'*32}]:
            with self.assertRaises(ValueError):ns['classify'](s.role.SOURCE,s.role.BOM,ns['BOOT'],{**state,**change},rows,done)


if __name__=='__main__':unittest.main()
