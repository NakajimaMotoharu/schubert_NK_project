"""Whole final source graph has current positive authority; no VM mutations."""
import unittest
import pg2942_current_completed_resume_sources as p


class CurrentCompletedGraph(unittest.TestCase):
    def test_all_final_sources_current_and_closed(self):
        files=p.sources()
        self.assertEqual(20,len(files))
        java=files[p.CLASS+'.java']
        for marker in [p.RUN,p.BOOT,p.SOURCE,p.BOM]:self.assertTrue(marker in java,marker)
        self.assertIn('MaintenanceCompletion.Outcome.WARNING',java)
        self.assertIn('pg2942_parent_receipt',files['pg2942_native_refs.py'])
        self.assertIn('runtime.owned_create_parent',files['pg2942_native_refs.py'])
        self.assertIn('ROOT=RUNTIME',files['pg2942_resume_contract.py'])
        self.assertIn('runtime-parent-created.private.json',files['pg2942_native_refs.py'])


if __name__=='__main__':unittest.main()
