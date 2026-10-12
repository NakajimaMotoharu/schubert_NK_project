"""Independent OLD/NEW/Root identity and exact WARNING profile, no UUID digit rewrites."""
import unittest
from pg1848_warning_signed_unused_sources import sources,CANDIDATE,OLD


class Bind(unittest.TestCase):
    def test_real_emitted_roles_warning_tuple_and_existing_unit_unchanged(self):
        values=sources('b'*64,'c'*64)
        java=values['Pg1848UnusedStage.java'];ref=values['pg1848_native_refs.py']
        self.assertIn('4148e3e8-f107-431a-ab27-d6e6d1f1772e',java)
        self.assertIn('MaintenanceCompletion.Outcome.WARNING',java)
        self.assertIn('genuineParentWarningOriginal=true',java)
        self.assertIn(OLD,java);self.assertIn(CANDIDATE,ref)
        self.assertIn('qualify_warning_parent(parent)',ref)
        self.assertIn("SuccessExitStatus':''",ref)
        self.assertNotIn('StartUnit',ref);self.assertNotIn('ResetFailedUnit',ref)
        self.assertIn('pg1851-warning-release-v1.tar',values['pg1848_input_preflight.py'])
        self.assertIn('pg1849-warning-completed-current-before-v1',ref)
        for raw in values.values():self.assertNotIn('f1848e',raw)


if __name__=='__main__':unittest.main()
