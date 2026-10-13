import unittest
from pg2132_current_normal_unused_sources import sources,BEFORE,CURRENT,CURRENT_BOM,production

class NormalUnusedRoles(unittest.TestCase):
    def test_actual_source_roles_current_normal_receipt_and_new_only_profile(self):
        values=sources('a'*64)
        self.assertIn('Pg2132UnusedStage.java',values)
        self.assertIn('pg2132_native_refs.py',values)
        stage=values['Pg2132UnusedStage.java']
        self.assertIn('genuineParentNormalWarningOriginal=true',stage)
        self.assertNotIn('managerFailureRetained=true',stage)
        refs=values['pg2132_native_refs.py']
        self.assertIn('START=113070840714;END=114755353173',refs)
        self.assertIn('pg2130-current-normal-before-v1',refs)
        self.assertIn("/proc/588342",refs)
        projection=values['pg2132_warning_parent_projection.py']
        self.assertIn('currentManagerGc',projection)
        self.assertNotIn('managerFailureRetained',projection)
        receipt=values['pg2132_parent_receipt.py']
        self.assertIn('a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75',receipt)
        all_source='\n'.join(values.values())
        self.assertIn(CURRENT,all_source)
        self.assertIn(production(),all_source)
        self.assertIn(CURRENT_BOM,all_source)
        self.assertIn(BEFORE,all_source)

    def test_bad_before_bom_rejected_before_source_emission(self):
        for bom in [None,'x'*64,'a'*63]:
            with self.assertRaises(ValueError):sources(bom)
        with self.assertRaises(ValueError):sources('a'*64,'b'*64)

if __name__=='__main__':unittest.main()
