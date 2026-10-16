"""Actual v1 rejects uuid; actual new table admits only fixed new dependency."""
import json
import unittest
from pg1446_current_cold_stage import W
from closed_role_import_graph import check_graph
import pg4522_failed_current_ro_sources as role


class RuntimeImportLoop(unittest.TestCase):
    def inputs(self):
        folder=W/'pg4522-failed-current-ro-tools-v1';pins=json.loads((folder/'payload-sha256.json').read_bytes())
        files={n:(folder/n).read_bytes()for n in pins if n.endswith('.py')}
        return folder,pins,files

    def test_original_actual_all_graph_rejects_shared_parent_uuid(self):
        folder,pins,files=self.inputs()
        with self.assertRaises(ValueError):check_graph((folder/'pg4522_input_preflight.py').read_text(),files,pins,('Pg4522CandidateRo.class','Pg4522CandidateRo$References.class'))

    def test_new_actual_full_graph_standard_difference_exact_uuid(self):
        folder,pins,files=self.inputs();new=role.sources();files={n:new[n].encode()for n in files}
        oldtext=(folder/'pg4522_input_preflight.py').read_text();newtext=new['pg4522_input_preflight.py']
        r=check_graph(newtext,files,pins,('Pg4522CandidateRo.class','Pg4522CandidateRo$References.class'))
        self.assertTrue(r['allActualImportLoopsPassed']);self.assertEqual(141,r['physicalFiles']);self.assertIn('uuid',r['standardImports'])
        # Apart from current v2 paths, exactly the approved one stdlib was added.
        self.assertEqual(oldtext,newtext.replace("'traceback', 'uuid'))","'traceback'))").replace(role.TOOLS,'pg4522-failed-current-ro-tools-v1').replace(role.SAVE,'pg4526-failed-current-ro-completed-v1'))

    def test_foreign_network_unfrozen_pg_null_and_missing_class_reject(self):
        _,pins,files=self.inputs();new=role.sources();files={n:new[n].encode()for n in files};preflight=new['pg4522_input_preflight.py']
        for module in ['socket','foreign','pg_missing']:
            changed=dict(files);changed['pg4522_parent_receipt.py']+=('\nimport '+module+'\n').encode()
            with self.subTest(module=module),self.assertRaises(ValueError):check_graph(preflight,changed,pins,('Pg4522CandidateRo.class',))
        with self.assertRaises(ValueError):check_graph(preflight,files,pins,('Missing.class',))
        with self.assertRaises(ValueError):check_graph(preflight,None,pins,('Pg4522CandidateRo.class',))


if __name__=='__main__':unittest.main()
