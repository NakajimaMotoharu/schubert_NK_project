import ast
import unittest
import pg2212_current_newboot_cold_dispatch as p
from pg2208_current_newboot_cold_sources import observer


class CurrentDispatcher(unittest.TestCase):
    def test_exact_new_boot_source_and_current_bundle_roles(self):
        s=p.source()
        for text in ['pg2209','pg2214-current-newboot-cold-stage-v2','pg2212-current-newboot-cold-owned-prepare-v1',
          'b2d6f605-61cf-425f-8fbd-12d606f6ee66','Pg2208CurrentColdPreparation','0.1.0-PG2126']:
            if text=='pg2209':continue # Frozen binding belongs to actual main namespace.
            self.assertIn(text,s)
        self.assertNotIn('/proc/3323',s)
        self.assertNotIn('0.1.0-PG1292',s)
        self.assertIn('frozenOperatorSource',s)
        self.assertIn("'-cp',cp,'Pg2208CurrentColdPreparation','prepare'",s)
        compile(s,'<independent whole dispatcher>', 'exec')

    def test_current_reference_namespace_never_calls_old_idle_peers_query(self):
        t=ast.parse(observer())
        f=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='observe')
        self.assertFalse(any(isinstance(n,ast.Assign) and any(isinstance(q,ast.Name) and q.id=='peers' for q in n.targets) for n in f.body))
        s=ast.unparse(f)
        self.assertIn('peer_check()',s)
        self.assertIn('runtime_check()',s)
        self.assertIn("rows == old['rows']",s)

    def test_actual_stage_full_tuple_not_only_wrapper_names(self):
        from pg2214_current_newboot_cold_stage_v2 import source
        s=source()
        self.assertIn("fixed['productionSource']=='3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8'",s)
        self.assertIn('pg2209-current-newboot-cold-frozen-v1.safe.json',s)
        self.assertIn('b2d6f605-61cf-425f-8fbd-12d606f6ee66',s)
        self.assertIn('pg2208-current-newboot-cold-tools-v1',s)
        for old in ['769ddb15','PG1292','pg1444-current','3d69f5af']:self.assertNotIn(old,s)


if __name__=='__main__':unittest.main()
